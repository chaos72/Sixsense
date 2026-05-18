# 🎓 Sixsense — Phase 7 누적 (2026-05-18)

> **현재 상태**: 자동 데이터 수집 **20/20 (100%)** + Multi-model 단기 GBR MAPE **4.54%**, 중장기 LSTM MAPE **9.19%** + hand-off 14화면 **실데이터 주입 완료** + 뉴스/이벤트 RSS+LLM 자동 수집 + **수동 갱신 버튼**.
>
> KAIST CAIO 6조 과제 제출 가능 + 실제 운영환경 발전 모두 가능.

---

## 📊 한눈에

```
정형 A:   ███████████████████████  7/7 ✅
비정형 B: ███████████████████████  7/7 ✅
거시:     ███████████████████████  5/5 ✅
타겟:     ███████████████████████  1/1 ✅
            ━━━━━━━━━━━━━━━━━━━━━━━
  🎉 총계: 20/20 (100%) 자동 수집

News:    ██████████ 10건 (RSS+Gemini, 최근 30일 Top 10)
Events:  ████       4건  (RSS+Gemini, 지정학·군사·재해·파업)
Insight: ████       250자 (Claude→Gemini→휴리스틱 fallback chain)
```

---

## 🖥️ 핵심 실행 (한 줄)

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend && \
  source ../.env && \
  .venv/bin/python3 pipelines/auto_collectors.py --all && \
  .venv/bin/python3 pipelines/collect_news_events.py && \
  .venv/bin/python3 pipelines/forecast_v2.py && \
  .venv/bin/python3 pipelines/build_insight.py && \
  .venv/bin/python3 pipelines/build_frontend_data.py
