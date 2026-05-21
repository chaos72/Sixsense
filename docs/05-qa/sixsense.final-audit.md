# Sixsense — 최종 사전 배포 감사 (Phase 7 완료, 2026-05-19)

> KAIST CAIO 6조 과제 + 사내 데모 직전 50+ 항목 자동 점검. 발표/데모 **GO** · 운영 배포 시 **P0 3건 + P1 2건** 처리 필요.

---

## 📊 종합 스코어

| 등급 | 항목 수 | 영역 |
|---|---|---|
| ✅ **PASS** | **49건** | 인프라 12 + Multi-Model 5 + data.js 무결성 24 + UI 디자인 15 + 보안/Git 5 (일부 중복 포함) |
| ⚠ **WARN** | **17건** | 데이터 신선도 14 + 운영 준비 3 (cron/endpoint/Anthropic credit) |
| ❌ **FAIL** | **0건** | — |

**결론**: **발표/데모는 즉시 GO**, 외부 운영 배포 전 **P0 3건 + P1 2건** 처리 필요.

---

## A. 인프라 (12/12 ✅)

| 컴포넌트 | 상태 |
|---|---|
| Frontend Vite :5173 | HTTP 200 |
| Backend FastAPI :8000 | HTTP 200 |
| `/api/snapshot` `/signals` `/macro` `/events` `/news` `/collection` `/accuracy` `/forecast/7` `/forecast/21` `/refresh/stages` | 모두 HTTP 200 |

## B. 21 신호 데이터 (⚠ 신선도 14건)

| | rows | 마지막 주 | 일수 | 신선도 |
|---|---|---|---|---|
| A-1 ~ A-7 | 11~53 | 2026-04-20 ~ 04-30 | 21~31일 전 | ⚠ |
| B-1, B-3, B-4, B-7 | 30~53 | 2026-04-27 | 24일 전 | ⚠ |
| **B-2, B-5, B-6** | 7~43 | **2026-05-18** | **3일 전** | ✅ |
| macro-* (6개) | 53 | 2026-04-27 ~ 04-30 | 21~24일 전 | ⚠ |
| target-dram | 53 | 2026-04-27 | 24일 전 | ⚠ |

**원인**: `backfill.py` + `auto_collectors.py` 상단에 `END = "2026-04-30"` 하드코딩 → 그 이후 데이터 필터링됨. 운영 시 P1으로 `END = date.today().isoformat()` 동적화 필요.

**영향**: 데이터 패턴 분석 + Multi-Model 학습 + 차트 표시는 정상 (4월말까지 53주 충분). 발표/데모 GO.

## C. Multi-Model 검증 (5/5 ✅)

| 모델 | 시계열 | MAPE | 목표 | 결과 |
|---|---|---|---|---|
| Prophet | 21주 | (baseline) | — | ✅ |
| sklearn HistGBR | 1~7주 | 6.79% | ≤10% | ✅ |
| **sklearn GBR ⭐** | 1~7주 | **4.54%** | ≤7% | ✅ baseline 7.54% 대비 **39.8% 개선** |
| **PyTorch LSTM ⭐** | 8~21주 | **9.92%** | ≤12% | ✅ |

## D. data.js 무결성 (24/24 ✅ — UI 확장 #1~#15 모두 검증)

| # | 확장 영역 | 검증 |
|---|---|---|
| #1 | InsightCard 존재 + model 표시 + keySignals ≥1 | ✅ |
| #3 | summary `**bold**` 강조 ≥3개 | ✅ (4~9개) |
| #3b | ModelValidationPanel + 단기 표 3행 + 중장기 1행 | ✅ |
| #4 | 4 모델 시계열 (Prophet 21 + HistGBR 7 + GBR 7 + LSTM 14) | ✅ |
| #9 | events 5 카테고리 다양성 + 국내 반도체 존재 | ✅ |
| #10 | macro 6개 (UST10 추가) | ✅ |
| #12 | insight summary ≥250자 + 마침표 완결 | ✅ (310자) |
| #14 | news 10/10 + events 10/10 제목·요약 한국어 | ✅ |
| #15 | macro ust10 첫번째 배치 | ✅ |
| 기타 | signalsA 7 + signalsB 7 + history ≥52주 + news 10 + events 10 | ✅ |

## E. UI 디자인 (15/15 ✅ — CSS 토큰 + 컴포넌트 모두 존재)

| # | CSS/컴포넌트 | 확인 |
|---|---|---|
| #1 | `<InsightCard>` (components.jsx) | ✅ |
| #3b | `<ModelValidationPanel>` (dashboard.jsx) | ✅ |
| #4 | `.insight-main` grid 3:2 좌우 분할 | ✅ |
| #5 | `.grid-snapshot` 7분화 (1fr 1fr 1fr 4fr) | ✅ |
| #6 | `--chart-baseline` 황색 + `--chart-secondary` 보라 토큰 | ✅ |
| #6 | `.theme-toggle` 강화 | ✅ |
| #7 | `<RefreshPanel>` + `.refresh-panel` CSS | ✅ |
| #8 | `categoryClass()` 매핑 | ✅ |
| #9 | `.events-type-domestic` 보라 칩 | ✅ |
| #13 | `.insight-main` breakpoint **800px** | ✅ |
| #13 | `.insight-body` font-size **11.5px** | ✅ |
| #14 | `korean_title()` 60-key KEYWORD_MAP | ✅ |
| #15 | `TWEAK_DEFAULTS.theme: "dark"` 디폴트 | ✅ |

