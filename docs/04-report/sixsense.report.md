# sixsense Completion Report

> **Summary**: bkit `/pdca report sixsense` 산출물. PRD→Plan→Design→Do→Analysis 전 과정 통합 보고서. KAIST CAIO 10기 6조 졸업 산출물.
>
> **Project**: Server DRAM Price 식스센스
> **Date**: 2026-05-17
> **Phase**: Report (bkit PDCA 7단계)
> **Team**: 김영석 (Dataiku Korea) · 주광철 (엔코아에너텍) · 김정일 (SK hynix)
> **Status**: ✅ MVP (UI 100%) — 백엔드 Phase 5는 향후 별도 사이클

---

## Executive Summary

### 1.1 Mission Recap

서버용 DDR5 DRAM 반도체의 주간 가격 변동을 단기(1~7주)/중장기(8~21주)로 자동 예측하고, 14개 프록시 신호·뉴스·이벤트·거시지표를 한 화면에서 분석할 수 있는 B2B 인텔리전스 대시보드를 구축한다.

### 1.2 Delivered

**프론트엔드 MVP — 14화면 전체 완성 + 디자인 핸드오프와 시각적 100% 동일**

| 영역 | 산출물 |
|------|--------|
| **문서 (PDCA 5단계)** | PRD · Plan · Design · Do · Analysis (총 5개) |
| **코드** | `frontend/` 약 3,500 LOC (React 19 + TypeScript + Vite) |
| **화면** | S-001 ~ S-014 14개 (메인 + 5 풀페이지 + 8 모달) |
| **컴포넌트** | 공유 13종 + Tweaks 12종 |
| **인터랙션** | 모달 스택, ESC/바깥클릭, 테마/밀도 토글, URL 딥링크, 차트 범위 필터 |

### 1.3 Value Delivered (4 Perspectives)

| 관점 | 정량 결과 | 정성 효과 |
|------|----------|----------|
| **Problem** (의사결정 사이클) | 매주 화 06:00 KST 1회 자동 갱신 (mock) | 사람 회의·수동 수집 시간 절감 가능성 검증 |
| **Solution** (AI 자동화) | 14신호 + 뉴스 감성 + 이벤트 통합 화면 1개 | 임원이 5분 내 시장 판단 가능 (mock 데이터로 시연 검증) |
| **Function/UX** (정보 밀도) | 14화면 hifi · 라이트/다크 + 편안/컴팩트 4조합 | 50대 임원 대상 한글 친화 UI · word-break/타이포 최적화 |
| **Core Value** (도메인 확장성) | HITL 패널로 임계치 사용자 조정 (UI 완성) | 향후 반도체 외 원자재·수요 예측에 동일 패턴 재사용 가능 |

---

## Context Anchor

| Key | Value |
|-----|-------|
| **WHY** | 반도체 가격 예측을 위한 데이터 수집·분석에 사람·시간·비용이 과다 투입되고 시장 급변에 대응 못함 |
| **WHO** | 반도체 부서 50대 임원 5명 (정우성/이병헌/장동건/이정재/조인성) |
| **RISK** | (해결됨) UI 정확성 — 핸드오프 직접 포팅 / (잔여) 백엔드 미구현 |
| **SUCCESS** | 14화면 hifi 완성 + 디자인 핸드오프 100% 동일 |
| **SCOPE** | Phase 0~4 완료 / Phase 5 미착수 / Phase 6 일부 |

---

## 1. PDCA 진행 요약

```
[PM]    📄 PRD 18 섹션 (84KB, 1,611줄)              ✅ 완료
  ↓
[Plan]  📋 Plan 10 섹션 (19KB, 326줄)               ✅ 완료
  ↓
[Design] 🏗️ Design 11 섹션 (50KB, 1,113줄)         ✅ 완료
  ↓
[Do]    🔧 Do v0.2 — 직접 포팅 가이드              ✅ 완료
        ⚠️ v0.1 폐기 (쇼케이스 → 핸드오프 포팅 전환)
  ↓
[Check] 🔍 Gap Analysis — Match Rate 60%           ✅ 완료
        UI 100% / Backend 0%
  ↓
[Act]   ⏭️ (Iteration 0회 — Critical은 Phase 5 별도) ⏭️ Skip
  ↓
[QA]    ⏭️ (Phase 6 — Playwright + Lighthouse)     ⏭️ Skip
  ↓
[Report] 📊 본 문서                                 ✅ 완료
  ↓
[Archive] ⏸️ (선택 — KAIST 제출 후 진행 가능)        ⏸️ Pending
```

