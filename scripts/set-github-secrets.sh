#!/usr/bin/env bash
# GitHub Actions Secrets 일괄 등록 헬퍼 (김영석님이 직접 실행)
#
# 사용법:  bash "/Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/scripts/set-github-secrets.sh"
#
# 동작: 프로젝트 루트 .env 에서 아래 10개 키의 값을 읽어
#       GitHub 저장소(chaos72/Sixsense)의 암호화 Secrets 로 등록한다.
#       키 '값'은 화면에 절대 출력하지 않는다(이름과 성공여부만 표시).
set -euo pipefail

REPO="chaos72/Sixsense"
ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/.env"

KEYS=(
  ANTHROPIC_API_KEY
  GEMINI_API_KEY
  GROQ_API_KEY
  KCS_API_URL
  KCS_API_KEY
  KOSIS_API_KEY
  KOSIS_FULL_URL
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_REGION
)

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ .env 파일을 찾을 수 없습니다: $ENV_FILE"; exit 1
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "❌ gh(GitHub CLI)가 설치되어 있지 않습니다."; exit 1
fi

echo "저장소: $REPO 에 Secrets 등록 시작 (값은 표시하지 않음)"
echo "────────────────────────────────────────────"

ok=0; fail=0
for KEY in "${KEYS[@]}"; do
  # .env 에서 'KEY=' 로 시작하는 첫 줄 → 첫 '=' 이후 전체를 값으로 (URL 의 = & 안전)
  line="$(grep -m1 "^${KEY}=" "$ENV_FILE" || true)"
  if [[ -z "$line" ]]; then
    echo "  ⏭  $KEY — .env 에 없음, 건너뜀"; ((fail++)); continue
  fi
  val="${line#*=}"
  # 앞뒤 따옴표 제거
  val="${val%\"}"; val="${val#\"}"
  val="${val%\'}"; val="${val#\'}"
  if [[ -z "$val" ]]; then
    echo "  ⏭  $KEY — 값이 비어 있음, 건너뜀"; ((fail++)); continue
  fi
  # 값은 표준입력(stdin)으로 전달한다.
  # 주의: `--body -` 는 stdin 이 아니라 리터럴 문자열 "-" 로 처리되므로 절대 쓰지 말 것!
  if printf '%s' "$val" | gh secret set "$KEY" --repo "$REPO" >/dev/null 2>&1; then
    echo "  ✅ $KEY 등록 완료 (${#val}자)"; ((ok++))
  else
    echo "  ❌ $KEY 등록 실패 (권한/네트워크 확인)"; ((fail++))
  fi
done

echo "────────────────────────────────────────────"
echo "완료: 성공 $ok개 / 실패·건너뜀 $fail개"
echo "이제 클로드에게 '다시 등록했어'라고 알려주세요 → 공용 주방 재검증을 진행합니다."
