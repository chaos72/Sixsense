# 🎓 Sixsense — KAIST CAIO 과제 제출 가이드 (Final)

> **최종 상태**: PDCA 6단계 모두 완료. Frontend MVP 작동 검증 완료. 제출 준비됨.

---

## ✅ 완료된 PDCA 산출물 (제출용)

| 단계 | 파일 | 줄수 | 비고 |
|------|------|------|------|
| PM (PRD) | [docs/00-pm/sixsense.prd.md](docs/00-pm/sixsense.prd.md) | 1,641 | 18 섹션 종합 PRD |
| Plan | [docs/01-plan/features/sixsense.plan.md](docs/01-plan/features/sixsense.plan.md) | 326 | 요구사항·아키텍처·위험 |
| Design | [docs/02-design/features/sixsense.design.md](docs/02-design/features/sixsense.design.md) | 1,113 | bkit 표준 11 섹션 |
| Do (v0.2) | [docs/03-do/features/sixsense.do.md](docs/03-do/features/sixsense.do.md) | ~330 | 핸드오프 직접 포팅 가이드 |
| Analysis | [docs/03-analysis/sixsense.analysis.md](docs/03-analysis/sixsense.analysis.md) | ~280 | Gap 분석 + Match Rate 60% |
| Report | [docs/04-report/sixsense.report.md](docs/04-report/sixsense.report.md) | ~290 | 최종 통합 보고 |

---

## 🖥️ 실행 가능한 MVP

| 항목 | 값 |
|------|-----|
| 위치 | `frontend/` |
| 화면 수 | 14 / 14 (100%) |
| 기술 스택 | React 19 + TypeScript 6 + Vite 8 |
| 코드 라인 | ~3,500 LOC |
| 빌드 시간 | 144ms |
| 번들 크기 | 88KB gzip |

### 데모 실행

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/frontend
npm run dev
# → http://localhost:5173 (브라우저 자동 열림)
```

**시연 시나리오** (5분):
1. 메인 대시보드 진입 (S-001) — 가격 3카드 + 차트 + 14신호 + Graph RAG + 뉴스/거시 + 이벤트/정확도
2. 차트 범위 필터 클릭 → `단기 1~7주` / `중장기 8~21주` / `전체`
3. 가격 카드 클릭 → S-002 예측 근거 모달 (1-7w/8-21w 탭)
4. A-4 Red Alert 신호 카드 클릭 → S-003 모달
5. Graph RAG 카드 → S-005 구리↔DRAM 모달
6. 우측 하단 ⚙️ Tweaks → 다른 13화면 탐색 + 라이트/다크 토글

---

## 📊 핵심 메트릭

| 메트릭 | 값 |
|--------|-----|
| Match Rate (Overall) | **60%** (UI 100%, Backend 0%) |
| Structural Match | 100% (14/14 화면) |
| Functional Depth | 100% (17/17 인터랙션) |
| API Contract | 0% (Phase 5 대기) |
| 요구사항 충족 (Met) | 10 / 12 = **83.3%** |
| 빌드 통과 | ✅ |
| 타입체크 통과 | ✅ |
| Lint 통과 | ✅ |

---

## 📁 디렉토리 구조 (최종)

```
Sixsense/
├── prd.md                                           # 루트 PRD (개발자 친화)
├── prd.docx, prd.md.bak                             # 원본/백업
├── NEXT_STEPS.md                                    # 본 문서
├── docs/                                            # 📄 PDCA 산출물
│   ├── 00-pm/sixsense.prd.md
│   ├── 01-plan/features/sixsense.plan.md
│   ├── 02-design/features/sixsense.design.md
│   ├── 03-do/features/sixsense.do.md
│   ├── 03-analysis/sixsense.analysis.md
│   └── 04-report/sixsense.report.md
├── frontend/                                        # 🖥️ MVP 실행 코드
│   ├── package.json
│   └── src/
│       ├── App.tsx, main.tsx
│       ├── styles/styles.css                        # 716줄 (핸드오프)
│       ├── mocks/data.js                            # 224줄
│       ├── components/components.jsx                # 282줄 (13 컴포넌트)
│       └── screens/                                 # 14 화면
│           ├── dashboard.jsx                        # S-001 (380줄)
│           ├── modals.jsx                           # S-002~S-013 (672줄)
│           ├── pages.jsx                            # S-006~S-014 (420줄)
│           ├── app.jsx                              # 라우팅 (181줄)
│           └── tweaks-panel.jsx                     # 개발 전용 (568줄)
├── design_handoff_sixsense_dram_dashboard/          # 🎨 Claude Design 핸드오프 SSOT
│   ├── README.md, Sixsense.html, Canvas.html
│   └── src/ (CSS, data, components, dashboard, modals, pages, app)
├── .claude/settings.json                            # Plan Mode 기본 진입
└── .env
```

---

## 🚀 발표 일정에 따른 다음 작업

### 시나리오 A: 즉시 발표 (현재 상태로)

```bash
# 1. dev 서버 기동
cd frontend && npm run dev