---

## 2. Key Decisions & Outcomes

> Decision Record Chain 종합 — 각 결정이 어떻게 흘러갔는지

### 2.1 시장·전략 결정 (PRD 단계)

| 결정 | 결과 |
|------|------|
| Target = 50대 임원 5명 | ✅ UI 정보 밀도와 한글 처리 우선순위 결정에 활용 |
| Beachhead = 메모리·반도체 부서 | ✅ 14신호 도메인 선정 근거 |
| 파일럿 3억 이내 | ✅ Phase 단순화 (Enterprise → Dynamic) |

### 2.2 아키텍처 결정 (Plan/Design 단계)

| 결정 | 출처 | 결과 |
|------|------|------|
| Dynamic 레벨 | Plan §7.1 | ✅ 7주 일정 안전 |
| React 18 → 19 (상위호환) | Design §2 | ✅ 호환 무이슈 |
| Recharts (계획) | Plan §7.2 | ⚠️ 미사용 (핸드오프 SVG 그대로 사용) |
| FastAPI 백엔드 | Plan §7.2 | ⏸ Phase 5 대기 |
| Option C — Pragmatic Balance | Design §2 | ✅ 적합 검증됨 |

### 2.3 구현 전략 결정 (Do 단계)

| 결정 | 결과 |
|------|------|
| **v0.1: TS 컴포넌트 재구현** | ❌ **실패** — 핸드오프와 다른 쇼케이스 생성 |
| **v0.2: 핸드오프 직접 포팅** | ✅ **성공** — 시각 100% 일치 |

→ **교훈**: 디자인 핸드오프가 이미 React 코드일 경우, **재작성보다 직접 포팅이 압도적으로 효율적**. 향후 PDCA 사이클에 반영할 패턴.

### 2.4 HITL 정책 (Design 단계)

| 결정 | 결과 |
|------|------|
| 단일 공유 컴포넌트 (중복 금지) | ✅ `components.jsx` HITL 하나로 모든 상세 화면에 표시 |
| 비동기 큐 + 진행상태 UI | ⚠️ UI는 완성, 백엔드 미구현 |

---

## 3. Success Criteria Final Status

> Plan §4 + Analysis §1.2 결과 통합

### 3.1 Functional Requirements

| FR ID | 상태 | 증거 |
|-------|------|------|
| FR-01 14신호 자동 수집 | ❌ Not Met | 백엔드 부재 → Phase 5 사이클 필요 |
| FR-02 52주 + 21주 시각화 | ✅ Met | `dashboard.jsx` DramChart |
| FR-03 S-001 메인 | ✅ Met | 380 LOC, 모든 영역 포함 |
| FR-04 5 드릴다운 모달 | ✅ Met | `modals.jsx` 672 LOC |
| FR-05 분석 페이지 | ✅ Met | `pages.jsx` 일부 |
| FR-06 이벤트/정확도/수집 | ✅ Met | `pages.jsx` 나머지 |
| FR-07 HITL + POST API | ⚠️ Partial | UI ✅ / API ❌ |
| FR-08 차트 범위 필터 | ✅ Met | short/mid/all 3 모드 |
| FR-09 모달 스택 + 딥링크 | ✅ Met | URL 파라미터 작동 |
| FR-10 테마/밀도 토글 | ✅ Met | Tweaks 패널 |
| FR-11 A-4 Red Alert 펄싱 | ✅ Met | CSS keyframes |
| FR-12 Graph RAG | ✅ Met | S-005 모달 |

**Overall Success Rate**: **10/12 = 83.3%** (Critical 1, Partial 1)

### 3.2 Non-Functional Requirements (Plan §3.2)

| 항목 | 목표 | 현재 | 비고 |
|------|------|------|------|
| Performance (UI) | Lighthouse ≥ 90 | ⏸ 미측정 | Phase 6 |
| Performance (API) | p95 ≤ 60ms | ⏸ N/A | Phase 5 후 측정 |
| MAPE (예측 정확도) | ≥ 80% (7w) | ⏸ N/A | Phase 5 후 측정 |
| Accessibility | WCAG 2.1 AA | ⏸ 미측정 | Phase 6 |
| 한글 처리 | word-break: keep-all | ✅ Met | `styles.css` body 적용 |
| 가용성 | 99.5% | ⏸ N/A | 운영 후 측정 |

