# 🎓 Sixsense — Phase 7 누적 (2026-05-18)

> **현재 상태**: 자동 데이터 수집 **20/20 (100%)** + Multi-model 단기 GBR MAPE **4.54%**, 중장기 LSTM MAPE **9.19%** + hand-off 14화면 **실데이터 주입 완료** + 뉴스/이벤트 RSS+LLM 자동 수집 + **수동 갱신 버튼**.
>
> KAIST CAIO 6조 과제 제출 가능 + 실제 운영환경 발전 모두 가능.

---

## 📊 한눈에

```
정형 A:   ███████████████████████  7/7 ✅
비정형 B: ███████████████████████  7/7 ✅
거시:     ███████████████████████  6/6 ✅ (UST10 추가)
타겟:     ███████████████████████  1/1 ✅
            ━━━━━━━━━━━━━━━━━━━━━━━
  🎉 총계: 21/21 (100%) 자동 수집

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
| #10 | news/events 풀 완전 분리 + 거시 UST10 | NEWS_QUERIES(DRAM 산업 14) vs EVENTS_QUERIES(글로벌+국내반도체 이벤트성 31)로 entry 단계부터 분리 → §05 AI 뉴스에 글로벌 이벤트 섞임 방지. LLM 단일 호출 `{news:[], events:[]}` 분리 출력. **미국 10년물 국채금리** (`macro-ust10`, FRED DGS10) 신규 추가 → macro 5→6개 |
| #11 | 인사이트 카드 클릭 → 전체 모달 팝업 | 카드에서 잘리는 250자 분석 → 본문 `-webkit-line-clamp:8` + fade. 카드 전체 `.tappable` + "🔍 클릭" 칩. 클릭 시 hand-off `<Modal>` 로 전체 분석 팝업 (헤드라인 19px + 핵심 신호 + 250자 본문 15.5px + 생성 시각, ESC/외부 클릭 닫기) |
| #12 | 인사이트 완결 문장 강제 (280~400자) | 모달에서도 "… 등 강력한" 같이 미완성 끊김 → 프롬프트 "반드시 마침표 완결" + enforce 잘림 마커 검출 → 마지막 마침표까지만 + 400자 cap. 현재 Gemini가 400자 완결 4문장 생성 ("…가격 상승이 불가피할 것으로 판단됩니다.") |
| #13 | 인사이트 가독성 미세조정 (2026-05-19) | (a) `.insight-main` 좌우 분할 breakpoint 1400px→**800px** (일반 노트북/데스크탑 환경에서 항상 좌우 3:2 유지). (b) 카드 안 본문 폰트 14px→**11.5px** + line-height 1.7→1.65 (모달은 14.5px 유지) |
| #14 | news/events 한국어 100% 보장 (2026-05-19) | `korean_title()` + `KEYWORD_MAP` 60개 매핑 (회사/기술/시장/사건/금융/국가) → 영문 헤드라인 자동 한국어 치환. 4 fallback 함수(heuristic_news/events + merge_news/events_only) 보강. Gemini RPM 회복 폴링으로 LLM 우선. 검증: **news 10/10 + events 10/10 제목·요약 모두 한국어** |

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
| 2 | **Google Gemini 2.5 Flash** | ✅ **현재 사용 중 (maxOutputTokens 8192로 확대 후 안정)** | — |
| 2' | Google Gemini 2.0 Flash | ⏳ RPM 한도 (간헐적) | 분당 회복 |
| 3 | Groq llama-3.3-70b | ❌ `.env`에 키 미설정 | console.groq.com 가입 (무료 14400/day) |
| 4 | 휴리스틱 | (fallback only) | 데이터 기반 250자 자동 생성, `**bold**` 강조 포함 |

**현재 인사이트** (Gemini 2.5 Flash, **400자 완결 4문장**, tone=pos / conf 88% / horizon long / 핵심 신호 A-2·A-5·B-4):
> headline: **AI 수요 폭증, 장기적 가격 상승 압력**
>
> 현재 서버 DRAM 가격은 지난주 대비 **+4.0%** 상승했으나, 단기 및 중장기 예측 모델은 약 **-16%** 하락을 전망합니다. 그러나 이러한 모델 예측과 달리, **AI 메모리 부족**에 대한 강력한 뉴스 신호들이 2027년까지의 심각한 공급 부족을 일관되게 경고하며 장기적인 가격 상승 압력을 시사합니다. 특히 **빅테크 CapEx**와 AWS Spot 가격 상승은 AI 인프라 투자 확대를 반영하며 수요 강세를 뒷받침합니다. 지정학적 리스크(GPR)와 구리 선물가 상승 또한 공급망 불안정 및 전반적인 원자재 비용 상승 가능성을 나타냅니다. 따라서 단기적인 가격 조정 가능성에도 불구하고, **AI 수요**가 견인하는 구조적인 공급 부족으로 인해 중장기적으로는 가격 상승이 불가피할 것으로 판단됩니다.

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
