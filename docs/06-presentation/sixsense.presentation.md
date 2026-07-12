---
marp: true
theme: default
size: 16:9
paginate: true
header: 'Sixsense · Server DRAM Price Intelligence Dashboard'
footer: 'KAIST CAIO 10기 6조 · v2.1 · 2026-07-12'
style: |
  section {
    font-family: 'Pretendard Variable', 'Pretendard', 'Apple SD Gothic Neo', -apple-system, sans-serif;
    font-size: 22px;
    background: #fafaf8;
    color: #1a1a1a;
  }
  h1 { color: #1a1a1a; font-size: 38px; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; }
  h2 { color: #4a4a48; font-size: 28px; }
  h3 { color: #4a4a48; font-size: 22px; }
  table { font-size: 18px; border-collapse: collapse; }
  th { background: #f4f3ef; padding: 6px 10px; border: 1px solid #d8d4cc; text-align: left; }
  td { padding: 6px 10px; border: 1px solid #e8e6e0; }
  strong { color: #1a1a1a; font-weight: 700; }
  code { background: #f4f3ef; padding: 2px 6px; border-radius: 3px; font-size: 18px; }
  .small { font-size: 16px; color: #4a4a48; }
  .muted { color: #8a8884; }
  .pos { color: #16a34a; font-weight: 700; }
  .neg { color: #dc2626; font-weight: 700; }
  .neu { color: #ca8a04; font-weight: 700; }
  .info { color: #2563eb; font-weight: 700; }
  .pill { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 14px; font-weight: 600; }
  .pill-p0 { background: #fef2f2; color: #dc2626; border: 1px solid #dc2626; }
  .pill-p1 { background: #fefce8; color: #ca8a04; border: 1px solid #ca8a04; }
  .pill-p2 { background: #eff6ff; color: #2563eb; border: 1px solid #2563eb; }
  section.title {
    background: linear-gradient(135deg, #1a1a1a 0%, #4a4a48 100%);
    color: #fafaf8;
  }
  section.title h1 { color: #fafaf8; border-bottom: 2px solid #fafaf8; font-size: 56px; }
  section.title h2 { color: #c6c4be; }
  section.title .small, section.title .muted { color: #c6c4be; }
  section.demo { background: #1a1a1c; color: #f4f3ef; }
  section.demo h1 { color: #f4f3ef; border-bottom: 2px solid #f4f3ef; }
---

<!-- _class: title -->

# Sixsense

## Server DRAM Price Intelligence Dashboard

<br>

**서버급 DDR5 DRAM 가격을 21개 실데이터 신호와 Multi-Model 앙상블로 매주 자동 예측하는 B2B 의사결정 대시보드**

<br><br>

<span class="small">KAIST CAIO 10기 6조 · v2.1 (2026-07-12 iOS 전용앱 전환 + 모바일 디자인 개선)</span>

---

# 목차

| # | 주제 | 시간 |
|---|---|---|
| 1 | **Executive Summary** — 한눈에 요약 | 3분 |
| 2 | **Why & What** — 페르소나·핵심가치 | 3분 |
| 3 | **UI Hand-off Identity** — 14화면 SSOT | 3분 |
| 4 | **Architecture & Pipeline** — 데이터 흐름 6단계 | 3분 |
| 5 | **Multi-Model 검증** — GBR 4.54% · LSTM 9.19% | 2분 |
| 6 | **라이브 데모** — http://localhost:5173 | 4분 |
| 7 | **발전 방향** — Production 로드맵 | 2분 |

<br>

<span class="small">총 **20분** + Q&A</span>

---

<!-- ────────────────────── 1. Executive Summary ────────────────────── -->

# 1. Executive Summary

## 한 줄 정의

> 서버급 DDR5 DRAM 가격을 **21개 실데이터 신호** + **Multi-Model 앙상블 예측** + **LLM 종합 인사이트** + **글로벌 이벤트 모니터링**으로 매주 자동 갱신하는 **B2B 의사결정 대시보드**

## 4대 핵심 성과

| 영역 | 성과 |
|---|---|
| 🎯 **자동 수집** | <span class="pos">21/21 신호 (100%)</span> — 정형 7 + 비정형 7 + 거시 6 + 타겟 1 |
| 📊 **단기 예측** | **XGBoost** <span class="pos">MAPE 11.05%</span> (LightGBM 17.86% 대비 우수 모델 자동 선정) |
| 📈 **중장기 예측** | PyTorch LSTM <span class="pos">held-out MAPE 9.19%</span> — 단기 예측 끝점에 anchor하여 차트 연결성 확보 |
| 🤖 **AI 인사이트** | Claude → Gemini → **Groq** → 휴리스틱 4-tier fallback (v1.1 신규) |

---

# 1. Executive Summary — 한눈에

```
┌─────────────────────────────────────────────────────────────────────────┐
│  매주 화요일 06:00 KST  (또는 §09 풋바 "🔄 수동 갱신" 버튼 1클릭)        │
│                                                                          │
│  ① auto_collectors.py    →  21 신호 (Yahoo/SEC/FRED/KOSIS/관세청/AWS/   │
│                              Manifold/HN/GPR/RSS)                        │
│  ② collect_news_events   →  RSS 45 쿼리 → Gemini 분류 →                 │
│                              news 10건 + events 10건 (5 카테고리 분리)   │
│  ③ forecast_v2.py        →  Prophet + GBR + LSTM 재학습 (~12초)         │
│  ④ build_insight.py      →  LLM 종합 분석 400자 (한국어 완결 문장)      │
│  ⑤ build_frontend_data   →  frontend/src/mocks/data.js (50 KB)          │
│                                              ↓ Vite HMR 자동 반영        │
│                              http://localhost:5173 (14화면 hand-off)    │
└─────────────────────────────────────────────────────────────────────────┘
```

**프론트엔드** Vite :5173 (React 19 + TS) · **백엔드** FastAPI :8000 (15+3 endpoint) · **DB** Supabase Postgres (선택)

---

# 1. Executive Summary — 산출물 (PDCA)

| 단계 | 산출물 | 분량 |
|---|---|---|
| PM (PRD) | [prd.md](../../prd.md) — Hand-off SSOT Edition 18 섹션 | 447줄 |
| Plan | [docs/01-plan/features/sixsense.plan.md](../01-plan/features/sixsense.plan.md) | 353줄 |
| Design | [docs/02-design/features/sixsense.design.md](../02-design/features/sixsense.design.md) | 1,155줄 |
| Do | [docs/03-do/features/sixsense.do.md](../03-do/features/sixsense.do.md) — 사용자 확장 12 매트릭스 | 291줄 |
| Analysis | [docs/03-analysis/sixsense.analysis.md](../03-analysis/sixsense.analysis.md) | 374줄 |
| QA | [docs/05-qa/sixsense.qa-report.md](../05-qa/sixsense.qa-report.md) — L1/L2/L3 67/67 통과 | 221줄 |
| Report | [docs/04-report/sixsense.report.md](../04-report/sixsense.report.md) | 396줄 |
| Modeling | [docs/10-modeling/modeling-architecture.md](../10-modeling/modeling-architecture.md) — Phase 6 | 177줄 |

<br>

**Git history**: 58 commits, Phase 1~7 + v1.1 데이터 최신화 + v2.0/v2.1 iOS 전환·모바일 개선 누적

**v2.0/v2.1 하이라이트**: iOS 전용앱(PWA) 전환(홈 화면 설치·오프라인 지원) · 하단 탭바 모바일 UX · 예측 영향도 0%인 신호 4개 정리(14→10개) · 기상이변/Graph RAG 섹션 제거 · 모바일 카드·표 레이아웃 전면 재정비(가운데 정렬·가로 통합·구분선 표 형태)

---

<!-- ────────────────────── 2. Why & What ────────────────────── -->

# 2. Why — 왜 이 문제인가

## 서버 DRAM 가격 예측의 어려움

- **단일 신호로 불가**: 가격은 공급(팹 가동·재고)·수요(AI CapEx·하이퍼스케일러)·거시(환율·금리)·지정학(대만·중국·우크라이나) **다중 요인 결합** 결과
- **시장 데이터 비공개**: DRAMeXchange/TrendForce 등 contract price는 유료 (월 수천 달러)
- **언어 장벽**: 핵심 정보가 대만(중문)·한국(한글)·미국(영문)에 분산 → 통합 모니터링 부재
- **기간 미스매치**: 분기 IR 공시(3개월) ↔ 주간 의사결정 ↔ 일간 거시 → 주기 통합 필요
- **AI 폭증 변동성**: 2024~2026 HBM/AI 서버 수요로 기존 cyclical 패턴 붕괴

## Sixsense의 해법

**14 프록시 신호 + 5 거시 + 1 타겟 + AI 종합 → 매주 화요일 06:00 자동 갱신, 단일 화면 5분 의사결정**

---

# 2. What — 3 페르소나 × 1 화면

| 페르소나 | 핵심 니즈 | 사용 흐름 |
|---|---|---|
| **P1 메모리 기획팀장** | 주간 회의 "다음 7주 / 21주 가격이 어디로?" | S-001 메인 → 5분 안에 결론 + 근거 + 트랙레코드 |
| **P2 시장정보 애널리스트** | 모델이 왜 그렇게 판단했는지 검증 | S-001 → S-002 contribution → HITL로 임계치 조정 |
| **P3 영업/조달 담당** | 거시 환경과 글로벌 이벤트 영향 | S-008 거시지표 + S-010 이벤트 + S-007 뉴스 상세 |

## 5대 핵심 가치 명제

1. **자동 수집 100%** — 매주 화요일 06:00 KST, 21 신호 무인 갱신
2. **Multi-Model 앙상블** — 단기 XGBoost (11.05%) + 중장기 LSTM (9.19%) + Prophet baseline
3. **설명 가능한 AI** — 14 신호 contribution bars + AI 종합 코멘터리
4. **HITL** — 사용자가 긍정/중립/부정 임계치 조정 → 재학습 트리거
5. **정확도 트랙레코드 공개** — 매 예측의 실제 오차 누적 (S-012)

---

<!-- ────────────────────── 3. UI Hand-off Identity ────────────────────── -->

# 3. UI Hand-off Identity — 단일 진실원 (SSOT)

## 원칙 0 — Pixel Identity

> 모든 UI는 `design_handoff_sixsense_dram_dashboard/` (Claude Design 14화면 hifi)을 **1px도 변경하지 않고** 사용. 새 UI 디자인 금지. 외부 차트/UI 라이브러리(Plotly/Recharts/D3/MUI) 추가 금지.

## 디자인 토큰 (hand-off 그대로)

- 색상: warm white `#fafaf8` 배경 · monochrome accent (light `#1a1a1a` / dark `#f4f3ef`)
- Signal tones: <span class="pos">pos</span> #16a34a · <span class="neu">neu</span> #ca8a04 · <span class="neg">neg</span> #dc2626 · alert #b91c1c · <span class="info">info</span> #2563eb
- Forecast: 단기 <span class="info">--sig-info</span> blue · 중장기 <span class="pos">--forecast-mid</span> pastel green
- 폰트: Pretendard Variable (한글) + JetBrains Mono `.num` (tabular-nums)
- 간격: comfortable / compact 토글 (`data-density`)

## 14화면 + 7가지 사용자 명시 확장

12회의 사용자 직접 요청으로 hand-off를 **확장만**, 변경은 0회 (모든 확장은 hand-off 토큰 재사용)

---

# 3. 14 화면 맵 (S-001 ~ S-014)

| ID | 형태 | 이름 |
|---|---|---|
| S-001 | Full | **메인 대시보드** — 모든 위젯 집합 |
| S-002 | Modal | AI 예측 근거 (14 신호 contribution + CI band + HITL) |
| S-003 | Modal | 정형 데이터 Group A 상세 (7 tab) |
| S-004 | Modal | 비정형 데이터 Group B 상세 (7 tab) |
| S-005 | Modal | Graph RAG — 구리 ↔ DRAM 상관관계 |
| S-006 | Full | AI 뉴스 분석 전체 목록 |
| S-007 | Modal | 뉴스 원문 & AI 분석 상세 |
| S-008 | Full | 거시경제 5탭 (Fed/DXY/PMI/USD-KRW/Copper) |
| S-009 | Modal | 주별 신호 스냅샷 (then vs now) |
| S-010 | Full | 글로벌 이벤트 전체 목록 |
| S-011 | Modal | 글로벌 이벤트 상세 |
| S-012 | Full | AI 예측 정확도 전체 이력 |
| S-013 | Modal | 당시 신호 vs 현재 신호 비교 |
| S-014 | Full | 데이터 수집 현황 상세 |

---

# 3. 사용자 명시 확장 12회 (Phase 7)

| # | 영역 | 변경 |
|---|---|---|
| 1~3 | §01 가격 스냅샷 + 인사이트 카드 | 그리드 3→7분화 (가격:인사이트 3:4), Claude 종합 판단 강조 |
| 4 | §02 DRAM 차트 + Multi-Model | Prophet + HistGBR + **GBR★** + **LSTM★** 4모델 동시 표시 |
| 5 | §01 가격 카드 제목 통일 | 12px + text-mid + weight 600 |
| 6 | 차트 색상 + 토글 | Prophet 황색 dotted · HistGBR 보라 long-dash · 다크 모드 토글 강화 |
| 7 | §09 풋바 수동 갱신 | 🔄 버튼 → 5단계 백그라운드 + 진행률 + 자동 새로고침 |
| 8~10 | §07 글로벌 이벤트 + §06 macro | 5 카테고리 (국내반도체/물리적충돌/기상이변/금융위기/기타) + UST10 |
| 11~12 | 인사이트 모달 + 완결 문장 | 카드 클릭 → Modal 팝업 (400자 완결 분석) |

<br>

<span class="small">모든 확장은 `frontend/src/` 만 수정. `design_handoff_*/` 원본은 **불변**.</span>

---

<!-- ────────────────────── 4. Architecture & Pipeline ────────────────────── -->

# 4. Architecture

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
│                              │ ESM import (Vite HMR)             │
└──────────────────────────────┼───────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────┐
│  Backend FastAPI :8000 (uvicorn --reload, 18 endpoint)           │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │  pipelines/  (cron 매주 화요일 06:00 KST)                  │  │
│  │    ① auto_collectors.py     → data/historical/*.json       │  │
│  │    ② collect_news_events.py → data/news/+events/latest.json│  │
│  │    ③ forecast_v2.py         → data/forecast/forecast_v2.json│  │
│  │    ④ build_insight.py       → data/insight/latest.json     │  │
│  │    ⑤ build_frontend_data.py → frontend/src/mocks/data.js  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  External: Yahoo·SEC EDGAR·FRED·KOSIS·관세청·AWS·Manifold·      │
│            HN Algolia·GPR·RSS · LLM: Anthropic/Gemini/Groq      │
└──────────────────────────────────────────────────────────────────┘
```

---

# 4. 21 신호 매핑 (정형 7 + 비정형 7 + 거시 6 + 타겟 1)

| Group | ID | 이름 | 소스 |
|---|---|---|---|
| **정형 A** | A-1 | 대만 공급망 | Yahoo TSM+UMC |
| | A-2 | 빅테크 CapEx | SEC EDGAR XBRL 4사 |
| | A-3 | 관세청 수출 | data.go.kr Itemtrade (HS 854232) |
| | A-4 | 재고/출하 지수 | KOSIS Open API |
| | A-5 | AWS Spot | AWS EC2 Pricing |
| | A-6 | 봉쇄확률 | Manifold Markets |
| | A-7 | 구리 선물가 | Yahoo HG=F |
| **비정형 B** | B-1~B-7 | 감성/지정학/LTA/HBM/BOM | Google News + LLM 4-tier fallback |
| **거시** | macro-fed/dxy/pmi/krw/cu/**ust10** | 금리/DXY/PMI/USD-KRW/구리/**10년물** | FRED + Yahoo Finance |
| **타겟** | target-dram | DRAM 가격 프록시 | Yahoo: MU 50% + SK Hynix 30% + Samsung 20% (base 100 정규화) |

<br>

**LLM 4-tier chain**: Anthropic Claude → Gemini 2.5 Flash → Groq → 휴리스틱

---

# 4. 데이터 흐름 (5단계 + UI)

| 단계 | 입력 | 출력 | 소요 |
|---|---|---|---|
| ① **데이터 수집** | 외부 API/RSS (21 신호) | `data/historical/*.json` | ~30초 |
| ② **뉴스/이벤트** | RSS 45 쿼리 (NEWS 14 + EVENTS 31) | `data/news/latest.json` + `data/events/latest.json` | ~20초 |
| ③ **모델 재학습** | historical (108주 × 21열) | `data/forecast/forecast_v2.json` + `model_comparison.txt` | ~12초 |
| ④ **AI 인사이트** | meta + 신호 + 뉴스 → LLM | `data/insight/latest.json` (400자 완결) | ~5초 |
| ⑤ **프론트엔드 빌드** | 모든 산출물 → SIXSENSE_DATA | `frontend/src/mocks/data.js` (50 KB) | <1초 |

<br>

**총 ~70초** · 풋바 "🔄 수동 갱신" 버튼 1클릭으로 모든 단계 백그라운드 실행 + 자동 새로고침

---

<!-- ────────────────────── 5. Multi-Model 검증 ────────────────────── -->

# 5. Multi-Model 검증 — 단기 (1~7주)

## 모델 비교 (model_comparison.txt 실측, v1.1 기준)

| 모델 | MAPE | 평가 |
|---|---|---|
| **XGBoost ⭐** | <span class="pos">**11.05%**</span> | 우수 모델 자동 선정 |
| LightGBM | 17.86% | 대안 |

## 환경 처리 (v1.1 업데이트)

- `libomp` 설치 완료 → **XGBoost/LightGBM 정식 활성화** (v1.0 당시 sklearn GBR/HistGBR fallback에서 전환)
- 우수 모델은 매 학습 시점마다 MAPE 비교로 자동 재선정 (하드코딩 없음)
- LSTM은 **PyTorch** (libomp 무관, 즉시 작동)

---

# 5. Multi-Model 검증 — 중장기 (8~21주)

## LSTM (PyTorch 2-layer, hidden=64)

| 모델 | held-out MAPE |
|---|---|
| Prophet | (baseline) |
| **LSTM ⭐** | <span class="pos">**9.19%**</span> |

## 학습 시간 (전체 파이프라인)

| Stage | 소요 |
|---|---|
| Prophet | 0.64s |
| Tree (단기) | 4.22s |
| LSTM (중장기) | 6.52s |
| **합계** | **~11.4초** |

<br>

**차트에 4개 모델 동시 표시** (S-001 §02):
Prophet 황색 dotted · HistGBR 보라 long-dash · **GBR★** 청색 · **LSTM★** 초록

---

<!-- ────────────────────── 6. Live Demo ────────────────────── -->

<!-- _class: demo -->

# 6. 라이브 데모

## http://localhost:5173

<br>

| Step | 화면 | 강조 포인트 |
|---|---|---|
| 1 | **S-001 §01 가격 스냅샷** | 7분화 그리드 · 현재가 $7.46 · 1~7w $9.25 (+24.0%) · 8~21w $8.67 (+16.2%) · 예측분석 인사이트 |
| 2 | **인사이트 카드 클릭** → Modal | 400자 한국어 완결 분석 (LLM 4-tier fallback, 실패 시 휴리스틱도 완결 분석 보장) |
| 3 | **§02 DRAM 차트** | 4 모델 동시 표시 + MAPE 비교 표 (XGBoost★ 11.05% · LSTM★ 9.19%) · 단기→중장기 절벽 없이 자연 연결(anchor 보정) |
| 4 | **§07 글로벌 이벤트** | 5 카테고리 다양성 (국내반도체·물리적충돌·기상이변·금융위기·기타) |
| 5 | **§09 풋바 "🔄 수동 갱신"** | 5단계 백그라운드 + 진행률 바 + 자동 새로고침 |
| 6 | **다크 모드 토글** | topbar 우측 "☾ 다크 모드" → 즉시 전환 |

---

<!-- _class: demo -->

# 6. 데모 시나리오 — 예상 Q&A

**Q1. 가격이 $-단위인데 어떻게 산출했나요?**
→ target-dram은 메모리 4사 주가 블렌드를 100 정규화한 인덱스. UI 표시는 `index × 0.01 = $ 단위` 환산.

**Q2. LLM이 휴리스틱으로 떨어진 경우는?**
→ 4-tier fallback (Anthropic→Gemini→Groq→휴리스틱). 휴리스틱도 데이터 기반 400자 완결 분석 보장. UI에 모델명 표시.

**Q3. news와 events가 중복되지 않나요?**
→ NEWS_QUERIES (DRAM 산업 14) vs EVENTS_QUERIES (글로벌+국내 반도체 이벤트성 31)로 **entry 단계부터 분리**. EVENTS는 news와 title 중복 자동 제거.

**Q4. 매주 화요일 자동화는?**
→ 현재 데모는 수동 갱신 버튼. 운영 시 cron / GitHub Actions로 매주 화 06:00 KST 자동 실행.

---

<!-- ────────────────────── 7. Production 로드맵 ────────────────────── -->

# 7. Production 배포 — P0 Blocker (배포 전 필수)

| # | 항목 | 현재 | 필요 |
|---|---|---|---|
| <span class="pill pill-p0">P0</span> | **시크릿 관리** | `.env` 파일 | AWS Secrets Manager / Vault, 환경별 분리 |
| <span class="pill pill-p0">P0</span> | **LLM 비용/한도** | Gemini 무료 1,500/day | Anthropic 충전 + Gemini 유료 + Groq 키 (3중 안전망) |
| <span class="pill pill-p0">P0</span> | **인증/권한** | 없음 (CORS only) | Supabase Auth + RLS 강화 |
| <span class="pill pill-p0">P0</span> | **DB 영속화** | JSON 파일 | Supabase 스키마 적용 + sync_supabase.py cron |
| <span class="pill pill-p0">P0</span> | **수동 갱신 보호** | 누구나 호출 가능 | 인증 토큰 + rate limit + audit log |

---

# 7. P1 (30일) + P2 (차후)

## <span class="pill pill-p1">P1</span> High Priority

- **호스팅**: Vercel(frontend) + Railway/Fly.io(backend) + GitHub Actions cron
- **관측성**: Sentry (errors) + Datadog (metrics) + Slack 알림
- **CI/CD**: PR typecheck + lint + 단위테스트 + L1 API 테스트
- **데이터 품질 SLO**: 수집률 ≥95% · MAPE 유지 · LLM 성공률 ≥90%

## <span class="pill pill-p2">P2</span> 차후

- **법무**: RSS 저작권 약관 점검, 뉴스 출처 명시 강화
- **성능**: data.js 50KB → API lazy load 전환
- **사용성**: 멀티유저, 주간 Email/Slack 리포트, 모바일 반응형, i18n
- **AI 강화**: 백테스팅 자동화, SHAP explainability, foundation model (Chronos)

---

# 7. 30/60/90일 로드맵

| 기간 | Sprint | 산출물 |
|---|---|---|
| **Day 0~7** | 배포 직전 | 시크릿 매니저 · Supabase 활성 · LLM 유료 · 인증 · Vercel+Railway 배포 · GitHub Actions cron |
| **Day 8~30** | 안정화 | Sentry/Datadog · CI/CD 게이트 · SLO 대시보드 · HITL 권한 분리 |
| **Day 31~90** | 확장 | 주간 리포트 · 백테스팅 자동화 · 모바일 · 워크스페이스 (멀티 유저) |

<br>

## 즉시 데모 vs 운영 격차

| 영역 | 데모 | 운영 격차 |
|---|---|---|
| UI + 21 신호 + Multi-Model + LLM 인사이트 + 수동 갱신 | ✅ 작동 | — |
| Supabase 동기화 + cron 자동 | 코드 준비 | 활성화 필요 |
| 인증 + 모니터링 | ❌ | 도입 필요 |

---

<!-- _class: title -->

# Thank you 🙇

<br>

## Q & A

<br>

| | |
|---|---|
| GitHub commits | **58개** (Phase 1~7 + v1.1 데이터 최신화 + v2.0/v2.1 모바일 전환 누적) |
| 자동 수집 신호 | **21개 수집 · 화면 표시 10개** (예측 영향도 0% 신호 4개 정리) |
| 단기 MAPE | **11.05%** (XGBoost ⭐) |
| 중장기 MAPE | **9.19%** (LSTM ⭐) |
| AI 인사이트 | Claude→Gemini→Groq→휴리스틱 4-tier · 400자 완결 |
| iOS 전용앱 | PWA 홈 화면 설치 + 오프라인 지원 + 하단 탭바 |
| 현재 버전 | **v2.1** (2026-07-12) |

<br>

<span class="small">데모: http://localhost:5173 · 백엔드: http://localhost:8000/docs (OpenAPI)</span>
