#!/usr/bin/env python3
"""honest_backtest.py — 예측 모델의 실력을 '단순 기준선'과 정직하게 비교하는 워크포워드 백테스트.

화면에 표시되는 '예측 검증 결과'의 유일한 출처. 매주 파이프라인에서 실행된다.

forecast_v2.py 의 데이터 준비에 있던 결함을 여기서는 제거하고 평가한다:
  1) 날짜를 모두 해당 주 월요일로 통일 (forecast_v2: 일요일/월요일 혼재로 한 주가 2행으로 분할)
  2) 과거를 미래 값으로 채우는 bfill 금지 — ffill 만, 관측 전은 결측(LightGBM 이 결측 처리)
  3) 월간·분기 발표 통계는 발표 지연(6주) 반영 — 그 주에 실제로 알 수 있던 값만 사용
  4) 매 시점마다 그 시점까지 정답이 확정된 데이터로만 재학습 (진짜 표본 외 예측)

비교: LightGBM 두 방식(가격 수준 예측 = 앱이 쓰던 방식 / 변화율 예측 = 개선 시도) vs 단순 기준선(지난주 값 유지).
합격 기준: 모델 평균 오차 < 기준선 평균 오차 그리고 '모델이 이긴 횟수'의 부호검정 p < 0.05.

출력: backend/data/validation/latest.json
"""
import os

# forecast_v2 와 같은 이유 — macOS 에서 libomp 충돌로 멈추는 것을 방지
os.environ.setdefault("OMP_NUM_THREADS", "1")

import glob
import json
import warnings
from datetime import date
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
HIST = ROOT / "data" / "historical"
OUT = ROOT / "data" / "validation" / "latest.json"

TARGET = "target-dram"
# 값이 그 신호가 아님이 확인된 것은 피처에서 뺀다 (정의는 화면과 같은 곳 — build_frontend_data)
from build_frontend_data import INVALID_SIGNALS
PUB_LAG_WEEKS = 6
LAGGED = {"A-2", "A-3", "A-4", "B-4", "macro-pmi"}   # 월간·분기 발표 통계
SENTIMENT = {"B-1", "B-2", "B-3", "B-5", "B-6", "B-7"}
H_MAX = 7
MIN_TRAIN = 26
DECISION_H = 4                                      # 구매 시뮬레이션: 지금 살지, 4주 뒤 살지

VARIANTS = {
    "level": "앱이 쓰던 방식 (가격 수준 예측)",
    "return": "개선 시도 (변화율 예측)",
}


def load_clean_frame() -> tuple[pd.DataFrame, pd.Series]:
    series = {}
    for f in sorted(glob.glob(str(HIST / "*.json"))):
        sid = Path(f).stem
        if sid.startswith("_") or sid in INVALID_SIGNALS:
            continue
        rows = json.loads(Path(f).read_text()).get("data", [])
        if not rows:
            continue
        s = pd.Series({pd.Timestamp(r["week"]): r["value"] for r in rows}).sort_index()
        s.index = s.index - pd.to_timedelta(s.index.weekday, unit="D")
        series[sid] = s.groupby(level=0).last()

    y_raw = series[TARGET]
    idx = pd.date_range(y_raw.index.min(), y_raw.index.max(), freq="W-MON")
    df = pd.DataFrame(index=idx)
    for sid, s in series.items():
        s = s.reindex(idx).ffill()
        if sid in SENTIMENT:
            s = s.rolling(3, min_periods=1).mean()
        if sid in LAGGED:
            s = s.shift(PUB_LAG_WEEKS)
        df[sid] = s

    y = df.pop(TARGET)
    X = df
    for lag in (1, 2, 4):
        X[f"y_lag{lag}"] = y.shift(lag)
    X["y_now"] = y
    X["y_ret1"] = y.pct_change(1)
    X["y_ret4"] = y.pct_change(4)
    return X, y


def _model():
    import lightgbm as lgb
    return lgb.LGBMRegressor(n_estimators=200, max_depth=4, learning_rate=0.05,
                             random_state=42, verbose=-1, n_jobs=1)


def run_variant(X: pd.DataFrame, y: pd.Series, kind: str) -> pd.DataFrame:
    rows = []
    n = len(y)
    for h in range(1, H_MAX + 1):
        future = y.shift(-h)
        target = future / y - 1 if kind == "return" else future
        for i in range(MIN_TRAIN + h, n - h):
            train_idx = [j for j in range(i - h + 1) if not np.isnan(target.iloc[j])]
            if len(train_idx) < MIN_TRAIN:
                continue
            model = _model()
            model.fit(X.iloc[train_idx], target.iloc[train_idx])
            p = float(model.predict(X.iloc[[i]])[0])
            now = float(y.iloc[i])
            pred = now * (1 + p) if kind == "return" else p
            rows.append({"h": h, "now": now, "actual": float(future.iloc[i]), "model": pred})
    r = pd.DataFrame(rows)
    r["e_model"] = (r.model - r.actual).abs() / r.actual * 100
    r["e_naive"] = (r.now - r.actual).abs() / r.actual * 100
    r["win"] = r.e_model < r.e_naive
    r["dir_ok"] = np.sign(r.model - r.now) == np.sign(r.actual - r.now)
    return r


