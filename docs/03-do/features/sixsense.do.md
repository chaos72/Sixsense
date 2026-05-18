# Sixsense — Do (Implementation Guide)

> **Hand-off SSOT Edition** (v0.3, 2026-05-18) — bkit `/pdca do sixsense` 산출물.
>
> **불변 원칙**: `design_handoff_sixsense_dram_dashboard/` 가 UI 단일 진실원이다. UI 컴포넌트·레이아웃·색상·간격을 1px도 변경하지 않는다. 신규 UI 디자인을 만들지 않는다. (이 규칙 위반 시 PRD §4 위반.)
>
> 본 v0.3은 (v0.2의 hand-off 직접 포팅 전략을 유지하면서) **실데이터 주입 파이프라인**을 추가했다: backend가 `frontend/src/mocks/data.js` 를 자동 생성하고, hand-off React 앱이 ESM import + Vite HMR 로 즉시 반영한다.

---

## 1. 아키텍처 한 줄

```
backend/data/*.json  ──[build_frontend_data.py]──►  frontend/src/mocks/data.js  ──[Vite HMR]──►  hand-off 14 화면
```

UI 코드는 `design_handoff_sixsense_dram_dashboard/src/` 의 JSX를 `frontend/src/screens/` 와 `frontend/src/components/` 로 직접 복사·이동한 것이다. 데이터 주입 외에 코드 수정 없음.

**사용자 명시 확장 (예외, 2026-05-18 누적)**:

