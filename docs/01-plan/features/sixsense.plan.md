# sixsense Planning Document

> **Summary**: 14가지 프록시 신호와 글로벌 이벤트를 100% AI로 자동 수집·분석하여 서버용 DRAM 가격을 주간 단위(단기 1~7주 / 중장기 8~21주)로 예측·시각화하는 웹 대시보드.
>
> **Project**: Server DRAM Price 식스센스 (KAIST CAIO 10기 6조)
> **Version**: 0.1
> **Author**: 김영석 (Dataiku Korea, 프로젝트 리드)
> **Date**: 2026-05-16
> **Status**: Draft

---

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Problem** | 전 세계에 흩어진 정형/비정형 데이터를 사람이 수동 수집·분석하여 매주 회의로 의사결정 → 시장 급변에 늦고 연간 수천억 원 손실 위험 |
| **Solution** | 14개 프록시 신호 + 거시지표 + 글로벌 이벤트를 100% AI로 자동 수집·예측하고, 14화면(S-001~S-014) 대시보드 + HITL 임계치 조정으로 비전문가도 5분 내 판단 |
| **Function/UX Effect** | 매주 화 06:00 KST 자동 갱신, 한 화면에서 단기/중장기 예측·신뢰구간·신호 기여도·뉴스/이벤트 영향·정확도 이력 + 라이트/다크·편안/컴팩트 토글 |
| **Core Value** | 의사결정 사이클 단축(주 1회 회의 → 매일 실시간 모니터링), 예측 정확도 추적 가능, HITL로 도메인 전문가 지식 지속 반영 |

---

## Context Anchor

> Auto-generated from Executive Summary. Propagated to Design/Do documents for context continuity.

| Key | Value |
|-----|-------|
| **WHY** | 반도체 가격 예측을 위한 데이터 수집·분석에 사람·시간·비용이 과다 투입되고 시장 급변에 대응 못함 |
| **WHO** | 반도체 영업전략/구매/마케팅/시장분석/금융투자 부서의 50대 임원 5명 (정우성/이병헌/장동건/이정재/조인성) |
| **RISK** | (1) 14신호 수집 실패 시 예측 정확도 급락 (2) HITL 재학습 응답 지연 (3) 디자인 핸드오프 SVG 차트의 Recharts 마이그레이션 시 신뢰구간 밴드 재현 |
| **SUCCESS** | KPI: 업무시간 절감률 ≥70%, 예측 정확도(MAPE) ≥80%, 사용자 수정률 ≤10%, API p95 ≤60ms |
| **SCOPE** | Phase 0 디자인 시스템 → Phase 1 S-001 → Phase 2 드릴다운 모달 → Phase 3 분석 페이지 → Phase 4 정확도+HITL → Phase 5 실측 통합 → Phase 6 검증 (총 7주) |

---

## 1. Overview

### 1.1 Purpose

서버용 DDR5 DRAM 반도체의 주간 가격 변동을 단기(1~7주)와 중장기(8~21주)로 자동 예측하고, 예측 근거가 되는 14개 프록시 신호·뉴스·글로벌 이벤트·거시지표를 한 화면에서 분석할 수 있는 B2B 인텔리전스 대시보드를 구축한다.

### 1.2 Background

- **시장 환경**: 서버용 DRAM은 HBM·DDR5 수요 폭증과 빅테크 CapEx 사이클에 민감하여 주간 단위 가격 변동성이 크다.
- **현재 의사결정 한계**: 영업·구매·투자 부서가 각자 정보를 수집·해석하며 주 1회 회의로 통합 → 정보 비대칭과 시차 발생.
- **AI 기반 자동화 기회**: 무료 공개 데이터 + LLM 기반 텍스트 분석 + 시계열 예측 모델 조합으로 100% 자동화 가능.
- **KAIST CAIO 과제 맥락**: 본 프로젝트는 KAIST CAIO 10기 6조의 졸업 산출물로, bkit PDCA 워크플로우로 진행한다.

