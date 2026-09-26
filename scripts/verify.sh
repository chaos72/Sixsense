#!/usr/bin/env bash
# verify.sh — 커밋·완료 보고 전 필수 검증 (v2.6 재발 방지 장치 3)
#
# 한 단계라도 실패하면 종료코드 1. Claude 는 git commit 전에 이 스크립트가 자동 실행되며(.claude/settings.json 훅),
# 실패하면 커밋이 막힌다. 사람이 직접 돌려도 된다:  bash scripts/verify.sh
#
#  1. 정적 검사 (pyflakes)         — 없는 이름·안 쓰는 코드
#  2. 자동 시험 (pytest)           — 과거 사고별 재발 방지 시험
#  3. 돌연변이 시험                — 과거 버그를 되살렸을 때 시험이 모두 잡는지 (시험의 시험)
#  4. 데이터 의미 검사 (--strict)  — 값이 그 지표가 맞는지, 걸린 신호가 제외 처리됐는지, 화면 데이터 이상
#  5. 화면 타입 검사 + 빌드
#  6. 화면 40개 자동 검사 (headless 브라우저 — 금지 표현·오류·NaN·모바일 넘침·불합격 표시)
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/backend/.venv/bin/python"
[ -x "$PY" ] || PY="python"            # GitHub Actions 등 가상환경이 없는 곳
FAIL=0
step() { echo; echo "── $1 ──"; }
run() { if "$@"; then echo "  ✅ 통과"; else echo "  ❌ 실패"; FAIL=1; fi; }

cd "$ROOT/backend"
step "1/6 정적 검사";          run "$PY" -m pyflakes pipelines tests
step "2/6 자동 시험";          run "$PY" -m pytest tests -q -p no:cacheprovider
step "3/6 돌연변이 시험";      run "$PY" tests/mutation_check.py
step "4/6 데이터 의미 검사";   run "$PY" pipelines/data_checks.py --strict
if [ "${VERIFY_SKIP_FRONTEND:-0}" != "1" ]; then
  cd "$ROOT/frontend"
  step "5/6 화면 타입 검사·빌드"
  OUT="$(mktemp -d)"
  run bash -c "npx tsc -b && npx vite build --outDir '$OUT' --emptyOutDir --logLevel error"
  rm -rf "$OUT"
  step "6/6 화면 40개 자동 검사"
  run node scripts/screen-check-run.mjs
fi

echo
if [ "$FAIL" = 0 ]; then echo "✅ verify.sh 전체 통과"; else echo "❌ verify.sh 실패 — 위의 ❌ 단계를 고치기 전에는 커밋·완료 보고 금지"; fi
exit $FAIL
