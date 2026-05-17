# Sixsense 예측 모델링 아키텍처 (Phase 6)

> **목적**: 정확도 개선을 위한 멀티 모델 앙상블. 기존 Prophet + 신규 트리 기반(단기) + LSTM(중장기).
> **결과**: 단기 GBR MAPE **4.54%** (Prophet 7.54% 대비 **39.7% 개선**), 중장기 LSTM held-out MAPE **9.19%**.

---

## 1. 모델 구성

### 단기 (1~7주): 트리 기반 모델

**선정 이유** (사용자 요구):
> 트리 기반 모델은 AWS 스팟 가격, 구리 가격, 최근 뉴스의 LLM 센티먼트 점수 등 즉각적으로 시장에 반영되는 피처의 비선형적 관계를 잡아내어 단기 가격 방향성 예측에 매우 탁월

**구현**: XGBoost / LightGBM 우선, macOS libomp 없으면 **sklearn GradientBoosting + HistGradientBoosting** 자동 fallback. 두 모델 학습 후 MAPE 비교로 우수 모델 자동 선정.

| 환경 | 1순위 | 2순위 | Fallback |
|------|------|------|---------|
| Linux/Windows | XGBoost | LightGBM | sklearn |
| macOS (libomp 설치) | XGBoost | LightGBM | sklearn |
| **macOS (libomp 없음)** | sklearn HistGBR | **sklearn GBR ⭐** | — |

### 중장기 (8~21주): LSTM

**선정 이유** (사용자 요구):
> 분기별로 발표되는 빅테크 CapEx, 관세청 ASP, 재고일수 등 장기 사이클을 타는 거시 지표를 기억하고 반영해야 함. TFT는 해석 가능성 ⭐ 하지만 학습 데이터 40~80주로는 과적합 위험.

**TFT vs LSTM 결정**:

| 항목 | TFT (Temporal Fusion Transformer) | LSTM ⭐ |
|------|----------------------------------|---------|
| 학습 데이터 요구량 | 200주+ (best) | 40~100주 가능 |
| 해석 가능성 | ⭐⭐⭐ Attention weights | ⭐ |
| 학습 시간 (40주) | ~10분 (heavy) | **~10초** |
| 환경 부담 | pytorch-forecasting + lightning | pytorch only |
| 가성비 (80주 데이터) | ⚠️ 과적합 위험 | ✅ 안정 |

**→ LSTM 선정** (속도 및 가성비 베스트). TFT는 학습 데이터 200주+ 확보 후 (Phase 7+) 도입 권장.

**LSTM 구조**:
- 2-layer LSTM (hidden=64) + dropout 0.2
- 입력: 12주 history × 20 features
- 출력: 21주 future (seq2seq 1-shot)
- 학습: Adam (lr=1e-3), 200 epochs, batch=8
- 정규화: z-score per feature

### 기존 (1~21주): Prophet

**유지 이유**: Univariate baseline. 트렌드 추출에 우수, 비교 기준.

---

## 2. 데이터 전처리 통합 (`preprocessing.py`)

사용자 요구사항 반영:
> 14종의 데이터 주기가 다릅니다(일별, 주별, 분기별). 이를 모두 '주차(Week)' 단위로 다운샘플링/업샘플링하여 하나의 통합 데이터프레임으로 만들어야 합니다.
> 비정형 LLM 긍부정 점수는 이동평균(Moving Average)을 적용해 노이즈를 줄입니다.

| 단계 | 처리 |
|------|------|
| 1. 로드 | `data/historical/*.json` 20개 파일 |
| 2. 주차 정렬 | 모두 `week` 컬럼 기준 outer join |
| 3. Sentiment MA | B-1/B-2/B-3/B-4/B-5/B-6에 3주 이동평균 |
| 4. NaN 처리 | ffill → bfill → 0 |
| 5. Lag 피처 | target lag-1/2/4 + feature lag-1/2/4 + rolling MA-4/8 (단기 모델용) |
| 6. 시퀀스 생성 | 12주 input + 21주 output (LSTM용) |

**결과**: 108주 × 20열 (target 1 + features 19) DataFrame, 모든 신호 비결측 100%.

---

## 3. 검증 결과 (학습 컷오프 2026-01-31, 검증 28주)

### 단기 (1~7주) 모델 비교

