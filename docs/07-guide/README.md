# 🎓 Sixsense 바이브 코딩 가이드 — Sixsense 사례 완전판

> ⚠️ **두 가지 가이드가 있습니다 — 본인 상황에 맞게 선택!**
>
> | 가이드 | 대상 | 예시 앱 | 파일 |
> |---|---|---|---|
> | **A. 일반화 튜토리얼** ⭐ 비전문가 새 앱 만들기 | 처음 시작 | **Stocksense** (주식 예측, 일반화 예시) | [vibe-coding-tutorial.md](vibe-coding-tutorial.md) |
> | B. Sixsense 사례 풀 가이드 (본 파일) | Sixsense 와 똑같이 만들고 싶을 때 / 참고용 | Sixsense (DRAM 가격 예측) | README.md (지금 보는 파일) |
>
> 🎯 **처음 만들 분은 [vibe-coding-tutorial.md](vibe-coding-tutorial.md) 부터 보세요!**
> 본 README 는 Sixsense 의 실제 코드 (code-snippets/) 와 함께 사례 참고용으로 사용하세요.

---

> **목표**: 이 가이드 하나만 보고도 https://sixsense-eta.vercel.app 같은 AI 데이터 대시보드를 비전문가가 처음부터 끝까지 따라 만들 수 있어야 합니다.
> **분량**: 약 5,000 줄. 인쇄 권장하지 않음. GitHub 또는 VS Code 에서 목차 클릭으로 이동하며 읽으세요.

---

## 📚 이 가이드의 사용법

1. **순서대로 읽기**: Step 1 → Step 10 까지 차례로. 절대 건너뛰지 마세요.
2. **명령어는 그대로 복사**: 회색 박스 안 명령어를 터미널에 그대로 붙여넣기 (Cmd+C / Cmd+V).
3. **예상 출력 확인**: 명령어 실행 후 "이렇게 보이면 OK" 박스와 비교.
4. **에러 발생 시**: 각 단계 끝의 "자주 발생하는 에러" 섹션 먼저 확인.
5. **검증 체크리스트**: 각 단계 끝의 ✅ 체크리스트를 모두 통과해야 다음 단계로.

## 🎁 실제 작동하는 코드 (code-snippets/)

본 가이드의 모든 코드는 [code-snippets/](code-snippets/) 폴더에 **실제로 작동하는 풀 버전**으로 들어 있습니다. 가이드 본문에는 핵심 패턴만 보여드리고, 실제 사용은 `code-snippets/` 의 파일을 그대로 복사합니다.

```
docs/07-guide/code-snippets/
├── requirements.txt              # Python 의존성 (정확한 버전)
├── .env.example                  # API 키 템플릿
├── pipelines/
│   ├── auto_collectors.py        # 21신호 수집 (969줄)
│   ├── collect_news_events.py    # RSS + LLM 분류 (1108줄)
│   ├── forecast_v2.py            # Multi-Model 학습 (430줄)
│   ├── build_insight.py          # LLM 인사이트 (399줄)
│   ├── build_frontend_data.py    # data.js 자동 생성 (566줄)
│   └── preprocessing.py          # 전처리 유틸 (141줄)
├── app/
│   └── main.py                   # FastAPI 18 endpoints (476줄)
├── frontend/
│   ├── app.jsx                   # 메인 + 라우팅 (196줄)
│   ├── dashboard.jsx             # S-001 메인 화면 (595줄)
│   ├── components.jsx            # 공통 컴포넌트 (386줄)
│   ├── styles.css                # 디자인 토큰 + 전체 CSS (1079줄)
│   ├── package.json              # npm 의존성
│   └── index.html
└── deploy/
    ├── vercel.json               # Vercel 배포 설정
    ├── .vercelignore             # 배포 제외 목록
    └── .gitignore                # Git 제외 목록
```

**사용 방법** (가이드 Step 5~9 에서 안내):
```bash
# 예: Step 5 의 21 collector 코드를 그대로 사용
cp docs/07-guide/code-snippets/pipelines/auto_collectors.py \
   backend/pipelines/

# 예: Step 9 의 vercel 설정 그대로 사용
cp docs/07-guide/code-snippets/deploy/vercel.json \
   ~/Documents/my-project/
```

이 코드들은 실제 https://sixsense-eta.vercel.app 을 만든 코드와 동일합니다. 그대로 복사 후 본인 도메인에 맞게 수정만 하면 됩니다.

## 📖 목차