### 1.3 Related Documents

- PRD: `docs/00-pm/sixsense.prd.md` (자동 참조 — Plan/Design/Do 전 과정 컨텍스트 제공)
- Design Hand-off: `design_handoff_sixsense_dram_dashboard/` (14개 화면 hifi 프로토타입, Claude Design 산출물)
- 백업: `prd.md.bak` (보강 전 원본 PRD 마크다운)

---

## 2. Scope

### 2.1 In Scope

- [ ] 14개 프록시 신호 자동 수집 파이프라인 (Group A 정형 7 + Group B 비정형 7)
- [ ] 매주 화 06:00 KST 배치 스케줄러
- [ ] DRAM 가격 단기/중장기 예측 모델 (Prophet + LSTM/Transformer)
- [ ] 14개 화면 (S-001 메인 + 6개 풀페이지 + 7개 모달) 구현
- [ ] 디자인 핸드오프의 디자인 토큰·공유 컴포넌트 12종 픽셀 단위 재현
- [ ] 12개 GET API + 1개 POST API (HITL)
- [ ] HITL(Human-In-The-Loop) 임계치/가중치 조정 기능
- [ ] Graph RAG (구리↔DRAM 상관관계) 시각화
- [ ] 라이트/다크 테마 + 편안/컴팩트 밀도 토글
- [ ] 모달 스택 + URL 딥링킹

### 2.2 Out of Scope

- 전통적 시계열 분석 기법(ARIMA, GARCH 등) — PRD §05 P2에서 명시적 제외
- 유료 데이터 소스(Bloomberg, Refinitiv 등) — PRD §05 P2 명시적 제외
- 모바일 네이티브 앱 — 웹 우선
- 다국어 (한국어만 지원 — 폰트 스택도 Pretendard 기반)
- 사용자 권한 관리/조직별 신호 접근 제어 — 디자인 핸드오프에 없음
- 데이터 내보내기 (CSV/PDF) — 디자인 핸드오프에 없음

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | 14개 프록시 신호 자동 수집 (매주 화 06:00 KST) | High | Pending |
| FR-02 | DRAM 가격 52주 히스토리 + 21주 예측 시각화 (신뢰구간 포함) | High | Pending |
| FR-03 | S-001 메인 대시보드: 가격 카드 3 + 차트 + 14신호 + Graph RAG + 뉴스/거시 + 이벤트/정확도 + 수집현황 | High | Pending |
| FR-04 | S-002~S-005 드릴다운 모달 (예측 근거, 신호 상세, Graph RAG 상세, 주별 스냅샷) | High | Pending |
| FR-05 | S-006~S-008 분석 페이지 (뉴스 목록, 뉴스 상세, 거시경제 통합 5탭) | High | Pending |
| FR-06 | S-010~S-014 이벤트/정확도/수집현황 페이지 | High | Pending |
| FR-07 | HITL 임계치 조정 패널 (모든 상세 화면 하단) + `POST /api/hitl/rules` | High | Pending |
| FR-08 | 차트 범위 필터 (short/mid/all) 3 모드 |  High | Pending |
| FR-09 | 모달 스택 + ESC/바깥클릭 닫기 + URL 딥링킹 | Medium | Pending |
| FR-10 | 라이트/다크 + 편안/컴팩트 4조합 즉시 토글 + localStorage 영속화 | Medium | Pending |
| FR-11 | A-4 재고지수 > 100 시 Red Alert 펄싱 애니메이션 | Medium | Pending |
| FR-12 | Graph RAG 구리↔DRAM 인과관계 (52주 오버레이 + 리드타임 상관계수) | Medium | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| Performance (API) | p95 ≤ 60ms (캐시 적중 시), p95 ≤ 500ms (캐시 미스) | TanStack Query devtools + 백엔드 APM |
| Performance (UI) | Lighthouse Performance ≥ 90, LCP < 2.5s, INP < 200ms | Lighthouse CI |
| Performance (예측) | MAPE ≥ 80% (1~7w), ≥ 70% (8~21w) | S-012 정확도 이력 페이지에서 자동 측정 |
| Accessibility | WCAG 2.1 AA 준수, 키보드 네비게이션, 스크린리더 호환 | axe-core 자동 검사 + 수동 테스트 |
| Security | OWASP Top 10, JWT 만료 1h + Refresh 7d, HTTPS 강제 | OWASP ZAP, npm audit |
| 한글 처리 | 본문 컨테이너 `word-break: keep-all`, 숫자 `.num` 클래스 일관 적용 | Storybook 시각 회귀 |
| 가용성 | 99.5% (월 다운타임 ≤ 3.6h), 수집 사이클 자동 재시도 3회 | Sentry + 상태 페이지 |

