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
     "        if w > _last_completed_week():   # 진행 중인 주 제외 — 개수·점수 합은 주가 끝나야 의미 (v2.5)\n            continue\n",
     ""),
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
            if src.count(now) < 1:
                print(f"  ⚠️ {name}: 되살릴 위치를 못 찾음(코드가 바뀜) — 목록 갱신 필요")
                survived.append(name + " (위치 없음)")
                continue
            f.write_text(src.replace(now, old, 1))   # 여러 곳이면 첫 번째(B-7 은 B-3 보다 앞)만
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
