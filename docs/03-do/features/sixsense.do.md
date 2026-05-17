# sixsense Implementation Guide

> **Summary**: bkit `/pdca do sixsense` 산출물 (v0.2). **전략 변경**: 핸드오프 코드를 **직접 포팅**하여 14화면 UI를 100% 재현. 컴포넌트 재구현 금지.
>
> **Project**: Server DRAM Price 식스센스
> **Date**: 2026-05-17
> **Phase**: Do (bkit PDCA 4단계)
> **Scope**: `--scope module-0-foundation` (현재 세션)
> **Strategy**: Direct Port (참조: PRD §7.4)

---

## ⚠️ 전략 변경 이력 (v0.2 — 2026-05-17)

**v0.1 (폐기)**: "공유 컴포넌트 12종을 핸드오프에서 영감을 받아 TypeScript로 처음부터 새로 작성" → 결과적으로 **컴포넌트 카탈로그(쇼케이스)**가 만들어졌고 실제 14화면 UI가 아니었음.

**v0.2 (현재)**: "핸드오프의 React 코드를 그대로 frontend/src/에 복사 + Vite 호환 최소 조정". 핸드오프와 100% 동일한 UI 보장. 사용자 요청: "무조건 UI는 claude design에서 만든 결과물 hand-off를 사용해야 해" (2026-05-17).

---

## Context Anchor

| Key | Value |
|-----|-------|
| **WHY** | 반도체 가격 예측을 위한 데이터 수집·분석에 사람·시간·비용이 과다 투입되고 시장 급변에 대응 못함 |
| **WHO** | 반도체 부서 50대 임원 5명 |
| **RISK** | 핸드오프 코드 포팅 시 React 19 호환성 + Vite JSX 처리 |
| **SUCCESS** | dev 서버에서 핸드오프 `Sixsense.html`과 시각적으로 동일한 14화면 표시 |
| **SCOPE** | Phase 0 (핸드오프 직접 포팅) → Phase 5 (API 연결) → Phase 6 (검증) |

---

## Design Anchor

**100% 핸드오프 동일 — 디자인 토큰/컴포넌트/레이아웃 모두 핸드오프에서 그대로 가져옴.** 변경 금지.

- 시각 SSOT: `design_handoff_sixsense_dram_dashboard/Sixsense.html` (인터랙티브 프로토타입)
- 코드 SSOT: `design_handoff_sixsense_dram_dashboard/src/*.{css,js,jsx}`

---

## Session Scope

### Current Session Modules

**선택된 scope**: `module-0-foundation` (재정의)

| Sub-task | 작업 | 출처 (hand-off) | 대상 (frontend) |
|----------|------|----------------|-----------------|
| 0a-backup | 기존 v0.1 쇼케이스 백업 | `src/App.tsx`, `src/design-system/` | `src/_legacy_showcase_v0.1/` |
| 0b-css | CSS 전체 복사 | `src/styles.css` | `src/styles/styles.css` |
| 0c-data | mock 데이터 복사 | `src/data.js` | `src/mocks/data.js` |
| 0d-components | 공유 컴포넌트 포팅 | `src/components.jsx` | `src/components/components.jsx` |
| 0e-dashboard | S-001 메인 포팅 | `src/dashboard.jsx` | `src/screens/dashboard.jsx` |
| 0f-modals | 8 모달 포팅 | `src/modals.jsx` | `src/screens/modals.jsx` |
| 0g-pages | 5 풀페이지 포팅 | `src/pages.jsx` | `src/screens/pages.jsx` |
| 0h-app | 라우팅/테마/스택 포팅 | `src/app.jsx` | `src/screens/app.jsx` |
| 0i-entry | 엔트리 래퍼 | — | `src/App.tsx` (5 라인) |

**총 9개 sub-task, 예상 시간**: 2~3시간 (포팅 + 호환성 조정)

---

## Upstream Context Chain

### Documents Loaded

- ✅ PRD v0.2: `docs/00-pm/sixsense.prd.md` (§7.4 직접 포팅 전략 명시)
- ✅ Plan: `docs/01-plan/features/sixsense.plan.md`
- ✅ Design: `docs/02-design/features/sixsense.design.md`
- ✅ Hand-off (시각/코드 SSOT): `design_handoff_sixsense_dram_dashboard/`

### Decision Record Chain

```
📋 Decision Record Chain
─────────────────────────────────────────────────────
[PRD §07]   UI 정의: 14화면 모두 핸드오프 그대로 사용
[PRD §7.4]  구현 전략: Direct Port (재구현 금지)
[Plan §7.2] 기술 스택: React + TS + Vite (Vite는 .jsx 네이티브 지원)
[Design §9] 폴더 구조: src/components/, src/screens/, src/mocks/, src/styles/
[Do v0.2]   엔트리 전략: TS App.tsx가 JSX hand-off-app을 래핑
─────────────────────────────────────────────────────
```

