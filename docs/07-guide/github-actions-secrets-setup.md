# 공용 주방(GitHub Actions) 열쇠(Secrets) 등록 안내

수동 갱신 버튼을 아이폰에서 무료로 작동시키기 위해, 데이터 파이프라인이 쓰는 API 키를
GitHub의 **Secrets(암호화 금고)** 에 딱 한 번 등록해야 합니다. 여기 넣은 값은 공개 저장소라도
**절대 외부에 노출되지 않습니다**(GitHub이 암호화해서 보관, 로그에도 `***`로 가려짐).

## 1단계 — 열쇠 등록 화면 열기

1. 브라우저에서 저장소로 이동: <https://github.com/chaos72/Sixsense>
2. 상단 메뉴 **Settings**(설정) 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. 초록색 **New repository secret** 버튼 클릭

## 2단계 — 아래 10개를 하나씩 등록

각 항목마다: **Name**(이름) 칸에 아래 "열쇠 이름"을 그대로 입력하고,
**Secret**(값) 칸에는 김영석님 컴퓨터의 `.env` 파일에서 **같은 이름 뒤 `=` 다음 값**을 복사해 붙여넣습니다.
그리고 **Add secret** 클릭 → 다시 **New repository secret** → 반복.

> `.env` 파일 위치: 프로젝트 폴더 최상위 `Sixsense/.env`
> (예: `.env`에 `GROQ_API_KEY=gsk_abcd...` 라고 있으면, 이름칸엔 `GROQ_API_KEY`, 값칸엔 `gsk_abcd...`)

| # | 열쇠 이름 (Name) | 용도 | `.env`에서 복사할 값 |
|---|---|---|---|
| 1 | `ANTHROPIC_API_KEY` | LLM 인사이트 | `.env` 동일 이름 값 |
| 2 | `GEMINI_API_KEY` | LLM 대체 | `.env` 동일 이름 값 |
| 3 | `GROQ_API_KEY` | LLM 대체·뉴스 번역 | `.env` 동일 이름 값 |
| 4 | `KCS_API_URL` | A-3 관세청 수출 | `.env` 동일 이름 값 |
| 5 | `KCS_API_KEY` | A-3 관세청 수출 | `.env` 동일 이름 값 |
| 6 | `KOSIS_API_KEY` | A-4 재고/출하 지수 | `.env` 동일 이름 값 |
| 7 | `KOSIS_FULL_URL` | A-4 재고/출하 지수 | `.env` 동일 이름 값 |
| 8 | `AWS_ACCESS_KEY_ID` | **A-5 AWS Spot(최중요)** | `.env` 동일 이름 값 |
| 9 | `AWS_SECRET_ACCESS_KEY` | **A-5 AWS Spot(최중요)** | `.env` 동일 이름 값 |
| 10 | `AWS_REGION` | A-5 AWS Spot | `.env` 동일 이름 값 (예: `us-east-1`) |

> 참고: B-2(대만 뉴스 감성)는 구글클라우드 인증이 복잡하고 화면에서 이미 제거된 신호라
> 공용 주방에서는 건너뜁니다(기존 값 유지). 나머지 신호는 정상 갱신됩니다.

## 3단계 — 워크플로 수동 실행(테스트)

1. 저장소 상단 **Actions** 탭 클릭
2. 왼쪽에서 **Sixsense 데이터 갱신** 클릭
3. 오른쪽 **Run workflow** 버튼 → 다시 **Run workflow**(초록 버튼) 클릭
4. 몇 초 뒤 실행이 시작됩니다. 클릭해 들어가면 5단계 진행 로그가 보입니다.
5. **약 5~8분** 후 초록 체크(✅)가 뜨면 성공 — `sixsense-bot`이 새 데이터를 커밋하고,
   Vercel이 자동으로 아이폰 앱에 반영합니다.

## 문제가 생기면

- 빨간 X(실패)가 뜨면, 실패한 단계를 클릭해 로그를 보고 저(클로드)에게 알려주세요.
  대개는 열쇠 이름 오타나 값 누락입니다.
- 열쇠 값을 수정하려면: Settings → Secrets → 해당 항목 → **Update**.

---

이 3단계(테스트 성공)까지 끝나면, 다음으로 **아이폰 앱의 버튼을 이 공용 주방에 연결**(2단계 작업)합니다.
