#!/usr/bin/env python3
"""Sixsense Phase 6 — 통합 forecast 파이프라인 v2.

3 모델 병렬 학습 + 비교:
1. Prophet (기존, baseline) — 단기/중장기 통합
2. XGBoost vs LightGBM (단기 1~7w) → 우수 모델 자동 선정
3. LSTM (중장기 8~21w)

출력:
- backend/data/forecast/forecast_v2_2026-02-w1.json (모든 모델 결과)
- backend/data/forecast/model_comparison.txt (사람 읽기용 비교)
"""
import json
import sys
import time
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))
from preprocessing import load_all_signals, make_lag_features, make_sequences

OUT_DIR = Path(__file__).parent.parent / "data" / "forecast"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "target-dram"
TRAIN_CUTOFF = pd.Timestamp("2026-01-31")
SHORT_H = 7
MID_H = 21


# ──────────────────────────────────────────────────────────────────────────────
# 평가 metric
# ──────────────────────────────────────────────────────────────────────────────
def mape(actual: np.ndarray, pred: np.ndarray) -> float:
    actual, pred = np.array(actual), np.array(pred)
    mask = actual != 0
    if mask.sum() == 0:
        return float("inf")
    return float(np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask]) * 100))


# ──────────────────────────────────────────────────────────────────────────────
# 1. Prophet (기존, baseline)
# ──────────────────────────────────────────────────────────────────────────────
def train_prophet(df: pd.DataFrame, target: str) -> dict:
    from prophet import Prophet
    train = df[df.index <= TRAIN_CUTOFF].reset_index().rename(columns={"week": "ds", target: "y"})
    m = Prophet(
        weekly_seasonality=False, yearly_seasonality=False, daily_seasonality=False,
        growth="linear", changepoint_prior_scale=0.05, interval_width=0.80, n_changepoints=8,
    )
    m.fit(train[["ds", "y"]])
    future = m.make_future_dataframe(periods=MID_H, freq="W-MON")
    fcst = m.predict(future)
    fcst_only = fcst[fcst["ds"] > TRAIN_CUTOFF].head(MID_H)
    return {
        "model": "Prophet (univariate)",
        "predictions": [
            {"week": r["ds"].date().isoformat(),
             "yhat": float(r["yhat"]),
             "yhat_lower": float(r["yhat_lower"]),
             "yhat_upper": float(r["yhat_upper"])}
            for _, r in fcst_only.iterrows()
        ],
    }