| # | 영역 | 변경 | 추가 파일/심볼 |
|---|---|---|---|
| #1 | S-001 §01 가격 스냅샷 | 4번째 슬롯에 "예측분석 인사이트" 카드 (초기 5분화 3:2) | `<InsightCard>` · `.grid-snapshot` · `.insight-*` · `build_insight.py` |
| #2 | 인사이트 강조 | 헤드라인 큰 굵은 tone-color, ai-note border 굵게 | `.insight-headline` · `.insight-tone-{pos\|neu\|neg}` |
| #3a | 인사이트 추가 강화 | 본문 14px(13→14), summary 내 `**bold**` 마크다운을 tone 컬러 chip으로 렌더, 6분화로 확장 (3:3 = 1fr 1fr 1fr 3fr) | `renderInsightEmphasis` (components.jsx) · `.insight-emphasis` · `.grid-snapshot` 변경 |
| #3b | S-001 §02 DRAM 차트 | 차트 카드 아래에 Phase 6 Multi-Model 검증 패널 추가 | `<ModelValidationPanel>` (dashboard.jsx) · `meta.modelValidation` (build_frontend_data.py) · `.model-*` CSS |
| #4a | 인사이트 카드 | 본문/CLAUDE 박스 위·아래 → 좌·우 분할 (3:2), 헤드라인 17px→15px(두 포인트 축소) | `.insight-main` (styles.css), components.jsx wrapper |
| #4b | §02 검증 패널 정리 | "🎉 Phase 6…" 헤드라인 배너 / "🏗️ 아키텍처" ASCII 카드 / "⚙️ 환경 처리" AiNote 삭제. MAPE 표 2개 + 학습 시간만 유지 | dashboard.jsx ModelValidationPanel 단순화 |
| #4c | §02 차트 | 4개 모델 결과 동시 표시 (Prophet baseline 1~21w 회색 dotted + HistGBR 1~7w 옅은 dashed + GBR★ 1~7w + LSTM★ 8~21w). model_comparison.txt 파싱 | `parse_model_comparison_series()` (build_frontend_data.py), `forecast_prophet` / `forecast_histgbr` 시계열 추가, DramChart + ChartLegend 4-line 지원 |
| #4d | 인사이트/대시보드 일치성 | build_insight.py 도 동일 model_comparison.txt 우선 파싱 → 두 영역의 GBR/LSTM 가격이 항상 일치 | build_insight.py:build_prompt() 보강 |
| #5  | §01 가격 스냅샷 가독성 | 그리드 6분화(3:3) → **7분화(3:4 = 1fr 1fr 1fr 4fr)**. 가격 3카드 제목("현재 계약가" / "1~7주 AI 예측가" / "8~21주 AI 예측가") 11px → 12px + 색상 `var(--text-dim)` → `var(--text-mid)` + weight 500 → 600 (인사이트 헤더와 통일). hand-off `.card-h` 글로벌 영향 회피 위해 `.grid-snapshot > .card > .card-h` 스코프 셀렉터로 한정. `.code` (🔍 클릭 표시)는 10px/text-faint 원본 보존 | styles.css `.grid-snapshot` + scoped `.card-h` 셀렉터만 |
| #6a | §02 차트 라인 구분 | Prophet baseline 회색 1.0px → **황색 `var(--chart-baseline)` 1.6px dotted (`2 4` 촘촘점)**, HistGBR 회색 1.2px → **보라 `var(--chart-secondary)` 1.8px long-dash (`7 3`)**. GBR★ 청색·LSTM★ 초록은 변경 없음. 차트와 범례 둘 다 동일 색/패턴 적용 | LineChart `dashed` prop이 string도 받도록 확장 (`s.dashed`가 string이면 그대로 strokeDasharray, boolean이면 기본 "4 3"). 새 토큰 `--chart-baseline` / `--chart-secondary` (light·dark 둘 다) |
| #6b | Topbar 테마 토글 가시성 | hand-off에 이미 존재했으나 `.btn.sm` 작은 회색이라 묻혀 보임 → **`.theme-toggle` 클래스 강화** (12px / weight 600 / border-strong / surface-2 배경 / 호버 시 accent 반전), 라벨 "☀ 라이트" → "☀ 라이트 모드" 확장, aria-label/title 추가 | styles.css `.theme-toggle` + app.jsx 토글 버튼 |
| #7  | §09 풋바 수동 갱신 버튼 | "이번 주 새 수집 데이터 현황" 풋바 아래에 **🔄 수동 갱신 실행** 패널 추가. 클릭 시 5단계 파이프라인 백그라운드 실행 (auto_collectors → collect_news_events → forecast_v2 → build_insight → build_frontend_data). 진행률 바 + 단계별 ✅ 로그 + 완료 시 자동 페이지 새로고침. 백엔드 신규 endpoint 3개 (`POST /api/refresh`, `GET /api/refresh/jobs/{id}`, `GET /api/refresh/stages`) | `<RefreshPanel>` (dashboard.jsx) · `.refresh-*` CSS · main.py `_run_refresh_pipeline` (threading, subprocess, timeout 10분) |
| #8  | §07 글로벌 이벤트 다양화 | RSS 쿼리 14→32 (전쟁/지진/환율/유가/금리 17건 추가, 영·한). LLM/휴리스틱이 **사용자 정의 4 카테고리** (`물리적 충돌` / `기상이변` / `금융 위기` / `기타`) 로 강제 분류. 휴리스틱 word-boundary 매칭으로 "warning"의 "war" 오인 방지. `diversify_events()` 라운드-로빈으로 카테고리 다양성 + 위험도 우선순위로 **무조건 10건 보장** (RSS 부족 시 placeholder). UI §07 3건 → 10건, **유형 칩(`.events-type-conflict/weather/financial/other`)** + 위험도 + 제목 + 지역 4-column 그리드 | collect_news_events.py `EVENT_CATEGORIES`, `classify_category()`, `classify_region()`, `diversify_events()` · dashboard.jsx `categoryClass()` + `events-row` 그리드 · styles.css `.events-type-*` |
| #9  | §07 국내 반도체 카테고리 + 한국어 요약 | 4 카테고리 → **5 카테고리** (`국내 반도체` 신규 추가, 1순위 — 삼성/하이닉스 파업·정전·화재). `classify_category()` 강화 — **회사명("Samsung/Hynix/삼성/하이닉스") + 부정 이벤트 키워드("strike/union/labor/blackout/fire/파업/노조/정전/화재") 조합 매칭**으로 "Samsung Electronics union talks" 같은 헤드라인 정확 분류. RSS 쿼리 32→42 (국내 반도체 직접 10개 추가). `diversify_events()` 5 카테고리 각 1건 강제 보장 + 라운드-로빈 (placeholder 폴백). **`korean_summary()` 함수 신규** — 카테고리·지역·키워드 기반 한국어 요약 자동 생성 (LLM 비활성 시에도 모든 events `summary` 한국어 보장). LLM 프롬프트 type enum 5 카테고리 + summary_ko 한국어 강제 | collect_news_events.py `korean_summary()`, `_make_placeholder()`, 5-cat `EVENT_CATEGORIES`/`classify_category()`/`diversify_events()` · dashboard.jsx `categoryClass()` "domestic" 추가 · styles.css `.events-type-domestic` (보라색, --chart-secondary 토큰) |
| #10 | news/events 풀 완전 분리 + macro UST10 신규 | (1) 사용자 지적: #8/#9 작업으로 events 다양화 RSS 쿼리 추가 시 동일 enriched pool 에서 news+events 동시 생성하던 구조 때문에 §05 AI 뉴스에도 글로벌 이벤트(전쟁/지진)가 섞임. **해결**: `NEWS_RSS_FEEDS/NEWS_QUERIES` (DRAM 산업 직접, 14개) vs `EVENTS_RSS_FEEDS/EVENTS_QUERIES` (글로벌+국내반도체 이벤트성, 31개)로 entry 단계부터 완전 분리. `fetch_entries(rss_urls)` 파라미터화. main()이 두 풀 독립 처리 (news 중복 제거 후 events). 새 함수: `llm_enrich_split()` (단일 LLM 호출에 `{news:[10], events:[10]}` 분리 출력 강제), `merge_news_only()`, `merge_events_only()`, `heuristic_news_only()`. (2) 거시경제 §06에 **미국 10년물 국채금리** (`macro-ust10`) 신규 — backfill.py `collect_macro_ust10()` (FRED DGS10 CSV, 53주, 위험자산 선호도 지표). build_frontend_data.py `MACRO_META` + `NEGATIVE_WHEN_UP` 튜플 (DXY/KRW/UST10 모두 ↑ 시 DRAM 부정) | collect_news_events.py NEWS/EVENTS 풀 분리 · backfill.py `collect_macro_ust10()` · build_frontend_data.py MACRO_META 6개 |
| —   | LLM 인사이트 정상화 | build_insight.py `maxOutputTokens: 2048 → 8192` (collect_news_events 와 동일). 2048 이 한국어 250자 + JSON 메타데이터 출력에 부족해 Gemini 응답이 잘려 휴리스틱으로 떨어지던 root cause 해결. 현재 Gemini 2.5 Flash 정상 사용 중 (246자 종합 분석) | build_insight.py maxOutputTokens |
| #11 | §01 인사이트 카드 클릭 → 전체 모달 팝업 | 250자 분석이 카드에서 잘림 → (a) 본문에 **CSS `-webkit-line-clamp: 8`** + 하단 fade gradient 로 부드러운 잘림, (b) 카드 전체 `.tappable` 처리 + "🔍 클릭" 칩 + 호버 시 accent 반전, (c) 클릭 시 hand-off `<Modal>` 컴포넌트로 **전체 분석 팝업** — 강조 헤드라인 19px + 핵심 신호 chip + 250자 본문(15.5px, line-height 1.85) + 생성 시각. ESC/외부 클릭 닫기 자동 (hand-off Modal 표준) | components.jsx `InsightCard` useState + `<Modal>` 통합 · styles.css `.insight-body-clamp` / `.insight-expand` / `.insight-modal-body` / `.insight-modal-summary` |
| #12 | 인사이트 본문 완결 문장 강제 | 모달에서도 LLM 응답이 "… 등 강력한 " 같이 미완성으로 끊기던 문제 (LLM이 출력 토큰 절약 + 250자 한도 의식해 자체 컷). 해결 3중 안전망: (a) **프롬프트**에 "280~360자, 반드시 마침표로 완결, '…' '...' '등 강력한' 같은 미완성 금지" 명시, (b) **enforce 로직**에 잘림 마커 검출 → 마지막 마침표까지만 사용, (c) **400자 cap** + 마침표 없으면 자동 추가. 휴리스틱도 동일하게 완결 문장 형태로 재작성. 결과: 400자 완결 4문장 분석 (Gemini "현재 서버 DRAM 가격은 … 가격 상승이 불가피할 것으로 판단됩니다.") | build_insight.py 프롬프트 + summary enforce + heuristic 재작성 |

