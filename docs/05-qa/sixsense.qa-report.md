# sixsense QA Report (L1/L2/L3 Runtime Verification)

> **Summary**: bkit `/pdca qa sixsense` 산출물. Phase 5 백엔드 구축 + Playwright 설치 후 L1/L2/L3 전체 테스트 실행. **67/67 (100%) 통과**.
>
> **Project**: Server DRAM Price 식스센스
> **Date**: 2026-05-17
> **Phase**: QA (bkit PDCA 8단계)
> **Test Engineer**: 김영석 (수동 실행, bkit qa-lead 표준 절차 준수)

---

## 1. 실행 환경

| 항목 | 값 |
|------|-----|
| Frontend dev | http://localhost:5173 (Vite 8 + React 19) |
| Backend API | http://localhost:8000 (FastAPI 0.115.0 + Python 3.9.6) |
| Test runner (L1) | bash + curl |
| Test runner (L2/L3) | Playwright 1.60.0 + Chromium 148 |
| OS | macOS Darwin 25.4.0 |

---

## 2. 결과 요약

| Level | 시나리오 수 | 통과 | 실패 | 통과율 | 총 소요 |
|-------|-----------|------|------|--------|--------|
| **L1 API** | 41 | 41 | 0 | **100%** | ~5s |
| **L2 UI Actions** | 17 | 17 | 0 | **100%** | 14.6s |
| **L3 E2E Scenarios** | 9 | 9 | 0 | **100%** | 16.2s |
| **합계** | **67** | **67** | **0** | **100%** | ~36s |

→ **QA_PASS**. Match Rate 산식 적용 시 100%.

---

## 3. L1 API 테스트 상세 (41건)

### Health (2)
- ✅ `GET /api/health` HTTP 200
- ✅ 응답 본문에 `"ok"` 포함

### Core GET endpoints (33)
- ✅ `GET /api/snapshot` HTTP 200 + currentPrice/forecast7/forecast21 모두 포함
- ✅ `GET /api/history` HTTP 200 + history 배열
- ✅ `GET /api/signals` HTTP 200 + groupA/groupB
- ✅ `GET /api/signals/A-1`, `/A-4`, `/B-3` HTTP 200
- ✅ `GET /api/signals/A-99` HTTP 404 (RESOURCE_NOT_FOUND)
- ✅ `GET /api/news` + 필터(`?sentiment=pos`) HTTP 200
- ✅ `GET /api/news/0` HTTP 200, `/news/9999` HTTP 404
- ✅ `GET /api/macro` HTTP 200
- ✅ `GET /api/events` + 필터(`?risk=high`) HTTP 200
- ✅ `GET /api/events/0` HTTP 200, `/events/9999` HTTP 404
- ✅ `GET /api/forecast/7` HTTP 200, `/forecast/21` HTTP 200
- ✅ `GET /api/forecast/14` HTTP 400 (VALIDATION_FAILED — horizon은 7/21만)
- ✅ `GET /api/accuracy` + 필터(`?horizon=7`) HTTP 200
- ✅ `GET /api/accuracy/0` HTTP 200
- ✅ `GET /api/collection` HTTP 200

### HITL POST + 폴링 (6)
- ✅ `POST /api/hitl/rules` HTTP 202 + `"processing"` + `queueId` 반환
- ✅ `GET /api/hitl/jobs/{queueId}` HTTP 200
- ✅ 1.5초 후 폴링 시 status `"done"` 전환
- ✅ `beforeResult` / `afterResult` 포함

### Validation errors (2)
- ✅ 빈 rules 배열 → HTTP 400
- ✅ 잘못된 schema → HTTP 422 (Pydantic)

---

## 4. L2 UI Action 테스트 상세 (17건)

### 메인 대시보드 S-001 (9)
- ✅ S-001 진입 시 가격 카드 3개 + 14신호 그리드 2개 + Graph RAG 모두 표시
- ✅ 현재 가격 카드에 mock 데이터 (`$3.20`) 정확히 표시
- ✅ 1~7주 예측 카드 클릭 → S-002 모달 열림 (배지 텍스트로 검증)
- ✅ Group A 첫 신호 카드 클릭 → S-003 모달 열림
- ✅ Graph RAG `상세 분석 →` 버튼 → S-005 모달
- ✅ ESC 키로 모달 닫힘
- ✅ 모달 바깥 클릭으로 닫힘
- ✅ 차트 범위 필터 3 모드 (단기/중장기/전체) 클릭 시 `.on` 활성 클래스 토글
- ✅ 전체 페이지 콘솔 에러 0건 (reload + networkidle 후)

### 풀페이지 URL 딥링크 (5)
- ✅ `?screen=S-006/S-008/S-010/S-012/S-014` 각각 렌더링 + 메인 콘텐츠 미표시

### 모달 딥링크 (2)
- ✅ `?modal=S-003&tab=A-4` → S-003 A-4 탭으로 직접 진입
- ✅ `?modal=S-002&horizon=21` → S-002 8~21주 탭

### 테마/밀도 토글 (1)
- ✅ Tweaks 패널에서 다크 모드 토글 시 `document.documentElement.dataset.theme === "dark"`

---

