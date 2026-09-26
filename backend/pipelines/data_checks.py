"""data_checks.py — 수집된 값이 '그 지표가 맞는지' 자동 검사 (v2.6 재발 방지 장치 2)

왜 필요한가: 2026-05 ~ 09 동안 A-4 는 반도체가 없는 엉뚱한 표의 임의 값(약 492만)이 '재고지수'로 저장됐고,
코드가 돌고 날짜 형식이 맞다는 이유로 아무도 걸러내지 못했다. 이 파일은 신호마다
① 정상 범위 ② 출처 문구 필수 단어 ③ 형식(월요일·중복·결측·무한대)을 검사해,
실패한 신호를 화면·AI 요약·예측 검증에서 자동으로 제외하게 한다 (build_frontend_data.invalid_signals).

범위는 '물리적으로 말이 되는 넓은 범위'로 잡는다 — 정상적인 급등락은 통과, 단위·표가 틀린 값은 걸러냄.

사용:
  python pipelines/data_checks.py            # 결과 출력 + backend/data/checks/latest.json 저장 (항상 종료코드 0)
  python pipelines/data_checks.py --strict   # 검사에 걸렸는데 화면·예측에서 제외되지 않은 신호가 있거나
                                             # 화면 데이터에 문제가 있으면 종료코드 1 (verify.sh 관문용)
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HIST = ROOT / "backend/data/historical"
OUT = ROOT / "backend/data/checks/latest.json"
FRONT = ROOT / "frontend/src/mocks/data.js"

_SENT = {"lo": -1.0, "hi": 1.0, "why": "감성 점수는 -1~+1"}

# sid: 정상 범위(lo~hi), 출처(source)에 반드시 들어 있어야 할 단어, 범위 근거
RULES: dict[str, dict] = {
    "target-dram": {"lo": 10, "hi": 5000, "words": ["MU", "SK Hynix", "Samsung"], "why": "2025-06-16=100 주가지수"},
    "A-1": {"lo": 10, "hi": 2000, "words": ["TSM", "UMC"], "why": "2025-06-16=100 주가지수"},
    "A-2": {"lo": 1e3, "hi": 1e7, "words": ["SEC"], "why": "빅테크 분기 CapEx(백만 달러)"},
    "A-3": {"lo": 1e8, "hi": 1e11, "words": ["관세청", "854232"], "why": "메모리 월간 수출액(달러) — 2025~26 실측 23억~157억"},
    "A-4": {"lo": 30, "hi": 300, "words": ["반도체", "재고지수"], "why": "2020=100 지수 — 실측 80~122 (492만 같은 값 차단)"},
    "A-5": {"lo": 0.005, "hi": 5, "words": ["spot"], "why": "EC2 스팟 시간당 달러"},
    "A-6": {"lo": 0.0, "hi": 1.0, "words": ["Manifold"], "why": "예측시장 확률"},
    "A-7": {"lo": 0.5, "hi": 20, "words": ["HG=F"], "why": "구리 선물 달러/파운드"},
    "B-1": {**_SENT, "words": ["Google News"]},
    "B-2": {**_SENT, "words": ["RSS"]},
    "B-3": {"lo": 0, "hi": 10000, "words": ["Hacker News"], "why": "주간 게시글 수"},
    "B-4": {"lo": 0, "hi": 2000, "words": ["GPR"], "why": "지정학 리스크 지수(1985~2019 평균=100)"},
    "B-5": {**_SENT, "words": ["Google News"]},
    "B-6": {**_SENT, "words": ["Google News"]},
    "B-7": {"lo": 0, "hi": 1e6, "words": ["Hacker News"], "why": "주간 점수 합"},
    "macro-cu": {"lo": 0.5, "hi": 20, "words": ["HG=F"], "why": "구리 선물 달러/파운드"},
    "macro-dxy": {"lo": 60, "hi": 160, "words": ["DX-Y"], "why": "달러 인덱스"},
    "macro-krw": {"lo": 700, "hi": 2500, "words": ["KRW"], "why": "원/달러 환율"},
    "macro-fed": {"lo": 0, "hi": 20, "words": ["DFF"], "why": "미국 기준금리 %"},
    "macro-ust10": {"lo": 0, "hi": 20, "words": ["DGS10"], "why": "미국 10년물 금리 %"},
    "macro-pmi": {"lo": 30, "hi": 300, "words": ["INDPRO"], "why": "산업생산지수(2017=100)"},
}


def check_payload(sid: str, payload: dict) -> list[str]:
    """한 신호 파일 내용 검사 → 문제 목록 (빈 목록 = 통과)."""
    rule = RULES.get(sid)
    if rule is None:
        return ["검사 규칙이 없는 신호 — data_checks.RULES 에 추가 필요"]
    rows = payload.get("data") or []
    if not rows:
        return ["데이터 없음"]
    problems = []
    weeks = [r.get("week") for r in rows]
    if len(weeks) != len(set(weeks)):
        problems.append("같은 주가 두 번 이상")
    if weeks != sorted(weeks):
        problems.append("주 순서가 뒤섞임")
    bad_day = [w for w in weeks if date.fromisoformat(w).weekday() != 0]
    if bad_day:
        problems.append(f"월요일이 아닌 주 {len(bad_day)}개 (예: {bad_day[0]})")
    vals = [r.get("value") for r in rows]
    non_num = [v for v in vals if not isinstance(v, (int, float)) or isinstance(v, bool)
               or not math.isfinite(float(v))]
    if non_num:
        problems.append(f"숫자가 아닌 값·무한대·결측 {len(non_num)}개")
    nums = [float(v) for v in vals if v not in non_num]
    out = [v for v in nums if not (rule["lo"] <= v <= rule["hi"])]
    if out:
        problems.append(f"정상 범위 {rule['lo']:g}~{rule['hi']:g} 밖의 값 {len(out)}개 "
                        f"(예: {out[0]:g}) — {rule['why']}")
    src = payload.get("source") or ""
    missing = [w for w in rule["words"] if w not in src]
    if missing:
        problems.append(f"출처 설명에 {missing} 없음 — 다른 표·다른 지표일 수 있음")
    return problems


def check_all() -> dict[str, list[str]]:
    """모든 신호 파일 검사 → {sid: 문제 목록} (문제 있는 신호만)."""
    result = {}
    for p in sorted(HIST.glob("*.json")):
        sid = p.stem
        if sid.startswith("_"):
            continue
        probs = check_payload(sid, json.loads(p.read_text()))
        if probs:
            result[sid] = probs
    for sid in RULES:                       # 규칙은 있는데 파일이 없는 신호
        if not (HIST / f"{sid}.json").exists():
            result[sid] = ["신호 파일 없음"]
    return result


def check_frontend_data(path: Path = FRONT) -> list[str]:
    """화면 데이터(data.js) 정적 검사 — 브라우저 없이 잡을 수 있는 것."""
    src = path.read_text()
    body = src[src.index("= {") + 2: len(src.rstrip().rstrip(";").rstrip())]
    problems = []
    for bad in ("NaN", "Infinity", "undefined"):
        if re.search(rf"(?<![A-Za-z]){bad}(?![A-Za-z])", body):
            problems.append(f"화면 데이터에 {bad} 포함")
    d = json.loads(body)
    v = d.get("validation")
    hist = d.get("history") or []
    if v and hist:
        cur = (v.get("current") or {}).get("week")
        if cur != hist[-1].get("date"):
            problems.append(f"예측 기준 주({cur}) ≠ 차트 최신 주({hist[-1].get('date')}) — 화면은 예측을 숨김(경고)")
        for x in v.get("variants", []):
            if x.get("forecast") and "pass" not in x:
                problems.append(f"{x.get('key')} 예측에 합격/불합격 표시 정보 없음")
    # v2.6: 뉴스·이벤트가 0건이면 화면이 비어 보인다 (번호 해석 실패로 뉴스 10건이 조용히 0건이 된 사고)
    for key, label in (("news", "뉴스"), ("events", "이벤트")):
        if not d.get(key):
            problems.append(f"화면 데이터에 {label} 0건")
    for grp in ("groupA", "groupB"):
        for r in (d.get("collection") or {}).get(grp, []):
            if r.get("status") not in ("ok", "stale", "fail", "invalid"):
                problems.append(f"수집 상태 값 이상: {r.get('id')}={r.get('status')}")
    return problems


def main() -> int:
    strict = "--strict" in sys.argv
    res = check_all()
    fe = check_frontend_data() if FRONT.exists() else ["화면 데이터 파일 없음"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"signals": res, "frontend": fe}, ensure_ascii=False, indent=2))
    # 검사에 걸린 신호가 화면에서 '제외'로 처리됐는지 — 걸렸는데도 정상 표시되면 관문 실패
    unhandled = []
    if FRONT.exists():
        body = FRONT.read_text()
        d = json.loads(body[body.index("= {") + 2: len(body.rstrip().rstrip(";").rstrip())])
        status = {r["id"]: r["status"] for g in ("groupA", "groupB") for r in (d.get("collection") or {}).get(g, [])}
        shown = {x["id"] for x in (d.get("signalsA") or []) + (d.get("signalsB") or [])}
        for sid in res:
            if sid in shown or (sid in status and status[sid] != "invalid") or not sid[:1] in "AB":
                unhandled.append(sid)
    print(f"[데이터 의미 검사] 신호 {len(RULES)}개 중 문제 {len(res)}개 (자동 제외됨 {len(res) - len(unhandled)}개, "
          f"제외 안 됨 {len(unhandled)}개) · 화면 데이터 문제 {len(fe)}개")
    for sid, probs in res.items():
        for pr in probs:
            print(f"  {'❌' if sid in unhandled else '⛔ 자동 제외'} {sid}: {pr}")
    for pr in fe:
        print(f"  ❌ 화면 데이터: {pr}")
    return 1 if strict and (unhandled or fe) else 0


if __name__ == "__main__":
    sys.exit(main())