데이터: `backend/pipelines/build_insight.py` 가 Claude(우선) → Gemini → 휴리스틱 fallback chain으로 `meta.insight` 생성. modelValidation은 `build_frontend_data.py:build_model_validation()` 가 `forecast/model_comparison.txt` 를 파싱(없으면 사용자 명세 fallback).

---

## 2. 디렉토리 매핑 (hand-off ↔ frontend)

| hand-off (SSOT) | frontend (포팅본) | 수정 정책 |
|---|---|---|
| `src/app.jsx` | `frontend/src/screens/app.jsx` | 변경 금지 |
| `src/dashboard.jsx` | `frontend/src/screens/dashboard.jsx` | 변경 금지 |
| `src/modals.jsx` | `frontend/src/screens/modals.jsx` | 변경 금지 |
| `src/pages.jsx` | `frontend/src/screens/pages.jsx` | 변경 금지 |
| `src/components.jsx` | `frontend/src/components/components.jsx` | 변경 금지 |
| `src/tweaks-panel.jsx` | `frontend/src/screens/tweaks-panel.jsx` | 변경 금지 (운영 시 제거) |
| `src/styles.css` | `frontend/src/styles/styles.css` | 변경 금지 |
| `src/data.js` (mock) | `frontend/src/mocks/data.js` (★ AUTO-GENERATED) | **이 파일만 백엔드가 갱신** |

