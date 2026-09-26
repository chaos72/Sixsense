"""build_frontend_data.py — 실데이터 → frontend/src/mocks/data.js

수집된 신호·뉴스·지표와 정직한 예측 검증 결과(honest_backtest.py)만 화면 데이터로 만든다.
검증을 통과하지 못한 예측 수치, 고정 신뢰도, 예시 문장은 넣지 않는다 (v2.3 화면 정직화).
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[2]
HIST = ROOT / "backend/data/historical"
VALIDATION = ROOT / "backend/data/validation/latest.json"
OUT = ROOT / "frontend/src/mocks/data.js"

# target-dram 은 메모리 3사 주가지수(2025-06-16 = 100)다. DRAM 계약가·$/GB 가 아니므로 환산하지 않고
# 지수 포인트 그대로 표시한다. (이전엔 ÷100 해서 "$7.47/GB 계약가"로 표시 — 사실과 다름)
UNIT_LABEL = "메모리 3사 주가지수"
UNIT_DESC = "MU 50% · SK하이닉스 30% · 삼성전자 20% 주가 가중, 2025-06-16 = 100"
PROXY_NOTE = "실제 DRAM 계약가가 아닌 대용 지표입니다."
# 수집 신선도 — 마지막 수집이 이 일수보다 오래되면 '갱신 중단'으로 표시
STALE_DAYS = 14
# 값 정체 — 수집은 되지만 같은 값이 이 주수 이상 이어지면 데이터가 멈춘 것으로 본다.
# 기준은 신호의 원천 발표 주기에 맞춘다 (예: A-3 관세청은 2026-03 값이 26주째 복사되고 있었음).
FROZEN_WEEKS = 8                                    # 주간·일간 시장 데이터
MONTHLY_SIGNALS = {"A-3", "A-4", "B-4", "macro-pmi"}  # 월간 통계 — 한 달 값이 발표 지연(약 2개월)까지 이어져 최대 약 4개월 같은 값 정상
QUARTERLY_SIGNALS = {"A-2"}                         # 분기 실적
NO_FROZEN_CHECK = {"macro-fed"}                     # 정책금리 — 회의 사이 동결이 정상 (수집일만 검사)


def frozen_limit(sid: str) -> int | None:
    """같은 값이 몇 주 이어지면 '갱신 중단'으로 볼지. None = 값 정체 검사 안 함."""
    if sid in NO_FROZEN_CHECK:
        return None
    if sid in QUARTERLY_SIGNALS:
        return 26
    if sid in MONTHLY_SIGNALS:
        return 17
    return FROZEN_WEEKS

# 설명은 실제 수집 방식 그대로 적는다(auto_collectors.py / backfill.py 의 source 와 일치).
# 이전 설명 일부는 수집하지 않는 기관 데이터를 적어 과장했음(예: B-5 'DRAMeXchange', B-6 'TrendForce').
SIGNAL_META = {
    "A-1": {"name": "대만 파운드리 주가",  "desc": "TSMC 70%·UMC 30% 주가 (각각 2025-06-16=100 정규화, Yahoo Finance)", "fmt": "pct"},
    "A-2": {"name": "빅테크 CapEx",        "desc": "빅테크 4사 분기 CapEx (SEC EDGAR, 분기 4개 관측)",     "fmt": "usd_b"},
    "A-3": {"name": "관세청 메모리 수출",  "desc": "HS 854232 월간 수출액 USD (관세청 Open API)",          "fmt": "raw"},
    "A-4": {"name": "반도체 재고지수",     "desc": "KOSIS 광업제조업동향조사 · 반도체 제조업(C261) 생산자제품 재고지수(원지수, 2020=100), 월간", "fmt": "raw"},
    "A-5": {"name": "AWS 스팟 가격",       "desc": "EC2 m6i.xlarge 스팟 시간당 USD (최근 90일)",            "fmt": "usd"},
    "A-6": {"name": "대만 침공 예측시장",  "desc": "Manifold Markets '2030년 전 중국의 대만 침공' 확률",    "fmt": "pct100"},
    "A-7": {"name": "구리 선물가",         "desc": "COMEX 구리 선물 HG=F (Yahoo Finance)",                  "fmt": "usd"},
    "B-1": {"name": "실적발표 뉴스 감성",  "desc": "구글 뉴스 헤드라인을 Gemini 로 감성 점수화 (-1~+1)",    "fmt": "sent"},
    "B-2": {"name": "대만 뉴스 감성",      "desc": "TechNews·Digitimes 등 RSS 키워드 감성 점수 (-1~+1)",    "fmt": "sent"},
    "B-3": {"name": "HN 메모리가격 화제도", "desc": "Hacker News 'memory chip price' 게시글 지표",          "fmt": "raw"},
    "B-4": {"name": "지정학 리스크",       "desc": "Caldara & Iacoviello GPR Index (월간)",                  "fmt": "sent_neg"},
    "B-5": {"name": "LTA 뉴스 감성",       "desc": "구글 뉴스 'LTA' 헤드라인 Gemini 감성 점수 (-1~+1)",      "fmt": "sent"},
    "B-6": {"name": "HBM 뉴스 감성",       "desc": "구글 뉴스 'HBM' 헤드라인 Gemini 감성 점수 (-1~+1)",      "fmt": "sent"},
    "B-7": {"name": "HN 메모리 화제도",    "desc": "Hacker News 메모리 관련 4개 검색어 게시글 점수",          "fmt": "raw"},
}
# USER-REQUESTED CHANGE (v1.2) — 화면에서 제외한 4개 신호.
# (제외 근거였던 '예측 영향도 0%' 수치는 누수가 있던 파이프라인 결과라 신뢰할 수 없음 — 표시만 제외 유지)
EXCLUDED_SIGNALS = {"A-2", "B-2", "B-3", "B-4"}
# 수집은 되지만 값이 그 신호가 아님이 확인된 것 — 화면·AI 요약·예측 검증에서 모두 뺀다 (한 곳에서만 정의).
INVALID_SIGNALS = {
    # (v2.5.1) A-4 는 올바른 표(반도체 재고지수)로 복구되어 제외 해제
}

MACRO_META = {
    # USER-REQUESTED EXTENSION (2026-05-19 #15) — 10년물 국채금리를 §06 거시경제 카드 첫번째로 배치
    # (위험자산 선호도 핵심 지표 → DRAM 의사결정에 가장 직접적)
    "macro-ust10": {"name": "미국 10년물 국채금리",   "desc": "FRED DGS10 (10-Year Treasury Yield, 위험자산 선호도 지표)", "unit": "%",  "scale": 1.0},
    "macro-fed":   {"name": "미국 금리",            "desc": "Effective Federal Funds Rate (FRED DFF)",                 "unit": "%",  "scale": 1.0},
    "macro-dxy":   {"name": "달러 인덱스 (DXY)",     "desc": "강달러 = DRAM 수출 부정 (DX-Y.NYB)",                        "unit": "",   "scale": 1.0},
    "macro-pmi":   {"name": "산업생산지수",          "desc": "FRED INDPRO (PMI 대체)",                                    "unit": "",   "scale": 1.0},
    "macro-krw":   {"name": "USD/KRW",              "desc": "원화 약세 = 수입 원가↑ (Yahoo KRW=X)",                       "unit": "원", "scale": 1.0},
    "macro-cu":    {"name": "구리 가격",            "desc": "LME 대체 (COMEX HG=F)",                                     "unit": "$",  "scale": 1.0},
}


def load_signal(sid: str) -> dict:
    p = HIST / f"{sid}.json"
    if not p.exists():
        return {"data": [], "source": "(없음)", "mode": "missing"}
    return json.loads(p.read_text())


def latest_value(rows: list[dict]) -> float | None:
    if not rows:
        return None
    return rows[-1]["value"]


def pct_change(rows: list[dict], lookback: int = 4) -> float:
    if len(rows) < lookback + 1:
        return 0.0
    last = rows[-1]["value"]
    prev = rows[-1 - lookback]["value"]
    if prev == 0:
        return 0.0
    return (last - prev) / abs(prev)


def normalize_sparkline(vals: list[float]) -> list[float]:
    if not vals:
        return [0.0] * 8
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return [0.5] * len(vals)
    return [round((v - lo) / (hi - lo), 3) for v in vals]


def fmt_signal(sid: str, rows: list[dict], ref_date: str) -> dict:
    meta = SIGNAL_META[sid]
    last = latest_value(rows) or 0.0
    sparkline_raw = [r["value"] for r in rows[-8:]] if rows else []
    spark = normalize_sparkline(sparkline_raw)

    fmt = meta["fmt"]
    tone = "neu"
    if fmt == "sent":  # -1..+1 sentiment
        value = f"{last:+.2f}"
        num = last
        tone = "pos" if last >= 0.30 else "neg" if last <= -0.30 else "neu"
    elif fmt == "sent_neg":  # GPR — high = bad
        value = f"{last:.1f}"
        num = last
        tone = "neg" if last >= 150 else "neu" if last >= 100 else "pos"
    elif fmt == "pct":  # 4-week % change
        ch = pct_change(rows, 4)
        value = f"{ch * 100:+.1f}%"
        num = ch
        tone = "pos" if ch >= 0.03 else "neg" if ch <= -0.03 else "neu"
    elif fmt == "pct100":  # already 0-100 percent
        value = f"{last * 100:.0f}%" if last < 1 else f"{last:.0f}%"
        num = last
        tone = "neu"
    elif fmt == "usd":
        value = f"${last:.2f}"
        num = last
        ch = pct_change(rows, 4)
        tone = "pos" if ch >= 0.03 else "neg" if ch <= -0.03 else "neu"
    elif fmt == "usd_b":  # USD billions
        value = f"${last / 1e9:.1f}B"
        num = last
        tone = "pos"
    else:  # raw
        if abs(last) >= 1e9:
            value = f"{last / 1e9:.2f}B"
        elif abs(last) >= 1e6:
            value = f"{last / 1e6:.2f}M"
        elif abs(last) >= 1e3:
            value = f"{last / 1e3:.1f}K"
        else:
            value = f"{last:.2f}"
        num = last

    sig = load_signal(sid)
    src_short = (sig.get("source") or "").split("(")[0].split(",")[0].strip()[:40] or "(미수집)"
    collected = sig.get("collectedAt")
    fr = freshness(rows, collected, ref_date, sid)

    return {
        "id": sid,
        "name": meta["name"],
        "source": src_short,
        "value": value,
        "num": round(num, 4),
        "tone": tone,
        "desc": meta["desc"],
        "spark": spark,
        # 상세 화면용 실측 이력 — 최근 26주 원값과 날짜 (가공·보간 없음)
        "recent": [{"week": r["week"], "value": round(r["value"], 4)} for r in rows[-26:]],
        "asOf": rows[-1]["week"] if rows else None,
        "collectedAt": collected,
        "dataSince": fr["dataSince"],
        "stale": fr["stale"],
        "staleReason": fr["reason"],
    }


def build_history(target_rows: list[dict]) -> tuple[list[dict], float]:
    """target-dram 최근 52주 — 지수 포인트 그대로 (week: -51 … 0, 0 = 최신)."""
    last52 = target_rows[-52:]
    history = [{"week": -(len(last52) - 1 - i), "date": r["week"],
                "value": round(r["value"], 2), "type": "actual"}
               for i, r in enumerate(last52)]
    return history, history[-1]["value"]


def build_trend(target_rows: list[dict]) -> dict:
    """실측 추세 요약 — 예측이 아니라 지나간 데이터의 서술 통계."""
    vals = [r["value"] for r in target_rows]

    def change(weeks: int):
        return round((vals[-1] / vals[-1 - weeks] - 1) * 100, 1) if len(vals) > weeks else None

    last52 = target_rows[-52:]
    hi = max(last52, key=lambda r: r["value"])
    lo = min(last52, key=lambda r: r["value"])
    recent = vals[-14:]
    weekly = [(recent[i] / recent[i - 1] - 1) * 100 for i in range(1, len(recent))]
    mean = sum(weekly) / len(weekly) if weekly else 0
    vol = (sum((w - mean) ** 2 for w in weekly) / len(weekly)) ** 0.5 if weekly else None
    return {
        "change1w": change(1), "change4w": change(4), "change13w": change(13),
        "high52": {"value": round(hi["value"], 2), "date": hi["week"]},
        "low52": {"value": round(lo["value"], 2), "date": lo["week"]},
        "weeklyVol13w": round(vol, 1) if vol is not None else None,
    }


def build_macro(ref_date: str) -> list[dict]:
    out = []
    for mid, meta in MACRO_META.items():
        rows = load_signal(mid)["data"]
        if not rows:
            continue
        last = rows[-1]["value"]
        prev = rows[-5]["value"] if len(rows) >= 5 else last
        # USER-REQUESTED EXTENSION (#10) — macro-ust10 도 강달러 계열(높을수록 위험자산 선호↓→DRAM 부정)
        NEGATIVE_WHEN_UP = ("macro-dxy", "macro-krw", "macro-ust10")
        change = "↑ 부정" if mid in NEGATIVE_WHEN_UP and last > prev else \
                 "↑ 긍정" if last > prev else \
                 "↓ 부정" if mid in NEGATIVE_WHEN_UP and last < prev else \
                 "↓ 긍정" if last < prev else "동결"
        tone = "neu"
        if mid in NEGATIVE_WHEN_UP:
            tone = "neg" if last > prev else "pos" if last < prev else "neu"
        elif mid in ("macro-pmi", "macro-cu"):
            tone = "pos" if last > prev else "neg" if last < prev else "neu"
        elif mid == "macro-fed":
            tone = "neu"

        if meta["unit"] == "원":
            val_str = f"{last:,.0f}"
        elif meta["unit"] == "$":
            val_str = f"${last:.2f}"
        elif meta["unit"] == "%":
            val_str = f"{last:.2f}%"
        else:
            val_str = f"{last:.1f}"

        history_vals = [round(r["value"], 2) for r in rows[-7:]]
        as_of = rows[-1]["week"]
        fr = freshness(rows, load_signal(mid).get("collectedAt"), ref_date, mid)
        out.append({
            "id": mid.replace("macro-", ""),
            "asOf": as_of,
            "source": (load_signal(mid).get("source") or "").split(" (")[0][:60],
            "unit": meta["unit"],
            "recent": [{"week": r["week"], "value": round(r["value"], 4)} for r in rows[-26:]],
            "stale": fr["stale"],
            "staleReason": fr["reason"],
            "dataSince": fr["dataSince"],
            "name": meta["name"],
            "value": val_str,
            "change": change,
            "tone": tone,
            "desc": meta["desc"],
            "history": history_vals,
        })
    return out


def _days_between(d1: str, d2: str) -> int:
    return abs((datetime.fromisoformat(d2[:10]) - datetime.fromisoformat(d1[:10])).days)


def freshness(rows: list[dict], collected: str | None, ref_date: str, sid: str) -> dict:
    """신선도 판정 — 수집 중단 또는 값 정체(신호 주기별 기준). 화면·인사이트가 같은 기준을 쓴다."""
    if not rows or not collected:
        return {"stale": True, "reason": "수집된 데이터 없음", "dataSince": None, "frozenWeeks": 0}
    run = 1
    while run < len(rows) and rows[-run]["value"] == rows[-run - 1]["value"]:
        run += 1
    since = rows[-run]["week"]
    if _days_between(collected, ref_date) > STALE_DAYS:
        reason = f"{collected} 이후 수집되지 않음"
    elif (limit := frozen_limit(sid)) is not None and run >= limit:
        reason = f"수집은 되지만 값이 {since} 이후 {run}주째 같음 (원천 데이터 미갱신)"
    else:
        reason = None
    return {"stale": reason is not None, "reason": reason, "dataSince": since, "frozenWeeks": run}


def build_collection(group: str, ref_date: str) -> list[dict]:
    """신호별 수집 상태 — 마지막 수집일이 기준일보다 STALE_DAYS 넘게 오래되면 '갱신 중단'."""
    rows = []
    for sid in (f"{group}-{i}" for i in range(1, 8)):
        sig = load_signal(sid)
        collected = sig.get("collectedAt")
        fr = freshness(sig.get("data", []), collected, ref_date, sid)
        status = ("invalid" if sid in INVALID_SIGNALS else "fail" if not sig.get("data")
                  else "stale" if fr["stale"] else "ok")
        rows.append({
            "id": sid,
            "name": SIGNAL_META.get(sid, {"name": sid})["name"],
            "source": (sig.get("source") or "(미수집)")[:50],
            "time": collected or "-",
            "weeks": len(sig.get("data", [])),
            "dataSince": fr["dataSince"],
            "reason": INVALID_SIGNALS.get(sid) or fr["reason"],
            "status": status,
        })
    return rows


def build_snapshot_past(target_rows: list[dict]) -> dict:
    """8주 전 시점 vs 현재 — 실측 지수와 신호 변화 (예측 아님)."""
    if len(target_rows) < 9:
        return {"date": None, "then": None, "now": None, "changePct": None, "signals": []}
    then_row, now_row = target_rows[-9], target_rows[-1]
    signals = []
    for sid in SIGNAL_META:
        rows = load_signal(sid)["data"]
        if len(rows) < 9:
            continue
        then, now = rows[-9]["value"], rows[-1]["value"]
        direction = "up" if now > then else "down" if now < then else "flat"
        signals.append({
            "id": sid, "name": SIGNAL_META[sid]["name"],
            "then": f"{then:+.2f}" if abs(then) < 10 else f"{then:.1f}",
            "now": f"{now:+.2f}" if abs(now) < 10 else f"{now:.1f}",
            "direction": direction,
        })
    return {
        "date": then_row["week"],
        "then": round(then_row["value"], 2),
        "now": round(now_row["value"], 2),
        "changePct": round((now_row["value"] / then_row["value"] - 1) * 100, 1),
        "signals": signals,
    }


NEWS_FILE = ROOT / "backend/data/news/latest.json"
EVENTS_FILE = ROOT / "backend/data/events/latest.json"
INSIGHT_FILE = ROOT / "backend/data/insight/latest.json"


def load_insight() -> dict | None:
    if not INSIGHT_FILE.exists():
        return None
    j = json.loads(INSIGHT_FILE.read_text())
    return {
        "headline": j.get("headline", ""),
        "summary": j.get("summary", ""),
        "tone": j.get("tone", "neu"),
        "keySignals": j.get("keySignals", []),
        "model": j.get("model", "AI"),
        "generatedAt": j.get("generatedAt", ""),
    }


def load_news_events() -> tuple[list[dict], list[dict], str]:
    """collect_news_events.py 의 산출물을 읽어 (news, events, source_label) 반환.
    파일 없으면 빈 리스트 + 안내 라벨."""
    news, events = [], []
    label_parts = []
    if NEWS_FILE.exists():
        nj = json.loads(NEWS_FILE.read_text())
        news = nj.get("news", [])
        label_parts.append(f"news {len(news)}건 ({nj.get('method', '?')}, {nj.get('collectedAt', '?')})")
    else:
        label_parts.append("news 미수집 — pipelines/collect_news_events.py 실행 필요")
    if EVENTS_FILE.exists():
        ej = json.loads(EVENTS_FILE.read_text())
        events = ej.get("events", [])
        # USER-REQUESTED CHANGE (v1.2) — 글로벌 이벤트에서 '기상이변' 카테고리 제외
        events = [e for e in events if e.get("type") != "기상이변"]
        label_parts.append(f"events {len(events)}건 (기상이변 제외)")
    else:
        label_parts.append("events 미수집")
    return news, events, " · ".join(label_parts)


def load_validation() -> dict | None:
    """honest_backtest.py 결과 — 화면의 '예측 검증 결과' 유일한 출처.
    build_insight.py 가 만든 '왜 불합격인가' 설명(숫자 대조 통과분만)을 함께 붙인다."""
    if not VALIDATION.exists():
        return None
    v = json.loads(VALIDATION.read_text())
    ins = json.loads(INSIGHT_FILE.read_text()) if INSIGHT_FILE.exists() else {}
    v["explanation"] = ins.get("validationExplanation") or {"status": "failed", "text": "", "model": "",
                                                             "reason": "설명 없음"}
    return v


def main():
    target = load_signal("target-dram")
    target_rows = target["data"]
    history, current = build_history(target_rows)
    trend = build_trend(target_rows)
    ref_date = target.get("collectedAt") or target_rows[-1]["week"]

    signalsA = [fmt_signal(f"A-{i}", load_signal(f"A-{i}")["data"], ref_date)
                for i in range(1, 8) if f"A-{i}" not in EXCLUDED_SIGNALS | INVALID_SIGNALS.keys()]
    signalsB = [fmt_signal(f"B-{i}", load_signal(f"B-{i}")["data"], ref_date)
                for i in range(1, 8) if f"B-{i}" not in EXCLUDED_SIGNALS | INVALID_SIGNALS.keys()]
    macro = build_macro(ref_date)

    real_news, real_events, news_label = load_news_events()
    groupA, groupB = build_collection("A", ref_date), build_collection("B", ref_date)
    rows = groupA + groupB
    collection = {
        "summary": {
            "total": len(rows),
            "success": sum(r["status"] == "ok" for r in rows),
            "stale": sum(r["status"] == "stale" for r in rows),
            "fail": sum(r["status"] == "fail" for r in rows),
            "invalid": sum(r["status"] == "invalid" for r in rows),
        },
        "week": ref_date,
        "staleDays": STALE_DAYS,
        "groupA": groupA,
        "groupB": groupB,
    }

    payload = {
        "meta": {
            "current": current,
            "currentChange": f"{trend['change1w']:+.1f}%" if trend["change1w"] is not None else "-",
            "unitLabel": UNIT_LABEL,
            "unitDesc": UNIT_DESC,
            "unitShort": "pt",
            "proxyNote": PROXY_NOTE,
            # 실제 생성 시각(한국 시간) — 이전엔 "06:00 KST" 고정이라 수동 실행·UTC 월요일 실행 때 틀렸음 (v2.5)
            "updated": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST"),
            "insight": load_insight(),
        },
        "history": history,
        "trend": trend,
        "validation": load_validation(),
        "signalsA": signalsA,
        "signalsB": signalsB,
        "news": real_news,
        "macro": macro,
        "events": real_events,
        "snapshotPast": build_snapshot_past(target_rows),
        "collection": collection,
    }

    js = f"""// AUTO-GENERATED by backend/pipelines/build_frontend_data.py