---

## 4. Success Criteria

### 4.1 Definition of Done

- [ ] FR-01 ~ FR-12 모든 기능 구현 완료
- [ ] 디자인 핸드오프 `Sixsense.html` 대비 픽셀 단위 일치 (오차 ±1px, 핵심 4화면 시각 회귀 자동화)
- [ ] 단위 테스트 + 통합 테스트 작성 및 통과 (Vitest + Testing Library)
- [ ] E2E 테스트 작성 및 통과 (Playwright, S-001 + 핵심 3 모달 경로)
- [ ] 코드 리뷰 완료 (3인 팀 상호 리뷰)
- [ ] OpenAPI 스펙(`backend/openapi.yaml`) 발행 및 프론트엔드 타입 생성
- [ ] 운영 환경 배포 + 1주 실측 수집 사이클 검증

### 4.2 Quality Criteria

- [ ] 테스트 커버리지 ≥ 80% (라인 + 브랜치)
- [ ] ESLint 0 errors, Prettier 일관 적용
- [ ] TypeScript strict 모드, `any` 사용 ≤ 5건 (외부 라이브러리 인터페이스만)
- [ ] Lighthouse Performance ≥ 90, Accessibility ≥ 95
- [ ] CI/CD 빌드 성공 (GitHub Actions)
- [ ] Storybook에 공유 컴포넌트 12종 모두 등록 + 4조합(라이트/다크 × 편안/컴팩트) 시각 회귀

### 4.3 Course-Specific (KAIST CAIO)

- [ ] PDCA 워크플로우 산출물 4종(PRD/Plan/Design/Do) 모두 `docs/` 트리에 존재
- [ ] bkit 명령으로 워크플로우 진행이 검증 가능
- [ ] 발표 자료(데모 시연 + PRD 핵심 페이지) 준비

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| R-01: 14신호 중 일부 수집 실패 (사이트 구조 변경, API 키 만료) | High | Medium | 신호별 fallback 정책 정의 (전주값 사용/보간/사용자 알림). S-014 수집 현황에서 실패 즉시 가시화 |
| R-02: HITL 재학습 응답 시간 과다 | High | Medium | 비동기 큐 + 진행상태 표시 UI (`processing` → `done`). 사용자는 즉시 다음 작업 가능 |
| R-03: SVG `LineChart` → Recharts 마이그레이션 시 신뢰구간 밴드 재현 어려움 | Medium | High | Phase 0에서 PoC 우선. 핸드오프 README §"Chart confidence bands stacking" 경고 정독 |
| R-04: 한글 줄바꿈 깨짐 (특히 카드 내부 긴 신호명) | Medium | Medium | 본문 `word-break: keep-all` 전역 적용. Storybook에서 긴 텍스트 케이스 시각 회귀 |
| R-05: AI 예측 모델 정확도 부족 (Phase 5 통합 시) | High | Medium | KPI 미달 시 분석 보고서 작성 + Phase 6에서 모델 튜닝 1주 추가 |
| R-06: Claude Code/bkit 환경 변경으로 PDCA 워크플로우 깨짐 | Medium | Low | 산출물 4종은 plain markdown — 도구 종속성 없음 |
| R-07: KAIST 발표 일정 임박 시 Phase 5 미완성 | High | Low | Phase 4까지만 완성해도 mock 데이터로 14화면 시연 가능 (디자인 핸드오프 그대로 사용) |