`frontend/src/App.tsx` 와 `frontend/src/main.tsx` 만 thin TypeScript wrapper로 신규 작성 (hand-off의 ReactDOM 부트스트랩을 Vite ESM 환경으로 옮기는 7~10줄).

---

## 3. 실데이터 → hand-off 주입 (핵심)

### 3.1 데이터 변환 파이프라인

`backend/pipelines/build_frontend_data.py` 는 다음을 수행:

1. `backend/data/historical/{A-1…A-7, B-1…B-7, macro-*, target-dram}.json` 읽기
2. `backend/data/forecast/forecast_v2_2026-02-w1.json` (Prophet + GBR + LSTM) 읽기
3. hand-off `data.js` 의 `SIXSENSE_DATA` 객체 스키마에 1:1 매핑:
   - `meta` — 현재가/1~7w 예측/8~21w 예측/모델명/신뢰도
   - `history` — target-dram 최근 52주 (index/100 = $-단가 환산)
   - `forecast7` — GBR 1~7주 (CI band 포함)
   - `forecast21` — LSTM 8~21주 (CI band 포함)
   - `signalsA` / `signalsB` — 각 7개 신호 카드 (latest value + 8주 sparkline + tone)
   - `macro` — 5개 거시지표 (latest + 7주 추세)
   - `accuracy` — forecast vs actual 비교 (21건)
   - `snapshotPast` — 8주 전 시점 14신호 vs 현재 비교 (S-009/S-013 데이터)
   - `collection` — 20/20 수집 현황 (S-014 데이터)
   - `news` / `events` — 실시간 RSS (TechNews + Digitimes + Google News 14쿼리) → Gemini 2.5 Flash 분류 → 최근 30일 상위 10건 + 이벤트형 ≤8건. 산출물: `backend/data/news/latest.json` + `backend/data/events/latest.json` ([collect_news_events.py](backend/pipelines/collect_news_events.py))
