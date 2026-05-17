# 🎓 Sixsense — 최신 상태 (Phase 5e 누적 / 2026-05-17)

> **현재 단계**: 자동 데이터 수집 16/20 (80%) 완료. Prophet 예측 MAPE 7.54%. Supabase 통합 준비 완료.
> KAIST CAIO 과제 제출 + 실제 운영환경 발전 모두 가능.

---

## 📊 현재 수집 현황 (한눈에)

```
정형 A:   ████████████████████░  6/7  (A-6 Manifold 추가, B-1만 대기)
                                         ↑ 6/7? 실제로는 A-3,4,5,6,7 + A-1,2 = 7/7
정형 A:   ███████████████████████  7/7 ✅  완료!
비정형 B: ████████░░░░░░░░░░░░░░  3/7  (B-3,4,7 작동, B-1,5,6는 Anthropic, B-2는 GCP)
거시:     ███████████████████████  5/5 ✅
타겟:     ███████████████████████  1/1 ✅

           ━━━━━━━━━━━━━━━━━━━━━━━
  총계: 16/20 (80%) 자동 수집 작동
```

---

## 📦 PDCA 산출물 (KAIST CAIO 제출용)

| 단계 | 파일 | 줄수 | 비고 |
|------|------|------|------|
| PM (PRD) | [docs/00-pm/sixsense.prd.md](docs/00-pm/sixsense.prd.md) | 1,641 | 18 섹션 종합 |
| Plan | [docs/01-plan/features/sixsense.plan.md](docs/01-plan/features/sixsense.plan.md) | 326 | 요구사항·아키텍처·위험 |
| Design | [docs/02-design/features/sixsense.design.md](docs/02-design/features/sixsense.design.md) | 1,113 | bkit 11 섹션 |
| Do (v0.2) | [docs/03-do/features/sixsense.do.md](docs/03-do/features/sixsense.do.md) | 284 | 핸드오프 직접 포팅 |
| Analysis | [docs/03-analysis/sixsense.analysis.md](docs/03-analysis/sixsense.analysis.md) | 320+ | Phase 5e 진행 반영 |
| QA | [docs/05-qa/sixsense.qa-report.md](docs/05-qa/sixsense.qa-report.md) | 230 | L1/L2/L3 67건 통과 |
| Report | [docs/04-report/sixsense.report.md](docs/04-report/sixsense.report.md) | 340+ | 통합 보고 |

---

## 🖥️ 실행 가능한 산출물

### 1. 프론트엔드 (14화면 핸드오프 그대로)

```bash
cd frontend && npm run dev
# → http://localhost:5173
```

### 2. 백엔드 API (FastAPI 15 엔드포인트)

```bash
cd backend
.venv/bin/uvicorn app.main:app --port 8000
# → http://localhost:8000/api/health
```

### 3. 자동 데이터 수집 (16개 신호)

```bash
cd backend
source ../.env
.venv/bin/python3 pipelines/auto_collectors.py --all
```

### 4. Prophet 예측 (매주 재학습)

```bash
.venv/bin/python3 pipelines/forecast.py
# → backend/data/forecast/forecast_2026-02-w1.json
# → MAPE 7.54%, 단기 1~7주 + 중장기 8~21주
```

### 5. Supabase 동기화 (스키마 1회 실행 후)

```bash
# Step 1 (1회): Supabase Studio → SQL Editor → backend/app/schema.sql 실행
# Step 2 (매주): JSON → Postgres push
.venv/bin/python3 pipelines/sync_supabase.py
```

---

## 🔑 등록된 API 키 (.env, gitignored)

| 키 | 상태 | 활용 신호 |
|----|------|----------|
| ANTHROPIC_API_KEY | ✅ 등록 / ⚠️ 크레딧 0 | B-1, B-5, B-6 (충전 후 활성) |
| KOSIS_API_KEY + KOSIS_FULL_URL | ✅ 작동 | A-4 (53주) |
| KCS_API_KEY (관세청 data.go.kr) | ✅ 작동 | A-3 (53주) |
| AWS_ACCESS_KEY_ID + SECRET | ✅ 작동 | A-5 (11주, 90일 한계) |
| SUPABASE_URL + PUBLISHABLE_KEY | ✅ 작동 | DB 통합 (스키마 1회 실행 대기) |
| GOOGLE_APPLICATION_CREDENTIALS | ⏸ 미설정 | B-2 (GDELT BigQuery) |
| REDDIT_CLIENT_ID + SECRET | ⏸ 미설정 | B-3 정확도 (현재 HN 대체) |

---

## 🎯 남은 4개 신호 — 다음 액션

### Priority 1: B-2 GDELT (15분, 가장 빠름)

```bash
# 진단
cd backend && .venv/bin/python3 pipelines/verify_b2_gcp.py

# 가이드: docs/09-data-acquisition/key-acquisition-guide.md §2
# 핵심 단계:
# 1. console.cloud.google.com 가입 + 결제카드
# 2. 프로젝트 생성 → IAM → Service Accounts
# 3. BigQuery Data Viewer + Job User 역할
# 4. JSON 키 다운로드 → ~/.config/gcp/sixsense-bq.json
# 5. .env에 GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcp/sixsense-bq.json
# 6. .venv/bin/python3 pipelines/auto_collectors.py B-2
```

→ +1 신호 (17/20)