---

## 6. Impact Analysis

### 6.1 Changed Resources

본 프로젝트는 신규 빌드이므로 변경 대상 기존 리소스는 없음. 단, 데이터 수집 소스의 외부 의존성은 명시:

| Resource | Type | Change Description |
|----------|------|--------------------|
| Yahoo Finance API (yfinance) | 외부 데이터 소스 | A-1 신호 수집 (신규 의존) |
| SEC EDGAR RESTful API | 외부 데이터 소스 | A-2 신호 수집 (신규 의존) |
| DART OpenAPI | 외부 데이터 소스 | 국내 기업 재무 데이터 (신규 의존) |
| FRED API | 외부 데이터 소스 | 거시지표 5종 (신규 의존) |
| Anthropic Claude API | LLM 서비스 | 뉴스/Earnings Call 감성 분석 (신규 의존) |
| 구글 알리미 RSS | 외부 피드 | 조사기관 코멘트 수집 (신규 의존) |

### 6.2 Current Consumers

신규 프로젝트이므로 해당 없음.

### 6.3 Verification

- [ ] 외부 API 모두 무료 티어 한도 내 사용량 검증 (PRD §05 P2: 유료 데이터 금지)
- [ ] API 키 관리: AWS Secrets Manager (운영) + `.env`(로컬, gitignore)
- [ ] Rate Limit 정책: 모든 외부 호출에 지수 백오프 재시도 + 429 처리

---

## 7. Architecture Considerations

### 7.1 Project Level Selection

| Level | Characteristics | Recommended For | Selected |
|-------|-----------------|-----------------|:--------:|
| **Starter** | Simple structure (`components/`, `lib/`, `types/`) | Static sites, portfolios, landing pages | ☐ |
| **Dynamic** | Feature-based modules, BaaS integration | Web apps with backend, SaaS MVPs, fullstack apps | ✅ |
| **Enterprise** | Strict layer separation, DI, microservices | High-traffic systems, complex architectures | ☐ |

**선택 근거**: 본 프로젝트는 14화면 풀스택 앱 + 외부 데이터 파이프라인 + LLM 통합. Dynamic 레벨이 가장 적합. Enterprise까지는 과도(3인 팀 + 7주 일정).

### 7.2 Key Architectural Decisions

| Decision | Options | Selected | Rationale |
|----------|---------|----------|-----------|
| Frontend Framework | Next.js / React + Vite / Vue | **React 18 + Vite 5** | 핸드오프가 React 18.3.1 기반. SSR 불필요 (관리자용 B2B). Vite가 가장 빠른 HMR |
| Language | JavaScript / TypeScript | **TypeScript 5** | 14화면 + 12 API의 타입 안정성 필수 |
| State Management | Context / Zustand / Redux / Jotai | **Zustand (UI 전역) + TanStack Query (서버 상태)** | 핸드오프 README 권장 |
| API Client | fetch / axios / TanStack Query | **TanStack Query + fetch** | 주간 갱신 데이터 → 캐싱 효과 큼 |
| Form Handling | react-hook-form / formik / native | **react-hook-form** | HITL 패널의 임계치 입력 폼 (가벼움) |
| Styling | Tailwind / CSS Modules / styled-components | **CSS Modules + CSS 변수** | 핸드오프가 CSS 변수 디자인 토큰 사용. Tailwind 미사용 |
| Charting | Recharts / Visx / D3 | **Recharts (1순위) / Visx (백업)** | 핸드오프의 SVG `LineChart` API 모양 보존하며 교체 |
| Testing | Jest / Vitest / Playwright | **Vitest (단위) + Playwright (E2E)** | Vite 친화적 |
| Backend Framework | FastAPI / Express / NestJS / BaaS | **FastAPI (Python)** | 데이터 수집·LLM·예측 모델 친화. OpenAPI 자동 생성 |
| Backend Language | Python / Node.js / Go | **Python 3.11+** | Prophet/LangChain 생태계 |
| DB | PostgreSQL / MongoDB / SQLite | **PostgreSQL + TimescaleDB** | 시계열 데이터 효율 |
| Cache | Redis / Memcached | **Redis** | 주간 스냅샷 캐싱 |
| Scheduler | APScheduler / Airflow / Celery | **APScheduler** | 단일 잡(매주 화 06:00) — Airflow 과도 |
| Hosting (FE) | Vercel / Netlify / S3+CDN | **Vercel** | React+Vite SPA 호환 |
| Hosting (BE) | AWS ECS / Render / Railway / Heroku | **Render** | 무료 티어로 PoC 가능, 추후 ECS 이전 |
| Auth | NextAuth / Auth0 / Clerk / 자체 | **자체 JWT** | 5명 임원 + 3명 개발자 — 외부 의존 불필요 |

