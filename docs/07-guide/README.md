# 🎓 Sixsense 바이브 코딩 가이드

> **비전문가도 따라할 수 있는 AI 데이터 대시보드 완성 매뉴얼**
> Sixsense (https://sixsense-eta.vercel.app) 의 처음부터 끝까지 — PRD → UI Hand-off → 데이터 수집 → AI 예측 → LLM 인사이트 → Vercel 배포 → 5명 협업 운영까지 한 단계도 빠짐없이.

## 산출물

| 파일 | 용도 |
|---|---|
| [sixsense-vibe-coding-guide.pptx](sixsense-vibe-coding-guide.pptx) | **발표용 PowerPoint** (28슬라이드, Dataiku 브랜드 양식) |
| [README.md](README.md) (이 파일) | **GitHub 즉시 미리보기용 마크다운** (동일 내용) |

## 누구를 위한 가이드인가

- ✅ **비전문가** — 개발 전공 아님, 코딩 부담 큰 분
- ✅ **MBA / 임원 / 기획자** — AI 도구를 활용해 직접 데이터 앱을 만들고 싶은 분
- ✅ **재사용 목적** — DRAM 외 부동산·환율·매출 등 다른 도메인 예측 대시보드 응용

---

## 🗺️ 전체 흐름 (10단계 + 부록 2)

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1. 시작 전 준비           (30분)                        │
│  Step 2. PRD 작성              (2~3시간)                     │
│  Step 3. UI 디자인 Hand-off    (1일)                        │
│  Step 4. React 포팅            (30분~1시간)                  │
│  Step 5. 데이터 수집 (21신호)  (2~3일)                       │
│  Step 6. AI 예측 모델          (1~2일)                       │
│  Step 7. LLM 인사이트          (반나절)                      │
│  Step 8. 백엔드 + 수동 갱신    (1일)                         │
│  Step 9. Vercel + GitHub 배포  (30분)                        │
│  Step 10. 협업 운영            (계속)                        │
│  ─────────────────────────────                              │
│  부록 1. 반드시 피해야 할 실수 (6가지)                       │
│  부록 2. 다른 도메인 응용                                    │
└──────────────────────────────────────────────────────────────┘

총 누적 시간: 약 7~10일 (비전문가 기준, 도구 학습 시간 포함)
```

---

## Step 1. 시작 전 준비 — 30분

**목표**: 작업 환경 구성

**필요 도구** (macOS 기준 / Windows는 WSL2):
- Homebrew · Node 18+ · Python 3.9+ · Git · VS Code(또는 Cursor)
- Claude Code CLI (선택, 권장)

**명령어**:
```bash
# 1) 도구 설치
brew install node python@3.11 git gh

# 2) 프로젝트 폴더 생성
mkdir my-project && cd my-project && git init

# 3) .env 와 .gitignore 미리 생성
touch .env
echo ".env" >> .gitignore
```

**검증**: `node -v && python3 -V && git --version` 모두 출력되면 OK

---

## Step 2. PRD 작성 — 2~3시간

**목표**: 만들 앱의 요구사항을 한 문서(prd.md)로 응축

**필수 18 섹션**:
1. 한 줄 정의 (무엇/누구/왜)
2. 페르소나 3명 + 각 핵심 니즈
3. 핵심 가치 5가지 (차별화 포인트)
4. 화면 목록 14개 (메인 1 + 모달/상세 13)
5. 데이터 신호 목록
6. 위험 분석

**작성 방법**: Claude (대화형) 에 "PRD 만들어줘" 요청 → 2~3회 보완

**검증**: 다른 사람이 읽고 5분 안에 화면 구성을 머릿속에 그릴 수 있는가

---

## Step 3. UI 디자인 — Claude Design Hand-off (1일)

**목표**: 14화면 hifi UI를 받아서 SSOT(단일 진실원)로 보관

**도구 우선순위**:
1. ⭐ **Claude Design** (claude.com/design) — PRD 첨부 + "14화면 hifi 한국어 다크/라이트 모드"
2. **Vercel v0** / **Figma Make** / **Lovable** — 모두 React 코드 출력 가능

**산출물**:
- `design_handoff_<project>/` 폴더에 통째로 보관 (jsx + css + mock data.js)
- 이 폴더가 모든 후속 작업의 **SSOT** — 절대 변경하지 않음

**⚠️ 절대 금지**: 받은 hand-off UI를 무시하고 새로 만들지 말 것 (가장 흔한 실수)

**검증**: hand-off의 mock 데이터로 14화면이 모두 클릭 가능한지 미리 확인

---

## Step 4. React 포팅 — 30분~1시간

**목표**: hand-off를 실행 가능한 React 앱으로 옮기기

**명령어**:
```bash
# 1) Vite 초기화
npm create vite@latest frontend -- --template react-ts

# 2) hand-off 통째로 복사
cp -r design_handoff/src/* frontend/src/

# 3) 의존성 설치 + 실행
cd frontend && npm install && npm run dev
# → http://localhost:5173 자동 열림
```

**검증**: 14화면 모두 클릭 가능 + 다크 모드 토글 작동

**⚠️ 금지**: hand-off CSS 토큰·컴포넌트 임의 변경. 신규 컴포넌트는 hand-off 디자인 토큰(`card`, `ai-note`, `dlabel`)만 조합

---

## Step 5. 데이터 수집 — 21신호 (2~3일)

**목표**: 무료 데이터 21개를 자동 수집해서 매주 갱신 가능하게

**신호 4 종류**:
| Group | 개수 | 예시 |
|---|---|---|
| 정형 (API) | 7 | Yahoo Finance / SEC EDGAR / KOSIS / 관세청 |
| 비정형 (RSS+LLM) | 7 | TechNews / Google News / Hacker News + LLM 분류 |
| 거시 | 6 | FRED (Fed/CPI/10년물 국채) + Yahoo (DXY/KRW/구리) |
| 타겟 | 1 | 예측 대상 (DRAM 가격 프록시 등) |

**LLM 4-tier fallback** (비정형 신호 + 뉴스 분류):
```
Anthropic Claude → Gemini 2.5 Flash → Groq → 키워드 휴리스틱
```

**준비**:
```bash
mkdir backend && cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install requests pandas yfinance feedparser
```

**.env 등록** (절대 commit 금지):
```
KOSIS_API_KEY=...
KCS_API_KEY=...
GEMINI_API_KEY=...
```

**검증**: `backend/data/historical/<signal>.json` 21개 파일 + 각 53주 데이터

---

## Step 6. AI 예측 모델 — Multi-Model (1~2일)

**목표**: 단기/중장기 호라이즌별 최적 모델 자동 선정

**모델 조합** (Sixsense 사례 MAPE):
| 모델 | 구간 | MAPE | 비고 |
|---|---|---|---|
| Prophet | baseline | 7.54% | 단순 baseline |
| HistGBR | 1~7주 | 6.86% | 중간 |
| **sklearn GBR ⭐** | 1~7주 | **4.54%** | **39.8% 개선** |
| **PyTorch LSTM ⭐** | 8~21주 | **9.19%** | 시계열 딥러닝 |

**설치**:
```bash
pip install scikit-learn prophet torch
# macOS 는 brew install libomp 필수 (XGBoost/LightGBM 사용 시)
```

**검증**: 단기 MAPE ≤ 7%, 중장기 MAPE ≤ 12% 목표 (미달 시 신호 추가)

---

## Step 7. LLM 인사이트 — 반나절

**목표**: 21신호 + 뉴스 + 모델 결과를 LLM이 한국어 400자로 종합 분석

**프롬프트 핵심 규칙**:
- 280~360자 사이 (마지막은 마침표로 완결)
- "..." "등 강력한" 같은 미완성 어구 금지
- 중요 단어 3~5개를 `**bold**`로 표시 (UI 강조용)
- 출력: `meta.insight = { headline, summary, tone, confidence, horizon, keySignals, model }`

**UI 표시**:
- 카드 안: 8줄 clamp + fade gradient
- 카드 클릭 → 전체 분석 모달 팝업 (hand-off `<Modal>` 컴포넌트)

**검증**: 모든 문장 한국어 + 마침표 완결 + bold 단어 3개 이상

---

## Step 8. 백엔드 API + 수동 갱신 — 1일

**목표**: FastAPI로 18개 endpoint + 풋바 "🔄 수동 갱신 실행" 버튼

**핵심 endpoint**:
```
GET  /api/snapshot, /api/signals, /api/macro, /api/events, /api/news, ...
POST /api/refresh         ← 5단계 파이프라인 백그라운드 실행
GET  /api/refresh/jobs/{id} ← 진행 상태 폴링
GET  /api/refresh/stages    ← 단계 메타데이터
```

**실행**:
```bash
.venv/bin/uvicorn app.main:app --port 8000 --reload
# → http://localhost:8000/docs (OpenAPI Swagger)
```

**⚠️ 운영 시 주의**: `threading` 대신 `asyncio.create_task` 사용 (`--reload` 모드와 충돌 방지)

---

## Step 9. Vercel + GitHub 시범 배포 — 30분

**목표**: 5명 협업 검토용 HTTPS URL 발급

**5단계**:
```bash
# 1) GitHub CLI 설치 + 인증
brew install gh
gh auth login --web    # 8자리 코드 입력

# 2) vercel.json + .vercelignore 작성 (monorepo 설정)

# 3) git push
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main

# 4) Vercel CLI 인증
npx vercel login

# 5) 배포
npx vercel --prod --yes --name <project-lowercase>
# → https://<project>-<hash>.vercel.app 발급
```

**자동 재배포**: GitHub webhook 자동 등록 → 향후 `git push` 시 자동 빌드 (~2분)

**검증**: HTTPS URL HTTP 200 + 14화면 모두 작동

---

## Step 10. 협업 운영 — 무한 반복

**5명 협업 워크플로우**:
1. Vercel URL을 카톡/Slack에 공유 (OG 메타로 카드 자동 표시)
2. 피드백은 GitHub Issues 또는 화면 캡처
3. 데이터 갱신: 로컬 CLI 5단계 → `git push` → Vercel 자동 재배포

**본격 운영 P0** (배포 전 필수):
- 인증 (Supabase Auth / NextAuth)
- cron 자동 갱신 (GitHub Actions `cron: '0 21 * * 1'`)
- Backend 호스팅 (Railway/Fly.io)
- API 인증 + CORS 운영 도메인

**자주 묻는 질문 (FAQ)**:
| Q | A |
|---|---|
| 다크 모드 안 됨? | `app.jsx` `TWEAK_DEFAULTS.theme: "dark"` 확인 |
| news 영문 그대로? | `korean_title()` 60키워드 매핑 적용 |
| 수동 갱신 안 됨? | uvicorn 살아있는지 + CORS 도메인 확인 |
| 차트가 너무 많이 잘림? | `forecast21` 데이터 + 미디어 쿼리 breakpoint 점검 |

---

## 부록 1. 반드시 피해야 할 실수 (6가지 안티패턴)

| # | 실수 | 해결 |
|---|---|---|
| 1 | Plotly 등 외부 라이브러리로 별도 HTML 생성 | hand-off SSOT 만 사용. 외부 차트 라이브러리 추가 금지 |
| 2 | hand-off UI 무시 + TypeScript 컴포넌트 쇼케이스 새로 작성 | 받은 hand-off가 SSOT — 그대로 React 포팅 |
| 3 | Anthropic 크레딧 부족으로 LLM 막힘 | 4-tier fallback 미리 (Anthropic + Gemini + Groq + 휴리스틱) |
| 4 | news/events 영문 그대로 표시 | `korean_title()` + KEYWORD_MAP 60개 매핑 필수 |
| 5 | `END = "2026-04-30"` 날짜 하드코딩 | `date.today().isoformat()` 동적화 |
| 6 | uvicorn `--reload` + threading 조합 | 운영 시 `asyncio.create_task` 대체 |

---

## 부록 2. 다른 도메인 응용 (재사용)

**동일 프레임워크 (PRD → Hand-off → 데이터 → Multi-Model → LLM)** 으로 다음 도메인에 즉시 응용 가능:

| 도메인 | 21신호 예시 |
|---|---|
| 부동산 가격 | 금리 + 입주물량 + 거래량 + 인허가 + 실거래가 + 부동산 뉴스 + 정책 |
| 환율 예측 | 무역수지 + 외환보유고 + Fed + CPI + 유가 + 중앙은행 코멘트 |
| 매출 예측 | 캘린더(요일/공휴일) + 날씨 + SNS 멘션 + 할인행사 + 경쟁사 가격 |
| 수요 예측 | PMI + 재고/출하 + 원자재 + 환율 + 산업별 뉴스 감성 |
| 주가 예측 | 실적 + ESG + 애널리스트 컨센서스 + 거시 + 산업 뉴스 |

**예측 모델 조합** (검증된 패턴):
- 단기: 트리 (GBR / XGBoost / LightGBM)
- 중장기: 시계열 딥러닝 (LSTM / TFT / Chronos)
- Baseline: Prophet

---

## 📚 참고 자료

- **실제 사례**: https://sixsense-eta.vercel.app (Sixsense — Server DRAM Price Intelligence)
- **GitHub repo**: https://github.com/chaos72/Sixsense
- **PDCA 산출물**: `/docs/00-pm/` (PRD), `/docs/03-do/` (Do), `/docs/05-qa/` (QA)
- **최종 감사 보고서**: [docs/05-qa/sixsense.final-audit.md](../05-qa/sixsense.final-audit.md)

---

## ✉️ 문의

| | |
|---|---|
| 작성 | 김영석 (Sr. Solution Engineer, Dataiku Korea) |
| 과정 | KAIST CAIO 10기 6조 |
| Email | youngseok.kim@dataiku.com |
| GitHub | https://github.com/chaos72/Sixsense |
| Demo | https://sixsense-eta.vercel.app |
