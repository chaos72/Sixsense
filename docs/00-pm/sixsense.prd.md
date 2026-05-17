# [Server DRAM Price 식스센스 : 서버용 D램 가격 예측 대시보드] — PRD

팀명: [CAIO 10기 6조 식스센스]

제품명: [Server DRAM Price 식스센스_v0.1]

제품철학: [반도체 가격은 예측이 아니라 분석을 통한 해석이다]

작성일: [2026-04-26]

## 01. 조원 및 회사 소개

| 이름 | 소속 | 역할 | 이메일 |
| --- | --- | --- | --- |
| [김정일] | [SK hynix] | [현업 사용자] | [piedmont2220@gmail.com] |
| [주광철] | [엔코아에너텍] | [개발 리드] | [caseyjoo@daum.net] |
| [김영석] | [Dataiku Korea] | [프로젝트 리드] | [chaos419@naver.com] |

## 02. 어떤 분야에 AI를 도입하려고 하는가

[서버용 DRAM 반도체 가격에 직간접적으로 영향을 줄 수 있는 전 세계에 흩어진 정형(숫자) 및 비정형(텍스트) 데이터를 100% AI 기반으로 자동으로 수집, 가공하여 서버용 DRAM 반도체 가격을 주간 단위로 단기(1~7주)/중장기(8~21주) 변동 추이를 예측(매주 화요일 예측)하고 시각화하는 웹 기반 대시보드 애플리케이션 구축]

## 03. 현재 어떤 문제가 있는가

- 고통: [반도체 가격 예측에 필요한 데이터 수집의 어려움과 전통적인 예측 방법이 잘 맞지 않을 뿐 아니라 서로 모여 회의하느라 시간과 비용이 많이 발생]
- 기존 대안의 한계: [현재는 제안된 정보를 기반으로 사람에 의해 수행되는데, 시장의 급박한 변동을 파악하고 반영하기 어려움]
- 문제의 규모: [만약 이문제를 해결할 수 있으면, 반도체 가격 예측의 문제를 넘어, 원자재 및 각종 수요 예측에 활용할 수 있어 수많은 사람이 겪는 문제를 해결할 수 있고, 이로 인한 연간 손실 비용은 파악하기 어려울 정도로 수천억 이상의 손실도 발행 할 수 있음]

## 04. 사용자는 누구인가

- 이름: [A.정우성 부사장, 50대, B.이병헌 전무, 50대, C.장동건 상무, 50대, D.이정재 상무, 50대, E.조인성 상무, 50대]
- 소속: [A.글로벌 반도체 영업 전략팀, B.수요기업 구매팀, C. 소재/장비기업 마케팅팀, D.반도체 시장분석 기관, E.금융/투자기관]
- 일과: [반도체 시장 동향을 파악하고자 매일 반도체 관련 정보를 수집하고, 또한 반도체 가격에 영향을 줄 수 있는 글로벌 이벤트(예, 전쟁, 태풍, 부도, 파업 등) 조사 및 정보 수집]
- 지불 의사: [ROI 계산을 통해 투자 비용이 결정될 수 있으나, 초기에는 파일럿 형태로 3억 이내]

## 05. 문제 해결을 위한 AI 기능

### P0 — MVP 필수