---

## 4. Quantitative Results

### 4.1 산출물 통계

| 카테고리 | 수치 |
|---------|------|
| PDCA 문서 | 5개 (PRD/Plan/Design/Do/Analysis) |
| 문서 총 줄수 | ~5,200줄 |
| 문서 총 크기 | ~190KB |
| 코드 파일 | 10개 (.tsx 2 + .jsx 5 + .css 1 + .js 1 + .ts 1) |
| 코드 총 LOC | ~3,500 |
| 구현 화면 | 14 / 14 (100%) |
| 공유 컴포넌트 | 12 + 12 Tweaks = 24개 |
| API 엔드포인트 | 0 / 15 (Phase 5 대기) |

### 4.2 빌드 메트릭

| 항목 | 값 |
|------|------|
| 프로덕션 빌드 시간 | 144ms |
| 번들 크기 (gzip) | 88KB JS + 4KB CSS = 92KB |
| 모듈 수 | 23 |
| 타입체크 | ✅ 0 errors |
| Lint | ✅ 0 errors |

### 4.3 Match Rate

```
Structural: 100%
Functional: 100% (UI)
Contract:     0% (API)
─────────────────────
Overall:    60%
```

---

## 5. 회고 (Retrospective)

### 5.1 잘된 점 (What went well)

1. **PRD 작성 단계에서 디자인 핸드오프를 SSOT로 선언** — 후속 Plan/Design 결정이 일관됨
2. **v0.1 실패에서 빠른 피봇** — 컴포넌트 재구현(7일 예상) → 핸드오프 직접 포팅(2시간)으로 14배 단축
3. **bkit PDCA 표준 준수** — 모든 단계 문서가 bkit 템플릿 형식 준수, KAIST 평가 대응 가능
4. **Context Anchor 일관성** — Plan→Design→Do→Analysis→Report 모두 동일한 5개 키 유지

### 5.2 아쉬운 점 (What could be improved)

1. **v0.1 시도 (컴포넌트 재구현)는 불필요한 우회** — 핸드오프가 이미 React 코드인 경우 처음부터 포팅이 정답이었음
2. **백엔드(Phase 5) 진입 못함** — 7주 일정 중 frontend MVP까지로 한정
3. **자동 테스트 부재** — Sig.test.tsx 1개만 (v0.1 백업에 있었음, 제거됨). Playwright E2E는 Phase 6 대기

### 5.3 향후 PDCA 사이클에 반영할 패턴

| 패턴 | 적용 시점 |
|------|----------|
| "핸드오프 React 코드는 재작성 말고 직접 포팅" | Do 단계 Checkpoint 4에서 명시적 질문화 |
| "Strategic Alignment Check를 매 Phase 종료시" | Plan/Design 진행 중 미스매치 조기 발견 |
| "Mock 데이터 구조를 PRD §17 TypeScript 타입과 정합 유지" | Phase 5 진입 시 API 응답 1:1 매핑 가능 |

---

## 6. 다음 사이클 권장 (Recommended Next Cycles)

### 6.1 즉시 (KAIST 발표 전)

| 작업 | 명령 |
|------|------|
| 시연 데모 리허설 | (수동) — 브라우저에서 14화면 클릭 시나리오 |
| 발표 자료 작성 | (수동) — PDCA 문서 핵심 페이지 발췌 |

### 6.2 Phase 5 — 백엔드 사이클 (별도 PDCA)

```
/pdca pm backend-sixsense       # 백엔드 단독 PRD (API 명세 우선)
/pdca plan backend-sixsense     # 데이터 수집 일정 + 인프라
/pdca design backend-sixsense   # FastAPI 라우터 + DB 스키마
/pdca do backend-sixsense       # 14 collector + scheduler
/pdca analyze backend-sixsense  # 통합 테스트
```

### 6.3 Phase 6 — QA 사이클

```
/pdca qa sixsense                # L1 (API) + L2 (UI) + L3 (E2E)
                                 # Phase 5 완료 후 실행
```

### 6.4 Archive

```
/pdca archive sixsense --summary  # 본 사이클 보존 + 메트릭만 유지
```

---

## 7. 팀 기여도