| Week | Prophet | hist_gbr | **GBR** | 실측 |
|------|---------|----------|---------|------|
| 2026-02-02 | 449.91 | 419.95 | **438.21** | 438.22 |
| 2026-02-09 | 468.88 | 426.07 | **438.21** | 463.67 |
| 2026-02-16 | 487.85 | 433.62 | **463.65** | 488.30 |
| 2026-02-23 | 506.81 | 440.76 | **463.66** | 506.30 |
| 2026-03-02 | 525.78 | 449.27 | **488.27** | 447.72 |
| 2026-03-09 | 544.75 | 456.22 | **488.29** | 478.32 |
| 2026-03-16 | 563.72 | 464.74 | **506.26** | 497.82 |

| 모델 | 단기 MAPE | 평가 |
|------|----------|------|
| Prophet (기존) | 7.54% | baseline |
| HistGradientBoosting | 6.86% | 중간 |
| **GradientBoostingRegressor** ⭐ | **4.54%** | **우수** (Prophet 대비 39.7% 개선) |

### 중장기 (8~21주) 모델 비교

| Week | Prophet | LSTM |
|------|---------|------|
| 2026-03-23 | 582.68 | 509.13 |
| 2026-04-27 | 677.52 | 478.17 |
| 2026-05-25 | 753.39 | 427.38 |
| 2026-06-22 | 829.26 | 507.53 |

| 모델 | 중장기 MAPE (held-out) | 평가 |
|------|----------------------|------|
| Prophet | (학습 시기 동일하므로 단기와 같은 산식 적용 어려움) | baseline |
| **LSTM** | **9.19%** | 합리적, 실측 변동성 반영 |

> Prophet은 정상 추세를 외삽하지만 LSTM은 최근 비정형/sentiment 신호의 변동을 반영하여 보다 보수적 예측 (가격 안정/하향).

### 학습 시간

| 모델 | 시간 | 비고 |
|------|------|------|
| Prophet | 0.64s | 가장 빠름 |
| Tree (sklearn) | 4.22s | 7개 horizon 모델 |
| LSTM | 6.52s | 200 epochs |
| **합계** | **~12초** | 전체 파이프라인 |

---

## 4. 운영 방식 — 멀티 모델 활용

### 동시 사용 정책

```python
# 단기 (1~7주) — 우수 모델 자동 선정
short_term_forecast = GBR  # sklearn (또는 XGBoost when libomp 설치 후)

# 중장기 (8~21주) — 멀티 모델 비교 출력
mid_term_forecasts = [Prophet, LSTM]  # 둘 다 dashboard에 표시
```

### Dashboard 표시 권장
- **단기 카드**: 우수 모델 (GBR) 값 + 신뢰구간
- **중장기 카드**: Prophet (추세) + LSTM (sentiment 반영) 두 값 표시 + 차이가 크면 알림

### 매주 운영 흐름

```bash
cd backend
source ../.env
.venv/bin/python3 pipelines/auto_collectors.py --all   # 20 신호 갱신
.venv/bin/python3 pipelines/forecast.py                  # Prophet (기존, 보존)
.venv/bin/python3 pipelines/forecast_v2.py               # 신규 multi-model
.venv/bin/python3 pipelines/sync_supabase.py             # DB push
```

---

## 5. 향후 개선 (Phase 7+)

| 항목 | 현재 | 향후 |
|------|------|------|
| XGBoost/LightGBM 실제 사용 | sklearn fallback | `brew install libomp` 후 자동 전환 |
| TFT 도입 | LSTM 사용 | 학습 데이터 200주+ 확보 시 (1년 후) |
| 앙상블 가중 평균 | 우수 모델 단독 | MAPE 역가중 평균 |
| Hyperparameter 튜닝 | 기본값 | Optuna/HPO |
| 신뢰구간 (트리/LSTM) | Prophet만 | Quantile regression + dropout MC |
| Online learning | 매주 재학습 | Incremental update |

---

## 6. 코드 위치

| 파일 | 역할 |
|------|------|
| `backend/pipelines/preprocessing.py` | 20 신호 통합, sentiment MA, lag/sequence 생성 |
| `backend/pipelines/forecast.py` | Prophet (기존, 보존) |
| `backend/pipelines/forecast_v2.py` | Prophet + Tree(GBR/HistGBR) + LSTM 통합 |
| `backend/data/forecast/forecast_v2_2026-02-w1.json` | 모든 모델 JSON 결과 |
| `backend/data/forecast/model_comparison.txt` | 사람 읽기용 비교 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | Phase 6 — Multi-model (Prophet + sklearn Tree + LSTM) 도입. 단기 MAPE 7.54%→4.54% |