| # | 단계 | 예상 시간 | 난이도 |
|---|---|---|---|
| **준비** | [Step 0. 이 가이드 시작 전](#step-0-이-가이드-시작-전) | 5분 | ⭐ |
| **Phase 1: 환경** | [Step 1. 도구 설치와 환경 구성](#step-1-도구-설치와-환경-구성) | 30~60분 | ⭐⭐ |
| **Phase 2: 기획** | [Step 2. PRD 작성](#step-2-prd-작성) | 2~3시간 | ⭐ |
| **Phase 3: 디자인** | [Step 3. UI 디자인 — Claude Design Hand-off](#step-3-ui-디자인--claude-design-hand-off) | 1일 | ⭐⭐ |
| **Phase 4: 개발** | [Step 4. React 포팅](#step-4-react-포팅) | 30분~1시간 | ⭐⭐⭐ |
| | [Step 5. 데이터 수집 (21신호)](#step-5-데이터-수집-21신호) | 2~3일 | ⭐⭐⭐⭐ |
| | [Step 6. AI 예측 모델 (Multi-Model)](#step-6-ai-예측-모델-multi-model) | 1~2일 | ⭐⭐⭐⭐ |
| | [Step 7. LLM 인사이트](#step-7-llm-인사이트) | 반나절 | ⭐⭐⭐ |
| | [Step 8. 백엔드 API + 수동 갱신](#step-8-백엔드-api--수동-갱신) | 1일 | ⭐⭐⭐ |
| **Phase 5: 배포** | [Step 9. Vercel + GitHub 시범 배포](#step-9-vercel--github-시범-배포) | 30분 | ⭐⭐ |
| **Phase 6: 운영** | [Step 10. 협업 운영](#step-10-협업-운영) | 계속 | ⭐ |
| **부록** | [부록 A. 반드시 피해야 할 실수](#부록-a-반드시-피해야-할-실수-6가지-안티패턴) | — | — |
| | [부록 B. 다른 도메인 응용](#부록-b-다른-도메인-응용) | — | — |
| | [부록 C. 자주 묻는 질문 (FAQ)](#부록-c-자주-묻는-질문-faq) | — | — |
| | [부록 D. 전체 디렉토리 구조](#부록-d-전체-디렉토리-구조) | — | — |

---

## Step 0. 이 가이드 시작 전

### 0.1. 이 가이드는 누구를 위한 것인가

- ✅ **비전문가**: 프로그래밍 경험이 없거나 부족한 분
- ✅ **MBA / 임원 / 기획자**: AI 도구를 활용해 직접 데이터 앱을 만들고 싶은 분
- ✅ **재사용 목적**: DRAM 외 다른 도메인(부동산·환율·매출 등)에 응용하고 싶은 분

### 0.2. 마지막에 얻을 결과물

이 가이드를 끝까지 따라하면 다음과 같은 결과물을 갖게 됩니다:

```
✅ HTTPS URL 1개 (예: https://my-project.vercel.app)
   - 14화면 hifi UI (다크/라이트 모드 토글)
   - 21개 실데이터 신호 자동 수집
   - Multi-Model AI 예측 (단기 MAPE 4.54%, 중장기 9.19%)
   - LLM 종합 인사이트 (한국어 400자)
   - 매주 화요일 자동 갱신 (cron 등록 시)

✅ GitHub repo 1개 (예: github.com/<your>/<project>)
   - 모든 코드 + 데이터 + PRD/Design/QA 문서
   - 다른 사람이 git clone 받아서 그대로 재현 가능

✅ 본인 능력
   - 다른 도메인(부동산/환율/매출 등)에 같은 패턴 적용 가능
```

### 0.3. 작업 환경 가정

이 가이드는 다음 환경을 가정합니다:
- **OS**: macOS (Apple Silicon M1/M2/M3 또는 Intel)
- **인터넷**: 안정적인 연결 (외부 API 호출 + Vercel 배포)
- **계정**: GitHub 계정 1개, Vercel 계정 1개 (둘 다 무료)
- **시간**: 총 7~10일 (도구 학습 포함, 한 번에 다 할 필요 없음)

**Windows 사용자**: WSL2 (Ubuntu) 또는 Git Bash 환경에서 거의 동일하게 작동합니다. 일부 brew 명령은 apt 또는 winget 으로 대체.

### 0.4. 도움 받기

각 단계에서 막히면:
1. 해당 단계 끝의 **"자주 발생하는 에러"** 섹션 먼저 확인
2. [부록 C. FAQ](#부록-c-자주-묻는-질문-faq) 검색
3. Claude (claude.ai) 에 에러 메시지 그대로 붙여넣기 + "어떻게 해결?" 질문
4. GitHub Issues 검색: https://github.com/chaos72/Sixsense/issues

### 0.5. 시작 전 마음가짐

- **완벽주의 X**: 첫 시도에 모든 게 완벽하지 않음. 한 단계씩 작동하면 OK.
- **AI 활용 적극**: Claude 와 대화하며 진행. AI 가 코드 짜주고 디버깅 도와줍니다.
- **백업 습관**: 매 단계마다 `git commit` (Step 1.5 에서 배움). 잘못 가도 되돌릴 수 있음.

---

## Step 1. 도구 설치와 환경 구성

> **예상 시간**: 30~60분 (이미 설치된 도구가 있으면 5~15분)
> **목표**: 작업에 필요한 모든 도구를 설치하고 첫 프로젝트 폴더를 만든다.

### 1.1. macOS 기본 점검

먼저 터미널을 엽니다.
- Spotlight (Cmd+Space) → "터미널" 입력 → Enter

다음 명령을 그대로 복사해서 붙여넣고 Enter:

```bash
sw_vers
```

**이렇게 보이면 OK** ✅:
```
ProductName:     macOS
ProductVersion:  14.x (또는 13.x, 15.x 등)
BuildVersion:    xxxxx
```

macOS 12 이하라면 [System Settings → General → Software Update] 에서 업데이트 권장.

### 1.2. Homebrew 설치 (macOS 패키지 매니저)

**Homebrew 가 이미 설치되어 있는지 확인**:
```bash
which brew
```

- `brew not found` 면 아직 설치 안 됨 → 아래 명령으로 설치
- `/opt/homebrew/bin/brew` 또는 `/usr/local/bin/brew` 출력되면 이미 설치됨 → 1.3 으로

**Homebrew 설치 명령**:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 중 macOS 비밀번호 입력 요청 → 본인 비밀번호 입력 (화면에 안 보임, 그냥 타이핑 후 Enter).
- 약 5~10분 소요
- 마지막에 "Next steps" 가 출력되면 시키는 대로 `eval "$(/opt/homebrew/bin/brew shellenv)"` 같은 명령 실행

**설치 확인**:
```bash
brew --version
```

**이렇게 보이면 OK** ✅: `Homebrew 4.x.x` 또는 그 이상

### 1.3. 필수 도구 한 번에 설치

다음 명령 한 줄로 모두 설치:

```bash
brew install node python@3.11 git gh
```

- **node**: JavaScript 런타임 (Vite + React 빌드용)
- **python@3.11**: 백엔드 + AI 모델용
- **git**: 버전 관리
- **gh**: GitHub CLI (인증 + repo 관리)

설치 시간 약 3~5분. 완료 후 각 도구 버전 확인:

```bash
node --version    # v20.x.x 이상 (또는 v18 이상)
python3 --version # Python 3.11.x
git --version     # git version 2.x.x
gh --version      # gh version 2.x.x
```

**4개 모두 출력되면 OK** ✅

### 1.4. VS Code 또는 Cursor 설치 (코드 편집기)

다음 중 하나 선택:

**옵션 A: VS Code (Microsoft, 무료, 가장 일반적)**
1. https://code.visualstudio.com 접속
2. "Download for Mac" 클릭 → .zip 다운로드
3. 압축 해제 → Applications 폴더로 드래그
4. Launchpad 에서 VS Code 실행

**옵션 B: Cursor (VS Code 기반 + AI 통합, 권장)** ⭐
1. https://cursor.sh 접속
2. "Download" → macOS 다운로드
3. 동일하게 Applications 폴더로 설치
4. 첫 실행 시 Claude/GPT-4 등 AI 모델 선택

**옵션 C: Claude Code CLI (터미널 기반, 권장 추가)** ⭐
- Claude 가 직접 터미널에서 파일 편집 + 명령 실행
- 설치:
```bash
curl -fsSL https://claude.ai/install.sh | sh
```
- 인증: `claude login` 명령 후 브라우저에서 Anthropic 계정 로그인

### 1.5. Git 기본 설정

본인 이름과 이메일 등록 (commit 시 표시됨):

```bash
git config --global user.name "본인 이름"
git config --global user.email "your-email@example.com"
```

확인:
```bash
git config --global --list | grep user
```

**이렇게 보이면 OK** ✅:
```
user.name=본인 이름
user.email=your-email@example.com
```

### 1.6. 프로젝트 폴더 생성

원하는 위치(예: ~/Documents)에 프로젝트 폴더 만들기:

```bash
cd ~/Documents
mkdir my-project
cd my-project
git init
```

`git init` 출력:
```
Initialized empty Git repository in /Users/<your>/Documents/my-project/.git/
```

### 1.7. .env 와 .gitignore 미리 생성 (보안!)

**.env 파일** (API 키 저장용, 절대 GitHub 에 올리면 안 됨):
```bash
touch .env
```

**.gitignore 파일** (Git 에서 무시할 파일 목록):
```bash
cat > .gitignore << 'EOF'
# Secrets — NEVER commit
.env
.env.*
!.env.example

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp

# Logs
*.log

# Node / Vite
node_modules/
dist/
.vite/
*.tsbuildinfo

# Python
.venv/
__pycache__/
*.pyc
*.pyo

# Vercel
.vercel
EOF
```

**확인**:
```bash
ls -la
```

**이렇게 보이면 OK** ✅: `.env`, `.gitignore`, `.git/` 폴더가 모두 보임

### 1.8. 첫 commit (백업 습관)

```bash
git add .gitignore
git commit -m "chore: 초기 환경 구성 — .gitignore 추가"
```

**출력**:
```
[main (root-commit) xxxxxxx] chore: 초기 환경 구성 — .gitignore 추가
 1 file changed, ...
```

### Step 1 검증 체크리스트 ✅

- [ ] `brew --version` → Homebrew 4.x 이상
- [ ] `node --version` → v18 이상
- [ ] `python3 --version` → 3.9 이상
- [ ] `git --version` → 2.x
- [ ] `gh --version` → 2.x (설치 확인만, 인증은 Step 9 에서)
- [ ] VS Code 또는 Cursor 또는 Claude Code 중 1개 이상 설치 완료
- [ ] `git config user.name` + `user.email` 설정 완료
- [ ] `~/Documents/my-project/` 생성 + `.git/` + `.env` + `.gitignore` 존재
- [ ] 첫 commit 성공

### 자주 발생하는 에러 (Step 1)

**Q1: `brew: command not found`**
- A: Homebrew 설치 후 셸 재시작 필요. 터미널 종료 후 다시 열기 또는:
  ```bash
  eval "$(/opt/homebrew/bin/brew shellenv)"   # Apple Silicon
  eval "$(/usr/local/bin/brew shellenv)"      # Intel
  ```

**Q2: `xcode-select: error: invalid developer directory`**
- A: Xcode Command Line Tools 가 필요. 설치:
  ```bash
  xcode-select --install
  ```

**Q3: `python3: command not found`**
- A: macOS 에 기본 python3 가 없거나 PATH 문제. `brew install python@3.11` 후 새 터미널 열기.

**Q4: 비밀번호 입력 시 아무것도 안 보임**
- A: 정상입니다. macOS sudo 는 입력 중 화면에 표시하지 않습니다. 그냥 타이핑하고 Enter.

**Q5: GitHub 계정 만들기는?**
- A: https://github.com/join 에서 무료 가입. Step 9 에서 사용.

---

## Step 2. PRD 작성

> **예상 시간**: 2~3시간 (Claude 와 대화하며)
> **목표**: 만들 앱의 요구사항을 한 마크다운 파일(prd.md)로 응축한다.
> **결과물**: `~/Documents/my-project/prd.md` (약 300~500줄)

### 2.1. PRD 가 왜 중요한가

PRD (Product Requirements Document) 가 없으면:
- ❌ 무엇을 만들지 모호함 → 작업이 산으로 감
- ❌ 화면이 머릿속에만 있음 → 협업 불가능
- ❌ AI 에게 시킬 때 같은 설명 반복 → 시간 낭비

PRD 가 있으면:
- ✅ Claude Design 에 PRD 한 번 첨부 → 14화면 즉시 생성
- ✅ 다른 사람이 5분 안에 프로젝트 이해
- ✅ 추후 PDCA (계획-실행-검토-개선) 의 기준점

### 2.2. PRD 필수 18 섹션

```
1.  한 줄 정의 (What/Who/Why)
2.  배경과 동기 (Why now)
3.  목표와 비목표 (Goal/Non-goal)
4.  페르소나 (사용자 3종)
5.  핵심 가치 명제 (Value Prop 5가지)
6.  사용자 여정 (User Journey)
7.  화면 목록 (14화면 권장)
8.  핵심 기능 (Feature List)
9.  데이터 신호 (Data Sources)
10. AI 모델 전략
11. 시스템 아키텍처 (간단히)
12. API 명세 (간단히)
13. 디자인 토큰 (색상/폰트)
14. 검증 기준 (L1/L2/L3 테스트)
15. 위험 분석 (Risk)
16. 일정 (Milestone)
17. 미래 계획 (Future Work)
18. 참고 자료
```

### 2.3. Claude 와 대화로 PRD 작성하기

**Step 2.3.1**. claude.ai 접속 → 로그인 → 새 대화 시작

**Step 2.3.2**. 첫 프롬프트 (그대로 복사 후 본인 주제로 수정):

```
나는 비전문가입니다. 다음 앱의 PRD를 마크다운으로 작성해주세요.
파일명: prd.md
형식: 18 섹션 (한 줄 정의 / 배경 / 목표 / 페르소나 3명 / 핵심 가치 5가지 /
       사용자 여정 / 화면 14개 / 기능 / 데이터 신호 / AI 모델 / 아키텍처 /
       API / 디자인 토큰 / 검증 / 위험 / 일정 / 미래 / 참고)

앱 주제: [본인 주제 입력. 예: 서버용 DRAM 가격을 예측하는 B2B 대시보드]

대상 사용자: [예: 메모리 반도체 기획팀 + 시장정보 애널리스트 + 영업 담당]

핵심 차별점: [예: 21개 실데이터 자동 수집 + Multi-Model + LLM 인사이트]

기간: 4주 안에 시범 데모 가능
예산: 무료 도구만 사용
```

**Step 2.3.3**. Claude 가 약 1~2분 후 PRD 초안 출력

**Step 2.3.4**. 출력된 마크다운을 복사해서 파일로 저장:
```bash
cd ~/Documents/my-project
# VS Code/Cursor 에서 prd.md 새 파일 생성 → Claude 출력 붙여넣기 → 저장
# 또는 터미널에서:
pbpaste > prd.md   # 클립보드의 PRD를 prd.md로 저장
```

### 2.4. PRD 보완 (필수 2~3회)

첫 번째 PRD 는 보통 부족합니다. 다음 항목을 Claude 에게 추가 요청:

**보완 요청 1**: 화면 14개를 더 자세히
```
앞서 만든 PRD에 화면 14개를 각각 다음 형식으로 자세히 설명해주세요:
- ID (S-001 ~ S-014)
- 화면 이름
- 핵심 위젯 목록
- 사용자 행동 (클릭 시 어디로?)
- mock 데이터 예시
```

**보완 요청 2**: 데이터 신호 21개 명세
```
PRD에 21개 데이터 신호를 다음 형식으로 추가해주세요:
- ID (A-1 ~ A-7, B-1 ~ B-7, macro-fed/dxy/pmi/krw/cu/ust10, target)
- 신호 이름
- 데이터 소스 (Yahoo Finance / FRED / 등 — 무료 API 만)
- 갱신 주기 (일간/주간/월간)
- 단위
- 예상 값 범위
```

**보완 요청 3**: 페르소나별 시나리오
```
PRD의 페르소나 3명 각각에 대해 다음을 추가해주세요:
- 하루 일과 (몇 시에 이 앱을 봄?)
- 가장 중요하게 보는 화면 (S-001 / S-002 등)
- 의사결정 흐름 (이 앱을 보고 무엇을 함?)
```

### 2.5. PRD 검증

작성된 prd.md 를 처음 보는 사람에게 보여주고 5분 안에 답할 수 있어야 합니다:

| Q | A |
|---|---|
| 무엇을 만드는 앱인가? | 한 줄 정의 섹션에서 |
| 누가 쓰는가? | 페르소나 섹션 |
| 핵심 화면 3개는? | 화면 목록 14개 중 메인 (S-001) + 상세 2개 |
| 데이터는 어디서? | 데이터 신호 섹션 |
| AI 가 무엇을 함? | AI 모델 전략 섹션 |
| 언제 완성? | 일정 섹션 |

### 2.6. PRD git 백업

```bash
cd ~/Documents/my-project
git add prd.md
git commit -m "docs(pm): PRD 초안 — 18섹션 + 14화면 + 21신호 명세"
```

### Step 2 검증 체크리스트 ✅

- [ ] `prd.md` 파일 존재 (~/Documents/my-project/prd.md)
- [ ] 18 섹션 모두 채워짐 (각 섹션 최소 1 문단)
- [ ] 페르소나 3명 + 핵심 가치 5가지 명시
- [ ] 화면 14개 (S-001~S-014) ID + 이름 + 위젯 목록
- [ ] 데이터 신호 21개 (A/B/macro/target) ID + 소스 + 단위
- [ ] git commit 완료

### 자주 발생하는 에러 (Step 2)

**Q1: Claude 가 PRD 를 너무 짧게 만든다**
- A: "더 자세히, 각 섹션당 최소 1 페이지 분량" 명시 + 보완 요청 2~3회.

**Q2: 14화면을 어떻게 정해야 할지 모르겠다**
- A: 메인 1 + 모달/팝업 8 + 풀페이지 상세 5 = 14. Sixsense 사례 참고:
  ```
  S-001: 메인 대시보드
  S-002: AI 예측 근거 (모달)
  S-003: 정형 데이터 상세 (모달)
  S-004: 비정형 데이터 상세 (모달)
  ... S-014 까지
  ```

**Q3: 데이터 21개를 어떻게 정하나?**
- A: 정형 7 + 비정형 7 + 거시 6 + 타겟 1 = 21 패턴 권장. 도메인별 응용은 [부록 B](#부록-b-다른-도메인-응용) 참조.

**Q4: docx 로 PRD 가 있는데 md 로 바꾸려면?**
- A:
  ```bash
  # macOS: pandoc 설치 후 변환
  brew install pandoc
  pandoc prd.docx -o prd.md
  ```

---

---

## Step 3. UI 디자인 — Claude Design Hand-off

> **예상 시간**: 4~8시간 (디자인 도구 학습 포함하면 1일)
> **목표**: 14화면 hifi UI 를 한 번에 받아서 SSOT(단일 진실원)로 보관.
> **결과물**: `~/Documents/my-project/design_handoff/` 폴더 안에 jsx + css + mock data.js.

### 3.1. ⚠️ 가장 중요한 원칙

**이 단계에서 받은 hand-off 가 모든 후속 작업의 SSOT(Single Source of Truth) 입니다.**

- ❌ **절대 금지**: 받은 hand-off 를 무시하고 React 컴포넌트를 새로 만들기
- ❌ **절대 금지**: 외부 차트 라이브러리(Plotly/Recharts/D3) 로 별도 HTML 생성
- ❌ **절대 금지**: hand-off CSS 토큰을 마음대로 바꾸기

이 원칙을 어기면 → 디자이너가 만든 UI 와 실제 화면이 달라짐 → 결국 모두 폐기하고 다시 작업 (Sixsense 제작 중 실제 겪음).

### 3.2. UI 디자인 도구 3가지 (우선순위)

| 도구 | 장점 | 단점 | URL |
|---|---|---|---|
| ⭐ **Claude Design** | PRD 첨부 → 14화면 한 번에 / React 코드 출력 / 한국어 OK | Anthropic 계정 필요 (Pro 권장) | https://claude.com/design |
| **Vercel v0** | UI 컴포넌트 빠르게 / React + Tailwind 출력 | 한 번에 1~2 화면씩, 14화면 만들려면 반복 | https://v0.dev |
| **Lovable** | 풀스택 (백엔드 포함) / Live preview | 무료 한도 제한 / 한국어 디자인 약함 | https://lovable.dev |

이 가이드는 **Claude Design 기준**으로 설명합니다.

### 3.3. Claude Design 사용법 (단계별)

**Step 3.3.1**. https://claude.com/design 접속 → "Start designing" 클릭

**Step 3.3.2**. 새 프로젝트 생성 → 이름: "My Project Dashboard"

**Step 3.3.3**. 좌측 채팅창에 PRD 첨부 (📎 아이콘 클릭 → `~/Documents/my-project/prd.md` 선택)

**Step 3.3.4**. 다음 프롬프트 입력 (그대로 복사 후 본인 정보로 수정):

```
첨부한 PRD를 바탕으로 다음 요구사항으로 hifi UI를 만들어주세요.

요구사항:
1. 화면 수: 14개 (PRD의 S-001 ~ S-014 그대로)
2. 언어: 한국어 100% (라벨/제목/본문)
3. 폰트: Pretendard Variable (한글) + JetBrains Mono (숫자/.num 클래스)
4. 다크/라이트 모드: 토글 버튼으로 전환 가능 (topbar 우측)
5. 색상 토큰:
   - 배경: warm white #fafaf8 (light) / #1a1a1c (dark)
   - 강조: pos #16a34a / neu #ca8a04 / neg #dc2626 / info #2563eb
6. 메인 화면(S-001) 구성:
   - §01 가격 스냅샷 (3카드 + 인사이트 카드, 4분화 또는 5분화)
   - §02 52주 히스토리 차트 + 1~21주 예측
   - §03 14 신호 카드 그리드
   - §05 AI 뉴스 리스트
   - §06 거시경제 6 카드
   - §07 글로벌 이벤트 리스트
   - §09 풋바: 갱신 시각 + 수동 갱신 버튼
7. 모달/팝업: S-002 ~ S-013 은 모달, S-006/S-008/S-010/S-012/S-014 는 풀페이지
8. 산출물: hand-off 패키지 (React jsx + CSS + mock data.js)

mock 데이터는 PRD의 데이터 신호 21개를 모두 채워서 14화면이 실데이터처럼
표시되게 해주세요.
```

**Step 3.3.5**. Claude Design 이 약 5~15분 동안 14화면 생성. 우측 프리뷰에서 모든 화면 클릭하며 검토.

**Step 3.3.6**. 마음에 안 드는 부분이 있으면 채팅창에 수정 요청:
```
S-001 메인 대시보드의 §02 차트가 너무 작아요. 화면 너비의 80%로 키워주세요.
```

### 3.4. Hand-off 패키지 다운로드

**Step 3.4.1**. Claude Design 우측 상단 "Export" 또는 "Hand-off" 버튼 클릭

**Step 3.4.2**. 옵션:
- ✅ "Include source files" (jsx 파일 포함)
- ✅ "Include mock data" (data.js 포함)
- ✅ "Format: React" (Next.js 가 아닌 일반 React)

**Step 3.4.3**. .zip 파일 다운로드 → `~/Documents/my-project/` 로 이동 → 압축 해제

### 3.5. Hand-off 폴더 구조 확인

```bash
cd ~/Documents/my-project/design_handoff
ls -la
```

**이렇게 보이면 OK** ✅:
```
README.md          # hand-off 설명서 (필독!)
src/
├── app.jsx        # 메인 앱 + 라우팅
├── dashboard.jsx  # S-001 메인 대시보드
├── modals.jsx     # S-002~S-013 모달
├── pages.jsx      # S-006/008/010/012/014 풀페이지
├── components.jsx # 공통 컴포넌트 (Sig/MetricCard/Modal 등)
├── mocks/
│   └── data.js    # mock 데이터 (21신호 + news + events + macro)
└── styles/
    └── styles.css # 전체 CSS (디자인 토큰 + 컴포넌트)
```

### 3.6. Hand-off README 정독

```bash
cat design_handoff/README.md | head -100
```

특히 다음 항목을 메모:
- **디자인 토큰**: 색상 변수 (--text / --surface / --sig-pos 등)
- **컴포넌트 사용법**: Sig, MetricCard, Modal, AiNote 등
- **데이터 스키마**: SIXSENSE_DATA 또는 비슷한 이름의 mock data 구조

### 3.7. mock data 로 hand-off 미리보기

Claude Design 의 프리뷰가 사라지기 전에 hand-off 가 mock data 로 정상 작동하는지 확인:

```bash
cd ~/Documents/my-project/design_handoff
# README 에 npm 명령이 있다면:
npm install
npm run dev
# 또는 그냥 Live Server 같은 VS Code 확장으로 index.html 열기
```

브라우저에서 14화면 모두 클릭하며 확인.

### 3.8. Hand-off git 백업

```bash
cd ~/Documents/my-project
git add design_handoff/
git commit -m "design: Claude Design hand-off — 14화면 hifi + mock data"
```

### Step 3 검증 체크리스트 ✅

- [ ] `design_handoff/` 폴더 존재
- [ ] `design_handoff/src/{app,dashboard,modals,pages,components}.jsx` 5개 파일 존재
- [ ] `design_handoff/src/mocks/data.js` 존재 + 21신호 mock 데이터 포함
- [ ] `design_handoff/src/styles/styles.css` 존재
- [ ] mock data 로 14화면 미리보기 정상 작동
- [ ] git commit 완료

### 자주 발생하는 에러 (Step 3)

**Q1: Claude Design 이 14화면을 다 안 만든다 (8~9개만)**
- A: "S-008 부터 S-014 까지 누락됐어요. 만들어주세요" 추가 요청.

**Q2: 한국어 텍스트가 깨진다**
- A: 프롬프트에 "폰트: Pretendard Variable 명시" + 다시 요청.

**Q3: hand-off 파일이 .tsx (TypeScript) 인데 .jsx 가 편하다**
- A: 그대로 사용. Vite 가 둘 다 지원. 또는 Claude 에게 "JSX 로만 변환" 요청.

**Q4: mock data 가 너무 단순함 (값이 0/null 만 있음)**
- A: "mock data 를 PRD 의 21신호 각각에 대해 53주 분량으로 채워주세요" 요청.

**Q5: 다크 모드 색상이 어색하다**
- A: "다크 모드 배경 #1a1a1c, 글자 #f4f3ef, accent #3EDAB2 같이 명확히 지정해주세요" 요청.

---

## Step 4. React 포팅

> **예상 시간**: 30분 ~ 1시간
> **목표**: hand-off 패키지를 실행 가능한 React 앱으로 옮기고 `npm run dev` 로 띄운다.
> **결과물**: `~/Documents/my-project/frontend/` 안에서 `http://localhost:5173` 정상 작동.

### 4.1. Vite + React 19 + TypeScript 프로젝트 초기화

```bash
cd ~/Documents/my-project
npm create vite@latest frontend -- --template react-ts
```

질문에 다음과 같이 답:
- "Need to install the following packages: create-vite" → **Y** Enter
- (자동 진행)

**완료 후 출력**:
```
Done. Now run:

  cd frontend
  npm install
  npm run dev
```

### 4.2. hand-off 의 src 통째로 복사

```bash
cp -r design_handoff/src/* frontend/src/
```

기존 frontend/src/App.tsx, main.tsx 등이 덮어쓰기 될 수 있음. 확인:
```bash
ls frontend/src/
```

**이렇게 보이면 OK** ✅:
```
app.jsx
components.jsx
dashboard.jsx
modals.jsx
pages.jsx
mocks/      # data.js 포함
styles/     # styles.css 포함
main.tsx    # Vite 기본 entry (수정 필요)
```

### 4.3. main.tsx 가 app.jsx 를 import 하도록 수정

```bash
cd frontend/src
cat > main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './app.jsx'
import './styles/styles.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
EOF
```

기존의 import App from './App' 같은 줄을 위 내용으로 교체. (VS Code 에서 직접 편집해도 됨)

### 4.4. index.html 수정 (title + meta)

```bash
cd ~/Documents/my-project/frontend
```

`index.html` 파일을 VS Code/Cursor 에서 열어서 다음으로 수정:

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My Project — 짧은 설명</title>
    <meta name="description" content="긴 설명. 검색엔진과 OG 카드용." />
    <meta property="og:title" content="My Project — 짧은 설명" />
    <meta property="og:description" content="긴 설명 동일." />
    <meta property="og:type" content="website" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### 4.5. 의존성 설치

```bash
cd ~/Documents/my-project/frontend
npm install
```

약 1~3분 소요. 출력:
```
added 250+ packages in 90s
```

### 4.6. 개발 서버 실행

```bash
npm run dev
```

**이렇게 보이면 OK** ✅:
```
  VITE v8.x.x  ready in 200 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 4.7. 브라우저에서 확인

http://localhost:5173 접속.

**확인 항목**:
- [ ] S-001 메인 대시보드가 표시되는가?
- [ ] §01 가격 스냅샷 3 카드 + 인사이트 영역 보이는가?
- [ ] §02 차트가 표시되는가? (mock data 기준)
- [ ] §06 거시경제 6 카드 보이는가?
- [ ] topbar 우측의 ☀/☾ 토글 버튼 클릭 → 다크/라이트 전환되는가?
- [ ] 카드 클릭 시 모달이 뜨는가?

### 4.8. 첫 commit + .gitignore 확인

```bash
cd ~/Documents/my-project
git status
```

`frontend/node_modules/` 가 보이면 .gitignore 가 제대로 작동 안 함. 확인:

```bash
cat .gitignore | grep node_modules
```

`node_modules/` 라인 없으면 추가:
```bash
echo "node_modules/" >> .gitignore
```

그 다음:
```bash
git add frontend/ design_handoff/
git commit -m "feat: hand-off → React 포팅 (Vite + React 19 + TS)"
```

### Step 4 검증 체크리스트 ✅

- [ ] `frontend/` 폴더 생성 + Vite 초기화 완료
- [ ] `frontend/src/{app,dashboard,modals,pages,components}.jsx` 복사 완료
- [ ] `frontend/src/main.tsx` 가 `./app.jsx` import
- [ ] `frontend/src/mocks/data.js` 와 `frontend/src/styles/styles.css` 복사 완료
- [ ] `npm install` 성공 (node_modules 약 250+ 패키지)
- [ ] `npm run dev` 후 http://localhost:5173 HTTP 200
- [ ] 14화면 모두 클릭 가능 + 다크 모드 토글 작동
- [ ] git commit 완료

### 자주 발생하는 에러 (Step 4)

**Q1: `Error: Cannot find module './app.jsx'`**
- A: main.tsx 의 import 경로 확인. 대소문자 정확히. `'./app.jsx'` 가 맞음 (App.jsx 아님).

**Q2: 화면이 흰색이고 아무것도 안 뜸**
- A: 브라우저 개발자 도구(F12) → Console 탭. 에러 메시지 확인. 보통:
  - "Failed to fetch module" → import 경로 오타
  - "data is undefined" → mocks/data.js 에 export 확인

**Q3: 한글이 깨짐 (□□□)**
- A: index.html `<html lang="ko">` 확인 + styles.css 에 Pretendard 폰트 link 확인. 또는:
```html
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" rel="stylesheet">
```
를 `<head>` 안에 추가.

**Q4: 다크 모드 토글이 안 보임**
- A: `app.jsx` 의 topbar 영역에 `<button onClick={...theme toggle...}>` 있는지 확인. 없으면 Claude 에게 "topbar 우측에 다크/라이트 토글 버튼 추가" 요청.

**Q5: 차트가 비어있음 (선이 안 그려짐)**
- A: `frontend/src/mocks/data.js` 에서 `SIXSENSE_DATA.history`, `forecast7`, `forecast21` 배열 확인. 비어있으면 mock data 가 부족함. Claude Design 으로 돌아가 보완.

---

## Step 5. 데이터 수집 (21신호)

> **예상 시간**: 2~3일 (신호 수와 API 학습 시간에 비례)
> **목표**: 무료 API 21개를 자동으로 수집해서 매주 갱신 가능하게 만든다.
> **결과물**: `backend/data/historical/<signal>.json` 21개 파일 (각 53주 시계열).

### 5.1. 21신호 구성 패턴

DRAM 외 다른 도메인에도 적용 가능한 일반화 패턴:

```
정형 (API 호출, 7개): 가격/거래량/주가/지표 등 숫자 데이터
비정형 (RSS + LLM, 7개): 뉴스/SNS/실적발표 등 텍스트 → LLM 분류
거시 (FRED + Yahoo, 6개): 금리/환율/원자재/PMI 등
타겟 (1개): 예측 대상 (DRAM 가격 / 부동산 가격 / 환율 등)
─────
합계 21개
```

### 5.2. backend 폴더 + Python 환경 구성

```bash
cd ~/Documents/my-project
mkdir backend && cd backend
python3 -m venv .venv
source .venv/bin/activate
```

활성화 확인:
```bash
which python3
```

**이렇게 보이면 OK** ✅: `/Users/.../my-project/backend/.venv/bin/python3`

### 5.3. 핵심 패키지 설치

```bash
pip install requests pandas numpy yfinance feedparser python-dotenv
```

데이터 분석/예측용 (Step 6에서도 사용):
```bash
pip install scikit-learn prophet torch
```

### 5.4. 폴더 구조 생성

```bash
mkdir -p data/historical data/forecast data/news data/events data/insight
mkdir -p pipelines
mkdir -p app
```

**구조 확인**:
```
backend/
├── .venv/                # Python 가상환경
├── app/                  # FastAPI (Step 8)
├── pipelines/            # 데이터 수집 + 모델 + 인사이트 스크립트
└── data/
    ├── historical/       # 21신호 시계열 JSON
    ├── forecast/         # 예측 결과
    ├── news/             # 뉴스
    ├── events/           # 이벤트
    └── insight/          # LLM 인사이트
```

### 5.5. .env 에 API 키 등록

`~/Documents/my-project/.env` 파일에 다음 추가 (각 키 발급 방법은 5.7 참고):

```bash
# 데이터 API (모두 무료)
KOSIS_API_KEY=               # 통계청 https://kosis.kr/openapi/
KCS_API_KEY=                 # 관세청 https://unipass.customs.go.kr/openapi/
AWS_ACCESS_KEY_ID=           # AWS Spot 가격 (선택)
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# LLM API (1개 이상 권장, 무료 tier 있음)
ANTHROPIC_API_KEY=           # https://console.anthropic.com ($5 충전 권장)
GEMINI_API_KEY=              # https://aistudio.google.com (무료 1500/day)
GROQ_API_KEY=                # https://console.groq.com (무료 14400/day)
```

### 5.6. 메인 수집 스크립트 작성

`backend/pipelines/auto_collectors.py` 파일 (전체 코드는 길어서 핵심 패턴만):

```python
"""auto_collectors.py — 21신호 자동 수집.

각 신호마다 collect_<id>() 함수 + COLLECTORS 리스트에 등록.
"""
import os
import json
import re
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

import requests
import yfinance as yf

# .env 자동 로드
ROOT = Path(__file__).resolve().parents[2]
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

START = "2025-05-01"   # 수집 시작일 (1년 전)
END = date.today().isoformat()  # 오늘 (운영 시 동적, 시범은 고정도 OK)
START_D = date.fromisoformat(START)
END_D = date.fromisoformat(END)
OUT_DIR = ROOT / "backend/data/historical"


def snap_to_monday(d: date) -> date:
    """주간 데이터: 해당 주의 월요일로 정규화."""
    return d - timedelta(days=d.weekday())


def save(signal_id: str, data: list, source: str, mode: str = "real"):
    """historical/<id>.json 저장 (Sixsense 공통 스키마)."""
    out = {
        "signalId": signal_id,
        "source": source,
        "mode": mode,
        "collectedAt": date.today().isoformat(),
        "rangeStart": data[0]["week"] if data else START,
        "rangeEnd": data[-1]["week"] if data else END,
        "data": data,
    }
    p = OUT_DIR / f"{signal_id}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {signal_id:13} {len(data):3}주 · {source[:50]}")


# ── 헬퍼: Yahoo Finance 주간 수집 ──
def yf_weekly(ticker: str) -> list:
    """Yahoo Finance 에서 주간 종가 시계열."""
    h = yf.Ticker(ticker).history(start=START, end=END, interval="1wk")
    if h.empty:
        return []
    return [
        {"week": snap_to_monday(idx.date()).isoformat(),
         "value": round(float(row["Close"]), 4)}
        for idx, row in h.iterrows()
    ]


# ── A-1: 대만 공급망 (TSMC + UMC 가중 평균) ──
def collect_A1_taiwan_supply():
    tsm = yf_weekly("TSM")
    umc = yf_weekly("UMC")
    if not tsm:
        raise RuntimeError("TSM Yahoo 데이터 없음")
    # 주별 가중평균 (TSMC 70% + UMC 30%)
    umc_map = {x["week"]: x["value"] for x in umc}
    data = [
        {"week": x["week"],
         "value": round(x["value"] * 0.7 + umc_map.get(x["week"], x["value"]) * 0.3, 3)}
        for x in tsm
    ]
    return data, "real", "Yahoo Finance TSM+UMC 가중평균 (70/30)"


# ── macro-fed: FRED Effective Fed Funds Rate ──
def collect_macro_fed():
    """FRED DFF — API 키 불필요, CSV 직접 다운로드."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF&cosd={START}&coed={END}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    lines = r.text.strip().split("\n")[1:]
    weekly = defaultdict(list)
    for ln in lines:
        parts = ln.split(",")
        if len(parts) != 2:
            continue
        d_str, val = parts[0].strip(), parts[1].strip()
        if not val or val == ".":
            continue
        try:
            v = float(val)
        except ValueError:
            continue
        d = date.fromisoformat(d_str)
        weekly[snap_to_monday(d).isoformat()].append(v)
    data = [{"week": w, "value": round(sum(v) / len(v), 4)}
            for w, v in sorted(weekly.items())]
    return data, "real", "FRED CSV DFF (Effective Federal Funds Rate)"


# ── COLLECTORS 등록 (21개 모두) ──
COLLECTORS = [
    ("A-1", collect_A1_taiwan_supply, "정형"),
    # ... A-2 ~ A-7 추가
    # ... B-1 ~ B-7 추가
    ("macro-fed", collect_macro_fed, "거시"),
    # ... macro-dxy/pmi/krw/cu/ust10 추가
    # ... target 추가
]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("ids", nargs="*")
    args = ap.parse_args()

    targets = [c for c in COLLECTORS if args.all or c[0] in args.ids]
    if not targets:
        print("사용법: python3 auto_collectors.py --all  또는  <id> <id> ...")
        return

    summary = {"total": len(targets), "success": 0, "fail": 0}
    for sid, fn, group in targets:
        try:
            data, mode, source = fn()
            save(sid, data, source, mode)
            summary["success"] += 1
        except Exception as e:
            print(f"  ❌ {sid:13} 실패: {str(e)[:80]}")
            summary["fail"] += 1
    print(f"\n총 {summary['total']}, 성공 {summary['success']}, 실패 {summary['fail']}")


if __name__ == "__main__":
    main()
```

**참고**: 전체 21개 collector 코드는 길어서 (약 750줄), 위 패턴을 Claude 에게 보여주고 "나머지 19개도 같은 패턴으로 만들어줘" 요청:

```
auto_collectors.py 의 위 패턴(A-1, macro-fed)을 보고 다음 19개 collector를 추가해주세요:

A-2. SEC EDGAR XBRL — Microsoft/Google/Amazon/Meta CapEx 합계
A-3. data.go.kr Itemtrade API — HS 854232 (메모리 칩) 수출 금액
A-4. KOSIS 통계청 API — 반도체 재고지수
A-5. AWS EC2 Spot 가격 — boto3
A-6. Manifold Markets API — Taiwan invasion 확률
A-7. Yahoo Finance HG=F — 구리 선물가
B-1~B-7. 뉴스/감성 (Step 7에서 다룰 collect_news_events.py 로 별도)
macro-dxy. Yahoo DX-Y.NYB
macro-pmi. FRED INDPRO
macro-krw. Yahoo KRW=X
macro-cu. Yahoo HG=F
macro-ust10. FRED DGS10
target. Yahoo MU+Hynix+Samsung 가중평균 (메모리 4사)

각 함수는 def collect_<id>() -> tuple[list, str, str] 시그니처:
- data: [{"week": "2025-05-01", "value": 123.45}, ...]
- mode: "real"
- source: 사람이 읽을 수 있는 설명 (예: "FRED CSV DFF (...)")
```

### 5.7. 무료 API 키 발급 가이드

**(a) FRED — 즉시 사용 (API 키 불필요)**
- URL 직접 다운로드: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series>`
- 시리즈 검색: https://fred.stlouisfed.org/searchresults?st=GDP

**(b) Yahoo Finance — 즉시 사용 (yfinance 라이브러리)**
- `pip install yfinance` 만으로 끝
- 한도: 비공식, 분당 약 100~200 요청 권장

**(c) KOSIS (한국 통계청) — 5분 가입**
1. https://kosis.kr/openapi/ 가입
2. "API 신청" → 사용 목적 입력 → 인증키 발급
3. `.env` 에 `KOSIS_API_KEY=<발급키>` 추가
4. 통계표 URL 생성: KOSIS 사이트에서 원하는 표 → "OpenAPI" 버튼 → URL 복사

**(d) data.go.kr (관세청 Itemtrade) — 10분 가입**
1. https://www.data.go.kr 가입
2. "Itemtrade" 검색 → 활용신청 → 자동 승인 (1~2일)
3. `.env` 에 `KCS_API_KEY=<발급키>` 추가

**(e) Anthropic Claude API — 5분 가입**
1. https://console.anthropic.com 가입
2. Settings → Billing → $5 충전 (테스트용 충분)
3. API Keys → Create Key → `.env` 에 `ANTHROPIC_API_KEY=sk-...` 추가

**(f) Google Gemini API — 무료 1500/day**
1. https://aistudio.google.com 접속 (Google 계정 로그인)
2. "Get API key" → Create → `.env` 에 `GEMINI_API_KEY=AIza...` 추가
3. 무료 한도: gemini-2.5-flash 분당 20 / 일 1500 요청

**(g) Groq API — 무료 14400/day** ⭐ (LLM fallback 권장)
1. https://console.groq.com 가입
2. API Keys → Create → `.env` 에 `GROQ_API_KEY=gsk_...` 추가
3. 무료 한도: 일 14400 요청 (Gemini 보다 많음)

### 5.8. 첫 실행 (한 신호씩 검증)

가장 단순한 macro-fed 부터:
```bash
cd ~/Documents/my-project/backend
source .venv/bin/activate
python3 pipelines/auto_collectors.py macro-fed
```

**이렇게 보이면 OK** ✅:
```
  ✅ macro-fed     53주 · FRED CSV DFF (Effective Federal Funds Rate)

총 1, 성공 1, 실패 0
```

결과 확인:
```bash
cat data/historical/macro-fed.json | python3 -m json.tool | head -20
```

### 5.9. 전체 21신호 한 번에 수집

```bash
python3 pipelines/auto_collectors.py --all
```

약 1~3분 소요 (LLM 사용 신호 포함 시 더 길 수도). 출력:
```
  ✅ A-1           53주 · Yahoo Finance TSM+UMC ...
  ✅ A-2           53주 · SEC EDGAR XBRL ...
  ...
  ✅ macro-ust10   53주 · FRED CSV DGS10 ...
  ✅ target        53주 · Yahoo MU+Hynix+Samsung ...

총 21, 성공 21, 실패 0
```

### 5.10. _summary.json 자동 생성

`auto_collectors.py` 마지막에 summary 도 저장하도록 추가:

```python
# main() 끝에 추가
summary_path = OUT_DIR / "_summary.json"
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
```

### 5.11. git 백업

```bash
cd ~/Documents/my-project
git add backend/
git commit -m "feat(data): 21신호 자동 수집 파이프라인 + 첫 실측 데이터"
```

### Step 5 검증 체크리스트 ✅

- [ ] `backend/.venv/` 가상환경 활성화 가능
- [ ] `backend/pipelines/auto_collectors.py` 작성 완료 (21 collectors)
- [ ] `.env` 에 KOSIS/KCS/Gemini 등 필요 키 등록
- [ ] `backend/data/historical/` 안에 21개 JSON 파일 + _summary.json
- [ ] 각 JSON 파일에 53주 정도 데이터 + `collectedAt` 포함
- [ ] git commit 완료

### 자주 발생하는 에러 (Step 5)

**Q1: `ModuleNotFoundError: No module named 'yfinance'`**
- A: 가상환경 활성화 안 됨. `source .venv/bin/activate` 다시 실행.

**Q2: Yahoo Finance HTTP 429 (Rate Limit)**
- A: 너무 빠른 호출. 각 ticker 사이 `time.sleep(0.5)` 추가.

**Q3: FRED CSV 가 "Unexpected errors" 반환**
- A: URL 의 `cosd`/`coed` 날짜 형식 확인 (YYYY-MM-DD). 또는 series ID 오타.

**Q4: KOSIS API "21" 에러**
- A: 인증키 미발급 또는 통계표 ID 오타. KOSIS 사이트 → 마이페이지 → 인증키 확인.

**Q5: data.go.kr 401**
- A: 활용신청이 아직 승인 안 됨 (1~2일 소요). 또는 endpoint URL 오타 (`/getItemtradeList` 빠짐).

**Q6: LLM 401 (Anthropic credit)**
- A: $5 충전 안 됨. console.anthropic.com → Billing.

**Q7: macOS libomp 미설치 (Step 6 에서 발생 가능)**
- A: `brew install libomp` 한 번 실행.

---

---

## Step 6. AI 예측 모델 (Multi-Model)

> **예상 시간**: 1~2일
> **목표**: 21신호 데이터로 단기(1~7주) + 중장기(8~21주) 가격 예측 모델 학습.
> **결과물**: `backend/data/forecast/forecast_v2_*.json` + `model_comparison.txt`

### 6.1. Multi-Model 전략 (왜 단일 모델이 아닌가)

**단일 모델의 한계**:
- Prophet 만 쓰면: 외부 신호 반영 약함, MAPE 7.54%
- LSTM 만 쓰면: 단기 예측이 보수적, 학습 시간 길음
- XGBoost 만 쓰면: 시계열 패턴 약함

**Multi-Model 의 장점**:
- 단기는 트리 계열(GBR/XGBoost)이 강함 → MAPE 4.54% (Sixsense)
- 중장기는 시계열 딥러닝(LSTM)이 강함 → MAPE 9.19%
- Prophet 은 baseline 비교용 → 모델 선정 근거

### 6.2. 전처리 모듈 작성

`backend/pipelines/preprocessing.py`:

```python
"""preprocessing.py — 21신호 historical JSON → 학습용 DataFrame."""
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HIST = ROOT / "backend/data/historical"

SIGNALS = [
    "A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7",
    "B-1", "B-2", "B-3", "B-4", "B-5", "B-6", "B-7",
    "macro-fed", "macro-dxy", "macro-pmi", "macro-krw", "macro-cu", "macro-ust10",
    "target-dram",  # 목표 변수
]

# B 신호는 sentiment (노이즈 많음) → 3주 이동평균 적용
SENTIMENT_SIGNALS = {"B-1", "B-2", "B-3", "B-4", "B-5", "B-6"}


def load_all_signals() -> pd.DataFrame:
    """21신호를 주별 wide format DataFrame 으로 변환."""
    frames = []
    for sid in SIGNALS:
        p = HIST / f"{sid}.json"
        if not p.exists():
            continue
        rows = json.loads(p.read_text())["data"]
        df = pd.DataFrame(rows)
        df["week"] = pd.to_datetime(df["week"])
        df = df.set_index("week")[["value"]].rename(columns={"value": sid})
        if sid in SENTIMENT_SIGNALS:
            df[sid] = df[sid].rolling(window=3, min_periods=1).mean()
        frames.append(df)
    merged = pd.concat(frames, axis=1).sort_index()
    merged = merged.ffill().bfill()  # 결측 채우기
    return merged


def make_lag_features(df: pd.DataFrame, target_col: str = "target-dram", horizon: int = 7) -> tuple:
    """트리 모델용 lag + rolling features."""
    X_cols = [c for c in df.columns if c != target_col]
    feats = pd.DataFrame(index=df.index)
    for lag in [1, 2, 4, 8]:
        for c in X_cols:
            feats[f"{c}_lag{lag}"] = df[c].shift(lag)
    for window in [4, 12]:
        feats[f"{target_col}_ma{window}"] = df[target_col].rolling(window).mean()
    feats[target_col] = df[target_col]
    feats = feats.dropna()
    y = feats[target_col].shift(-horizon).dropna()
    X = feats.loc[y.index].drop(columns=[target_col])
    return X, y


def make_sequences(df: pd.DataFrame, target_col: str = "target-dram",
                    input_len: int = 12, output_len: int = 21) -> tuple:
    """LSTM 용 seq2seq 시퀀스."""
    arr = df.values.astype(np.float32)
    target_idx = df.columns.get_loc(target_col)
    Xs, Ys = [], []
    for i in range(len(arr) - input_len - output_len + 1):
        Xs.append(arr[i:i+input_len])
        Ys.append(arr[i+input_len:i+input_len+output_len, target_idx])
    return np.array(Xs), np.array(Ys)
```

### 6.3. 학습 + 예측 스크립트 (forecast_v2.py)

`backend/pipelines/forecast_v2.py` — Prophet + GBR + LSTM 3 모델:

```python
"""forecast_v2.py — Multi-Model 학습 + 예측.

단기(1~7주): sklearn GradientBoostingRegressor
중장기(8~21주): PyTorch LSTM
Baseline: Prophet (비교용)
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from preprocessing import load_all_signals, make_lag_features, make_sequences

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "backend/data/forecast"
OUT.mkdir(parents=True, exist_ok=True)


def train_prophet(df: pd.DataFrame) -> dict:
    from prophet import Prophet
    t0 = time.time()
    target = df[["target-dram"]].rename(columns={"target-dram": "y"}).reset_index().rename(columns={"week": "ds"})
    train = target.iloc[:-28]
    m = Prophet(weekly_seasonality=True, daily_seasonality=False)
    m.fit(train)
    future = m.make_future_dataframe(periods=21, freq="W-MON")
    pred = m.predict(future).tail(21)
    elapsed = round(time.time() - t0, 2)
    return {
        "predictions": [{"week": d.strftime("%Y-%m-%d"),
                         "yhat": float(y), "yhat_lower": float(l), "yhat_upper": float(u)}
                         for d, y, l, u in zip(pred["ds"], pred["yhat"], pred["yhat_lower"], pred["yhat_upper"])],
        "train_sec": elapsed,
    }


def train_gbr_short(df: pd.DataFrame) -> dict:
    from sklearn.ensemble import GradientBoostingRegressor
    t0 = time.time()
    X, y = make_lag_features(df, horizon=7)
    split = int(len(X) * 0.7)
    Xtr, Xte, ytr, yte = X.iloc[:split], X.iloc[split:], y.iloc[:split], y.iloc[split:]
    model = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    mape = np.mean(np.abs((yte.values - pred) / yte.values)) * 100
    # 마지막 7주 예측
    final_pred = model.predict(X.iloc[-7:])
    return {
        "predictions": [{"week": str(idx), "yhat": float(v)}
                         for idx, v in zip(X.iloc[-7:].index, final_pred)],
        "mape": round(float(mape), 2),
        "train_sec": round(time.time() - t0, 2),
    }


def train_lstm_mid(df: pd.DataFrame) -> dict:
    import torch
    import torch.nn as nn
    t0 = time.time()
    X, Y = make_sequences(df, input_len=12, output_len=21)
    if len(X) < 20:
        return {"predictions": [], "mape": None, "train_sec": 0,
                "note": "데이터 부족 (X<20)"}
    split = int(len(X) * 0.8)
    Xtr, Xte = torch.tensor(X[:split]), torch.tensor(X[split:])
    Ytr, Yte = torch.tensor(Y[:split]), torch.tensor(Y[split:])

    class LSTM(nn.Module):
        def __init__(self, n_feat, hidden=64, out=21):
            super().__init__()
            self.lstm = nn.LSTM(n_feat, hidden, num_layers=2, batch_first=True, dropout=0.2)
            self.fc = nn.Linear(hidden, out)
        def forward(self, x):
            o, _ = self.lstm(x)
            return self.fc(o[:, -1, :])

    model = LSTM(n_feat=X.shape[2])
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    for epoch in range(50):
        opt.zero_grad()
        pred = model(Xtr)
        loss = loss_fn(pred, Ytr)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        pred_te = model(Xte).numpy()
    mape = float(np.mean(np.abs((Yte.numpy() - pred_te) / Yte.numpy())) * 100)
    # 마지막 시퀀스로 미래 21주 예측
    last_seq = torch.tensor(X[-1:])
    with torch.no_grad():
        future_pred = model(last_seq).numpy()[0]
    last_week = df.index[-1]
    pred_weeks = [last_week + pd.Timedelta(weeks=i+1) for i in range(21)]
    return {
        "predictions": [{"week": w.strftime("%Y-%m-%d"), "yhat": float(v)}
                         for w, v in zip(pred_weeks, future_pred)],
        "mape": round(mape, 2),
        "train_sec": round(time.time() - t0, 2),
    }


def main():
    print("[1/4] 데이터 로드 + 전처리")
    df = load_all_signals()
    print(f"  → {len(df)}주 × {len(df.columns)}열")

    print("[2/4] Prophet (baseline)")
    prophet_res = train_prophet(df)
    print(f"  → {len(prophet_res['predictions'])}주 예측, {prophet_res['train_sec']}s")

    print("[3/4] GBR (단기 1~7w)")
    gbr_res = train_gbr_short(df)
    print(f"  → MAPE {gbr_res['mape']}%, {gbr_res['train_sec']}s")

    print("[4/4] LSTM (중장기 8~21w)")
    lstm_res = train_lstm_mid(df)
    print(f"  → MAPE {lstm_res['mape']}%, {lstm_res['train_sec']}s")

    # 저장
    out_json = OUT / "forecast_v2_2026-02-w1.json"
    out_json.write_text(json.dumps({
        "generated_at": pd.Timestamp.now().isoformat(),
        "models": {
            "prophet": prophet_res,
            "tree_short": gbr_res,
            "lstm_mid": lstm_res,
        }
    }, ensure_ascii=False, indent=2))

    # 비교 표
    cmp_txt = f"""════════════════════════════════════════════
  Multi-Model 비교 ({pd.Timestamp.now().strftime('%Y-%m-%d')})
════════════════════════════════════════════

📈 단기 (1~7주) MAPE
  prophet  (baseline)
  hist_gbr: {gbr_res['mape']}%, gbr: {gbr_res['mape']}%

📈 중장기 (8~21주)
  LSTM held-out MAPE: {lstm_res['mape']}%

⏱  학습 시간
  prophet         {prophet_res['train_sec']}s
  tree_short      {gbr_res['train_sec']}s
  lstm_mid        {lstm_res['train_sec']}s
"""
    (OUT / "model_comparison.txt").write_text(cmp_txt)
    print(f"\n✅ 저장: {out_json}")
    print(cmp_txt)


if __name__ == "__main__":
    main()
```

### 6.4. macOS libomp 사전 설치 (XGBoost/LightGBM 쓸 경우)

```bash
brew install libomp
```

(이 가이드는 sklearn GBR 만 사용하므로 필수는 아니지만 추후 확장 시 필요)

### 6.5. 실행

```bash
cd ~/Documents/my-project/backend
source .venv/bin/activate
python3 pipelines/forecast_v2.py
```

**예상 출력**:
```
[1/4] 데이터 로드 + 전처리
  → 53주 × 21열
[2/4] Prophet (baseline)
  → 21주 예측, 2.68s
[3/4] GBR (단기 1~7w)
  → MAPE 4.54%, 8.76s
[4/4] LSTM (중장기 8~21w)
  → MAPE 9.19%, 13.31s

✅ 저장: backend/data/forecast/forecast_v2_2026-02-w1.json
```

### 6.6. 결과 검증

```bash
cat data/forecast/model_comparison.txt
```

**검증 기준**:
- 단기 GBR MAPE ≤ 7% (Sixsense 사례 4.54%)
- 중장기 LSTM MAPE ≤ 12% (Sixsense 사례 9.19%)

목표 미달 시:
- 신호 추가 (더 많은 정형/비정형 데이터)
- hyperparameter 튜닝 (n_estimators 늘리기, learning_rate 조정)
- LSTM hidden size 증가 (64 → 128)

### 6.7. git 백업

```bash
cd ~/Documents/my-project
git add backend/pipelines/forecast_v2.py backend/pipelines/preprocessing.py backend/data/forecast/
git commit -m "feat(model): Multi-Model 예측 (Prophet + GBR + LSTM)"
```

### Step 6 검증 체크리스트 ✅

- [ ] `preprocessing.py` + `forecast_v2.py` 작성 완료
- [ ] `data/forecast/forecast_v2_*.json` 생성 (3 모델 모두 예측 포함)
- [ ] `data/forecast/model_comparison.txt` 생성 (MAPE 표)
- [ ] 단기 MAPE ≤ 7% 목표 충족 (또는 baseline 보다 개선)
- [ ] 중장기 MAPE ≤ 12% 목표 충족
- [ ] git commit 완료

### 자주 발생하는 에러 (Step 6)

**Q1: `ModuleNotFoundError: No module named 'prophet'`**
- A: `pip install prophet` 한 번 더. macOS 면 약 1~2분 소요.

**Q2: Prophet 학습 시 "cmdstanpy WARNING" 도배**
- A: 무시 가능. 학습은 정상 진행.

**Q3: LSTM MAPE 가 50% 이상으로 너무 큼**
- A: 데이터 양 부족 (X < 20). 더 긴 historical 기간 필요. 또는 epoch 50 → 200 증가.

**Q4: `XGBoost: libomp not loaded`**
- A: sklearn GBR 만 쓰면 OK. XGBoost 쓰려면 `brew install libomp`.

**Q5: torch 가 GPU 못 잡음**
- A: CPU 로도 충분 (Sixsense LSTM 13초). MPS 필요하면 `torch.device('mps')` 명시.

---

## Step 7. LLM 인사이트

> **예상 시간**: 4~6시간
> **목표**: 21신호 + 모델 결과 + 뉴스 5건 → LLM 이 한국어 400자 종합 분석 생성.
> **결과물**: `backend/data/insight/latest.json` + UI 카드에 표시.

### 7.1. 왜 LLM 인사이트가 필요한가

숫자만 보면 의사결정 어려움:
- ❌ "MAPE 4.54%, 다음 7주 후 $5.06" → 무엇을 의미?
- ✅ "AI 수요 폭증으로 장기 상승 압력. 그러나 단기는 재고 부담으로 조정 국면…"

LLM 이 21신호 + 모델 결과 + 뉴스 맥락을 종합해서 **의사결정용 자연어 코멘트** 자동 생성.

### 7.2. 뉴스 수집 스크립트 (collect_news_events.py)

`backend/pipelines/collect_news_events.py` — RSS + LLM 분류:

```python
"""collect_news_events.py — RSS 30~45 쿼리 → LLM 분류 → news 10건 + events 10건.

NEWS 풀: DRAM/반도체 산업 직접 (Yahoo/TechNews/Google News 영·한 14 쿼리)
EVENTS 풀: 글로벌 이벤트 (전쟁/지진/금리/유가/한국 반도체 노조 등 31 쿼리)
"""
import os
import re
import json
from pathlib import Path
from datetime import date, timedelta
import requests
import feedparser

ROOT = Path(__file__).resolve().parents[2]
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# (실제 코드는 약 1000줄. 핵심 패턴만 발췌)

NEWS_QUERIES = [
    ("Taiwan semiconductor", "en"),
    ("DRAM memory price", "en"),
    ("HBM Nvidia", "en"),
    ("Samsung memory", "en"),
    ("SK Hynix HBM", "en"),
    # ... 14개
    ("메모리 반도체", "ko"),
    ("HBM 수요", "ko"),
]

EVENTS_QUERIES = [
    # 국내 반도체 이벤트
    ("Samsung union strike", "en"),
    ("SK Hynix labor strike", "en"),
    ("삼성전자 파업", "ko"),
    # 물리적 충돌
    ("Ukraine war", "en"),
    ("Israel Iran", "en"),
    # 기상이변
    ("major earthquake", "en"),
    # 금융위기
    ("Fed rate decision", "en"),
    # ... 31개
]


def build_rss_urls(queries):
    """Google News RSS 쿼리 URL 생성."""
    return [f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl={lang}-US&gl=US&ceid=US:{lang.split('-')[0]}"
             for q, lang in queries]


def fetch_entries(urls):
    """RSS 파싱 + 최근 30일 entries 추출."""
    cutoff = date.today() - timedelta(days=30)
    seen, entries = set(), []
    for url in urls:
        try:
            f = feedparser.parse(url)
            for e in f.entries:
                pub = e.get("published_parsed") or e.get("updated_parsed")
                if not pub:
                    continue
                d = date(pub.tm_year, pub.tm_mon, pub.tm_mday)
                if d < cutoff:
                    continue
                title = (e.get("title") or "").strip()
                if title in seen:
                    continue
                seen.add(title)
                entries.append({
                    "date": d.isoformat(),
                    "title": title,
                    "summary": re.sub(r"<[^>]+>", " ", e.get("summary") or "")[:300],
                    "source": (e.get("source", {}).get("title") if isinstance(e.get("source"), dict) else "RSS") or "RSS",
                    "link": e.get("link", ""),
                })
        except Exception as exc:
            print(f"  ⚠ RSS 실패: {url[:50]} — {exc}")
    return entries


# ── LLM Fallback Chain ──
def llm_classify(prompt: str) -> str | None:
    """Anthropic → Gemini → Groq → None."""
    # 1. Anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                json={"model": "claude-3-5-haiku-20241022", "max_tokens": 2000,
                      "messages": [{"role": "user", "content": prompt}]}, timeout=60)
            if r.status_code == 200:
                return r.json()["content"][0]["text"]
        except Exception:
            pass

    # 2. Gemini
    key = os.getenv("GEMINI_API_KEY")
    if key:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"maxOutputTokens": 16384, "temperature": 0.0}},
                timeout=60)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    # 3. Groq
    key = os.getenv("GROQ_API_KEY")
    if key:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 4000}, timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return None  # 모두 실패 → 휴리스틱으로 폴백


# ── 한국어 키워드 매핑 (영문 휴리스틱 fallback 용) ──
KEYWORD_MAP = {
    "Samsung": "삼성", "SK Hynix": "SK하이닉스", "Micron": "마이크론",
    "shortage": "부족", "surge": "급등", "decline": "하락",
    "earthquake": "지진", "typhoon": "태풍", "war": "전쟁",
    "Fed rate cut": "Fed 금리 인하", "oil": "유가",
    "Ukraine": "우크라이나", "Iran": "이란",
    # ... 60개
}

def korean_title(en_title: str) -> str:
    """영문 → 한국어 키워드 자동 치환."""
    if re.search(r"[가-힣]", en_title):
        return en_title  # 이미 한국어 포함
    out = en_title
    for k in sorted(KEYWORD_MAP.keys(), key=len, reverse=True):
        out = re.sub(re.escape(k), KEYWORD_MAP[k], out, flags=re.IGNORECASE)
    return out


def main():
    print("[1/3] NEWS 풀 수집 (DRAM 산업 직접)")
    news_entries = fetch_entries(build_rss_urls(NEWS_QUERIES))
    print(f"  → {len(news_entries)}건")

    print("[2/3] EVENTS 풀 수집 (글로벌 이벤트, news 중복 제거)")
    news_titles = {e["title"] for e in news_entries}
    events_entries = [e for e in fetch_entries(build_rss_urls(EVENTS_QUERIES)) if e["title"] not in news_titles]
    print(f"  → {len(events_entries)}건")

    # LLM 분류 프롬프트 (간략 버전)
    prompt = f"""다음 헤드라인을 분석해서 JSON 으로 출력하세요.
출력: {{"news": [...10건], "events": [...10건]}}
각 항목: title_ko(한국어), summary_ko, score(-1~1), tone(pos/neu/neg), type, region, risk

NEWS 후보:
{json.dumps(news_entries[:20], ensure_ascii=False, indent=2)}

EVENTS 후보:
{json.dumps(events_entries[:30], ensure_ascii=False, indent=2)}
"""
    llm_out = llm_classify(prompt)
    # 파싱 + 휴리스틱 fallback (코드 생략, 핵심: 모든 title 한국어 보장)

    # 저장
    (ROOT / "backend/data/news/latest.json").write_text(...)
    (ROOT / "backend/data/events/latest.json").write_text(...)

if __name__ == "__main__":
    main()
```

(전체 코드는 약 1000줄. Claude 에게 "위 패턴으로 collect_news_events.py 전체 작성" 요청)

### 7.3. 인사이트 생성 스크립트 (build_insight.py)

`backend/pipelines/build_insight.py`:

```python
"""build_insight.py — 21신호 + 거시 + 뉴스 → LLM 종합 분석 400자."""
import json, os, re
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def build_prompt() -> str:
    """프롬프트 빌드 — 신호 최신값 + forecast + 뉴스 5건."""
    # 1) historical 마지막 값
    sigs = {}
    hist_dir = ROOT / "backend/data/historical"
    for sid in ["A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7",
                 "B-1", "B-2", "B-3", "B-4", "B-5", "B-6", "B-7",
                 "macro-ust10", "macro-fed", "macro-dxy",
                 "target-dram"]:
        p = hist_dir / f"{sid}.json"
        if p.exists():
            rows = json.loads(p.read_text())["data"]
            if rows:
                sigs[sid] = rows[-1]["value"]

    # 2) forecast 마지막 값
    fc = json.loads((ROOT / "backend/data/forecast/forecast_v2_2026-02-w1.json").read_text())
    gbr_last = fc["models"]["tree_short"]["predictions"][-1]["yhat"]
    lstm_last = fc["models"]["lstm_mid"]["predictions"][-1]["yhat"]

    # 3) 최근 뉴스 5건
    news = json.loads((ROOT / "backend/data/news/latest.json").read_text())["news"][:5]
    news_str = "\n".join(f"- [{n['date']}] {n['title']}" for n in news)

    return f"""당신은 서버 DRAM 가격 의사결정용 시장 분석가입니다.
다음 데이터를 종합해서 한국어 종합 분석을 작성하세요.

【현재 신호】
{json.dumps(sigs, ensure_ascii=False, indent=2)}

【예측 결과】
- GBR 7주 후: {gbr_last:.2f}
- LSTM 21주 후: {lstm_last:.2f}

【최근 뉴스 Top 5】
{news_str}

★ 출력 형식 (JSON 만, 마크다운 금지):
{{
  "headline": "22자 이내 한국어 강조 메시지",
  "summary": "280~360자 한국어 종합 분석. 반드시 마침표(.)로 완결. '...' '등 강력한' 같은 미완성 어구 금지. 중요한 단어 3~5개를 **bold**로 감싸기.",
  "tone": "pos|neu|neg",
  "confidence": 0~100,
  "horizon": "short|mid|long",
  "keySignals": ["A-2", "B-4"]
}}
"""


def call_llm(prompt: str) -> dict | None:
    """Anthropic → Gemini → Groq fallback."""
    # ... collect_news_events.py 의 llm_classify 와 동일 패턴
    # Gemini 호출 시 maxOutputTokens=8192 이상 (250자 한국어 + JSON 구조)
    pass


def heuristic_fallback(prompt_ctx: dict) -> dict:
    """LLM 모두 실패 시 데이터 기반 휴리스틱."""
    return {
        "headline": "휴리스틱 분석",
        "summary": "GBR 모델은 7주 후 **상승** 전망, LSTM 21주 예측은 **하락** 시사. 단기와 중장기 방향이 갈리므로 호라이즌별 의사결정이 필요합니다.",
        "tone": "neu",
        "confidence": 50,
        "horizon": "mid",
        "keySignals": ["A-2", "B-4"],
    }


def main():
    print("[1/3] 컨텍스트 빌드")
    prompt = build_prompt()
    print(f"  → 프롬프트 {len(prompt)}자")

    print("[2/3] LLM 호출")
    result = call_llm(prompt) or heuristic_fallback({})

    # summary 보정 (마침표 완결 강제)
    summary = result.get("summary", "")
    if summary and not summary.rstrip().endswith((".", "다", "요")):
        summary = summary.rstrip(",.;:·") + "."
    if len(summary) > 400:
        cutoff = summary[:400].rfind(".")
        summary = summary[:cutoff+1] if cutoff > 200 else summary[:380] + "."
    result["summary"] = summary

    print(f"[3/3] 저장")
    out = ROOT / "backend/data/insight/latest.json"
    out.write_text(json.dumps({
        "generatedAt": "2026-05-26T12:00:00",
        "model": "Gemini gemini-2.5-flash",  # 실제 사용된 모델명
        **result,
    }, ensure_ascii=False, indent=2))
    print(f"  ✅ {out}")
    print(f"  headline: {result['headline']}")
    print(f"  summary ({len(summary)}자): {summary[:100]}...")


if __name__ == "__main__":
    main()
```

### 7.4. 실행 + 검증

```bash
cd ~/Documents/my-project/backend
source .venv/bin/activate
python3 pipelines/collect_news_events.py
python3 pipelines/build_insight.py
```

**예상 출력**:
```
[1/3] 컨텍스트 빌드
  → 프롬프트 1800자
[2/3] LLM 호출
[3/3] 저장
  ✅ backend/data/insight/latest.json
  headline: AI 수요 견인, 단기 조정 후 안정화
  summary (310자): 서버 DRAM 가격은 현재 **$6.09**로 상승했으나, GBR 및 LSTM...
```

### 7.5. 인사이트 UI 컴포넌트 (frontend)

frontend/src/components/components.jsx 에 `<InsightCard>` 추가:

```jsx
function InsightCard({ insight }) {
  const [open, setOpen] = useState(false);
  if (!insight) return <div>인사이트 준비 중</div>;
  return (
    <>
      <div className="card insight-card tappable" onClick={() => setOpen(true)}>
        <div className="insight-h">
          <span className="insight-glyph">◆</span>
          <span>예측분석 인사이트</span>
          <span className="num">{insight.model}</span>
        </div>
        <div className="insight-main">
          <div className="insight-body insight-body-clamp">
            {renderEmphasis(insight.summary)}
          </div>
          <div className="ai-note insight-claude">
            <div className="label">CLAUDE 종합 판단 · {insight.confidence}%</div>
            <div className="insight-headline">{insight.headline}</div>
            <div className="insight-keysig">
              {insight.keySignals?.map(s => (
                <span key={s} className="num insight-sig-chip">{s}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
      {open && <Modal title="전체 분석" onClose={() => setOpen(false)}>
        <div className="insight-modal-summary">{renderEmphasis(insight.summary)}</div>
      </Modal>}
    </>
  );
}

function renderEmphasis(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
    const m = part.match(/^\*\*([^*]+)\*\*$/);
    return m ? <strong key={i} className="insight-emphasis">{m[1]}</strong> : <span key={i}>{part}</span>;
  });
}
```

### Step 7 검증 체크리스트 ✅

- [ ] `collect_news_events.py` + `build_insight.py` 작성 완료
- [ ] `backend/data/news/latest.json` (10건) + `backend/data/events/latest.json` (10건)
- [ ] 모든 title + summary 한국어 (한글 포함)
- [ ] `backend/data/insight/latest.json` 생성 (headline + 250~400자 summary)
- [ ] summary 가 마침표로 완결 (`...` 같은 미완성 X)
- [ ] bold 강조 단어 3개 이상 (`**word**`)
- [ ] `<InsightCard>` 컴포넌트 frontend 에 추가

### 자주 발생하는 에러 (Step 7)

**Q1: Gemini 429 (Rate Limit)**
- A: 분당 20 req 한도 초과. 40초 대기 후 재시도. 또는 GROQ_API_KEY 추가 (무료 14400/day).

**Q2: Anthropic 400 "credit balance too low"**
- A: $5 충전 (console.anthropic.com → Billing). 또는 Gemini fallback 자동 작동.

**Q3: summary 가 "..." 로 잘림**
- A: maxOutputTokens 2048 → 8192 로 증가. 프롬프트에 "반드시 마침표 완결" 명시.

**Q4: news 가 영문 그대로**
- A: `korean_title()` 함수 구현 + `KEYWORD_MAP` 60개 매핑. Step 7.2 의 코드 참조.

**Q5: 인사이트가 너무 일반적이고 데이터 안 반영**
- A: 프롬프트에 "신호 수치를 인용해서 설명" 명시. 또는 신호값을 더 자세히 컨텍스트에 포함.

---

## Step 8. 백엔드 API + 수동 갱신

> **예상 시간**: 1일
> **목표**: FastAPI 로 15개 GET endpoint + 풋바 "🔄 수동 갱신 실행" 버튼.
> **결과물**: `http://localhost:8000` + frontend 풋바에 갱신 버튼.

### 8.1. FastAPI 설치

```bash
cd ~/Documents/my-project/backend
source .venv/bin/activate
pip install fastapi uvicorn[standard]
```

### 8.2. main.py 작성

`backend/app/main.py`:

```python
"""FastAPI backend — 15개 GET endpoint + 수동 갱신."""
import json
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend/data"
VENV_PY = ROOT / "backend/.venv/bin/python3"

app = FastAPI(title="My Project API", version="0.1.0")

# CORS — 로컬 개발 + Vercel 배포 도메인 모두 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        # 운영 배포 후 실제 도메인 추가:
        # "https://my-project.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "My Project API", "endpoints": "/api/health, /api/snapshot, ..."}


@app.get("/api/health")
def health():
    return {"status": "ok", "ts": time.time()}


@app.get("/api/snapshot")
def snapshot():
    """현재 가격 + 단기/중장기 예측 요약."""
    target = json.loads((DATA / "historical/target-dram.json").read_text())["data"]
    forecast = json.loads((DATA / "forecast/forecast_v2_2026-02-w1.json").read_text())
    return {
        "current": target[-1]["value"],
        "pred7": forecast["models"]["tree_short"]["predictions"][-1]["yhat"],
        "pred21": forecast["models"]["lstm_mid"]["predictions"][-1]["yhat"],
    }


@app.get("/api/signals")
def signals():
    """21신호 메타 + 최신값."""
    out = []
    for sid in ["A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7",
                 "B-1", "B-2", "B-3", "B-4", "B-5", "B-6", "B-7"]:
        p = DATA / f"historical/{sid}.json"
        if p.exists():
            j = json.loads(p.read_text())
            out.append({"id": sid, "value": j["data"][-1]["value"], "source": j["source"]})
    return out


@app.get("/api/macro")
def macro():
    """6 거시지표."""
    out = []
    for sid in ["macro-ust10", "macro-fed", "macro-dxy", "macro-pmi", "macro-krw", "macro-cu"]:
        p = DATA / f"historical/{sid}.json"
        if p.exists():
            j = json.loads(p.read_text())
            out.append({"id": sid.replace("macro-", ""), "value": j["data"][-1]["value"]})
    return out


@app.get("/api/news")
def news():
    return json.loads((DATA / "news/latest.json").read_text())


@app.get("/api/events")
def events():
    return json.loads((DATA / "events/latest.json").read_text())


@app.get("/api/insight")
def insight():
    return json.loads((DATA / "insight/latest.json").read_text())


# ── 수동 갱신 (5단계 파이프라인 백그라운드 실행) ──
REFRESH_JOBS: dict[str, dict[str, Any]] = {}
REFRESH_STAGES = [
    ("auto_collectors", "데이터 수집 (21신호)", ["--all"]),
    ("collect_news_events", "뉴스/이벤트 수집", []),
    ("forecast_v2", "예측 모델 재학습", []),
    ("build_insight", "AI 인사이트 생성", []),
    ("build_frontend_data", "프론트엔드 데이터 빌드", []),
]


def _run_pipeline(job_id: str):
    job = REFRESH_JOBS[job_id]
    job["status"] = "running"
    for idx, (script, label, args) in enumerate(REFRESH_STAGES, start=1):
        job["currentStep"] = idx
        job["stage"] = label
        result = subprocess.run(
            [str(VENV_PY), str(ROOT / f"backend/pipelines/{script}.py"), *args],
            cwd=str(ROOT / "backend"), capture_output=True, text=True, timeout=600,
        )
        job["logs"].append({"step": idx, "stage": label,
                             "ok": result.returncode == 0,
                             "lastLine": (result.stdout or result.stderr)[-200:]})
        if result.returncode != 0:
            job["status"] = "failed"
            job["error"] = result.stderr[-500:]
            return
    job["status"] = "done"
    job["totalDurSec"] = round(time.time() - job["createdAt"], 1)


@app.post("/api/refresh", status_code=202)
def post_refresh():
    """5단계 파이프라인 백그라운드 실행."""
    for jid, j in REFRESH_JOBS.items():
        if j["status"] in ("queued", "running"):
            return {"queueId": jid, "reused": True}
    job_id = f"rf_{uuid.uuid4().hex[:12]}"
    REFRESH_JOBS[job_id] = {
        "status": "queued", "stage": "대기 중", "currentStep": 0,
        "totalSteps": len(REFRESH_STAGES), "logs": [],
        "createdAt": time.time(),
    }
    threading.Thread(target=_run_pipeline, args=(job_id,), daemon=True).start()
    return {"queueId": job_id, "status": "queued"}


@app.get("/api/refresh/jobs/{job_id}")
def get_refresh_job(job_id: str):
    if job_id not in REFRESH_JOBS:
        raise HTTPException(404, "Job not found")
    return REFRESH_JOBS[job_id]


@app.get("/api/refresh/stages")
def get_refresh_stages():
    return {"stages": [{"step": i+1, "id": s[0], "label": s[1]} for i, s in enumerate(REFRESH_STAGES)],
             "totalSteps": len(REFRESH_STAGES)}
```

### 8.3. 백엔드 실행

```bash
cd ~/Documents/my-project/backend
source .venv/bin/activate
.venv/bin/uvicorn app.main:app --port 8000 --reload
```

**이렇게 보이면 OK** ✅:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 8.4. 동작 확인

새 터미널 열어서:
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/snapshot
curl http://localhost:8000/api/refresh/stages
```

또는 브라우저로:
- http://localhost:8000/docs ← Swagger UI 자동 생성

### 8.5. 프론트엔드에 RefreshPanel 추가

frontend/src/screens/dashboard.jsx 에 풋바 영역:

```jsx
function RefreshPanel() {
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);
  const API = window.location.hostname === "localhost" ? "http://localhost:8000" : "";

  const trigger = async () => {
    try {
      const r = await fetch(`${API}/api/refresh`, { method: "POST" });
      const j = await r.json();
      setJob({ ...j, logs: [] });
      pollRef.current = setInterval(async () => {
        const rr = await fetch(`${API}/api/refresh/jobs/${j.queueId}`);
        const jj = await rr.json();
        setJob(jj);
        if (jj.status === "done") {
          clearInterval(pollRef.current);
          setTimeout(() => window.location.reload(), 1200);
        } else if (jj.status === "failed") {
          clearInterval(pollRef.current);
        }
      }, 2000);
    } catch (e) {
      setError(`백엔드 연결 실패 — ${e.message}`);
    }
  };

  const isRunning = job && (job.status === "queued" || job.status === "running");
  const progress = job ? Math.round((job.currentStep / job.totalSteps) * 100) : 0;

  return (
    <div className="refresh-panel">
      <button className="refresh-btn" onClick={trigger} disabled={isRunning}>
        {isRunning ? "갱신 중..." : "🔄 수동 갱신 실행"}
      </button>
      {job && (
        <>
          <div className="refresh-progress-bar">
            <div className="refresh-progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <div>{job.currentStep}/{job.totalSteps} · {job.stage}</div>
        </>
      )}
      {error && <div className="refresh-error">{error}</div>}
    </div>
  );
}
```

### 8.6. CSS 추가 (styles.css)

```css
.refresh-panel { margin-top: 12px; padding: 14px; border: 1px dashed var(--border); }
.refresh-btn { padding: 8px 16px; background: var(--accent); color: var(--bg); border: none; cursor: pointer; }
.refresh-progress-bar { height: 6px; background: var(--border); border-radius: 3px; margin-top: 8px; }
.refresh-progress-fill { height: 100%; background: var(--sig-info); transition: width 0.4s; }
.refresh-error { color: var(--sig-neg); margin-top: 8px; font-size: 12px; }
```

### Step 8 검증 체크리스트 ✅

- [ ] FastAPI + uvicorn 설치
- [ ] `backend/app/main.py` 작성 (15+ endpoints)
- [ ] `uvicorn app.main:app --port 8000 --reload` 정상 실행
- [ ] http://localhost:8000/docs Swagger UI 표시
- [ ] `curl http://localhost:8000/api/snapshot` 정상 응답
- [ ] frontend `<RefreshPanel>` 추가 + 풋바에 표시
- [ ] 갱신 버튼 클릭 → 5단계 백그라운드 실행 → 자동 새로고침
- [ ] git commit 완료

### 자주 발생하는 에러 (Step 8)

**Q1: `uvicorn: command not found`**
- A: 가상환경 활성화 안 됨. `source .venv/bin/activate` 후 재시도.

**Q2: CORS 에러 (브라우저 콘솔 "blocked by CORS")**
- A: `main.py` 의 `allow_origins` 에 frontend URL 추가. 로컬은 `http://localhost:5173`, 배포는 `https://<project>.vercel.app`.

**Q3: 수동 갱신 클릭 후 진행 안 됨 (currentStep=0 유지)**
- A: ⚠ 알려진 이슈 — `uvicorn --reload` 모드 + `threading` 충돌. CLI 로 5단계 직접 실행:
  ```bash
  python3 pipelines/auto_collectors.py --all && python3 pipelines/collect_news_events.py && python3 pipelines/forecast_v2.py && python3 pipelines/build_insight.py && python3 pipelines/build_frontend_data.py
  ```
  운영 시 `asyncio.create_task` 또는 Celery 로 대체.

**Q4: `Module not found: app.main`**
- A: cwd 가 `backend/` 인지 확인. 또는 `uvicorn backend.app.main:app` 처럼 풀패스.

---

---

## Step 9. Vercel + GitHub 시범 배포

> **예상 시간**: 30분
> **목표**: 5명 협업 검토용 HTTPS URL 발급. GitHub push → Vercel 자동 재배포 흐름 구축.
> **결과물**: `https://<project>.vercel.app` 같은 공개 URL.

### 9.1. 배포 방식 결정

| 방식 | 작동 | 미작동 | 추천 |
|---|---|---|---|
| **A. Frontend only** (정적 호스팅) | 14화면 + mock data 표시 | 수동 갱신 버튼 (backend 호출 실패) | ⭐ 시범 운영 |
| B. Frontend + Backend serverless | 모두 작동 | Prophet/torch 200MB+ Vercel 한도 초과 | 비추 |
| C. Frontend Vercel + Backend Railway | 모두 작동 | 별도 호스팅 비용/설정 | 본격 운영 |

**이 가이드는 옵션 A (frontend only)** 로 진행. 본격 운영 시 옵션 C 로 전환.

### 9.2. GitHub repo 생성

**옵션 A: GitHub.com 웹에서**:
1. https://github.com/new 접속
2. Repository name: `my-project` (소문자 권장)
3. Public 또는 Private 선택
4. **README, .gitignore, license 모두 체크 해제** (이미 로컬에 있음)
5. "Create repository" 클릭

생성된 URL 복사: `https://github.com/<your-username>/my-project`

### 9.3. GitHub CLI 인증

```bash
gh auth login --web
```

8자리 코드가 출력됨 (예: `A754-A616`):
```
! First copy your one-time code: A754-A616
Open this URL in your browser: https://github.com/login/device
```

1. 코드 복사 → https://github.com/login/device 열기
2. 코드 입력 → "Authorize" 클릭
3. 터미널에 "✓ Authentication complete" 표시

### 9.4. git remote 연결 + push

```bash
cd ~/Documents/my-project
git remote add origin https://github.com/<your-username>/my-project.git
git push -u origin main
```

**이렇게 보이면 OK** ✅:
```
Enumerating objects: ...
To https://github.com/<your-username>/my-project.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

브라우저에서 GitHub repo 확인 — 모든 파일이 보여야 함.

### 9.5. vercel.json 작성 (monorepo 설정)

`~/Documents/my-project/vercel.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "version": 2,
  "framework": "vite",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "devCommand": "cd frontend && npm run dev",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### 9.6. .vercelignore (배포 크기 최소화)

`~/Documents/my-project/.vercelignore`:

```
# Backend (Python, Vercel 배포 대상 아님)
backend/

# Hand-off 원본 (이미 frontend/src/ 에 포팅됨)
design_handoff/

# 문서
docs/

# 기타
.bkit/
.claude/
prd.docx
*.bak
```

### 9.7. Vercel CLI 인증 (sudo 없이)

```bash
cd ~/Documents/my-project
npx vercel login
```

device code URL 출력 (예: `https://vercel.com/oauth/device?user_code=SBHJ-DRRR`):
1. URL 복사 → 브라우저에서 열기
2. "Continue with GitHub" (이미 GitHub 인증됨이므로 즉시 완료)
3. 터미널에 "✓ Email confirmed" 표시

### 9.8. 첫 배포

```bash
npx vercel --prod --yes --name my-project
```

(name 은 반드시 소문자 + 하이픈만. 폴더명에 대문자 있으면 자동 generated name이 invalid)

**약 1~2분 소요. 출력**:
```
🔍 Inspect: https://vercel.com/<scope>/my-project/<id>
✅ Production: https://my-project-xxxxx.vercel.app

▲ Aliased: https://my-project-eta.vercel.app
```

### 9.9. 배포 검증

```bash
curl -I https://my-project-eta.vercel.app
```

**이렇게 보이면 OK** ✅: `HTTP/2 200`

브라우저에서 URL 열어 14화면 모두 확인:
- [ ] 다크 모드 + 라이트 모드 토글 작동
- [ ] §01 가격 스냅샷 표시
- [ ] §02 차트 표시
- [ ] §05 뉴스 한국어 표시
- [ ] §07 이벤트 한국어 + 5 카테고리
- [ ] §06 거시경제 6 카드
- [ ] 모달 클릭 시 팝업

### 9.10. GitHub ↔ Vercel webhook 자동 등록 확인

이제 `git push origin main` 만 하면 Vercel 이 자동으로 재빌드 + 배포.

테스트:
```bash
cd ~/Documents/my-project
# 작은 변경 (예: README 한 줄 수정)
echo "" >> README.md
git add README.md
git commit -m "test: Vercel auto-rebuild"
git push
```

Vercel Dashboard (https://vercel.com/dashboard) 접속 → my-project → Deployments 탭. 새 배포가 자동 시작됨 (약 1~2분 후 완료).

### Step 9 검증 체크리스트 ✅

- [ ] GitHub repo 생성 + git push 성공
- [ ] vercel.json + .vercelignore 작성
- [ ] `npx vercel login` 인증 완료
- [ ] `npx vercel --prod --yes --name <project>` 첫 배포 성공
- [ ] HTTPS URL HTTP 200 + 14화면 모두 정상
- [ ] `git push` 시 Vercel 자동 재배포 확인

### 자주 발생하는 에러 (Step 9)

**Q1: `Project names must be lowercase`**
- A: `--name` 옵션을 소문자로. 예: `--name my-project` (My-Project ❌)

**Q2: `Permission denied (publickey)` git push**
- A: GitHub 인증 미완료. `gh auth login --web` 다시 실행.

**Q3: Vercel 배포 후 흰 화면**
- A: 브라우저 콘솔(F12) 확인. 보통 `404 Not Found /assets/...` → vercel.json 의 outputDirectory 오타.

**Q4: 한국어 폰트 깨짐**
- A: index.html `<html lang="ko">` 확인 + Pretendard CDN link 추가.

**Q5: Vercel build 실패 "npm install failed"**
- A: Vercel Dashboard → Settings → Build & Development Settings → Node.js Version 을 18.x 또는 20.x 로 변경.

**Q6: GitHub repo URL 잊었을 때**
- A: `git remote -v` 로 확인. 또는 `gh repo view --web` 으로 브라우저에서 열기.

---

## Step 10. 협업 운영

> **목표**: 5명 협업 워크플로우 정착 + 데이터 매주 갱신 + 본격 운영 준비.

### 10.1. 조원 5명에게 공유

카톡/Slack 에 다음 메시지 공유:

```
🎯 우리 프로젝트 시범 데모: https://my-project-eta.vercel.app

✅ 작동:
- 14화면 hand-off UI / 21신호 차트 / Multi-Model 예측 / AI 인사이트 / 다크 모드 / 한국어

❌ 미작동 (의도된 동작):
- 수동 갱신 버튼 (backend 없음, 데이터는 매주 갱신 push 로 반영)

💬 피드백:
- GitHub Issues: https://github.com/<your>/my-project/issues
- 또는 카톡으로 화면 캡처 + 의견
```

OG meta 덕분에 카톡/Slack 에 자동으로 미리보기 카드 표시됨.

### 10.2. 주간 데이터 갱신 워크플로우

매주 화요일 (또는 원하는 주기) 다음 5단계 실행:

```bash
cd ~/Documents/my-project/backend
source .venv/bin/activate
python3 pipelines/auto_collectors.py --all
python3 pipelines/collect_news_events.py
python3 pipelines/forecast_v2.py
python3 pipelines/build_insight.py
python3 pipelines/build_frontend_data.py

cd ..
git add frontend/src/mocks/data.js backend/data/
git commit -m "data: weekly refresh $(date +%Y-%m-%d)"
git push
```

**자동 재배포**: GitHub push → Vercel webhook → 1~2분 후 새 URL 반영.

### 10.3. 자동 cron 등록 (선택, 본격 운영용)

매주 화요일 06:00 KST 자동 실행:

**옵션 A: macOS launchd (로컬)**:
`~/Library/LaunchAgents/com.myproject.refresh.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.myproject.refresh</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ~/Documents/my-project/backend && source .venv/bin/activate && python3 pipelines/auto_collectors.py --all && python3 pipelines/collect_news_events.py && python3 pipelines/forecast_v2.py && python3 pipelines/build_insight.py && python3 pipelines/build_frontend_data.py && cd .. && git add . && git commit -m "data: weekly refresh" && git push</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key><integer>2</integer>
        <key>Hour</key><integer>6</integer>
    </dict>
</dict>
</plist>
```

등록:
```bash
launchctl load ~/Library/LaunchAgents/com.myproject.refresh.plist
```

**옵션 B: GitHub Actions (권장, 클라우드)**:
`~/Documents/my-project/.github/workflows/weekly-refresh.yml`:
```yaml
name: Weekly Data Refresh
on:
  schedule:
    - cron: '0 21 * * 1'   # 매주 화요일 06:00 KST (UTC 21:00 Mon)
  workflow_dispatch:        # 수동 실행도 가능
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && python pipelines/auto_collectors.py --all
      - run: cd backend && python pipelines/collect_news_events.py
        env: { GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }} }
      - run: cd backend && python pipelines/forecast_v2.py
      - run: cd backend && python pipelines/build_insight.py
        env: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }} }
      - run: cd backend && python pipelines/build_frontend_data.py
      - run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "data: weekly refresh ($(date +%Y-%m-%d))" || echo "no changes"
          git push
```

GitHub repo → Settings → Secrets → Actions → API 키 등록.

### 10.4. 본격 운영 P0 (시범 → 운영 격차)

5명 협업이 끝나고 외부 사용자에게 공개 시 반드시 처리:

| # | 항목 | 액션 |
|---|---|---|
| P0-1 | **수동 갱신 endpoint thread 멈춤** | uvicorn `--reload` + threading 충돌. 운영 시 `asyncio.create_task` 또는 Celery 도입. |
| P0-2 | **cron 자동 갱신** | GitHub Actions 등록 (10.3 옵션 B) |
| P0-3 | **API 인증** | `POST /api/refresh` 누구나 호출 가능 → Supabase Auth + API Token. |
| P0-4 | **CORS 운영 도메인** | `main.py` `allow_origins` 에 실제 운영 도메인 추가. |
| P0-5 | **Backend 호스팅** | Railway / Fly.io / AWS — `cd backend && railway up` (Railway 무료 tier). |

### 10.5. P1 (배포 후 30일 내)

| # | 항목 | 액션 |
|---|---|---|
| P1-1 | END 하드코딩 → `date.today()` | 데이터 신선도 자동 보장 |
| P1-2 | LLM 비용 안정화 | Anthropic 충전 + Groq 키 추가 (3중 안전망) |
| P1-3 | 모니터링 (Sentry / Datadog) | 에러 추적 + 메트릭 |
| P1-4 | CI/CD (GitHub Actions) | PR typecheck + lint + 단위 테스트 |

### Step 10 검증 체크리스트 ✅

- [ ] Vercel URL 5명에게 공유 완료
- [ ] 주간 데이터 갱신 워크플로우 1회 실행 + git push 자동 재배포 확인
- [ ] (선택) GitHub Actions cron 등록
- [ ] P0/P1 액션 아이템 인식 (본격 운영 전 처리)

---

## 부록 A. 반드시 피해야 할 실수 (6가지 안티패턴)

Sixsense 제작 중 실제로 겪고 되돌린 실수 모음. 같은 함정 회피용.

### A-1. ❌ Plotly/Recharts/D3 등 외부 라이브러리로 별도 HTML 만들기
**증상**: hand-off 가 있는데 "더 멋진 차트 보여줘" 요청에 별도 dashboard.html 생성
**문제**: SSOT 깨짐. hand-off UI 와 실제 화면 다름. 결국 폐기
**해결**: hand-off 의 `<LineChart>` 컴포넌트만 사용. 4모델 차트도 SVG 기반으로 확장

### A-2. ❌ hand-off UI 무시 + TypeScript 컴포넌트 쇼케이스 새로 작성
**증상**: 받은 hand-off 가 마음에 안 들어서 "TypeScript 로 새로 만들어줘" 요청
**문제**: 디자인이 완전히 달라짐. 며칠 작업이 무용지물
**해결**: hand-off 가 SSOT. 변경 필요 시 hand-off 디자인 토큰만 조합해서 확장

### A-3. ❌ Anthropic 크레딧 부족으로 LLM 막힘
**증상**: build_insight.py 실행 시 HTTP 400 "credit balance too low"
**문제**: 휴리스틱 폴백으로 떨어짐. 인사이트 품질 저하
**해결**: 4-tier fallback 미리 설정 (Anthropic + Gemini + Groq + 휴리스틱). 최소 Gemini + Groq 무료 키 2개 등록

### A-4. ❌ news/events 영문 그대로 표시
**증상**: 휴리스틱 폴백 시 영문 RSS 헤드라인 그대로 사용자에게 노출
**문제**: 한국어 대시보드에 영문이 섞여 어색
**해결**: `korean_title()` 함수 + KEYWORD_MAP 60개 매핑 (Samsung → 삼성 등). 모든 fallback 경로에 적용

### A-5. ❌ END = "2026-04-30" 같은 날짜 하드코딩
**증상**: 매주 갱신해도 새 데이터가 안 들어옴 (END 이후 데이터 필터링됨)
**문제**: 사용자가 "왜 최신 데이터가 아니야?" 의문
**해결**: `END = date.today().isoformat()` 동적화. cron 실행 시점이 곧 END

### A-6. ❌ uvicorn --reload + threading 조합
**증상**: POST /api/refresh 호출 시 thread 가 첫 iteration 진입 전 멈춤
**문제**: 시범 단계는 OK 지만 운영 시 critical
**해결**: 운영 시 `asyncio.create_task` 또는 Celery/RQ 도입. 시범 단계는 CLI 직접 실행

---

## 부록 B. 다른 도메인 응용

Sixsense 의 PRD → Hand-off → 데이터 → Multi-Model → LLM 프레임워크는 다음 도메인에 즉시 응용 가능:

### B-1. 부동산 가격 예측 (서울 아파트)
| Group | 21신호 후보 |
|---|---|
| 정형 7 | 한국은행 기준금리 / 입주물량 / 거래량 (KB부동산) / 인허가 (국토부) / 실거래가 (직방) / 미분양 수 / 청약 경쟁률 |
| 비정형 7 | 부동산 뉴스 / 청약 커뮤니티 / 카카오맵 리뷰 / 정책 발표 / 분양 광고 / 유튜브 채널 / 트위터 |
| 거시 6 | Fed 금리 / DXY / 한국 GDP / 가계대출 / 전세가율 / KOSPI |
| 타겟 1 | 서울 아파트 평균가 (KB부동산 시세) |

### B-2. 환율 예측 (USD/KRW)
| Group | 21신호 후보 |
|---|---|
| 정형 7 | 무역수지 / 외환보유고 / 외국인 채권 순매수 / 한국 CDS / 단기 외채 / VIX / 유가 |
| 비정형 7 | 한국은행 코멘트 / Fed 의장 연설 / 외환시장 코멘터리 / IMF 보고서 / Bloomberg 헤드라인 |
| 거시 6 | Fed 금리 / 한국 기준금리 / 미국 10년물 / DXY / WTI / 금 |
| 타겟 1 | USD/KRW |

### B-3. 매출 예측 (이커머스)
| Group | 21신호 후보 |
|---|---|
| 정형 7 | 일간 PV / UV / 신규가입 / 결제 전환율 / 평균 객단가 / 리뷰 수 / 환불률 |
| 비정형 7 | SNS 멘션 / 인스타 해시태그 / 유튜브 리뷰 / 네이버 검색량 / 카페 후기 / 카카오톡 광고 / 푸시 알림 반응 |
| 거시 6 | 소비자물가 / 가계대출 / 환율 / 유가 / 기상특보 / 공휴일 |
| 타겟 1 | 일간 매출액 |

### B-4. 수요 예측 (제조업 SCM)
| Group | 21신호 후보 |
|---|---|
| 정형 7 | 주문 receive / 재고 / 출하 / 반품률 / 리드타임 / 공급사 가동률 / 부품 단가 |
| 비정형 7 | 고객사 IR 발표 / 시장 리포트 / 컨퍼런스 코멘트 / 산업 뉴스 / 트레이드 매체 / 컨설팅 노트 / 정부 공시 |
| 거시 6 | PMI / GDP / 원자재 / 환율 / 유가 / 운임 지수 (BDI) |
| 타겟 1 | 분기 출하량 |

### B-5. 주가 예측 (단일 종목)
| Group | 21신호 후보 |
|---|---|
| 정형 7 | 분기 실적 / 영업이익률 / 매출 성장률 / ROE / 부채비율 / 자사주 매입 / 배당 |
| 비정형 7 | 애널리스트 컨센서스 / 실적발표 콜 / ESG 점수 / 뉴스 감성 / 트위터 멘션 / Reddit (WSB) / 직원 리뷰 |
| 거시 6 | Fed 금리 / 10년물 / VIX / 섹터 지수 / S&P 500 / DXY |
| 타겟 1 | 주가 |

**모든 도메인 공통**:
- 단기 모델: 트리 (sklearn GBR / XGBoost / LightGBM)
- 중장기 모델: 시계열 딥러닝 (PyTorch LSTM / TFT / Chronos)
- Baseline: Prophet
- LLM 인사이트: 21신호 + 모델 결과 + 뉴스 → 한국어 400자 종합 분석

---

## 부록 C. 자주 묻는 질문 (FAQ)

### 일반

**Q1: 이 가이드 다 따라하는 데 정말 7~10일 걸리나?**
A: 비전문가 + 처음 시도 기준. 도구 학습 시간 포함. 두 번째부터는 3~5일.

**Q2: Mac 이 없어도 가능?**
A: Windows 는 WSL2 (Ubuntu) 권장. Linux 는 거의 동일. 일부 brew 명령은 apt 로 대체.

**Q3: 비용은 얼마 드나?**
A: **0원** (시범 운영). 무료 tier 만 사용:
- Vercel free (100GB/월)
- GitHub free (public repo)
- Gemini free (1500/day)
- Yahoo/FRED/KOSIS 무료 API
선택 비용: Anthropic $5 충전 (LLM 정확도 향상).

**Q4: AI 가 다 만들어주면 결국 내 능력은?**
A: 도구 활용 + 의사결정 = 능력. 같은 패턴으로 다른 도메인 (부록 B) 즉시 응용 가능.

### Step 별

**Q5: PRD 작성 시 Claude 가 자꾸 추상적인 말만 한다**
A: "구체적 수치 명시, 실제 화면 mock 예시 포함" 추가 요청. 또는 비슷한 프로젝트 PRD 첨부 후 "비슷하게" 요청.

**Q6: hand-off 받았는데 너무 못생겼다**
A: 디자인 사양을 더 구체적으로. "Notion / Linear / Vercel Dashboard 같은 스타일" 같은 참고처 명시.

**Q7: 데이터 수집 21개 다 필요한가?**
A: 도메인에 따라 10~30개. 단 다양성이 중요. 정형/비정형/거시/타겟 4 종류 균형 유지.

**Q8: AI 모델이 너무 부정확하다 (MAPE 20%+)**
A: 1) 신호 더 추가 2) 데이터 기간 늘리기 (1년 → 3년) 3) target 정의 재검토 (너무 노이즈 많은가?).

**Q9: LLM 응답이 항상 비슷한 말만 한다**
A: 프롬프트에 "관점을 다양화: 강세론 + 약세론 + 중립론 균형있게" 명시.

**Q10: 백엔드 endpoint thread 멈춤 어떻게 해결?**
A: 시범 단계는 CLI 직접 실행. 운영 시 `asyncio.create_task` 또는 Celery (참고: [부록 A-6](#a-6-uvicorn---reload--threading-조합)).

### 배포

**Q11: Vercel 외 다른 호스팅?**
A: Cloudflare Pages (무료, 더 빠름), Netlify (Vercel 비슷), GitHub Pages (정적만).

**Q12: 도메인 (예: my-project.com) 연결 가능?**
A: Vercel Dashboard → Settings → Domains → "Add" → 도메인 입력 → DNS A record 설정.

**Q13: 5명 협업 시 동시 push 충돌?**
A: 각자 branch 만들고 PR 로 main 에 merge. GitHub flow 표준 패턴.

**Q14: 시범 → 운영 전환 시간?**
A: P0 5건 모두 처리 (인증 + cron + endpoint + CORS + backend 호스팅) 약 1주.

### 비용/한도

**Q15: Gemini 일일 한도 1500 모자라다**
A: Groq 무료 14400/day 추가. 또는 Gemini 유료 (~$0.075/M tokens, 매우 저렴).

**Q16: Anthropic Claude 비용**
A: claude-haiku-4-5: input $1/M tokens, output $5/M tokens. 매주 1회 인사이트 생성 ≈ $0.50/월.

**Q17: Vercel 한도 100GB 초과 시?**
A: Pro $20/월. 또는 Cloudflare Pages (무한 무료).

### 협업

**Q18: 5명 모두 git 모름**
A: GitHub Desktop (GUI) 추천. clone / pull / push 버튼으로 가능.

**Q19: 피드백 모으기 어렵다**
A: GitHub Issues 템플릿 만들기:
```markdown
## 화면
- [ ] S-001 / S-002 / ...

## 피드백
무엇이 문제? 어떻게 개선?

## 캡처
(첨부)
```

**Q20: 코드 리뷰?**
A: PR (Pull Request) → 코멘트 → main 머지. GitHub Copilot 또는 Claude 가 자동 리뷰도 가능.

---

## 부록 D. 전체 디렉토리 구조

가이드 완료 시 다음 구조가 됨:

```
my-project/                                  # ~/Documents/my-project/
├── .env                                     # API 키 (gitignored)
├── .env.example                             # 키 템플릿 (commit OK)
├── .gitignore
├── .vercelignore
├── vercel.json                              # Vercel 배포 설정
├── prd.md                                   # PRD 18 섹션
├── README.md
├── .git/
├── .vercel/                                 # Vercel CLI 자동 생성 (gitignored)
├── .github/
│   └── workflows/
│       └── weekly-refresh.yml               # GitHub Actions cron
│
├── design_handoff/                          # Step 3 Claude Design 산출물
│   └── src/
│       ├── app.jsx
│       ├── dashboard.jsx
│       ├── modals.jsx
│       ├── pages.jsx
│       ├── components.jsx
│       ├── mocks/data.js
│       └── styles/styles.css
│
├── frontend/                                # Step 4 React 앱
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── public/
│   ├── node_modules/                        # gitignored
│   └── src/
│       ├── main.tsx
│       ├── app.jsx                          # hand-off 포팅
│       ├── screens/
│       │   ├── dashboard.jsx
│       │   ├── modals.jsx
│       │   └── pages.jsx
│       ├── components/
│       │   └── components.jsx
│       ├── mocks/
│       │   └── data.js                      # build_frontend_data.py 자동 생성
│       └── styles/
│           └── styles.css
│
├── backend/                                 # Step 5~8
│   ├── .venv/                               # Python 가상환경 (gitignored)
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                          # FastAPI 18 endpoints
│   │   └── data.json                        # mock data (기본값)
│   ├── pipelines/                           # 5단계 자동 갱신
│   │   ├── auto_collectors.py               # 21신호 수집
│   │   ├── collect_news_events.py           # RSS + LLM 분류
│   │   ├── forecast_v2.py                   # Multi-Model
│   │   ├── build_insight.py                 # LLM 인사이트
│   │   ├── build_frontend_data.py           # data.js 자동 생성
│   │   └── preprocessing.py                 # 전처리 유틸
│   └── data/                                # 자동 갱신 산출물
│       ├── _summary.json
│       ├── historical/
│       │   ├── A-1.json ~ A-7.json
│       │   ├── B-1.json ~ B-7.json
│       │   ├── macro-fed.json ~ macro-ust10.json
│       │   └── target-dram.json
│       ├── forecast/
│       │   ├── forecast_v2_*.json
│       │   └── model_comparison.txt
│       ├── news/latest.json
│       ├── events/latest.json
│       └── insight/latest.json
│
└── docs/                                    # PDCA 산출물 (선택)
    ├── 00-pm/prd.md
    ├── 01-plan/sixsense.plan.md
    ├── 02-design/sixsense.design.md
    ├── 03-do/sixsense.do.md
    ├── 04-report/sixsense.report.md
    ├── 05-qa/sixsense.qa-report.md
    └── 07-guide/                            # 본 가이드
        ├── README.md
        └── sixsense-vibe-coding-guide.pptx
```

---

## 🎉 가이드 완료

이 가이드 끝까지 따라하면 다음을 얻습니다:

✅ **공개 URL** (예: https://my-project-eta.vercel.app)
✅ **GitHub repo** (예: https://github.com/<you>/my-project)
✅ **21신호 자동 수집** + **Multi-Model AI 예측** + **LLM 인사이트**
✅ **다른 도메인 응용 능력** (부동산/환율/매출/수요/주가)

## 💬 막힐 때

1. 각 Step 끝의 "자주 발생하는 에러" 먼저 확인
2. [부록 C. FAQ](#부록-c-자주-묻는-질문-faq) 검색
3. Claude (claude.ai) 에 에러 + 컨텍스트 붙여넣기
4. GitHub Issues: https://github.com/chaos72/Sixsense/issues

## 📚 참고

- **실제 사례**: https://sixsense-eta.vercel.app (Sixsense — Server DRAM Price Intelligence)
- **GitHub repo**: https://github.com/chaos72/Sixsense
- **발표용 PPTX**: [sixsense-vibe-coding-guide.pptx](sixsense-vibe-coding-guide.pptx) (28 슬라이드, Dataiku 브랜드 양식)
- **실제 작동 코드**: [code-snippets/](code-snippets/) (Python 3000줄 + JSX 2200줄 + CSS 1000줄)
- **부록 E**: 14화면 와이어프레임
- **부록 F**: data.js SIXSENSE_DATA 스키마
- **부록 G**: Claude Code 사용법
- **부록 H**: 터미널/git/VS Code/JSON/Markdown cheatsheet

---

---

## 부록 E. 14화면 와이어프레임 (S-001 ~ S-014)

비전문가가 Claude Design 에 무엇을 만들어달라고 할 때 참고용. https://sixsense-eta.vercel.app 의 실제 화면 구성.

### S-001 메인 대시보드 (가장 중요)

```
┌────────────────────────────────────────────────────────────────────┐
│ ◉ Sixsense  Server DRAM Price Intelligence              [☾ 다크 모드]│ ← topbar
├────────────────────────────────────────────────────────────────────┤
│ §01 가격 스냅샷  2026-04-22 기준 — 매주 화요일 06:00 자동 갱신       │
│ ┌──────┐┌──────┐┌──────┐┌─────────────────────────┐                │
│ │현재가 ││1~7w  ││8~21w ││  ◆ 예측분석 인사이트   │ ← 4분화 그리드  │
│ │$6.09 ││$5.06 ││$5.08 ││  Gemini gemini-2.5-flash│   (3:4 비율)   │
│ │+4.0% ││-16.9%││-16.7%││  ┌────────┬───────────┐ │                │
│ └──────┘└──────┘└──────┘│  │본문 좌측│CLAUDE 종합│ │                │
│                          │  │ 분석 8줄│  판단     │ │                │
│                          │  │ (clamp) │ headline  │ │                │
│                          │  │  fade   │ A-2 · B-4│ │                │
│                          └────────────────────────┘                  │
├────────────────────────────────────────────────────────────────────┤
│ §02 DRAM 52주 히스토리 + AI 예측      [단기][중장기][전체]            │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │  ─── 실측 (52w)                                                  │ │
│ │  ⋯⋯ Prophet baseline (1~21w, 황색 dotted)                       │ │
│ │  --- HistGBR (1~7w, 보라 long-dash · 6.86%)                      │ │
│ │  ▬▬ GBR★ (1~7w, 청색 · 4.54%)                                   │ │
│ │  ▬▬ LSTM★ (8~21w, 초록 · 9.19%)                                 │ │
│ └────────────────────────────────────────────────────────────────┘ │
│ [Phase 6 Multi-Model 검증 표 2개: 단기 + 중장기]                     │
├────────────────────────────────────────────────────────────────────┤
│ §03 14 신호 통합 현황                                                │
│  Group A (정형 7): A-1 대만공급 | A-2 CapEx | A-3 수출 | A-4 재고 ... │
│  Group B (비정형 7): B-1 IR감성 | B-2 대만뉴스 | B-3 Reddit | B-4 GPR │
├────────────────────────────────────────────────────────────────────┤
│ §05 AI 뉴스 (Top 3)            §06 거시경제 (6개)                    │
│ ┌─────────────────────┐       ┌─────────────────────┐               │
│ │ 삼성·SK하이닉스 AI...│       │ ust10  4.38% ↑ neg │               │
│ │ HBM 부족 경고       │       │ fed    3.64%       │               │
│ │ Micron 메모리 칩... │       │ dxy    98.1  ↓ pos │               │
│ └─────────────────────┘       │ pmi    102.5       │               │
│                               │ krw    1,487 ↓ pos │               │
│                               │ cu     $5.93 ↑ pos │               │
│                               └─────────────────────┘               │
├────────────────────────────────────────────────────────────────────┤
│ §07 글로벌 이벤트 (Top 10)     §08 AI 예측 정확도 (트랙레코드)       │
│ ┌───┬─────┬────────────┬───┐ ┌─────────────────────┐                │
│ │위험│유형 │  제목      │지역│ │ 4주전 예측 $5.00 →실제│                │
│ ├───┼─────┼────────────┼───┤ │ 8주전 예측 $4.80 →실제│                │
│ │high│파업 │삼성 협상.. │한국│ │ ...                  │                │
│ │high│충돌 │우크라이나..│우크│ └─────────────────────┘                │
│ │mid │이변 │일본 지진.. │일본│                                       │
│ │mid │금융 │Fed 금리.. │미국│                                       │
│ │... │ ... │ ...       │... │                                       │
│ └───┴─────┴────────────┴───┘                                       │
├────────────────────────────────────────────────────────────────────┤
│ §09 이번 주 새 수집 데이터 현황       [수집 현황 →]                  │
│ 정형 56건 ✓ | 비정형 64건 ✓ | 수집실패 0건 | 다음 수집까지 6일 22시간 │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ 🔄 수동 갱신 실행 (5단계 백그라운드)                              │ │
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 진행률 바              │ │
│ │ 단계 N/5 · 현재 stage 명                                        │ │
│ └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### S-002 ~ S-014 (모달 + 풀페이지)

| ID | 형태 | 이름 | 핵심 위젯 |
|---|---|---|---|
| S-002 | Modal | AI 예측 근거 | 14신호 contribution bars + CI band + HITL |
| S-003 | Modal | 정형 데이터 Group A 상세 | 7 tab (A-1~A-7) |
| S-004 | Modal | 비정형 데이터 Group B 상세 | 7 tab (B-1~B-7) |
| S-005 | Modal | Graph RAG | 구리 ↔ DRAM 상관관계 시각화 |
| S-006 | Full | AI 뉴스 전체 목록 | 10건 + 상세 카드 |
| S-007 | Modal | 뉴스 원문 & AI 분석 | 단/중/장기 영향 표 |
| S-008 | Full | 거시경제 통합 상세 | 6 tab (ust10 첫번째) + 차트 |
| S-009 | Modal | 주별 신호 스냅샷 | then vs now 비교 |
| S-010 | Full | 글로벌 이벤트 전체 | 10건 + 카테고리 필터 |
| S-011 | Modal | 글로벌 이벤트 상세 | 단/중/장기 영향 + 관련 신호 |
| S-012 | Full | AI 예측 정확도 이력 | 누적 MAPE + 주별 오차 |
| S-013 | Modal | 당시 신호 vs 현재 비교 | 의사결정 사후 검증 |
| S-014 | Full | 데이터 수집 현황 상세 | 21신호 last update + 상태 |

**Claude Design 에 보낼 프롬프트 예시** (위 와이어프레임 첨부 + 다음 문구):

```
첨부한 와이어프레임 (sixsense-wireframe.txt) 의 14화면을 hifi 디자인으로
만들어주세요. S-001 의 §01 가격 스냅샷은 7분화 그리드 (1fr 1fr 1fr 4fr,
가격 3카드 + 인사이트 카드), §02 차트는 4개 모델 라인 동시 표시,
§07 이벤트는 5 카테고리 (국내 반도체/물리적 충돌/기상이변/금융 위기/기타)
유형 칩으로 색 구분 (보라/적/황/청/회).
```

---

## 부록 F. data.js (SIXSENSE_DATA) 스키마 명세

`frontend/src/mocks/data.js` 의 구조. UI 컴포넌트가 이 스키마를 직접 import 해서 사용. `backend/pipelines/build_frontend_data.py` 가 21신호 JSON 을 이 스키마로 자동 변환.

```javascript
// frontend/src/mocks/data.js (자동 생성)
export const SIXSENSE_DATA = {
  // ── meta: 가격 스냅샷 + LLM 인사이트 + Multi-Model 검증 ──
  meta: {
    current: 6.09,                  // 현재가 ($/GB)
    pred7: 5.06,                    // 1~7주 GBR 예측
    pred21: 5.08,                   // 8~21주 LSTM 예측
    currentChange: "+4.0%",         // 전주 대비
    pred7Change: "-16.9%",
    pred21Change: "-16.7%",
    updated: "2026-05-18 06:00 KST",
    model: "GBR (단기) + LSTM (중장기) + Prophet (베이스)",
    confidence: 81,

    // LLM 인사이트
    insight: {
      headline: "AI 수요 견인, 단기 조정 후 안정화",
      summary: "서버 DRAM 가격은 현재 **$6.09**로 상승했으나, GBR 및 LSTM 모델은...",
      tone: "neu",                  // "pos" | "neu" | "neg"
      confidence: 75,
      horizon: "long",              // "short" | "mid" | "long"
      keySignals: ["A-2", "A-3"],
      model: "Gemini gemini-2.5-flash",
      generatedAt: "2026-05-19T11:30:00",
    },

    // Multi-Model 검증 패널
    modelValidation: {
      headline: "🎉 단기 MAPE 7.54% → 4.54% (39.8% 개선)",
      shortRows: [
        { model: "Prophet (기존)",    mape: 7.54, eval: "baseline", winner: false },
        { model: "sklearn HistGBR",  mape: 6.86, eval: "중간",      winner: false },
        { model: "sklearn GBR",      mape: 4.54, eval: "39.8% 개선", winner: true  },
      ],
      midRows: [
        { model: "LSTM (PyTorch 2-layer hidden=64)", mape: 9.19 },
      ],
      trainTimes: [
        { name: "Prophet",     sec: 2.68 },
        { name: "Tree (단기)",  sec: 8.76 },
        { name: "LSTM (중장기)", sec: 13.31 },
      ],
      trainTotal: 24.75,
      architecture: "20개 신호 통합 DataFrame ...",
      envNote: "XGBoost/LightGBM 우선 → macOS libomp 미설치 → sklearn fallback ...",
    },
  },

  // ── history: 52주 실측 시계열 (§02 차트 검정 라인) ──
  history: [
    { week: 1, value: 1.85, x: 1 },
    { week: 2, value: 1.92, x: 2 },
    // ... 52개
  ],

  // ── forecast 4종 (§02 차트 4개 라인) ──
  forecast7: [   // GBR ★ 1~7w 청색
    { week: 1, value: 4.382, lower: 4.16, upper: 4.60, type: "f7" },
    // ... 7개
  ],
  forecast21: [  // LSTM ★ 8~21w 초록
    { week: 8, value: 5.091, lower: 4.58, upper: 5.60, type: "f21" },
    // ... 14개
  ],
  forecast_prophet: [  // Prophet baseline 1~21w 황색
    { week: 1, value: 4.499, type: "prophet" },
    // ... 21개
  ],
  forecast_histgbr: [  // HistGBR 1~7w 보라
    { week: 1, value: 4.199, type: "histgbr" },
    // ... 7개
  ],

  // ── signalsA: 정형 7개 (§03 그룹 A 카드) ──
  signalsA: [
    { id: "A-1", name: "대만 공급망", group: "정형", value: 281.16,
      change: "+2.3%", tone: "pos", spark: [...], source: "Yahoo TSM+UMC" },
    // ... A-2 ~ A-7
  ],

  // ── signalsB: 비정형 7개 (§03 그룹 B 카드) ──
  signalsB: [
    { id: "B-1", name: "Earnings Call 감성", value: 0.0,
      change: "neu", tone: "neu", spark: [...], source: "SEC EDGAR + LLM" },
    // ... B-2 ~ B-7
  ],

  // ── macro: 거시 6개 (§06 거시경제) — ust10 첫번째 ──
  macro: [
    { id: "ust10", name: "미국 10년물 국채금리", value: "4.38%",
      change: "↑ 부정", tone: "neg", history: [4.1, 4.15, 4.2, 4.25, 4.28, 4.35, 4.38] },
    { id: "fed",   name: "미국 금리",         value: "3.64%", change: "동결", tone: "neu", history: [...] },
    { id: "dxy",   name: "달러 인덱스 (DXY)", value: "98.1",  change: "↓ 부정", tone: "pos", history: [...] },
    { id: "pmi",   name: "산업생산지수",      value: "102.5", change: "동결", tone: "neu", history: [...] },
    { id: "krw",   name: "USD/KRW",          value: "1,487", change: "↓ 부정", tone: "pos", history: [...] },
    { id: "cu",    name: "구리 가격",         value: "$5.93", change: "↑ 긍정", tone: "pos", history: [...] },
  ],

  // ── news: AI 뉴스 10건 (§05) ──
  news: [
    { date: "2026-05-15", title: "삼성·SK하이닉스, AI 메모리 부족 경고",
      titleEn: "Samsung and SK Hynix warn ...", source: "Tom's Hardware",
      score: 0.95, tone: "pos", conf: 98, hot: true,
      summary: "삼성과 SK하이닉스는 AI 기반 HBM 수요 폭증으로 ...",
      effects: {
        short: { tone: "pos", text: "단기적인 서버 DDR5 공급 부족 심화." },
        mid:   { tone: "pos", text: "중기적으로 서버 DDR5 공급 제약 유지." },
        long:  { tone: "pos", text: "장기적인 가격 상승 전망 강화." },
      },
      linked: ["B-6 관련", "A-4 관련"],
      link: "https://...",
    },
    // ... 10건 (모두 한국어 title + summary)
  ],

  // ── events: 글로벌 이벤트 10건 (§07) — 5 카테고리 ──
  events: [
    { id: "ev-1", type: "국내 반도체", region: "한국", risk: "high",
      title: "삼성 노사 협상 결렬, 파업 임박", impact: "공급↓",
      date: "2026-05-13",
      summary: "삼성의 노사 협상이 결렬되어 ...",
      effects: { short: {...}, mid: {...}, long: {...} },
      links: [0], affects: ["A-4", "B-2"] },
    { id: "ev-2", type: "물리적 충돌", region: "우크라이나", risk: "high",
      title: "Ukraine war ...", impact: "공급↓", ... },
    { id: "ev-3", type: "기상이변", region: "일본", risk: "mid", ... },
    { id: "ev-4", type: "금융 위기", region: "미국", risk: "high", ... },
    { id: "ev-5", type: "기타", region: "글로벌", risk: "low", ... },
    // ... 10건 (5 카테고리 각 2건씩)
  ],

  // ── accuracy: AI 예측 정확도 (§08) ──
  accuracy: [
    { predDate: "2026-04-22", pred: 5.20, actual: 5.18, errorPct: -0.4 },
    { predDate: "2026-04-15", pred: 5.15, actual: 5.22, errorPct: 1.4 },
    // ... 8건
  ],

  // ── collection: 수집 현황 (§09 풋바) ──
  collection: {
    groupA: [
      { id: "A-1", newItems: 7, status: "success" },
      // ... A-2 ~ A-7
    ],
    groupB: [
      { id: "B-1", newItems: 7, status: "success" },
      // ... B-2 ~ B-7
    ],
    summary: { fail: 0 },
  },
};
```

**중요**: 이 스키마를 정확히 따라야 hand-off UI 가 자동으로 작동합니다. `build_frontend_data.py` 가 backend/data/*.json → 이 스키마로 자동 변환.

---

## 부록 G. Claude Code 사용법 (가장 강력한 도구)

이 가이드의 모든 작업은 Claude Code CLI 에 다음과 같이 한 줄로 시킬 수 있습니다.

### G-1. 설치 + 인증

```bash
# 설치 (Anthropic 공식 CLI)
curl -fsSL https://claude.ai/install.sh | sh

# 인증 (브라우저 자동 열림)
claude login
```

### G-2. 프로젝트 폴더에서 실행

```bash
cd ~/Documents/my-project
claude
```

### G-3. 자주 쓰는 한 줄 요청

| 작업 | 명령 |
|---|---|
| PRD 작성 | `"prd.md 를 18 섹션으로 작성해줘. 주제는 [본인 주제]"` |
| hand-off 포팅 | `"design_handoff/src/ 를 frontend/src/ 로 옮기고 npm run dev 띄워줘"` |
| collector 추가 | `"auto_collectors.py 에 macro-ust10 (FRED DGS10) collector 추가해줘"` |
| 모델 학습 | `"forecast_v2.py 실행하고 결과 보여줘"` |
| 에러 디버깅 | `"방금 에러 [에러 메시지 붙여넣기] 해결해줘"` |
| commit + push | `"지금까지 변경 commit하고 GitHub push 해줘"` |
| Vercel 배포 | `"vercel.json 작성하고 npx vercel --prod 로 배포해줘"` |

### G-4. Claude Code 가 자동으로 하는 것

- 파일 생성/수정 (Read/Write/Edit)
- 터미널 명령 실행 (Bash)
- 외부 정보 검색 (WebFetch/WebSearch)
- git/gh/vercel CLI 호출
- 에러 메시지 자동 분석 + 해결

**팁**: 막힐 때는 그냥 "지금 막혔어, 도와줘" 라고만 해도 Claude 가 컨텍스트 보고 해결책 제시.

---

## 부록 H. 비전문가용 필수 cheatsheet

### H-1. 터미널 기본 (macOS)

| 명령 | 의미 |
|---|---|
| `pwd` | 현재 폴더 위치 출력 |
| `ls` | 현재 폴더 파일 목록 |
| `ls -la` | 숨김 파일 포함 + 상세 |
| `cd 폴더명` | 폴더로 이동 |
| `cd ..` | 상위 폴더로 이동 |
| `cd ~` | 홈 폴더로 이동 |
| `mkdir 이름` | 새 폴더 생성 |
| `touch 파일명` | 빈 파일 생성 |
| `cat 파일명` | 파일 내용 출력 |
| `cp 원본 대상` | 파일 복사 |
| `mv 원본 대상` | 파일 이동 / 이름 변경 |
| `rm 파일` | 파일 삭제 (휴지통 없이) |
| `rm -rf 폴더` | 폴더 통째로 삭제 (위험!) |
| `Ctrl+C` | 실행 중 명령 중단 |
| `Ctrl+L` 또는 `clear` | 화면 지우기 |
| `↑` 화살표 | 이전 명령 불러오기 |
| `Cmd+T` | 새 탭 |
| `Cmd+K` | 터미널 화면 지우기 |

### H-2. git 기본

| 명령 | 의미 |
|---|---|
| `git status` | 현재 상태 (어떤 파일 변경됨?) |
| `git diff` | 변경 내용 보기 |
| `git add 파일` | commit 대상에 추가 |
| `git add .` | 모든 변경 추가 (주의 - .env 같은 파일 제외 확인) |
| `git commit -m "메시지"` | 변경사항 저장 (로컬) |
| `git push` | GitHub 에 업로드 |
| `git pull` | GitHub 에서 다운로드 |
| `git log --oneline` | commit 히스토리 한 줄씩 |
| `git checkout 파일` | 파일 변경 취소 (commit 전) |
| `git branch` | 현재 branch 확인 |
| `git checkout -b 이름` | 새 branch 만들고 이동 |
| `git merge 이름` | 다른 branch 를 현재 branch 에 병합 |
| `git remote -v` | 원격 저장소 URL 확인 |

### H-3. VS Code / Cursor 단축키 (Mac)

| 단축키 | 기능 |
|---|---|
| `Cmd+P` | 파일 빠른 열기 (파일명 입력) |
| `Cmd+Shift+P` | 명령 팔레트 (모든 기능 검색) |
| `Cmd+B` | 사이드바 토글 |
| `Cmd+J` | 터미널 토글 |
| `Cmd+/` | 주석 토글 |
| `Cmd+D` | 같은 단어 추가 선택 |
| `Cmd+S` | 저장 |
| `Cmd+Z` / `Cmd+Shift+Z` | 실행 취소 / 다시 실행 |
| `Cmd+F` | 검색 |
| `Cmd+Shift+F` | 전체 폴더 검색 |
| `Cmd+G` | 다음 검색 결과 |
| `Cmd+,` | 설정 |
| `Cmd+Shift+E` | Explorer 사이드바 |

### H-4. JSON 읽는 법

```json
{
  "key": "value",           ← 키-값 쌍 (쉼표로 구분)
  "number": 42,              ← 숫자는 따옴표 X
  "boolean": true,           ← true / false / null
  "array": [1, 2, 3],        ← 배열 (대괄호)
  "nested": {                ← 객체 안에 객체
    "inner_key": "inner_val"
  },
  "list_of_objects": [
    {"a": 1, "b": 2},
    {"a": 3, "b": 4}
  ]
}
```

**점 표기법으로 접근**:
- `data.key` → "value"
- `data.array[0]` → 1
- `data.nested.inner_key` → "inner_val"
- `data.list_of_objects[1].a` → 3

### H-5. Markdown 작성법 (PRD 등)

```markdown
# 제목 1 (가장 큼)
## 제목 2
### 제목 3

**굵게** *기울임* ~~취소선~~

- 불릿 1
- 불릿 2
  - 들여쓰기 (2 공백)

1. 번호 목록
2. 자동 번호

[링크 텍스트](https://example.com)
![이미지 alt](https://image-url.png)

| 표 헤더 | 헤더 2 |
|---------|--------|
| 셀 1    | 셀 2   |

​```bash
코드 블록 (언어 명시 시 syntax 강조)
echo "Hello"
​```

> 인용문

`인라인 코드`
```

### H-6. 자주 발생하는 macOS 보안 경고

**"앱이 손상되어 열 수 없습니다"** (Claude Code 등 미서명 앱):
```bash
# 시스템 설정 → 개인정보 보호 및 보안 → 하단 "그래도 열기" 클릭
# 또는 터미널에서:
sudo xattr -d com.apple.quarantine /Applications/Claude.app
```

**"개발자를 확인할 수 없음"**:
- 앱을 우클릭 → "열기" → "열기" 한 번 더

---


