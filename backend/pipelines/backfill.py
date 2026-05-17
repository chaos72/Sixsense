#!/usr/bin/env python3
"""Sixsense one-shot historical backfill (2025-05-01 ~ 2026-04-30).

Attempts REAL data collection for 14 signals + 5 macro + target proxy.
For sources that are paid/restricted, generates synthetic data with
clear `_synthetic: true` marker.

Output:
- backend/data/historical/<signal_id>.json — weekly time series per signal
- backend/data/historical/_summary.json — collection result summary

Usage:
  cd backend && .venv/bin/python3 pipelines/backfill.py
"""
import json
import math
import time
import warnings
from datetime import date, timedelta
from pathlib import Path

import requests
import yfinance as yf

warnings.filterwarnings("ignore")

START = "2025-05-01"
END = "2026-04-30"
SEC_USER_AGENT = "Sixsense KAIST CAIO 6jo caio6@kaist.example"

OUT_DIR = Path(__file__).parent.parent / "data" / "historical"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def write_series(signal_id: str, data: list[dict], source: str, mode: str, note: str = ""):
    """Write a signal's weekly series to JSON."""
    payload = {
        "signalId": signal_id,
        "source": source,
        "mode": mode,  # "real" | "synthetic" | "partial"
        "collectedAt": date.today().isoformat(),
        "rangeStart": START,
        "rangeEnd": END,
        "note": note,
        "data": data,
    }
    out_path = OUT_DIR / f"{signal_id}.json"
    out_path.write_text(json.dumps(payload, indent=2, default=str))
    return len(data)


def yf_weekly(ticker: str) -> list[dict]:
    """Fetch weekly close prices from Yahoo Finance."""
    df = yf.download(ticker, start=START, end=END, interval="1wk", progress=False, auto_adjust=False)
    if len(df) == 0:
        return []
    out = []
    for idx, row in df.iterrows():
        try:
            close = float(row["Close"].iloc[0] if hasattr(row["Close"], "iloc") else row["Close"])
            if not math.isnan(close):
                out.append({"week": idx.date().isoformat(), "value": round(close, 4)})
        except Exception:
            pass
    return out


def synth_weekly(seed: int, base: float, trend: float, season_amp: float, noise: float) -> list[dict]:
    """Generate weekly synthetic series with trend + seasonality + noise."""
    rng = lambda i: (math.sin(i * 12.9898 + seed) * 43758.5453) % 1
    start = date.fromisoformat(START)
    end = date.fromisoformat(END)
    weeks = (end - start).days // 7 + 1
    out = []
    for i in range(weeks):
        w = start + timedelta(weeks=i)
        season = math.sin(2 * math.pi * i / 52) * season_amp
        n = (rng(i) - 0.5) * noise * 2
        value = base + trend * i + season + n
        out.append({"week": w.isoformat(), "value": round(value, 4), "_synthetic": True})
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Group A — 정형 7
# ──────────────────────────────────────────────────────────────────────────────
def collect_A1_taiwan_supply():
    """TSMC + UMC weekly stock — proxy for 대만 공급망"""
    tsm = yf_weekly("TSM")
    umc = yf_weekly("UMC")
    if not tsm or not umc:
        raise RuntimeError("Yahoo Finance no data")
    # Blend: 70% TSMC, 30% UMC, normalized to baseline 100
    out = []
    for i, t in enumerate(tsm):
        if i < len(umc):
            blended = 0.7 * t["value"] + 0.3 * umc[i]["value"]
            out.append({"week": t["week"], "value": round(blended, 4)})
    return out, "real", "Yahoo Finance: TSM (70%) + UMC (30%)"


