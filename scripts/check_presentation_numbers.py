"""발표자료의 '현재 수치'가 실제 데이터와 같은지 대조 (v3.0, CLAUDE.md 6절)

실제 값(검증 결과 파일·화면 데이터·시험 결과·git)에서 기대 문자열을 만들고, 그 문자열이 발표자료에 들어 있는지 확인한다.
발표에 적힌 숫자를 옮겨 적어 비교하지 않는다 — 발표가 바뀌면 옮겨 적은 값도 같이 틀릴 수 있기 때문.
사용:  backend/.venv/bin/python scripts/check_presentation_numbers.py     → 불일치 0이면 종료코드 0
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = (ROOT / "docs/06-presentation/sixsense.presentation.md").read_text()
PY = str(ROOT / "backend/.venv/bin/python")


def _run(cmd, cwd=ROOT):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd).stdout


def main() -> int:
    v = json.loads((ROOT / "backend/data/validation/latest.json").read_text())
    lv = next(x for x in v["variants"] if x["key"] == "level")
    ch = next(x for x in v["variants"] if x["key"] != "level")
    ov, oc, pr = lv["overall"], ch["overall"], lv["procurement"]
    D = json.loads(_run(["node", "-e", "import('./frontend/src/mocks/data.js').then(m=>{const D=m.SIXSENSE_DATA;"
                         "console.log(JSON.stringify({c:D.collection.summary,h:D.history.slice(-1)[0],t:D.trend}))})"]))
    tests = re.search(r"(\d+) passed", _run([PY, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"], ROOT / "backend"))
    mut = re.search(r"(\d+)개 중 시험이 잡은 것 (\d+)개", _run([PY, "tests/mutation_check.py"], ROOT / "backend"))
    commits = _run(["git", "rev-list", "--count", "HEAD"]).strip()

    expect = [   # (이름, 발표에 있어야 할 문자열)
        ("앱 방식 MAPE", f"{ov['modelMape']}%"), ("기준선 MAPE", f"{round(ov['naiveMape'], 1)}%"),
        ("개선 시도 MAPE", f"{round(oc['modelMape'], 1)}%"), ("앱 방식 기준선 이긴 비율", f"{ov['winRate']}%"),
        ("개선 시도 이긴 비율", f"{oc['winRate']}%"), ("개선 시도 p값", f"p = {oc['pValue']}"),
        ("앱 방식 오르내림 적중률", f"{ov['dirAcc']}%"), ("개선 시도 오르내림 적중률", f"{oc['dirAcc']}%"),
        ("'항상 오른다' 적중률", f"{ov['alwaysUpDirAcc']}%"), ("검증 횟수", f"{ov['n']}회 워크포워드"),
        ("모델대로 구매 시 단가", f"+{pr['modelPct']}%"), ("미래를 알 때 단가", f"{pr['perfectPct']}%"),
        ("현재 지수", f"{round(D['h']['value'], 1)} pt"), ("4주 변화", f"+{D['t']['change4w']}%"),
        ("신호 수", f"{D['c']['total']}개 신호"), ("정상 신호", f"정상 {D['c']['success']}"),
        ("제외 신호", f"제외 {D['c']['invalid']}"),
        ("자동 시험 수", f"자동 시험 {tests.group(1)}개" if tests else "(시험 실행 실패)"),
        ("돌연변이 적발", f"{mut.group(2)}개 모두 적발" if mut else "(돌연변이 실행 실패)"),
        ("커밋 수", f"{commits} commits"),
    ]
    bad = 0
    for name, s in expect:
        ok = s in DECK
        bad += not ok
        print(("  ✅" if ok else "  ❌"), f"{name}: 발표에 '{s}'", "있음" if ok else "없음")
    print(f"[발표 수치 대조] {len(expect)}개 중 불일치 {bad}개")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