// DO NOT EDIT MANUALLY — regenerate via: python3 pipelines/build_frontend_data.py
// 데이터 소스: backend/data/historical/* + backend/data/validation/latest.json
//             + backend/data/news/latest.json + backend/data/events/latest.json
// 생성 시각: {datetime.utcnow().isoformat()}Z
// 뉴스/이벤트: {news_label}

export const SIXSENSE_DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};
"""
    OUT.write_text(js, encoding="utf-8")
    v = payload["validation"] or {}
    print(f"✅ {OUT.relative_to(ROOT)} 생성 완료 ({OUT.stat().st_size:,} bytes)")
    print(f"   - {UNIT_LABEL}: {current:.2f} pt  (지난주 대비 {payload['meta']['currentChange']})")
    print(f"   - 예측 검증: {v.get('verdict', '결과 없음')} ({v.get('runAt', '-')})")
    print(f"   - 수집: 정상 {collection['summary']['success']} · 갱신중단 {collection['summary']['stale']} · "
          f"제외 {collection['summary']['invalid']} · 실패 {collection['summary']['fail']} / {collection['summary']['total']}")
    print(f"   - history: {len(history)}주, signalsA: {len(signalsA)}, signalsB: {len(signalsB)}, macro: {len(macro)}")


if __name__ == "__main__":
    main()
