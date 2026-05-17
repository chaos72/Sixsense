#!/usr/bin/env python3
"""Sixsense Phase 5e — 11개 미수집 신호의 자동 collector 모듈.

각 collector:
- 환경변수에서 자격증명 읽음 (없으면 인포한 에러 메시지)
- requests/boto3/google-cloud-bigquery/anthropic 등 적합한 클라이언트
- 결과를 [{week, value}] 표준 형식으로 반환

사용:
    .venv/bin/python3 pipelines/auto_collectors.py <signal_id>
    .venv/bin/python3 pipelines/auto_collectors.py --all

저장 위치: backend/data/historical/<signal_id>.json (backfill.py와 동일)
"""
import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
HIST_DIR = ROOT / "data" / "historical"
HIST_DIR.mkdir(parents=True, exist_ok=True)


def _load_dotenv(env_path: Path):
    """Minimal .env loader — 파일에서 환경변수 로드 (이미 설정된 값은 보존).
    프로젝트 루트 .env (Sixsense/.env)를 우선 사용.
    """
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        # 따옴표 제거
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        # 빈 값(또는 미설정)일 때만 .env로 덮어쓰기 — shell의 비어있는 변수 보호
        if k and not os.environ.get(k):
            os.environ[k] = v


# 프로젝트 루트 .env 우선, 그 다음 backend/.env (legacy)
_PROJECT_ROOT = ROOT.parent  # Sixsense/
_load_dotenv(_PROJECT_ROOT / ".env")
_load_dotenv(ROOT / ".env")  # backend/.env (있다면)

START = "2025-05-01"
END = "2026-04-30"
START_D = date.fromisoformat(START)
END_D = date.fromisoformat(END)


# ──────────────────────────────────────────────────────────────────────────────
# Common helpers
# ──────────────────────────────────────────────────────────────────────────────
def snap_to_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def write_signal(sid: str, data: list[dict], source: str, mode: str = "real") -> dict:
    payload = {
        "signalId": sid,
        "source": source,
        "mode": mode,
        "collectedAt": date.today().isoformat(),
        "rangeStart": data[0]["week"] if data else "-",
        "rangeEnd": data[-1]["week"] if data else "-",
        "note": f"Auto-collected via {Path(__file__).name}",
        "data": data,
    }
    out = HIST_DIR / f"{sid}.json"
    out.write_text(json.dumps(payload, indent=2, default=str))
    return {"weeks": len(data), "out": str(out)}


def monthly_to_weekly(monthly: list[tuple[date, float]]) -> list[dict]:
    """월간 데이터를 주간으로 forward-fill."""
    monthly = sorted(monthly)
    weeks = (END_D - START_D).days // 7 + 1
    out = []
    cur = 0
    for i in range(weeks):
        w = START_D + timedelta(weeks=i)
        while cur + 1 < len(monthly) and monthly[cur + 1][0] <= w:
            cur += 1
        if cur < len(monthly):
            out.append({"week": snap_to_monday(w).isoformat(), "value": round(monthly[cur][1], 4)})
    return out


def need_env(var: str, signup_url: str) -> str:
    val = os.getenv(var)
    if not val:
        raise EnvironmentError(
            f"환경변수 {var} 미설정. {signup_url} 에서 무료 발급 후:\n"
            f"  export {var}=your_key_here\n"
            f"또는 backend/.env 파일에 {var}=... 추가 후 다시 실행."
        )
    return val


# ──────────────────────────────────────────────────────────────────────────────
# B-4 지정학 리스크 (Caldara & Iacoviello GPR Index) — 키 불필요
# ──────────────────────────────────────────────────────────────────────────────
def collect_B4_gpr():
    """https://www.matteoiacoviello.com/gpr.htm → gpr_monthly_recent.csv (또는 gpr.csv)"""
    candidate_urls = [
        "https://www.matteoiacoviello.com/gpr_files/gpr_export.xls",
        "https://www.matteoiacoviello.com/gpr_files/gpr_monthly_recent.csv",
        "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls",
    ]
    raw = None
    used_url = None
    for url in candidate_urls:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and len(r.content) > 100:
                raw = r
                used_url = url
                break
        except requests.RequestException:
            continue
    if raw is None:
        raise RuntimeError("GPR CSV 다운로드 실패. URL 변경되었을 수 있음 → matteoiacoviello.com/gpr.htm 확인")

    monthly = []
    if used_url.endswith(".csv"):
        text = raw.text.strip().split("\n")
        for ln in text[1:]:
            parts = ln.split(",")
            if len(parts) < 2:
                continue
            try:
                ym = parts[0].strip()
                # ym format may be "2025-05" or "2025-05-01" or "May 2025"
                d = None
                for fmt in ("%Y-%m", "%Y-%m-%d", "%b-%Y", "%b %Y", "%Y%m"):
                    try:
                        d = datetime.strptime(ym, fmt).date()
                        break
                    except ValueError:
                        continue
                if d is None or not (START_D <= d <= END_D):
                    continue
                val = float(parts[1])
                monthly.append((d, val))
            except (ValueError, IndexError):
                continue
    else:
        # xls format — try parsing via pandas
        import pandas as pd
        from io import BytesIO
        df = pd.read_excel(BytesIO(raw.content))
        date_col = next((c for c in df.columns if "date" in c.lower() or "month" in c.lower()), df.columns[0])
        gpr_col = next((c for c in df.columns if "gpr" in c.lower() and "h" not in c.lower()[1:3]), df.columns[1])
        for _, row in df.iterrows():
            try:
                d = pd.to_datetime(row[date_col]).date()
                if not (START_D <= d <= END_D):
                    continue
                monthly.append((d, float(row[gpr_col])))
            except (ValueError, TypeError):
                continue

    if not monthly:
        raise RuntimeError(f"GPR 데이터 추출 실패 (사용 URL: {used_url})")

    data = monthly_to_weekly(monthly)
    return data, "real", f"Caldara & Iacoviello GPR Index ({used_url})"


