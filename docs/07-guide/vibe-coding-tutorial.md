# 🎓 바이브 코딩 튜토리얼 — Claude Desktop 으로 나만의 AI 앱 만들기

> **예시 앱**: **Stocksense** — 내 관심 종목 (Apple/Tesla/Samsung 등) 의 6개월 시세 예측 + AI 인사이트 대시보드
> **사용 도구**: Claude Desktop (claude.ai) 만 사용. 코드는 Claude 가 다 만들어주고, 비전문가는 복사 + 실행만.
> **결과물**: 자신만의 HTTPS URL (예: `https://my-stocksense.vercel.app`) — 친구·동료에게 공유 가능

이 가이드는 **DRAM 가격 예측 사례 (Sixsense)** 를 일반화한 튜토리얼입니다. 같은 패턴으로 가계부·부동산·환율·매출 등 어떤 도메인에도 적용 가능 ([부록 D 참조](#부록-d-다른-도메인-응용)).

---

## 📚 이 가이드의 사용법 (꼭 읽어주세요)

### 누구를 위한 것인가
- ✅ **비전문가** — 코드 한 줄도 안 써 본 분
- ✅ **시간 여유** — 7~10일 (하루 1~2시간씩 진행 가능)
- ✅ **호기심** — "AI 가 진짜 코드 만들어줘?" 궁금한 분

### 따라하기 핵심 원칙

1. **모든 작업은 Claude Desktop 에게 묻는다**
   - "이거 어떻게 해?" 하면 Claude 가 명령어 + 설명 줌
   - 명령어는 복사 → 터미널에 붙여넣기 → Enter
   - 에러 나면 그 에러를 그대로 Claude 에게 붙여넣기

2. **순서대로 진행한다**
   - Step 1 → Step 2 → ... 차례로
   - 한 단계 안 끝나면 다음으로 가지 말 것

3. **검증 박스를 꼭 확인한다**
   - 각 단계 끝에 "이렇게 보이면 OK ✅" 박스 있음
   - 다르면 Claude 에게 "내 화면이 다른데?" 물어보기

4. **막혀도 괜찮다**
   - 비전문가는 막히는 게 정상
   - Claude 에게 "지금 막혔어, 도와줘" 한 번에 해결

---

## 📖 목차

| # | 단계 | 시간 | 난이도 | Claude 에게 물어볼 것 |
|---|---|---|---|---|
| 준비 | [Step 0. 시작 전 마음가짐](#step-0-시작-전-마음가짐) | 5분 | ⭐ | — |
| | [Step 1. Claude Desktop 설치](#step-1-claude-desktop-설치) | 10분 | ⭐ | — |
| | [Step 2. 기본 도구 설치](#step-2-기본-도구-설치) | 30분 | ⭐⭐ | "Mac 에서 Homebrew, Node, Python, Git 설치해줘" |
| 기획 | [Step 3. 나만의 앱 아이디어 정하기](#step-3-나만의-앱-아이디어-정하기) | 30분 | ⭐ | "내가 만들 앱은 ... 인데 PRD 어떻게 시작?" |
| | [Step 4. Claude Desktop 으로 PRD 작성](#step-4-claude-desktop-으로-prd-작성) | 2~3시간 | ⭐⭐ | "이 주제로 PRD 마크다운 만들어줘" |
| 디자인 | [Step 5. Claude Design 으로 UI 받기](#step-5-claude-design-으로-ui-받기) | 4~6시간 | ⭐⭐ | (Claude Design 별도 사이트) |
| | [Step 6. 받은 코드 로컬에서 실행](#step-6-받은-코드-로컬에서-실행) | 1~2시간 | ⭐⭐⭐ | "이 코드 어떻게 실행해?" |
| 데이터 | [Step 7. 실데이터 수집 코드 요청](#step-7-실데이터-수집-코드-요청) | 1~2일 | ⭐⭐⭐ | "Yahoo Finance 에서 Apple 주가 받는 Python 코드 만들어줘" |
| AI | [Step 8. AI 예측 모델 코드 요청](#step-8-ai-예측-모델-코드-요청) | 1일 | ⭐⭐⭐ | "이 데이터로 6개월 예측하는 모델 만들어줘" |
| | [Step 9. AI 분석 코멘트 자동 생성](#step-9-ai-분석-코멘트-자동-생성) | 4시간 | ⭐⭐ | "이 데이터를 보고 한국어 분석 코멘트 만들어줘" |
| 배포 | [Step 10. Vercel 무료 배포](#step-10-vercel-무료-배포) | 30분 | ⭐⭐ | "이거 Vercel 에 배포하는 법 알려줘" |
| 운영 | [Step 11. 친구·동료에게 공유](#step-11-친구동료에게-공유) | 10분 | ⭐ | (URL 카톡으로 보내기) |
| 부록 | [A. Claude Desktop 100% 활용법](#부록-a-claude-desktop-100-활용법) | — | — | — |
| | [B. 자주 발생하는 에러 모음](#부록-b-자주-발생하는-에러-모음) | — | — | — |
| | [C. 터미널/git/JSON 기본](#부록-c-터미널git기본) | — | — | — |
| | [D. 다른 도메인 응용](#부록-d-다른-도메인-응용) | — | — | — |
| | [E. Stocksense 완성본 참고](#부록-e-stocksense-완성본-참고) | — | — | — |

---

## Step 0. 시작 전 마음가짐

### 왜 "바이브 코딩"인가
- **바이브 코딩** = AI 와 대화하며 코드 작성. 비전문가도 가능.
- 옛날엔: 코드 = 개발자만. 책 100권 + 학원 1년.
- 지금은: AI 가 코드 짜줌. 비전문가는 "무엇을 만들고 싶은가" + "복사·붙여넣기" 만 하면 됨.

### 7~10일 분량 = 하루 1~2시간씩
- 한 번에 다 할 필요 X
- 일주일 잡고 차근차근
- 일 끝나고 1시간씩 → 일주일 + 주말 = 충분

### 비용
- **0원** (무료 도구만)
- Claude Desktop: 무료 (Pro 결제는 더 많이 쓸 수 있지만 가이드는 무료로도 가능)
- Vercel: 무료 (월 100GB)
- 데이터 API: 무료 (Yahoo Finance + FRED + RSS)
- 도메인: vercel.app 무료 도메인 사용

### 결과물 (가이드 끝까지 따라하면)
- **공개 URL** (예: `https://my-stocksense.vercel.app`) — 카톡으로 친구 보내기 가능
- **AI 가 만든 14화면 대시보드** — 다크/라이트 모드, 모바일도 작동
- **자동 데이터 수집** — 매일 또는 매주 갱신
- **AI 분석 코멘트** — "지금 사야 할까?" 한국어로 답
- **본인의 코드** — GitHub 에 저장, 누구나 볼 수 있음

---

## Step 1. Claude Desktop 설치

> **시간**: 10분
> **목표**: claude.ai 또는 Claude Desktop 앱 설치 + 로그인

### 1.1. 두 가지 옵션 중 선택

**옵션 A: 웹 (가장 쉬움)** ⭐
- 브라우저로 https://claude.ai 접속
- 별도 설치 X
- 단 매번 브라우저 켜야 함

**옵션 B: 데스크탑 앱**
- https://claude.ai/download 접속
- "Download for Mac" 클릭
- .dmg 파일 다운로드 → Applications 폴더로 드래그
- Spotlight (Cmd+Space) → "Claude" → Enter
- 한 번 설치 후 Cmd+Tab 으로 빠르게 전환 가능

이 가이드는 **옵션 B (데스크탑 앱) 권장** — 작업 효율 높음.

### 1.2. 로그인

- Google 계정 또는 이메일로 가입
- 무료 plan 로 시작 (Pro 결제 안 해도 됨)

### 1.3. 첫 대화 테스트

Claude 채팅창에:
```
안녕! 나는 비전문가야. 앞으로 너와 함께 앱 만들 거야. 잘 부탁해!
```

Claude 가 친절하게 답하면 OK ✅

### Step 1 검증 ✅
- [ ] claude.ai 또는 Claude Desktop 접속 가능
- [ ] 계정 로그인 완료
- [ ] 첫 대화 성공

---

## Step 2. 기본 도구 설치

> **시간**: 30분
> **목표**: 코드 실행에 필요한 도구 (Homebrew/Node/Python/Git) 설치
> **포인트**: 모든 명령을 Claude 에게 물어보고 받은 답을 그대로 따라하기

### 2.1. Claude 에게 도와달라고 하기

Claude Desktop 채팅창에:

```
나는 macOS Mac (M2 또는 Intel 모름) 사용자이고 비전문가야.
다음 도구를 설치하고 싶어:
- Homebrew
- Node.js (최신 LTS)
- Python 3.11
- Git
- GitHub CLI (gh)
- VS Code

각각 어떻게 설치하는지 명령어를 한 줄씩 알려줘.
명령어는 그대로 복사할 수 있게 ```bash 코드 블록으로 줘.
설치 후 확인 방법도 알려줘.
```

Claude 가 다음과 같이 답할 거에요 (실제 예시):

```bash
# 1. Homebrew 설치 (먼저)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Node + Python + Git + gh + VS Code 한 번에
brew install node python@3.11 git gh
brew install --cask visual-studio-code

# 3. 확인
brew --version
node --version
python3 --version
git --version
gh --version
code --version
```

### 2.2. 터미널 열기

- Spotlight (Cmd+Space) → "터미널" 입력 → Enter
- 또는 Launchpad → 기타 → 터미널

### 2.3. 명령어 그대로 복사

1. Claude 답변의 명령어 영역에 마우스 올림
2. 우측 상단 "Copy" 버튼 클릭
3. 터미널 클릭 → Cmd+V → Enter

### 2.4. 첫 명령 (Homebrew 설치) — 약 10분

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**중간에 일어나는 일**:
- "Password:" → 본인 Mac 비밀번호 입력 (화면에 안 보임, 그냥 타이핑 후 Enter)
- "Press RETURN/ENTER to continue" → Enter
- 다운로드 + 설치 진행 (약 5~10분)
- 마지막에 "Next steps" 안내

**Next steps 가 보이면**: 거기 적힌 명령 그대로 실행 (보통 `eval "$(/opt/homebrew/bin/brew shellenv)"`).

### 2.5. 나머지 도구 설치

```bash
brew install node python@3.11 git gh
brew install --cask visual-studio-code
```

약 3~5분.

### 2.6. 설치 확인

```bash
brew --version    # Homebrew 4.x.x
node --version    # v20 이상
python3 --version # Python 3.11.x
git --version     # git version 2.x.x
gh --version      # gh version 2.x.x
```

5개 모두 버전이 출력되면 OK ✅

### 2.7. 막혔다면

터미널에 빨간 에러 메시지가 뜨면, **에러 전체를 복사** → Claude Desktop 에 붙여넣기:

```
방금 [명령어] 했더니 이런 에러가 났어:

[에러 전체 붙여넣기]

어떻게 해결?
```

Claude 가 진단 + 해결 명령 줌.

### Step 2 검증 ✅
- [ ] `brew --version` → 4.x 이상
- [ ] `node --version` → v18 이상
- [ ] `python3 --version` → 3.9 이상
- [ ] `git --version` → 2.x
- [ ] `gh --version` → 2.x

---

## Step 3. 나만의 앱 아이디어 정하기

> **시간**: 30분
> **목표**: "내가 만들 앱이 무엇인지" 한 줄로 정의

### 3.1. 좋은 아이디어의 조건

비전문가 첫 앱으로 좋은 조건:

| 조건 | 이유 |
|---|---|
| **외부 데이터 API 무료** | 데이터 비용 0원 |
| **시계열 데이터** | AI 예측 가능 |
| **개인 관심사** | 만들면서 재미있음 |
| **결과 = 의사결정** | "사야 할까? 팔아야 할까?" 같은 답 |

### 3.2. 추천 도메인 5가지

| # | 앱 이름 (가칭) | 무엇? | 무료 데이터 |
|---|---|---|---|
| 1 | **Stocksense** ⭐ (본 가이드 예시) | 내 관심 종목 6개월 예측 | Yahoo Finance + FRED |
| 2 | **Realsense** | 우리 동네 아파트 시세 예측 | KB부동산 + 통계청 + 한국은행 |
| 3 | **Walletsense** | 내 카드 지출 분석 + 다음달 예측 | 신한카드 API (선택) + 가계부 CSV |
| 4 | **Travelsense** | 항공권 가격 추적 + 최적 구매 시점 | Skyscanner RSS + Google Flights |
| 5 | **Weatherbiz** | 우리 가게 매출 vs 날씨 분석 | 기상청 + 본인 POS 데이터 |

### 3.3. 이 가이드는 **Stocksense** 로 진행

본인이 다른 도메인을 선택하면 [부록 D](#부록-d-다른-도메인-응용) 참고하여 가이드의 신호/모델을 교체.

### 3.4. Claude Desktop 으로 아이디어 다듬기

```
내가 만들고 싶은 앱: Stocksense

핵심: 내 관심 종목 5~10개 (예: Apple, Tesla, Samsung, NVIDIA, SK하이닉스)
의 다음 1~6개월 가격을 AI 가 예측하고, "지금 사야 할까/팔아야 할까"
한국어 코멘트를 매일 보여주는 대시보드.

비전문가 입장에서 이 아이디어가 실현 가능한지 + 어떤 데이터/모델/UI 가
필요한지 친절하게 설명해줘.
```

Claude 가 답:
- "충분히 가능. Yahoo Finance 무료 API + LSTM 모델 + Claude API 인사이트 조합으로 일주일이면 시범판 완성"
- 추가 신호 추천 (금리/PMI/뉴스 감성 등)
- 화면 예시 (메인 + 종목별 상세 + AI 코멘트)

### Step 3 검증 ✅
- [ ] 만들 앱의 한 줄 정의 작성
- [ ] 주요 사용자 (본인 또는 타겟) 1명 정함
- [ ] 무료 데이터 소스 1개 이상 확인 (Yahoo Finance 등)

---

## Step 4. Claude Desktop 으로 PRD 작성

> **시간**: 2~3시간
> **목표**: 마크다운 파일 (`prd.md`) 18 섹션 완성

### 4.1. PRD 가 왜 필요한가
- 없으면: Claude Design 에 "앱 만들어줘" 만 함 → 매번 다른 결과 → 시간 낭비
- 있으면: PRD 첨부 → 14화면 한 번에 정확히 받음

### 4.2. 프로젝트 폴더 생성

터미널에서:
```bash
mkdir -p ~/Documents/my-stocksense
cd ~/Documents/my-stocksense
```

### 4.3. Claude Desktop 으로 PRD 1차 생성

다음을 그대로 복사해서 Claude 에게 보내기:

```
나는 비전문가야. 다음 앱의 PRD (Product Requirements Document) 를
마크다운 파일로 작성해줘.

## 앱 정보
- 이름: Stocksense
- 한 줄 정의: 내 관심 종목 5~10개의 다음 1~6개월 가격을 AI 로 예측하고
              "지금 사야 할까/팔아야 할까" 한국어 코멘트를 매일 보여주는 대시보드
- 대상 사용자: 개인 투자자 (월 1~10회 매매)
- 차별점: 단순 차트 X. 실데이터 신호 15~20개 + Multi-Model 앙상블 + LLM 분석

## 필수 18 섹션 (한국어로 작성)
1.  한 줄 정의
2.  배경과 동기
3.  목표와 비목표
4.  페르소나 (3명, 각 페르소나의 핵심 니즈 1개씩)
5.  핵심 가치 명제 (5가지)
6.  사용자 여정 (User Journey)
7.  화면 목록 (14화면, S-001 ~ S-014)
8.  핵심 기능 (Feature List)
9.  데이터 신호 (정형 7 + 비정형 5 + 거시 5 + 타겟 1 = 18신호)
10. AI 모델 전략 (단기/중장기 분리)
11. 시스템 아키텍처 (간단히)
12. API 명세 (10개 정도 GET endpoint)
13. 디자인 토큰 (색상, 폰트)
14. 검증 기준
15. 위험 분석
16. 일정 (4주)
17. 미래 계획
18. 참고 자료

분량: 각 섹션 최소 1 문단. 전체 200~400줄.

출력 형식: 마크다운 코드 블록 (```markdown ... ```) 으로 감싸서 전체 내용.
```

Claude 가 약 1~2분 동안 PRD 초안 출력.

### 4.4. PRD 파일로 저장

Claude 출력 마크다운 → 우측 상단 "Copy" → 터미널에서:
```bash
pbpaste > prd.md
```

또는 VS Code 로:
```bash
code prd.md
```
→ 새 파일 → Cmd+V → Cmd+S 저장

### 4.5. PRD 보완 (필수 2~3회)

#### 보완 1: 화면 14개 자세히
```
앞서 만든 PRD 의 화면 14개를 각각 다음 형식으로 자세히 보강해줘.

## S-001 [화면 이름]
- 위치: 메인 / 모달 / 풀페이지
- 핵심 위젯 5~7개 (각 위젯의 데이터 소스 + 사용자 행동)
- 모바일에서도 작동하는지
- mock 데이터 1개 예시 (JSON 형식)
```

#### 보완 2: 데이터 신호 18개 명세
```
PRD 의 18신호 각각에 대해 다음을 추가해줘.

## A-1 [신호 이름]
- 그룹: 정형 / 비정형 / 거시 / 타겟
- 데이터 소스: Yahoo Finance / FRED / 통계청 등 (URL)
- API 키 필요 여부: O / X
- 갱신 주기: 일간 / 주간 / 월간
- 단위: $ / % / 개
- 예상 값 범위: 0 ~ 1000
- 왜 이 신호가 가격 예측에 도움?
```

#### 보완 3: 페르소나 시나리오
```
PRD 의 페르소나 3명 각각에 대해 다음을 추가해줘.

## 페르소나 1: [이름]
- 하루 일과: 06:00 ~ 23:00 (이 앱은 언제 봄?)
- 가장 중요하게 보는 화면: S-001 / S-002 등
- 의사결정 흐름: 이 앱 보고 → 무엇을 함?
- 만족 기준: 어떤 결과가 나와야 "좋다" 평가?
```

### 4.6. PRD 검증

다음 질문에 prd.md 만 보고 답할 수 있어야 OK:

| Q | A 가능? |
|---|---|
| 무엇을 만드는가? | 한 줄 정의 섹션 |
| 누가 쓰는가? | 페르소나 |
| 핵심 화면 3개? | S-001 + 모달 2개 |
| 데이터는 어디서? | 데이터 신호 18개 |
| AI 가 무엇을 함? | AI 모델 전략 |
| 4주 후 완성? | 일정 섹션 |

### 4.7. git 으로 백업

```bash
cd ~/Documents/my-stocksense
git init
echo ".env" > .gitignore
git add prd.md .gitignore
git commit -m "docs: PRD 초안 작성"
```

### Step 4 검증 ✅
- [ ] `~/Documents/my-stocksense/prd.md` 존재
- [ ] 18 섹션 모두 채워짐
- [ ] 화면 14개 + 데이터 신호 18개 명세
- [ ] git commit 완료

### 막혔을 때
- Claude 출력이 너무 짧음 → "더 자세히, 각 섹션 1 페이지" 요청
- 18 섹션 중 일부 누락 → "10번 11번 누락됐어, 추가해줘"
- 마크다운 형식 망가짐 → "마크다운만, 다른 텍스트 빼고" 요청

---

## Step 5. Claude Design 으로 UI 받기

> **시간**: 4~6시간 (디자인 도구 익히는 시간 포함)
> **목표**: 14화면 hifi UI 를 Hand-off 패키지로 받기

### 5.1. ⚠️ 가장 중요한 원칙

> **이 단계에서 받은 UI 가 모든 후속 작업의 SSOT (단일 진실원) 입니다.**
> 받은 UI 를 무시하고 "내가 다시 디자인" 하면 모든 작업이 어긋납니다.
> 마음에 안 들면 Claude Design 에 "수정 요청" 으로 보완하세요.

### 5.2. Claude Design 접속

1. https://claude.com/design 접속
2. Claude Pro 계정으로 로그인 (월 $20, 무료 trial 가능)
3. "Start Designing" 또는 "New Project" 클릭
4. 프로젝트 이름: "My Stocksense"

### 5.3. PRD 첨부 + 첫 프롬프트

좌측 채팅창:
1. 📎 아이콘 (첨부) 클릭
2. `~/Documents/my-stocksense/prd.md` 선택 → 첨부
3. 프롬프트 입력:

```
첨부한 PRD 를 바탕으로 hifi UI 를 만들어주세요.

요구사항:
1. 화면 수: 14개 (PRD의 S-001 ~ S-014 그대로)
2. 언어: 한국어 100%
3. 폰트: Pretendard Variable (한글), JetBrains Mono (숫자)
4. 다크/라이트 모드: 토글 버튼 (topbar 우측)
5. 색상 토큰:
   - 배경 라이트: warm white #fafaf8
   - 배경 다크: charcoal #1a1a1c
   - 강조: 상승(녹색 #16a34a), 중립(황색 #ca8a04), 하락(적색 #dc2626)
   - info: #2563eb

6. 메인 화면 (S-001) 구성:
   ┌─────────────────────────────────────────────┐
   │ §01 가격 스냅샷 — 종목별 카드 5~10개          │
   │ §02 차트 — 1년 히스토리 + 6개월 예측         │
   │ §03 신호 통합 현황 — 18신호 카드 그리드       │
   │ §04 AI 인사이트 — Claude 분석 코멘트 카드     │
   │ §05 뉴스 — Top 10 (한국어)                  │
   │ §06 거시지표 — 5 카드 (금리/환율/유가/...)    │
   │ §07 글로벌 이벤트 — 위험도 칩 + 카테고리     │
   │ §08 예측 정확도 — 트랙레코드                  │
   │ §09 데이터 수집 현황 + 수동 갱신 버튼         │
   └─────────────────────────────────────────────┘

7. 모달/팝업: S-002 ~ S-013 은 클릭 시 모달, S-006/S-008/S-010/S-012/S-014 는 풀페이지
8. 모바일 반응형: 320px 까지 작동
9. 산출물: React jsx + CSS + mock data.js (모든 컴포넌트 + 가짜 데이터까지)

mock 데이터는 PRD 의 18신호를 모두 채워서 14화면 모두 데이터처럼 표시되게.
```

### 5.4. Claude Design 동작 (5~15분)

- Claude 가 14화면 생성
- 우측 프리뷰에 실시간 표시
- 각 화면을 클릭하며 검토

### 5.5. 마음에 안 드는 부분 수정 요청

```
S-001 메인 대시보드 의 §02 차트가 너무 작아요.
화면 너비의 80% 로 키워주세요.
또 종목 5개 모두 한 차트에 겹쳐서 표시되게 해주세요.
```

```
§04 AI 인사이트 카드가 §01 가격 스냅샷 옆에 있는 게 더 좋겠어요.
가격 스냅샷 3카드 + 인사이트 카드 1개 → 4분화 그리드 (1:1:1:2 비율)
```

```
다크 모드에서 차트 색상이 잘 안 보여요.
강조 색상을 더 밝게 (녹색 #4ade80, 적색 #f87171) 해주세요.
```

원하는 모양 나올 때까지 5~10회 반복.

### 5.6. Hand-off 패키지 다운로드

1. 우측 상단 "Export" 또는 "Hand-off" 버튼
2. 옵션:
   - ✅ "Include source files" (jsx)
   - ✅ "Include mock data" (data.js)
   - ✅ "Format: React" (Next.js X)
3. .zip 다운로드

### 5.7. 다운로드한 zip 압축 해제

터미널에서:
```bash
cd ~/Downloads
unzip my-stocksense-handoff.zip -d ~/Documents/my-stocksense/design_handoff
ls ~/Documents/my-stocksense/design_handoff
```

**이렇게 보이면 OK** ✅:
```
README.md
src/
├── app.jsx
├── dashboard.jsx
├── modals.jsx
├── pages.jsx
├── components.jsx
├── mocks/data.js
└── styles/styles.css
```

### 5.8. Hand-off README 정독

Claude Desktop 에:
```
이 README 파일을 읽고 중요한 내용을 한국어로 요약해줘:

[README.md 내용 그대로 붙여넣기]
```

Claude 가 핵심 요약 (디자인 토큰, 컴포넌트 사용법, 데이터 스키마).

### 5.9. git 백업

```bash
cd ~/Documents/my-stocksense
git add design_handoff/
git commit -m "design: Claude Design hand-off 14화면 + mock data"
```

### Step 5 검증 ✅
- [ ] `design_handoff/src/` 안에 5개 jsx + mock + styles
- [ ] 14화면 모두 만족스러운 상태
- [ ] git commit 완료

### 막혔을 때
- "Hand-off 버튼이 없어" → Pro 결제 필요할 수 있음. claude.ai/pricing 확인.
- "14화면 다 안 만들어" → "S-008부터 누락됐어, 추가해줘" 요청
- "한국어가 깨져" → "Pretendard 폰트 명시" 요청
- "데이터가 너무 단순" → "PRD 의 18신호 mock 을 53주 분량으로 채워줘"

---

## Step 6. 받은 코드 로컬에서 실행

> **시간**: 1~2시간
> **목표**: hand-off 를 `npm run dev` 로 띄워서 http://localhost:5173 에서 14화면 확인

### 6.1. Claude Desktop 에게 도움 요청

```
나는 비전문가야. 방금 Claude Design 에서 받은 React 코드가
~/Documents/my-stocksense/design_handoff/src/ 에 있어.

이걸 npm run dev 로 실행 가능한 Vite + React 19 + TypeScript 프로젝트로
변환하고 싶어. 다음 명령어를 한 줄씩 그대로 복사할 수 있게 알려줘:

1. Vite 프로젝트 초기화 (frontend 폴더로)
2. hand-off src/ 통째로 복사
3. main.tsx 가 app.jsx 를 import 하도록 수정
4. index.html 의 title + meta 한국어로 수정
5. npm install
6. npm run dev

각 단계마다 "이렇게 보이면 OK" 표시도 추가해줘.
```

Claude 가 정확한 명령어 + 검증 박스 줌. 그대로 따라하기.

### 6.2. 실제 명령 (Claude 가 안내할 예시)

```bash
cd ~/Documents/my-stocksense

# 1. Vite + React + TS 초기화
npm create vite@latest frontend -- --template react-ts
# 질문에 "Y" Enter

# 2. hand-off src 복사
cp -r design_handoff/src/* frontend/src/

# 3. main.tsx 수정
cat > frontend/src/main.tsx << 'EOF'
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

# 4. index.html 수정
cat > frontend/index.html << 'EOF'
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Stocksense — 내 관심 종목 AI 예측</title>
    <meta name="description" content="개인 투자자를 위한 AI 시세 예측 + 분석 코멘트 대시보드" />
    <meta property="og:title" content="Stocksense" />
    <meta property="og:description" content="AI 가 매일 분석해주는 내 관심 종목 6개월 예측" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# 5. 의존성 설치
cd frontend && npm install

# 6. 개발 서버 실행
npm run dev
```

### 6.3. 브라우저에서 확인

http://localhost:5173 자동 또는 수동으로 열기.

**확인 항목**:
- [ ] S-001 메인 대시보드 표시
- [ ] §01 가격 스냅샷 5~10 카드 (mock 데이터)
- [ ] §02 차트 표시
- [ ] §04 AI 인사이트 카드 (mock 텍스트)
- [ ] 다크/라이트 토글 작동
- [ ] 카드 클릭 → 모달 팝업
- [ ] 모바일 반응형 (브라우저 너비 줄여서 확인)

### 6.4. 에러 발생 시

터미널 에러 그대로 → Claude Desktop:

```
방금 npm run dev 했더니 이런 에러가 났어:

[빨간 에러 전체 붙여넣기]

해결 명령어 알려줘.
```

자주 발생하는 에러 (Claude 가 자동 해결):

| 에러 | 원인 | 해결 |
|---|---|---|
| `Cannot find module './app.jsx'` | import 경로 오타 | main.tsx 의 경로 확인 |
| 흰 화면 (콘솔 에러) | data.js 의 export 누락 | data.js 끝에 `export const SIXSENSE_DATA = ...` |
| 한글 깨짐 | Pretendard 폰트 미로드 | index.html 에 폰트 CDN 추가 |
| 다크 모드 토글 안 보임 | hand-off 누락 | app.jsx 의 topbar 영역에 토글 버튼 추가 요청 |

### 6.5. git 백업

```bash
cd ~/Documents/my-stocksense

# .gitignore 에 node_modules 추가
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore
echo ".vite/" >> .gitignore

git add frontend/ .gitignore
git commit -m "feat: Vite + React 19 포팅, 14화면 mock 데이터로 작동"
```

### Step 6 검증 ✅
- [ ] http://localhost:5173 HTTP 200
- [ ] 14화면 모두 표시
- [ ] 다크/라이트 토글 작동
- [ ] mock 데이터로 차트/카드/뉴스 표시
- [ ] git commit 완료

---

## Step 7. 실데이터 수집 코드 요청

> **시간**: 1~2일
> **목표**: mock 데이터 → 실제 Yahoo Finance + FRED + 뉴스 데이터로 교체
> **결과물**: `backend/data/historical/<신호>.json` 18개 파일

### 7.1. 백엔드 폴더 + Python 환경 구성

Claude Desktop:

```
나는 Stocksense 앱의 백엔드를 만들 거야. 다음을 해줘:

1. backend/ 폴더 생성
2. Python 3.11 가상환경 (.venv) 만들기
3. 필요한 패키지 설치 명령 (requests, pandas, yfinance, feedparser, python-dotenv, scikit-learn, prophet, torch, fastapi, uvicorn)
4. backend/data/historical, backend/data/forecast 등 하위 폴더 생성

한 줄씩 그대로 복사할 수 있는 명령어로 알려줘.
```

Claude 답변 (예시):
```bash
cd ~/Documents/my-stocksense
mkdir -p backend/data/{historical,forecast,news,insight}
mkdir -p backend/pipelines backend/app

cd backend
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install requests pandas numpy yfinance feedparser python-dotenv
pip install scikit-learn prophet torch
pip install fastapi uvicorn[standard]
```

### 7.2. 18신호 수집 코드 한 번에 요청

```
나는 Stocksense 앱의 18신호 수집 Python 코드를 만들 거야.
파일: backend/pipelines/auto_collectors.py

다음 18신호를 각각 collect_<id>() 함수로 작성해줘.
- 모든 함수는 (data: list, mode: str, source: str) 튜플 반환
- data 는 [{"week": "YYYY-MM-DD", "value": 123.45}, ...] 형식
- 주간 데이터 (월요일 기준 정규화)
- 기간: 최근 53주

## 정형 7개
1. A-1: Apple 주가 (Yahoo Finance AAPL)
2. A-2: Tesla 주가 (TSLA)
3. A-3: Samsung 주가 (005930.KS)
4. A-4: NVIDIA 주가 (NVDA)
5. A-5: SK하이닉스 (000660.KS)
6. A-6: S&P 500 지수 (^GSPC)
7. A-7: KOSPI 지수 (^KS11)

## 비정형 5개 (뉴스 헤드라인 카운트 + 키워드 sentiment)
1. B-1: Apple 관련 뉴스 감성 (Google News RSS "Apple stock")
2. B-2: Tesla 관련 뉴스 감성 (RSS "Tesla")
3. B-3: AI/반도체 뉴스 (RSS "AI semiconductor")
4. B-4: Reddit r/wallstreetbets (Hacker News API 대체 가능)
5. B-5: 시장 공포지수 (VIX, ^VIX)

## 거시 5개
1. macro-fed: FRED DFF (Effective Fed Funds Rate)
2. macro-dxy: 달러 인덱스 (DX-Y.NYB)
3. macro-cpi: FRED CPIAUCSL (CPI)
4. macro-ust10: FRED DGS10 (10년물 국채금리)
5. macro-oil: WTI 원유 (CL=F)

## 타겟 1개
- target-portfolio: 위 5개 종목 (AAPL/TSLA/Samsung/NVDA/Hynix) 동등 가중 평균

## 기타 요구사항
- .env 파일에서 API 키 자동 로드
- COLLECTORS 리스트 + main() 함수로 한 번에 실행
- 사용법: python3 auto_collectors.py --all  또는  python3 auto_collectors.py A-1
- 결과 저장: backend/data/historical/<id>.json

전체 코드를 ```python 블록으로 줘. 약 500~800줄 예상.
```

Claude 가 약 1~2분 후 전체 코드 출력 (~500줄).

### 7.3. 코드 저장

Claude 출력의 "Copy" → 터미널:
```bash
cd ~/Documents/my-stocksense
# VS Code 로 열어서 저장
code backend/pipelines/auto_collectors.py
# 새 파일에 붙여넣기 → Cmd+S
```

### 7.4. 첫 실행 (한 신호씩 검증)

```bash
cd ~/Documents/my-stocksense/backend
source .venv/bin/activate
python3 pipelines/auto_collectors.py A-1
```

**이렇게 보이면 OK** ✅:
```
  ✅ A-1           53주 · Yahoo Finance AAPL
```

확인:
```bash
cat data/historical/A-1.json | python3 -m json.tool | head -10
```

### 7.5. 전체 18신호 한 번에

```bash
python3 pipelines/auto_collectors.py --all
```

약 1~3분 소요. 18개 ✅ 표시.

### 7.6. .env 에 API 키 등록 (FRED 등 필요 시)

대부분 무료 API 는 키 없이 가능. 단 일부는 가입 필요:

```bash
# .env 파일 (~/Documents/my-stocksense/.env)
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Step 8/9 LLM 용 (선택)
GEMINI_API_KEY=AIzaxxxxx        # 무료 fallback
```

각 키 발급 방법은 Claude Desktop 에 "Anthropic API 키 어떻게 받아?" 물어보기.

### 7.7. git 백업

```bash
cd ~/Documents/my-stocksense
git add backend/
git commit -m "feat(data): 18신호 자동 수집 (Yahoo + FRED + RSS)"
```

### Step 7 검증 ✅
- [ ] `backend/data/historical/` 안에 18개 JSON 파일
- [ ] 각 파일에 53주 정도 데이터
- [ ] `cat data/historical/A-1.json | python3 -m json.tool` 출력 확인
- [ ] git commit 완료

### 막혔을 때
- "yfinance 429 에러" → "각 ticker 사이 sleep 0.5 추가해줘" 요청
- "FRED CSV 빈 값 에러" → "빈 값 + dot(.) 처리하는 if 추가" 요청
- "한국 종목 (005930.KS) 안 됨" → ticker 형식 확인 (.KS = 한국 거래소)

---

## Step 8. AI 예측 모델 코드 요청

> **시간**: 1일
> **목표**: 18신호로 단기(1~7주) + 중장기(8~26주) target-portfolio 예측

### 8.1. Claude Desktop 으로 forecast 코드 요청

```
나는 Stocksense 앱의 AI 예측 모델을 만들 거야.
파일: backend/pipelines/forecast_v2.py

다음 3개 모델로 target-portfolio (5개 종목 동등 가중) 를 예측:

## 단기 (1~7주)
- sklearn GradientBoostingRegressor
- features: 18신호의 lag(1,2,4,8) + rolling(4,12) + target 자체 lag
- 검증: 마지막 28주 held-out MAPE
- 목표: MAPE 7% 이하

## 중장기 (8~26주)
- PyTorch LSTM (2 layer, hidden=64, dropout=0.2)
- features: 18신호 + target 시계열
- input_len=12, output_len=26 (seq2seq)
- 검증: 마지막 시퀀스 held-out MAPE
- 목표: MAPE 12% 이하

## Baseline
- Prophet (weekly_seasonality, 21주 예측)
- 비교용

## 입출력
- 입력: backend/data/historical/*.json 18개
- 출력 1: backend/data/forecast/forecast_v2.json
  (models.prophet.predictions, models.tree_short.predictions, models.lstm_mid.predictions)
- 출력 2: backend/data/forecast/model_comparison.txt
  (단기 MAPE 표 + 중장기 MAPE + 학습 시간)

## preprocessing.py 도 같이 만들어줘
- load_all_signals() → 18신호 wide format DataFrame
- make_lag_features() → 트리용 lag/rolling features
- make_sequences() → LSTM 용 seq2seq

전체 코드를 ```python 블록으로 줘. 두 파일 합쳐서 약 600~800줄 예상.
```

Claude 답변 (2~3분) → 2개 파일 코드.

### 8.2. 코드 저장

```bash
code backend/pipelines/preprocessing.py
# Claude 의 preprocessing.py 코드 붙여넣기 → Cmd+S

code backend/pipelines/forecast_v2.py
# Claude 의 forecast_v2.py 코드 붙여넣기 → Cmd+S
```

### 8.3. 실행

```bash
cd ~/Documents/my-stocksense/backend
source .venv/bin/activate
python3 pipelines/forecast_v2.py
```

약 15~30초 소요. 출력:
```
[1/4] 데이터 로드 + 전처리
  → 53주 × 18열
[2/4] Prophet (baseline)
  → 21주 예측, 2.5s
[3/4] GBR (단기 1~7w)
  → MAPE 5.2%, 8.7s
[4/4] LSTM (중장기 8~26w)
  → MAPE 10.8%, 12.5s

✅ 저장: backend/data/forecast/forecast_v2.json
```

### 8.4. 검증

```bash
cat backend/data/forecast/model_comparison.txt
```

**목표 충족 확인**:
- 단기 GBR MAPE ≤ 7% ✅
- 중장기 LSTM MAPE ≤ 12% ✅

미달 시 Claude 에게:
```
단기 MAPE 가 10% 로 목표 7% 초과. 어떻게 개선?
```
→ Claude: "n_estimators 늘리기, hyperparameter 튜닝, 신호 추가" 등 제안.

### Step 8 검증 ✅
- [ ] `backend/data/forecast/forecast_v2.json` 생성
- [ ] `model_comparison.txt` MAPE 목표 충족
- [ ] git commit 완료

---

## Step 9. AI 분석 코멘트 자동 생성

> **시간**: 4시간
> **목표**: 18신호 + 모델 결과 + 뉴스 → LLM 이 한국어 400자 종합 분석 코멘트 생성
> **포인트**: Claude Desktop 으로 build_insight.py 코드 받기 + 실행

### 9.1. Claude Desktop 으로 코드 요청

```
나는 Stocksense 앱의 AI 분석 코멘트 자동 생성 코드를 만들 거야.
파일: backend/pipelines/build_insight.py

다음을 해주세요.

## 입력
- backend/data/historical/*.json (18신호 최신값)
- backend/data/forecast/forecast_v2.json (모델 예측)
- backend/data/news/latest.json (최근 뉴스 Top 5, 선택)

## LLM 호출
- 우선순위: Anthropic Claude → Gemini → Groq → 휴리스틱
- API 키는 .env 에서 읽기
- 각 API 한도 초과 시 자동 다음 fallback

## 프롬프트
"당신은 개인 투자자 의사결정용 분석가입니다. 다음 데이터를 종합해서
한국어로 280~360자 분석을 작성하세요. 반드시 마침표로 완결, 중요한
단어 3~5개를 **bold** 마크다운으로 강조."

## 출력
backend/data/insight/latest.json:
{
  "generatedAt": "2026-05-26T00:00:00",
  "model": "Gemini gemini-2.5-flash",
  "headline": "AI 수요 견인, 단기 강세 전망",
  "summary": "현재 5개 종목 평균가 $... 상승... ",
  "tone": "pos|neu|neg",
  "confidence": 75,
  "horizon": "short|mid|long",
  "keySignals": ["A-1", "B-3"]
}

전체 코드를 ```python 블록으로 줘. 약 300~400줄 예상.
```

Claude 답변 → `code backend/pipelines/build_insight.py` 로 저장.

### 9.2. .env 에 LLM API 키 추가

LLM 키 발급 (Claude Desktop 에 "Anthropic / Gemini / Groq 키 발급 방법" 물어보기):

```bash
# .env 에 추가
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx  # https://console.anthropic.com (Pro 결제 시 $5 충전)
GEMINI_API_KEY=AIzaxxxxxxxx        # https://aistudio.google.com (무료 1500/day)
GROQ_API_KEY=gsk_xxxxxxxx          # https://console.groq.com (무료 14400/day)
```

**비전문가 추천**: Gemini + Groq 무료만 사용. 충분.

### 9.3. 실행

```bash
cd ~/Documents/my-stocksense/backend
source .venv/bin/activate
python3 pipelines/build_insight.py
```

**예상 출력**:
```
[1/3] 컨텍스트 빌드 (18신호 + forecast + 뉴스)
  → 프롬프트 1500자
[2/3] LLM 호출 (Gemini 2.5 Flash)
  ✅ 응답 320자
[3/3] 저장
  ✅ backend/data/insight/latest.json
     headline: AI 수요 견인, 단기 강세 전망
     summary (320자): 현재 5개 종목 평균가 **$185.40**로 ...
```

### 9.4. 결과 확인

```bash
cat backend/data/insight/latest.json | python3 -m json.tool
```

**검증**:
- summary 가 한국어 마침표로 완결
- `**word**` 마크다운으로 3개 이상 강조
- headline 22자 이내

### 9.5. (선택) 뉴스 수집 코드도 요청

```
collect_news_events.py 도 만들어줘.
- Google News RSS 로 5개 종목 뉴스 수집 (Apple/Tesla/Samsung/NVIDIA/SK하이닉스)
- LLM 로 한국어 분류 (긍정/중립/부정)
- Top 10 저장: backend/data/news/latest.json
- 영문 헤드라인 → 한국어 키워드 매핑 (Apple → 애플, Tesla → 테슬라 등)
- 같은 LLM fallback 사용

약 500~800줄 예상.
```

→ `code backend/pipelines/collect_news_events.py` → 실행 → 10건 한국어 뉴스 확보.

### Step 9 검증 ✅
- [ ] `backend/data/insight/latest.json` 생성
- [ ] summary 한국어 + 마침표 완결 + bold 3개 이상
- [ ] (선택) `news/latest.json` 10건 한국어

---

## Step 10. Vercel 무료 배포

> **시간**: 30분
> **목표**: HTTPS URL 발급 (예: `https://my-stocksense.vercel.app`)

### 10.1. data.js 자동 생성 스크립트 요청

Claude Desktop:
```
나는 backend/data/*.json 의 모든 데이터를 frontend/src/mocks/data.js 의
SIXSENSE_DATA 스키마로 자동 변환하는 build_frontend_data.py 가 필요해.

스키마 (참고):
{
  meta: {current, pred7, pred21, insight: {headline, summary, ...}},
  history: [...52주],
  forecast7: [...7주],
  forecast21: [...14주],
  signalsA: [...정형 7],
  signalsB: [...비정형 5],
  macro: [...5],
  news: [...10],
}

코드 작성해줘. 약 400줄 예상.
```

→ `code backend/pipelines/build_frontend_data.py` → 실행:
```bash
python3 pipelines/build_frontend_data.py
# → frontend/src/mocks/data.js 자동 갱신
```

브라우저에서 http://localhost:5173 새로고침 → mock 데이터가 실데이터로 교체된 것 확인.

### 10.2. GitHub repo 생성

웹:
1. https://github.com/new
2. Repository name: `my-stocksense`
3. Public 선택
4. "Create repository"

### 10.3. Claude Desktop 으로 GitHub push 안내 받기

```
나는 https://github.com/<내아이디>/my-stocksense 라는 빈 repo 만들었어.
~/Documents/my-stocksense 의 코드를 push 하는 명령어 알려줘.

GitHub CLI (gh) 인증 + git remote add origin + push 까지 한 번에.
```

Claude 답:
```bash
# 1. GitHub CLI 인증 (브라우저로 8자리 코드 입력)
gh auth login --web

# 2. remote 연결
cd ~/Documents/my-stocksense
git remote add origin https://github.com/<your-username>/my-stocksense.git

# 3. push
git push -u origin main
```

### 10.4. Vercel 배포 안내 받기

```
나는 ~/Documents/my-stocksense 를 Vercel 에 배포하고 싶어.
구조는 monorepo (frontend/ 가 React, backend/ 는 Python).

frontend 만 Vercel 에 배포하고 싶어. 다음을 알려줘:
1. vercel.json 어떻게 작성?
2. .vercelignore 어떻게? (backend 제외)
3. npx vercel --prod 명령어
```

Claude 답:

**vercel.json**:
```json
{
  "version": 2,
  "framework": "vite",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install"
}
```

**.vercelignore**:
```
backend/
design_handoff/
docs/
.env
```

**배포 명령**:
```bash
cd ~/Documents/my-stocksense

# vercel.json 작성
cat > vercel.json << 'EOF'
{
  "version": 2,
  "framework": "vite",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install"
}
EOF

# .vercelignore 작성
cat > .vercelignore << 'EOF'
backend/
design_handoff/
docs/
.env
EOF

# Vercel CLI 로그인 (브라우저 자동 열림)
npx vercel login

# 첫 배포 (소문자 이름 필수)
npx vercel --prod --yes --name my-stocksense
```

### 10.5. 배포 결과 확인

약 1~2분 후:
```
🔍 Inspect: https://vercel.com/<scope>/my-stocksense/<id>
✅ Production: https://my-stocksense-xxxxx.vercel.app
▲ Aliased: https://my-stocksense-eta.vercel.app
```

브라우저에서 URL 열기:
- HTTPS 자동
- 14화면 모두 작동
- 다크/라이트 토글
- 모바일에서도 (폰으로 URL 열어보기)

### 10.6. GitHub ↔ Vercel 자동 재배포 확인

이제 `git push origin main` 하면 Vercel 이 자동 재빌드:

```bash
echo "" >> README.md   # 작은 변경
git add README.md
git commit -m "test: auto rebuild"
git push
```

Vercel Dashboard (https://vercel.com/dashboard) → "Deployments" 탭에 새 배포 자동 시작.

### Step 10 검증 ✅
- [ ] GitHub repo 에 코드 push 완료
- [ ] Vercel HTTPS URL 발급
- [ ] URL HTTP 200 + 14화면 작동
- [ ] git push → Vercel 자동 재배포 확인

### 막혔을 때
- "Project name must be lowercase" → `--name` 소문자로
- "GitHub 인증 실패" → `gh auth login --web` 다시
- "Vercel build 실패" → 로그 캡처 → Claude 에게 붙여넣기

---

## Step 11. 친구·동료에게 공유

> **시간**: 10분
> **목표**: URL 공유 + 피드백 받기

### 11.1. 카톡/Slack 공유 메시지

```
🎯 내가 만든 AI 주식 분석 앱: https://my-stocksense-eta.vercel.app

✅ 작동:
- 내 관심 종목 5개 (Apple/Tesla/Samsung/NVIDIA/SK하이닉스) 6개월 예측
- AI 가 매일 한국어 분석 코멘트
- 다크/라이트 모드, 모바일도 OK

피드백은 카톡으로 화면 캡처 + 의견 부탁! 🙏
```

OG meta 덕분에 자동으로 미리보기 카드 표시 (Step 6 에서 index.html title/og 설정).

### 11.2. 피드백 받는 법

옵션:
- 카톡 단톡방 (가장 쉬움)
- GitHub Issues (https://github.com/<your>/my-stocksense/issues)
- Google Form (구글 설문지)

### 11.3. 매주 데이터 갱신

매주 일요일 (또는 원하는 주기) 다음 명령:

```bash
cd ~/Documents/my-stocksense/backend
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
# → 1~2분 후 Vercel 자동 재배포
```

복잡하면 Claude Desktop 에 "이 5단계 한 번에 실행하는 shell 스크립트 만들어줘" 요청.

### Step 11 검증 ✅
- [ ] 친구 3명 이상에게 URL 공유
- [ ] 첫 피드백 1개 이상 받음
- [ ] 다음 갱신 일정 정함

---

## 🎉 가이드 완료

축하합니다! 이제 다음을 갖고 있습니다:

- ✅ **공개 URL** (예: https://my-stocksense.vercel.app)
- ✅ **GitHub repo** (코드 공개 또는 비공개)
- ✅ **18신호 자동 수집** + **AI 예측 모델** + **LLM 인사이트**
- ✅ **본인 능력**: Claude Desktop 으로 다른 도메인 앱 응용 가능

---

## 부록 A. Claude Desktop 100% 활용법

### A-1. 막혔을 때 만능 프롬프트

```
[지금 상황 한 줄]
[방금 실행한 명령어]
[에러 메시지 또는 안 되는 부분]

어떻게 해결?
```

예시:
```
나는 비전문가야. 방금 npm run dev 했어.
에러: "Cannot find module './app.jsx'"
어떻게 해결?
```

### A-2. 코드를 더 자세히 받고 싶을 때

```
방금 준 코드를 더 자세히, 한국어 주석 포함해서 다시 줘.
비전문가도 이해할 수 있게 단계별로.
```

### A-3. 코드가 너무 길면

```
이 코드를 3~5개 작은 파일로 분리하고 싶어. 어떻게 나눠?
```

### A-4. 처음부터 다시

```
지금까지 한 작업 다 잊고, [목표] 를 처음부터 다시 가르쳐줘.
나는 비전문가이고 시간은 N 분 있어.
```

### A-5. Claude Desktop 의 한계
- 본인 컴퓨터에서 직접 명령 실행 X (사용자가 해야 함)
- 파일 시스템 접근 X (.zip 첨부로 우회 가능)
- 실시간 데이터 X (학습 시점 데이터까지만)

→ 이런 부분은 Claude Code CLI (claude.ai/install) 가 보완. 단 비전문가는 Desktop 으로 충분.

---

## 부록 B. 자주 발생하는 에러 모음

### B-1. 터미널 관련

| 에러 | 해결 |
|---|---|
| `command not found: brew` | Step 2 의 Homebrew 설치 후 셸 재시작 (터미널 종료 → 다시 열기) |
| `xcode-select error` | `xcode-select --install` |
| `Permission denied` | `sudo` 추가 또는 폴더 권한 확인 |
| `No such file or directory` | `pwd` 로 현재 위치 확인 + `cd` 로 이동 |

### B-2. Node/npm 관련

| 에러 | 해결 |
|---|---|
| `npm: command not found` | `brew install node` 다시 |
| `npm ERR! peer dep missing` | `npm install --legacy-peer-deps` |
| `EACCES permission denied` | `sudo chown -R $(whoami) ~/.npm` |

### B-3. Python/pip 관련

| 에러 | 해결 |
|---|---|
| `pip: command not found` | `python3 -m pip install ...` |
| `externally-managed-environment` | 가상환경 안에서 실행 (`source .venv/bin/activate`) |
| `ModuleNotFoundError` | `.venv` 활성화 + `pip install <module>` |
| `prophet 설치 실패` | `brew install gcc` 후 다시 |

### B-4. Git/GitHub 관련

| 에러 | 해결 |
|---|---|
| `fatal: not a git repository` | `git init` |
| `Updates were rejected` | `git pull --rebase` 후 다시 push |
| `Permission denied (publickey)` | `gh auth login --web` 다시 |
| `.env 가 commit 됨` | `git rm --cached .env` + `.gitignore` 에 추가 |

### B-5. Vercel 관련

| 에러 | 해결 |
|---|---|
| `Project name must be lowercase` | `--name` 옵션 소문자로 |
| `Build failed: npm install` | Node 버전 확인 (`engines` 필드) |
| `404 on assets` | `outputDirectory` 경로 확인 |
| 흰 화면 | 브라우저 콘솔(F12) → 에러 → Claude 에게 |

### B-6. 막혀도 안 풀릴 때

1. **에러 전체** 를 Claude Desktop 에 복사
2. "비전문가야. 처음부터 다시 설명해줘" 추가
3. Claude 가 단계별 해결책 제시

---

## 부록 C. 터미널/git 기본

### C-1. 터미널 명령

| 명령 | 의미 |
|---|---|
| `pwd` | 현재 위치 |
| `ls -la` | 파일 목록 (숨김 포함) |
| `cd 폴더` | 폴더로 이동 |
| `cd ..` | 상위 폴더 |
| `cd ~` | 홈 폴더 |
| `mkdir 이름` | 폴더 생성 |
| `touch 파일명` | 빈 파일 |
| `cat 파일` | 파일 내용 출력 |
| `cp 원본 대상` | 복사 |
| `mv 원본 대상` | 이동/이름 변경 |
| `rm 파일` | 삭제 |
| `Cmd+C` | 명령 중단 |
| `Cmd+K` | 화면 지우기 |

### C-2. git 기본

| 명령 | 의미 |
|---|---|
| `git status` | 상태 확인 |
| `git add 파일` | 추적 추가 |
| `git add .` | 모든 변경 추가 |
| `git commit -m "메시지"` | 저장 (로컬) |
| `git push` | GitHub 에 업로드 |
| `git pull` | GitHub 에서 다운로드 |
| `git log --oneline` | 히스토리 |

### C-3. VS Code 단축키 (Mac)

| 단축키 | 기능 |
|---|---|
| `Cmd+P` | 파일 빠른 열기 |
| `Cmd+Shift+P` | 명령 팔레트 |
| `Cmd+B` | 사이드바 토글 |
| `Cmd+J` | 터미널 토글 |
| `Cmd+/` | 주석 토글 |
| `Cmd+S` | 저장 |

---

## 부록 D. 다른 도메인 응용

본 가이드의 **Stocksense** 패턴을 다음 도메인에 즉시 응용 가능. 신호 종류만 바꾸면 됨.

### D-1. Walletsense (가계부 + AI 지출 분석)

| 변경 사항 |
|---|
| 데이터: Yahoo X → 본인 카드 CSV (수동 업로드) |
| 신호 18 → 12 (식비/교통/문화/...) |
| 모델: 시계열 예측 → 카테고리별 트렌드 분석 |
| LLM: "이번 달 식비 과지출, 다음달 어떻게?" |

### D-2. Realsense (서울 아파트 시세)

| 변경 사항 |
|---|
| 데이터: Yahoo X → KB부동산 시세 + 국토부 실거래가 + 입주물량 |
| 신호: 금리/거래량/인허가/미분양/청약 |
| 모델: 단기 1~3개월, 중장기 6~12개월 |
| LLM: "이 지역, 지금 매수 적절?" |

### D-3. Weatherbiz (날씨 vs 우리 가게 매출)

| 변경 사항 |
|---|
| 데이터: Yahoo X → 기상청 API + 본인 POS CSV |
| 신호: 기온/강수/습도/공휴일 |
| 모델: 회귀 분석 (날씨 → 매출) |
| LLM: "이번 주말 매출 예측 + 재고 추천" |

### D-4. Travelsense (항공권 가격 추적)

| 변경 사항 |
|---|
| 데이터: Yahoo X → Skyscanner RSS + 한국→일본 항공권 |
| 신호: 환율/유가/공휴일/이벤트 |
| 모델: 시계열 + 이벤트 영향 |
| LLM: "이번 출장, 지금 예약 vs 1주 대기?" |

### D-5. Healthsense (체중/운동 + AI 코치)

| 변경 사항 |
|---|
| 데이터: Apple Health Export (수동) |
| 신호: 체중/걸음수/수면/심박 |
| 모델: 추세 분석 + 목표 시점 예측 |
| LLM: "이번 주 운동 더 / 식단 어떻게?" |

**공통**: PRD → Claude Design → React 포팅 → 데이터 수집 → 예측 → LLM → 배포 패턴 동일.

---

## 부록 E. Stocksense 완성본 참고

본 튜토리얼의 패턴을 그대로 적용한 **실제 사례** (DRAM 가격 예측):
- 데모: https://sixsense-eta.vercel.app
- 코드: https://github.com/chaos72/Sixsense
- 풀 가이드 (Sixsense 특화): [README.md](README.md) (3,407줄)
- 실제 작동 코드: [code-snippets/](code-snippets/) (6,345줄)
- 발표 자료: [sixsense-vibe-coding-guide.pptx](sixsense-vibe-coding-guide.pptx) (28 슬라이드)

본 튜토리얼은 위 사례를 **일반 비전문가 + Stocksense 예시** 로 재구성한 것입니다.

---

## ✉️ 문의

| | |
|---|---|
| 작성 | 김영석 (Sr. Solution Engineer, Dataiku Korea) |
| 과정 | KAIST CAIO 10기 6조 |
| Email | youngseok.kim@dataiku.com |
| GitHub | https://github.com/chaos72 |
| Demo | https://sixsense-eta.vercel.app |

---

**🎯 핵심 메시지**: 비전문가도 Claude Desktop 한 도구만으로 7~10일이면 자신만의 AI 데이터 대시보드를 만들 수 있습니다. 막힐 때마다 Claude 에게 "어떻게 해?" 만 물어보세요.
