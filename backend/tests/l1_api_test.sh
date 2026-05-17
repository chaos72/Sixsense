#!/usr/bin/env bash
# L1 API Tests — Sixsense backend
# Design Ref: Design §8.2 L1 API Test Scenarios
# Usage: bash l1_api_test.sh
set -u

BASE="${BASE:-http://localhost:8000}"
PASS=0
FAIL=0
FAILED_NAMES=()

assert_status() {
  local name="$1"
  local expected="$2"
  local actual="$3"
  if [ "$expected" = "$actual" ]; then
    printf "  ✅ %-50s [HTTP %s]\n" "$name" "$actual"
    PASS=$((PASS+1))
  else
    printf "  ❌ %-50s [expected %s, got %s]\n" "$name" "$expected" "$actual"
    FAIL=$((FAIL+1))
    FAILED_NAMES+=("$name")
  fi
}

assert_contains() {
  local name="$1"
  local needle="$2"
  local haystack="$3"
  if echo "$haystack" | grep -q "$needle"; then
    printf "  ✅ %-50s [contains '%s']\n" "$name" "$needle"
    PASS=$((PASS+1))
  else
    printf "  ❌ %-50s [missing '%s']\n" "$name" "$needle"
    FAIL=$((FAIL+1))
    FAILED_NAMES+=("$name")
  fi
}

curl_status() { curl -s -o /dev/null -w "%{http_code}" "$@"; }
curl_body()   { curl -s "$@"; }

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  L1 API Tests — Sixsense backend ($BASE)"
echo "═══════════════════════════════════════════════════════════════════"

# ── Health ─────────────────────────────────────────────────────────
echo ""
echo "[Health]"
assert_status "GET /api/health"                200 "$(curl_status $BASE/api/health)"
assert_contains "  └─ body has 'ok'" '"ok"' "$(curl_body $BASE/api/health)"

# ── 1~14 GET endpoints ────────────────────────────────────────────
echo ""
echo "[Core GET endpoints]"
assert_status "GET /api/snapshot"              200 "$(curl_status $BASE/api/snapshot)"
assert_contains "  └─ currentPrice present" '"currentPrice"' "$(curl_body $BASE/api/snapshot)"
assert_contains "  └─ forecast7 present" '"forecast7"' "$(curl_body $BASE/api/snapshot)"
assert_contains "  └─ forecast21 present" '"forecast21"' "$(curl_body $BASE/api/snapshot)"

assert_status "GET /api/history"               200 "$(curl_status $BASE/api/history)"
assert_contains "  └─ history array" '"history"' "$(curl_body $BASE/api/history)"

assert_status "GET /api/signals"               200 "$(curl_status $BASE/api/signals)"
assert_contains "  └─ groupA present" '"groupA"' "$(curl_body $BASE/api/signals)"
assert_contains "  └─ groupB present" '"groupB"' "$(curl_body $BASE/api/signals)"

assert_status "GET /api/signals/A-1"           200 "$(curl_status $BASE/api/signals/A-1)"
assert_status "GET /api/signals/B-3"           200 "$(curl_status $BASE/api/signals/B-3)"
assert_status "GET /api/signals/A-99 (404)"    404 "$(curl_status $BASE/api/signals/A-99)"

assert_status "GET /api/news"                  200 "$(curl_status $BASE/api/news)"
assert_contains "  └─ items array" '"items"' "$(curl_body $BASE/api/news)"
assert_status "GET /api/news?sentiment=pos"    200 "$(curl_status "$BASE/api/news?sentiment=pos")"

assert_status "GET /api/news/0"                200 "$(curl_status $BASE/api/news/0)"
assert_status "GET /api/news/9999 (404)"       404 "$(curl_status $BASE/api/news/9999)"

assert_status "GET /api/macro"                 200 "$(curl_status $BASE/api/macro)"
assert_status "GET /api/events"                200 "$(curl_status $BASE/api/events)"
assert_status "GET /api/events?risk=high"      200 "$(curl_status "$BASE/api/events?risk=high")"

assert_status "GET /api/events/0"              200 "$(curl_status $BASE/api/events/0)"
assert_status "GET /api/events/9999 (404)"     404 "$(curl_status $BASE/api/events/9999)"

assert_status "GET /api/forecast/7"            200 "$(curl_status $BASE/api/forecast/7)"
assert_status "GET /api/forecast/21"           200 "$(curl_status $BASE/api/forecast/21)"
assert_status "GET /api/forecast/14 (400)"     400 "$(curl_status $BASE/api/forecast/14)"
assert_contains "  └─ VALIDATION_FAILED" 'VALIDATION_FAILED' "$(curl_body $BASE/api/forecast/14)"

assert_status "GET /api/accuracy"              200 "$(curl_status $BASE/api/accuracy)"
assert_status "GET /api/accuracy?horizon=7"    200 "$(curl_status "$BASE/api/accuracy?horizon=7")"
assert_status "GET /api/accuracy/0"            200 "$(curl_status $BASE/api/accuracy/0)"

assert_status "GET /api/collection"            200 "$(curl_status $BASE/api/collection)"

# ── 15. POST /api/hitl/rules ──────────────────────────────────────
echo ""
echo "[HITL POST + polling]"
HITL_BODY='{"signalId":"A-4","rules":[{"id":"alert","value":95}],"comment":"test"}'
HITL_RES=$(curl -s -X POST $BASE/api/hitl/rules -H "Content-Type: application/json" -d "$HITL_BODY")
assert_status "POST /api/hitl/rules"           202 "$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/api/hitl/rules -H "Content-Type: application/json" -d "$HITL_BODY")"
assert_contains "  └─ processing status" '"processing"' "$HITL_RES"
assert_contains "  └─ queueId returned" '"queueId"' "$HITL_RES"

QUEUE_ID=$(echo "$HITL_RES" | sed -n 's/.*"queueId":"\([^"]*\)".*/\1/p')
echo "  ℹ️  queueId = $QUEUE_ID"

assert_status "GET /api/hitl/jobs/$QUEUE_ID"   200 "$(curl_status $BASE/api/hitl/jobs/$QUEUE_ID)"
sleep 1.5
JOB_RES=$(curl_body $BASE/api/hitl/jobs/$QUEUE_ID)
assert_contains "  └─ status=done after poll" '"done"' "$JOB_RES"
assert_contains "  └─ beforeResult present" '"beforeResult"' "$JOB_RES"
assert_contains "  └─ afterResult present" '"afterResult"' "$JOB_RES"

# ── Validation errors ─────────────────────────────────────────────
echo ""
echo "[Validation errors]"
EMPTY_RULES='{"signalId":"A-4","rules":[]}'
assert_status "POST /api/hitl/rules (empty rules)" 400 "$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/api/hitl/rules -H "Content-Type: application/json" -d "$EMPTY_RULES")"

MALFORMED='{"signalId":123}'
assert_status "POST /api/hitl/rules (malformed)"   422 "$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/api/hitl/rules -H "Content-Type: application/json" -d "$MALFORMED")"

# ── Summary ───────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Summary: ${PASS} passed, ${FAIL} failed (total $((PASS+FAIL)))"
echo "═══════════════════════════════════════════════════════════════════"
if [ $FAIL -gt 0 ]; then
  echo ""
  echo "Failed tests:"
  printf "  - %s\n" "${FAILED_NAMES[@]}"
  exit 1
fi
exit 0