# ──────────────────────────────────────────────────────────────────────────────
# B-7 BOM 신호 — Hacker News API (키 불필요)
# ──────────────────────────────────────────────────────────────────────────────
def collect_B7_bom_hn():
    """HN Algolia API — 'memory chip', 'HBM', 'DRAM' 관련 글의 주간 점수 합계."""
    queries = ["HBM memory", "DRAM price", "NVIDIA H100", "Apple silicon memory"]
    weekly_scores = defaultdict(float)
    weekly_counts = defaultdict(int)
    for q in queries:
        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": q,
            "tags": "story",
            "numericFilters": f"created_at_i>{int(datetime.fromisoformat(START).timestamp())},created_at_i<{int(datetime.fromisoformat(END).timestamp())}",
            "hitsPerPage": 200,
        }
        r = requests.get(url, params=params, timeout=30)
        if r.status_code != 200:
            continue
        j = r.json()
        for hit in j.get("hits", []):
            try:
                created = datetime.fromisoformat(hit["created_at"].replace("Z", "+00:00")).date()
                if not (START_D <= created <= END_D):
                    continue
                wk = snap_to_monday(created).isoformat()
                weekly_scores[wk] += hit.get("points", 0)
                weekly_counts[wk] += 1
            except (KeyError, ValueError):
                continue
        time.sleep(0.5)
    # Sum all weeks in range (zero-fill missing)
    weeks = (END_D - START_D).days // 7 + 1
    data = []
    for i in range(weeks):
        w = snap_to_monday(START_D + timedelta(weeks=i)).isoformat()
        data.append({"week": w, "value": round(weekly_scores[w], 2)})
    return data, "real", f"Hacker News Algolia API (queries: {len(queries)}건)"


# ──────────────────────────────────────────────────────────────────────────────
# A-6 Polymarket — 키 불필요 (시장 ID 검색)
# ──────────────────────────────────────────────────────────────────────────────
def collect_A6_manifold():
    """A-6 대안: Manifold Markets — 'China invades Taiwan by 2030' (vol 56만, 가장 활발).
    Polymarket history 비어있고 Metaculus API는 인증 요구로 변경됨 → Manifold로 전환.
    완전 공개 API, 키 불필요.
    """
    mid = "wENpa5mETtrCnBYJKl5t"
    question = "Will China launch a full-scale invasion of Taiwan before 2030?"

    all_bets = []
    before = None
    while True:
        params = {"contractId": mid, "limit": 1000}
        if before:
            params["before"] = before
        r = requests.get("https://api.manifold.markets/v0/bets", params=params, timeout=30)
        r.raise_for_status()
        bets = r.json()
        if not bets:
            break
        all_bets.extend(bets)
        before = bets[-1]["id"]  # manifold API는 bet ID 사용 (timestamp 아님)
        if len(bets) < 1000:
            break
        time.sleep(0.2)

    from collections import defaultdict
    from datetime import datetime
    weekly = defaultdict(list)
    for b in all_bets:
        t_ms = b.get("createdTime", 0)
        if not t_ms:
            continue
        d = datetime.fromtimestamp(t_ms / 1000).date()
        if not (START_D <= d <= END_D):
            continue
        wk = snap_to_monday(d).isoformat()
        prob = b.get("probAfter")
        if prob is not None:
            weekly[wk].append(prob)

    data = [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]
    if not data:
        raise RuntimeError(f"Manifold market {mid} bets 데이터 없음 (시장 신규 가능성)")
    return data, "real", f"Manifold Markets '{question}' ({len(all_bets)} bets → {len(data)}주)"