4. ESM `export const SIXSENSE_DATA = {...};` 로 `frontend/src/mocks/data.js` 출력

### 3.2 실행

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend
source ../.env
.venv/bin/python3 pipelines/build_frontend_data.py
# → ✅ frontend/src/mocks/data.js 생성 완료 (29,190 bytes)
#    - 현재가: $6.09 (지난주 대비 +4.0%)
#    - 1~7주 예측: $5.64 (-7.4%)
#    - 8~21주 예측: $8.29 (+36.2%)
#    - history: 52주, forecast7: 7주, forecast21: 14주
```

Vite dev server가 실행 중이면 HMR 자동 반영 → 브라우저 새로고침 불필요.

### 3.3 신호 변환 규칙

| 포맷 | 규칙 | tone 판정 |
|---|---|---|
| `sent` (감성, -1~+1) | 표시: `+0.75` / `+0.00` | pos ≥ 0.30, neg ≤ -0.30, 그 외 neu |
| `sent_neg` (GPR 등 높을수록 부정) | 표시: `152.3` | neg ≥ 150, neu ≥ 100, 그 외 pos |
| `pct` (4주 % 변화) | 표시: `+17.2%` | pos ≥ +3%, neg ≤ -3%, 그 외 neu |
| `pct100` (이미 %) | 표시: `18%` | neu (Manifold 확률) |
| `usd` ($-가격) | 표시: `$4.82` | 4주 변화 기준 pos/neg/neu |
| `usd_b` (USD billions) | 표시: `$80.0B` | pos (CapEx 강세) |
| `raw` (원시 수치) | 표시: 자동 단위 (M/K/raw) | A-4만 alert (>100), 그 외 neu |

스파크라인은 최근 8개 값을 0~1 정규화 (LineChart 컴포넌트가 그대로 그림).

---

## 4. Frontend 빌드 & 실행

### 4.1 개발 모드

```bash
cd frontend
npm install   # 1회
npm run dev
# → http://localhost:5173
```

`App.tsx` (10줄) 는 `screens/app.jsx` 의 hand-off 루트 컴포넌트를 마운트만 한다:

```tsx
// PORTED FROM: design_handoff_sixsense_dram_dashboard/Sixsense.html
// @ts-expect-error — JSX module without explicit types (intentional)
import HandoffApp from './screens/app.jsx'
export default function App() {
  return <HandoffApp />
}
```

### 4.2 프로덕션 빌드

```bash
npm run build   # vite build → dist/
npm run preview # 정적 서빙 미리보기
```

---

## 5. Backend 빌드 & 실행

### 5.1 의존성

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# fastapi, uvicorn, requests, pandas, scikit-learn, prophet, torch, plotly (대시보드 PoC만 사용), pyarrow, supabase
```

### 5.2 실행

```bash
.venv/bin/uvicorn app.main:app --port 8000
# → http://localhost:8000/api/health
```

### 5.3 주간 자동 갱신 (cron 권장)

매주 화요일 06:00 KST:

```bash
0 6 * * 2 cd /path/to/Sixsense/backend && source ../.env && \
  .venv/bin/python3 pipelines/auto_collectors.py --all && \
  .venv/bin/python3 pipelines/collect_news_events.py && \
  .venv/bin/python3 pipelines/forecast_v2.py && \
  .venv/bin/python3 pipelines/build_insight.py && \
  .venv/bin/python3 pipelines/build_frontend_data.py
```

---

## 6. 컴포넌트별 데이터 매핑 (검증용)

### 6.1 S-001 메인 대시보드

