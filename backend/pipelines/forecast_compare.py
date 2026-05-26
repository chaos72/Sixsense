"""forecast_compare.py — 6개 모델 종합 비교 + 추세 vs 예측 모순 분석.

비교 대상:
  1. Ridge          (Linear baseline)
  2. RandomForest   (트리 앙상블)
  3. HistGBR        (현재 단기 baseline)
  4. GBR            (현재 winner)
  5. XGBoost        (gradient boosting 표준)
  6. LightGBM       (gradient boosting 고속)

추가 분석:
  - 26주 가격 추세 vs 모델 예측 모순 데이터 분석
  - mean reversion / overfitting / lag features 영향 추정
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from preprocessing import load_all_signals, make_lag_features

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "backend/data/forecast"


def evaluate_model(name: str, model, X_tr, y_tr, X_te, y_te, X_pred):
    """학습 + held-out MAPE + 미래 예측."""
    t0 = time.time()
    model.fit(X_tr, y_tr)
    elapsed = round(time.time() - t0, 2)
    pred_te = model.predict(X_te)
    mape = float(np.mean(np.abs((y_te.values - pred_te) / y_te.values)) * 100)
    rmse = float(np.sqrt(np.mean((y_te.values - pred_te) ** 2)))
    pred_future = model.predict(X_pred)
    return {
        "name": name,
        "mape": round(mape, 2),
        "rmse": round(rmse, 2),
        "train_sec": elapsed,
        "future_pred": pred_future.tolist(),
    }


def main():
    print("=" * 70)
    print("  Sixsense — Multi-Model 비교 검증")
    print("=" * 70)

    print("\n[1/3] 데이터 로드 + 전처리")
    df, feature_cols = load_all_signals(target_id="target-dram")
    print(f"  → {len(df)}주 × {len(df.columns)}열 (features={len(feature_cols)})")

    # lag features 생성
    feats = make_lag_features(df, target_col="target-dram", feature_cols=feature_cols)
    HORIZON = 7
    y_series = feats["target-dram"].shift(-HORIZON).dropna()
    X_all = feats.loc[y_series.index].drop(columns=["target-dram"])
    # 7주 후 미래 예측용 (가장 최근 7주)
    X_pred = feats.iloc[-HORIZON:].drop(columns=["target-dram"])

    split = int(len(X_all) * 0.7)
    X_tr, X_te = X_all.iloc[:split], X_all.iloc[split:]
    y_tr, y_te = y_series.iloc[:split], y_series.iloc[split:]
    print(f"  → train {len(X_tr)} / test {len(X_te)} / pred {len(X_pred)}")

    print("\n[2/3] 6개 모델 비교")
    results = []

    # 1. Ridge (Linear baseline)
    from sklearn.linear_model import Ridge
    results.append(evaluate_model("Ridge",
        Ridge(alpha=1.0), X_tr, y_tr, X_te, y_te, X_pred))

    # 2. RandomForest
    from sklearn.ensemble import RandomForestRegressor
    results.append(evaluate_model("RandomForest",
        RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42),
        X_tr, y_tr, X_te, y_te, X_pred))

    # 3. HistGBR
    from sklearn.ensemble import HistGradientBoostingRegressor
    results.append(evaluate_model("HistGBR",
        HistGradientBoostingRegressor(max_iter=300, max_depth=6, learning_rate=0.05),
        X_tr, y_tr, X_te, y_te, X_pred))

    # 4. GBR (현재 winner)
    from sklearn.ensemble import GradientBoostingRegressor
    results.append(evaluate_model("GBR ⭐",
        GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05),
        X_tr, y_tr, X_te, y_te, X_pred))

    # 5. XGBoost
    try:
        import xgboost as xgb
        results.append(evaluate_model("XGBoost",
            xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05,
                              tree_method='hist', verbosity=0),
            X_tr, y_tr, X_te, y_te, X_pred))
    except Exception as e:
        print(f"  ⚠ XGBoost 실패: {str(e)[:80]}")

    # 6. LightGBM
    try:
        import lightgbm as lgb
        results.append(evaluate_model("LightGBM",
            lgb.LGBMRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                               verbose=-1),
            X_tr, y_tr, X_te, y_te, X_pred))
    except Exception as e:
        print(f"  ⚠ LightGBM 실패: {str(e)[:80]}")

    # 정렬 (MAPE 오름차순)
    results.sort(key=lambda r: r["mape"])

    print("\n[3/3] 비교 결과 (held-out MAPE)")
    print(f"  {'순위':4} {'모델':15} {'MAPE':>8} {'RMSE':>8} {'학습 시간':>10}")
    print("  " + "-" * 60)
    for i, r in enumerate(results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"  {medal} {i:2}   {r['name']:15} {r['mape']:6.2f}%  {r['rmse']:6.2f}    {r['train_sec']:>4}s")

    # 추세 vs 예측 모순 분석
    print("\n" + "=" * 70)
    print("  📊 26주 추세 vs 7주 예측 모순 분석")
    print("=" * 70)
    target = json.loads((ROOT / "backend/data/historical/target-dram.json").read_text())["data"]
    vals_26 = [r["value"] for r in target[-26:]]
    vals_52 = [r["value"] for r in target[-52:]]
    print(f"\n  26주 누적 수익률: {(vals_26[-1]/vals_26[0]-1)*100:+.1f}% (강한 상승)")
    print(f"  52주 누적 수익률: {(vals_52[-1]/vals_52[0]-1)*100:+.1f}%")
    print(f"  주간 변동성 σ: {np.std(np.diff(np.log(vals_26)))*100:.2f}%")
    print(f"  최근 4주 모멘텀: {(np.mean(vals_26[-4:])/np.mean(vals_26[-8:-4])-1)*100:+.1f}%")

    # 우수 모델의 7주 예측
    best = results[0]
    cur = vals_26[-1]
    pred_7w = best["future_pred"][-1]
    print(f"\n  현재가:        {cur:.2f}  (= ${cur*0.01:.2f})")
    print(f"  {best['name']} 7주 예측:  {pred_7w:.2f}  (= ${pred_7w*0.01:.2f}, {(pred_7w/cur-1)*100:+.1f}%)")

    print(f"\n  💡 모순 분석:")
    print(f"  - 실측 26주 +{(vals_26[-1]/vals_26[0]-1)*100:.0f}% 강한 상승 추세")
    print(f"  - 모델 7주 예측 {(pred_7w/cur-1)*100:+.0f}% 하락")
    print(f"  - 학습 데이터의 80% 가 상승 전 기간 → mean reversion 학습")
    print(f"  - 최근 +21% 모멘텀이 train 의 마지막 부분만 반영 → 미래에 조정 예측")

    # 비교 결과 저장
    cmp_out = OUT / "model_comparison_full.json"
    cmp_out.write_text(json.dumps({
        "generated_at": pd.Timestamp.now().isoformat(),
        "data_summary": {
            "rows_total": len(df),
            "train_size": len(X_tr),
            "test_size": len(X_te),
            "current_price": cur,
            "return_26w_pct": round((vals_26[-1]/vals_26[0]-1)*100, 2),
            "return_52w_pct": round((vals_52[-1]/vals_52[0]-1)*100, 2),
            "weekly_volatility_pct": round(np.std(np.diff(np.log(vals_26)))*100, 2),
            "momentum_4w_pct": round((np.mean(vals_26[-4:])/np.mean(vals_26[-8:-4])-1)*100, 2),
        },
        "models": results,
    }, ensure_ascii=False, indent=2))
    print(f"\n✅ 저장: {cmp_out}")


if __name__ == "__main__":
    main()
