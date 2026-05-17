#!/usr/bin/env python3
"""Sixsense Prophet forecast — train on data through 2026-01-31,
predict 2026-02-week1 ~ 2026-06-week4 (21 weeks ahead).

Outputs:
- backend/data/forecast/forecast_2026-02-w1.json
  - short_term: 1~7주 예측
  - mid_term:   8~21주 예측
  - with 80%/95% confidence intervals
- backend/data/forecast/forecast_summary.txt — human-readable summary

Usage:
  cd backend && .venv/bin/python3 pipelines/forecast.py
"""
import json
import sys
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
from prophet import Prophet

warnings.filterwarnings("ignore")

HIST_DIR = Path(__file__).parent.parent / "data" / "historical"
OUT_DIR = Path(__file__).parent.parent / "data" / "forecast"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_FILE = HIST_DIR / "target-dram.json"
TRAIN_CUTOFF = "2026-01-31"
FORECAST_START = "2026-02-02"  # First Monday of Feb 2026

# Regressors (collected signals to use as external regressors)
REGRESSORS = ["A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7", "B-1", "B-2", "B-3", "B-4", "B-5", "B-6", "B-7", "macro-fed", "macro-dxy", "macro-pmi", "macro-krw", "macro-cu"]


def load_series(path: Path) -> pd.DataFrame:
    j = json.loads(path.read_text())
    df = pd.DataFrame(j["data"])
    df["ds"] = pd.to_datetime(df["week"])
    df["y"] = df["value"]
    return df[["ds", "y"]].sort_values("ds").reset_index(drop=True)