## 5. L3 E2E 시나리오 테스트 상세 (9건)

### 페르소나별 멀티 화면 플로우 (3)
- ✅ **Persona B (구매팀)**: S-001 진입 → A-4 신호 카드 → S-003 모달 → 닫기 → S-014 수집 현황 (멀티 화면 + 모달 스택)
- ✅ **Persona A (영업전략)**: 1~7주 카드 → S-002 → ESC → 8~21주 카드 → S-002 (다른 horizon)
- ✅ **Persona D (시장분석)**: Graph RAG → S-005 → ESC → S-010 이벤트 목록

### 모달 스택 (1)
- ✅ S-007 뉴스 모달 진입 + 모달 표시 검증

### HITL 백엔드 통합 (3)
- ✅ S-003 모달에서 HITL 패널 표시 확인
- ✅ `POST /api/hitl/rules` 호출 시 HTTP 202 + processing 상태
- ✅ HITL job 폴링 → done 상태 + before/afterResult 비교 가능

### 전체 화면 무결성 (2)
- ✅ 6개 풀페이지 순차 진입 → 콘솔 에러 0건
- ✅ 8개 모달 (각 필수 파라미터 포함) 진입 → 콘솔 에러 0건

---

## 6. Match Rate 재산정

### 6.1 Before (Phase 4 종료 시점, 2026-05-17 새벽)
```
Structural:    100% × 0.2 = 20.0
Functional:    100% × 0.4 = 40.0
Contract:        0% × 0.4 =  0.0
─────────────────────────────────
Overall:       60.0%
```

### 6.2 After (Phase 5+QA 완료 시점, 2026-05-17 현재)

런타임 실행 가능 → v2.3.0 formula 적용:
```
Structural:    100% × 0.15 = 15.0
Functional:    100% × 0.25 = 25.0
Contract:      100% × 0.25 = 25.0   ← 백엔드 구축으로 0% → 100%
Runtime:       100% × 0.35 = 35.0   ← L1/L2/L3 100% 통과
──────────────────────────────────
Overall:       100.0%
```

**해석**:
- L1 (API): 모든 15 엔드포인트 + 검증 케이스 통과 → Contract 100%
- L2 (UI): 메인 + 모달 + 라우팅 + 토글 모두 작동 → Functional 100%
- L3 (E2E): 페르소나 시나리오 + HITL 통합 + 14화면 무결성 → Runtime 100%

---

## 7. 발견된 이슈 및 해결

| ID | 단계 | 이슈 | 해결 |
|----|------|------|------|
| Q-01 | L1 | `signals/A-1` 404 반환 | data.json 필드명 차이 (`code` → `id`). `main.py` 수정 후 41/41 통과 |
| Q-02 | L2 | 차트 범위 버튼 셀렉터 모호 | `getByRole('button', { name: '단기 1~7주', exact: true })`로 정확한 라벨 사용 |
| Q-03 | L2 | "전체" 텍스트 충돌 (필터 vs "전체 목록 →") | `exact: true`로 차트 필터의 "전체"만 매칭 |
| Q-04 | L3 | 8개 모달 중 일부 진입 실패 | `app.jsx`의 `window.SIXSENSE_DATA` 미포팅 → import + sed 전체 치환 |

모두 해결됨. 잔여 이슈 0건.

---

## 8. 잔여 갭 (Phase 6 이후)

| ID | 항목 | 우선순위 |
|----|------|---------|
| L4-01 | Lighthouse Performance ≥ 90 측정 | Medium |
| L4-02 | LCP < 2.5s, INP < 200ms 측정 | Medium |
| L5-01 | OWASP ZAP 자동 스캔 | Low (Enterprise 레벨에만) |
| L5-02 | npm audit 운영 정책 | Low |
| A-01 | 인증 (JWT) 실제 구현 | High (운영 전 필수) |
| A-02 | PostgreSQL + TimescaleDB 전환 (현재 in-memory) | High (운영 전 필수) |
| A-03 | Redis 캐시 도입 | Medium |
| A-04 | 14신호 실제 데이터 수집기 | High (운영 전 필수) |
| A-05 | 매주 화 06:00 KST 스케줄러 | High |

---

## 9. 재현 명령 (CI/CD 통합용)

```bash
# 1. Backend 기동
cd backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Frontend 기동
cd ../frontend
npm run dev &

# 3. L1 (API)
bash ../backend/tests/l1_api_test.sh
# → "41 passed, 0 failed"

# 4. L2 (UI Actions)
npx playwright test l2_ui_actions
# → "17 passed"

# 5. L3 (E2E)
npx playwright test l3_scenarios
# → "9 passed"

# 6. 종합 (Playwright)
npx playwright test
# → "26 passed (L2+L3)"
```

---

## 10. Checkpoint — QA Status

→ **QA_PASS** (Match Rate 100%, 잔여 critical 이슈 0건)

**다음 단계 권장**:
- ✅ Report 단계 진행 (`/pdca report sixsense`) — 본 QA 결과 반영
- ⏸ 운영 배포는 §8의 A-01~A-05 (인증·DB·스케줄러) 해결 후

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-05-17 | bkit QA 단계 — L1/L2/L3 67건 100% 통과 | 김영석 |
