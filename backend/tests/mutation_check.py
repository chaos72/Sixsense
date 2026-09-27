"""돌연변이 시험 — '시험을 시험한다' (v2.6 재발 방지 장치 1-b)

과거에 실제로 있었던 버그를 코드 복사본에 하나씩 되살린 뒤 자동 시험을 돌린다.
시험이 실패해야(= 버그를 잡아야) 정상이다. 버그를 되살렸는데 시험이 통과하면 그 시험은 쓸모없다는 뜻.

사용: backend/.venv/bin/python backend/tests/mutation_check.py   (모두 잡으면 종료코드 0)
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
PIPELINES = BACKEND / "pipelines"

# (이름, 파일, 지금 코드, 되살릴 옛 버그 코드)
MUTATIONS = [
    ("v2.3.2 과거 값 고정 해제 (새 값으로 덮어씀)", "auto_collectors.py",
     'fresh = [r for r in new_data if is_open(r["week"])]',
     'fresh = list(new_data); kept = [r for r in kept if r["week"] not in {x["week"] for x in new_data}]'),
    ("v2.5 오류1 빈 주 재시도 없음 (영구 빈칸)", "auto_collectors.py",
     "return not ft or week > ft or (week not in have and week >= retry_from)",
     "return not ft or week > ft"),
    ("v2.5 오류6 기준 날짜를 현지 날짜로", "auto_collectors.py",
     'else datetime.now(timezone.utc).date()', 'else date.today()'),
    ("v2.5 오류2 B-7 진행 중인 주 포함 (0 표시)", "auto_collectors.py",
     "    # Sum all weeks in range (zero-fill missing)\n    weeks = (END_D - START_D).days // 7 + 1\n    data = []\n    for i in range(weeks):\n        w = snap_to_monday(START_D + timedelta(weeks=i)).isoformat()\n        if w > _last_completed_week():   # 진행 중인 주 제외 — 개수·점수 합은 주가 끝나야 의미 (v2.5)\n            continue\n",
     "    # Sum all weeks in range (zero-fill missing)\n    weeks = (END_D - START_D).days // 7 + 1\n    data = []\n    for i in range(weeks):\n        w = snap_to_monday(START_D + timedelta(weeks=i)).isoformat()\n"),
    ("v2.4.1 A-4 응답 검사 제거 (엉뚱한 표 저장)", "auto_collectors.py",
     'if not all("재고지수" in itm and "반도체" in ind for itm, ind in names):', "if False:"),
    ("v2.3.1 A-1 정규화 없이 가중 (TSMC 98%)", "auto_collectors.py",
     "(0.7 * tsm[w] / bt + 0.3 * umc[w] / bu) * 100", "0.7 * tsm[w] + 0.3 * umc[w]"),
    ("v2.5 네트워크 오류를 '설정 필요'로", "auto_collectors.py",
     "    except requests.exceptions.RequestException as e:", "    except ZeroDivisionError as e:"),
    ("v2.4 숫자 안전장치가 p값 줄여 쓰기 허용", "build_insight.py",
     "(abs(a) >= 1 and abs(x - abs(a)) <= tol)", "abs(x - abs(a)) <= tol"),
    ("v2.5 p값 검정이 항상 합격 쪽 (옛 부호검정처럼 과소)", "honest_backtest.py",
     "return float(1 - stats.t.cdf(dm, df=n - 1))", "return 0.0"),
    ("v2.4 지금 예측에 미래 정보(정답 없는 행) 사용", "honest_backtest.py",
     "train_idx = [j for j in range(n) if not np.isnan(target.iloc[j])]", "train_idx = list(range(n))"),
    ("v2.6 LLM 기사 번호 'N3' 해석 못 함 (뉴스 10건이 조용히 0건)", "collect_news_events.py",
     "return int(m.group()) - 1 if m else -1", "return -1"),
    ("v2.6 화면 뉴스 0건 검사 제거", "data_checks.py",
     "        if not d.get(key):\n            problems.append(f\"화면 데이터에 {label} 0건\")\n", ""),
    ("v2.6 데이터 의미 검사 범위 확인 제거 (492만 통과)", "data_checks.py",
     'out = [v for v in nums if not (rule["lo"] <= v <= rule["hi"])]', "out = []"),
    ("v2.6.1 정책: 오픈소스 모델(llama) 몰래 추가", "gemini_client.py",
     'BULK_MODELS = (', 'BULK_MODELS = ("llama-3.3-70b-versatile", '),
    ("v2.6.1 정책: 호출 주소를 다른 공급자로", "gemini_client.py",
     '_URL = "https://generativelanguage.googleapis.com/', '_URL = "https://api.groq.com/openai/'),
    ("v2.6.1 A-3 한 달 연결 실패를 무시하고 일부 달로 저장", "auto_collectors.py",
     "    if net_errors:\n", "    if False:\n"),
    ("v2.6.1 최신 관측 후퇴 방지 장치 제거", "auto_collectors.py",
     "        why = _regressed(sid, data)\n        if why:\n", "        why = _regressed(sid, data)\n        if False:\n"),
    ("v2.6.2 후퇴 방지 두 번째 검사를 주간 신호에도 적용 (B-2 오탐)", "auto_collectors.py",
     "    if sid in MONTHLY_SIGNALS | QUARTERLY_SIGNALS and nc < oc:\n", "    if nc < oc:\n"),
    ("v2.6.2 뉴스 피드 일부 실패를 무시하고 나머지로 저장 (B-2·B-1·B-5·B-6)", "auto_collectors.py",
     "        if why:\n            raise requests.exceptions.ConnectionError(\n",
     "        if False:\n            raise requests.exceptions.ConnectionError(\n"),
    ("v2.6.3 시간 초과·연결 오류 피드를 건너뛰고 나머지로 저장", "auto_collectors.py",
     '            why = f"{type(e).__name__}: {str(e)[:40]}"\n', "            continue\n"),
    ("v2.6.2 피드 연결 실패(응답 없음)를 정상으로 간주", "auto_collectors.py",
     "    if status is None:\n        return \"응답 없음(연결 실패)\"\n", "    if status is None:\n        return None\n"),
    ("v2.6.3 피드 전체 시간 제한 제거 (조금씩 끝없이 오는 응답에 붙잡힘)", "feeds.py",
     "    t.join(TOTAL_TIMEOUT)\n", "    t.join()\n"),
    ("v2.6.3 신호 피드 시간 예산 제거 (느리지만 성공하는 피드 22개가 작업 한도 초과)", "auto_collectors.py",
     "        if time.monotonic() - started > SIGNAL_FEED_BUDGET:\n", "        if False:\n"),
    ("v2.6.3 뉴스 목록 시간 예산 제거 (느린 피드 여러 개가 작업 한도 초과)", "collect_news_events.py",
     "        if time.monotonic() - started > FEED_BUDGET:\n", "        if False:\n"),
    ("v2.6.3 피드를 대기 시간 제한 없는 옛 방식으로 받기", "auto_collectors.py",
     "            f = feeds.get_feed(url)          # 대기 시간 제한 있음 (v2.6.3)\n",
     "            import feedparser\n            f = feedparser.parse(url)\n"),
    ("v2.3.1 신선도: 기준금리도 같은 값 검사", "build_frontend_data.py",
     "    if sid in NO_FROZEN_CHECK:\n        return None\n", ""),
]


def main() -> int:
    caught, survived = 0, []
    for name, fname, now, old in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "pipelines"
            shutil.copytree(PIPELINES, copy, ignore=shutil.ignore_patterns("__pycache__"))
            f = copy / fname
            src = f.read_text()
            n = src.count(now)
            if n != 1:
                # 여러 곳이면 엉뚱한 곳을 바꿀 수 있다(v2.6.2: 새 코드의 같은 문장이 후퇴 방지 대신 바뀌던 문제) → 앞뒤 문맥을 넣어 한 곳으로
                print(f"  ⚠️ {name}: 되살릴 위치가 {n}곳(정확히 1곳이어야 함) — 목록 갱신 필요")
                survived.append(name + f" (위치 {n}곳)")
                continue
            f.write_text(src.replace(now, old))
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", str(BACKEND / "tests")],
                               env={**os.environ, "SIXSENSE_PIPELINES": str(copy)},
                               capture_output=True, text=True, cwd=BACKEND)
            if r.returncode != 0:
                caught += 1
                print(f"  ✅ 잡음: {name}")
            else:
                survived.append(name)
                print(f"  ❌ 놓침: {name} — 이 버그를 막는 시험이 없음")
    total = len(MUTATIONS)
    print(f"[돌연변이 시험] 되살린 과거 버그 {total}개 중 시험이 잡은 것 {caught}개")
    return 0 if caught == total else 1


if __name__ == "__main__":
    sys.exit(main())