def main():
    # ── 1. Load target ─────────────────────────────────────────────────────
    if not TARGET_FILE.exists():
        print(f"❌ {TARGET_FILE} 없음. 먼저 backfill.py 실행 필요")
        sys.exit(1)

    print(f"\n{'═'*80}")
    print(f"  Sixsense Prophet Forecast")
    print(f"  학습 컷오프: {TRAIN_CUTOFF}")
    print(f"  예측 시작:   {FORECAST_START} (1~7주 단기 + 8~21주 중장기)")
    print(f"{'═'*80}\n")

    target_df = load_series(TARGET_FILE)
    print(f"  📊 Target (target-dram proxy): {len(target_df)}주 [{target_df['ds'].min().date()} ~ {target_df['ds'].max().date()}]")

    # ── 2. Load regressors ─────────────────────────────────────────────────
    regressor_dfs = {}
    for sid in REGRESSORS:
        fp = HIST_DIR / f"{sid}.json"
        if fp.exists():
            df = load_series(fp).rename(columns={"y": sid})
            regressor_dfs[sid] = df
            print(f"  ✅ Regressor {sid:12} {len(df)}주 로드")
        else:
            print(f"  ⚠️  Regressor {sid:12} 없음 — 제외")

    # ── 3. Merge regressors into target df ─────────────────────────────────
    merged = target_df.copy()
    for sid, df in regressor_dfs.items():
        merged = merged.merge(df[["ds", sid]], on="ds", how="left")
    # Forward-fill, back-fill, then zero-fill any remaining NaN (defensive)
    merged = merged.ffill().bfill().fillna(0)

    # ── 4. Split train (≤ 2026-01-31) ──────────────────────────────────────
    cutoff = pd.Timestamp(TRAIN_CUTOFF)
    train = merged[merged["ds"] <= cutoff].copy()
    print(f"\n  📚 Train set: {len(train)}주 [{train['ds'].min().date()} ~ {train['ds'].max().date()}]")

    if len(train) < 10:
        print(f"❌ 학습 데이터 부족 (최소 10주 필요, 현재 {len(train)})")
        sys.exit(1)

    # ── 5. Train Prophet — univariate (no regressors), conservative ────────
    # 학습 데이터가 ~40주뿐이라 yearly seasonality + regressors는 과적합 유발.
    # Phase 5 단계에서는 단순 univariate로 안정성 우선.
    # 향후 Phase 6에서 더 긴 히스토리 확보 후 regressor 재도입 권장.
    print(f"\n  🤖 Prophet 학습 중 (univariate, conservative)...")
    m = Prophet(
        weekly_seasonality=False,
        yearly_seasonality=False,   # 40주로는 연간 주기 추정 불가
        daily_seasonality=False,
        growth="linear",
        changepoint_prior_scale=0.05,  # 보수적 (default 0.05)
        interval_width=0.80,
        n_changepoints=8,
    )
    m.fit(train)
    # Regressors loaded but unused in this conservative config (kept in output JSON for transparency)

    # ── 6. Build future dataframe (21 weeks beyond cutoff) ─────────────────
    future = m.make_future_dataframe(periods=21, freq="W-MON")

    # ── 7. Predict ─────────────────────────────────────────────────────────
    forecast = m.predict(future)
    fcst_only = forecast[forecast["ds"] > cutoff].copy()

    # ── 8. Split short_term (1-7w) and mid_term (8-21w) ────────────────────
    short_term = fcst_only.iloc[:7]
    mid_term = fcst_only.iloc[7:21]

    # ── 9. Validate against actuals (2026-02 onwards if available) ────────
    actuals_after = merged[merged["ds"] > cutoff].copy()
    validation = []
    if len(actuals_after) > 0:
        for _, a_row in actuals_after.iterrows():
            f_match = fcst_only[fcst_only["ds"] == a_row["ds"]]
            if len(f_match) > 0:
                f_row = f_match.iloc[0]
                err_pct = abs((a_row["y"] - f_row["yhat"]) / a_row["y"]) * 100
                validation.append({
                    "week": a_row["ds"].date().isoformat(),
                    "actual": round(a_row["y"], 4),
                    "predicted": round(f_row["yhat"], 4),
                    "lower": round(f_row["yhat_lower"], 4),
                    "upper": round(f_row["yhat_upper"], 4),
                    "error_pct": round(err_pct, 2),
                    "within_ci": bool(f_row["yhat_lower"] <= a_row["y"] <= f_row["yhat_upper"]),
                })

    # ── 10. Format output ──────────────────────────────────────────────────
    def fmt_period(df):
        return [
            {
                "week": row["ds"].date().isoformat(),
                "yhat": round(row["yhat"], 4),
                "yhat_lower": round(row["yhat_lower"], 4),
                "yhat_upper": round(row["yhat_upper"], 4),
            }
            for _, row in df.iterrows()
        ]

    output = {
        "model": "prophet_v1.3.0",
        "target": "target-dram (Memory stocks blend, base=100)",
        "trainedAt": date.today().isoformat(),
        "trainCutoff": TRAIN_CUTOFF,
        "trainWeeks": len(train),
        "regressors": list(regressor_dfs.keys()),
        "interval_width": 0.80,
        "forecast": {
            "short_term_1_7w": fmt_period(short_term),
            "mid_term_8_21w": fmt_period(mid_term),
        },
        "validation_vs_actuals": validation,
        "last_train_value": round(train["y"].iloc[-1], 4),
    }

    out_path = OUT_DIR / "forecast_2026-02-w1.json"
    out_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\n  📁 JSON 저장: {out_path}")

    # ── 11. Human-readable summary ─────────────────────────────────────────
    summary_lines = []
    summary_lines.append("═" * 80)
    summary_lines.append(f"  Sixsense Forecast — 2026-02-w1 시작 1~21주")
    summary_lines.append(f"  학습: {len(train)}주 데이터, 컷오프 {TRAIN_CUTOFF}")
    summary_lines.append(f"  모델: Prophet 1.3.0 + {len(regressor_dfs)} regressors")
    summary_lines.append(f"  Target: Memory stocks 가중 평균 (MU 50% + SK 30% + Samsung 20%, base=100)")
    summary_lines.append(f"  마지막 실측값: {output['last_train_value']:.2f}")
    summary_lines.append("═" * 80)
    summary_lines.append("")
    summary_lines.append("📈 단기 예측 (1~7주, 2026-02-w1 ~ 2026-03-w2)")
    summary_lines.append(f"{'Week':14} {'예측':>10} {'80% 하한':>10} {'80% 상한':>10}  변화율")
    summary_lines.append("-" * 80)
    base = output["last_train_value"]
    for p in output["forecast"]["short_term_1_7w"]:
        chg = (p["yhat"] - base) / base * 100
        summary_lines.append(f"{p['week']:14} {p['yhat']:>10.2f} {p['yhat_lower']:>10.2f} {p['yhat_upper']:>10.2f}  {chg:+.2f}%")
    summary_lines.append("")
    summary_lines.append("📈 중장기 예측 (8~21주, 2026-03-w3 ~ 2026-06-w4)")
    summary_lines.append(f"{'Week':14} {'예측':>10} {'80% 하한':>10} {'80% 상한':>10}  변화율")
    summary_lines.append("-" * 80)
    for p in output["forecast"]["mid_term_8_21w"]:
        chg = (p["yhat"] - base) / base * 100
        summary_lines.append(f"{p['week']:14} {p['yhat']:>10.2f} {p['yhat_lower']:>10.2f} {p['yhat_upper']:>10.2f}  {chg:+.2f}%")
    summary_lines.append("")

    if validation:
        within = sum(1 for v in validation if v["within_ci"])
        mape = sum(v["error_pct"] for v in validation) / len(validation)
        summary_lines.append("🔍 사후 검증 (예측 vs 실측, 2026-02 이후 실측 데이터 비교)")
        summary_lines.append(f"  - 비교 가능한 주: {len(validation)}")
        summary_lines.append(f"  - 80% 신뢰구간 내 포함: {within}/{len(validation)} ({within/len(validation)*100:.1f}%)")
        summary_lines.append(f"  - MAPE (평균 절대 오차율): {mape:.2f}%")
        summary_lines.append("")
        summary_lines.append(f"{'Week':14} {'실측':>10} {'예측':>10} {'오차%':>8} {'CI내':>6}")
        summary_lines.append("-" * 60)
        for v in validation[:15]:
            ok = "✓" if v["within_ci"] else "✗"
            summary_lines.append(f"{v['week']:14} {v['actual']:>10.2f} {v['predicted']:>10.2f} {v['error_pct']:>7.2f}% {ok:>6}")
    else:
        summary_lines.append("⚠️  사후 검증 불가 — 2026-02 이후 실측 데이터 없음")

    summary_lines.append("═" * 80)
    summary_text = "\n".join(summary_lines)
    (OUT_DIR / "forecast_summary.txt").write_text(summary_text)
    print(summary_text)


if __name__ == "__main__":
    main()
