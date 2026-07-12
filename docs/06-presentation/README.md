# Sixsense — 발표자료

## 파일

- [sixsense.presentation.md](sixsense.presentation.md) — Marp 호환 markdown (24 슬라이드, 20분 분량)

## 미리보기 / 변환 방법

### VS Code (가장 간단)
1. **Marp for VS Code** 확장 설치
2. `sixsense.presentation.md` 열기 → 우측 상단 미리보기 버튼

### CLI (PDF/PPTX 생성)

```bash
# Marp CLI 설치 (1회)
npm install -g @marp-team/marp-cli

# PDF 변환 (한글 폰트 포함)
marp sixsense.presentation.md --pdf --allow-local-files

# PowerPoint 변환
marp sixsense.presentation.md --pptx --allow-local-files

# HTML reveal.js 변환 (브라우저 직접 열기)
marp sixsense.presentation.md --html --allow-local-files
```

산출물: `sixsense.presentation.pdf` / `.pptx` / `.html`

### 한글 폰트 권장

본 발표 자료는 `Pretendard Variable` 우선, macOS 시스템 `Apple SD Gothic Neo` fallback 으로 작동. PDF 생성 시 시스템 폰트 자동 포함됨.

## 슬라이드 구조 (20분 + Q&A)

| # | 섹션 | 시간 | 슬라이드 |
|---|---|---|---|
| 0 | 타이틀 + 목차 | 1분 | 2장 |
| 1 | Executive Summary | 3분 | 3장 |
| 2 | Why & What — 페르소나·핵심가치 | 3분 | 2장 |
| 3 | UI Hand-off Identity — 14화면 SSOT | 3분 | 3장 |
| 4 | Architecture & Pipeline | 3분 | 3장 |
| 5 | Multi-Model 검증 | 2분 | 2장 |
| 6 | 라이브 데모 (http://localhost:5173) | 4분 | 2장 |
| 7 | Production 로드맵 | 2분 | 3장 |
| 8 | Thank You + Q&A | — | 1장 |

**총 24 슬라이드 · 20분 발표 + Q&A**

## 데모 준비 체크리스트

발표 직전 확인:

- [ ] `cd backend && .venv/bin/uvicorn app.main:app --port 8000 --reload &` — 백엔드 :8000
- [ ] `cd frontend && npm run dev` — 프론트엔드 :5173
- [ ] http://localhost:5173 새로고침 → S-001 메인 정상 표시 확인
- [ ] 인사이트 카드 클릭 → 모달 정상 팝업 확인
- [ ] §02 차트 4개 모델 라인 모두 표시 확인
- [ ] §07 글로벌 이벤트 5 카테고리 표시 확인
- [ ] §09 풋바 "🔄 수동 갱신" 버튼 클릭 가능 확인 (실제 클릭은 발표 중에)
- [ ] 다크 모드 토글 작동 확인 (topbar 우측)

## 발표 팁

- **데모는 6번째 섹션** (가장 인상적) — 사전 리허설 권장
- **수동 갱신 실행**은 시간 여유 있을 때 라이브 (1~2분 소요)
- Q&A 질문 예상: P0/P1 로드맵 슬라이드를 참조하면 거의 답변 가능
- 보조 자료가 필요한 경우 [docs/03-do/](../03-do/features/sixsense.do.md) 의 사용자 확장 12 매트릭스 참조