# ──────────────────────────────────────────────────────────────────────────────
# 2. XGBoost vs LightGBM (단기, 1~7w)
# ──────────────────────────────────────────────────────────────────────────────
def train_tree_short(df: pd.DataFrame, target: str, fcols: list[str]) -> dict:
    """Direct multi-horizon — 1~7w 각각 별도 모델.

    XGBoost/LightGBM 우선 → 둘 다 OpenMP 필요 (macOS: brew install libomp).
    실패 시 sklearn HistGradientBoosting (OpenMP 무관) + GradientBoosting fallback.
    """
    # 모델 import — OpenMP 사용 가능 여부 dummy fit으로 검증
    use_xgb_lgb = True
    try:
        import xgboost as xgb
        import lightgbm as lgb
        # dummy fit으로 dylib 실제 load 확인
        _xa = xgb.XGBRegressor(n_estimators=2, verbosity=0)
        _xa.fit(np.array([[1.0], [2.0], [3.0]]), np.array([1.0, 2.0, 3.0]))
        _xb = lgb.LGBMRegressor(n_estimators=2, verbose=-1)
        _xb.fit(np.array([[1.0], [2.0], [3.0]]), np.array([1.0, 2.0, 3.0]))
        model_a_name, model_b_name = "xgboost", "lightgbm"
        def make_a(): return xgb.XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05,
                                              objective="reg:squarederror", random_state=42,
                                              n_jobs=-1, verbosity=0)
        def make_b(): return lgb.LGBMRegressor(n_estimators=200, max_depth=4, learning_rate=0.05,
                                               random_state=42, n_jobs=-1, verbose=-1)
    except Exception as e:
        print(f"      ⚠️ XGBoost/LightGBM 미지원: {str(e)[:100]}")
        print(f"      → sklearn HistGradientBoosting + GradientBoosting fallback")
        use_xgb_lgb = False
        from sklearn.ensemble import HistGradientBoostingRegressor, GradientBoostingRegressor
        model_a_name, model_b_name = "hist_gbr", "gbr"
        def make_a(): return HistGradientBoostingRegressor(max_iter=200, max_depth=4, learning_rate=0.05, random_state=42)
        def make_b(): return GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)

    feat_df = make_lag_features(df, target, fcols)
    train_mask = feat_df.index <= TRAIN_CUTOFF
    if train_mask.sum() < 20:
        raise RuntimeError(f"학습 데이터 부족: {train_mask.sum()}주")

    # 각 horizon h에 대해 target_{t+h}를 예측
    results = {model_a_name: [], model_b_name: []}
    feature_only_cols = [c for c in feat_df.columns if c != target]

    for h in range(1, SHORT_H + 1):
        y_h = feat_df[target].shift(-h)
        X = feat_df[feature_only_cols]
        valid = y_h.notna()
        X_tr, y_tr = X.loc[valid & train_mask], y_h.loc[valid & train_mask]
        if len(X_tr) < 10:
            continue

        m_a = make_a(); m_a.fit(X_tr, y_tr)
        m_b = make_b(); m_b.fit(X_tr, y_tr)

        last_feat = X.loc[feat_df.index == TRAIN_CUTOFF]
        if len(last_feat) == 0:
            last_feat = X[X.index <= TRAIN_CUTOFF].tail(1)
        pred_a = float(m_a.predict(last_feat)[0])
        pred_b = float(m_b.predict(last_feat)[0])

        target_week = TRAIN_CUTOFF + pd.Timedelta(weeks=h)
        target_week = target_week - pd.Timedelta(days=target_week.weekday())
        results[model_a_name].append({"week": target_week.date().isoformat(), "yhat": pred_a, "horizon": h})
        results[model_b_name].append({"week": target_week.date().isoformat(), "yhat": pred_b, "horizon": h})

    # 사후 검증으로 우수 모델 선정
    actuals = []
    for h in range(1, SHORT_H + 1):
        target_week = TRAIN_CUTOFF + pd.Timedelta(weeks=h)
        target_week = target_week - pd.Timedelta(days=target_week.weekday())
        # df에서 해당 주차 실측값
        match = df[df.index == target_week]
        if len(match) > 0:
            actuals.append(float(match[target].iloc[0]))
        else:
            actuals.append(None)

    a_preds = [p["yhat"] for p in results[model_a_name]]
    b_preds = [p["yhat"] for p in results[model_b_name]]
    valid_pairs = [(a, x, l) for a, x, l in zip(actuals, a_preds, b_preds) if a is not None]
    if valid_pairs:
        a_arr, x_arr, l_arr = zip(*valid_pairs)
        a_mape = mape(a_arr, x_arr)
        b_mape = mape(a_arr, l_arr)
        winner = model_a_name if a_mape <= b_mape else model_b_name
    else:
        a_mape = b_mape = float("nan")
        winner = model_a_name

    return {
        "models": results,
        "model_a_name": model_a_name,
        "model_b_name": model_b_name,
        "engine": "xgb+lgb" if use_xgb_lgb else "sklearn (libomp 없음 fallback)",
        "validation": {
            f"{model_a_name}_mape": round(a_mape, 2) if not np.isnan(a_mape) else None,
            f"{model_b_name}_mape": round(b_mape, 2) if not np.isnan(b_mape) else None,
            "winner": winner,
            "actuals": [{"week": (TRAIN_CUTOFF + pd.Timedelta(weeks=h)
                                  - pd.Timedelta(days=(TRAIN_CUTOFF + pd.Timedelta(weeks=h)).weekday())
                                  ).date().isoformat(),
                         "actual": a} for h, a in zip(range(1, SHORT_H+1), actuals) if a is not None],
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# 3. LSTM (중장기, 8~21w)
# ──────────────────────────────────────────────────────────────────────────────
def train_lstm_mid(df: pd.DataFrame, target: str, fcols: list[str]) -> dict:
    """PyTorch LSTM — 12주 history → 21주 future. seq2seq 1-shot."""
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    SEQ_LEN = 12

    X, Y, dates = make_sequences(df, target, fcols, seq_len=SEQ_LEN, horizon=MID_H)
    if len(X) < 10:
        raise RuntimeError(f"LSTM 시퀀스 부족: {len(X)}")

    # train/eval split by date
    train_mask = dates <= TRAIN_CUTOFF
    X_tr, Y_tr = X[train_mask], Y[train_mask]
    if len(X_tr) < 5:
        # Cutoff 너무 이르면 모든 가능 시퀀스로 학습
        X_tr, Y_tr = X[:max(5, len(X)-1)], Y[:max(5, len(X)-1)]

    # Normalize (z-score per feature)
    mean = X_tr.mean(axis=(0, 1), keepdims=True)
    std = X_tr.std(axis=(0, 1), keepdims=True) + 1e-8
    y_mean = Y_tr.mean()
    y_std = Y_tr.std() + 1e-8
    Xn_tr = (X_tr - mean) / std
    Yn_tr = (Y_tr - y_mean) / y_std

    device = "cpu"
    torch.manual_seed(42)

    class LSTMForecaster(nn.Module):
        def __init__(self, n_feat: int, hidden: int = 64, horizon: int = MID_H):
            super().__init__()
            self.lstm = nn.LSTM(n_feat, hidden, num_layers=2, batch_first=True, dropout=0.2)
            self.head = nn.Linear(hidden, horizon)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.head(out[:, -1, :])

    n_feat = X_tr.shape[-1]
    model = LSTMForecaster(n_feat).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    Xt = torch.tensor(Xn_tr, dtype=torch.float32).to(device)
    Yt = torch.tensor(Yn_tr, dtype=torch.float32).to(device)

    EPOCHS = 200
    BATCH = 8
    ds = TensorDataset(Xt, Yt)
    loader = DataLoader(ds, batch_size=BATCH, shuffle=True)

    model.train()
    for ep in range(EPOCHS):
        for xb, yb in loader:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()

    # 예측: 학습 컷오프 시점의 마지막 SEQ_LEN주를 입력으로
    cutoff_idx = df.index.get_indexer([TRAIN_CUTOFF], method="ffill")[0]
    seq_input = df[fcols + [target]].iloc[cutoff_idx - SEQ_LEN + 1 : cutoff_idx + 1].values
    seq_norm = (seq_input.reshape(1, SEQ_LEN, -1) - mean) / std
    model.eval()
    with torch.no_grad():
        pred_norm = model(torch.tensor(seq_norm, dtype=torch.float32).to(device)).cpu().numpy()[0]
    pred = pred_norm * y_std + y_mean

    # 미래 21주의 주차
    future_weeks = []
    for h in range(1, MID_H + 1):
        wk = TRAIN_CUTOFF + pd.Timedelta(weeks=h)
        wk = wk - pd.Timedelta(days=wk.weekday())
        future_weeks.append(wk.date().isoformat())

    predictions = [{"week": w, "yhat": float(p), "horizon": h+1}
                   for h, (w, p) in enumerate(zip(future_weeks, pred))]

    # 사후 검증 — 학습에 사용하지 않은 시퀀스로 MAPE
    test_mask = ~train_mask
    test_mape = None
    if test_mask.sum() > 0:
        X_te, Y_te = X[test_mask], Y[test_mask]
        Xn_te = (X_te - mean) / std
        with torch.no_grad():
            Pn_te = model(torch.tensor(Xn_te, dtype=torch.float32).to(device)).cpu().numpy()
        P_te = Pn_te * y_std + y_mean
        # 21주 평균 MAPE
        mapes = []
        for i in range(len(Y_te)):
            m_i = mape(Y_te[i], P_te[i])
            if not np.isinf(m_i):
                mapes.append(m_i)
        if mapes:
            test_mape = float(np.mean(mapes))

    return {
        "model": "LSTM (PyTorch, 2-layer, hidden=64, seq=12)",
        "predictions": predictions,
        "validation": {"avg_mape_held_out": round(test_mape, 2) if test_mape else None},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main: 모든 모델 학습 + 비교
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'═'*80}")
    print(f"  Sixsense Phase 6 — 통합 Forecast (Prophet + XGB/LGB + LSTM)")
    print(f"  학습 컷오프: {TRAIN_CUTOFF.date()}")
    print(f"{'═'*80}\n")

    df, fcols = load_all_signals(TARGET)
    print(f"  📊 통합 데이터: {df.shape[0]}주 × {df.shape[1]}열")
    print(f"      기간: {df.index.min().date()} ~ {df.index.max().date()}\n")

    # 학습/검증 분리
    n_train = (df.index <= TRAIN_CUTOFF).sum()
    n_val = (df.index > TRAIN_CUTOFF).sum()
    print(f"      Train: {n_train}주, Validation: {n_val}주\n")

    results = {"trainedAt": date.today().isoformat(), "trainCutoff": str(TRAIN_CUTOFF.date()),
               "models": {}}

    # 1. Prophet
    print(f"  🔵 [1/3] Prophet 학습 중...")
    t0 = time.time()
    try:
        prophet_out = train_prophet(df, TARGET)
        prophet_out["elapsed_sec"] = round(time.time() - t0, 2)
        results["models"]["prophet"] = prophet_out
        print(f"      ✅ 완료 ({prophet_out['elapsed_sec']}s)")
    except Exception as e:
        print(f"      ❌ 실패: {e}")
        results["models"]["prophet"] = {"error": str(e)}

    # 2. XGBoost vs LightGBM
    print(f"\n  🟢 [2/3] XGBoost + LightGBM 학습 중 (단기 1~7w)...")
    t0 = time.time()
    try:
        tree_out = train_tree_short(df, TARGET, fcols)
        tree_out["elapsed_sec"] = round(time.time() - t0, 2)
        results["models"]["tree_short"] = tree_out
        v = tree_out["validation"]
        ma, mb = tree_out["model_a_name"], tree_out["model_b_name"]
        print(f"      ✅ 완료 ({tree_out['elapsed_sec']}s) — engine={tree_out['engine']}")
        print(f"         {ma} MAPE: {v.get(f'{ma}_mape')}% | {mb} MAPE: {v.get(f'{mb}_mape')}%")
        print(f"         🏆 우수 모델: {v['winner'].upper()}")
    except Exception as e:
        print(f"      ❌ 실패: {e}")
        results["models"]["tree_short"] = {"error": str(e)}

    # 3. LSTM
    print(f"\n  🟣 [3/3] LSTM 학습 중 (중장기 8~21w)...")
    t0 = time.time()
    try:
        lstm_out = train_lstm_mid(df, TARGET, fcols)
        lstm_out["elapsed_sec"] = round(time.time() - t0, 2)
        results["models"]["lstm_mid"] = lstm_out
        print(f"      ✅ 완료 ({lstm_out['elapsed_sec']}s)")
        v = lstm_out["validation"]
        if v.get("avg_mape_held_out"):
            print(f"         Held-out 평균 MAPE: {v['avg_mape_held_out']}%")
    except Exception as e:
        print(f"      ❌ 실패: {e}")
        import traceback; traceback.print_exc()
        results["models"]["lstm_mid"] = {"error": str(e)}

    # 저장
    out_path = OUT_DIR / "forecast_v2_2026-02-w1.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n  📁 결과 저장: {out_path.name}")

    # 비교 텍스트
    lines = ["═" * 80,
             "  Sixsense Phase 6 — 모델 비교 (2026-02-w1 시작 예측)",
             f"  학습 데이터: {n_train}주 (~{TRAIN_CUTOFF.date()}), 검증: {n_val}주",
             "═" * 80, ""]

    # 단기 비교 (1~7w)
    tree_meta = results["models"].get("tree_short", {})
    ma_name = tree_meta.get("model_a_name", "model_a")
    mb_name = tree_meta.get("model_b_name", "model_b")
    lines.append("📈 단기 예측 비교 (1~7주)")
    lines.append(f"{'Week':14} {'Prophet':>10} {ma_name:>12} {mb_name:>12} {'실측':>10}")
    lines.append("-" * 70)
    p_short = results["models"].get("prophet", {}).get("predictions", [])[:SHORT_H]
    t_a = tree_meta.get("models", {}).get(ma_name, [])
    t_b = tree_meta.get("models", {}).get(mb_name, [])
    actuals = {a["week"]: a["actual"] for a in tree_meta.get("validation", {}).get("actuals", [])}
    for i in range(SHORT_H):
        wk = p_short[i]["week"] if i < len(p_short) else "-"
        p = p_short[i]["yhat"] if i < len(p_short) else None
        x = t_a[i]["yhat"] if i < len(t_a) else None
        l = t_b[i]["yhat"] if i < len(t_b) else None
        a = actuals.get(wk)
        line = f"{wk:14}"
        for v, w in zip((p, x, l, a), (10, 12, 12, 10)):
            line += f" {v:{w}.2f}" if v is not None else f" {'-':>{w}}"
        lines.append(line)

    if tree_meta and "validation" in tree_meta:
        v = tree_meta["validation"]
        lines.append("")
        lines.append(f"단기 MAPE — {ma_name}: {v.get(f'{ma_name}_mape')}%, {mb_name}: {v.get(f'{mb_name}_mape')}%")
        lines.append(f"🏆 단기 우수 모델: {v['winner'].upper()}")

    # 중장기 비교
    lines.append("")
    lines.append("📈 중장기 예측 (8~21주)")
    lines.append(f"{'Week':14} {'Prophet':>10} {'LSTM':>10}")
    lines.append("-" * 50)
    p_mid = results["models"].get("prophet", {}).get("predictions", [])[SHORT_H:]
    lstm_pred = results["models"].get("lstm_mid", {}).get("predictions", [])
    for i in range(MID_H - SHORT_H):
        wk = p_mid[i]["week"] if i < len(p_mid) else "-"
        p = p_mid[i]["yhat"] if i < len(p_mid) else None
        l = lstm_pred[SHORT_H + i]["yhat"] if SHORT_H + i < len(lstm_pred) else None
        line = f"{wk:14}"
        for v in (p, l):
            line += f" {v:10.2f}" if v is not None else f" {'-':>10}"
        lines.append(line)

    if "lstm_mid" in results["models"] and "validation" in results["models"]["lstm_mid"]:
        v = results["models"]["lstm_mid"]["validation"]
        if v.get("avg_mape_held_out"):
            lines.append("")
            lines.append(f"LSTM held-out MAPE: {v['avg_mape_held_out']}%")

    # 소요 시간
    lines.append("")
    lines.append("⏱  학습 소요 시간:")
    for name, m in results["models"].items():
        if "elapsed_sec" in m:
            lines.append(f"  {name:15} {m['elapsed_sec']:.2f}s")

    lines.append("")
    lines.append("═" * 80)

    summary = "\n".join(lines)
    (OUT_DIR / "model_comparison.txt").write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()
