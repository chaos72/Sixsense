# 아이폰 버튼 연결 — GitHub 토큰을 Vercel에 등록

아이폰 '수동 갱신' 버튼이 공용 주방(GitHub Actions)을 **원격에서 켜려면**, Vercel의 작은
함수가 GitHub에 "시작" 신호를 보낼 **출입증(토큰)** 이 하나 필요합니다.
이 토큰은 Vercel 서버에만 저장되고 아이폰/브라우저에는 절대 노출되지 않습니다.

## 1단계 — GitHub 토큰(출입증) 만들기

1. 브라우저에서: <https://github.com/settings/personal-access-tokens/new>
   (GitHub → 우측 상단 프로필 → Settings → Developer settings → Personal access tokens →
   **Fine-grained tokens** → **Generate new token**)
2. 아래처럼 설정:
   - **Token name**: `sixsense-refresh` (아무 이름)
   - **Expiration**: 원하는 기간 (예: 90 days 또는 No expiration)
   - **Repository access**: **Only select repositories** → `chaos72/Sixsense` 선택
   - **Permissions** → **Repository permissions** → **Actions** 항목을 **Read and write** 로 설정
     (이 권한이 있어야 워크플로를 원격에서 켤 수 있습니다. 나머지는 건드리지 않아도 됨)
3. 맨 아래 **Generate token** 클릭 → 나오는 토큰 문자열(`github_pat_...`)을 **복사**
   (이 화면을 벗어나면 다시 못 보니 지금 복사)

## 2단계 — Vercel에 토큰 등록

1. <https://vercel.com> 로그인 → **Sixsense** 프로젝트 클릭
2. 상단 **Settings** → 왼쪽 **Environment Variables**
3. 새 변수 추가:
   - **Key(이름)**: `GH_DISPATCH_TOKEN`
   - **Value(값)**: 방금 복사한 토큰(`github_pat_...`) 붙여넣기
   - **Environments**: Production (그리고 Preview도 체크해두면 안전)
4. **Save** 클릭

## 3단계 — 재배포 (토큰 적용)

환경변수는 **새 배포부터 적용**되므로 한 번 재배포가 필요합니다. 두 가지 방법 중 하나:

- **간단**: 저에게 "토큰 등록했어"라고 알려주시면, 제가 재배포를 트리거하고
  아이폰에서 버튼이 실제로 작동하는지 확인해 드립니다.
- **직접**: Vercel 프로젝트 → **Deployments** → 맨 위 배포의 **⋯** → **Redeploy**.

## 완료 후

아이폰 앱에서 '수동 갱신 실행'을 누르면:
1. 공용 주방이 시작되고 "약 5분 소요" 안내가 뜹니다
2. 진행 상태가 표시되고, 완료되면 **자동으로 새로고침**되어 새 데이터가 반영됩니다

> 참고(보안): 이 버튼 주소는 공개되어 있어 이론상 누구나 누를 수 있지만, 동시에 두 번은
> 실행되지 않도록 막혀 있고, GitHub Actions는 공개 저장소라 무료라서 위험/비용은 사실상 없습니다.
> 원하시면 나중에 간단한 암호 보호를 추가할 수 있습니다.
