"""Sixsense Phase 6 — 통합 시계열 전처리.

설계 요구사항 (사용자 제공):
- 14신호 + 5거시 + 1타겟 = 20개 시계열
- 다양한 주기 (일별/주별/분기별) → 주간 통일
- 비정형 sentiment (B-1/B-2/B-3/B-4/B-5/B-6) → 이동평균(MA)으로 노이즈 감소
- NaN forward-fill + back-fill

출력: pandas DataFrame (week index + 20 columns)
"""
import json
from pathlib import Path
from typing import Optional

import pandas as pd

HIST_DIR = Path(__file__).parent.parent / "data" / "historical"

# Sentiment 신호 (이동평균 적용)
SENTIMENT_SIGNALS = {"B-1", "B-2", "B-3", "B-4", "B-5", "B-6"}

# 분기/월간 신호 (forward-fill 자연스러움)
LOW_FREQ_SIGNALS = {"A-2", "A-3", "A-4", "macro-pmi"}


def load_all_signals(target_id: str = "target-dram") -> tuple[pd.DataFrame, list[str]]:
    """모든 신호 파일을 한 DataFrame으로 통합.

    Returns:
        df: DatetimeIndex (week), columns = [target, A-1, ..., macro-cu]
        feature_cols: target 제외 19개 신호 ID
    """
    files = sorted([f for f in HIST_DIR.glob("*.json") if not f.name.startswith("_")])
    if not files:
        raise RuntimeError(f"{HIST_DIR}에 신호 파일 없음 — backfill 먼저 실행")

    frames = {}
    for fp in files:
        try:
            j = json.loads(fp.read_text())
            sid = j["signalId"]
            df = pd.DataFrame(j["data"])
            df["week"] = pd.to_datetime(df["week"])
            df = df[["week", "value"]].rename(columns={"value": sid}).set_index("week")
            frames[sid] = df
        except Exception as e:
            print(f"  ⚠️ {fp.name} skip: {e}")

    if target_id not in frames:
        raise RuntimeError(f"타겟 {target_id} 없음")

    # outer join — 모든 주차 합집합
    merged = pd.concat(frames.values(), axis=1).sort_index()
    merged = merged.asfreq("W-MON", method=None) if False else merged

    # NaN 처리: forward-fill → back-fill → 0
    # (sentiment 신호는 이동평균 후 추가 ffill로 노이즈 완화)
    for sid in SENTIMENT_SIGNALS & set(merged.columns):
        # 3주 이동평균 (centered=False, min_periods=1)
        merged[sid] = merged[sid].rolling(window=3, min_periods=1).mean()

    merged = merged.ffill().bfill().fillna(0)

    feature_cols = [c for c in merged.columns if c != target_id]
    # 일관된 순서로 정렬
    feature_cols.sort()

    return merged, feature_cols


def make_lag_features(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    lags: list[int] = None,
    rolling_windows: list[int] = None,
) -> pd.DataFrame:
    """단기 모델용 lag + rolling 피처 생성.

    각 feature에 대해:
    - lag-1, lag-2, lag-4 (직전 주, 2주 전, 4주 전)
    - rolling mean (4주, 8주)
    """
    if lags is None:
        lags = [1, 2, 4]
    if rolling_windows is None:
        rolling_windows = [4, 8]

    out = df.copy()
    # target lag (자기회귀 컴포넌트)
    for lag in lags:
        out[f"{target_col}_lag{lag}"] = out[target_col].shift(lag)

    # feature lag + rolling
    for col in feature_cols:
        for lag in lags:
            out[f"{col}_lag{lag}"] = out[col].shift(lag)
        for w in rolling_windows:
            out[f"{col}_ma{w}"] = out[col].rolling(window=w, min_periods=1).mean().shift(1)

    # target rolling features
    for w in rolling_windows:
        out[f"{target_col}_ma{w}"] = out[target_col].rolling(window=w, min_periods=1).mean().shift(1)

    return out.dropna()


def make_sequences(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    seq_len: int = 12,
    horizon: int = 21,
) -> tuple:
    """LSTM/TFT용 시퀀스 데이터 생성.

    Returns:
        X: (n_samples, seq_len, n_features)  - 과거 seq_len 주의 features
        Y: (n_samples, horizon)              - 미래 horizon 주의 target
        dates: (n_samples,)                  - 각 sample의 예측 시작 주
    """
    import numpy as np
    X, Y, dates = [], [], []
    cols = feature_cols + [target_col]
    arr = df[cols].values
    target_arr = df[target_col].values
    for i in range(len(df) - seq_len - horizon + 1):
        X.append(arr[i : i + seq_len])
        Y.append(target_arr[i + seq_len : i + seq_len + horizon])
        dates.append(df.index[i + seq_len])
    return np.array(X), np.array(Y), pd.DatetimeIndex(dates)


if __name__ == "__main__":
    df, fcols = load_all_signals()
    print(f"통합 DataFrame: {df.shape} | target=target-dram | features={len(fcols)}")
    print(f"기간: {df.index.min().date()} ~ {df.index.max().date()}")
    print(f"\n신호별 비결측 비율:")
    for c in df.columns:
        nn = df[c].notna().sum()
        print(f"  {c:12} {nn:3}/{len(df)} ({nn/len(df)*100:.0f}%)")