# (매주 화요일 06:00 KST cron 자동 실행 대상 — 또는 S-001 풋바 "🔄 수동 갱신" 버튼)
```

### Frontend (이미 실행 중일 가능성)
```bash
cd frontend && npm run dev   # → http://localhost:5173
```

### Backend API (수동 갱신 + 15 기본 endpoint)
```bash
cd backend && .venv/bin/uvicorn app.main:app --port 8000 --reload
# → http://localhost:8000/docs (OpenAPI Swagger)
```

---

## 🎯 hand-off SSOT (UI 진실원)

> **무조건** `design_handoff_sixsense_dram_dashboard/` (Claude Design hifi 14화면)이 UI 단일 진실원. 신규 UI 디자인 금지. 외부 차트 라이브러리(Plotly/Recharts/D3) 금지.

### 7가지 사용자 명시 확장 (예외 — `frontend/src/` 만 수정, hand-off 토큰만 사용)
| # | 영역 | 변경 |
|---|---|---|
| #1 | S-001 §01 가격 스냅샷 | 4번째 슬롯에 `<InsightCard>` 추가 (초기 5분화 3:2) |
| #2 | 인사이트 강조 | 헤드라인 큰 굵은 tone-color + ai-note 강화 |
| #3 | 인사이트 + §02 차트 | 본문 14px + `**bold**` 마크다운 → tone chip. 6분화로 확장. §02에 Multi-Model 검증 패널 추가 |
| #4 | 차트 + 인사이트 | 차트에 4개 모델 동시 표시 (Prophet/HistGBR/GBR★/LSTM★). 인사이트 본문/CLAUDE 좌·우 분할. 헤드라인 15px. 검증 패널 정리 (헤드라인/아키텍처/AiNote 제거) |
| #5 | §01 그리드 | 7분화(3:4). 가격 카드 제목 12px + text-mid 컬러 (인사이트 헤더와 통일) |
| #6 | 차트 색상 + 토글 | Prophet 황색 dotted + HistGBR 보라 long-dash로 명확 구분. 다크/라이트 토글 버튼 가시성 강화 (`.theme-toggle`) |
| #7 | §09 풋바 | **🔄 수동 갱신 실행** 버튼 + 진행률 바 + 단계별 로그 + 완료 시 자동 새로고침 |
| #8 | §07 글로벌 이벤트 모니터링 | RSS 32 쿼리 + 4 카테고리(물리적충돌/기상이변/금융위기/기타) 강제 분류 + 라운드-로빈 다양성 + **10건 보장** + 유형 칩 |
| #9 | §07 국내 반도체 + 한국어 | **국내 반도체** 5번째 카테고리 1순위 추가 (삼성/하이닉스 파업·정전·화재 — 회사명+이벤트 조합 매칭). 5 카테고리 각 1건 강제 보장 + 라운드-로빈. **`korean_summary()` 자동 한국어 요약** (LLM 비활성 시에도). 보라색 칩(--chart-secondary) |

---

## 🔄 데이터 흐름 (실데이터 → hand-off UI)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  매주 화요일 06:00 KST (또는 §09 풋바 "🔄 수동 갱신" 버튼)             │
│                                                                          │
│  ① auto_collectors.py --all   → backend/data/historical/*.json          │
│  ② collect_news_events.py     → backend/data/news/latest.json           │
│                                  backend/data/events/latest.json         │
│  ③ forecast_v2.py             → backend/data/forecast/forecast_v2_*.json│
│                                  backend/data/forecast/model_comparison.txt
│  ④ build_insight.py           → backend/data/insight/latest.json        │
│  ⑤ build_frontend_data.py     → frontend/src/mocks/data.js              │
│                                              ↓ ESM import (Vite HMR)     │
│                                  http://localhost:5173 (14화면 hand-off) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 LLM Chain (build_insight.py / collect_news_events.py)

| 순위 | LLM | 상태 (2026-05-18 11:30 KST) | 회복 |
|---|---|---|---|
| 1 | Anthropic Claude (haiku-4-5) | ❌ HTTP 400 "credit balance too low" | console.anthropic.com → Billing 충전 (영구) |
| 2 | Google Gemini 2.5 Flash | ⏳ HTTP 429 RPM 20/min 초과 (분당 한도) | 32~60초 후 자동 회복 |
| 2' | Google Gemini 2.0 Flash | ⏳ 동일 RPM 한도 | 동일 |
| 3 | Groq llama-3.3-70b | ❌ `.env`에 키 미설정 | console.groq.com 가입 (무료 14400/day, 가장 빠른 해결) |
| 4 | **휴리스틱** | ✅ 현재 사용 중 | 데이터 기반 250자 자동 생성, `**bold**` 강조 포함 |

**현재 인사이트** (휴리스틱, 250자):
> headline: "**하락·하락 동조, 하락 시그널**"
> 단기 GBR은 7주 후 $5.06 (-16.9%), 중장기 LSTM은 21주 후 $5.08 (-16.6%)를 가리킵니다. A-4 재고지수 4.75(<95)로 공급 타이트 신호. DXY 98.1로 강달러 압력↓. 최근 30일 핵심 뉴스 5건이 동반. 워치 포인트: AI 서버 수요·HBM 캡 증설·지정학 리스크를 주간 단위로 점검하세요.

---

## 📦 PDCA 산출물 (KAIST CAIO 제출용)

| 단계 | 파일 | 비고 |
|------|------|------|
| PM (PRD) | [prd.md](prd.md) (사본 [docs/00-pm/sixsense.prd.md](docs/00-pm/sixsense.prd.md)) | Hand-off SSOT Edition, 18 섹션 + 7가지 확장 표 |
| Plan | [docs/01-plan/features/sixsense.plan.md](docs/01-plan/features/sixsense.plan.md) | 요구사항·아키텍처·위험 |
| Design | [docs/02-design/features/sixsense.design.md](docs/02-design/features/sixsense.design.md) | hand-off 그대로 |
| Do | [docs/03-do/features/sixsense.do.md](docs/03-do/features/sixsense.do.md) | hand-off 직접 포팅 + 실데이터 주입 + 7가지 확장 매트릭스 |
| Check | [docs/03-analysis/sixsense.analysis.md](docs/03-analysis/sixsense.analysis.md) | Phase 5e 진행 반영 |
| QA | [docs/05-qa/sixsense.qa-report.md](docs/05-qa/sixsense.qa-report.md) | L1/L2/L3 67/67 |
| Report | [docs/04-report/sixsense.report.md](docs/04-report/sixsense.report.md) | 통합 보고 |

---

## 🔑 등록된 API 키 (.env, gitignored)

| 키 | 상태 | 활용 |
|----|------|------|
| ANTHROPIC_API_KEY | ✅ 등록 / ⚠️ 크레딧 0 | LLM 1순위 — 충전 후 활성 |
| GEMINI_API_KEY | ✅ 작동 (RPM 한도) | LLM 2순위 — 분당 20 req |
| KOSIS_API_KEY + KOSIS_FULL_URL | ✅ 작동 | A-4 (53주) |
| KCS_API_KEY (관세청) | ✅ 작동 | A-3 (53주) |
| AWS_ACCESS_KEY_ID + SECRET | ✅ 작동 | A-5 (11주, 90일 한계) |
| SUPABASE_URL + PUBLISHABLE_KEY | ✅ 작동 | DB 통합 (schema.sql 1회 실행 대기) |
| GROQ_API_KEY | ⏸ 미설정 | LLM 3순위 fallback (무료 14400/day, **추천 추가**) |

---

## 📁 핵심 자산 구조

```
Sixsense/
├── .env                                # 모든 API 키 (gitignored)
├── prd.md                              # PRD Hand-off SSOT Edition
├── NEXT_STEPS.md                       # 본 파일
├── design_handoff_sixsense_dram_dashboard/   # ★ UI SSOT (변경 금지)
├── frontend/                           # React 19 + TS + Vite (hand-off 직접 포팅)
│   └── src/{App.tsx, screens/, components/, mocks/data.js, styles/}
├── backend/
│   ├── app/{main.py, schema.sql, supabase_client.py}
│   ├── pipelines/
│   │   ├── auto_collectors.py          # ① 20 신호 수집
│   │   ├── collect_news_events.py      # ② RSS + Gemini → news/events
│   │   ├── forecast_v2.py              # ③ Prophet + GBR + LSTM
│   │   ├── build_insight.py            # ④ LLM 종합 인사이트
│   │   ├── build_frontend_data.py      # ⑤ 실데이터 → frontend mocks
│   │   ├── sync_supabase.py            # (선택) JSON → Postgres
│   │   └── backfill.py
│   └── data/
│       ├── historical/{A-*, B-*, macro-*, target-dram}.json
│       ├── forecast/forecast_v2_*.json + model_comparison.txt
│       ├── news/latest.json            # 10건 (Gemini 분류)
│       ├── events/latest.json          # 4건 (high-risk 분류)
│       └── insight/latest.json         # 250자 (LLM/휴리스틱)
└── docs/
    ├── 00-pm/sixsense.prd.md
    ├── 01-plan/features/sixsense.plan.md
    ├── 02-design/features/sixsense.design.md
    ├── 03-do/features/sixsense.do.md
    ├── 03-analysis/sixsense.analysis.md
    ├── 04-report/sixsense.report.md
    ├── 05-qa/sixsense.qa-report.md
    ├── 09-data-acquisition/
    └── 10-modeling/modeling-architecture.md