## F. 보안 + Git (5/5 ✅)

- `.env` gitignore 보호 ✅
- `.env` git untracked ✅
- 실제 AWS 키 코드/문서 노출 없음 ✅ (AWS 공식 예시 키 `AKIAIOSFODNN7EXAMPLE`만 docs에 있음 — false positive)
- 총 commits **33** (Phase 1~7 누적)
- working tree clean ✅

## G. 운영 배포 액션 아이템 (⚠ 3건)

### 🔴 P0 (배포 전 필수)

| # | 항목 | 액션 |
|---|---|---|
| P0-1 | **수동 갱신 endpoint thread 멈춤** | `POST /api/refresh` 가 첫 iteration 진입 전 멈춤 (uvicorn `--reload` + threading 조합). 운영 시 `asyncio.create_task` + `subprocess.create_subprocess_exec` 로 대체, 또는 Celery/RQ 도입. **CLI 실행은 100% 정상**이라 cron 자동화는 즉시 가능. |
| P0-2 | **cron 자동 갱신 미등록** | GitHub Actions (`cron: '0 21 * * 1'` = 매주 화 06:00 KST) 또는 macOS launchd 등록. 5단계 파이프라인 CLI 호출 (~70초). |
| P0-3 | **API 인증 + CORS 운영 도메인** | `POST /api/refresh` 누구나 호출 가능. Supabase Auth + API Token 도입. CORS `allow_origins` 에 운영 도메인 추가. |

### 🟡 P1 (배포 후 30일)

| # | 항목 | 액션 |
|---|---|---|
| P1-1 | **데이터 수집 END 하드코딩** | `backfill.py` + `auto_collectors.py` `END = "2026-04-30"` → `END = date.today().isoformat()` 동적화. forecast_v2 의 학습 cutoff 도 동적 조정 (현재 80주 → today - 7w). |
| P1-2 | **LLM 비용 안정화** | Anthropic 크레딧 충전 (1순위 활성 → 더 정확한 분석) + Groq API 키 추가 (3순위 무료 14400/day fallback). |

### ⚠ 기타 (선택)

- AWS 공식 예시 키 (`AKIAIOSFODNN7EXAMPLE`) 를 `<EXAMPLE>` 같이 마스킹 — GitGuardian false alarm 방지
- `docs/06-presentation/` 발표자료 commit 결정 (현재 untracked)

---

## 발표/데모 GO 체크리스트

- [x] Frontend :5173 + Backend :8000 동작
- [x] §01 가격 스냅샷 7분화 + 인사이트 카드 좌우 분할
- [x] §02 DRAM 차트 4개 모델 동시 표시 (Prophet/HistGBR/GBR★/LSTM★) + MAPE 검증 표
- [x] §05 AI 뉴스 10/10 한국어
- [x] §06 거시경제 6개 (UST10 첫번째)
- [x] §07 글로벌 이벤트 10건 5 카테고리 다양성 100% 한국어
- [x] §09 수동 갱신 버튼 표시 (CLI 백업)
- [x] 인사이트 카드 클릭 → 모달 팝업 (310자 완결)
- [x] 다크 모드 디폴트
- [x] 토글로 라이트 모드 전환 가능

**모든 발표 시나리오 검증 통과** — KAIST CAIO 6조 과제 제출 + 사내 데모 즉시 가능.

---

## Phase 7 commit 누적 (요약)

```
957d2c5 feat(ui #15): §06 macro ust10 첫번째 + 다크 모드 디폴트
1f2be77 data: 차트 + 인사이트 재생성 (#14 news/events 한국어 반영)
e4e00aa data: 수동 갱신 결과 반영 (2026-05-18 historical + 재학습)
4f7ded7 feat(news/events #14): 휴리스틱도 한국어 100% (korean_title)
1d0fbfc feat(ui #13): §01 인사이트 가독성 미세조정
82bea84 feat(insight #12): 인사이트 본문 완결 문장 강제
04adf36 feat(phase7-ui #11): 인사이트 카드 클릭 → 모달 팝업
ce8e2fc fix(insight): Gemini maxOutputTokens 2048→8192
61e7dec feat(phase7 #10): news/events 풀 분리 + macro UST10
153cfbd feat(phase7-ui #9): §07 국내 반도체 카테고리 + 한국어
adbc60e feat(phase7-ui #8): §07 글로벌 이벤트 4 카테고리 + 유형 칩
6f4a228 feat(phase7-ui): hand-off 7가지 사용자 명시 확장 + 수동 갱신
ed8a8b4 feat(phase7-data): 실데이터 → hand-off UI 주입 파이프라인
3ca4d9f chore: Plotly 산출물 정리
```

**총 33 commits · 사용자 명시 확장 15회 · 모든 hand-off SSOT 원칙 준수.**