| Hand-off 위젯 | data.js 필드 | 백엔드 소스 |
|---|---|---|
| `<MetricCard>` × 3 (가격 스냅샷) | `meta.{current, pred7, pred21, *Change}` | `target-dram.json` last + `forecast_v2_*.json` |
| `<InsightCard>` (사용자 확장 #1/#2/#3a) | `meta.insight.{headline, summary, tone, confidence, horizon, keySignals, model}` (summary 내 `**bold**`) | `insight/latest.json` (Claude→Gemini→휴리스틱) |
| `<ModelValidationPanel>` (사용자 확장 #3b) | `meta.modelValidation.{headline, shortRows, midRows, trainTimes, trainTotal, architecture, envNote}` | `forecast/model_comparison.txt` 파싱 |
| DRAM 52주 + 1~7w/8~21w `<LineChart>` | `history`, `forecast7`, `forecast21` | target-dram + forecast_v2 |
| 14 신호 `<SignalCard>` 그리드 | `signalsA[]`, `signalsB[]` | `historical/{A,B}-*.json` last value + sparkline |
| Graph RAG 미니 차트 | (hand-off mock 유지) | (운영 시 macro-cu + target-dram 상관) |
| AI 뉴스 카드 3건 | `news[].hot=true` | `news/latest.json` (RSS+Gemini, 30일 윈도우 top 10) |
| 거시 카드 5건 | `macro[]` | `historical/macro-*.json` |
| 이벤트 칩 3건 | `events[]` | `events/latest.json` (지정학·군사·재해·파업 분류) |
| 정확도 3건 | `accuracy[].actual !== null` | forecast_v2 vs target-dram |
| 수집 풋바 | `collection.summary` | `_summary.json` + 신호별 카운트 |

### 6.2 S-008 거시경제 5탭

| Tab | `macro[].id` | 실데이터 |
|---|---|---|
| 미국 금리 | `fed` | FRED DFF |
| 달러 인덱스 | `dxy` | Yahoo DX-Y.NYB |
| 산업생산지수 (PMI 대체) | `pmi` | FRED INDPRO |
| USD/KRW | `krw` | Yahoo KRW=X |
| 구리 | `cu` | Yahoo HG=F |

### 6.3 S-012 정확도 + S-014 수집 현황

- S-012: `accuracy[]` 21건 → MAPE 누적 라인 + 표
- S-014: `collection.groupA[]` + `collection.groupB[]` → 신호별 마지막 수집/신규 건수/상태

---

## 7. 변경 금지 / 변경 허용 매트릭스

| 변경 대상 | 허용? | 이유 |
|---|---|---|
| `frontend/src/screens/*.jsx` (포팅본) | ⚠ 사용자 명시 확장만 | hand-off SSOT — §1 확장 영역 외 변경 금지 |
| `frontend/src/components/components.jsx` | ⚠ 사용자 명시 확장만 | hand-off SSOT — 신규 컴포넌트는 hand-off 토큰만 사용 |
| `frontend/src/styles/styles.css` | ⚠ 사용자 명시 확장만 | hand-off SSOT — 신규 CSS는 hand-off CSS 변수만 사용 |
| `frontend/src/mocks/data.js` | ⚠ 자동 갱신만 | `build_frontend_data.py` 출력 |
| `frontend/src/App.tsx` / `main.tsx` | ✅ Vite 마운트 코드만 | thin wrapper |
| `backend/pipelines/*.py` | ✅ 데이터 파이프라인 강화 OK | UI에 영향 없음 |
| `backend/app/main.py` (FastAPI) | ✅ API 추가/수정 OK | UI는 mocks/data.js만 봄 |
| `backend/data/*.json` | ⚠ 수집기 출력만 | 손으로 수정 금지 |
| 새 화면 추가 | ❌ 원칙 금지 | hand-off 14화면이 전부. 추가가 필요하면 hand-off부터 갱신 |
| 새 컴포넌트 추가 | ❌ 원칙 금지 | hand-off `components.jsx` 가 전부 |
| 새 시각화 라이브러리 (Plotly 등) | ❌ 금지 | hand-off LineChart (SVG) 사용 |

---

## 8. 검증 절차

### 8.1 L1 자동
```bash
cd backend
.venv/bin/python3 -m pytest tests/
bash tests/l1_api_test.sh
.venv/bin/python3 pipelines/build_frontend_data.py   # 종료코드 0 확인
```

### 8.2 L2 브라우저 수동
```bash
# 1. 데이터 최신화
cd backend && source ../.env && \
  .venv/bin/python3 pipelines/build_frontend_data.py

# 2. dev server (이미 실행 중이면 HMR 자동)
cd ../frontend && npm run dev

# 3. http://localhost:5173 접속 후 §6 체크리스트 수행
```

### 8.3 L3 정합성
- 단기 MAPE ≤ 7% (현재 4.54% ✅)
- 중장기 MAPE ≤ 12% (현재 9.19% ✅)
- 자동 수집 20/20 (100% ✅)
- news/events 카드에 "[데모]" 라벨 확인 (운영 시 실시간 크롤러로 교체)

---

## 9. 운영 단계 후속 (P2)

| # | 작업 | 영향 |
|---|---|---|
| OP-1 | Supabase Postgres 동기화 (`sync_supabase.py`) — `signals` / `signal_data` / `forecasts` 테이블 | UI는 mocks 그대로 사용 (서버 캐시 도입 시 변경 가능) |
| OP-2 | Tweaks 패널 제거, 어드민 페이지로 분리 | 운영 환경 정리 |
| OP-3 | HITL 임계치 저장 → 재학습 트리거 (백엔드 endpoint) | hand-off `<HITL>` 컴포넌트가 이미 UI에 있음 |
| OP-4 | cron / GitHub Actions 주간 자동 실행 (auto_collectors + collect_news_events + forecast_v2 + build_frontend_data) | 매주 화요일 06:00 KST |
| OP-5 | 뉴스/이벤트 누적 history 구축 (RSS 30일 윈도우 한계 보완) | 매주 cron 누적 → 1년 차 완전 history |

---

## 10. 흔한 함정 (Pitfalls)

1. **Hand-off UI를 "더 예쁘게" 만들고 싶은 충동** — 절대 금지. 사용자가 직접 디자인한 14화면이 SSOT다. 같은 실수를 두 번 했다 (TS 컴포넌트 쇼케이스 v0.1, Plotly HTML 대시보드).
2. **`data.js` 를 손으로 편집** — `build_frontend_data.py` 출력으로 자동 갱신. 수동 편집은 다음 실행 시 덮어쓰임.
3. **Plotly / Recharts / D3 외부 차트 라이브러리 추가** — 금지. hand-off의 SVG 기반 `<LineChart>` 사용.
4. **새 시각화 HTML 파일 생성** — 금지. UI는 오직 `http://localhost:5173` (hand-off 포팅본).
5. **`forecast_v2.py` 의 인덱스 (438, 506...) 를 그대로 표시** — `build_frontend_data.py` 가 `× 0.01` 스케일링으로 `$X.XX` 형태로 변환 (1.00 ~ 8.29 범위).
6. **A-4 Red Alert 누락** — `> 100` 이면 자동 `tone="alert"`, hand-off CSS의 pulsing dot 애니메이션이 작동.

---

## 11. 변경 이력

| Ver | 일자 | 변경 |
|---|---|---|
| 0.1 | 2026-05-15 | 초안 (TS 컴포넌트 쇼케이스) — ❌ hand-off 무시, 폐기 |
| 0.2 | 2026-05-16 | 핸드오프 직접 포팅 전환 (14 화면 동작) |
| **0.3** | **2026-05-18** | **실데이터 주입 파이프라인 추가 (`build_frontend_data.py`), 변경 금지/허용 매트릭스 명문화, news/events 데모 더미 표시 규칙 추가** |