def collect_A6_polymarket():
    """(deprecated) Polymarket — history 비어있음. collect_A6_manifold 사용 권장."""
    search_url = "https://gamma-api.polymarket.com/markets"
    r = requests.get(search_url, params={"limit": 50, "active": "true", "closed": "false", "tag_id": "703"}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Polymarket markets API 실패: {r.status_code}")
    markets = r.json() if isinstance(r.json(), list) else r.json().get("markets", [])
    taiwan_markets = [m for m in markets if "taiwan" in (m.get("question", "") + m.get("description", "")).lower()]
    if not taiwan_markets:
        # Fallback: try without tag filter
        r2 = requests.get(search_url, params={"limit": 200, "q": "Taiwan"}, timeout=20)
        if r2.status_code == 200:
            markets = r2.json() if isinstance(r2.json(), list) else r2.json().get("markets", [])
            taiwan_markets = [m for m in markets if "taiwan" in (m.get("question", "") + m.get("description", "")).lower()]
    if not taiwan_markets:
        raise RuntimeError("Polymarket에 'Taiwan' 관련 active market 없음 (시간 따라 변동). Metaculus 대체 권장.")

    # Use first Taiwan market with longest history
    market = taiwan_markets[0]
    market_id = market.get("id") or market.get("conditionId")
    history_url = f"https://clob.polymarket.com/prices-history?market={market_id}&interval=1w&fidelity=10080"
    r = requests.get(history_url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Polymarket prices-history 실패: {r.status_code}")
    hist = r.json().get("history", [])
    weekly = defaultdict(list)
    for pt in hist:
        try:
            t = datetime.fromtimestamp(pt["t"]).date()
            if not (START_D <= t <= END_D):
                continue
            wk = snap_to_monday(t).isoformat()
            weekly[wk].append(pt["p"])
        except (KeyError, ValueError):
            continue
    data = [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]
    if not data:
        raise RuntimeError(f"Polymarket history 비어있음 (market_id={market_id})")
    return data, "real", f"Polymarket gamma+clob API (market: {market.get('question', market_id)[:60]})"


# ──────────────────────────────────────────────────────────────────────────────
# B-3 Reddit — PRAW (env var) 또는 HN 대체 (즉시)
# ──────────────────────────────────────────────────────────────────────────────
def collect_B3_reddit():
    """Reddit PRAW으로 r/hardware r/memorymarket 'memory price' 주간 게시물.
    환경변수 미설정 시 Hacker News 대체."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if client_id and client_secret:
        try:
            import praw
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="Sixsense Research v1.0",
            )
            weekly = defaultdict(int)
            for sub in ["hardware", "buildapc", "memorymarket"]:
                for post in reddit.subreddit(sub).search("memory price", sort="new", time_filter="year", limit=500):
                    created = datetime.fromtimestamp(post.created_utc).date()
                    if not (START_D <= created <= END_D):
                        continue
                    wk = snap_to_monday(created).isoformat()
                    weekly[wk] += 1
                time.sleep(1)
            weeks = (END_D - START_D).days // 7 + 1
            data = []
            for i in range(weeks):
                w = snap_to_monday(START_D + timedelta(weeks=i)).isoformat()
                data.append({"week": w, "value": weekly[w]})
            return data, "real", "Reddit PRAW (r/hardware + buildapc + memorymarket, 'memory price')"
        except ImportError:
            raise EnvironmentError("praw 패키지 미설치: pip install praw")
        except Exception as e:
            print(f"  ⚠️ Reddit PRAW 실패, HN 대체: {e}")

    # Fallback: Hacker News
    print("  ℹ️  REDDIT_CLIENT_ID/SECRET 미설정 → Hacker News 대체 사용")
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "query": "memory chip price",
        "tags": "story",
        "numericFilters": f"created_at_i>{int(datetime.fromisoformat(START).timestamp())},created_at_i<{int(datetime.fromisoformat(END).timestamp())}",
        "hitsPerPage": 500,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()
    weekly = defaultdict(int)
    for hit in j.get("hits", []):
        try:
            created = datetime.fromisoformat(hit["created_at"].replace("Z", "+00:00")).date()
            if not (START_D <= created <= END_D):
                continue
            wk = snap_to_monday(created).isoformat()
            weekly[wk] += 1
        except (KeyError, ValueError):
            continue
    weeks = (END_D - START_D).days // 7 + 1
    data = []
    for i in range(weeks):
        w = snap_to_monday(START_D + timedelta(weeks=i)).isoformat()
        data.append({"week": w, "value": weekly[w]})
    return data, "real", "Hacker News Algolia ('memory chip price') — Reddit 대체"


# ──────────────────────────────────────────────────────────────────────────────
# A-3 관세청 수출 — KCS_API_KEY 필요
# ──────────────────────────────────────────────────────────────────────────────
def collect_A3_kcs():
    """관세청 무역통계 API (data.go.kr) — HS 854232 (메모리) 월별 수출액.

    엔드포인트: https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList
    HS 코드 정정 (관세청조회코드 Excel 기준):
      - 854231 = 프로세서/컨트롤러 (잘못된 코드, 이전에 사용)
      - 854232 = 메모리 ← 정확
      - 8542321010 = 디램 (DRAM) ← 가장 세부
    파라미터 정정:
      - imexTpcd: 수출입구분 (1=수출, 2=수입)
    """
    key = need_env("KCS_API_KEY", "https://www.data.go.kr (활용신청 → Itemtrade 서비스)")
    base_url = os.getenv("KCS_API_URL", "https://apis.data.go.kr/1220000/Itemtrade")
    full_url = f"{base_url}/getItemtradeList"
    monthly = []
    for year in (2025, 2026):
        for month in range(1, 13):
            if year == 2025 and month < 5:
                continue
            if year == 2026 and month > 4:
                break
            ym = f"{year}{month:02d}"
            params = {
                "serviceKey": key,
                "strtYymm": ym,
                "endYymm": ym,
                "hsSgn": "854232",     # 메모리 (이전 854231=프로세서 오류)
                "imexTpcd": "1",       # 수출 (이전 expoImpoTp 잘못된 파라미터명)
                "type": "json",
            }
            try:
                r = requests.get(full_url, params=params, timeout=30)
                if r.status_code == 401:
                    raise RuntimeError(
                        f"data.go.kr 401 Unauthorized — 다음 중 하나일 가능성:\n"
                        f"  (1) Itemtrade 서비스 활용신청 미승인 (data.go.kr 마이페이지 확인)\n"
                        f"  (2) 신청 후 활성화 대기 중 (보통 1~2시간 소요)\n"
                        f"  (3) encoding/decoding 키 혼동 — 마이페이지에서 두 종류 확인"
                    )
                r.raise_for_status()
                # JSON 응답 우선 시도
                try:
                    j = r.json()
                    items = j.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if isinstance(items, dict):
                        items = [items]
                    if items:
                        amt = float(items[0].get("expDlr", 0))
                        d = date(year, month, 1)
                        monthly.append((d, amt))
                except (ValueError, KeyError):
                    # XML fallback
                    from xml.etree import ElementTree as ET
                    root = ET.fromstring(r.text)
                    for item in root.iter("item"):
                        amt_el = item.find("expDlr")
                        if amt_el is not None and amt_el.text:
                            monthly.append((date(year, month, 1), float(amt_el.text)))
                            break
            except RuntimeError:
                raise
            except Exception as e:
                print(f"  ⚠️ {ym} 실패: {str(e)[:80]}")
            time.sleep(0.3)
    if not monthly:
        raise RuntimeError(
            "관세청 API 응답에서 데이터 추출 실패. "
            "data.go.kr 마이페이지에서 Itemtrade 서비스 활성화 상태 확인 필요."
        )
    data = monthly_to_weekly(monthly)
    return data, "real", f"관세청 data.go.kr Itemtrade HS 854232 (메모리) 월간 수출 ({len(monthly)}개월, USD)"


# ──────────────────────────────────────────────────────────────────────────────
# A-4 KOSIS 재고/출하 지수 — KOSIS_API_KEY 필요
# ──────────────────────────────────────────────────────────────────────────────
def collect_A4_kosis():
    """KOSIS 광공업동향조사 — 전자부품(C26) 재고지수 월간.

    3가지 방식 지원 (우선순위 순):
    1. KOSIS_USER_STATS_ID — 사용자가 KOSIS 사이트에서 만든 사용자정의표 ID (가장 간단)
    2. KOSIS_FULL_URL — KOSIS 사이트의 'URL 생성기'로 만든 전체 URL
    3. (기본) 하드코드된 표 + objL1/itmId (사용자 등록 표과 일치해야 함)
    """
    key = need_env("KOSIS_API_KEY", "https://kosis.kr/openapi")

    # 방식 1: 사용자 통계작성 ID (가장 안정적)
    user_stats_id = os.getenv("KOSIS_USER_STATS_ID")
    if user_stats_id:
        url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
        params = {
            "method": "getList", "apiKey": key, "format": "json", "jsonVD": "Y",
            "userStatsId": user_stats_id,
            "prdSe": "M",
            "startPrdDe": "202505", "endPrdDe": "202604",
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        arr = r.json()
    elif os.getenv("KOSIS_FULL_URL"):
        # 방식 2: 사용자가 KOSIS URL 생성기로 만든 URL 직접 사용
        r = requests.get(os.environ["KOSIS_FULL_URL"], timeout=30)
        r.raise_for_status()
        arr = r.json()
    else:
        # 방식 3: 기본 시도 (사용자 등록 표과 일치해야 함)
        url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
        params = {
            "method": "getList", "apiKey": key, "format": "json", "jsonVD": "Y",
            "itmId": "T20", "objL1": "13102641",
            "prdSe": "M", "startPrdDe": "202505", "endPrdDe": "202604",
            "orgId": "101", "tblId": "DT_1F02012",
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        arr = r.json()

    if not isinstance(arr, list) or not arr:
        raise RuntimeError(
            f"KOSIS 응답 비어있음 또는 오류: {arr}\n"
            f"→ KOSIS_USER_STATS_ID 또는 KOSIS_FULL_URL 사용 권장. "
            f"가이드: docs/09-data-acquisition/kosis-url-generation.md"
        )
    monthly = []
    for row in arr:
        try:
            prd = row.get("PRD_DE", "")  # YYYYMM
            val = float(row.get("DT", 0))
            d = date(int(prd[:4]), int(prd[4:]), 1)
            monthly.append((d, val))
        except (ValueError, KeyError):
            continue
    if not monthly:
        raise RuntimeError("KOSIS 데이터 파싱 실패")
    data = monthly_to_weekly(monthly)
    return data, "real", "KOSIS 광공업동향 C26 재고지수 (월간→주간 forward-fill)"


# ──────────────────────────────────────────────────────────────────────────────
# A-5 AWS Spot 가격 — AWS IAM 키 필요
# ──────────────────────────────────────────────────────────────────────────────
def collect_A5_aws_spot():
    """AWS describe_spot_price_history — m6i.xlarge 90일 history."""
    aws_key = need_env("AWS_ACCESS_KEY_ID", "https://console.aws.amazon.com/iam (계정 → IAM → Access keys, 무료)")
    _ = need_env("AWS_SECRET_ACCESS_KEY", "(위와 함께 발급되는 secret)")
    try:
        import boto3
    except ImportError:
        raise EnvironmentError("boto3 미설치: pip install boto3")
    ec2 = boto3.client("ec2", region_name="us-east-1")
    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(days=90)
    paginator = ec2.get_paginator("describe_spot_price_history")
    pages = paginator.paginate(
        InstanceTypes=["m6i.xlarge"],
        ProductDescriptions=["Linux/UNIX"],
        StartTime=start_dt,
        EndTime=end_dt,
        AvailabilityZone="us-east-1a",
    )
    weekly = defaultdict(list)
    for page in pages:
        for entry in page["SpotPriceHistory"]:
            d = entry["Timestamp"].date()
            if not (START_D <= d <= END_D):
                continue
            wk = snap_to_monday(d).isoformat()
            weekly[wk].append(float(entry["SpotPrice"]))
    data = [{"week": w, "value": round(sum(v) / len(v), 6)} for w, v in sorted(weekly.items())]
    if not data:
        raise RuntimeError("AWS Spot history 비어있음")
    return data, "real", "AWS EC2 m6i.xlarge spot (us-east-1a, 최대 90일)"


# ──────────────────────────────────────────────────────────────────────────────
# B-2 GDELT BigQuery (대만 뉴스 감성)
# ──────────────────────────────────────────────────────────────────────────────
def collect_B2_rss_sentiment():
    """B-2: TechNews.tw + Digitimes RSS 피드 → 서버/메모리 헤드라인 sentiment.

    GDELT BigQuery 대안 — GCP credentials 불필요.
    feedparser로 RSS 파싱, 키워드 기반 sentiment (기본).
    ANTHROPIC_API_KEY + 크레딧 있으면 Claude로 정확한 sentiment 옵션 활성화.
    """
    try:
        import feedparser
    except ImportError:
        raise EnvironmentError("feedparser 미설치: pip install feedparser")

    # 1. Topic-specific RSS (대만 기술 매체)
    RSS_FEEDS = [
        "https://technews.tw/category/semiconductor/feed/",
        "https://technews.tw/category/ai/feed/",
        "https://technews.tw/feed/",
        "https://www.digitimes.com.tw/rss/news.xml",
    ]
    # 2. Google News RSS 검색 (메모리/반도체 키워드, 키 불필요)
    GOOGLE_NEWS_QUERIES = [
        ("Taiwan semiconductor", "en"),
        ("DRAM memory price", "en"),
        ("HBM Nvidia", "en"),
        ("Samsung memory", "en"),
        ("SK Hynix HBM", "en"),
        ("Micron DRAM", "en"),
        ("AI server memory demand", "en"),
        ("半導體 台灣", "zh-TW"),
        ("記憶體 DRAM", "zh-TW"),
    ]
    for q, lang in GOOGLE_NEWS_QUERIES:
        url = (
            f"https://news.google.com/rss/search?"
            f"q={q.replace(' ', '+')}&hl={lang}-US&gl=US&ceid=US:{lang.split('-')[0]}"
        )
        RSS_FEEDS.append(url)

    # 서버/메모리 관련 헤드라인 필터 (한자/영어)
    TOPIC_KEYWORDS = [
        "伺服器", "記憶體", "半導體", "DRAM", "HBM", "NAND", "SSD",
        "AI", "輝達", "Nvidia", "三星", "Samsung", "海力士", "SK", "美光", "Micron",
        "晶片", "chip", "memory", "server", "semiconductor", "fab",
    ]
    # 긍정/부정 키워드 (간단 lexicon)
    POS = ["增長", "上漲", "上揚", "增加", "強勁", "熱絡", "暢旺", "突破", "創新高",
           "狂潮", "革命", "獲利", "強勢", "超車", "躍升", "成長",
           "growth", "surge", "boost", "shortage", "rally", "soar", "expand", "bullish"]
    NEG = ["下跌", "減少", "萎縮", "弱勢", "疲軟", "庫存過剩", "拒買", "管制", "禁令",
           "decline", "drop", "weak", "oversupply", "ban", "restrict", "bearish", "slump"]

    from collections import defaultdict
    from datetime import datetime
    import time as _t

    all_entries = []
    for url in RSS_FEEDS:
        try:
            f = feedparser.parse(url)
            for e in f.entries:
                pub = e.get("published_parsed") or e.get("updated_parsed")
                if not pub:
                    continue
                d = date(pub.tm_year, pub.tm_mon, pub.tm_mday)
                # RSS는 보통 최근 4~30일만 제공 — END_D(2026-04-30) 무시하고 START_D 이상만
                # 운영 시 매주 cron으로 누적 → 1년 차에 완전 history
                if d < START_D:
                    continue
                title = e.get("title", "") or ""
                summary = e.get("summary", "") or ""
                text = (title + " " + summary)[:500]
                if not any(kw.lower() in text.lower() for kw in TOPIC_KEYWORDS):
                    continue
                all_entries.append({"date": d, "title": title, "text": text})
        except Exception as e:
            print(f"  ⚠️ {url[:50]}: {str(e)[:60]}")
        _t.sleep(0.2)

    if not all_entries:
        raise RuntimeError("RSS 토픽 매칭 entries 0건")

    # 키워드 기반 sentiment (-1 ~ +1)
    def kw_sentiment(text: str) -> float:
        low = text.lower()
        pos = sum(1 for k in POS if k.lower() in low)
        neg = sum(1 for k in NEG if k.lower() in low)
        if pos + neg == 0:
            return 0.0
        return round((pos - neg) / (pos + neg), 3)

    # 주별 집계: count + avg sentiment
    weekly = defaultdict(list)
    for ent in all_entries:
        wk = snap_to_monday(ent["date"]).isoformat()
        weekly[wk].append(kw_sentiment(ent["text"]))

    # value = count × avg_sentiment (수량 + 방향 결합 지표)
    # 또는 단순 avg_sentiment 만 사용 가능
    data = []
    for wk in sorted(weekly):
        scores = weekly[wk]
        n = len(scores)
        avg = sum(scores) / n
        # 결합 점수: avg sentiment 그대로 (count로 가중하면 0 sentiment 주가 사라짐)
        data.append({"week": wk, "value": round(avg, 4)})

    return data, "real", (
        f"TechNews.tw + Digitimes + Google News RSS ({len(all_entries)} entries, "
        f"키워드 sentiment, {len(data)}주)"
    )


def collect_B2_gdelt_bq():
    """GDELT BigQuery — 1TB/월 free, 대만 반도체 뉴스 주간 볼륨."""
    creds = need_env(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "https://console.cloud.google.com → IAM → Service Accounts → JSON 다운로드 (BigQuery 권한)",
    )
    try:
        from google.cloud import bigquery
    except ImportError:
        raise EnvironmentError("google-cloud-bigquery 미설치: pip install google-cloud-bigquery")
    client = bigquery.Client.from_service_account_json(creds)
    query = """
    SELECT
      DATE_TRUNC(DATE(_PARTITIONTIME), WEEK(MONDAY)) AS week,
      COUNT(*) AS article_count
    FROM `gdelt-bq.gdeltv2.events_partitioned`
    WHERE _PARTITIONTIME BETWEEN '2025-05-01' AND '2026-04-30'
      AND (Actor1CountryCode = 'TWN' OR Actor2CountryCode = 'TWN')
      AND THEMES LIKE '%TECH_%'
    GROUP BY week
    ORDER BY week
    """
    res = client.query(query).result()
    data = []
    for row in res:
        wk = snap_to_monday(row["week"]).isoformat()
        data.append({"week": wk, "value": int(row["article_count"])})
    if not data:
        raise RuntimeError("GDELT BigQuery 결과 비어있음")
    return data, "real", "GDELT BigQuery events_partitioned (TWN actor + TECH theme)"


# ──────────────────────────────────────────────────────────────────────────────
# B-1, B-5, B-6 — Claude API + IR PDF 자동 분석
# ──────────────────────────────────────────────────────────────────────────────
SAMSUNG_IR_URLS = [
    # 분기당 1개씩, 총 5개 (Q2-25, Q3-25, Q4-25, Q1-26, Q2-26 일부)
    "https://www.samsung.com/global/ir/financial-information/earnings-release/",
]
SKHYNIX_IR_URLS = ["https://www.skhynix.com/eng/ir/earningsRelease.do"]
MICRON_IR_URLS = ["https://investors.micron.com/financial-information/quarterly-results"]


def _llm_sentiment(text: str, prompt_topic: str) -> float:
    """LLM 기반 sentiment (-1~+1). 우선순위: Anthropic → Gemini → Groq.
    셋 다 키 없으면 EnvironmentError.
    """
    prompt = (
        f"다음 텍스트는 메모리 반도체 회사의 IR 자료다. {prompt_topic}에 대한 sentiment를 "
        f"-1 (매우 부정) ~ +1 (매우 긍정) 사이 한 개의 숫자로만 답변하라. 다른 설명 금지.\n\n"
        f"<text>\n{text[:8000]}\n</text>"
    )

    # ── 1순위: Anthropic Claude (크레딧 있을 때) ──
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 32,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
            if r.status_code == 200:
                txt = r.json()["content"][0]["text"].strip()
                m = re.search(r"-?\d+\.?\d*", txt)
                if m:
                    return max(-1.0, min(1.0, float(m.group())))
            elif r.status_code == 400 and "credit balance" in r.text.lower():
                print(f"    Anthropic 크레딧 부족 → Gemini fallback")
        except Exception as e:
            print(f"    Anthropic 실패, fallback: {str(e)[:50]}")

    # ── 2순위: Google Gemini (무료 1500 req/day) ──
    gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    if gemini_key:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 32, "temperature": 0.0},
                },
                timeout=60,
            )
            if r.status_code == 200:
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                m = re.search(r"-?\d+\.?\d*", txt)
                if m:
                    return max(-1.0, min(1.0, float(m.group())))
            else:
                print(f"    Gemini HTTP {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"    Gemini 실패, fallback: {str(e)[:50]}")

    # ── 3순위: Groq (무료 14400 req/day) ──
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 32,
                    "temperature": 0.0,
                },
                timeout=60,
            )
            if r.status_code == 200:
                txt = r.json()["choices"][0]["message"]["content"].strip()
                m = re.search(r"-?\d+\.?\d*", txt)
                if m:
                    return max(-1.0, min(1.0, float(m.group())))
        except Exception as e:
            print(f"    Groq 실패: {str(e)[:50]}")

    raise EnvironmentError(
        "LLM sentiment API 키 미설정 또는 모두 실패.\n"
        "다음 중 하나를 .env에 추가 (모두 무료):\n"
        "  - GEMINI_API_KEY=... (https://ai.google.dev — 무료 1500 req/day, 권장)\n"
        "  - GROQ_API_KEY=...   (https://console.groq.com — 무료 14400 req/day)\n"
        "  - ANTHROPIC_API_KEY=... + Billing 크레딧 (https://console.anthropic.com)"
    )


# Backwards-compat alias
_claude_sentiment = _llm_sentiment


def _collect_ir_news_sentiment(prompt_topic: str, source_label: str) -> tuple[list[dict], str, str]:
    """B-1/B-5/B-6 공통 파이프라인: Google News에서 메모리社 IR/실적 헤드라인 → LLM sentiment.
    PDF 다운로드 + 추출은 회사별 IR 페이지 구조가 자주 바뀌어 불안정 → 뉴스 헤드라인으로 우회.
    """
    import feedparser
    from collections import defaultdict
    from datetime import datetime

    # 메모리社 실적/IR 뉴스 검색
    queries = [
        f"Samsung memory {prompt_topic}",
        f"SK Hynix {prompt_topic}",
        f"Micron {prompt_topic}",
    ]
    entries = []
    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
        f = feedparser.parse(url)
        for e in f.entries[:60]:
            pub = e.get("published_parsed") or e.get("updated_parsed")
            if not pub:
                continue
            d = date(pub.tm_year, pub.tm_mon, pub.tm_mday)
            if d < START_D:
                continue
            entries.append({
                "date": d,
                "text": ((e.get("title") or "") + " " + (e.get("summary") or ""))[:600],
            })
        time.sleep(0.3)

    if not entries:
        raise RuntimeError(f"{source_label} 뉴스 entries 0건")

    # 주별 그룹 → 주당 1~2개 대표 entries만 LLM 호출 (rate 한도 보호)
    weekly_text = defaultdict(list)
    for ent in entries:
        wk = snap_to_monday(ent["date"]).isoformat()
        weekly_text[wk].append(ent["text"])

    weekly_score = []
    n_llm_calls = 0
    for wk in sorted(weekly_text):
        texts = weekly_text[wk]
        # 주별 헤드라인 5개 합쳐서 1회 호출
        combined = "\n---\n".join(texts[:5])
        try:
            score = _llm_sentiment(combined, prompt_topic)
            n_llm_calls += 1
            weekly_score.append({"week": wk, "value": round(score, 4)})
        except EnvironmentError:
            # 키 전혀 없으면 keyword fallback
            POS = ["growth", "surge", "boost", "demand", "expand", "increase", "strong", "record"]
            NEG = ["decline", "drop", "weak", "fall", "cut", "decrease", "loss", "miss"]
            low = combined.lower()
            pos = sum(1 for k in POS if k in low)
            neg = sum(1 for k in NEG if k in low)
            score = 0.0 if pos+neg==0 else (pos-neg)/(pos+neg)
            weekly_score.append({"week": wk, "value": round(score, 4)})

    mode = "real" if n_llm_calls > 0 else "real-keyword"
    src = f"Google News '{source_label}' ({len(entries)} entries, "
    src += f"LLM {n_llm_calls}회 호출, {len(weekly_score)}주)" if n_llm_calls > 0 \
        else f"키워드 fallback, {len(weekly_score)}주)"
    return weekly_score, mode, src


def collect_B1_earnings_sentiment():
    """B-1: 메모리社 실적 발표 sentiment (Google News + LLM)."""
    return _collect_ir_news_sentiment(
        prompt_topic="quarterly earnings memory pricing outlook",
        source_label="Earnings Call sentiment",
    )


def collect_B5_lta_sentiment():
    """B-5: LTA (장기 계약) 비율 관련 뉴스 sentiment."""
    return _collect_ir_news_sentiment(
        prompt_topic="long-term agreement LTA contract memory supply ratio",
        source_label="LTA ratio",
    )


def collect_B6_hbm_mix():
    """B-6: HBM 매출 비중 관련 뉴스 sentiment."""
    return _collect_ir_news_sentiment(
        prompt_topic="HBM revenue mix share growth high bandwidth memory",
        source_label="HBM mix",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Registry + main
# ──────────────────────────────────────────────────────────────────────────────
COLLECTORS = {
    "A-3": collect_A3_kcs,
    "A-4": collect_A4_kosis,
    "A-5": collect_A5_aws_spot,
    "A-6": collect_A6_manifold,
    "B-1": collect_B1_earnings_sentiment,
    "B-2": collect_B2_rss_sentiment,
    "B-3": collect_B3_reddit,
    "B-4": collect_B4_gpr,
    "B-5": collect_B5_lta_sentiment,
    "B-6": collect_B6_hbm_mix,
    "B-7": collect_B7_bom_hn,
}


def run_one(sid: str) -> dict:
    fn = COLLECTORS.get(sid)
    if not fn:
        return {"signalId": sid, "status": "unknown"}
    try:
        data, mode, source = fn()
        r = write_signal(sid, data, source, mode)
        return {"signalId": sid, "status": "ok", "weeks": r["weeks"], "source": source}
    except (NotImplementedError, EnvironmentError) as e:
        return {"signalId": sid, "status": "needs_setup", "reason": str(e)}
    except Exception as e:
        return {"signalId": sid, "status": "failed", "reason": str(e)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("signal_id", nargs="?")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()
    targets = list(COLLECTORS.keys()) if args.all else ([args.signal_id] if args.signal_id else [])
    if not targets:
        p.print_help()
        sys.exit(1)
    print(f"\n{'═'*72}\n  Phase 5e Auto-collectors\n{'═'*72}\n")
    for sid in targets:
        r = run_one(sid)
        if r["status"] == "ok":
            print(f"  ✅ {sid:5} {r['weeks']:3}주  | {r['source'][:60]}")
        elif r["status"] == "needs_setup":
            first_line = r["reason"].split("\n")[0]
            print(f"  ⏸  {sid:5} 설정 필요 | {first_line[:60]}")
        else:
            print(f"  ❌ {sid:5} 실패     | {r['reason'][:60]}")
    print()


if __name__ == "__main__":
    main()