### 7.3 Clean Architecture Approach

```
Selected Level: Dynamic

Folder Structure Preview:
┌─────────────────────────────────────────────────────────┐
│ frontend/                                               │
│   src/                                                  │
│     design-system/   (Sig, MetricCard, LineChart, ...)  │
│     features/                                           │
│       dashboard/     (S-001)                            │
│       forecast/      (S-002, S-009)                     │
│       signals/       (S-003, S-004)                     │
│       graph-rag/     (S-005)                            │
│       news/          (S-006, S-007)                     │
│       macro/         (S-008)                            │
│       events/        (S-010, S-011)                     │
│       accuracy/      (S-012, S-013)                     │
│       collection/    (S-014)                            │
│     pages/           (라우트 정의)                       │
│     services/        (API client, TanStack Query)       │
│     store/           (Zustand)                          │
│     styles/          (디자인 토큰 CSS 변수)              │
│     types/           (OpenAPI 생성 타입)                 │
│     mocks/           (Phase 5 이전 mock 데이터)          │
│                                                         │
│ backend/                                                │
│   app/                                                  │
│     api/             (FastAPI 라우터)                    │
│     services/        (수집·예측·LLM)                    │
│     models/          (SQLAlchemy)                       │
│     pipelines/       (배치 작업)                         │
│   tests/                                                │
│                                                         │
│ docs/                (PDCA 산출물)                       │
│ design_handoff_sixsense_dram_dashboard/  (참조용)        │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Convention Prerequisites

### 8.1 Existing Project Conventions

- [ ] `CLAUDE.md` has coding conventions section → **Phase 0에서 생성 필요**
- [ ] `docs/01-plan/conventions.md` → **본 파일 시리즈와 함께 생성**
- [ ] `CONVENTIONS.md` at project root → 신규
- [ ] ESLint configuration → Phase 0에서 추가
- [ ] Prettier configuration → Phase 0
- [ ] TypeScript configuration → Phase 0

### 8.2 Conventions to Define/Verify

| Category | Current State | To Define | Priority |
|----------|---------------|-----------|:--------:|
| **Naming** | missing | 컴포넌트 PascalCase, 파일 kebab-case, 함수 camelCase | High |
| **Folder structure** | missing | `features/<도메인>/components|hooks|api|types` | High |
| **Import order** | missing | external → internal absolute → relative (ESLint `import/order` 규칙 강제) | Medium |
| **Environment variables** | missing | `VITE_*` (클라이언트), 그 외는 서버 전용 | Medium |
| **Error handling** | missing | 백엔드: `{error, message, trace_id}` 표준 응답 / 프론트: TanStack Query 에러 바운더리 | Medium |
| **한글 처리** | missing | 본문 컨테이너 `word-break: keep-all`, 숫자 `.num` 클래스 | High |
| **AI 자동생성 라벨** | missing | AI 출력에 `AiNote` 컴포넌트 사용, "AI 종합 판단 · Claude 자동 생성" 라벨 표시 | Medium |

### 8.3 Environment Variables Needed

| Variable | Purpose | Scope | To Be Created |
|----------|---------|-------|:-------------:|
| `VITE_API_URL` | 백엔드 API base URL | Client | ☐ |
| `VITE_USE_MOCK` | mock/실측 데이터 토글 | Client | ☐ |
| `DATABASE_URL` | PostgreSQL 연결 | Server | ☐ |
| `REDIS_URL` | Redis 연결 | Server | ☐ |
| `ANTHROPIC_API_KEY` | Claude API (감성 분석) | Server | ☐ |
| `FRED_API_KEY` | 거시지표 수집 | Server | ☐ |
| `DART_API_KEY` | DART OpenAPI | Server | ☐ |
| `JWT_SECRET` | JWT 서명 | Server | ☐ |
| `JWT_REFRESH_SECRET` | Refresh 토큰 | Server | ☐ |
| `SENTRY_DSN` | 에러 모니터링 | Both | ☐ |

### 8.4 Pipeline Integration

본 프로젝트는 bkit 9-phase Development Pipeline의 일부가 아닌 PDCA 단독 워크플로우로 진행.

| Phase | Status | Document Location | Command |
|-------|:------:|-------------------|---------|
| Phase 1 (Schema) | ☐ | `docs/01-plan/schema.md` | 필요 시 별도 |
| Phase 2 (Convention) | ☐ | `docs/01-plan/conventions.md` | 필요 시 별도 |

---

## 9. Next Steps

1. [x] PRD 작성 완료 (`docs/00-pm/sixsense.prd.md`)
2. [ ] **현재 단계**: Plan 문서 작성 완료 → 팀 리뷰
3. [ ] Design 문서 작성 (`docs/02-design/features/sixsense.design.md`) — 3가지 아키텍처 옵션 중 Option C(Pragmatic Balance) 권장
4. [ ] Do 문서 작성 (`docs/03-do/features/sixsense.do.md`) — 구현 가이드 + Checkpoint 4 승인
5. [ ] Phase 0 구현 시작 — 디자인 시스템 + 공유 컴포넌트 12종

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-05-16 | bkit PDCA Plan 단계 초안 — PRD 자동 참조, 디자인 핸드오프 반영 | 김영석 |

---

## 10. Phase 6 — 멀티 모델 예측 아키텍처 (2026-05-17 추가)

사용자 요구: 정확도 개선을 위해 기존 Prophet 외 단기/중장기 별도 모델 도입.

### Architecture Decision
- **단기 (1~7주)**: 트리 기반 (XGBoost / LightGBM 우선, macOS libomp 없으면 sklearn GBR/HistGBR fallback). 두 모델 학습 후 MAPE 비교로 우수 모델 자동 선정.
- **중장기 (8~21주)**: LSTM (PyTorch). TFT는 학습 데이터 200주+ 확보 후 도입 (현재 40~80주는 과적합 위험).
- **기존 Prophet 보존**: baseline + 비교 기준으로 계속 사용.

### Success Criteria 갱신
- 단기 MAPE ≤ 5% (Phase 5e 7.54% → **달성 4.54%**)
- 중장기 MAPE ≤ 15% (LSTM held-out **9.19% 달성**)
- 학습 시간 ≤ 30초 (전체 파이프라인 ~12초 ✅)

### 위험 + 대응
- **소량 데이터 과적합**: LSTM dropout 0.2, 80주 학습 (cutoff 2026-01-31)
- **macOS OpenMP 미설치**: sklearn fallback 자동 (XGBoost/LightGBM 무관 운영 보장)
- **신규 모델 결과 신뢰**: Prophet 동시 출력으로 sanity check

상세: docs/10-modeling/modeling-architecture.md

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.2 | 2026-05-17 | Phase 6 멀티 모델 아키텍처 추가 (단기 Tree + 중장기 LSTM) | 김영석 |
