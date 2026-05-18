# Sixsense — Server DRAM Price Intelligence Dashboard

> **PRD (Product Requirements Document) — Hand-off SSOT Edition**
> 본 PRD는 `design_handoff_sixsense_dram_dashboard/` (Claude Design hifi 14화면 산출물)을 **단일 진실원(SSOT)** 으로 삼아 작성되었다. **모든 UI는 hand-off의 픽셀과 컴포넌트를 100% 그대로 사용한다.** 새로운 UI 디자인을 만들지 않는다. 본 문서가 hand-off와 충돌할 경우 hand-off가 우선한다.

---

## 0. 메타

| 항목 | 내용 |
|---|---|
| 제품명 | **Sixsense (식스센스)** |
| 부제 | Server DRAM Price Intelligence Dashboard |
| 버전 | 0.6 (Hand-off SSOT Edition) |
| 일자 | 2026-05-18 |
| 소속 | KAIST CAIO 10기 6조 |
| UI SSOT | `design_handoff_sixsense_dram_dashboard/` (14 화면, hifi, React JSX) |
| 데이터 SSOT | `backend/data/historical/*.json` + `backend/data/forecast/forecast_v2_*.json` |
| 코드 SSOT | `frontend/src/` (hand-off 직접 포팅) + `backend/` (FastAPI + pipelines) |

---

## 1. 제품 한 줄 정의

서버급 DDR5 DRAM 가격을 **14개 프록시 신호(정형 7 + 비정형 7) + 5개 거시지표 + Multi-model 예측(단기 GBR · 중장기 LSTM · 베이스 Prophet)** 으로 매주 자동 갱신하는 B2B 의사결정 대시보드.

타겟 사용자: **메모리·반도체 전략/기획팀** (가격 콜을 내야 하는 의사결정자).

---

## 2. 사용자 & 페르소나

- **P1 — 메모리 기획팀장**: 주간 회의에서 "다음 7주 / 21주 가격이 어디로 가는가"를 답해야 함. 단일 화면(S-001)에서 결론 + 근거 + 정확도 트랙레코드까지 5분 안에 본다.
- **P2 — 시장정보 애널리스트**: 14개 신호를 드릴다운하며 모델이 왜 그렇게 판단했는지(S-002 contribution bars)를 검증한다. HITL 패널로 임계치를 조정해 재학습 트리거.
- **P3 — 영업/조달 담당**: 거시지표 페이지(S-008)와 글로벌 이벤트 목록(S-010) 위주로 본다. 뉴스 상세(S-007)에서 단기/중장기/장기 영향 판단을 참고.

---

## 3. 핵심 가치 명제

1. **14 신호 자동 수집 100%**: 매주 화요일 06:00 KST, 정형 7 + 비정형 7 신호가 자동 갱신 (현재 20/20 신호 자동화).
2. **Multi-model 앙상블**: 단기 GBR (MAPE 4.54%) + 중장기 LSTM (MAPE 9.19%) + 베이스 Prophet.
3. **설명 가능한 AI**: 모든 예측이 14 신호 기여도 막대 + AI 종합 판단 코멘터리로 시각화된다 (S-002).
4. **HITL (Human-In-The-Loop)**: 사용자가 긍정/중립/부정 임계치를 직접 조정해 재학습할 수 있다 (전 상세 화면).
5. **정확도 트랙레코드 공개**: 매 예측의 실제 오차를 S-012에서 누적 공개. MAPE 추이 라인차트.

---

## 4. UI 원칙 (SSOT)

**규칙 0 — Hand-off Pixel Identity:**
모든 화면은 `design_handoff_sixsense_dram_dashboard/src/{app,dashboard,modals,pages,components}.jsx` 의 컴포넌트·레이아웃·색상·간격·타이포그래피를 1px도 변경하지 않고 사용한다. 신규 UI 디자인을 만들지 않는다.