```

---

## 🚀 즉시 데모 가능

```bash
# 1. 데이터 + 예측 + 인사이트 갱신
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend
source ../.env
.venv/bin/python3 pipelines/auto_collectors.py --all && \
  .venv/bin/python3 pipelines/collect_news_events.py && \
  .venv/bin/python3 pipelines/forecast_v2.py && \
  .venv/bin/python3 pipelines/build_insight.py && \
  .venv/bin/python3 pipelines/build_frontend_data.py

# 2. 백엔드 + 프론트엔드 동시 기동
.venv/bin/uvicorn app.main:app --port 8000 --reload &
cd ../frontend && npm run dev
```

→ http://localhost:5173 → S-001 메인 대시보드에서:
- §01 가격 스냅샷 7분화 (3 카드 + 인사이트 카드 좌우 분할, 250자 강조 본문 + CLAUDE 종합 판단)
- §02 DRAM 차트 4개 모델 동시 표시 (Prophet 황색 + HistGBR 보라 + GBR★ 청색 + LSTM★ 초록) + MAPE 검증 표
- §03 14 신호 카드, §04 Graph RAG, §05 뉴스/거시, §06 이벤트/정확도, §07 수집 풋바 + **🔄 수동 갱신** 버튼

---

## 📅 Phase 히스토리

| Phase | 일자 | 주요 변경 |
|---|---|---|
| 5 | 2026-05-16 | Backend FastAPI 15 endpoint + L1/L2/L3 67/67 |
| 5e | 2026-05-17 | 20/20 자동 수집 (KOSIS·KCS·AWS·Manifold·RSS) |
| 5f | 2026-05-17 | Supabase REST 통합 |
| 6 | 2026-05-17 | Multi-model (Prophet + GBR + LSTM, MAPE 4.54%) |
| **7** | **2026-05-18** | **Hand-off SSOT 재정렬 + 실데이터 주입 + News/Events RSS+LLM + 7가지 UI 확장 + 수동 갱신 endpoint** |