| 팀원 | 기여 영역 | 산출물 |
|------|----------|--------|
| 김영석 (Dataiku Korea, 프로젝트 리드) | PDCA 워크플로우 운영, 문서 작성, 디자인 시스템 가드 | 5개 PDCA 문서, 핸드오프 포팅 |
| 주광철 (엔코아에너텍, 개발 리드) | 백엔드 설계 (Design §3, §4) | Phase 5 사이클 리드 예정 |
| 김정일 (SK hynix, 현업 사용자) | 도메인 검증, 14신호 정의 검수 | PRD §05 P0 기능 1~8 검수 |

---

## 8. 산출물 위치

```
/Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/
├── prd.md                                      # 루트 PRD (개발자 친화)
├── docs/
│   ├── 00-pm/sixsense.prd.md                  # bkit 위치 PRD (동기화)
│   ├── 01-plan/features/sixsense.plan.md
│   ├── 02-design/features/sixsense.design.md
│   ├── 03-do/features/sixsense.do.md           # v0.2
│   ├── 03-analysis/sixsense.analysis.md        # 본 사이클 Check
│   └── 04-report/sixsense.report.md            # 본 문서
├── frontend/                                   # 실행 가능한 MVP
│   ├── src/
│   │   ├── App.tsx                            # TS 래퍼 (8줄)
│   │   ├── main.tsx
│   │   ├── styles/styles.css                  # 716줄 (핸드오프 그대로)
│   │   ├── mocks/data.js                      # 224줄
│   │   ├── components/components.jsx          # 282줄
│   │   └── screens/                           # 5 화면 파일, 2,221줄
│   └── package.json                           # React 19 + Vite 8 + TS 6
├── design_handoff_sixsense_dram_dashboard/    # 핸드오프 SSOT (참조)
└── NEXT_STEPS.md                              # 사용자 가이드
```

---

## 9. 검증 명령 (재현 가능)

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/frontend

# 빌드 검증
npm run typecheck     # 0 errors
npm run lint          # 0 errors
npm run build         # 144ms, 88KB gzip
npm run test          # (전체 테스트 추가는 Phase 6)

# 시연
npm run dev           # http://localhost:5173
                      # 우측 하단 ⚙️ Tweaks 패널에서 14화면 모두 탐색 가능

# 핸드오프 원본과 나란히 비교
open design_handoff_sixsense_dram_dashboard/Sixsense.html
```

---

## 9.5 Phase 5 + QA 업데이트 (2026-05-17 추가)

**Phase 5 백엔드 + L1/L2/L3 런타임 테스트 완료**:

| 항목 | 결과 |
|------|------|
| FastAPI 백엔드 | ✅ 15 엔드포인트 + HITL 큐 + Validation (in-memory) |
| L1 API 테스트 | ✅ 41/41 통과 (~5s) |
| L2 UI Action 테스트 | ✅ 17/17 통과 (14.6s, Playwright) |
| L3 E2E 시나리오 | ✅ 9/9 통과 (16.2s, 페르소나 + HITL 통합) |
| Match Rate (Runtime formula) | **100%** (Structural+Functional+Contract+Runtime 모두 100%) |
| 발견 이슈 | 4건 모두 해결, 잔여 critical 0건 |

상세: [docs/05-qa/sixsense.qa-report.md](../05-qa/sixsense.qa-report.md)

이로써 본 사이클은 **MVP → 검증된 시스템**으로 발전. 운영 배포까지의 잔여 작업은 인증/실DB/실데이터 수집기뿐 (Phase 6 분기).

## 10. 결론

본 PDCA 사이클은 **프론트엔드 MVP + 백엔드 API + L1/L2/L3 100% 통과** 및 **bkit PDCA 전체 단계 수행 검증**이라는 두 목표를 달성했다.

**핵심 성과**:
1. ✅ 14화면 hifi UI를 핸드오프와 시각적으로 100% 동일하게 구현
2. ✅ bkit 표준 PDCA 5단계 문서 모두 생성 (PRD/Plan/Design/Do/Analysis/Report)
3. ✅ "디자인 핸드오프 직접 포팅" 패턴을 검증 — 향후 사이클에 재사용 가능

**잔여 작업**:
- Phase 5 백엔드 (별도 PDCA 사이클로 진행)
- Phase 6 QA (Phase 5 완료 후)

본 산출물은 **KAIST CAIO 10기 6조 졸업 산출물**로 제출 가능하며, **실제 운영 배포를 위해서는 백엔드 사이클(Phase 5)이 선행 조건**이다.

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-05-17 | bkit PDCA Report 단계 — PRD~Analysis 통합 보고 | 김영석 |