**규칙 0-예외 — 사용자 명시 확장 (User-Requested Extension):**
사용자가 직접 "이 영역 옆에 X를 추가해줘" 같이 구체적 UI 확장을 지시한 경우에만 hand-off를 확장한다. 이 경우에도 (a) `design_handoff_*/` 원본은 절대 건들지 않고 `frontend/src/` 만 수정, (b) 외부 차트/UI 라이브러리 추가 금지(Plotly/Recharts/D3/MUI 등), (c) 신규 컴포넌트는 hand-off의 디자인 토큰(card/dlabel/num/ai-note CSS 클래스 + Pretendard + JetBrains Mono)만 조합해서 만든다.

**현재까지 확장된 영역**:
| 영역 | 확장 내용 | 추가 컴포넌트 | 추가 CSS |
|---|---|---|---|
| S-001 §01 가격 스냅샷 | 4번째 슬롯에 "예측분석 인사이트" 카드 추가, 그리드 7분화 (1fr 1fr 1fr 4fr = 가격 3 : 인사이트 4, #5). 본문 14px, summary 내 `**bold**` 강조 단어는 tone 컬러 + 배경 chip, 헤드라인 15px / weight 800 / tone 색상. §01 가격 3카드의 제목("현재 계약가" 등) 11px → 12px + 색상 `--text-mid` (인사이트 헤더와 통일, #5) | `<InsightCard>` + `renderInsightEmphasis` (components.jsx) | `.grid-snapshot`, `.insight-card`, `.insight-headline`, `.insight-emphasis`, `.insight-tone-{pos\|neu\|neg}`, `.grid-snapshot > .card > .card-h` (styles.css) |
| S-001 §02 DRAM 차트 | 차트 카드 아래에 MAPE 비교 표 2개 (단기 Prophet/HistGBR/GBR★ + 중장기 LSTM + 학습 시간). 차트 자체에 4개 모델 라인 동시 표시 — **Prophet baseline 황색 dotted (2 4)** + **HistGBR 보라 long-dash (7 3)** + **GBR★ 청색** + **LSTM★ 초록** (#6a 색·패턴 강화). 인사이트 헤드라인 17px→15px, 본문/CLAUDE 박스 좌·우 분할. **Topbar 다크/라이트 모드 토글 버튼 가시성 강화** (#6b) | `<ModelValidationPanel>` · DramChart 4-line · LineChart `dashed` string 지원 | `.model-validation`, `.model-table`, `.model-train-time`, `.insight-main`, `--chart-baseline`/`--chart-secondary` 토큰, `.theme-toggle` (styles.css) |
| S-001 §09 풋바 | **수동 갱신 패널** 추가 (#7) — "🔄 수동 갱신 실행" 버튼 클릭 시 백엔드가 5단계 파이프라인을 백그라운드 실행, 진행률 바 + 단계별 로그를 풋바 아래 표시, 완료 시 자동 페이지 새로고침으로 신규 데이터 반영 | `<RefreshPanel>` (dashboard.jsx) | `.refresh-*` (styles.css) + backend `POST /api/refresh` / `GET /api/refresh/jobs/{id}` / `GET /api/refresh/stages` |
| S-001 §07 글로벌 이벤트 | **5 카테고리 다양화 + 10건 보장 + 한국어 요약** (#8/#9) — 사용자 정의 5 카테고리(**국내 반도체** / 물리적 충돌 / 기상이변 / 금융 위기 / 기타)로 LLM·휴리스틱 강제 분류. **국내 반도체 1순위** (삼성/하이닉스 파업·정전·화재) — 회사명+이벤트 키워드 조합 매칭. diversify_events() 5 카테고리 각 1건 강제 보장 + 라운드-로빈 + 부족 시 placeholder. **`korean_summary()` 휴리스틱 한국어 요약 자동 생성** — LLM 비활성 시에도 모든 요약 한국어. UI에 **유형 칩(보라/적색/황색/청색/회색)** + 위험도 + 제목 + 지역 4-column 그리드 | collect_news_events.py + dashboard.jsx §07 events-row | `.events-type-domestic/conflict/weather/financial/other` |
| §05 AI 뉴스 + §07 글로벌 이벤트 풀 분리 + §06 UST10 추가 (#10) | (1) news/events 가 같은 enriched pool 에서 동시 생성되던 구조 → entry 단계부터 완전 분리. NEWS_QUERIES (DRAM 산업 직접 14개) vs EVENTS_QUERIES (글로벌+국내반도체 이벤트성 31개). LLM 호출 단일화하되 `{news:[], events:[]}` 분리 출력 강제. news 중복 제거 후 events 처리. (2) 거시경제 §06에 **미국 10년물 국채금리 (FRED DGS10)** 신규 — 위험자산 선호도 지표, ↑ 시 DRAM 부정 | collect_news_events.py NEWS/EVENTS 풀 분리 · backfill.py collect_macro_ust10 | MACRO_META 6개 |
| §01 인사이트 카드 클릭 → 전체 모달 팝업 (#11) | 250자 LLM 분석이 카드에서 잘림 → 본문 8줄 clamp + fade gradient, 카드 전체 클릭 가능, hand-off `<Modal>` 로 전체 분석 팝업 (헤드라인 19px + 핵심 신호 chip + 250자 본문 15.5px + 생성 시각, ESC/외부 클릭 닫기) | components.jsx `InsightCard` + hand-off `<Modal>` | `.insight-body-clamp`, `.insight-modal-summary` |

**디자인 토큰** (hand-off `src/styles.css` 발췌):
- 색상: Warm white `#fafaf8` / Pure white `#ffffff` 배경, monochrome 액센트 `#1a1a1a` (light) / `#f4f3ef` (dark)
- Signal tones: `--sig-pos #16a34a`, `--sig-neu #ca8a04`, `--sig-neg #dc2626`, `--sig-alert #b91c1c`, `--sig-info #2563eb`
- Forecast emphasis: 단기 `--sig-info #2563eb` (blue dashed), 중장기 `--forecast-mid #10b981` (pastel green)
- 폰트: Pretendard Variable (한글) + Inter (라틴) + JetBrains Mono (`.num` — tabular-nums + nowrap)
- 간격: comfortable (pad 20×16, gap 14) / compact (pad 14×10, gap 8) — `data-density` 속성
- 라운드: 4 / 6 / 10 (sm / default / lg)

**핵심 컴포넌트** (hand-off `components.jsx`):
`<Sig>`, `<Sparkline>`, `<MetricCard>`, `<LineChart>` (SVG 기반, series·bands·refLines), `<Modal>` (스택), `<Tabs>`, `<Seg>`, `<HITL>`, `<AiNote>`, `<BarRow>`.

---

## 5. 화면 맵 (14 화면, hand-off 1:1)

| ID | 형태 | 이름 | 핵심 위젯 |
|---|---|---|---|
| S-001 | Full page | 메인 대시보드 | 가격 스냅샷 3카드 **+ 예측분석 인사이트 카드 (6분화 3:3, 사용자 요청 확장 #1/#2/#3)** + DRAM 52주 + 1~7w/8~21w 예측 차트 (Seg 단기/중장기/전체) **+ Phase 6 Multi-Model 검증 패널 (MAPE 표 + 아키텍처, 사용자 요청 확장 #3)** + 14 신호 카드 + Graph RAG (구리↔DRAM) + AI 뉴스/거시 2-col + 이벤트/정확도 2-col + 수집 풋바 |
| S-002 | Modal | AI 예측 근거 상세 | 14 신호 contribution bars + CI band 차트 + 주별 예측 표 + `<AiNote>` + `<HITL>` |
| S-003 | Modal (7 tabs A-1…A-7) | 정형 데이터 Group A 상세 | 신호별 28주 추세 + 원시 데이터 표 + AI 해석. A-4 > 100 시 Red Alert 배너 |
| S-004 | Modal (7 tabs B-1…B-7) | 비정형 데이터 Group B 상세 | 신호별 8주 감성 추세 + 뉴스 기사 리스트 + AI 해석 |
| S-005 | Modal | Graph RAG — 구리 ↔ DRAM 상관관계 | 104주 오버레이 + Lead-time 상관계수 막대 + 인과 경로 다이어그램 |
| S-006 | Full page | AI 뉴스 분석 전체 목록 | 필터(감성·소스·날짜) + 정렬 + 카드/표 리스트 |
| S-007 | Modal | 뉴스 원문 & AI 분석 상세 | AI 요약 + 단/중/장기 영향 + 연결 신호 + 원문 링크 |
| S-008 | Full page (5 tabs) | 거시경제 지표 통합 | Fed / DXY / PMI / USD-KRW / Copper. 52주 추세 + 월별 원시 + DRAM 상관 코멘터리 |
| S-009 | Modal | 주별 신호 스냅샷 | 과거: 그 시점 14신호 vs 현재 비교 + 오차. 미래: 예측 분해 |
| S-010 | Full page | 글로벌 이벤트 전체 목록 | 필터(리스크·타입·지역) + 이벤트 리스트 |
| S-011 | Modal | 글로벌 이벤트 상세 | AI 요약 + 단/중/장기 영향 + 연결 뉴스 + 영향 신호 |
| S-012 | Full page | AI 예측 정확도 전체 이력 | MAPE 누적 라인 + 필터(7w / 21w / all) + 히스토리 표 |
| S-013 | Modal | 당시 신호 vs 현재 신호 비교 | 14 신호 then/now 좌우 비교 + AI 오차 원인 설명 |
| S-014 | Full page | 데이터 수집 현황 상세 | 신호별 소스/마지막 수집/신규 건수/주간 델타/성공률 |

---

## 6. 14 프록시 신호 (실데이터 매핑)

### 6.1 Group A — 정형 (7종)

| ID | 이름 | 실제 데이터 소스 | 갱신 주기 | 백엔드 파일 |
|---|---|---|---|---|
| A-1 | 대만 공급망 | Yahoo Finance: TSM (70%) + UMC (30%) 블렌드 | 주간 | `historical/A-1.json` |
| A-2 | 빅테크 CapEx | SEC EDGAR XBRL — 4사 분기 공시 (AWS·MSFT·GOOGL·META) | 분기 | `historical/A-2.json` |
| A-3 | 관세청 수출 | data.go.kr Itemtrade API (HS 854232 메모리, imexTpcd=수출) | 주간 | `historical/A-3.json` |
| A-4 | 재고/출하 지수 | KOSIS Open API (사용자 생성 URL) | 월간→주간 forward-fill | `historical/A-4.json` |
| A-5 | AWS Spot 가격 | AWS EC2 Spot Pricing API (p4d.24xlarge, us-east-1) | 90일 한계 | `historical/A-5.json` |
| A-6 | 봉쇄확률 | Manifold Markets ("China invasion of Taiwan before 2030") | 실시간 | `historical/A-6.json` |
| A-7 | 구리 선물가 | Yahoo Finance HG=F (COMEX Copper, LME 대체) | 주간 | `historical/A-7.json` |

### 6.2 Group B — 비정형 (7종, LLM 감성)

| ID | 이름 | 실제 데이터 소스 | LLM | 백엔드 파일 |
|---|---|---|---|---|
| B-1 | Earnings Call | Google News RSS ('Earnings Call sentiment', 168건/33주) | 4-tier fallback | `historical/B-1.json` |
| B-2 | 대만 뉴스 감성 | TechNews.tw + Digitimes + Google News (1038건/39주) | 4-tier fallback | `historical/B-2.json` |
| B-3 | Reddit/HN | Hacker News Algolia API (DRAM 쿼리) | 4-tier fallback | `historical/B-3.json` |
| B-4 | 지정학 리스크 | Caldara & Iacoviello GPR Index (외부 xls) | (수치형) | `historical/B-4.json` |
| B-5 | LTA 비율 | DRAMeXchange 프록시 (Google News) | 4-tier fallback | `historical/B-5.json` |
| B-6 | HBM/D램 믹스 | TrendForce 프록시 (Google News) | 4-tier fallback | `historical/B-6.json` |
| B-7 | BOM 신호 | Hacker News Algolia (PCB·기판 쿼리 4건) | (수치형) | `historical/B-7.json` |

**LLM 4-tier fallback chain:** Anthropic → Gemini 2.5 Flash → Groq → keyword.

### 6.3 거시경제 (5종)

| ID | 이름 | 소스 | 파일 |
|---|---|---|---|
| macro-fed | 미국 금리 (DFF) | FRED CSV | `historical/macro-fed.json` |
| macro-dxy | 달러 인덱스 | Yahoo Finance DX-Y.NYB | `historical/macro-dxy.json` |
| macro-pmi | 산업생산지수 (PMI 대체) | FRED INDPRO | `historical/macro-pmi.json` |
| macro-krw | USD/KRW | Yahoo Finance KRW=X | `historical/macro-krw.json` |
| macro-cu | 구리 가격 | Yahoo Finance HG=F | `historical/macro-cu.json` |
| macro-ust10 | 미국 10년물 국채금리 | FRED DGS10 (10-Year Treasury Constant Maturity) | `historical/macro-ust10.json` |

### 6.4 타겟

| ID | 이름 | 소스 | 정규화 |
|---|---|---|---|
| target-dram | Server DRAM 가격 프록시 | Yahoo Finance 블렌드: MU 50% + SK Hynix 30% + Samsung 20% | base 100 (2025-05-01 = 100) |

---

## 7. 데이터 흐름 (실데이터 → hand-off UI)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  매주 화요일 06:00 KST                                                       │
│                                                                              │
│  [auto_collectors.py --all]                                                  │
│     ├─ A-1…A-7 (정형) ────→ backend/data/historical/A-*.json                │
│     ├─ B-1…B-7 (비정형, LLM) → backend/data/historical/B-*.json             │
│     ├─ macro-* ──────────→ backend/data/historical/macro-*.json             │
│     └─ target-dram ──────→ backend/data/historical/target-dram.json         │
│                                ↓                                             │
│  [collect_news_events.py]  RSS (TechNews/Digitimes/Google News × 14 쿼리)   │
│     → Gemini 분류 → backend/data/news/latest.json (10건)                    │
│                       backend/data/events/latest.json (≤8건)                │
│                                ↓                                             │
│  [forecast_v2.py] Prophet + GBR(short) + LSTM(mid)                           │
│     └─ backend/data/forecast/forecast_v2_2026-02-w1.json                    │
│                                ↓                                             │
│  [build_insight.py]  Anthropic Claude → Gemini → 휴리스틱 fallback           │
│     └─ backend/data/insight/latest.json  (S-001 인사이트 카드용)             │
│                                ↓                                             │
│  [build_frontend_data.py]                                                    │
│     └─ frontend/src/mocks/data.js  (SIXSENSE_DATA export)                   │
│                                ↓                                             │
│  [Vite HMR] hand-off React 앱이 자동 리로드                                  │
│     └─ http://localhost:5173  (14 화면 hand-off, 실데이터)                   │
└────────────────────────────────────────────────────────────────────────────┘
```

**중요**: hand-off UI 코드(`frontend/src/screens/*.jsx`, `frontend/src/components/components.jsx`) 는 절대 수정하지 않는다. 데이터만 `mocks/data.js` 를 통해 주입한다.

---

## 8. 기능 요구사항

### 8.1 P0 (필수)

| # | 기능 | 화면 | 검증 |
|---|---|---|---|
| F-01 | 14 신호 자동 주간 수집 | (백엔드) | `auto_collectors.py --all` 종료코드 0, 20/20 OK |
| F-02 | Multi-model 예측 (Prophet + GBR + LSTM) | (백엔드) | `forecast_v2.py` MAPE 출력 |
| F-03 | 가격 스냅샷 3카드 (현재·1~7w·8~21w) | S-001 | hand-off MetricCard, 클릭 시 S-002 |
| F-04 | DRAM 52주 차트 + Seg(단기/중장기/전체) | S-001 | hand-off LineChart, range 변경 시 시리즈 토글 |
| F-05 | 14 신호 카드 그리드 (Group A 7 + B 7) | S-001 | hand-off SignalCard, 클릭 시 S-003/S-004 |
| F-06 | AI 예측 근거 모달 (contribution + CI + 표) | S-002 | hand-off Modal + BarRow + LineChart |
| F-07 | A-4 Red Alert (>100) | S-001 / S-003 | tone="alert", pulsing dot |
| F-08 | 거시지표 5탭 페이지 | S-008 | hand-off Tabs + LineChart |
| F-09 | 정확도 트래킹 | S-012 | hand-off LineChart MAPE 추이 + 표 |
| F-10 | 수집 현황 페이지 | S-014 | hand-off 표, 신호별 마지막 수집 + 신규 건수 |

### 8.2 P1 (강화)

| # | 기능 | 화면 |
|---|---|---|
| F-11 | HITL 임계치 조정 + 재학습 트리거 | S-002/S-003/S-004/S-007/S-008/S-009/S-010/S-011/S-012/S-013 |
| F-12 | Graph RAG (구리↔DRAM 인과 경로) | S-005 |
| F-13 | 뉴스 필터/정렬 + 상세 모달 | S-006/S-007 |
| F-14 | 이벤트 필터 + 상세 모달 (단/중/장기 영향) | S-010/S-011 |
| F-15 | 주별 신호 스냅샷 (과거 vs 현재) | S-009/S-013 |
| F-16 | 다크 모드 + Density 토글 | (전 화면) data-theme / data-density |

### 8.3 P2 (선택)

| # | 기능 |
|---|---|
| F-17 | Supabase REST 동기화 (signals + signal_data + forecasts) |
| F-18 | URL 딥링크 (`?screen=S-008&tab=fed`) |
| F-19 | Tweaks 패널 (개발용, 운영 시 제거) |

---

## 9. 비기능 요구사항

| 항목 | 목표 |
|---|---|
| 단기 MAPE (1~7w) | ≤ 7% (현재 GBR 4.54% ✅) |
| 중장기 MAPE (8~21w) | ≤ 12% (현재 LSTM 9.19% ✅) |
| 자동 수집 성공률 | ≥ 95% (현재 20/20 = 100%) |
| 갱신 주기 | 매주 화요일 06:00 KST |
| 차트 렌더링 | < 200ms (SVG, 52주 + 21주 forecast) |
| 한글 폰트 | Pretendard Variable, `word-break: keep-all` 강제 |
| 다크/라이트 | localStorage 영속, 즉시 전환 |
| 접근성 | ESC로 모달 닫기, 클릭 외 영역 닫기, 키보드 탭 순환 |

---

## 10. 기술 스택

### 10.1 Frontend
- React 19 + TypeScript + Vite 8
- Hand-off JSX 직접 포팅 (`frontend/src/screens/*.jsx`, `frontend/src/components/components.jsx`)
- `App.tsx`는 thin TS wrapper로 `screens/app.jsx`를 마운트
- SVG 기반 LineChart (외부 차트 라이브러리 없음)
- CSS 변수 기반 디자인 토큰 (`styles.css`)

### 10.2 Backend
- FastAPI + Python 3.9.6 (15 endpoints)
- pipelines: `auto_collectors.py`, `forecast_v2.py`, `build_frontend_data.py`, `sync_supabase.py`, `backfill.py`
- Multi-model: Prophet (베이스) + sklearn GradientBoostingRegressor (단기, macOS libomp 회피) + PyTorch LSTM (중장기, seq2seq 12→21)
- 데이터 저장: JSON 파일 (1차) + Supabase Postgres (2차, 선택)

### 10.3 데이터 수집
- HTTP: requests + 4-tier LLM fallback (Anthropic → Gemini → Groq → keyword)
- 외부 API: Yahoo Finance, SEC EDGAR, FRED CSV, KOSIS, 관세청, AWS Pricing, Manifold, Hacker News Algolia, GPR Index, RSS (TechNews/Digitimes/Google News)

---

## 11. 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (http://localhost:5173)          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  React 19 / Vite — hand-off 직접 포팅 (14 화면)             │  │
│  │  • src/screens/{app, dashboard, modals, pages}.jsx         │  │
│  │  • src/components/components.jsx (Sig, MetricCard, ...)    │  │
│  │  • src/mocks/data.js  ← AUTO-GENERATED (실데이터)           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ▲                                   │
│                              │ ESM import (HMR)                  │
└──────────────────────────────┼───────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────┐
│  Backend (FastAPI, port 8000)│                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │  pipelines/                                                │  │
│  │    auto_collectors.py  ──▶ data/historical/*.json          │  │
│  │    forecast_v2.py      ──▶ data/forecast/forecast_v2_*.json│  │
│  │    build_frontend_data.py ─▶ frontend/src/mocks/data.js   │  │
│  │    sync_supabase.py    ──▶ Postgres (선택)                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  External Data Sources                                     │   │
│  │  Yahoo Finance | SEC EDGAR | FRED | KOSIS | 관세청          │   │
│  │  AWS Pricing  | Manifold  | HN Algolia | GPR | RSS         │   │
│  │  LLM: Anthropic / Gemini / Groq                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 12. 디렉토리 구조

```
Sixsense/
├── .env                                # API 키 (gitignored)
├── prd.md                              # 본 PRD (hand-off SSOT edition)
├── NEXT_STEPS.md                       # 현재 상태 요약
├── design_handoff_sixsense_dram_dashboard/   # ★ UI SSOT (변경 금지)
│   ├── README.md                       # 14화면 설계서
│   ├── Sixsense.html                   # 통합 프로토타입
│   ├── Sixsense Canvas.html            # 14화면 캔버스
│   └── src/{app, dashboard, modals, pages, components, data, styles, tweaks-panel}
├── frontend/                           # React 앱 (hand-off 직접 포팅)
│   ├── src/App.tsx                     # thin wrapper
│   ├── src/screens/{app, dashboard, modals, pages, tweaks-panel}.jsx
│   ├── src/components/components.jsx   # 공통 컴포넌트
│   └── src/mocks/data.js               # ★ AUTO-GENERATED (실데이터)
├── backend/
│   ├── app/main.py                     # FastAPI 15 endpoints
│   ├── app/schema.sql                  # Supabase DDL
│   ├── pipelines/
│   │   ├── auto_collectors.py          # 20개 신호 수집기
│   │   ├── forecast_v2.py              # Prophet + GBR + LSTM
│   │   ├── build_frontend_data.py      # 실데이터 → frontend mocks
│   │   ├── sync_supabase.py            # JSON → Postgres
│   │   └── backfill.py
│   └── data/
│       ├── historical/{A-*, B-*, macro-*, target-dram}.json
│       └── forecast/forecast_v2_*.json
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

## 13. 실행 방법

### 13.1 한 줄 데모 (실데이터 + Multi-model + hand-off UI)

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend && \
  source ../.env && \
  .venv/bin/python3 pipelines/auto_collectors.py --all && \
  .venv/bin/python3 pipelines/collect_news_events.py && \
  .venv/bin/python3 pipelines/forecast_v2.py && \
  .venv/bin/python3 pipelines/build_insight.py && \
  .venv/bin/python3 pipelines/build_frontend_data.py
# (위 5개가 매주 화요일 06:00 KST 자동 실행 대상)

# 프론트엔드 (이미 실행 중이면 HMR 자동 반영)
cd ../frontend && npm run dev
# → http://localhost:5173
```

### 13.2 개별 단계

```bash
# 데이터 수집만
.venv/bin/python3 pipelines/auto_collectors.py --all

# 뉴스/이벤트 (RSS → Gemini)
.venv/bin/python3 pipelines/collect_news_events.py

# 예측분석 인사이트 (Claude/Gemini 종합 판단)
.venv/bin/python3 pipelines/build_insight.py

# 예측만
.venv/bin/python3 pipelines/forecast_v2.py

# 데이터 → frontend mocks 변환만
.venv/bin/python3 pipelines/build_frontend_data.py

# Backend API
.venv/bin/uvicorn app.main:app --port 8000

# Supabase 동기화 (선택, schema.sql 1회 실행 후)
.venv/bin/python3 pipelines/sync_supabase.py
```

---

## 14. 검증 기준 (Acceptance)

### 14.1 자동 (L1)
- [ ] `pytest backend/tests/` 전부 통과
- [ ] `bash backend/tests/l1_api_test.sh` 41/41 통과
- [ ] `build_frontend_data.py` 종료코드 0, `frontend/src/mocks/data.js` 갱신 확인

### 14.2 수동 (L2 — 브라우저)
- [ ] S-001 진입 시 가격 스냅샷 3카드에 실측 $-가격 표시 (현재 $6.09)
- [ ] DRAM 차트 52주 history + 1~7w forecast + 8~21w forecast 모두 렌더
- [ ] Seg(단기/중장기/전체) 클릭 시 차트 시리즈 변화
- [ ] 14 신호 카드 클릭 시 S-003/S-004 모달 오픈 + 해당 tab 활성
- [ ] S-002 모달에서 contribution bars + AiNote 렌더
- [ ] S-008 5탭(Fed/DXY/PMI/USD-KRW/Copper) 전부 실측 데이터로 렌더
- [ ] S-012에서 accuracy 21건 표시 + MAPE 라인 차트
- [ ] S-014에서 20/20 신호 수집 현황 표시
- [ ] 다크 모드 토글 + Density 토글 정상 작동

### 14.3 정합성 (L3)
- [ ] 모든 신호의 `source` 필드가 실제 수집 소스명을 반영
- [ ] 단기 MAPE ≤ 7% (현재 4.54% ✅)
- [ ] 중장기 MAPE ≤ 12% (현재 9.19% ✅)
- [ ] news 10건 / events 4건이 최근 30일 RSS + Gemini 분류로 채워짐 ([news/latest.json](backend/data/news/latest.json))

---

## 15. 리스크 & 가정

| # | 항목 | 내용 | 완화 |
|---|---|---|---|
| R-01 | target-dram 프록시 한계 | 실제 contract price API가 없어 메모리 4사 주가 블렌드를 인덱스로 사용 | 운영 시 DRAMeXchange/InSpectrum 유료 피드 결합 가능 |
| R-02 | news / events 30일 윈도우 | RSS는 보통 30일치만 노출 → 초기 history 부족 | `collect_news_events.py` 를 매주 cron 누적 호출하면 1년 차 완전 history 확보 |
| R-03 | LLM 크레딧 | Anthropic 잔액 0 → Gemini 무료 fallback 우선 | 4-tier chain으로 자동 대체 |
| R-04 | A-5 AWS Spot 90일 한계 | API 제약상 최대 90일 (11주) 데이터만 | 운영 시 매주 누적 저장으로 long history 구축 |
| R-05 | macOS libomp 미설치 | XGBoost/LightGBM 사용 불가 | sklearn GradientBoostingRegressor 자동 fallback |
| R-06 | Hand-off 변경 유혹 | 기능 추가 시 신규 UI 만들고 싶은 충동 | **본 PRD §4 규칙 0 — Hand-off Pixel Identity 위반 금지** |

---

## 16. 일정 (PDCA)

| 단계 | 산출물 | 상태 |
|---|---|---|
| PRD | 본 문서 (Hand-off SSOT Edition) | ✅ |
| Plan | `docs/01-plan/features/sixsense.plan.md` | (hand-off 기준 재정렬 예정) |
| Design | `docs/02-design/features/sixsense.design.md` (hand-off 그대로) | ✅ |
| Do | `docs/03-do/features/sixsense.do.md` | ✅ (hand-off 직접 포팅) |
| Check | `docs/03-analysis/sixsense.analysis.md` | ✅ |
| Report | `docs/04-report/sixsense.report.md` | ✅ |
| QA | `docs/05-qa/sixsense.qa-report.md` | ✅ (67/67) |

---

## 17. KAIST CAIO 6조 제출용 요약

> Sixsense는 **Claude Design hand-off로 만든 14화면 hifi 디자인을 1px도 바꾸지 않고 React로 직접 포팅**하고, **20개 실데이터 신호를 자동 수집해 Multi-model 앙상블(단기 GBR 4.54% MAPE, 중장기 LSTM 9.19% MAPE)** 로 매주 갱신하는 B2B 서버 DRAM 가격 의사결정 대시보드입니다. 모든 PDCA 산출물이 hand-off를 단일 진실원으로 삼아 작성되었으며, 운영 단계에서 별도 UI 재작업 없이 데이터·모델만 강화하면 즉시 production에 투입할 수 있습니다.

---

## 18. Version History

| Ver | 일자 | 주요 변경 |
|---|---|---|
| 0.1 | 2026-05-15 | 초기 PRD (18 섹션, 1641 lines) |
| 0.2~0.5 | 2026-05-16~17 | Phase 5 / 5e / 5f 누적 |
| **0.6** | **2026-05-18** | **Hand-off SSOT Edition — 화면·컴포넌트·데이터 흐름 모두 hand-off 기준으로 재작성. `build_frontend_data.py` 추가로 실데이터 → hand-off UI 자동 주입.** |
