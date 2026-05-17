# Sixsense Data Acquisition Report — 최신 상태 (v0.5)

> **Summary**: 정형 7 + 비정형 7 + 거시 5 + 타겟 1 = 20개 신호 중 **17개 자동 수집 완료 (85%)**.
> Prophet 학습/예측 + 사후 검증 MAPE 7.54% 유지.
>
> **Date**: 2026-05-17 (v0.4 — Phase 5e 진행 중 누적 업데이트)
> **Range**: 2025-05-01 ~ 2026-04-30 (53주)
> **Train cutoff**: 2026-01-31 (40주)

---

## 1. 수집 결과 종합 (최신)

| 분류 | 신호 | 출처 | 결과 | 모드 | 추가 시점 |
|------|------|------|------|------|---------|
| **정형 (Group A)** | A-1 대만 공급망 | Yahoo Finance: TSM(70%) + UMC(30%) | ✅ **53주** | real | Phase 5c |
| | A-2 빅테크 CapEx | SEC EDGAR XBRL (META/MSFT/GOOGL/AMZN) | ✅ **53주** | real | Phase 5c |
| | A-3 관세청 메모리 수출 | data.go.kr Itemtrade HS 854232 | ✅ **53주** | real | Phase 5e ⭐ |
| | A-4 KOSIS 재고지수 | KOSIS DT_1F02012 (사용자 URL) | ✅ **53주** | real | Phase 5e ⭐ |
| | A-5 AWS EC2 Spot | boto3 m6i.xlarge us-east-1a | ✅ **11주** | real | Phase 5e ⭐ |
| | A-6 대만 침공 확률 | Manifold Markets API | ✅ **52주** | real | Phase 5e ⭐ |
| | A-7 구리 선물 | Yahoo Finance HG=F | ✅ **53주** | real | Phase 5c |
| **비정형 (Group B)** | B-1 Earnings Call | (Anthropic 크레딧 충전 + PDF 코드) | ⏸ 대기 | — | — |
| | B-2 대만 뉴스 sentiment | **TechNews.tw + Digitimes RSS** (feedparser + 키워드) | ✅ **1주+** (RSS는 최근 분량, 매주 누적) | real | Phase 5e ⭐ |
| | B-3 Reddit/HN | Hacker News Algolia 대체 | ✅ **53주** | real | Phase 5e |
| | B-4 지정학 리스크 GPR | Caldara & Iacoviello GPR Index | ✅ **53주** | real | Phase 5e |
| | B-5 LTA 비율 | (Anthropic + PDF 코드) | ⏸ 대기 | — | — |
| | B-6 HBM 비중 | (Anthropic + PDF 코드) | ⏸ 대기 | — | — |
| | B-7 BOM 신호 | Hacker News Algolia (HBM/DRAM) | ✅ **53주** | real | Phase 5e |
| **거시 (Macro)** | fed | FRED CSV DFF | ✅ **53주** | real | Phase 5c |
| | dxy | Yahoo Finance DX-Y.NYB | ✅ **53주** | real | Phase 5c |
| | pmi | FRED INDPRO (NAPM 폐기→대체) | ✅ **53주** | real | Phase 5c |
| | krw | Yahoo Finance KRW=X | ✅ **53주** | real | Phase 5c |
| | cu | Yahoo Finance HG=F | ✅ **53주** | real | Phase 5c |
| **타겟 (Y)** | target-dram | MU 50% + SK 30% + Samsung 20% | ✅ **53주** | real-proxy | Phase 5c |

### 진행 추이

| Phase | 수집 신호 | 누적 | 변화 |
|-------|----------|------|------|
| 5c 초기 백필 | 9개 | 9 (45%) | A-1/A-2/A-7 + 5거시 + 타겟 |
| 5e B-3/B-4/B-7 (무키) | +3 | 12 (60%) | Hacker News + Caldara GPR |
| 5e A-4 KOSIS | +1 | 13 (65%) | KOSIS_FULL_URL |
| 5e A-3 관세청 | +1 | 14 (70%) | Excel 코드표 정정 |
| 5e A-5 AWS | +1 | 15 (75%) | boto3 + IAM 키 |
| 5e A-6 Manifold | +1 | 16 (80%) | Polymarket/Metaculus 대안 |
| **5e B-2 RSS** ⭐ | **+1** | **17 (85%)** | **TechNews.tw + Digitimes feedparser** |

→ **현재 자동 수집 17/20 (85%)**

---

## 2. Prophet 예측 결과

### 2.1 모델 구성

| 항목 | 값 |
|------|-----|
| 모델 | Prophet 1.3.0 (Univariate, conservative) |
| 학습 신호 (regressor 로드) | **15개** (보수적 모드에서 미사용 정책) |
| 학습 기간 | 2025-04-28 ~ 2026-01-26 (40주) |
| 예측 시작 | 2026-02-02 |
| 단기/중장기 horizon | 1~7주 / 8~21주 |
| 신뢰구간 | 80% |

### 2.2 단기 예측 (1~7주)