def collect_A2_bigtech_capex():
    """Big4 quarterly CapEx from SEC EDGAR (META/MSFT/GOOGL/AMZN)."""
    # CIKs (10-digit zero-padded)
    ciks = {
        "META": "0001326801",
        "MSFT": "0000789019",
        "GOOGL": "0001652044",
        "AMZN": "0001018724",
    }
    quarterly = {}  # date → total $M
    for name, cik in ciks.items():
        url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/PaymentsToAcquirePropertyPlantAndEquipment.json"
        try:
            r = requests.get(url, headers={"User-Agent": SEC_USER_AGENT}, timeout=15)
            r.raise_for_status()
            facts = r.json()
            units = facts.get("units", {}).get("USD", [])
            for f in units:
                end_date = f.get("end", "")
                if not (START <= end_date <= END):
                    continue
                val = f.get("val", 0) / 1e6  # to $M
                quarterly[end_date] = quarterly.get(end_date, 0) + val
            time.sleep(0.2)  # be polite
        except Exception as e:
            print(f"  ⚠️ {name} SEC fetch failed: {str(e)[:60]}")
    if not quarterly:
        raise RuntimeError("No CapEx data from SEC")
    # Forward-fill quarterly to weekly
    sorted_q = sorted(quarterly.items())
    start = date.fromisoformat(START)
    end = date.fromisoformat(END)
    weeks = (end - start).days // 7 + 1
    out = []
    cur_idx = 0
    for i in range(weeks):
        w = start + timedelta(weeks=i)
        # Find latest quarterly value ≤ this week
        while cur_idx + 1 < len(sorted_q) and date.fromisoformat(sorted_q[cur_idx + 1][0]) <= w:
            cur_idx += 1
        val = sorted_q[cur_idx][1] if sorted_q else 0
        out.append({"week": w.isoformat(), "value": round(val, 2)})
    return out, "real", f"SEC EDGAR XBRL — {len(quarterly)} quarterly observations from {len(ciks)} companies"


def collect_A3_kor_customs():
    """관세청 수출 — requires Korean Customs API key registration."""
    raise NotImplementedError(
        "관세청 Open API requires registration at unipass.customs.go.kr. "
        "After getting key, replace this with: GET https://unipass.customs.go.kr/ets/hmpg/ets/ats/imAtsReportAjax.do"
    )


def collect_A4_kor_inventory():
    """KOSIS 재고/출하 — requires KOSIS Open API key."""
    raise NotImplementedError(
        "KOSIS Open API requires registration at kosis.kr/openapi. "
        "After getting key, fetch series '2030_4' (재고출하지수)."
    )


def collect_A5_aws_spot():
    """AWS EC2 Spot prices via Pricing API. Public but complex format."""
    try:
        # Public AWS pricing index endpoint (no auth)
        url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        # Just verify reachable; actual spot history requires per-region per-instance per-az queries
        # Fallback to synthetic for time series (Pricing API is current-state, not history)
        raise NotImplementedError(
            "AWS Pricing API returns current-state JSON only. Historical spot prices require "
            "DescribeSpotPriceHistory (AWS SDK with credentials) or third-party Spot Advisor."
        )
    except requests.RequestException as e:
        raise RuntimeError(f"AWS Pricing API unreachable: {e}")


