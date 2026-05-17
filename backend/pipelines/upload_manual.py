#!/usr/bin/env python3
"""Manual CSV upload tool — 사용자가 직접 수집한 데이터를 historical/ 폴더로 적재.

CSV 형식 (헤더 필수):
    week,value
    2025-05-05,123.45
    2025-05-12,124.10
    ...

사용법:
    # 단일 파일 업로드
    .venv/bin/python3 pipelines/upload_manual.py A-3 manual/A-3.csv --source "관세청 무역통계 CSV"

    # 일괄 업로드 (manual/ 폴더의 *.csv 모두)
    .venv/bin/python3 pipelines/upload_manual.py --all

업로드 결과:
    backend/data/historical/<signal-id>.json  (mode: "manual")
    backend/data/historical/_summary.json     (자동 갱신)
"""
import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
HIST_DIR = ROOT / "data" / "historical"
MANUAL_DIR = ROOT / "data" / "manual"
HIST_DIR.mkdir(parents=True, exist_ok=True)
MANUAL_DIR.mkdir(parents=True, exist_ok=True)


def parse_csv(csv_path: Path) -> list[dict]:
    """CSV → [{week: 'YYYY-MM-DD', value: float}, ...]
    week 정규화: 어떤 형식이든 ISO 날짜로 변환 + 해당 주의 월요일로 스냅.
    """
    out = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "week" not in reader.fieldnames or "value" not in reader.fieldnames:
            raise ValueError(f"CSV 헤더 'week,value' 필수. 현재: {reader.fieldnames}")
        for row_no, row in enumerate(reader, start=2):
            wk_raw = (row.get("week") or "").strip()
            val_raw = (row.get("value") or "").strip()
            if not wk_raw or not val_raw:
                continue
            # 날짜 파싱 (YYYY-MM-DD / YYYY/MM/DD / YYYYMMDD 등 허용)
            d = None
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    d = datetime.strptime(wk_raw, fmt).date()
                    break
                except ValueError:
                    continue
            if d is None:
                raise ValueError(f"행 {row_no}: 날짜 형식 인식 불가 '{wk_raw}'")
            # 해당 주의 월요일로 스냅 (주간 정규화)
            mon = d - timedelta(days=d.weekday())
            try:
                v = float(val_raw)
            except ValueError:
                raise ValueError(f"행 {row_no}: value 숫자 아님 '{val_raw}'")
            out.append({"week": mon.isoformat(), "value": round(v, 4)})
    # 같은 주에 여러 값이 있으면 평균
    from collections import defaultdict
    grouped = defaultdict(list)
    for item in out:
        grouped[item["week"]].append(item["value"])
    return [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(grouped.items())]


def upload_one(signal_id: str, csv_path: Path, source_note: str = "manual CSV upload") -> dict:
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)
    data = parse_csv(csv_path)
    if not data:
        raise ValueError("데이터 0건 — CSV 비었거나 모든 행 무효")
    payload = {
        "signalId": signal_id,
        "source": source_note,
        "mode": "manual",
        "collectedAt": date.today().isoformat(),
        "rangeStart": data[0]["week"],
        "rangeEnd": data[-1]["week"],
        "note": f"Uploaded from {csv_path.name}, {len(data)}주",
        "data": data,
    }
    out_path = HIST_DIR / f"{signal_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    return {
        "signalId": signal_id,
        "weeks": len(data),
        "rangeStart": data[0]["week"],
        "rangeEnd": data[-1]["week"],
        "outPath": str(out_path),
    }


def update_summary():
    """Re-aggregate _summary.json from all signal files in historical/"""
    summary = {
        "lastUpdated": date.today().isoformat(),
        "totalSignals": 0,
        "byMode": {"real": 0, "manual": 0, "synthetic": 0, "partial": 0, "skipped": 0, "failed": 0},
        "signals": [],
    }
    for fp in sorted(HIST_DIR.glob("*.json")):
        if fp.name.startswith("_"):
            continue
        try:
            j = json.loads(fp.read_text())
            summary["signals"].append({
                "signalId": j.get("signalId"),
                "mode": j.get("mode"),
                "weeks": len(j.get("data", [])),
                "rangeStart": j.get("rangeStart"),
                "rangeEnd": j.get("rangeEnd"),
                "source": j.get("source"),
            })
            summary["totalSignals"] += 1
            m = j.get("mode", "real")
            summary["byMode"][m] = summary["byMode"].get(m, 0) + 1
        except Exception:
            pass
    (HIST_DIR / "_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    return summary


def main():
    p = argparse.ArgumentParser(description="Manual CSV upload for Sixsense signals.")
    p.add_argument("signal_id", nargs="?", help="신호 ID (예: A-3, B-1). --all 사용 시 생략.")
    p.add_argument("csv_path", nargs="?", help="CSV 파일 경로 (예: data/manual/A-3.csv)")
    p.add_argument("--source", default="manual CSV upload", help="출처 설명 (data acquisition report용)")
    p.add_argument("--all", action="store_true", help="data/manual/*.csv 모두 업로드 (파일명=신호ID)")
    args = p.parse_args()

    print(f"\n{'═'*70}\n  Sixsense Manual Upload\n{'═'*70}\n")

    if args.all:
        csvs = sorted(MANUAL_DIR.glob("*.csv"))
        if not csvs:
            print(f"  ⚠️  {MANUAL_DIR}에 CSV 파일 없음")
            sys.exit(0)
        for csv_path in csvs:
            sid = csv_path.stem
            try:
                r = upload_one(sid, csv_path, args.source)
                print(f"  ✅ {sid:12} {r['weeks']:3}주 [{r['rangeStart']} ~ {r['rangeEnd']}]")
            except Exception as e:
                print(f"  ❌ {sid:12} 실패: {e}")
    else:
        if not args.signal_id or not args.csv_path:
            print("  ❌ signal_id와 csv_path 둘 다 필요. 또는 --all 사용.")
            p.print_help()
            sys.exit(1)
        try:
            r = upload_one(args.signal_id, Path(args.csv_path), args.source)
            print(f"  ✅ {r['signalId']:12} {r['weeks']:3}주 [{r['rangeStart']} ~ {r['rangeEnd']}]")
            print(f"     → {r['outPath']}")
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            sys.exit(1)

    s = update_summary()
    print(f"\n  📊 전체 신호 현황 (모드별): {s['byMode']}")
    print(f"  📁 _summary.json 갱신됨\n")


if __name__ == "__main__":
    main()
