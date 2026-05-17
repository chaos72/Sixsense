# sixsense Design Document

> **Summary**: 서버용 DRAM 가격을 단기(1~7주)/중장기(8~21주)로 자동 예측하는 14화면 B2B 인텔리전스 대시보드의 기술 설계. 프론트엔드(React 18 + TS + Vite + Recharts), 백엔드(FastAPI + PostgreSQL + Redis), 데이터 수집 파이프라인(매주 화 06:00 KST), HITL 임계치 조정 기능을 포괄.
>
> **Project**: Server DRAM Price 식스센스 (KAIST CAIO 10기 6조)
> **Version**: 0.1
> **Author**: 김영석 (Dataiku Korea, 프로젝트 리드)
> **Date**: 2026-05-17
> **Status**: Approved (Option C — Pragmatic Balance)

### Pipeline References

- PRD: `docs/00-pm/sixsense.prd.md` (18 섹션)
- Plan: `docs/01-plan/features/sixsense.plan.md` (Architecture 결정 사슬)
- Design Hand-off: `design_handoff_sixsense_dram_dashboard/` (14화면 hifi 프로토타입 SSOT)

---

## Context Anchor

> Plan 문서에서 복사. Do 문서로 전파.

| Key | Value |
|-----|-------|
| **WHY** | 반도체 가격 예측을 위한 데이터 수집·분석에 사람·시간·비용이 과다 투입되고 시장 급변에 대응 못함 |
| **WHO** | 반도체 영업전략/구매/마케팅/시장분석/금융투자 부서의 50대 임원 5명 |
| **RISK** | (1) 14신호 수집 실패 시 예측 정확도 급락 (2) HITL 재학습 응답 지연 (3) SVG → Recharts 신뢰구간 밴드 재현 |
| **SUCCESS** | KPI: 업무시간 절감 ≥70%, 예측 정확도(MAPE) ≥80%, 사용자 수정률 ≤10%, API p95 ≤60ms |
| **SCOPE** | Phase 0 디자인 시스템 → Phase 6 검증 (총 7주, 모듈 7개 / 세션 10개) |

---

## Design Anchor

> Claude Design 핸드오프(`design_handoff_sixsense_dram_dashboard/`)가 디자인 토큰 잠금 역할. Pencil MCP 미사용. PRD §16 디자인 토큰 섹션 + 핸드오프 `src/styles.css` 가 시각 SSOT.

---

## 1. Overview

### 1.1 Design Goals

1. **단일 진실 공급원(SSOT) 원칙** — UI는 Claude Design 핸드오프, 기술 결정은 본 Design 문서, 사용자 요구는 PRD가 각각 SSOT.
2. **픽셀 단위 디자인 재현** — 핸드오프 `Sixsense.html`과 ±1px 오차 이내. 디자인 토큰만 사용(hex 직접 입력 금지).
3. **모듈식 점진적 구현** — 7개 모듈 × 10세션 단위. 각 세션 종료 시 deployable 산출물 확보. bkit `--scope module-N` 지원.
4. **타입 안전성** — TypeScript strict 모드, OpenAPI 스펙으로부터 프론트엔드 타입 자동 생성.
5. **운영 친화성** — 매주 화 06:00 KST 자동 수집 사이클 + 수집 실패 즉시 가시화 + HITL 비동기 큐.
6. **KAIST CAIO 평가 적합성** — bkit PDCA 워크플로우 표준 산출물 4종 모두 생성, 결정 사슬 추적 가능.

### 1.2 Design Principles

- **Feature-based folder structure** — 도메인별로 코드 응집. `features/<도메인>/{components,hooks,api,types}` 패턴.
- **Server-state vs UI-state 분리** — TanStack Query(서버) + Zustand(UI 전역). React Context는 테마/밀도에만 한정.
- **Composition over inheritance** — 모든 UI는 12개 공유 컴포넌트 + 화면 전용 조합으로 구성.
- **No business logic in components** — 컴포넌트는 prop 받고 렌더, 비즈니스 로직은 hooks(`useForecast`, `useSignals`)에.
- **Fail-soft for collection** — 14신호 중 일부 수집 실패 시 전체 사이클 중단 금지. 신호별 fallback + UI에 명시.
- **HITL as first-class** — 모든 상세 화면 하단에 단일 공유 HITL 컴포넌트. 도메인 지식 지속 반영 가능.

---

## 2. Architecture Options

### 2.0 Architecture Comparison

> bkit 워크플로우 표준: 3가지 옵션 비교 후 Checkpoint 3에서 선택.

| 옵션 | 핵심 | 장점 | 단점 | 적합도 |
|------|------|------|------|--------|
| **Option A — Minimal Changes** | 핸드오프 HTML 프로토타입을 그대로 정적 호스팅 | 최소 노력, 즉시 시연 가능 | 백엔드 연결 불가, mock 데이터만 가능, 실측 데이터 못 씀 | 발표 데모용으로만 |
| **Option B — Clean Architecture** | Enterprise 레벨 + DDD + 마이크로서비스 + 헥사고날 | 확장성·유지보수성 최고, 대규모 팀에 적합 | 3인 팀 7주 일정에 과도, 학습 곡선 가파름 | **부적합** |
| **Option C — Pragmatic Balance** ⭐ | Dynamic 레벨 + Feature-based 모듈 + 단일 FastAPI 서비스 | 핸드오프 권장 스택 그대로 사용, 7주 안에 완성 가능, 향후 리팩토링 여지 확보 | 트래픽 1000 RPS 초과 시 일부 분리 필요 | **선택 ✅** |

**선택 근거 (Checkpoint 3)**: Option C는 핸드오프 권장사항(React+TS+Recharts+Vite+TanStack Query)과 완전 일치. 7주 일정에 안전. KAIST CAIO 과제 평가에 충분한 완성도.

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Browser (User)                                  │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Vercel (Edge Network + Static Assets)                       │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │             Frontend (React 18 + TypeScript + Vite SPA)                │ │
│  │                                                                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────────┐  │ │
│  │  │ Pages        │  │ Modal Stack  │  │ Design System (12 components)│  │ │
│  │  │ (Router 6)   │  │ (Zustand)    │  │ Sig MetricCard LineChart...  │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └───────────────┬─────────────┘  │ │
│  │         │                 │                          │                 │ │
│  │  ┌──────▼─────────────────▼──────────────────────────▼─────────────┐  │ │
│  │  │ TanStack Query (서버 상태 캐시, 5분 TTL)                          │  │ │
│  │  └─────────────────────────────┬─────────────────────────────────────┘ │ │
│  └────────────────────────────────┼────────────────────────────────────────┘ │
└───────────────────────────────────┼──────────────────────────────────────────┘
                                    │ Bearer Token (JWT 1h)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                Render (또는 AWS ECS — Phase 6 결정)                          │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │           Backend (FastAPI + Python 3.11+)                             │ │