def collect_A6_polymarket():
    """Polymarket — search for relevant market (semiconductor, Taiwan, etc.)."""
    try:
        # Polymarket public API
        url = "https://gamma-api.polymarket.com/markets?limit=10&active=true&closed=false"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        # Markets list returned — but finding semiconductor-relevant historical is non-trivial
        raise NotImplementedError(
            "Polymarket API reachable, but no standing 'Taiwan blockade' market for "
            "2025-05~2026-04 with weekly resolution. Manual market ID curation needed."
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Polymarket unreachable: {e}")


def collect_A7_copper():
    """LME copper paid → COMEX Copper Futures HG=F via Yahoo (free proxy)."""
    data = yf_weekly("HG=F")
    if not data:
        raise RuntimeError("Yahoo Finance no data for HG=F")
    return data, "real", "Yahoo Finance HG=F (COMEX Copper Futures, LME 대체)"


# ──────────────────────────────────────────────────────────────────────────────
# Group B — 비정형 7
# ──────────────────────────────────────────────────────────────────────────────
def collect_B1_earnings_call():
    raise NotImplementedError(
        "FactSet Transcripts requires paid subscription. "
        "Free alternative: Seeking Alpha 'Earnings Call Transcripts' (partial), "
        "or scrape investor.samsung.com / investor.skhynix.com IR pages quarterly."
    )


def _gdelt_get(params, retries=3):
    """GDELT with rate-limit backoff."""
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    for attempt in range(retries):
        time.sleep(12 + attempt * 10)  # 12s, 22s, 32s
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200 and r.text.strip().startswith("{"):
            return r.json()
        print(f"    GDELT attempt {attempt+1}/{retries}: status={r.status_code}, retry...")
    raise RuntimeError(f"GDELT exhausted retries (last status: {r.status_code})")


def collect_B2_taiwan_news_sentiment():
    """Reuters/Bloomberg paid → GDELT 2.0 free alternative."""
    try:
        j = _gdelt_get({
            "query": "Taiwan semiconductor",
            "mode": "timelinevol",
            "format": "json",
            "startdatetime": "20250501000000",
            "enddatetime": "20260430000000",
            "timelinesmooth": "7",
        })
        tl = j.get("timeline", [])
        if not tl or not tl[0].get("data"):
            raise RuntimeError("GDELT empty timeline")
        from collections import defaultdict
        weekly = defaultdict(list)
        for pt in tl[0]["data"]:
            d_str = pt["date"][:8]
            d = date(int(d_str[:4]), int(d_str[4:6]), int(d_str[6:8]))
            mon = d - timedelta(days=d.weekday())
            weekly[mon.isoformat()].append(pt["value"])
        out = [{"week": w, "value": round(sum(v) / len(v) * 1000, 4)} for w, v in sorted(weekly.items())]
        return out, "real", "GDELT 2.0 Article Volume Timeline (Reuters/Bloomberg 대체)"
    except Exception as e:
        raise RuntimeError(f"GDELT B-2 failed: {e}")


def collect_B3_reddit_x():
    raise NotImplementedError(
        "Pushshift API was shut down in 2023, X API requires paid subscription ($100~$5000/mo). "
        "Free alternative: Reddit official API (PRAW) on r/hardware r/memorymarket with rate limit. "
        "Requires Reddit OAuth app registration."
    )


def collect_B4_geopolitical_risk():
    """GDELT 2.0 free — global event tone."""
    try:
        j = _gdelt_get({
            "query": "semiconductor shortage OR Taiwan strait OR export ban",
            "mode": "timelinetone",
            "format": "json",
            "startdatetime": "20250501000000",
            "enddatetime": "20260430000000",
            "timelinesmooth": "7",
        })
        tl = j.get("timeline", [])
        if not tl or not tl[0].get("data"):
            raise RuntimeError("GDELT empty timeline")
        # Group to weekly average tone (negative = bad sentiment / high risk)
        from collections import defaultdict
        weekly = defaultdict(list)
        for pt in tl[0]["data"]:
            d_str = pt["date"][:8]
            d = date(int(d_str[:4]), int(d_str[4:6]), int(d_str[6:8]))
            mon = d - timedelta(days=d.weekday())
            weekly[mon.isoformat()].append(pt["value"])
        out = [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]
        return out, "real", "GDELT 2.0 Tone Timeline (semiconductor/Taiwan/export ban)"
    except Exception as e:
        raise RuntimeError(f"GDELT B-4 failed: {e}")


def collect_B5_lta_ratio():
    raise NotImplementedError(
        "DRAMeXchange LTA ratio is paid subscription only. "
        "Free alternative: Korean Customs trade balance (관세청 API, A-3 동일 키) of 'DRAM IC' "
        "as inflow-outflow proxy. Or estimate from Samsung/SK quarterly IR (manual)."
    )


def collect_B6_hbm_mix():
    raise NotImplementedError(
        "TrendForce HBM/DRAM mix is paid. Free alternative: SK Hynix earnings call "
        "(quarterly) discloses HBM revenue % — scrape from investor.skhynix.com PDFs."
    )


def collect_B7_bom_signal():
    raise NotImplementedError(
        "Supply-chain BOM transcripts (Bloomberg Supply Chain etc.) are paid. "
        "Free alternative: track Apple/NVIDIA/AMD product launch news as demand signal "
        "(news API or Apple/NVIDIA RSS)."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Macro 5
# ──────────────────────────────────────────────────────────────────────────────
def collect_macro_fed():
    """FRED DFF (Effective Fed Funds Rate) — no API key needed via fredgraph.csv"""
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF&cosd={START}&coed={END}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        lines = r.text.strip().split("\n")[1:]
        out = []
        from collections import defaultdict
        weekly = defaultdict(list)
        for ln in lines:
            d_str, val = ln.split(",")
            if val.strip() == ".":
                continue
            d = date.fromisoformat(d_str)
            mon = d - timedelta(days=d.weekday())
            weekly[mon.isoformat()].append(float(val))
        out = [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]
        return out, "real", "FRED CSV DFF (Effective Federal Funds Rate)"
    except Exception as e:
        raise RuntimeError(f"FRED DFF failed: {e}")


def collect_macro_dxy():
    data = yf_weekly("DX-Y.NYB")
    if not data:
        raise RuntimeError("DXY no data")
    return data, "real", "Yahoo Finance DX-Y.NYB (US Dollar Index)"


def collect_macro_pmi():
    """ISM PMI는 FRED에서 NAPM이 폐기됨 → INDPRO (Industrial Production Index, 월간) 대체."""
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO&cosd={START}&coed={END}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        lines = r.text.strip().split("\n")[1:]
        monthly = []
        for ln in lines:
            d_str, val = ln.split(",")
            if val.strip() == ".":
                continue
            monthly.append((date.fromisoformat(d_str), float(val)))
        if not monthly:
            raise RuntimeError("NAPM empty")
        # Forward-fill monthly to weekly
        start = date.fromisoformat(START)
        end = date.fromisoformat(END)
        weeks = (end - start).days // 7 + 1
        out = []
        cur_idx = 0
        for i in range(weeks):
            w = start + timedelta(weeks=i)
            while cur_idx + 1 < len(monthly) and monthly[cur_idx + 1][0] <= w:
                cur_idx += 1
            out.append({"week": w.isoformat(), "value": monthly[cur_idx][1]})
        return out, "real", "FRED CSV INDPRO (Industrial Production Index, monthly→forward-fill weekly, PMI 대체)"
    except Exception as e:
        raise RuntimeError(f"INDPRO failed: {e}")


def collect_macro_krw():
    data = yf_weekly("KRW=X")
    if not data:
        raise RuntimeError("KRW no data")
    return data, "real", "Yahoo Finance KRW=X (USD/KRW spot)"


def collect_macro_copper():
    return collect_A7_copper()  # same source


# ──────────────────────────────────────────────────────────────────────────────
# Target Y — DRAM price proxy
# ──────────────────────────────────────────────────────────────────────────────
def collect_target_dram_proxy():
    """DRAM contract price is paid (DRAMeXchange/TrendForce).
    Use weighted proxy from memory stocks:
        - Micron (MU) NASDAQ — pure-play memory, US-listed
        - SK Hynix (000660.KS) — Korean memory specialist
        - Samsung Electronics (005930.KS) — incl. memory + others
    Index normalized to base 100 at first week, representing relative memory pricing pressure.
    """
    mu = yf_weekly("MU")
    sk = yf_weekly("000660.KS")
    ss = yf_weekly("005930.KS")
    if not (mu and sk and ss):
        raise RuntimeError("Memory stock proxies unavailable")
    # Align by index (assume same date range)
    n = min(len(mu), len(sk), len(ss))
    base_mu, base_sk, base_ss = mu[0]["value"], sk[0]["value"], ss[0]["value"]
    out = []
    for i in range(n):
        # Normalize each to base 100, then weight 0.5/0.3/0.2 (US heavier as pure-play)
        idx = (
            0.5 * (mu[i]["value"] / base_mu) +
            0.3 * (sk[i]["value"] / base_sk) +
            0.2 * (ss[i]["value"] / base_ss)
        ) * 100
        out.append({"week": mu[i]["week"], "value": round(idx, 4)})
    return out, "real-proxy", "Yahoo Finance blend: MU (50%) + SK Hynix (30%) + Samsung (20%), normalized to base 100"


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
COLLECTORS = [
    # (signal_id, function, group_label)
    ("A-1", collect_A1_taiwan_supply, "정형"),
    ("A-2", collect_A2_bigtech_capex, "정형"),
    ("A-3", collect_A3_kor_customs, "정형"),
    ("A-4", collect_A4_kor_inventory, "정형"),
    ("A-5", collect_A5_aws_spot, "정형"),
    ("A-6", collect_A6_polymarket, "정형"),
    ("A-7", collect_A7_copper, "정형"),
    ("B-1", collect_B1_earnings_call, "비정형"),
    ("B-2", collect_B2_taiwan_news_sentiment, "비정형"),
    ("B-3", collect_B3_reddit_x, "비정형"),
    ("B-4", collect_B4_geopolitical_risk, "비정형"),
    ("B-5", collect_B5_lta_ratio, "비정형"),
    ("B-6", collect_B6_hbm_mix, "비정형"),
    ("B-7", collect_B7_bom_signal, "비정형"),
    ("macro-fed", collect_macro_fed, "거시"),
    ("macro-dxy", collect_macro_dxy, "거시"),
    ("macro-pmi", collect_macro_pmi, "거시"),
    ("macro-krw", collect_macro_krw, "거시"),
    ("macro-cu", collect_macro_copper, "거시"),
    ("target-dram", collect_target_dram_proxy, "타겟"),
]


def main():
    print(f"\n{'═'*80}\nSixsense one-shot backfill: {START} ~ {END}\n{'═'*80}\n")
    results = []
    for sid, fn, group in COLLECTORS:
        try:
            data, mode, source = fn()
            n = write_series(sid, data, source, mode)
            first = data[0]["week"] if data else "-"
            last = data[-1]["week"] if data else "-"
            status = "✅"
            note = f"{n}주 [{first} ~ {last}]"
            results.append({"signalId": sid, "group": group, "mode": mode, "weeks": n,
                            "rangeStart": first, "rangeEnd": last, "source": source, "status": "real"})
            print(f"  {status} {sid:12} {group:4} | {note:40} | {source[:55]}")
        except NotImplementedError as e:
            results.append({"signalId": sid, "group": group, "mode": "skipped",
                            "status": "skipped", "reason": str(e)})
            print(f"  ⏸  {sid:12} {group:4} | SKIPPED (paid/restricted)             | {str(e)[:70]}")
        except Exception as e:
            results.append({"signalId": sid, "group": group, "mode": "failed",
                            "status": "failed", "reason": str(e)})
            print(f"  ❌ {sid:12} {group:4} | FAILED                                 | {str(e)[:70]}")

    summary = {
        "backfilledAt": date.today().isoformat(),
        "rangeStart": START,
        "rangeEnd": END,
        "totalSignals": len(COLLECTORS),
        "collected": len([r for r in results if r["status"] == "real"]),
        "skipped": len([r for r in results if r["status"] == "skipped"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results,
    }
    (OUT_DIR / "_summary.json").write_text(json.dumps(summary, indent=2, default=str))

    print(f"\n{'═'*80}")
    print(f"  수집: {summary['collected']:2d} / 19  |  스킵(paid): {summary['skipped']:2d}  |  실패: {summary['failed']:2d}")
    print(f"  결과 위치: {OUT_DIR}")
    print(f"{'═'*80}\n")
    return summary


if __name__ == "__main__":
    main()
