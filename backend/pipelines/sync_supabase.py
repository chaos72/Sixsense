#!/usr/bin/env python3
"""Sixsense JSON → Supabase 동기화.

사전 조건:
1. Sixsense/.env 에 SUPABASE_URL + SUPABASE_PUBLISHABLE_KEY 설정됨
2. Supabase Studio에서 backend/app/schema.sql 실행 (테이블 생성)

사용법:
    cd backend
    .venv/bin/python3 pipelines/sync_supabase.py             # 모든 신호 + 예측 동기화
    .venv/bin/python3 pipelines/sync_supabase.py --signals   # 신호만
    .venv/bin/python3 pipelines/sync_supabase.py --forecast  # 예측만
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Add parent for app.* import
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.supabase_client import sb

HIST_DIR = Path(__file__).parent.parent / "data" / "historical"
FCST_DIR = Path(__file__).parent.parent / "data" / "forecast"

SIGNAL_META = {
    "A-1":         ("정형", "대만 공급망"),
    "A-2":         ("정형", "빅테크 CapEx"),
    "A-3":         ("정형", "관세청 수출"),
    "A-4":         ("정형", "KOSIS 재고/출하"),
    "A-5":         ("정형", "AWS Spot 가격"),
    "A-6":         ("정형", "Polymarket 봉쇄확률"),
    "A-7":         ("정형", "구리 선물가"),
    "B-1":         ("비정형", "Earnings Call"),
    "B-2":         ("비정형", "대만 뉴스 감성"),
    "B-3":         ("비정형", "Reddit/HN"),
    "B-4":         ("비정형", "지정학 리스크 GPR"),
    "B-5":         ("비정형", "LTA 비율"),
    "B-6":         ("비정형", "HBM/D램 믹스"),
    "B-7":         ("비정형", "BOM 신호"),
    "macro-fed":   ("거시", "미국 금리"),
    "macro-dxy":   ("거시", "달러 인덱스 DXY"),
    "macro-pmi":   ("거시", "산업생산 INDPRO"),
    "macro-krw":   ("거시", "USD/KRW"),
    "macro-cu":    ("거시", "구리 (macro)"),
    "target-dram": ("타겟", "DRAM 가격 proxy"),
}


def sync_signals():
    """historical/*.json → signals + signal_data 테이블."""
    files = sorted(HIST_DIR.glob("*.json"))
    files = [f for f in files if not f.name.startswith("_")]
    print(f"\n  📥 historical/ JSON 파일: {len(files)}개")

    sig_rows = []
    data_rows = []
    for fp in files:
        try:
            j = json.loads(fp.read_text())
            sid = j["signalId"]
            group, name = SIGNAL_META.get(sid, ("기타", sid))
            sig_rows.append({
                "signal_id": sid,
                "group": group,
                "name": name,
                "source": (j.get("source") or "")[:200],
                "mode": j.get("mode", "real"),
                "range_start": j.get("rangeStart"),
                "range_end": j.get("rangeEnd"),
                "note": (j.get("note") or "")[:500],
            })
            for row in j.get("data", []):
                data_rows.append({
                    "signal_id": sid,
                    "week": row["week"],
                    "value": row["value"],
                })
        except Exception as e:
            print(f"    ❌ {fp.name}: {e}")

    # signals upsert (on signal_id)
    print(f"  📤 signals: {len(sig_rows)}건 upsert...")
    try:
        sb.upsert("signals", sig_rows, on_conflict="signal_id")
        print(f"     ✅ 완료")
    except Exception as e:
        print(f"     ❌ 실패: {e}")
        return False

    # signal_data upsert (on signal_id+week, 배치 500개씩)
    print(f"  📤 signal_data: {len(data_rows)}건 upsert (배치)...")
    batch = 500
    total = 0
    for i in range(0, len(data_rows), batch):
        chunk = data_rows[i:i+batch]
        try:
            sb.upsert("signal_data", chunk, on_conflict="signal_id,week")
            total += len(chunk)
            print(f"     {total:>5}/{len(data_rows)} 완료")
        except Exception as e:
            print(f"     ❌ 배치 {i//batch+1} 실패: {e}")
            return False
    print(f"  ✅ signal_data: {total}건 동기화")
    return True


def sync_forecast():
    """forecast/forecast_2026-02-w1.json → forecasts 테이블."""
    fp = FCST_DIR / "forecast_2026-02-w1.json"
    if not fp.exists():
        print(f"  ⚠️ {fp} 없음 — 먼저 forecast.py 실행 필요")
        return False

    j = json.loads(fp.read_text())
    model = j.get("model", "prophet")
    target = j.get("target", "target-dram").split()[0]  # 첫 단어만
    train_cutoff = j.get("trainCutoff")
    regressors = j.get("regressors", [])
    iw = j.get("interval_width", 0.80)

    rows = []
    for h, p in enumerate(j["forecast"]["short_term_1_7w"], start=1):
        rows.append({
            "model": model,
            "target_id": target,
            "train_cutoff": train_cutoff,
            "horizon": h,
            "week": p["week"],
            "yhat": p["yhat"],
            "yhat_lower": p["yhat_lower"],
            "yhat_upper": p["yhat_upper"],
            "interval_width": iw,
            "regressors_used": regressors,
        })
    for h, p in enumerate(j["forecast"]["mid_term_8_21w"], start=8):
        rows.append({
            "model": model,
            "target_id": target,
            "train_cutoff": train_cutoff,
            "horizon": h,
            "week": p["week"],
            "yhat": p["yhat"],
            "yhat_lower": p["yhat_lower"],
            "yhat_upper": p["yhat_upper"],
            "interval_width": iw,
            "regressors_used": regressors,
        })

    print(f"  📤 forecasts: {len(rows)}건 upsert...")
    try:
        sb.upsert("forecasts", rows, on_conflict="model,train_cutoff,week")
        print(f"     ✅ 완료")
        return True
    except Exception as e:
        print(f"     ❌ 실패: {e}")
        return False


def verify():
    """업로드 후 카운트 확인."""
    print(f"\n  🔍 Supabase 확인:")
    for table in ["signals", "signal_data", "forecasts"]:
        try:
            rows = sb.select(table, "signal_id" if table != "forecasts" else "week", limit=10000)
            print(f"     {table:15} {len(rows):>5}건")
        except Exception as e:
            print(f"     {table:15} 조회 실패: {str(e)[:80]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--signals", action="store_true", help="신호 데이터만 동기화")
    p.add_argument("--forecast", action="store_true", help="예측 결과만 동기화")
    args = p.parse_args()

    print(f"\n{'═'*72}")
    print(f"  Sixsense → Supabase 동기화")
    print(f"  URL: {sb.url}")
    print(f"{'═'*72}")

    # 연결 확인 먼저
    ping = sb.ping()
    if not ping.get("auth_ok"):
        print(f"  ❌ Supabase 연결 실패: {ping}")
        print(f"     1) Sixsense/.env에 SUPABASE_URL + SUPABASE_PUBLISHABLE_KEY 확인")
        print(f"     2) Supabase Studio → SQL Editor에서 backend/app/schema.sql 실행")
        sys.exit(1)
    print(f"  ✅ Supabase 연결됨 (status {ping.get('status')})")

    if args.signals or not (args.signals or args.forecast):
        sync_signals()
    if args.forecast or not (args.signals or args.forecast):
        sync_forecast()

    verify()
    print(f"\n{'═'*72}\n")


if __name__ == "__main__":
    main()
