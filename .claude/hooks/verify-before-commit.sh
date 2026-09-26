#!/usr/bin/env bash
# Claude 커밋 관문 (v2.6 재발 방지 장치 3) — .claude/settings.json 의 PreToolUse(Bash) 훅.
# Claude 가 실행하려는 Bash 명령에 'git commit' 이 들어 있으면 scripts/verify.sh 를 먼저 돌리고,
# 실패하면 종료코드 2 로 명령을 막는다(= 검증 없이 커밋 불가). 그 밖의 명령은 바로 통과.
cmd="$(jq -r '.tool_input.command // ""')"
case "$cmd" in
  *"git commit"*) ;;
  *) exit 0 ;;
esac
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if out="$(bash "$ROOT/scripts/verify.sh" 2>&1)"; then
  exit 0
fi
{
  echo "⛔ 커밋 차단: scripts/verify.sh 가 실패했습니다. 실패한 단계를 고친 뒤 다시 커밋하세요."
  echo "$out" | grep -E "❌|──" | tail -20
} >&2
exit 2