def current_forecast(X: pd.DataFrame, y: pd.Series, kind: str) -> list[dict]:
    """최신 주에서 1~H_MAX 주 뒤 예측. 검증(run_variant)과 같은 모델·같은 피처를 쓴다.
    검증 불합격이어도 화면에 '참고용'으로 보여주기 위한 값 (v2.4)."""
    n, now = len(y), float(y.iloc[-1])
    last_week = y.index[-1]
    out = []
    for h in range(1, H_MAX + 1):
        future = y.shift(-h)
        target = future / y - 1 if kind == "return" else future
        train_idx = [j for j in range(n) if not np.isnan(target.iloc[j])]
        model = _model()
        model.fit(X.iloc[train_idx], target.iloc[train_idx])
        p = float(model.predict(X.iloc[[n - 1]])[0])
        value = now * (1 + p) if kind == "return" else p
        out.append({"h": h, "week": (last_week + pd.Timedelta(weeks=h)).date().isoformat(),
                    "value": round(value, 2), "changePct": round((value / now - 1) * 100, 2)})
    return out


def sign_test_p(wins: int, n: int) -> float:
    """모델이 기준선을 wins 번 이상 이길 확률 (둘의 실력이 같다고 가정할 때)."""
    return sum(comb(n, k) for k in range(wins, n + 1)) / 2 ** n


def summarize(r: pd.DataFrame) -> dict:
    by_h = [{
        "h": int(h), "n": int(len(g)),
        "modelMape": round(g.e_model.mean(), 2), "naiveMape": round(g.e_naive.mean(), 2),
        "winRate": round(g.win.mean() * 100, 1), "dirAcc": round(g.dir_ok.mean() * 100, 1),
    } for h, g in r.groupby("h")]

    wins, n = int(r.win.sum()), len(r)
    p = sign_test_p(wins, n)
    overall = {
        "n": n,
        "modelMape": round(r.e_model.mean(), 2), "naiveMape": round(r.e_naive.mean(), 2),
        "winRate": round(wins / n * 100, 1), "dirAcc": round(r.dir_ok.mean() * 100, 1),
        "alwaysUpDirAcc": round((r.actual > r.now).mean() * 100, 1),
        "underRate": round((r.model < r.actual).mean() * 100, 1),
        "pValue": round(p, 3),
    }

    d = r[r.h == DECISION_H]
    wait = d.model < d.now
    buy_model = np.where(wait, d.actual, d.now)
    base = d.now.mean()
    procurement = {
        "n": int(len(d)), "horizonWeeks": DECISION_H,
        "alwaysNow": round(base, 2),
        "model": round(float(buy_model.mean()), 2),
        "modelPct": round((buy_model.mean() / base - 1) * 100, 2),
        "perfectPct": round((np.minimum(d.now, d.actual).mean() / base - 1) * 100, 2),
        "waitRate": round(wait.mean() * 100, 1),
        "waitCount": int(wait.sum()),
        "waitCorrect": int((wait & (d.actual < d.now)).sum()),
    }
    passed = overall["modelMape"] < overall["naiveMape"] and p < 0.05
    return {"byHorizon": by_h, "overall": overall, "procurement": procurement, "pass": bool(passed)}


def main():
    X, y = load_clean_frame()
    print(f"교정 데이터: {len(y)}주 ({y.index.min().date()} ~ {y.index.max().date()}), 피처 {X.shape[1]}개")

    variants = []
    for key, name in VARIANTS.items():
        s = summarize(run_variant(X, y, key))
        s["forecast"] = current_forecast(X, y, key)
        o = s["overall"]
        print(f"  [{name}] 모델 {o['modelMape']}% vs 기준선 {o['naiveMape']}% · 우세 {o['winRate']}% · "
              f"p={o['pValue']} · 구매 {s['procurement']['modelPct']:+.2f}% → {'합격' if s['pass'] else '불합격'}")
        variants.append({"key": key, "name": name, **s})

    passed = any(v["pass"] for v in variants)
    payload = {
        "runAt": date.today().isoformat(),
        "dataWeeks": int(len(y)),
        "dataRange": [y.index.min().date().isoformat(), y.index.max().date().isoformat()],
        "target": "메모리 3사 주가지수 (MU 50% · SK하이닉스 30% · 삼성전자 20%, 2025-06-16 = 100)",
        "baseline": "단순 기준선 — 지난주 값이 그대로 유지된다고 가정",
        "passRule": "모델 평균 오차 < 기준선 평균 오차, 그리고 부호검정 p < 0.05",
        "method": [
            f"과거 각 시점마다 그 시점까지 정답이 확정된 데이터로만 새로 학습해 1~{H_MAX}주 뒤를 예측",
            "날짜를 월요일로 통일, 미래 값으로 과거를 채우지 않음",
            f"월간·분기 발표 통계는 발표 지연 {PUB_LAG_WEEKS}주 반영 (그 시점에 실제로 알 수 있던 값만)",
        ],
        "current": {"week": y.index[-1].date().isoformat(), "value": round(float(y.iloc[-1]), 2)},
        "variants": variants,
        "pass": passed,
        "verdict": "합격" if passed else "불합격",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"  ✅ {OUT.relative_to(ROOT.parent)} — 판정: {payload['verdict']}")


if __name__ == "__main__":
    main()