| Week | 예측 | 80% CI | 변화율 |
|------|-----|--------|--------|
| 2026-02-02 | 410.30 | [386, 437] | -11.33% |
| 2026-02-09 | 421.67 | [393, 447] | -8.87% |
| 2026-02-16 | 433.05 | [406, 461] | -6.41% |
| 2026-02-23 | 444.43 | [418, 472] | -3.95% |
| 2026-03-02 | 455.81 | [427, 483] | -1.49% |
| 2026-03-09 | 467.18 | [439, 492] | +0.97% |
| 2026-03-16 | 478.56 | [451, 504] | +3.42% |

### 2.3 중장기 예측 (8~21주)

| Week | 예측 | 80% CI | 변화율 |
|------|-----|--------|--------|
| 2026-03-23 | 489.94 | [460, 516] | +5.88% |
| 2026-04-27 | 546.82 | [514, 580] | +18.18% |
| 2026-05-25 | 592.33 | [553, 630] | +28.01% |
| 2026-06-22 | 637.84 | [592, 683] | +37.85% |

### 2.4 사후 검증

| 지표 | 값 | 평가 |
|------|-----|------|
| **MAPE** | **7.54%** | ✅ PRD 목표 ≤20% 통과 |
| 80% CI 적중 | 5/13 (38.5%) | ⚠️ Phase 6에서 interval_width 상향 |
| 최고 정확 주 | 2026-03-02 (1.81%) | 단기 예측 우수 |

---

## 3. 미수집 4개 — 다음 액션

### B-2 — ✅ RSS 방식으로 해결됨 (GCP 불필요)

**현재 작동**: TechNews.tw + Digitimes RSS 4개 피드 + 키워드 sentiment.
- 매주 cron 실행으로 누적 → 1년 차에 완전 history
- 초기 backfill은 RSS 한계로 최근 4~30일만
- GCP 사용 시 대안: `pipelines/verify_b2_gcp.py` 진단 도구 + `collect_B2_gdelt_bq()` 함수 별도 보존

### B-1 / B-5 / B-6 (Anthropic + PDF — 3개 한번에)

**상태**: 키 등록됨 (108자), 크레딧 0 → 충전 필요. PDF 파이프라인 추가 구현 필요.

**사용자 액션** (5분 + 1시간 코드):
1. https://console.anthropic.com/settings/billing → 카드 + $5+ 충전
2. 추가 코드: PDF 다운로드 + pypdf 텍스트 추출 + Claude 호출 (가이드 §4)

---

## 4. 무엇이 작동하는지 — 운영 가능성 평가

### ✅ 즉시 운영 가능

- 매주 화요일 06:00 cron으로 16개 신호 자동 갱신
- Prophet 매주 재학습 → 새 21주 예측 출력
- Supabase에 push (테이블 생성 후)

### 운영 명령 (한 줄)

```bash
cd backend
source ../.env
.venv/bin/python3 pipelines/auto_collectors.py --all   # 16개 신호 갱신
.venv/bin/python3 pipelines/forecast.py                  # Prophet
.venv/bin/python3 pipelines/sync_supabase.py             # DB push
```

### Cron 등록 예시

```cron
# crontab -e
0 7 * * 2 cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend && \
  source ../.env && \
  .venv/bin/python3 pipelines/auto_collectors.py --all && \
  .venv/bin/python3 pipelines/forecast.py && \
  .venv/bin/python3 pipelines/sync_supabase.py >> /tmp/sixsense_weekly.log 2>&1
```

---

## 5. 운영 환경 키 발급 상태

| 키 | 발급 | 등록 | 작동 |
|----|------|------|------|
| ANTHROPIC_API_KEY | ✅ | ✅ (108자) | ⚠️ 크레딧 0 |
| KOSIS_API_KEY + URL | ✅ | ✅ | ✅ |
| KCS_API_KEY (관세청 data.go.kr) | ✅ | ✅ | ✅ |
| AWS_ACCESS_KEY_ID + SECRET | ✅ | ✅ | ✅ |
| SUPABASE_URL + PUBLISHABLE | ✅ | ✅ | ✅ |
| GOOGLE_APPLICATION_CREDENTIALS | ⏸ | ⏸ | ⏸ |
| REDDIT_CLIENT_ID + SECRET | ⏸ | ⏸ | (HN 대체 사용 중) |

---

## 6. 학습 (Phase 5e 진행 중 누적)

1. **data.go.kr 401 ≠ 권한 없음** — 잘못된 파라미터/HS 코드일 수도. Excel 코드표가 가장 빠른 디버그
2. **KOSIS는 사용자 등록 표만 접근** — 웹사이트 URL 생성기가 가장 안전
3. **AWS spot history 90일 제약** — 매주 cron 누적으로 1년 차에 완전 history
4. **Metaculus 403 변경 (2024년)** — 인증 필수, 대안 Manifold Markets 사용
5. **Manifold pagination은 bet ID 기반** (timestamp 아님)
6. **requests.HTTPError가 EnvironmentError 상속** → exception 분류 주의
7. **Shell 빈 환경변수 보호** — `if not os.environ.get(k)` 패턴 필수

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | 초기 백필 9/19 + Prophet MAPE 7.54% |
| 0.2 | 2026-05-17 | 11신호 자동 collector 추가 (B-3/B-4/B-7) |
| 0.3 | 2026-05-17 | A-3 관세청 + A-4 KOSIS + A-5 AWS |
| **0.4** | **2026-05-17** | **A-6 Manifold Markets 추가 → 16/20 (80%), B-2 verify 도구** |