---

## 1. Pre-Implementation Checklist

### 1.1 Documents Verified

- [x] PRD §7.4 직접 포팅 전략 명시
- [x] Design Hand-off 폴더 존재 확인
- [x] v0.1 쇼케이스를 백업할 위치 결정 (`src/_legacy_showcase_v0.1/`)

### 1.2 Environment Ready

- [x] Node.js v24.15.0 + npm 11.12.1
- [x] frontend/ 프로젝트 이미 초기화됨 (v0.1에서)
- [x] 의존성 모두 설치됨 (react, react-router-dom, recharts, vitest 등)

---

## 2. Implementation Strategy: Direct Port

### 2.1 핵심 원칙

1. **재작성 금지** — 핸드오프 JSX 코드를 그대로 사용. 컴포넌트 분해·리팩토링 금지.
2. **CSS 전체 복사** — 디자인 토큰만이 아닌 컴포넌트 스타일까지 모두.
3. **Mock 데이터 그대로** — `data.js`는 변경 없이 import.
4. **JSX 확장자 유지** — TypeScript로 변환 안 함 (변환 시 디버그 시간 폭증). 향후 Phase 6에서 점진적 TS 마이그레이션.
5. **최소 호환 조정** — Vite는 .jsx를 네이티브 처리. import 경로만 보정.

### 2.2 잠재 호환성 이슈와 대응

| 이슈 | 원인 | 대응 |
|------|------|------|
| React 18 vs 19 | 핸드오프는 React 18, 우리는 19 | 19는 18 하위호환. `<StrictMode>` 정도만 주의 |
| `useState` hook 명시 import 누락 | 핸드오프 코드가 글로벌 React 사용 가정 | 각 파일 상단에 `import React, {useState, useEffect, ...} from 'react'` 추가 |
| CSS 클래스명 (kebab-case) | 핸드오프는 일반 CSS, 우리는 CSS Module 옵션도 있음 | **CSS Module 사용 안 함** — 전역 styles.css로 import |
| Tweaks 패널 | 개발 전용 | 일단 포함, 나중에 프로덕션 빌드에서 제거 |

---

## 3. Key Files to Create/Modify

### 3.1 New Files (이번 세션)

```
frontend/src/
├── App.tsx                          [REWRITE: 5라인 래퍼]
├── main.tsx                         [MODIFY: import styles/styles.css]
├── styles/
│   ├── styles.css                   [NEW: hand-off 전체 복사]
│   ├── tokens.css                   [KEEP: 이미 있음, 호환 위해 유지 가능]
│   └── globals.css                  [REMOVE: styles.css에 통합됨]
├── mocks/
│   └── data.js                      [NEW: hand-off 복사]
├── components/
│   └── components.jsx               [NEW: hand-off 복사 + import 조정]
├── screens/
│   ├── dashboard.jsx                [NEW: hand-off 복사]
│   ├── modals.jsx                   [NEW: hand-off 복사]
│   ├── pages.jsx                    [NEW: hand-off 복사]
│   ├── app.jsx                      [NEW: hand-off 복사 — 라우팅 + 모달 스택]
│   └── tweaks-panel.jsx             [NEW: 개발 전용]
└── _legacy_showcase_v0.1/           [NEW: v0.1 백업]
    ├── App.tsx
    └── design-system/...
```

### 3.2 Files to Modify

- `src/main.tsx`: 새 styles.css 경로 import
- `src/App.tsx`: 쇼케이스 코드 제거, JSX 앱 마운트 래퍼만

---

## 4. Dependencies

추가 설치 없음. v0.1에서 이미 react, react-router-dom, recharts 모두 설치됨. 단, 핸드오프 차트는 자체 SVG이므로 recharts는 Phase 1 이후에만 사용.

---

## 5. Implementation Notes

### 5.1 Why Direct Port

| 비교축 | 재작성 (v0.1 시도) | 직접 포팅 (v0.2) |
|--------|-------------------|------------------|
| UI 정확성 | ❌ 카탈로그가 나옴 | ✅ 100% 동일 |
| 개발 시간 | 7일 (Phase 0만) | 2~3시간 (Phase 0 전체) |
| 유지보수 | TS 타입 + Storybook | 향후 점진적 TS 변환 |
| 위험 | 디자인 변경 가능성 | 핸드오프와 격리됨 |

### 5.2 v0.1 쇼케이스 처리

v0.1의 12개 컴포넌트(TypeScript)는 **참고용으로 보존**(`src/_legacy_showcase_v0.1/`). 향후 점진적 TS 마이그레이션 시 참고. 단 실제 라우트에서는 사용 안 함.