│  │                                                                        │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │ │
│  │  │ API Routes │  │ Auth (JWT) │  │ Rate Limit │  │ OpenAPI        │  │ │
│  │  │ (12 GET    │  │            │  │ (slowapi)  │  │ /openapi.yaml  │  │ │
│  │  │  +1 POST)  │  │            │  │            │  │ (자동 생성)     │  │ │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────────────────┘  │ │
│  │        │               │               │                              │ │
│  │  ┌─────▼───────────────▼───────────────▼────────────────────────────┐ │ │
│  │  │             Services Layer                                       │ │ │
│  │  │  ┌───────────────┐  ┌────────────┐  ┌────────────────────────┐  │ │ │
│  │  │  │ ForecastSvc   │  │ SignalSvc  │  │ HITLSvc (rules + retrain│ │ │ │
│  │  │  │ (Prophet/LSTM)│  │ (14 signals│  │  queue + diff response)│  │ │ │
│  │  │  └───────┬───────┘  └─────┬──────┘  └─────────┬──────────────┘  │ │ │
│  │  └──────────┼─────────────────┼──────────────────┼─────────────────┘ │ │
│  │             │                 │                  │                   │ │
│  │  ┌──────────▼─────────────────▼──────────────────▼─────────────────┐ │ │
│  │  │  Pipelines (APScheduler — 매주 화 06:00 KST)                     │ │ │
│  │  │  yfinance + SEC EDGAR + DART + FRED + RSS + News Crawler          │ │ │
│  │  │  → LLM 감성 분석 (Anthropic Claude API)                          │ │ │
│  │  │  → DB 적재                                                        │ │ │
│  │  └────────────────┬──────────────────────────┬───────────────────────┘ │ │
│  └───────────────────┼──────────────────────────┼──────────────────────────┘ │
└──────────────────────┼──────────────────────────┼─────────────────────────────┘
                       ▼                          ▼
            ┌────────────────────┐    ┌────────────────────┐
            │ PostgreSQL +       │    │ Redis              │
            │ TimescaleDB        │    │ (스냅샷 캐시 5분)   │
            │ (시계열·메타)       │    │                    │
            └────────────────────┘    └────────────────────┘
                       ▲
                       │
            ┌──────────┴──────────┐
            │ Neo4j (Graph RAG    │
            │ — 구리↔DRAM 인과)   │
            └─────────────────────┘
```

### 2.2 Data Flow

#### 2.2.1 정기 수집 사이클 (매주 화 06:00 KST)

```
APScheduler trigger
  ↓
Pipeline orchestrator (병렬 7개 + 7개 = 14신호)
  ├─ Group A (정형 7) → yfinance/SEC/DART/FRED API 호출
  │  └─ 파싱 → 정규화 → PostgreSQL INSERT
  ├─ Group B (비정형 7) → RSS/뉴스 사이트 크롤링
  │  └─ Anthropic Claude API (감성 점수 -1.0~1.0) → PostgreSQL INSERT
  │
  ├─ 거시지표 5종 (Fed Rate/DXY/PMI/USDKRW/Copper) → FRED API
  └─ 글로벌 이벤트 → 뉴스 + GDELT 등 → 분류
  ↓
Forecast Service
  ├─ Prophet (1~7주) → 예측값 + 신뢰구간 → PostgreSQL forecast 테이블
  └─ LSTM/Transformer (8~21주) → 동일
  ↓
Graph RAG Update (구리↔DRAM)
  └─ Neo4j 노드/엣지 갱신
  ↓
Redis 캐시 invalidate (5분 후 신규 요청부터 자동 갱신)
  ↓
S-014 데이터 수집 현황 갱신 (success/fail/partial)
```

#### 2.2.2 사용자 조회 플로우 (예: S-001 메인 대시보드 진입)

```
사용자 로그인 (JWT 발급, 1h 만료)
  ↓
GET /api/snapshot (가격 + 예측 + 메타)
GET /api/history (52주 + 21주 예측)        ─┐
GET /api/signals (14신호 현재값)              ├─ 병렬 (TanStack Query)
GET /api/macro (5거시지표)                   │
GET /api/events?limit=3 (hot 이벤트)         │
GET /api/news?limit=3 (hot 뉴스)             │
GET /api/accuracy?limit=3 (최근 정확도)       │
GET /api/collection (수집 현황)              ─┘
  ↓
Backend: Redis 캐시 hit (5분 TTL) → 응답
         Redis 캐시 miss → PostgreSQL 조회 → Redis 저장 → 응답
  ↓
Frontend: 화면 렌더 (S-001)
```

#### 2.2.3 HITL 조정 플로우

```
사용자가 상세 화면 (예: S-003 A-4)에서 임계치 변경
  ↓
"저장 & 재학습" 클릭
  ↓
POST /api/hitl/rules
  Body: {signalId: "A-4", rules: [{id:"alert", value: 95}], comment?}
  ↓
Backend:
  1. PostgreSQL hitl_rules 테이블 UPDATE
  2. Retrain queue에 작업 등록 (비동기, status: "processing")
  3. 즉시 응답: {status: "processing", queueId, eta_seconds}
  ↓
Frontend: "처리 중" UI 표시 + 폴링 (5초 간격)
  ↓
Backend Worker: 모델 재학습 완료 → status: "done" + 신/구 결과
  ↓
Frontend: 신/구 결과 비교 표시 + 관련 쿼리 invalidate
```

### 2.3 Dependencies

#### 2.3.1 외부 데이터 소스

| 신호/지표 | 소스 | 형식 | 무료 한도 | Fallback |
|-----------|------|------|-----------|----------|
| A-1 대만 공급망 | Yahoo Finance (yfinance) | API | 무제한 (적정 사용) | 전주값 유지 |
| A-2 빅테크 CapEx | SEC EDGAR REST | API | 무제한 | 전주값 유지 |
| A-3 국내 재무 | DART OpenAPI | API | 1만/일 | 전주값 유지 |
| A-4 재고지수 | 자체 크롤 + 가공 | HTML | — | Red Alert 유지 |
| A-5~A-7 | FRED + 자체 | API | 12만/월 | 전주값 |
| B-1~B-7 비정형 | RSS + 뉴스 사이트 | RSS/HTML | — | 빈 배열 + 경고 |
| 거시지표 | FRED API | API | 공유 한도 | 전월값 |
| 글로벌 이벤트 | 뉴스 + GDELT | API | 12만/월 | 빈 배열 |

#### 2.3.2 외부 서비스

| 서비스 | 용도 | 비용 |
|--------|------|------|
| Anthropic Claude API (Sonnet) | 뉴스 감성 분석, AI 종합 판단 | 종량제 (예상 월 30만 원) |
| Vercel | 프론트엔드 호스팅 | 무료 (Pro 필요 시 월 $20) |
| Render | 백엔드 호스팅 | 무료 PoC → 운영 $7/월 |
| Sentry | 에러 모니터링 | 무료 (개발자 1인) |

---

## 3. Data Model

### 3.1 Entity Definition

> PRD §17의 TypeScript 타입 정의 + 백엔드 SQLAlchemy 모델 매핑.

#### 3.1.1 PriceHistory (DRAM 가격 시계열)

```python
class PriceHistory(Base):
    __tablename__ = "price_history"
    id: int
    week: int                  # -51~0 (과거) / 1~21 (예측)
    value: Decimal             # USD/GB
    lower: Optional[Decimal]   # 신뢰구간 하단 (예측만)
    upper: Optional[Decimal]
    type: Enum("actual", "forecast_7", "forecast_21")
    model: Optional[str]       # "prophet_v2.1" 등
    confidence: Optional[Decimal]
    created_at: datetime
```

#### 3.1.2 Signal (14개 프록시 신호)

```python
class Signal(Base):
    __tablename__ = "signals"
    id: str                    # "A-1" ~ "A-7", "B-1" ~ "B-7"
    name: str
    group: Enum("A", "B")
    source: str
    description: str

class SignalSnapshot(Base):
    __tablename__ = "signal_snapshots"
    id: int
    signal_id: str  → FK
    week: date
    value: str       # 표시 포맷 (예: "+2.5%")
    num: Decimal     # 정렬/계산용
    tone: Enum("pos", "neu", "neg", "alert")
    spark: JSON      # 28주 sparkline 배열
    collected_at: datetime
```

#### 3.1.3 News

```python
class News(Base):
    __tablename__ = "news"
    id: UUID
    date: date
    title: str
    title_en: Optional[str]
    source: str
    url: str
    score: Decimal              # -1.0~1.0 감성 점수
    tone: Enum("pos", "neu", "neg")
    confidence: Decimal         # 0.0~1.0
    hot: bool
    summary: text               # AI 요약
    effects: JSON               # {short, mid, long}
    linked_signals: JSON        # 신호 ID 배열
```

#### 3.1.4 Macro, Event, Accuracy, Collection

(PRD §17 TypeScript 정의 그대로 SQLAlchemy 변환)

#### 3.1.5 HITL Rule

```python
class HITLRule(Base):
    __tablename__ = "hitl_rules"
    id: int
    signal_id: str → FK
    rule_id: str                # "pos", "neu", "neg"
    label: str
    tone: str
    value: Decimal              # 사용자 조정값
    step: Decimal
    unit: str
    updated_by: int → user
    updated_at: datetime

class RetrainJob(Base):
    __tablename__ = "retrain_jobs"
    id: UUID
    rule_change_id: int
    status: Enum("queued", "processing", "done", "failed")
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    before_result: Optional[JSON]
    after_result: Optional[JSON]
```

### 3.2 Entity Relationships

```
Signal (1) ──< (N) SignalSnapshot      [주별 신호 값]
Signal (1) ──< (N) HITLRule            [신호별 임계치]
HITLRule (1) ──< (N) RetrainJob        [재학습 이력]
News (N) ──< (M) Signal                [N:M, linked_signals JSON]
Event (N) ──< (M) News                 [N:M, linked_news JSON]
PriceHistory ────────────────          [독립]
Macro / MacroHistory                   [독립]
Accuracy → SignalSnapshot              [당시 스냅샷 보존]
```

### 3.3 Database Schema

```sql
-- PostgreSQL + TimescaleDB 확장 (시계열 효율)

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE price_history (
  id BIGSERIAL PRIMARY KEY,
  week INTEGER NOT NULL,
  value NUMERIC(10,2) NOT NULL,
  lower NUMERIC(10,2),
  upper NUMERIC(10,2),
  type VARCHAR(20) NOT NULL,
  model VARCHAR(50),
  confidence NUMERIC(4,3),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('price_history', 'created_at');

CREATE INDEX idx_price_type_week ON price_history(type, week);

CREATE TABLE signals (
  id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  "group" VARCHAR(1) NOT NULL,
  source VARCHAR(100),
  description TEXT
);

CREATE TABLE signal_snapshots (
  id BIGSERIAL PRIMARY KEY,
  signal_id VARCHAR(10) REFERENCES signals(id),
  week DATE NOT NULL,
  value VARCHAR(50),
  num NUMERIC(15,4),
  tone VARCHAR(10) NOT NULL,
  spark JSONB,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('signal_snapshots', 'collected_at');

CREATE INDEX idx_snap_signal_week ON signal_snapshots(signal_id, week DESC);

-- (news, events, macro, accuracy, hitl_rules, retrain_jobs 동일 패턴)
```

---

## 4. API Specification

### 4.1 Endpoint List

| Method | Path | 화면 | 인증 | 캐시 |
|--------|------|------|------|------|
| GET | `/api/snapshot` | S-001 | JWT | 5m |
| GET | `/api/history` | S-001 | JWT | 5m |
| GET | `/api/signals` | S-001 | JWT | 5m |
| GET | `/api/signals/:id` | S-003, S-004 | JWT | 5m |
| GET | `/api/news` | S-006 | JWT | 1m |
| GET | `/api/news/:id` | S-007 | JWT | 5m |
| GET | `/api/macro` | S-001, S-008 | JWT | 5m |
| GET | `/api/macro/:id` | S-008 | JWT | 5m |
| GET | `/api/events` | S-010 | JWT | 1m |
| GET | `/api/events/:id` | S-011 | JWT | 5m |
| GET | `/api/forecast/:horizon` | S-002 | JWT | 5m |
| GET | `/api/accuracy` | S-012 | JWT | 5m |
| GET | `/api/accuracy/:date/:horizon` | S-013 | JWT | 5m |
| GET | `/api/collection` | S-014 | JWT | 5m |
| POST | `/api/hitl/rules` | HITL panel | JWT | — |
| POST | `/api/auth/login` | 로그인 | — | — |
| POST | `/api/auth/refresh` | 토큰 갱신 | Refresh | — |

### 4.2 Detailed Specification

#### `GET /api/snapshot`

```
Query: 없음
Response 200:
{
  "currentPrice": { "value": 3.20, "unit": "/GB", "code": "DDR5 8Gb", "asOf": "2026-05-13T09:00:00+09:00" },
  "forecast7": { "value": 3.65, "change_pct": 14.1, "model": "prophet_v2.1", "confidence": 0.81 },
  "forecast21": { "value": 4.10, "change_pct": 28.1, "model": "lstm_v1.0", "confidence": 0.74 },
  "updatedAt": "2026-05-13T06:00:00+09:00"
}
```

#### `GET /api/forecast/:horizon`

```
Path: horizon = 7 | 21
Response 200:
{
  "horizon": 7,
  "createdAt": "2026-05-13T06:00:00+09:00",
  "model": "prophet_v2.1",
  "confidence": 0.81,
  "valueRange": { "value": 3.65, "lower": 3.40, "upper": 3.90 },
  "contributions": [
    { "rank": 1, "code": "A-2", "label": "빅테크 CapEx 급증", "pct": 28, "tone": "pos" },
    { "rank": 2, "code": "B-1", "label": "Earnings Call 긍정", "pct": 22, "tone": "pos" }
    // ... 14개
  ],
  "weeklyTable": [
    { "week": 1, "value": 3.28, "lower": 3.20, "upper": 3.36 }
    // ... 7주
  ],
  "aiSummary": "1~7주 단기 예측..."
}
```

#### `POST /api/hitl/rules`

```
Body:
{
  "signalId": "A-4",
  "rules": [
    { "id": "alert", "value": 95 }
  ],
  "comment": "재고지수 임계치 보수적으로 조정"
}

Response 202 (Accepted):
{
  "status": "processing",
  "queueId": "rj_01HXYZ...",
  "etaSeconds": 30,
  "pollUrl": "/api/hitl/jobs/rj_01HXYZ"
}

Response 200 (when done — via polling):
{
  "status": "done",
  "beforeResult": {...},
  "afterResult": {...},
  "diff": "..."
}
```

#### 공통 응답 규약

```
HTTP 200 OK          정상
HTTP 202 Accepted    비동기 작업 등록 (HITL retrain)
HTTP 400 Bad Request {error, message, fieldErrors}
HTTP 401 Unauthorized JWT 없음/만료
HTTP 403 Forbidden   권한 없음
HTTP 404 Not Found
HTTP 429 Too Many    Rate limit 초과
HTTP 503 Service Unavailable 수집 사이클 진행 중

에러 응답 본문:
{ "error": "RESOURCE_NOT_FOUND", "message": "신호 ID 'A-99'을 찾을 수 없습니다.", "trace_id": "uuid" }
```

---

## 5. UI/UX Design

### 5.1 Screen Layout

> PRD §07 + 핸드오프 README가 SSOT. 본 섹션은 라우팅·모달 스택 규약만.

#### 5.1.1 라우팅 맵

```
/                       → S-001 메인 대시보드 (default route)
/news                   → S-006 뉴스 전체 목록
/news/:id               → S-007 뉴스 상세 (또는 query param 모달)
/macro                  → S-008 거시경제 5탭
/macro/:id              → S-008 특정 탭 활성화
/events                 → S-010 이벤트 전체 목록
/events/:id             → S-011 이벤트 상세 (모달)
/accuracy               → S-012 정확도 이력
/collection             → S-014 수집 현황
/login                  → 로그인 (Auth)

모달은 query param으로 직렬화:
  ?modal=S-002&horizon=7
  ?modal=S-003&tab=A-4
  ?modal=S-005
  ?modal=S-009&week=2026-05-20
  ?modal=S-013&date=2026-04-15&horizon=7
```

#### 5.1.2 모달 스택 규약

- 모달 위에 모달 가능 (예: S-011 → 연결뉴스 클릭 → S-007)
- Zustand `modalStack: Array<{id, params}>` 로 관리
- ESC/바깥클릭은 최상위 모달만 닫음
- 모든 모달 닫혔을 때만 body scroll 해제
- 모달 스택 깊이 ≤ 3 (UX 안정성)

### 5.2 User Flow

PRD §06 8단계 Happy Path 참조. 핵심:

```
Login → S-001 → (가격 카드 클릭) → S-002 → HITL 조정 → 저장 → 결과 확인 → 닫기
                ↘ (신호 카드 클릭) → S-003/S-004 → 28주 트렌드 → 닫기
                ↘ (차트 점 클릭) → S-009 → 닫기
                ↘ (뉴스 더보기) → S-006 → 기사 클릭 → S-007 → 닫기
```

### 5.3 Component List

> PRD §14 컴포넌트 인벤토리 참조.

**공유 (12)**: Sig, Sparkline, MetricCard, LineChart, Modal, Tabs, Seg, HITL, AiNote, BarRow, FilterSelect, SectionHead

**화면 전용**:
- Dashboard 영역: DramChart, ChartRangeSeg, SignalCard, GraphRagMini
- 모달별: S002~S013 각각 컴포넌트
- 페이지별: S006, S008, S010, S012, S014 각각

### 5.4 Page UI Checklist

> bkit gap-detector가 Phase 4(check)에서 자동 검증. 각 페이지가 만족해야 할 조건.

#### S-001 메인 대시보드

- [ ] Topbar 56px 고정 + 브랜드 + 자동수집 상태 + 마지막 갱신 + 테마 토글
- [ ] 가격 카드 3개 (현재/1-7w/8-21w) — 카드 클릭 시 S-002 모달
- [ ] DRAM 52주 차트 + 21주 예측 + 신뢰구간 밴드 + 범위 필터 3 모드
- [ ] 14신호 카드 (Group A·B 각 7개) — 카드 클릭 시 S-003/S-004 모달
- [ ] A-4 신호값 > 100 시 펄싱 알림
- [ ] Graph RAG 카드 (구리·DRAM 미니 차트 + 상관계수 + AI 코멘트) — 클릭 시 S-005
- [ ] 뉴스/거시 2열 (각 5개 미리보기) — 클릭 시 S-007/S-008
- [ ] 이벤트/정확도 2열 (각 3개) — 클릭 시 S-011/S-013
- [ ] 수집 현황 푸터바 (정형/비정형/실패/사이클/다음 수집)
- [ ] 라이트/다크 토글 즉시 반영 + localStorage 저장
- [ ] 편안/컴팩트 토글 즉시 반영
- [ ] 모든 한글 텍스트 `word-break: keep-all` 적용

#### S-002 AI 예측 근거 모달

- [ ] 1-7w / 8-21w 2탭 + 활성 탭 밑줄
- [ ] 예측값 + 신뢰구간 + 모델 정보
- [ ] 신호 기여도 바차트 (14개, 순위순)
- [ ] 주별 예측 테이블 (7주 또는 21주)
- [ ] AI 종합 판단 (AiNote 컴포넌트)
- [ ] 하단 HITL 패널 고정
- [ ] ESC/바깥클릭으로 닫힘

#### S-003 정형 Group A 상세 / S-004 비정형 Group B 상세

- [ ] 7탭 (A-1~A-7 / B-1~B-7) + 활성 탭 강조
- [ ] 각 탭: 트렌드 차트 (A: 28주 / B: 8주 감성)
- [ ] 원본 데이터 테이블
- [ ] AI 해석 (AiNote)
- [ ] 하단 HITL 패널
- [ ] A-4 탭 활성 시 Red Alert 배너 (값 > 100)

#### S-005 Graph RAG

- [ ] 52주 구리 vs DRAM 오버레이 차트
- [ ] 리드타임 상관계수 막대 (-10주 ~ +10주)
- [ ] 인과관계 다이어그램 (PCB → 패키징 → DC 투자)
- [ ] AI 코멘트 (AiNote)

#### S-006 뉴스 전체 / S-010 이벤트 전체

- [ ] 필터 칩 (감성/위험도)
- [ ] 정렬 드롭다운 (영향도/신뢰/날짜)
- [ ] 출처 필터
- [ ] 결과 카운트 표시 (`N건 표시`)
- [ ] 페이지네이션 (또는 무한 스크롤)
- [ ] 행 클릭 → 상세 모달

#### S-007 뉴스 상세 / S-011 이벤트 상세

- [ ] AI 요약
- [ ] 단/중/장기 영향 (3구간)
- [ ] 연결 신호/뉴스 칩
- [ ] 원문 링크 (새 탭)
- [ ] 하단 HITL 패널 (S-007)

#### S-008 거시경제 통합

- [ ] 5탭 (Fed Rate / DXY / PMI / USDKRW / Copper)
- [ ] 각 탭: 52주 트렌드 + 월간 원본 + DRAM 상관 노트
- [ ] 탭 활성 시 URL 동기화 (`?tab=fed`)

#### S-009 주별 신호 스냅샷

- [ ] 과거주: 당시 14신호 vs 현재 + 오차 분석
- [ ] 미래주: 예측 분해도 (어떤 신호가 어떻게 기여하는지)

#### S-012 정확도 이력 / S-013 당시 vs 현재 비교

- [ ] MAPE 추이 라인차트 (S-012)
- [ ] 정확도 이력 테이블 + 필터 (7w/21w/all)
- [ ] 행 클릭 → S-013
- [ ] 14신호 사이드바이사이드 비교 (S-013)
- [ ] 오차 원인 AI 분석 (AiNote)

#### S-014 데이터 수집 현황

- [ ] 14신호 + 거시 + 이벤트별 행
- [ ] 출처, 마지막 수집 시각, 신규 항목 수, 주간 증감
- [ ] success/fail/partial 상태 배지
- [ ] 실패 시 원인 표시

---

## 6. Error Handling

### 6.1 Error Code Definition

| Code | HTTP | 의미 | 사용자 메시지 |
|------|------|------|---------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 로그인 실패 | "ID 또는 비밀번호가 올바르지 않습니다." |
| `AUTH_TOKEN_EXPIRED` | 401 | JWT 만료 | "세션이 만료되었습니다. 다시 로그인해주세요." |
| `AUTH_INSUFFICIENT_PERM` | 403 | 권한 부족 | "이 작업에 필요한 권한이 없습니다." |
| `RESOURCE_NOT_FOUND` | 404 | 리소스 없음 | "요청한 항목을 찾을 수 없습니다." |
| `VALIDATION_FAILED` | 400 | 입력 검증 실패 | (필드별 상세 메시지) |
| `RATE_LIMIT_EXCEEDED` | 429 | API 호출 한도 초과 | "잠시 후 다시 시도해주세요." |
| `COLLECTION_IN_PROGRESS` | 503 | 수집 사이클 진행 중 | "데이터 갱신 중입니다 (약 N분 후 완료)." |
| `EXTERNAL_API_DOWN` | 503 | 외부 API 장애 | "외부 데이터 소스 일시 장애. 이전 주 데이터를 표시합니다." |
| `HITL_RETRAIN_FAILED` | 500 | 재학습 실패 | "재학습 처리 중 오류가 발생했습니다. 관리자에게 문의하세요." |
| `INTERNAL_SERVER_ERROR` | 500 | 일반 서버 오류 | "오류가 발생했습니다. trace_id: XXX" |

### 6.2 Error Response Format

```typescript
// 표준 에러 응답
type ErrorResponse = {
  error: string;          // 위 Code 중 하나
  message: string;        // 사용자 표시용 한국어
  fieldErrors?: {         // VALIDATION_FAILED 시
    [field: string]: string;
  };
  trace_id: string;       // Sentry/로그 추적용 UUID
  retryAfter?: number;    // 429/503 시 권장 대기 초
};
```

**프론트엔드 처리**:
- 401 → 로그인 페이지 리다이렉트 (자동 refresh 1회 시도 후)
- 429/503 → 지수 백오프 재시도 (1s → 2s → 4s, 최대 3회)
- 400 → 사용자에게 필드별 메시지 표시
- 500 → 에러 바운더리 + Sentry 전송 + trace_id 표시

---

## 7. Security Considerations

### 7.1 인증·인가

- JWT 액세스 토큰: 1시간 만료, HS256 서명, `JWT_SECRET` 환경변수
- Refresh 토큰: 7일 만료, httpOnly + Secure 쿠키
- 5명 임원 + 3명 개발자, 역할: viewer / analyst(HITL 가능) / admin
- HITL 변경은 `analyst` 이상 권한 필수

### 7.2 데이터 보호

- HTTPS 강제 (HSTS 1년)
- 응답에 민감정보 미포함 (사용자 정보는 `me` 엔드포인트로 분리)
- 외부 API 키는 서버 환경변수만 (클라이언트 노출 금지)
- 데이터베이스 백업 일 1회, 7일 보존, 암호화

### 7.3 OWASP Top 10 대응

- **A01 Broken Access Control**: 모든 보호 엔드포인트에 JWT 가드
- **A02 Cryptographic Failures**: bcrypt(cost=12) 패스워드 해시, JWT_SECRET 32 bytes 이상
- **A03 Injection**: SQLAlchemy ORM 사용 (raw SQL 금지), Pydantic 검증
- **A05 Security Misconfiguration**: 운영에서 CORS 화이트리스트, 디버그 모드 비활성
- **A07 Identification & Auth**: 로그인 5회 실패 시 15분 잠금
- **A09 Logging & Monitoring**: Sentry + 인증·HITL 변경 감사 로그

### 7.4 Rate Limiting

- 로그인: IP별 5회 / 15분
- 일반 GET API: 사용자별 1000회 / 시간
- HITL POST: 사용자별 30회 / 시간

---

## 8. Test Plan

### 8.1 Test Scope

- **L1 API 테스트**: 모든 12 GET + 1 POST 엔드포인트, 200/401/404/400 케이스
- **L2 UI Action 테스트**: 카드/버튼/탭/필터/모달 인터랙션
- **L3 E2E 시나리오**: PRD §06 8단계 Happy Path 전체 + HITL 저장 플로우
- **L4 성능 (Enterprise)**: Lighthouse Performance ≥ 90, LCP < 2.5s — Phase 6
- **L5 보안 (Enterprise)**: OWASP ZAP 자동 스캔, npm audit — Phase 6

### 8.2 L1 API Test Scenarios

```bash
# 인증 없이 호출 → 401
curl -i http://localhost:8000/api/snapshot
# Expected: 401 Unauthorized, {error: "AUTH_TOKEN_EXPIRED" 또는 AUTH_INVALID_CREDENTIALS}

# 로그인 후 호출 → 200
TOKEN=$(curl -s -X POST .../api/auth/login -d '{"email":"...","password":"..."}' | jq -r .accessToken)
curl -i -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/snapshot
# Expected: 200 OK, JSON with currentPrice/forecast7/forecast21/updatedAt

# 존재하지 않는 신호 → 404
curl -i -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/signals/A-99
# Expected: 404, {error: "RESOURCE_NOT_FOUND"}

# HITL 잘못된 입력 → 400
curl -i -H "Authorization: Bearer $TOKEN" -X POST .../api/hitl/rules -d '{"invalid":"data"}'
# Expected: 400, {error: "VALIDATION_FAILED", fieldErrors: {...}}

# Rate Limit 초과 → 429
for i in {1..40}; do curl -X POST .../api/hitl/rules ... ; done
# Expected: 41번째 응답 429, {error: "RATE_LIMIT_EXCEEDED", retryAfter: 60}
```

### 8.3 L2 UI Action Test Scenarios

```typescript
// frontend/tests/e2e/dashboard-actions.spec.ts (Playwright)

test('S-001: 가격 카드 클릭 시 S-002 모달 열림', async ({ page }) => {
  await page.goto('/');
  await page.locator('[data-screen="S-001"] [data-card="forecast7"]').click();
  await expect(page.locator('[data-modal="S-002"]')).toBeVisible();
  await expect(page).toHaveURL(/modal=S-002/);
});

test('S-001: 차트 범위 필터 클릭 시 시각 전환', async ({ page }) => {
  await page.goto('/');
  await page.locator('[data-seg="range"] >> text=중장기').click();
  await expect(page.locator('[data-chart="dram"] .forecast-21w')).toBeVisible();
  await expect(page.locator('.forecast-21w')).toHaveCSS('stroke-width', '2.6');
});

test('S-002: ESC 키로 모달 닫힘', async ({ page }) => {
  await page.goto('/?modal=S-002&horizon=7');
  await page.keyboard.press('Escape');
  await expect(page.locator('[data-modal="S-002"]')).not.toBeVisible();
});

test('HITL: 임계치 변경 후 저장 → 응답 표시', async ({ page }) => {
  await page.goto('/?modal=S-003&tab=A-4');
  await page.fill('[data-hitl-input="alert"]', '95');
  await page.locator('text=저장 & 재학습').click();
  await expect(page.locator('[data-hitl-status]')).toContainText('처리 중');
  await page.waitForResponse(/\/api\/hitl\/rules/);
  await expect(page.locator('[data-hitl-diff]')).toBeVisible({ timeout: 30000 });
});
```

### 8.4 L3 E2E Scenario Test Scenarios

```typescript
// PRD §06 Happy Path 전체

test('Persona B 이병헌 구매팀장: A-4 Red Alert 감지 → 드릴다운 → HITL 조정', async ({ page }) => {
  await page.goto('/login');
  await login(page, 'lee@example.com');
  await expect(page).toHaveURL('/');
  // S-001 진입
  await expect(page.locator('[data-screen="S-001"]')).toBeVisible();
  // A-4 신호 Red Alert 확인
  const a4Card = page.locator('[data-signal="A-4"]');
  await expect(a4Card.locator('.sig.alert')).toBeVisible();
  // 클릭 → S-003 A-4 탭
  await a4Card.click();
  await expect(page.locator('[data-modal="S-003"][data-active-tab="A-4"]')).toBeVisible();
  // Red Alert 배너 확인
  await expect(page.locator('[data-banner="red-alert"]')).toBeVisible();
  // HITL 패널에서 임계치 조정
  await page.fill('[data-hitl-input="alert"]', '95');
  await page.locator('text=저장 & 재학습').click();
  // 응답 대기 + 결과 확인
  await page.waitForSelector('[data-hitl-diff]', { timeout: 30000 });
  // S-014로 이동하여 수집 현황 확인
  await page.locator('text=수집 현황').click();
  await expect(page).toHaveURL('/collection');
});
```

### 8.5 Seed Data Requirements

- **L1/L2 테스트용**: 14신호 × 4주 + 가격 52주 + 뉴스 30건 + 이벤트 10건 + 사용자 3명 (viewer/analyst/admin)
- **L3 테스트용**: 추가로 A-4 신호값 105 (Red Alert 트리거)
- **위치**: `backend/tests/fixtures/seed.sql`
- **CI 실행 전**: `make seed-test-db`

---

## 9. Clean Architecture

### 9.1 Layer Structure

```
Frontend (React SPA — Feature-based, not strict layers):

┌─────────────────────────────────────────────────────┐
│ Pages (Route Handlers)                              │
│  - 라우터 정의, 페이지 컴포넌트 마운트                 │
├─────────────────────────────────────────────────────┤
│ Features (도메인별 모듈)                              │
│  - dashboard/, forecast/, signals/, news/ ...        │
│  - 각각 components/, hooks/, api/, types/             │
├─────────────────────────────────────────────────────┤
│ Design System (공유 UI)                              │
│  - 12 컴포넌트, 디자인 토큰만 의존                     │
├─────────────────────────────────────────────────────┤
│ Services (API client, TanStack Query 설정)           │
│  - openapi-typescript 자동 생성 타입 사용              │
├─────────────────────────────────────────────────────┤
│ Store (Zustand)                                     │
│  - 전역 UI 상태만 (theme, density, modalStack, auth)  │
├─────────────────────────────────────────────────────┤
│ Styles (디자인 토큰 + globals)                        │
└─────────────────────────────────────────────────────┘


Backend (FastAPI — 4 Layer):

┌─────────────────────────────────────────────────────┐
│ Presentation (api/)                                 │
│  - FastAPI 라우터, Pydantic 스키마                   │
├─────────────────────────────────────────────────────┤
│ Application (services/)                             │
│  - 비즈니스 로직, 외부 서비스 호출                     │
├─────────────────────────────────────────────────────┤
│ Domain (models/)                                    │
│  - SQLAlchemy 엔티티, 도메인 규칙                     │
├─────────────────────────────────────────────────────┤
│ Infrastructure (pipelines/, db/, cache/)            │
│  - APScheduler, PostgreSQL, Redis, 외부 API 클라이언트│
└─────────────────────────────────────────────────────┘
```

### 9.2 Dependency Rules

**Frontend**:
- `pages` → `features` → `services`/`store`/`design-system`
- `features/<도메인>`는 다른 `features/<도메인>`를 직접 import 금지
- `design-system`은 어디서든 import 가능 (외부 의존)
- `styles`는 import 트리에 등장 안 함 (CSS만)

**Backend**:
- `api` → `services` → `models` (한 방향)
- `models`는 다른 레이어 import 금지
- `pipelines`는 `services`까지만 의존

### 9.3 File Import Rules

```typescript
// ESLint import/order + import/no-restricted-paths

// 좋은 예
import { useQuery } from '@tanstack/react-query';        // external
import { Sig, MetricCard } from '@/design-system';       // internal absolute
import { useForecast } from './hooks/useForecast';       // relative

// 나쁜 예
import { NewsCard } from '@/features/news/components/NewsCard';  // ❌ 도메인 침범
```

### 9.4 This Feature's Layer Assignment

| 컴포넌트/파일 | 레이어 | 위치 |
|--------------|--------|------|
| 14개 화면 컴포넌트 | Features | `frontend/src/features/<도메인>/` |
| 12개 공유 컴포넌트 | Design System | `frontend/src/design-system/` |
| API 클라이언트 | Services | `frontend/src/services/api/` |
| 전역 상태 (theme, modalStack) | Store | `frontend/src/store/` |
| 14신호 수집 로직 | Backend Application | `backend/app/services/collectors/` |
| 예측 모델 | Backend Application | `backend/app/services/forecast/` |
| HITL 재학습 큐 | Backend Infrastructure | `backend/app/pipelines/hitl_worker.py` |

---

## 10. Coding Convention Reference

### 10.1 Naming Conventions

| 영역 | 규칙 | 예시 |
|------|------|------|
| 컴포넌트 | PascalCase | `MetricCard`, `LineChart` |
| 파일명 | 컴포넌트는 PascalCase, 그 외 kebab-case | `MetricCard.tsx`, `use-forecast.ts` |
| 함수 | camelCase | `getCurrentPrice()` |
| 훅 | `use` 접두 + camelCase | `useForecast()` |
| 상수 | UPPER_SNAKE | `MAX_MODAL_DEPTH` |
| 타입 | PascalCase | `type ForecastHorizon = 7 \| 21` |
| CSS 클래스 (CSS Module) | camelCase | `styles.sig`, `styles.dotPos` |
| API 엔드포인트 | kebab-case | `/api/hitl/rules` |
| DB 테이블 | snake_case | `signal_snapshots` |

### 10.2 Import Order

```typescript
// 1. External
import { useQuery } from '@tanstack/react-query';

// 2. Internal absolute (별칭 @/)
import { Sig } from '@/design-system';
import { useAuthStore } from '@/store/auth';

// 3. Relative (같은 도메인)
import { ForecastCard } from './components/ForecastCard';

// 4. Types (마지막)
import type { Forecast } from '@/types/api';

// 5. Styles (가장 마지막)
import styles from './Dashboard.module.css';
```

### 10.3 Environment Variables

| 변수 | 범위 | 예시 |
|------|------|------|
| `VITE_*` | 클라이언트 노출 가능 | `VITE_API_URL`, `VITE_USE_MOCK` |
| 그 외 | 서버 전용 | `DATABASE_URL`, `ANTHROPIC_API_KEY` |

**금지**: 시크릿을 `VITE_*` 접두로 만들지 말 것.

### 10.4 This Feature's Conventions

- **한글 처리**: 본문 컨테이너 `word-break: keep-all` 필수. 숫자는 `.num` 클래스.
- **AI 출력 표시**: `<AiNote>` 컴포넌트 사용, 라벨 "AI 종합 판단 · Claude 자동 생성".
- **에러 바운더리**: 화면 단위로 ErrorBoundary 감싸기. trace_id 표시 의무.
- **데이터 fetch**: 모든 서버 데이터는 TanStack Query 거치기. 직접 fetch 금지.
- **모달**: `useModalStack().open('S-002', {horizon: 7})` 패턴. URL은 자동 동기화.

---

## 11. Implementation Guide

### 11.1 File Structure

```
Sixsense/
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── .storybook/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── styles/
│       │   ├── tokens.css        # 디자인 토큰 (CSS 변수)
│       │   └── globals.css       # body 리셋, word-break, .num
│       ├── design-system/        # 12 공유 컴포넌트
│       │   ├── Sig/
│       │   ├── Sparkline/
│       │   ├── MetricCard/
│       │   ├── LineChart/
│       │   ├── Modal/
│       │   ├── Tabs/
│       │   ├── Seg/
│       │   ├── HITL/
│       │   ├── AiNote/
│       │   ├── BarRow/
│       │   ├── FilterSelect/
│       │   └── SectionHead/
│       ├── features/             # 도메인별
│       │   ├── dashboard/        # S-001
│       │   ├── forecast/         # S-002, S-009
│       │   ├── signals/          # S-003, S-004
│       │   ├── graph-rag/        # S-005
│       │   ├── news/             # S-006, S-007
│       │   ├── macro/            # S-008
│       │   ├── events/           # S-010, S-011
│       │   ├── accuracy/         # S-012, S-013
│       │   └── collection/       # S-014
│       ├── pages/                # 라우트 정의
│       ├── services/             # API 클라이언트, TanStack Query
│       ├── store/                # Zustand (theme, density, modalStack, auth)
│       ├── types/                # openapi-typescript 자동 생성
│       └── mocks/                # Phase 5 이전 mock 데이터
│
├── backend/
│   ├── pyproject.toml
│   ├── openapi.yaml             # 자동 생성 (FastAPI)
│   └── app/
│       ├── main.py              # FastAPI app
│       ├── api/                 # 라우터
│       │   ├── snapshot.py
│       │   ├── history.py
│       │   ├── signals.py
│       │   ├── news.py
│       │   ├── macro.py
│       │   ├── events.py
│       │   ├── forecast.py
│       │   ├── accuracy.py
│       │   ├── collection.py
│       │   ├── hitl.py
│       │   └── auth.py
│       ├── services/            # 비즈니스 로직
│       │   ├── forecast/
│       │   ├── signals/
│       │   ├── hitl/
│       │   └── collectors/      # 14신호 수집기
│       ├── models/              # SQLAlchemy
│       ├── pipelines/           # APScheduler 작업
│       └── tests/
│
├── docs/                        # PDCA 산출물
│   ├── 00-pm/sixsense.prd.md
│   ├── 01-plan/features/sixsense.plan.md
│   ├── 02-design/features/sixsense.design.md  ← 본 파일
│   └── 03-do/features/sixsense.do.md
│
└── design_handoff_sixsense_dram_dashboard/   # 시각 디자인 SSOT (참조 전용)
```

### 11.2 Implementation Order

총 7주, Phase 0 ~ Phase 6:

| Phase | 기간 | 모듈 | 산출물 |
|-------|------|------|--------|
| Phase 0 | 1주차 | module-0-foundation | 프로젝트 셋업 + 디자인 토큰 + 12 공유 컴포넌트 |
| Phase 1 | 2주차 | module-1-dashboard | S-001 메인 + 라우팅 + mock 데이터 |
| Phase 2 | 3주차 | module-2-modals | S-002, S-003, S-004, S-005, S-009 |
| Phase 3 | 4주차 | module-3-pages | S-006, S-007, S-008, S-010, S-011 |
| Phase 4 | 5주차 | module-4-accuracy-hitl | S-012, S-013, S-014 + HITL API |
| Phase 5 | 6주차 | module-5-pipeline | 백엔드 수집 파이프라인 + 실제 API 전환 |
| Phase 6 | 7주차 | module-6-validation | UAT + KPI + L4/L5 테스트 + 발표 |

### 11.3 Session Guide

#### Module Map

| Module Key | 범위 | 의존 모듈 | 예상 세션 |
|------------|------|-----------|-----------|
| `module-0-foundation` | 프로젝트 셋업 + 디자인 토큰 + 공유 컴포넌트 12종 | — | 1 |
| `module-1-dashboard` | S-001 메인 대시보드 (라우팅·테마·밀도 토글) | module-0 | 1 |
| `module-2-modals` | S-002, S-003, S-004, S-005, S-009 (드릴다운 모달 5종) | module-1 | 2 |
| `module-3-pages` | S-006, S-007, S-008, S-010, S-011 | module-1 | 2 |
| `module-4-accuracy-hitl` | S-012, S-013, S-014 + HITL `POST /api/hitl/rules` | module-2, module-3 | 1 |
| `module-5-pipeline` | 백엔드 데이터 수집 파이프라인 | module-4 | 2 |
| `module-6-validation` | KPI 측정 + UAT + 발표 자료 | module-5 | 1 |

**총 10 세션**

#### Recommended Session Plan

```
Phase 0  → /pdca do sixsense --scope module-0-foundation
Phase 1  → /pdca do sixsense --scope module-1-dashboard
Phase 2  → /pdca do sixsense --scope module-2-modals       (2 세션)
Phase 3  → /pdca do sixsense --scope module-3-pages        (2 세션)
Phase 4  → /pdca do sixsense --scope module-4-accuracy-hitl
Phase 5  → /pdca do sixsense --scope module-5-pipeline     (2 세션)
Phase 6  → /pdca do sixsense --scope module-6-validation
           /pdca analyze sixsense                          (Check 단계)
           /pdca qa sixsense                                (QA 단계)
           /pdca report sixsense                            (Report 단계)
           /pdca archive sixsense                           (Archive)
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-05-16 | 얇은 포인터 버전 (PRD 참조) | 김영석 |
| 0.2 | 2026-05-17 | bkit 표준 11개 섹션 모두 충실히 작성 — Architecture, Data Model, API Spec, UI/UX, Error Handling, Security, Test Plan, Clean Architecture, Coding Convention, Implementation Guide | 김영석 |