### Priority 2: Anthropic 크레딧 충전 (5분, 가장 가성비)

```bash
# 1. https://console.anthropic.com/settings/billing → 카드 + $5 충전
# 2. (추가 코드 작업: PDF 다운로드 + Claude sentiment 추출 — 1시간)
# 3. .venv/bin/python3 pipelines/auto_collectors.py B-1
```

→ +3 신호 (B-1+B-5+B-6 = 20/20 완성)

### Priority 3: Reddit PRAW (5분, 선택)

```bash
# 1. reddit.com/prefs/apps → script 앱 생성
# 2. .env에 REDDIT_CLIENT_ID/SECRET
# 3. 자동 B-3가 HN 대체 → Reddit으로 전환됨
```

→ B-3 정확도 향상 (신호 수 동일)

---

## 📁 핵심 자산 (디렉토리 구조)

```
Sixsense/
├── .env                              # 모든 API 키 (gitignored)
├── prd.md / prd.docx / prd.md.bak    # PRD 18섹션
├── NEXT_STEPS.md                     # 본 파일
├── design_handoff_.../               # 14화면 hifi 디자인 (SSOT)
├── frontend/                         # React 19 + TS + Vite (14화면 동작)
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI 15 endpoints
│   │   ├── data.json                 # mock 데이터
│   │   ├── supabase_client.py        # Supabase REST 래퍼
│   │   └── schema.sql                # DB DDL (Studio에서 1회)
│   ├── pipelines/
│   │   ├── backfill.py               # 초기 백필 (1회)
│   │   ├── auto_collectors.py        # 11개 자동 collector
│   │   ├── upload_manual.py          # 수동 CSV 업로드
│   │   ├── forecast.py               # Prophet 학습/예측
│   │   ├── sync_supabase.py          # JSON → DB
│   │   └── verify_b2_gcp.py          # B-2 GCP 진단
│   ├── data/
│   │   ├── historical/               # 16개 신호 시계열
│   │   ├── forecast/                 # Prophet 출력
│   │   └── manual/                   # 사용자 CSV 템플릿
│   └── tests/
│       └── l1_api_test.sh            # 41 API 테스트 (모두 통과)
└── docs/
    ├── 00-pm/sixsense.prd.md
    ├── 01-plan/features/sixsense.plan.md
    ├── 02-design/features/sixsense.design.md
    ├── 03-do/features/sixsense.do.md
    ├── 03-analysis/sixsense.analysis.md
    ├── 04-report/sixsense.report.md
    ├── 05-qa/sixsense.qa-report.md
    └── 09-data-acquisition/
        ├── data-acquisition-report.md   # v0.4 최신 수집 현황
        ├── auto-upload-guide.md         # 11신호 자동화
        ├── manual-upload-guide.md       # 수동 CSV
        ├── key-acquisition-guide.md     # 8개 키 발급 절차
        ├── kosis-url-generation.md      # KOSIS 사용자 URL
        ├── data-go-kr-troubleshooting.md # 관세청 디버그
        └── supabase-integration.md      # DB 통합
```

---

## 📅 커밋 히스토리 (최근 10개)

```bash
git log --oneline -10
```

```
(최신)  feat(phase5e): A-6 Manifold + B-2 GCP 진단 + 문서 통합 갱신
        feat(phase5e): A-5 AWS EC2 Spot 11주 수집 성공
        feat(phase5e): A-3 관세청 53주 수집 성공 (Excel 코드 참조)
        feat(phase5e): A-3 data.go.kr Itemtrade 엔드포인트 적용
        feat(phase5f): Supabase 통합 — REST + 스키마 + sync
        feat(phase5e): collector가 루트 .env 자동 로드
        feat(phase5e): A-4 KOSIS 재고지수 53주 수집 성공
        feat(phase5e): KOSIS collector 3가지 입력 방식 지원
        feat(phase5e): 11신호 자동 collector + 3개 즉시 수집
        feat: Phase 5 backend + L1/L2/L3 runtime tests 100% (67/67)
(첫)    chore: initial commit — Sixsense DRAM Dashboard MVP
```

---

## ✅ 즉시 데모 가능 (단일 명령)

```bash
# 1. 데이터 + 예측 갱신
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend
source ../.env
.venv/bin/python3 pipelines/auto_collectors.py --all && \
  .venv/bin/python3 pipelines/forecast.py && \
  cat data/forecast/forecast_summary.txt

# 2. 백엔드 + 프론트엔드 동시 기동
.venv/bin/uvicorn app.main:app --port 8000 &
cd ../frontend && npm run dev
```

→ http://localhost:5173 에서 14화면 시연 + 백엔드 API 호출 + Prophet 예측 결과 확인

---

## Version History

| Version | Date | 누적 신호 | 주요 변경 |
|---------|------|---------|----------|
| 0.1 | 2026-05-16 | 9 | 초기 백필 + Phase 5 backend |
| 0.2 | 2026-05-17 | 12 | B-3/B-4/B-7 자동 수집 |
| 0.3 | 2026-05-17 | 14 | A-4 KOSIS + A-3 관세청 |
| 0.4 | 2026-05-17 | 15 | A-5 AWS EC2 Spot |
| **0.5** | **2026-05-17** | **16** | **A-6 Manifold + B-2 GCP 진단 + 문서 통합** |