### 5.3 Code-to-Design Traceability

각 포팅된 .jsx 파일 상단에 다음 주석 추가:

```javascript
// PORTED FROM: design_handoff_sixsense_dram_dashboard/src/<file>.jsx
// DO NOT MODIFY UI WITHOUT UPDATING DESIGN HAND-OFF FIRST
// Design Ref: PRD §07, §7.4 Direct Port Strategy
```

### 5.4 Things to Avoid

- ❌ 핸드오프 JSX를 "정리"하거나 "리팩토링"
- ❌ CSS 클래스를 CSS Module로 변환
- ❌ "더 나은" 색상/간격/타이포 적용
- ❌ 새 화면 추가 (S-015 등)
- ❌ 핸드오프에 있지만 "필요 없어 보이는" 기능 제거

### 5.5 Checklist (구현 중 매 단계 자가 검증)

- [ ] dev 서버에서 화면을 핸드오프 `Sixsense.html`과 나란히 띄워 비교
- [ ] 픽셀 단위 일치 (오차 ±2px 허용)
- [ ] 모든 클릭/호버 인터랙션 동일하게 작동
- [ ] 라이트/다크 + 편안/컴팩트 4조합 모두 동작
- [ ] 모달 ESC + 바깥클릭 닫힘
- [ ] 콘솔에 에러 0건

---

## 6. Testing Checklist

### 6.1 Visual Acceptance (필수)

브라우저 2개 띄워 비교:
1. `open design_handoff_sixsense_dram_dashboard/Sixsense.html`
2. `open http://localhost:5173/`

확인:
- [ ] S-001 메인 대시보드 레이아웃 동일
- [ ] 가격 카드 3개 (현재/1-7w/8-21w) 위치·스타일 동일
- [ ] DRAM 차트 + 범위 필터 동일
- [ ] 14신호 카드 (Group A·B) 동일
- [ ] Graph RAG 카드 동일
- [ ] 뉴스/거시/이벤트/정확도/수집 푸터 모두 동일
- [ ] 각 화면 모달 진입 동일하게 작동

### 6.2 Functional Acceptance

- [ ] 모든 클릭 가능 카드가 클릭 시 적절한 화면 전환
- [ ] 차트 범위 필터 3 모드 작동
- [ ] HITL 패널 저장 버튼 작동 (mock)
- [ ] 테마/밀도 토글 즉시 반영
- [ ] 모달 스택 (모달 위 모달) 작동

### 6.3 Code Quality

```bash
cd frontend
npm run typecheck   # .tsx만 검사 (.jsx는 타입 검사 안 함)
npm run lint        # ESLint 0 errors
npm run build       # 프로덕션 빌드 성공
```

---

## 7. Progress Tracking

### 7.1 Current Session Tasks

| Sub-task | 상태 |
|----------|------|
| 0a-backup | 진행 예정 |
| 0b-css | 진행 예정 |
| 0c-data | 진행 예정 |
| 0d-components | 진행 예정 |
| 0e-dashboard | 진행 예정 |
| 0f-modals | 진행 예정 |
| 0g-pages | 진행 예정 |
| 0h-app | 진행 예정 |
| 0i-entry | 진행 예정 |

### 7.2 Blockers (사전 예측)

- **JSX의 글로벌 React 의존성**: 핸드오프 코드가 글로벌 `React`를 가정하면 각 .jsx 파일에 `import React from 'react'` 추가 필요. Vite는 자동 JSX runtime 사용하지만, hook 사용 시 명시 import 필요.
- **CSS 클래스 충돌**: 핸드오프의 `.card`, `.btn` 등이 우리 v0.1 design-system의 CSS Module과 겹치면 안 됨 → v0.1을 `_legacy_showcase_v0.1/`로 격리하여 import 트리에서 제외하면 해결.

---

## ✅ Checkpoint 4 — Implementation Approval

**범위 요약**:
- 신규 파일: 9개 (CSS 1 + data 1 + components 1 + screens 4 + app entry 1 + legacy 백업 1)
- 수정 파일: 2개 (App.tsx, main.tsx)
- 삭제 파일: 0개 (v0.1은 백업, 추후 점진 마이그레이션)
- 예상 LOC: ~2,500 (핸드오프 그대로 복사 + 작은 호환 조정)
- 예상 시간: 2~3시간

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-05-16 | 컴포넌트 재구현 가이드 — Phase 0 모듈 분할 | 김영석 |
| 0.2 | 2026-05-17 | **전략 변경**: 핸드오프 직접 포팅으로 재작성. v0.1 쇼케이스는 `_legacy_showcase_v0.1/`로 백업. | 김영석 |