- [기능 1 : 14가지의 강력한 프록시(대리) 데이터를 하나의 대시보드로 통합하여, 복잡한 엑셀 작업 없이 직관적인 인사이트 제공.]
- [기능 2 : 반도체 가격에 영향을 주는 무료 수집 가능한 정형/비정형 데이터 자동 수집]
- [기능 3 : 이러한 정형/비정형 데이터를 비전문가도 파악할 수 있는 UI/UX 제공(시각화 챠트 포함)]
- [기능 4 : 정형/비정형/각종 글로벌 이벤트 데이터를 기반으로 단기(1~7주)/중장기(8~21주) 주별 예측은 100% AI에 의해 자동 예측]
- [기능 5 : DRAM 가격 52주 히스토리 및 AI 예측결과 그래프로 시각화. 이때 신뢰구간 상향 하향 표시]
- [기능 6 : 서버용 DRAM 가격과 구리가격의 영향도 파악을 위한 Graph RAG 기능 포함 ]
- [기능 7 : 뉴스 감성점수, 글로벌 이벤트위험도 점수, AI 판단 근거 기준 등에 대해 HITL(Human in the Loop)기능을 반영하여, 임계치(Threshold) 또는 가중치(Weight)를 조정할 수 있는 수정 기능을 제공하고, 수정 시 원래 결과와 수정 반영된 결과도 함께 제공
- [기능 8 : 주체별 재고일수 추이 (최근 1년) 및 주요 분석 기관의 코멘트와 제조사 가동률 데이터(단위: 주/Weeks)를 생산자 재고, 수요기업(PC/서버), 유통채널(스팟) 정보를 포함하여 제공

### P1 — 있으면 좋음

- [기능 A : 주별 새롭게 무상 수집 가능한 정형/비정형 데이터 목록 제공]
- [기능 B : 주별 반도체 가격에 영향을 줄 수 있는 글로벌 이벤트(전쟁, 지진, 태풍 등) 목록 제공]

### P2 — 제외 (Non-Goals)

- [하지 않을 것 1 : 전통적인 시계열 분석 기법 적용 금지(ARIMA 등)]
- [하지 않을 것 2 : 유료 데이터 수집 금지]

### P3 — 초기 데이터 적재

- [기능 A : 최초 데이터 적재 필요. 최소 초기 지난 4주 데이터를 수집 및 적재]

### P0 기능 ↔ 화면(Screen) 매핑

Claude Design 핸드오프 (`/design_handoff_sixsense_dram_dashboard/`)에서 픽셀 단위로 설계된 14개 화면(S-001 ~ S-014)에 P0/P1 기능을 다음과 같이 매핑한다.

| P0 기능 | 매핑 화면 | 인터랙션 |
| --- | --- | --- |
| 기능 1 (14신호 통합 대시보드) | **S-001** 메인 대시보드 | Group A·B 각 7카드, 카드 클릭 → S-003/S-004 |
| 기능 2 (자동 수집) | **S-014** 데이터 수집 현황 + S-001 푸터바 | 매주 화 06:00 KST, 신호별 success/fail |
| 기능 3 (비전문가용 UI/UX) | 전 화면 공통 | 디자인 토큰 기반 정보 밀도/테마 토글 |
| 기능 4 (단기/중장기 AI 예측) | **S-001** 가격 스냅샷 3카드 → **S-002** 예측 근거 모달 | 1~7주/8~21주 탭, 신호 기여도 바차트 |
| 기능 5 (52주 히스토리 + 신뢰구간 시각화) | **S-001** DRAM 차트 영역 | 범위 필터(단기/중장기/전체), 신뢰구간 밴드, 점 클릭 → S-009 |
| 기능 6 (Graph RAG: 구리↔DRAM) | **S-001** Graph RAG 미니 + **S-005** 상세 모달 | 52주 오버레이, 리드타임 상관계수, 인과관계 다이어그램 |
| 기능 7 (HITL 임계치/가중치 조정) | 전 상세 화면(S-002, S-003, S-004, S-007 등)의 **HITL 패널** | 긍정/중립/부정 3규칙 입력, `저장 & 재학습` → `POST /api/hitl/rules` |
| 기능 8 (재고/가동률/거시지표) | **S-008** 거시경제 통합(5탭) + **S-014** 수집 현황 | Fed Rate/DXY/PMI/USD-KRW/Copper 52주 트렌드 |
| P1-A (신규 수집 데이터 목록) | **S-014** 데이터 수집 현황 | 신호별 신규 항목 수, 주간 증감 |
| P1-B (글로벌 이벤트 목록) | **S-010** 글로벌 이벤트 목록 + **S-011** 상세 모달 | 위험도 필터, 영향 방향, 연결 뉴스/신호 |

추가 화면(PRD 미명시, 디자인에서 신규 도입):
- **S-006** AI 뉴스 분석 전체 목록 (감성/출처/날짜 필터)
- **S-007** 뉴스 원문 + AI 분석 상세 (단/중/장기 영향)
- **S-009** 주별 신호 스냅샷 (차트 점 드릴다운)
- **S-012** AI 예측 정확도 이력 (MAPE 추이)
- **S-013** 당시 신호 vs 현재 신호 비교 (예측 오차 분석)

## 06. 사용자 시나리오

매주 화요일 아침, 사용자(반도체 전략/구매/투자 담당자)가 대시보드를 열어 "이번 주 서버 DRAM 가격이 어떻게 될까?"를 5분 안에 판단할 수 있도록 설계한다.

### 6.1 전체 플로우 (Happy Path)

1. **로그인 → S-001 메인 대시보드 진입**
   - 페이지 상단(Topbar): 자동수집 상태 표시, 마지막 업데이트 타임스탬프, 테마/밀도 토글
2. **첫 5초 — 가격 스냅샷 3카드 확인**
   - 현재 계약가 / 1~7주 AI 예측가 / 8~21주 AI 예측가
   - 카드 상단 변화율(▲/▼)과 신뢰도(%)로 즉시 판단
3. **차트 영역에서 52주 트렌드 + 예측 확인**
   - 범위 필터(`단기 1~7주` / `중장기 8~21주` / `전체`)로 시각 전환
   - 8~21주 구간은 파스텔 그린으로 강조(2.6px 라인, 큰 점)
4. **14신호 카드 영역에서 이상치 감지**
   - Group A(정형 7) / Group B(비정형 7) 그리드
   - A-4 재고지수가 100 초과 시 Red Alert (펄싱 애니메이션) — 즉시 시선 유도
5. **드릴다운(필요 시)**
   - 가격 카드 클릭 → **S-002** 예측 근거 모달 (신호 기여도 바차트, 주별 예측 테이블)
   - 신호 카드 클릭 → **S-003**(정형) 또는 **S-004**(비정형) 상세 모달
   - 차트 미래 점 클릭 → **S-009** 주별 신호 스냅샷
   - Graph RAG 카드 → **S-005** 구리↔DRAM 인과관계 모달
   - 뉴스 카드 → **S-007** 원문 + AI 분석 모달
   - 이벤트 카드 → **S-011** 이벤트 상세 모달
   - 정확도 카드 → **S-013** 당시/현재 신호 비교 모달
6. **전체 목록 페이지로 이동(선택)**
   - 뉴스 더보기 → **S-006** 전체 뉴스 분석 페이지
   - 거시지표 더보기 → **S-008** 5탭(Fed/DXY/PMI/USDKRW/Copper)
   - 이벤트 더보기 → **S-010** 글로벌 이벤트 목록
   - 정확도 더보기 → **S-012** MAPE 추이 + 정확도 이력
   - 수집 현황 더보기 → **S-014** 신호별 수집 상태
7. **HITL 조정(옵션)**
   - 모든 상세 화면 하단의 HITL 패널에서 임계치(긍정 ≥0.30 / 중립 ±0.15 / 부정 ≤-0.30)를 조정
   - `저장 & 재학습` 클릭 → `POST /api/hitl/rules` 호출 → 수정 전/후 비교 결과 제공
8. **세션 종료**
   - 사용자 설정(테마/밀도)은 localStorage에 자동 저장

### 6.2 페르소나별 진입 경로

| 페르소나 | 1순위 관심 | 주요 경로 |
| --- | --- | --- |
| A. 정우성 부사장 (영업전략) | 가격 방향성, 신뢰도 | S-001 → S-002 → S-012 (예측 정확도 검증) |
| B. 이병헌 전무 (구매팀) | 단기 변동, 재고 위험 | S-001 → A-4 신호 카드 → S-003(A-4) → S-014 |
| C. 장동건 상무 (마케팅) | 거시지표, 뉴스 톤 | S-001 → S-008 거시 → S-006 뉴스 목록 |
| D. 이정재 상무 (시장분석) | 이벤트, Graph RAG | S-001 → S-005 → S-010 이벤트 → S-011 상세 |
| E. 조인성 상무 (투자) | 정확도 이력, MAPE | S-012 → S-013 → S-001 종합 판단 |

### 6.3 핵심 인터랙션 규칙

- **모달 스택**: 모달 위에 모달이 겹쳐 열림 (예: S-011 이벤트 → 연결뉴스 → S-007)
- **딥링크**: URL 쿼리 파라미터로 화면/탭/모달 상태 직접 진입 가능
  - 예) `?screen=S-001&modal=S-003&tab=A-4`
- **테마/밀도**: 우상단 토글로 라이트/다크 + 편안/컴팩트 전환, 즉시 반영
- **ESC/바깥 클릭**: 항상 최상위 모달만 닫힘

## 07. 화면 정의

전체 14개 화면이 Claude Design을 통해 픽셀 단위(hifi)로 설계되어 `/design_handoff_sixsense_dram_dashboard/` 폴더에 hand-off되어 있다. 본 PRD에서는 화면 목록·역할·진입 경로만 명세하며, 시각 구현 명세(레이아웃·여백·타이포·색상)는 디자인 핸드오프 산출물을 단일 진실 공급원(SSOT)으로 한다.

> ⚠️ **절대 원칙 (CRITICAL)**: 구현은 핸드오프의 14개 화면과 **100% 동일한 UI**를 목표로 한다. **새로운 화면을 만들거나 컴포넌트 카탈로그/쇼케이스를 별도 작성하지 않는다**. 구현 전략은 §7.4 참조.

### 7.1 화면 목록 (S-001 ~ S-014)

| ID | 타입 | 화면명 | 핵심 역할 |
| --- | --- | --- | --- |
| S-001 | Full page | 메인 대시보드 | 진입점. 가격 스냅샷 + 차트 + 14신호 + Graph RAG + 뉴스/거시 + 이벤트/정확도 + 수집 현황 |
| S-002 | Modal | AI 예측 근거 상세 | 1~7w/8~21w 2탭. 신호 기여도 바차트, 신뢰구간, 주별 예측 테이블 |
| S-003 | Modal | 정형 Group A 상세 | 7탭(A-1~A-7). 28주 트렌드 + 원본 테이블 + AI 해석. A-4 Red Alert 특수 처리 |
| S-004 | Modal | 비정형 Group B 상세 | 7탭(B-1~B-7). 8주 감성 차트 + 뉴스 리스트 + AI 해석 |
| S-005 | Modal | Graph RAG — 구리↔DRAM | 52주 오버레이 + 리드타임 상관계수 + 인과관계 다이어그램 |
| S-006 | Full page | AI 뉴스 분석 전체 목록 | 감성/출처/날짜 필터, 정렬, 페이지네이션 |
| S-007 | Modal | 뉴스 원문 + AI 분석 | 기사별 AI 요약 + 단/중/장기 DRAM 영향 + 연결 신호 + 원문링크 |
| S-008 | Full page | 거시경제 지표 통합 | 5탭(Fed Rate / DXY / PMI / USD-KRW / Copper). 52주 트렌드 + 월간 원본 + 상관 노트 |
| S-009 | Modal | 주별 신호 스냅샷 | 차트 점 클릭 진입. 과거주: 신호 vs 실제 / 미래주: 예측 분해 |
| S-010 | Full page | 글로벌 이벤트 전체 목록 | 위험도/유형 필터, DRAM 영향 방향 |
| S-011 | Modal | 글로벌 이벤트 상세 | AI 요약 + 단/중/장기 영향 + 연결 뉴스/신호 |
| S-012 | Full page | AI 예측 정확도 이력 | MAPE 추이 라인차트 + 정확도 이력 테이블(7w/21w/전체 필터) |
| S-013 | Modal | 당시 신호 vs 현재 신호 | 과거 예측 시점의 14신호 vs 현재 사이드바이사이드 + 오차원인 AI 분석 |
| S-014 | Full page | 데이터 수집 현황 | 신호별 출처·타임스탬프·신규 항목·주간 증감·success/fail |

### 7.2 라우팅 규칙

- **Full page**(S-001/006/008/010/012/014): 라우터의 실제 URL 경로로 매핑 (예: `/`, `/news`, `/macro`, `/events`, `/accuracy`, `/collection`)
- **Modal**(S-002/003/004/005/007/009/011/013): 현재 페이지 위에 오버레이. URL 쿼리 파라미터로 상태 직렬화하여 새로고침/공유 시에도 복원

### 7.3 디자인 핸드오프 산출물 위치

```
design_handoff_sixsense_dram_dashboard/
├── README.md                  # 구현 가이드 (필독)
├── Sixsense.html              # 14화면 전체 인터랙티브 프로토타입
├── Sixsense Canvas.html       # 14화면을 동시에 펼친 디자인 캔버스
├── design-canvas.jsx          # 캔버스 전용 컴포넌트
└── src/
    ├── styles.css             # 디자인 토큰(CSS 변수) + 컴포넌트 스타일 전체
    ├── data.js                # mock 데이터 (API 스키마 추론용)
    ├── components.jsx         # 공유 컴포넌트 (Sig, MetricCard, LineChart, Modal, HITL ...)
    ├── dashboard.jsx          # S-001
    ├── modals.jsx             # S-002, S-003, S-004, S-005, S-007, S-009, S-011, S-013
    ├── pages.jsx              # S-006, S-008, S-010, S-012, S-014
    ├── app.jsx                # 라우팅 + 모달 스택 + 테마/밀도 + 딥링크
    └── tweaks-panel.jsx       # 개발 전용(프로덕션 미포함)
```

### 7.4 구현 전략 — 핸드오프 직접 포팅 (Direct Port)

핸드오프 코드는 그 자체가 React 코드(JSX)이므로 **재작성하지 않고 직접 포팅**한다. 이는 핸드오프와 100% 동일한 UI를 보장하는 가장 안전하고 빠른 경로다.

**포팅 단계 (Phase 0):**

| 단계 | 작업 | 출처 | 대상 |
|------|------|------|------|
| 1 | 전체 CSS 복사 | `design_handoff/src/styles.css` | `frontend/src/styles/styles.css` |
| 2 | mock 데이터 복사 | `design_handoff/src/data.js` | `frontend/src/mocks/data.js` |
| 3 | 공유 컴포넌트 포팅 | `design_handoff/src/components.jsx` | `frontend/src/components/components.jsx` |
| 4 | S-001 대시보드 포팅 | `design_handoff/src/dashboard.jsx` | `frontend/src/screens/dashboard.jsx` |
| 5 | 8개 모달 포팅 | `design_handoff/src/modals.jsx` | `frontend/src/screens/modals.jsx` |
| 6 | 5개 풀페이지 포팅 | `design_handoff/src/pages.jsx` | `frontend/src/screens/pages.jsx` |
| 7 | 라우팅/테마/모달 스택 포팅 | `design_handoff/src/app.jsx` | `frontend/src/screens/app.jsx` |
| 8 | 엔트리에서 핸드오프 앱 마운트 | — | `frontend/src/App.tsx` (얇은 래퍼) |

**금지 사항 (DO NOT)**:
- ❌ 핸드오프와 다른 새로운 UI/레이아웃 작성
- ❌ "컴포넌트 카탈로그/쇼케이스" 페이지 작성
- ❌ 핸드오프에 없는 화면 추가
- ❌ 핸드오프 디자인 토큰 (색상/타이포/간격) 변경

**허용 사항 (OK)**:
- ✅ Vite/TypeScript 호환을 위한 최소 변경 (import 경로, 파일 확장자)
- ✅ Mock 데이터를 향후 실제 API 호출로 교체 (Phase 5)
- ✅ `tweaks-panel.jsx`는 개발 전용 — 프로덕션 배포 시 제외

**프로덕션 차트 라이브러리 교체**는 Phase 6 이후 별도 작업. 초기 포팅 단계에서는 핸드오프의 SVG `LineChart`를 그대로 사용한다.

## 08. 기술 요구사항 ⭐

### 기술 스택

- 언어: [Python 3.11]
- 핵심 언어 & 런타임
- 백엔드 언어: [Python 3.11]
- 프론트엔드 언어: [TypeScript 5.x + JavaScript (ES2022)
- 패키지 관리 (백엔드): [pip + requirements.txt]
- 패키지 관리 (프론트엔드): [npm + package.json]
- 프레임워크
- 백엔드 API 프레임워크: [FastAPI 0.111]
- ASGI 서버: [Uvicorn 0.29 (FastAPI 실행용)]
- 프론트엔드 UI 프레임워크: [React 18 + TypeScript]
- 프론트엔드 빌드 도구: [Vite 5.x (개발 서버 및 번들링)]
- CSS 스타일링: [TailwindCSS 3.x]
- 데이터베이스 & ORM
- DB 엔진: Supabase (파일 1개: dram_sixsense.db)
- ORM: SQLAlchemy 2.0 + psycopg2 (Python ↔ Supabase 연결)
- 데이터 검증: Pydantic v2 (API 입출력 데이터 타입 검증)
- DB 마이그레이션: Alembic 1.13 (테이블 구조 변경 이력 관리)
- 백엔드 구성 라이브러리
- 비동기 HTTP 클라이언트: httpx 0.27 (외부 API 비동기 호출)
- 동기 HTTP 클라이언트: requests 2.31 (단순 크롤링)
- 환경변수 관리: python-dotenv 1.0 (.env 파일로 API 키 관리)
- 설정 관리: pydantic-settings 2.x (환경 설정 타입 안전 관리)
- 날짜/시간 처리: python-dateutil 2.9
- JSON 처리: orjson 3.9 (빠른 JSON 직렬화, FastAPI 연동)
- 스케줄러 (자동화)
- 작업 스케줄러: APScheduler 3.10
- 매주 화요일 새벽 6시 자동 실행
- 수집 → 감성분석 → 예측 → DB 저장 순서 파이프라인 실행
- 수집 실패 시 재시도(retry) 3회 자동 처리
- 비동기 처리: asyncio (Python 내장, 병렬 데이터 수집)
- 데이터 수집 라이브러리
- Group A — 정형 데이터 (7종)

| 신호 | 라이브러리 | 용도 |
| --- | --- | --- |
| A-1 대만 공급망 | yfinance 0.2 | ASPEED·Quanta·Wiwynn 주가·재무 데이터 |
| A-1 XBRL 파싱 | lxml 5.x + anthropic | XBRL 재무제표 파싱 + LLM 보조 추출 |
| A-2 빅테크 CapEx | sec-edgar-downloader 5.x | SEC EDGAR 10-Q 자동 다운로드 |
| A-2 수치 추출 | anthropic | LLM으로 CapEx 수치 정확 추출 |
| A-3 관세청 ASP | requests + xml.etree | 관세청 무역통계 Open API 호출 |
| A-4 재고/출하 | requests | KOSIS Open API 호출 |
| A-5 AWS Spot | boto3 1.34 | AWS EC2 Spot 가격 API |
| A-6 Polymarket | requests | Polymarket CLOB API 호출 |
| A-7 구리 가격 | fredapi 0.5 | FRED API (티커 PCOPPUSDM) |

- Group B — 비정형 데이터 (7종)

| 신호 | 라이브러리 | 용도 |
| --- | --- | --- |
| B-1 Earnings Call | requests + BeautifulSoup4 4.12 | FMP API·Motley Fool 트랜스크립트 수집 |
| B-2 대만 뉴스 | feedparser 6.0 | TechNews.tw RSS 피드 파싱 |
| B-3 Reddit | praw 7.7 | r/hardware·r/semiconductors 자동 수집 |
| B-4 지정학 | requests | GDELT Project API 쿼리 |
| B-5 LTA 비율 | requests + BeautifulSoup4 | TechNews.tw 번체자 키워드 크롤링 |
| B-6 HBM IR PDF | pdfplumber 0.11 | IR PDF 자동 다운로드 및 텍스트 추출 |
| B-7 서버 BOM | feedparser 6.0 | OCP 블로그·데이터센터 뉴스 RSS 파싱 |
| B-8 재고일수(공시) | OpenDartReader + pandas 2.2 | DART 오픈 API 기반 삼성전자·SK하이닉스 분기별 재고자산 자동 수집 및 정형화 |
| 전체 B군 감성분석 | anthropic 0.28 | Claude API로 -1~+1 감성 점수화 |

- AI / ML 엔진
- LLM (언어 AI): anthropic 0.28 — Claude API
- Group B 전체 뉴스·문서 감성 분석 (-1~+1 점수화)
- AI 요약 텍스트 자동 생성 (한국어 3~5문장)
- 단기·중기·장기 DRAM 영향 분석 텍스트 생성
- SEC 10-Q, IR PDF, XBRL 수치 추출 보조
- 예측 오차 원인 분석 텍스트 생성
- 예측 AI (시계열 예측): prophet 1.1 — Facebook Prophet
- 7주·21주 주별 DRAM 가격 예측
- 신뢰구간 상단/하단 자동 계산
- Group A 정형 데이터를 외부 회귀 변수(regressor)로 투입
- Group B 감성 점수를 피처로 추가
- ARIMA 등 전통 시계열 기법 일절 사용 금지
- 데이터 처리: pandas 2.2 — 시계열 데이터 전처리·병합·집계
- 수치 계산: numpy 1.26 — 배열 연산·통계 계산
- 통계 분석: scipy 1.13 — 상관계수·선행 시차 최적화 계산
- 머신러닝 유틸: scikit-learn 1.5 — 정규화·피처 엔지니어링
- Graph RAG 엔진 (구리↔DRAM 상관관계)
- 그래프 구조 관리: networkx 3.3 — 신호 간 인과관계 노드·엣지 관리
- 상관계수 계산: scipy.stats.pearsonr — 선행 시차별 상관계수 산출
- LLM 관계 추론: anthropic — 인과관계 경로 자연어 해석 생성
- 데이터 처리: pandas — 시차(lag) 이동 및 시계열 정렬
- 프론트엔드 라이브러리
- 차트·시각화: Plotly.js 2.x (via react-plotly.js)
- DRAM 52주 히스토리 + 예측 라인 차트 (신뢰구간 포함)
- 구리↔DRAM 오버레이 차트 (Graph RAG)
- 선행 시차별 상관계수 바 차트
- 누적 오차율 추이 차트
- 보조 차트: Recharts 2.x
- 신호 기여도 막대그래프
- 감성 점수 추이 라인 차트
- 재고/출하 비율 차트
- HTTP 클라이언트: axios 1.7 (React → FastAPI 데이터 요청)
- 서버 상태 관리: TanStack Query 5.x (React Query, API 캐싱·자동 갱신)
- UI 컴포넌트: Headless UI 2.x (탭·모달·드롭다운 접근성 컴포넌트)
- 아이콘: Lucide React 0.4 (신호등 아이콘·화살표 등)
- 날짜 처리: date-fns 3.x (날짜 포맷팅)
- 시각화 상세 매핑

| 화면 | 차트 유형 | 사용 라이브러리 |
| --- | --- | --- |
| S-001 메인 — DRAM 차트 | 라인 차트 + 신뢰구간 영역 | Plotly.js |
| S-001 메인 — 신호 카드 | 신호등 배지 (🟢🟡🔴) | TailwindCSS |
| S-001 메인 — Graph RAG 요약 | 미니 듀얼 라인 차트 | Recharts |
| S-002 — 신호 기여도 | 수평 막대그래프 | Recharts |
| S-002 — 주별 예측 테이블 | 데이터 테이블 | TailwindCSS |
| S-003/004 — 신호 추이 | 라인 차트 + 바 차트 | Recharts |
| S-005 — Graph RAG | 듀얼 축 라인 차트 + 바 차트 | Plotly.js |
| S-008 — 거시지표 추이 | 라인 차트 | Plotly.js |
| S-012 — 오차율 추이 | 라인 차트 | Recharts |
| S-013 — 신호 비교 테이블 | 컬러 데이터 테이블 | TailwindCSS |

- 외부 API 목록 & 인증 방식

| API | 인증 방식 | 비용 |
| --- | --- | --- |
| Anthropic (Claude) | API Key (.env) | 유료 (사용량 기반) |
| FRED API | API Key (.env, 무료 발급) | 무료 |
| SEC EDGAR | 없음 (공개 API) | 무료 |
| KOSIS Open API | API Key (.env, 무료 발급) | 무료 |
| 관세청 무역통계 | API Key (.env, 무료 발급) | 무료 |
| Yahoo Finance | 없음 (yfinance 라이브러리) | 무료 |
| Polymarket CLOB | 없음 (공개 API) | 무료 |
| GDELT Project | 없음 (공개 API) | 무료 |
| Reddit (PRAW) | Client ID + Secret (.env) | 무료 |
| FMP (Earnings Call) | API Key (.env, 무료 티어) | 무료 티어 |
| AWS (Spot 가격) | AWS Access Key (.env) | 무료 (API 호출) |
| DART(재고일수) | API Key(.env, 무료 발급) | 무료 |

- 개발 환경 & 실행
- 컨테이너: Docker + Docker Compose
- docker-compose up 한 명령어로 백엔드 + 프론트엔드 동시 실행
- 비개발자도 터미널에서 명령어 하나로 전체 시스템 구동 가능
- 백엔드 포트: http://localhost:8000
- 프론트엔드 포트: http://localhost:3000
- API 문서 자동 생성: http://localhost:8000/docs (FastAPI Swagger UI 자동 제공)
- 환경변수 파일: .env (API 키 모음, Git에 업로드 금지)
- Git 버전 관리: .gitignore로 .env·dram_sixsense.db·__pycache__ 제외
- 전체 기술 스택 한눈에 보기
┌─────────────────────────────────────────────────────────────┐

│  브라우저 (사용자)                                                         │

│  React 18 + TypeScript + Vite                                            │

│  Plotly.js + Recharts + TailwindCSS + TanStack Query                     │

└─────────────────────┬───────────────────────────────────────┘

│ HTTP (axios)

┌─────────────────────▼───────────────────────────────────────┐

│  백엔드 API                                                                 │

│  FastAPI 0.111 + Uvicorn + Pydantic v2                                   │

│  SQLAlchemy 2.0 + Alembic                                                 │

└──────┬─────────────────────┬────────────────────────────────┘

│ ORM                 │ APScheduler (매주 화요일 06:00)

┌──────▼──────┐    ┌─────────▼─────────────────────────────┐

│  SQLite 3   │    │  AI / 데이터 수집 파이프라인             │

│  dram_      │    │                                        │

│  sixsense   │    │  [데이터 수집]                          │

│  .db        │    │  yfinance / sec-edgar-downloader       │

│             │    │  fredapi / boto3 / praw / feedparser   │

│  5개 테이블  │    │  requests + BeautifulSoup4             │

│  · dram_   │    │                                        │

│    prices   │    │  [AI 분석]                              │

│  · macro_   │    │  anthropic (Claude API)                │

│    indicators    │  → 감성분석 / 요약 / LLM 파싱           │

│  · news_    │    │                                        │

│    articles │    │  [예측]                                 │

│  · predic   │    │  prophet (시계열 예측)                  │

│    tions    │    │  scipy + networkx (Graph RAG)          │

│  · collec   │    │  pandas + numpy (데이터 처리)           │

│    tion_logs│    │                                        │

└──────────────┘    └───────────────────────────────────────┘

### 데이터 모델

- 데이터 모델(DB 테이블 설계)
- 전체 테이블 구조
dram_sixsense.db

│

├── dram_prices          (DRAM 실제 가격 히스토리)

├── proxy_signals        (14개 프록시 신호 주간 점수)

├── news_articles        (수집 뉴스/문서 + Claude 분석)

├── global_events        (글로벌 이벤트 + DRAM 영향 분석)

├── predictions          (AI 7주/21주 예측 결과)

├── graph_rag_results    (구리↔DRAM 상관관계 분석)

└── collection_logs      (수집 작업 실행 로그)

- 테이블 ① dram_prices — DRAM 가격 히스토리
┌─────────────────┬─────────────┬─────────────────┐

│  컬럼명                 │  타입                │  설명 / 예시값                             │

├─────────────────┼─────────────┼─────────────────┤

│  id                    │  INTEGER PK         │  자동 증가 고유번호                      │

│  week_date             │  DATE (UNIQUE)      │  2026-04-21  (해당 주 화요일 날짜)  │

│  price_usd             │  REAL               │  3.20  ($/GB)                               │

│  price_source          │  TEXT               │  "customs_asp"  수집 출처 코드       │

│  raw_export_usd        │  REAL               │  4,820,000,000  (관세청 수출금액 $)  │

│  raw_weight_kg         │  REAL               │  1,506,250,000  (수출중량 kg)          │

│  wow_change_pct        │  REAL               │  +2.5  (전주 대비 변동률 %)            │

│  created_at            │  DATETIME           │  2026-04-22 06:05:00                    │

└─────────────────┴─────────────┴─────────────────┘

인덱스: week_date (조회 성능 최적화)

- 테이블 ② proxy_signals — 14개 프록시 신호 주간 점수
┌─────────────────┬─────────────┬─────────────────┐

│  컬럼명                 │  타입                │  설명 / 예시값                             │

├─────────────────┼─────────────┼─────────────────┤

│  id                    │  INTEGER PK         │  자동 증가 고유번호                      │

│  week_date             │  DATE               │  2026-04-21                                │

│  signal_code           │  TEXT               │  "A1", "A2", ... "B7"  (14개)             │

│  signal_name           │  TEXT               │  "대만 공급망 지표"                      │

│  group_type            │  TEXT               │  "A" (정형) 또는 "B" (비정형)           │

│  raw_value             │  TEXT               │  "8.2" / "+0.81" / "102.4"               │

│  raw_unit              │  TEXT               │  "%" / "점수" / "지수" / "$/lb"         │

│  score                 │  REAL               │  -1.0 ~ +1.0  (정규화된 신호 점수)   │

│  signal_label          │  TEXT               │  "positive" / "neutral" / "negative"    │

│  alert_flag            │  BOOLEAN            │  TRUE  (A4가 100 초과 시 Red Alert)│

│  confidence            │  REAL               │  0.87  (신뢰도 0~1)                       │

│  ai_reason             │  TEXT               │  Claude 생성 한국어 해석 텍스트     │

│  source_url            │  TEXT               │  수집 출처 URL 또는 API 엔드포인트 │

│  created_at            │  DATETIME           │  2026-04-22 06:10:00                    │

└─────────────────┴─────────────┴─────────────────┘

인덱스: (week_date, signal_code) — 복합 UNIQUE 제약

비고: 매주 14개 행 생성 (signal_code × week_date = 1개 행)

- 테이블 ③ news_articles — 뉴스/문서 + Claude 분석
┌───────────────┬─────────────┬─────────────────┐

│  컬럼명          │  타입                   │  설명 / 예시값                            │

├───────────────┼─────────────┼─────────────────┤

│  id             │  INTEGER PK         │  자동 증가 고유번호                    │

│  collected_week │  DATE                   │  2026-04-21  (수집 기준 주)          │

│  published_at   │  DATETIME           │  2026-04-21 09:30:00  (기사 발행일)│

│  title_original │  TEXT           │  영문/번체 원문 제목                   │

│  title_korean   │  TEXT           │  Claude 번역 한국어 제목             │

│  source_name    │  TEXT           │  "Reuters" / "TechNews.tw"           │

│  source_url     │  TEXT           │  원문 기사 URL                          │

│  signal_code    │  TEXT           │  "B1"~"B7"  (연관 신호 코드)         │

│  content_summary│  TEXT           │  Claude 생성 한국어 요약 3~5문장│

│  sentiment_score│  REAL           │  -1.0 ~ +1.0                              │

│  sentiment_label│  TEXT           │  "positive" / "neutral" / "negative"  │

│  confidence     │  REAL           │  0.87  (Claude 판단 신뢰도)           │

│  impact_short   │  TEXT           │  "positive"  (1~4주 영향 판정)       │

│  impact_medium  │  TEXT           │  "neutral"   (5~12주 영향 판정)      │

│  impact_long    │  TEXT           │  "neutral"   (13주~ 영향 판정)       │

│  impact_reason  │  TEXT           │  Claude 생성 영향 근거 텍스트       │

│  related_signals│  TEXT           │  "A4,B4"  (연관 신호 코드 목록)      │

│  url_hash       │  TEXT (UNIQUE)  │  URL MD5 해시 (중복 수집 방지)     │

│  created_at     │  DATETIME       │  2026-04-22 06:15:00                   │

└───────────────┴──────────────┴────────────────┘

인덱스: url_hash (중복 방지), collected_week, signal_code

- 테이블 ④ global_events — 글로벌 이벤트
┌───────────────┬──────────────┬────────────────┐

│  컬럼명          │  타입            │  설명 / 예시값                            │

├───────────────┼──────────────┼────────────────┤

│  id             │  INTEGER PK     │  자동 증가 고유번호                    │

│  collected_week │  DATE           │  2026-04-21                              │

│  event_date     │  DATE           │  2026-04-21  (이벤트 발생일)        │

│  event_type     │  TEXT           │  "war" / "earthquake" / "typhoon"  │

│                 │                 │  "strike" / "bankruptcy" / "policy"   │

│  region         │  TEXT           │  "대만" / "미국" / "중국"               │

│  title          │  TEXT           │  이벤트 제목                             │

│  summary        │  TEXT           │  Claude 생성 한국어 요약             │

│  risk_level     │  TEXT           │  "high" / "medium" / "low"           │

│  dram_impact_   │  TEXT           │  "negative"  (공급/수요/가격 방향)  │

│    direction    │                 │                                               │

│  impact_short   │  TEXT           │  "negative"  (1~4주)                   │

│  impact_medium  │  TEXT           │  "neutral"   (5~12주)                   │

│  impact_long    │  TEXT           │  "positive"  (13주~)                    │

│  impact_reason  │  TEXT           │  Claude 생성 근거 텍스트             │

│  affected_      │  TEXT           │  "A1,B4"  (영향 받는 신호 코드)      │

│    signals      │                 │                                               │

│  source_urls    │  TEXT           │  관련 뉴스 URL 목록 (JSON 배열)   │

│  created_at     │  DATETIME       │  2026-04-22 06:20:00                  │

└───────────────┴──────────────┴────────────────┘

인덱스: collected_week, risk_level, event_type

- 테이블 ⑤ predictions — AI 예측 결과
┌───────────────┬──────────────┬────────────────┐

│  컬럼명          │  타입            │  설명 / 예시값                           │

├───────────────┼──────────────┼────────────────┤

│  id             │  INTEGER PK     │  자동 증가 고유번호                    │

│  generated_week │  DATE           │  2026-04-22  (예측 생성 주)          │

│  horizon_weeks  │  INTEGER        │  7  또는  21                              │

│  weekly_forecasts│ TEXT           │  JSON 배열: 주차별 예측값 상세     │

│                 │                 │  [{"week":1,"date":"2026-04-28",     │

│                 │                 │    "predicted":3.28,                      │

│                 │                 │    "lower":3.20,"upper":3.36}, ...].     │

│  final_predicted│  REAL           │  3.65  (최종 주차 예측값)              │

│  final_lower    │  REAL           │  3.40  (최종 신뢰구간 하단)           │

│  final_upper    │  REAL           │  3.90  (최종 신뢰구간 상단)           │

│  signal_contrib │  TEXT           │  JSON: 신호별 기여도                 │

│                 │                 │  {"A2":0.28,"B1":0.22,"A7":0.18...}.     │

│  ai_summary     │  TEXT           │  Claude 생성 종합 판단 텍스트      │

│  model_version  │  TEXT           │  "prophet_v2.1"                          │

│  model_confidence│ REAL           │  0.81  (전체 신뢰도)                     │

│  actual_price   │  REAL (NULL)    │  NULL → 해당 주 도래 시 자동 채움│

│  accuracy_pct   │  REAL (NULL)    │  NULL → actual_price 입력 후 계산 │

│  created_at     │  DATETIME       │  2026-04-22 06:25:00                  │

└───────────────┴──────────────┴────────────────┘

인덱스: (generated_week, horizon_weeks) — 복합 UNIQUE 제약

- 테이블 ⑥ graph_rag_results — 구리↔DRAM 상관관계
┌───────────────┬──────────────┬────────────────┐

│  컬럼명          │  타입             │  설명 / 예시값                           │

├───────────────┼──────────────┼────────────────┤

│  id             │  INTEGER PK     │  자동 증가 고유번호                    │

│  analysis_week  │  DATE (UNIQUE)  │  2026-04-22  (분석 기준 주)          │

│  analysis_weeks │  INTEGER        │  104  (분석에 사용된 주 수)           │

│  correlation_   │  REAL           │  +0.72  (피어슨 상관계수)             │

│    coeff        │                 │                                               │

│  optimal_lag_wk │  INTEGER        │  10  (최적 선행 시차, 주)              │

│  lag_analysis   │  TEXT           │  JSON: 시차별 상관계수               │

│                 │                 │  {"4":0.51,"6":0.64,"8":0.69,...}          │

│  causality_paths│  TEXT           │  JSON: 인과관계 경로 및 기여도    │

│                 │                 │  [{"path":"PCB 기판 원가",             │

│                 │                 │    "lag_weeks":"4~6",                   │

│                 │                 │    "contribution":0.42}, ...]             │

│  current_copper │  REAL           │  4.82  (현재 구리 가격 $/lb)          │

│  copper_change_ │  REAL           │  +8.3  (구리 변동률 %)                │

│    pct          │                 │                                              │

│  dram_forecast_ │  TEXT           │  "6~8% 상승 가능"                     │

│    impact       │                 │                                           │

│  ai_insight     │  TEXT           │  Claude 생성 현재 시사점 텍스트   │

│  confidence     │  REAL           │  0.74                                       │

│  created_at     │  DATETIME       │  2026-04-22 06:28:00                  │

└───────────────┴──────────────┴────────────────┘

- 테이블 ⑦ collection_logs — 수집 작업 로그
┌───────────────┬──────────────┬─────────────────┐

│  컬럼명          │  타입            │  설명 / 예시값                              │

├───────────────┼──────────────┼─────────────────┤

│  id             │  INTEGER PK     │  자동 증가 고유번호                      │

│  run_week       │  DATE           │  2026-04-22  (실행 기준 주)             │

│  task_name      │  TEXT           │  "collect_A1" / "sentiment_B4"          │

│                 │                 │  "run_prophet" / "graph_rag"           │

│  signal_code    │  TEXT (NULL)    │  "A1" ~ "B7"  (해당되는 경우)           │

│  status         │  TEXT           │  "success" / "failed" / "partial"          │

│  records_added  │  INTEGER        │  42  (새로 저장된 데이터 건수)         │

│  tokens_used    │  INTEGER (NULL) │  1240  (Claude API 토큰 사용량)       │

│  duration_sec   │  REAL           │  12.4  (작업 소요 시간 초)               │

│  error_message  │ TEXT (NULL)    │  NULL 또는 오류 내용 전문              │

│  retry_count    │  INTEGER        │  0 / 1 / 2  (재시도 횟수)                 │

│  created_at     │  DATETIME       │  2026-04-22 06:05:12                     │

└───────────────┴──────────────┴─────────────────┘

인덱스: run_week, task_name, status

- 테이블 간 관계 요약
dram_prices ───────────────────────────────────┐

(실제 주간 DRAM 가격)                                    │

▼

proxy_signals ──────────────────────────► predictions

(14개 신호 주간 점수)        신호 점수를    (1~7주/8~21주 예측)

Prophet 피처로  │

news_articles ──► proxy_signals              │

(뉴스 감성 → B군 점수에 반영)               │

▼

graph_rag_results ──────────────► 예측 보정 입력값

(구리↔DRAM 선행 분석)               구리 선행 효과를 예측에 반영

global_events ────────────────────────────────────

(이벤트 리스크)              독립 참조 (예측 미반영, UI 표시용)

collection_logs ───────────────────────────────────

(모든 작업 성공/실패 기록)   독립 모니터링

### 데이터 흐름 (Data Flow)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

매주 화요일 새벽 6:00  APScheduler 자동 트리거

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 1 : 데이터 수집 (06:00 ~ 06:15, 병렬 실행)

┌─────────────────────────────────────────────────┐

│  [Group A 정형 7종]             [Group B 비정형 7종]      │

│                                                         │

│  A1: yfinance API 호출             B1: FMP API 호출          │

│  A2: SEC EDGAR API 호출         B2: TechNews RSS 파싱     │

│  A3: 관세청 Open API 호출       B3: Reddit PRAW 수집       │

│  A4: KOSIS Open API 호출        B4: GDELT API 호출         │

│  A5: AWS Price API 호출          B5: TechNews 크롤링        │

│  A6: Polymarket API 호출        B6: IR PDF 다운+파싱       │

│  A7: FRED API 호출                B7: OCP RSS 파싱           │

│                                                         │

│  ※ 각 수집 결과 → collection_logs 에 성공/실패 즉시 기록  │

│  ※ httpx 비동기로 최대한 병렬 실행하여 시간 단축          │

└──────────────────────────┬──────────────────────┘

│

▼ 수집 완료 데이터

PHASE 2 : AI 감성 분석 (06:15 ~ 06:22, Claude API 호출)

┌─────────────────────────────────────────────────┐

│  수집된 B군 비정형 텍스트 → Claude API 일괄 전송          │

│                                                         │

│  ① url_hash 확인 → 이미 분석된 기사 스킵 (중복 방지)      │

│  ② 신규 기사/문서만 Claude에게 전송                       │

│     프롬프트: "DRAM 가격 관점에서 -1~+1 점수를 매겨줘"    │

│  ③ 응답 파싱 → sentiment_score, summary, impact 추출    │

│  ④ news_articles 테이블 저장                             │

│  ⑤ 토큰 사용량 → collection_logs.tokens_used 기록        │

│                                                         │

│  A군 정형 데이터 → 규칙 기반 점수화 (Claude 불필요)        │

│    예) A4: 재고÷출하×100 → 100 초과 시 score=-0.8        │

│        A7: 구리 전주 대비 % → 정규화 후 점수 변환         │

└──────────────────────────┬──────────────────────┘

│

▼ 14개 신호 점수 (-1~+1) 완성

PHASE 3 : 신호 점수 저장 & 검증 (06:22 ~ 06:24)

┌─────────────────────────────────────────────────┐

│  proxy_signals 테이블에 14개 신호 × 1주 = 14행 저장      │

│                                                         │

│  데이터 품질 검증:                                       │

│  · 14개 중 10개 이상 수집 성공 시 → 예측 진행            │

│  · 10개 미만 성공 시 → 예측 보류, 관리자 경고 로그 기록  │

│  · 이상값 검출: 전주 대비 ±50% 초과 시 플래그 표시       │

└──────────────────────────┬──────────────────────┘

│

▼ 검증 완료 신호 점수

PHASE 4 : AI 예측 실행 (06:24 ~ 06:28)

┌─────────────────────────────────────────────────┐

│  Prophet 모델 입력 준비:                                 │

│  · dram_prices 52주 히스토리 (y 변수)                   │

│  · proxy_signals 14개 점수 (외부 회귀 변수)              │

│  · graph_rag_results 구리 선행 효과 (lag 10주 보정)      │

│                                                         │

│  Prophet 실행 → 7주 예측 + 21주 예측 각각 생성           │

│  · 주별 예측값 (1주~7주, 1주~21주)                       │

│  · 신뢰구간 상단/하단                                    │

│  · 신호별 기여도 계산 (permutation importance)           │

│                                                         │

│  Claude API → 종합 판단 텍스트 자동 생성                  │

│  predictions 테이블 저장                                  │

│                                                         │

│  과거 예측 정확도 자동 업데이트:                          │

│  · 오늘 실제 DRAM 가격 확인                              │

│  · 해당 주 예측값의 actual_price, accuracy_pct 채움      │

└──────────────────────────┬──────────────────────┘

│

▼

PHASE 5 : Graph RAG 업데이트 (06:28 ~ 06:30)

┌─────────────────────────────────────────────────┐

│  구리 104주 vs DRAM 104주 시계열 로드                    │

│  scipy로 시차별(4·6·8·10·12·16주) 상관계수 재계산        │

│  networkx로 인과관계 그래프 업데이트                      │

│  Claude → 현재 시사점 텍스트 생성                        │

│  graph_rag_results 테이블 저장                           │

└──────────────────────────┬──────────────────────┘

│

▼ 전체 파이프라인 완료 (06:30)

PHASE 6 : API 서빙 (상시)

┌─────────────────────────────────────────────────┐

│  FastAPI (Uvicorn) → SQLite에서 데이터 조회              │

│  → React 프론트엔드에 JSON 응답                          │

│                                                         │

│  주요 API 엔드포인트:                                    │

│  GET /api/dashboard/summary    메인 대시보드 전체 요약    │

│  GET /api/predictions/{weeks}  7주 또는 21주 예측        │

│  GET /api/signals              14개 신호 현황            │

│  GET /api/signals/{code}       개별 신호 상세            │

│  GET /api/news                 뉴스 목록                 │

│  GET /api/news/{id}            뉴스 상세                 │

│  GET /api/events               글로벌 이벤트 목록         │

│  GET /api/graph-rag            구리↔DRAM 분석            │

│  GET /api/accuracy             예측 정확도 이력           │

│  GET /api/collection/status    수집 현황                 │

└─────────────────────────────────────────────────┘

### 비기능 요구사항

- NFR-01. 성능 (Performance)
항목                          목표값          측정 기준

──────────────────────────────────────────────────────

API 응답 시간                 ≤ 2초           P95 기준

메인 대시보드 초기 로딩         ≤ 3초           브라우저 기준

차트 렌더링 (Plotly)           ≤ 1초           52주 데이터 기준

전체 수집 파이프라인 완료       ≤ 30분          06:00 ~ 06:30

Claude API 호출 1건 응답       ≤ 10초          단일 뉴스 분석 기준

Prophet 예측 실행              ≤ 60초          104주 데이터 기준

- SQLite 인덱스 최적화: week_date, signal_code, url_hash 필수
- TanStack Query로 프론트엔드 데이터 캐싱 (5분 TTL)
- FastAPI 응답 캐싱: 동일 주 데이터 반복 조회 시 메모리 캐시 활용

- NFR-02. 신뢰성 (Reliability)
항목                          내용

───────────────────────────────────────────────────────

수집 실패 재시도               최대 3회 자동 재시도 (간격: 5분)

부분 수집 허용                 14개 중 10개 이상 성공 시 예측 진행

이전 주 데이터 폴백            수집 완전 실패 시 직전 주 값 유지

예측 보류 기준                 10개 미만 신호 수집 시 예측 미실행

수집 로그 보존                 collection_logs 90일 이상 보존

DB 자동 백업                  매주 수집 전 dram_sixsense.db 백업본 생성

- 각 수집 작업을 독립 try/except로 감싸 — 1개 실패가 전체를 막지 않음
- 수집 파이프라인 실패 시 collection_logs에 오류 내용 전문 기록
- 프론트엔드: API 오류 시 마지막 성공 데이터 + 오류 배너 동시 표시

- NFR-03. 데이터 품질 (Data Quality)
항목                          처리 방법

──────────────────────────────────────────────────────

중복 수집 방지                news_articles.url_hash UNIQUE 제약

이상값 감지                   전주 대비 ±50% 초과 시 플래그 표시

결측값 처리                   직전 주 값으로 보간 (Prophet forward-fill)

Claude 재분석 방지             url_hash로 이미 분석된 기사 스킵

신호 점수 정규화              모든 raw_value → -1~+1 표준화 후 저장

데이터 신선도 표시             마지막 업데이트 시각 항상 UI 상단 표시

- NFR-04. 보안 (Security)
항목                          처리 방법

───────────────────────────────────────────────────────

중복 분석 방지                url_hash로 기분석 기사 재분석 차단

주간 토큰 예산 설정           주당 최대 토큰 수 .env에서 설정 가능

토큰 사용량 기록              collection_logs.tokens_used 매회 기록

프롬프트 최적화               기사 본문 대신 제목+요약만 전송 (압축)

배치 처리                     기사 개별 호출 → 최대 5건 묶어 배치 호출

예산 초과 방지                주간 누적 토큰이 한도 80% 도달 시 경고 로그

- NFR-05. Claude API 비용 관리
항목                          처리 방법

──────────────────────────────────────────────────────

중복 분석 방지                url_hash로 기분석 기사 재분석 차단

주간 토큰 예산 설정           주당 최대 토큰 수 .env에서 설정 가능

토큰 사용량 기록              collection_logs.tokens_used 매회 기록

프롬프트 최적화               기사 본문 대신 제목+요약만 전송 (압축)

배치 처리                     기사 개별 호출 → 최대 5건 묶어 배치 호출

예산 초과 방지                주간 누적 토큰이 한도 80% 도달 시 경고 로그

- NFR-06. 외부 API 준수 (Rate Limiting)
API                  무료 제한                  대응 방법

───────────────────────────────────────────────────────

FRED API            120 req/분                 주 1회 수집으로 여유

KOSIS API            10,000 req/일              주 1회 수집으로 여유

관세청 API            1,000 req/일              주 1회 수집으로 여유

Reddit PRAW          60 req/분                  크롤링 간 1초 대기

FMP (무료)            250 req/일                최소 필요 항목만 요청

SEC EDGAR            10 req/초                  httpx rate limiter 적용

yfinance             비공식 (과부하 주의)         수집 간 2초 대기

TechNews 크롤링       명시적 제한 없음            robots.txt 확인, 3초 대기

- httpx 비동기 클라이언트에 asyncio.sleep() 및 rate limiter 적용
- robots.txt 자동 확인 후 크롤링 허용 여부 검증

- NFR-07. 유지보수성 (Maintainability)
항목                          처리 방법

──────────────────────────────────────────────────────

신호 추가 용이성              signal_code 기반 플러그인 구조

새 신호 추가 시 수집 함수 1개만 추가

모델 버전 관리                predictions.model_version 컬럼 기록

설정 중앙화                   .env + pydantic-settings 단일 관리

API 문서 자동 생성            FastAPI Swagger UI (/docs) 항상 접근 가능

오류 메시지 명확화            collection_logs.error_message 전문 기록

코드 구조 표준화              FastAPI 라우터 → 서비스 → DB 3계층 분리

- NFR-08. 확장성 (Scalability)
항목                          현재 → 미래 확장 경로

───────────────────────────────────────────────────────

DB 확장                       SQLite → PostgreSQL (SQLAlchemy 코드 무변경)

배포 확장                     로컬 Docker → Railway/Render 클라우드 배포

신호 확장                     14개 → 20개 이상 추가 용이한 구조

사용자 확장                   단일 사용자 → 로그인 추가 시 FastAPI Auth 추가

예측 모델 교체               Prophet → 더 고도화된 모델로 교체 가능

- NFR-09. 운영 모니터링 (Observability)
항목                          처리 방법

───────────────────────────────────────────────────────

수집 현황 UI                  S-014 화면에서 성공/실패 상태 시각화

수집 완료 알림                성공/실패 시 터미널 로그 + 색상 출력

오류 추적                     collection_logs 테이블로 전체 이력 추적

API 상태 확인                 GET /api/health — 서버 상태 즉시 확인

수집 소요시간 기록             collection_logs.duration_sec 매 작업 기록

Claude 비용 추적              주간 토큰 합계 대시보드 하단 표시

- 비기능 요구사항 전체 요약
┌─────┬─────────────────────────┬──────────────────┐

│  코드   │  분류                                  │  핵심 목표                                   │

├─────┼─────────────────────────┼──────────────────┤

│ NFR-01. │ 성능                     │ API ≤2초, 파이프라인 ≤30분           │

│ NFR-02 │ 신뢰성                   │ 수집 실패 재시도 3회, 폴백 처리       │

│ NFR-03 │ 데이터 품질               │ 중복 방지, 이상값 감지, 정규화         │

│ NFR-04 │ 보안                     │ .env 키 관리, DB Git 제외                │

│ NFR-05 │ Claude API 비용 관리      │ 중복 분석 차단, 토큰 예산 설정         │

│ NFR-06 │ 외부 API 준수            │ Rate limit 준수, robots.txt 확인          │

│ NFR-07. │ 유지보수성               │ 플러그인 구조, 3계층 코드 분리         │

│ NFR-08. │ 확장성                   │ SQLite→PostgreSQL 무변경 마이그레이션│

│ NFR-09. │ 운영 모니터링            │ 수집 현황 UI, 비용 추적, 상태 API        │

└─────┴──────────────────────────┴──────────────────┘

## 09. 데이터 확보 방안

[Group A: 정형 데이터 - 수요 및 공급 모듈]

- 대만 공급망 지표 (MOPS 데이터):
- 수집 대상: 종목코드 5274(ASPEED), 2382(Quanta), 6669(Wiwynn)의 주별 매출(Net Sales) 및 YoY 증감률.
- 기능: Yahoo Finance API (yfinance) 활용. ASPEED(5274.TW), Quanta(2382.TW), Wiwynn(6669.TW)의 재무 데이터를 API로 무료 자동 호출. XBRL 파싱 + LLM 보조 parsing

- 빅테크 CapEx 및 CPU 매출 (SEC EDGAR):
- 수집 대상: MSFT, GOOGL의 10-Q 내 현금흐름표 상 'Purchases of property and equipment'. INTC, AMD의 데이터센터 부문 매출.
- 기능: SEC EDGAR RESTful API (공식) 사용(무료). 세부 매출은 SEC API로 10-Q 텍스트를 긁어온 뒤, LLM(Gemini 등)을 연결해 'Data Center Revenue' 숫자만 추출하도록 파이프라인 구축.
- 한국 관세청 수출 평균 단가 (ASP):
- 수집 대상: HS코드 854232(메모리 반도체)의 월별 수출중량 및 수출금액.
- 기능: 수출금액 ÷ 수출중량 수식을 통해 킬로그램당 달러 가격을 역산하고 메인 가격 차트로 플로팅.
- 한국 통계청 재고/출하 지수:
- 수집 대상: KOSIS 제조업 반도체 품목의 월별 재고지수 및 출하지수.
- 기능: (재고지수 ÷ 출하지수) × 100 수식을 계산하여 이 수치가 100을 돌파할 때 대시보드에 'Red Alert(공급 과잉)' 경고 띄움.
- KOSIS Open API
- 클라우드 유휴 서버(AWS Spot):
- 수집 대상: AWS EC2 스팟 인스턴스 (r5, r6 계열) 과거 3개월 요금.
- 기능: AWS Price API를 연동하여 특정 리전의 가격 우상향 추세 렌더링.
- 폴리마켓 (Polymarket API):
- 수집 대상: Nvidia earnings, Fed rate cut, Taiwan blockade 관련 마켓의 'Yes' 토큰 가격.
- 기능: Polymarket CLOB API를 연동해 3개 지표의 주간 평균 확률(%)을 대시보드 하단에 게이지 바 형태로 표시.
- 구리 가격 시계열 (정형):
- 수집 대상: FRED (Federal Reserve Economic Data) API. 티커 PCOPPUSDM (글로벌 구리 가격) - 100% 무료 자동화.

[Group B: 비정형 데이터 - 자연어 처리(NLP) 및 점수화 모듈]

- Earnings Call 센티먼트 분석:
- 수집 대상: MSFT, GOOGL, MU, SK Hynix 실적 발표 대본(시킹알파 등).
- 기능: Financial Modeling Prep (FMP) 무료 티어 API 활용(분기별 트랜스크립트 제공) 또는 Motley Fool 크롤링. 감성 분석은 단순 룰베이스가 아닌 LLM 프롬프트로 처리.
- 대만 뉴스 플로우 스코어링:
- 수집 대상: Digitimes Server 섹션 헤드라인.
- 기능: TechNews.tw (무료) 웹사이트 RSS 피드 활용. LLM에 기사 내용을 던져 "서버 수요 관점에서 -1 ~ +1 점수를 매겨줘"라고 바이브 코딩.
- 직장인 커뮤니티 마이닝 (수동 업로드 지원):
- 기능: Reddit (r/hardware, r/semiconductors) 의 무료 API(PRAW) 활용. "yield", "fab utilization" 등의 키워드로 글로벌 엔지니어들의 동향 자동 수집.
- 지정학적 리스크 플래그 (Google News API):
- 수집 대상: "BIS" AND "Export Controls" AND "China" 뉴스 볼륨.
- 기능: GDELT Project API 활용. 전 세계 뉴스를 실시간 데이터베이스화하는 무료 플랫폼. "Export Control", "China", "Semiconductor" 쿼리로 볼륨 트래킹.
- LTA(Long Term Agreement) 비율 추정치
- 수집 대상: 대만 현지 IT 전문 매체의 '주문(訂單)', '예약/풀가동(滿載)', 'CoWoS' 관련 기사 볼륨 및 긍/부정 뉘앙스.
- 접속 및 검색: TechNews.tw 웹사이트 상단 검색창에 번체자 키워드를 입력합니다. LTA/주문 관련 검색어: "伺服器 訂單" (서버 주문), "CoWoS 滿載" (CoWoS 풀가동/예약완료)
- 기사 필터링: 주 1회, 최근 1주일간 올라온 해당 키워드의 기사 제목과 요약문을 크롤링(또는 복사)합니다.
- HBM/D램간 이익율 및 캐파 할당 비율 추청치
- TSMC의 CoWoS 증설 관련 뉴스(TechNews)와 주요 벤더의 IR 자료 PDF를 자동 다운로드하여 LLM 문서 파싱 기법으로 "HBM vs Legacy" 뉘앙스 점수화.
- 서버 BOM 및 원자재 언급 텍스트 (비정형):
- OCP (Open Compute Project) 블로그 및 백서 RSS 피드 (데이터센터 인프라 트렌드).
- 주요 서버 ODM(Quanta, Wiwynn) 및 쿨링업체(Vertiv)의 Earnings Call 트랜스크립트 (원자재 비용 압박 언급 추출).
- 데이터센터 전력 인프라 관련 영문 뉴스 RSS.
- 주체별 재고일수 및 주요 분석 기관의 코멘트와 제조사 가동률 (비정형):
- DART 오픈 API 기반 삼성전자·SK하이닉스 분기별 재고자산 자동 수집 및 정형화
- 조사기관 코멘트 및 가동률 : 구글 알리미(TrendForce, Counterpoint 키워드) RSS 피드 실시간 파싱
- 국내외 IT 매체의 서버용 DRAM 가동률 및 스팟 시장 관련 기사 본문 크롤링
- 저작권·개인정보: [저작권 및 개인정보 포함 정보는 수집 금지]

## 10. 구현 방안 및 일정

디자인 핸드오프가 완료된 상태에서, 14개 화면을 위험도와 의존성 순으로 구현한다. 각 Phase 종료 시점에 실행 가능한(deployable) 산출물을 확보한다.

### 10.1 Phase 계획

| Phase | 기간 | 목표 | 산출물 / 완료 조건 |
| --- | --- | --- | --- |
| Phase 0 — 기반 | 1주차 | 프로젝트 셋업 + 디자인 시스템 구축 | React+TS 프로젝트, 디자인 토큰(CSS 변수) 이식, 공유 컴포넌트 8종(Sig, MetricCard, LineChart, Modal, Tabs, Seg, HITL, AiNote) 구현, Storybook 등록 |
| Phase 1 — 메인 대시보드 | 2주차 | S-001 메인 화면 + mock 데이터 연결 | S-001 완성, 라우팅·테마·밀도 토글 작동, mock API 응답으로 화면 검증 |
| Phase 2 — 예측 드릴다운 | 3주차 | S-002, S-003, S-004, S-005, S-009 모달 | 차트 점 클릭/카드 클릭으로 모달 진입, 모달 스택 작동, 딥링크 URL 작동 |
| Phase 3 — 분석 페이지 + 뉴스/이벤트 | 4주차 | S-006, S-007, S-008, S-010, S-011 | 필터/정렬, 페이지네이션, 모달 위 모달 스택 |
| Phase 4 — 정확도/수집 + HITL 연동 | 5주차 | S-012, S-013, S-014 + HITL 백엔드 연동 | MAPE 차트, `POST /api/hitl/rules` 정상 동작, 수정 전후 비교 결과 표시 |
| Phase 5 — 데이터 파이프라인 통합 | 6주차 | mock → 실제 API 전환 | 매주 화 06:00 KST 자동 수집 사이클 작동, S-014에 실측 표시 |
| Phase 6 — 검증·튜닝·발표 | 7주차 | KPI 측정 + 시연 자료 준비 | §11 KPI 측정, 사용자 테스트, 발표 데모 시나리오 확정 |

### 10.2 의존성 다이어그램

```
Phase 0 (기반) ──┬──> Phase 1 (S-001) ──┬──> Phase 2 (드릴다운 모달)
                 │                       └──> Phase 3 (분석 페이지)
                 │                                    │
                 └──> Phase 5 (실제 데이터) <─────────┘
                                                      │
                                              Phase 4 (HITL)
                                                      │
                                              Phase 6 (검증)
```

### 10.3 Phase별 위험 요소

- **Phase 0**: SVG 라인차트 → Recharts 마이그레이션 시 신뢰구간 밴드(`polygon` opacity) 재현 난이도 → 핸드오프의 `LineChart` 구현(특히 band 스택) 정독 후 진행
- **Phase 1**: 차트 범위 필터(`short`/`mid`/`all`)의 시각 강조 규칙 → 디자인 토큰 그대로 사용
- **Phase 2**: 모달 스택 + 딥링크 URL 동기화 → URL 파라미터 인코딩 표준 사전 합의
- **Phase 4**: HITL 저장 시 재학습 트리거의 응답 시간 → UI에는 비동기 큐 상태(`processing` → `done`) 표시 필요
- **Phase 5**: 14신호의 수집 실패 fallback (이전 주 값 사용? 보간?) → 백엔드와 사전 합의

## 11. 성과 측정 방법 (KPI)

| KPI | 목표 값 |
| --- | --- |
| [업무 시간 절감률] | [≥ 70 %] |
| [정확도] | [≥ 80 %] |
| [사용자 수정률] | [≤ 10 %] |
| [API 응답 시간 p95] | [≤ 60 ms] |
| [비용절감규모] |  |
| [부가수익창출규모] |  |

모두 기계가 측정 가능한 숫자로 기재합니다.

## 12. 팀원별 역할 분담

디자인 핸드오프 기준으로 작업 단위를 재정의한다. 각자가 단독 PR을 만들 수 있도록 디렉토리 경계를 명확히 분리한다.

| 팀원 | 역할 | 담당 화면/모듈 | 담당 PRD 섹션 | Git 커밋 범위 |
| --- | --- | --- | --- | --- |
| 김영석 (Dataiku Korea, 프로젝트 리드) | PM·발표·데모 + 디자인 시스템 가드 | Phase 0 디자인 토큰/공유 컴포넌트, S-001 통합 책임 | 1, 2, 3, 6, 7, 10, 11 | `docs/`, `frontend/design-system/`, `frontend/pages/dashboard/` |
| 주광철 (엔코아에너텍, 개발 리드) | 백엔드 + 데이터 파이프라인 + HITL | §15 API 12개 + `POST /api/hitl/rules`, §9 데이터 수집 자동화, S-014 백엔드 | 5, 8, 9, 13(인프라), 15 | `backend/`, `pipelines/`, `infra/` |
| 김정일 (SK hynix, 현업 사용자) | 프론트엔드 화면 구현 + 도메인 검증 | S-002~S-013 (모달 + 분석 페이지), 도메인 신호 정의 검수 | 4, 14(컴포넌트), 16(디자인 토큰), 17(데이터 스키마) | `frontend/pages/`, `frontend/components/screens/` |

### 12.1 협업 규칙

- **디자인 핸드오프 SSOT**: 시각 명세에 이견이 있을 경우 `design_handoff_sixsense_dram_dashboard/`의 산출물이 최종 결정권을 가진다. PR에서 디자인 차이를 발견하면 김영석에게 리뷰 요청.
- **API 스펙 SSOT**: §15 API 엔드포인트 명세에 따른다. 백엔드(주광철)는 OpenAPI 스펙을 `backend/openapi.yaml`로 발행, 프론트엔드(김정일)는 이로부터 TypeScript 타입을 생성한다.
- **mock → 실측 전환**: Phase 5 이전까지 프론트엔드는 `frontend/mocks/` 디렉토리의 mock 응답을 사용. 환경변수 `VITE_USE_MOCK=true|false`로 토글.
- **PR 리뷰 정책**: 모든 PR은 다른 1인 이상의 승인 필요. 디자인 변경 동반 PR은 김영석 필수 승인.


---

## 13. 기술 스택 (Tech Stack)

디자인 핸드오프의 권장 사항을 기준으로 한다. 핸드오프 코드는 브라우저 인라인 Babel 기반의 참조 구현이며, 프로덕션에서는 아래 스택으로 재작성한다.

### 13.1 프론트엔드

| 영역 | 선택 | 비고 |
| --- | --- | --- |
| 언어 | TypeScript 5.x | 모든 컴포넌트/유틸 |
| 프레임워크 | React 18 | 핸드오프와 동일 (18.3.1) |
| 라우팅 | React Router 6 (또는 Next.js App Router) | Full page는 실제 라우트, Modal은 query param 또는 parallel route |
| 상태 관리 | TanStack Query (서버 상태) + Zustand (전역 UI 상태) | 데이터는 주간 갱신이라 캐싱 효과 큼 |
| 차트 | Recharts 또는 Visx | 핸드오프의 SVG `LineChart` API 모양을 그대로 보존하며 교체 |
| 스타일링 | CSS Modules + CSS 변수 (디자인 토큰) | 핸드오프의 `src/styles.css` 토큰 그대로 이식 |
| 폰트 | Pretendard Variable (self-hosted) + JetBrains Mono + Inter | jsdelivr CDN 의존 제거 |
| 빌드 도구 | Vite 5 | 빠른 HMR |
| 테스트 | Vitest + Testing Library + Playwright(E2E) | 핵심 14화면 스모크 테스트 |

### 13.2 백엔드

| 영역 | 선택 | 비고 |
| --- | --- | --- |
| 언어 | Python 3.11+ | 데이터 수집·전처리 친화 |
| 웹 프레임워크 | FastAPI | OpenAPI 자동 생성, async 지원 |
| AI/예측 모델 | Prophet (단기 1~7w) + LSTM/Transformer (중장기 8~21w) | `model: prophet_v2.1` 등 핸드오프 표기와 일치 |
| 감성 분석 | Anthropic Claude API (Sonnet/Opus) | 뉴스/Earnings Call 텍스트 분석, HITL 임계치 적용 |
| Graph RAG | Neo4j + LangChain | 구리↔DRAM 인과관계 그래프 |
| 데이터 저장 | PostgreSQL (시계열·메타) + S3 (원본 파일) | TimescaleDB 확장 고려 |
| 캐시 | Redis | 주간 스냅샷 캐싱 |
| 배치 스케줄러 | APScheduler 또는 Airflow | 매주 화 06:00 KST 자동 수집 |

### 13.3 데이터 수집 도구

- yfinance, SEC EDGAR API, DART OpenAPI, FRED API, RSS 피드 파서, requests + BeautifulSoup (라이선스 확인된 사이트만)

### 13.4 인프라

| 영역 | 선택 |
| --- | --- |
| 호스팅 | AWS (EC2/ECS + RDS + S3) 또는 Vercel(프론트) + Render(백엔드) |
| CI/CD | GitHub Actions |
| 모니터링 | Sentry (에러), Grafana + Prometheus (메트릭) |
| 시크릿 관리 | .env (로컬) + AWS Secrets Manager (운영) |

---

## 14. 컴포넌트 인벤토리 (Component Inventory)

디자인 핸드오프 `src/components.jsx`에 정의된 공유 컴포넌트를 프로덕션 코드베이스에 재현한다. 동일한 props 구조를 유지하여 화면 코드 변경을 최소화한다.

### 14.1 공유 컴포넌트 (모든 화면 공통)

| 컴포넌트 | 역할 | 주요 props |
| --- | --- | --- |
| `<Sig>` | 감성·위험도 배지 | `tone: pos\|neu\|neg\|alert\|info`, 자식: 라벨 |
| `<Sparkline>` | 인라인 미니 라인차트 | `data: number[]`, `tone`, `height` |
| `<MetricCard>` | 큰 숫자 카드 (가격 스냅샷용) | `label`, `code`, `value`, `unit`, `change`, `changeTone`, `sub`, `onClick` |
| `<LineChart>` | SVG/차트 라이브러리 라인차트 | `width`, `height`, `series`, `bands`, `refLines`, `xLabels`, `yDomain`, `padding` |
| `<Modal>` | 모달 쉘 (ESC/바깥클릭, 스택 지원) | `title`, `badge`(S-XXX), `onClose`, `size` |
| `<Tabs>` | 상단 탭 스트립 | `tabs: [{id, code, label}]`, `active`, `onChange` |
| `<Seg>` | 세그먼트 컨트롤 (차트 범위 등) | `options`, `value`, `onChange` |
| `<HITL>` | Human-In-The-Loop 임계치 조정 패널 | `rules: [{id, label, tone, desc, value, step, unit}]` |
| `<AiNote>` | AI 자동 생성 콜아웃 | `label`, `source`, 자식 |
| `<BarRow>` | 신호 기여도 막대 한 줄 | `rank`, `code`, `label`, `pct`, `tone` |
| `<FilterSelect>` | 드롭다운 필터 | `options`, `value`, `onChange` |
| `<SectionHead>` | 섹션 헤더 (제목 + 우측 액션) | `title`, `subtitle`, `action` |

### 14.2 화면 전용 컴포넌트

| 컴포넌트 | 위치 | 사용 화면 |
| --- | --- | --- |
| `<DramChart>` | dashboard | S-001 (범위 필터 통합) |
| `<ChartRangeSeg>` | dashboard | S-001 |
| `<SignalCard>` | dashboard | S-001 (14신호 그리드) |
| `<GraphRagMini>` | dashboard | S-001 (Graph RAG 카드) |
| 각 `<S00X>` 모달 컴포넌트 | modals | S-002, S-003, S-004, S-005, S-007, S-009, S-011, S-013 |
| 각 `<S00X>` 페이지 컴포넌트 | pages | S-006, S-008, S-010, S-012, S-014 |

### 14.3 컴포넌트 구현 우선순위 (Phase 0)

1. `<Sig>` → `<Sparkline>` → `<MetricCard>` (가장 단순하고 의존 없음)
2. `<Tabs>`, `<Seg>`, `<FilterSelect>`, `<SectionHead>`
3. `<LineChart>` (Recharts 기반 재작성, 신뢰구간 밴드 주의 §10.3)
4. `<Modal>` (모달 스택 + ESC + body scroll lock)
5. `<HITL>`, `<AiNote>`, `<BarRow>`

---

## 15. API 엔드포인트 명세

핸드오프 README의 데이터 페치 명세를 그대로 채택한다. 모든 응답은 JSON, 인증은 Bearer Token, CORS 허용.

### 15.1 조회(GET) 엔드포인트 — 12종

| Method | Path | 화면 | 응답 핵심 필드 |
| --- | --- | --- | --- |
| GET | `/api/snapshot` | S-001 | 현재가, 1~7w/8~21w 예측, 모델명, 신뢰도, 갱신 타임스탬프 |
| GET | `/api/history` | S-001 | 52주 가격 시계열 + forecast 신뢰구간 |
| GET | `/api/signals` | S-001 | 14신호 현재값, tone, sparkline 데이터 |
| GET | `/api/signals/:id` | S-003, S-004 | 28주 트렌드, 원본 테이블, AI 해석 |
| GET | `/api/news` | S-006 | 페이지네이션된 뉴스, 필터 지원 (sentiment, source, date) |
| GET | `/api/news/:id` | S-007 | 기사 본문, AI 요약, 단/중/장기 영향, 연결 신호 |
| GET | `/api/macro` | S-001, S-008 | 5개 거시지표 현재값, 변화, 설명 |
| GET | `/api/macro/:id` | S-008 | 52주 트렌드, 월간 원본, DRAM 상관 노트 |
| GET | `/api/events` | S-010 | 이벤트 목록, 필터 (risk, type) |
| GET | `/api/events/:id` | S-011 | 이벤트 상세, 단/중/장기 영향, 연결 뉴스/신호 |
| GET | `/api/forecast/:horizon` | S-002 | horizon=7\|21, 신호 기여도, 주별 예측 테이블, AI 요약 |
| GET | `/api/accuracy` | S-012 | 정확도 이력 페이지네이션 (filter: 7w/21w/all) |
| GET | `/api/accuracy/:date/:horizon` | S-013 | 당시 14신호 스냅샷 vs 현재 비교, 오차원인 AI 분석 |
| GET | `/api/collection` | S-014 | 신호별 출처, 마지막 수집 시각, 신규 항목 수, success/fail |

### 15.2 변경(POST) 엔드포인트

| Method | Path | 화면 | 본문 |
| --- | --- | --- | --- |
| POST | `/api/hitl/rules` | 모든 HITL 패널 | `{signalId, rules: [{id, value}], comment?}` → 임계치 저장 + 재학습 큐 등록, 응답: 수정 전후 결과 비교 |

### 15.3 공통 응답 규약

- HTTP 200: 정상 응답 (캐시 헤더 `Cache-Control: max-age=300` 권장 — 5분, 데이터는 주간 갱신)
- HTTP 401: 미인증 (프론트는 로그인 페이지로 리다이렉트)
- HTTP 429: Rate Limit 초과 (프론트는 지수 백오프 재시도)
- HTTP 503: 수집 사이클 진행 중 (S-014에 안내 표시)
- 에러 응답 본문: `{"error": "code", "message": "사용자에게 보일 한국어 메시지", "trace_id": "uuid"}`

### 15.4 캐싱 전략

- TanStack Query `staleTime`:
  - `/api/snapshot`, `/api/history`, `/api/signals`, `/api/macro`: 5분
  - `/api/news`, `/api/events`: 1분 (목록 갱신 빈도 높음)
  - `/api/accuracy`, `/api/collection`: 5분
  - `/api/forecast/:horizon`, `/api/signals/:id`, `/api/news/:id`, `/api/events/:id`: 5분
- HITL 저장 후 관련 쿼리는 `invalidateQueries`로 즉시 무효화

---

## 16. 디자인 토큰 (Design Tokens)

핸드오프 `src/styles.css` 상단의 CSS 변수 정의를 프로덕션 코드에 그대로 이식한다. 직접 값을 쓰지 말고 항상 변수 참조.

### 16.1 색상 — 라이트 테마 (기본값)

| 토큰 | 값 | 용도 |
| --- | --- | --- |
| `--bg` | `#fafaf8` | 페이지 배경 (warm white) |
| `--bg-elev` | `#f4f3ef` | 상승 영역 배경 |
| `--surface` | `#ffffff` | 카드/모달 배경 |
| `--surface-2` | `#fafaf8` | 호버, 테이블 헤더 |
| `--border` | `#e8e6e0` | 기본 보더 |
| `--border-strong` | `#d8d4cc` | 강조 보더 |
| `--text` | `#1a1a1a` | 본문 |
| `--text-mid` | `#4a4a48` | 보조 텍스트 |
| `--text-dim` | `#8a8884` | 약한 텍스트 |
| `--text-faint` | `#b8b6b0` | 가장 약한 텍스트 |
| `--accent` | `#1a1a1a` | 활성 탭 밑줄, 주요 버튼 |
| `--grid` | `#efede8` | 차트 그리드 |

### 16.2 색상 — 신호 톤 (라이트/다크 공통 의미)

| 토큰 | 라이트 | 다크 | 의미 |
| --- | --- | --- | --- |
| `--sig-pos` | `#16a34a` | `#4ade80` | 긍정 |
| `--sig-neu` | `#ca8a04` | `#fbbf24` | 중립 |
| `--sig-neg` | `#dc2626` | `#f87171` | 부정 |
| `--sig-alert` | `#b91c1c` | `#ef4444` | Red Alert (A-4 등) — 펄싱 |
| `--sig-info` | `#2563eb` | `#60a5fa` | 1~7주 예측 |
| `--forecast-mid` | `#10b981` | `#6ee7b7` | 8~21주 예측 (강조) |

> **중요**: 1~7주는 파란색 점선, 8~21주는 파스텔 그린 (`mid` 범위에서는 굵은 실선 2.6px). 두 색을 절대 섞거나 바꾸지 말 것.

### 16.3 타이포그래피

```
Sans: "Pretendard Variable", Pretendard, Inter, -apple-system, sans-serif
Mono: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace
```

| 토큰 | 값 (편안 / 컴팩트) | 용도 |
| --- | --- | --- |
| Base body | 13px / 12px | 일반 본문 |
| Big metric | 26px / 22px, weight 600 | 가격 등 큰 숫자 (.num 클래스) |
| Section title | 15px, weight 600 | 카드 섹션 헤더 |
| Page title (h1) | 22px, weight 700 | 페이지 최상단 |
| Card label | 13px, weight 500 | 카드 라벨 |
| Card-h / dlabel | 11px, weight 500, UPPERCASE, letter-spacing 0.02em | 메타 라벨 |
| Tab | 13px, weight 500 (활성 600) | 탭 라벨 |
| Button | 12px, weight 500 | 버튼 |
| Table th | 11px, weight 500, UPPERCASE | 테이블 헤더 |
| Table td | 12px | 테이블 본문 |
| Mono code small | 10px, weight 500 | 코드/식별자 |

- `word-break: keep-all` 본문 컨테이너 필수 (한글 줄바꿈 보호)
- `.num` 클래스: `font-family: var(--mono)` + `font-variant-numeric: tabular-nums` + `letter-spacing: -0.01em` + `white-space: nowrap`

### 16.4 밀도 (Density)

| 토큰 | 편안(기본) | 컴팩트 |
| --- | --- | --- |
| `--pad-x` | 20px | 14px |
| `--pad-y` | 16px | 10px |
| `--gap` | 14px | 8px |
| `--row-h` | 36px | 28px |

`<html data-density="compact">`로 토글.

### 16.5 모서리 반경 / 그림자

```
--radius-sm: 4px
--radius:    6px   (카드, 버튼, 입력 기본)
--radius-lg: 10px  (모달)

--shadow-sm: 0 1px 2px rgba(20,18,12,0.04)
--shadow:    0 2px 8px rgba(20,18,12,0.06), 0 1px 2px rgba(20,18,12,0.04)
--shadow-lg: 0 12px 40px rgba(20,18,12,0.16), 0 4px 12px rgba(20,18,12,0.08)
```

다크 테마는 순수 black + 높은 투명도 (0.4 / 0.6).

---

## 17. 데이터 스키마 (TypeScript 타입 초안)

핸드오프 `src/data.js`의 mock 데이터 구조를 기반으로 한 백엔드 응답 타입.

```typescript
// 가격 시계열
type HistoryPoint = {
  week: number;          // -51 ~ 0 (과거), 1 ~ 21 (예측)
  value: number;
  lower?: number;        // 신뢰구간 하단 (예측만)
  upper?: number;        // 신뢰구간 상단 (예측만)
  type: 'actual' | 'forecast_7' | 'forecast_21';
};

// 14개 신호
type Signal = {
  id: string;            // 'A-1' ~ 'A-7', 'B-1' ~ 'B-7'
  name: string;          // 표시 라벨 (한글)
  source: string;        // 데이터 출처
  value: string;         // 표시값 (포맷 완료)
  num: number;           // 수치 (정렬/계산용)
  tone: 'pos' | 'neu' | 'neg' | 'alert';
  spark: number[];       // 28주 스파크라인 데이터
};

// 뉴스
type News = {
  id: string;
  date: string;          // ISO 8601
  title: string;
  titleEn?: string;
  source: string;
  score: number;         // -1.0 ~ 1.0 감성 점수
  tone: 'pos' | 'neu' | 'neg';
  conf: number;          // 0.0 ~ 1.0 신뢰도
  hot: boolean;          // 메인 화면 노출 여부
  summary: string;       // AI 요약
  effects: {
    short: string;       // 단기 영향
    mid: string;         // 중기 영향
    long: string;        // 장기 영향
  };
  linked: string[];      // 연결 신호 ID
  url: string;           // 원문 링크
};

// 거시지표
type Macro = {
  id: 'fed' | 'dxy' | 'pmi' | 'usdkrw' | 'copper';
  name: string;
  value: string;
  change: number;
  tone: 'pos' | 'neu' | 'neg';
  desc: string;
  history: { date: string; value: number }[];  // 52주
};

// 이벤트
type Event = {
  id: string;
  date: string;
  title: string;
  risk: 'high' | 'mid' | 'low';
  impact: 'pos' | 'neu' | 'neg';
  summary: string;
  effects: { short: string; mid: string; long: string };
  linkedNews: string[];
  affectedSignals: string[];
};

// 예측 정확도
type AccuracyRow = {
  date: string;          // 예측 시점
  horizon: 7 | 21;
  pred: number;
  actual: number;
  errorPct: number;
  signalsSnapshot?: Signal[];  // 당시 신호 (S-013용)
};

// 수집 현황
type CollectionStatus = {
  signalId: string;
  source: string;
  lastCollected: string; // ISO 8601
  newItemsCount: number;
  weekOverWeekDelta: number;
  status: 'success' | 'fail' | 'partial';
  failReason?: string;
};

// HITL 규칙
type HITLRule = {
  id: string;            // 'pos' | 'neu' | 'neg'
  label: string;
  tone: 'pos' | 'neu' | 'neg';
  desc: string;
  value: number;         // 사용자 조정값
  step: number;          // 입력 step
  unit: string;          // 표시 단위
};
```

---

## 18. 검증 및 인수 기준 (UAT)

각 Phase 종료 시점에 다음 항목을 체크리스트로 검증한다.

### Phase 0 (디자인 시스템)
- [ ] 모든 12개 공유 컴포넌트가 Storybook에 등록되고 라이트/다크 + 편안/컴팩트 4조합에서 픽셀 단위 일치
- [ ] 한글 본문이 `word-break: keep-all`로 줄바꿈 정상
- [ ] `.num` 클래스가 모든 숫자에 적용되어 폭이 흔들리지 않음

### Phase 1 (S-001 메인)
- [ ] 핸드오프 `Sixsense.html`을 옆에 띄우고 픽셀 단위 비교 (오차 ±1px 허용)
- [ ] 차트 범위 필터 3 모드 모두 작동 (`short`/`mid`/`all`)
- [ ] 가격 카드/신호 카드 호버 시 -1px 이동 + 보더 강조 + 그림자
- [ ] 테마/밀도 토글 즉시 반영 + localStorage 영속화

### Phase 2~4 (모달/페이지)
- [ ] 모든 화면 진입 경로(클릭/URL 딥링크) 작동
- [ ] 모달 스택 ESC/바깥클릭으로 최상위만 닫힘
- [ ] HITL 패널 `저장 & 재학습` → 응답 표시 + 관련 화면 갱신

### Phase 5 (실측 통합)
- [ ] 매주 화 06:00 KST 자동 수집 실행 후 S-014에 신규 항목 표시
- [ ] 수집 실패 시 사용자에게 명확히 안내 (어떤 신호가 왜 실패했는지)

### Phase 6 (KPI)
- [ ] §11의 4개 KPI 측정 + 기준 미달 시 원인 분석 보고서 작성