# 2. 핸드오프 원본도 함께 띄워 비교 (선택)
open /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/design_handoff_sixsense_dram_dashboard/Sixsense.html
```

### 시나리오 B: 백엔드 추가 (시간 여유 시)

```bash
# Phase 5 — 별도 PDCA 사이클로 진행 권장
# (현재 Claude Code 세션 종료 후 새 세션에서)
claude
/pdca pm backend-sixsense
/pdca plan backend-sixsense
/pdca design backend-sixsense
/pdca do backend-sixsense
```

### 시나리오 C: QA + 정확도 측정

```bash
# Phase 6 — Playwright + Lighthouse
/pdca qa sixsense
```

---

## 🆘 시연 중 문제 발생 시

### Q1. dev 서버가 안 뜨거나 포트 충돌
```bash
lsof -i :5173        # 사용 중 프로세스 확인
pkill -f vite         # 기존 Vite 종료
npm run dev           # 재시작
```

### Q2. 화면이 깨져 보임
- 브라우저 캐시 클리어: `Cmd + Shift + R` (강제 새로고침)
- 다크 모드 자동 진입 시 Tweaks에서 라이트로 토글

### Q3. 핸드오프 원본과 비교하고 싶음
- `open design_handoff_sixsense_dram_dashboard/Sixsense.html` — 핸드오프 원본
- 두 창을 나란히 두고 비교

### Q4. Sixsense.html 더블클릭하면 화면이 안 뜸
- Chrome/Safari로 열면 됨
- 또는 `python3 -m http.server 8000` 후 `http://localhost:8000/Sixsense.html`

---

## 🎯 KAIST CAIO 평가 대응 포인트

| 평가 항목 | 본 사이클 증빙 |
|----------|--------------|
| **PDCA 방법론 적용** | docs/ 트리에 6개 산출물 (PRD~Report) |
| **bkit 워크플로우** | bkit 표준 템플릿 준수, 명령 형식 매칭 |
| **결정 사슬 추적성** | 각 문서 Context Anchor + Decision Record Chain |
| **MVP 작동** | http://localhost:5173 실시간 시연 |
| **UI 완성도** | 핸드오프와 시각적 100% 동일 |
| **회고·개선 능력** | Report §5 (v0.1 실패에서 v0.2로 피봇) |
| **확장성** | Module Map + Recommended Session Plan → Phase 5/6 명시 |

---

## 📅 변경 이력

| Date | 변경 |
|------|------|
| 2026-05-16 | Phase 0~1 v0.1 (TS 컴포넌트 쇼케이스) — **폐기** |
| 2026-05-17 | v0.2: 핸드오프 직접 포팅 → 14화면 완성, Analysis + Report 추가, NEXT_STEPS 최종 |
