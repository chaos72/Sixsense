#!/usr/bin/env python3
"""Sixsense Phase 5e — 11개 미수집 신호의 자동 collector 모듈.

각 collector:
- 환경변수에서 자격증명 읽음 (없으면 인포한 에러 메시지)
- requests/boto3 등 적합한 클라이언트 (LLM 은 Gemini 무료 티어 단독 — gemini_client)
- 결과를 [{week, value}] 표준 형식으로 반환

사용:
    .venv/bin/python3 pipelines/auto_collectors.py <signal_id>
    .venv/bin/python3 pipelines/auto_collectors.py --all

저장 위치: backend/data/historical/<signal_id>.json (backfill.py와 동일)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

from gemini_client import BULK_MODELS, gemini_generate

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

# USER-REQUESTED EXTENSION (#18, 2026-06-11) — START/END 동적화 (1년 롤링 윈도우).
# 이전엔 END="2026-04-30" 하드코딩이라 그 이후 Yahoo/FRED 데이터가 필터링됨.
# 환경변수로 오버라이드 가능 (SIXSENSE_START / SIXSENSE_END), 미지정 시 today 기준 최근 1년.
from datetime import timedelta as _td
# 기준 날짜는 UTC — 한국 월요일 새벽(UTC 로는 일요일)에 돌려도 끝나지 않은 주를 마감하지 않게 (v2.5)
END_D = date.fromisoformat(os.getenv("SIXSENSE_END")) if os.getenv("SIXSENSE_END") else datetime.now(timezone.utc).date()
START_D = date.fromisoformat(os.getenv("SIXSENSE_START")) if os.getenv("SIXSENSE_START") else (END_D - _td(weeks=56))
START = START_D.isoformat()
END = END_D.isoformat()


# ──────────────────────────────────────────────────────────────────────────────
# Common helpers
# ──────────────────────────────────────────────────────────────────────────────
def snap_to_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def write_signal(sid: str, data: list[dict], source: str, mode: str = "real",
                 frozen: dict | None = None) -> dict:
    payload = {
        "signalId": sid,
        "source": source,
        "mode": mode,
        "collectedAt": date.today().isoformat(),
        "rangeStart": data[0]["week"] if data else "-",
        "rangeEnd": data[-1]["week"] if data else "-",
        "note": f"Auto-collected via {Path(__file__).name}",
        **(frozen or {}),
        "data": data,
    }
    out = HIST_DIR / f"{sid}.json"
    out.write_text(json.dumps(payload, indent=2, default=str))
    return {"weeks": len(data), "out": str(out)}


# ──────────────────────────────────────────────────────────────────────────────
# 주 단위 고정 (v2.3.2) — 다시 가져오면 과거 값이 달라지는 원천(뉴스 검색·LLM 채점·
# 예측시장·HN 추천수)은 끝난 주를 한 번 마감하면 다시 고치지 않는다.
# 가계부처럼: 지난 주 칸은 마감, 진행 중인 주 칸만 계속 적는다.
# Yahoo·FRED·공식 통계는 기관의 수정 발표를 반영해야 하므로 대상이 아니다.
# ──────────────────────────────────────────────────────────────────────────────
FREEZE_SIGNALS = {"A-5", "A-6", "B-1", "B-2", "B-3", "B-5", "B-6", "B-7"}


def _last_completed_week() -> str:
    """실행일 기준 이미 끝난 마지막 주(월요일). 예: 2026-09-24(목) → 2026-09-14."""
    return (snap_to_monday(END_D) - timedelta(weeks=1)).isoformat()


def _load_existing(sid: str) -> dict | None:
    f = HIST_DIR / f"{sid}.json"
    return json.loads(f.read_text()) if f.exists() else None


def _final_through(sid: str) -> str | None:
    """이 신호에서 이미 마감된 마지막 주. 기존 파일이 있는데 마감선이 없으면(첫 적용)
    지금 파일의 끝난 주들을 그대로 마감한다."""
    old = _load_existing(sid)
    if not old or not old.get("data"):
        return None
    return old.get("finalThrough") or _last_completed_week()


RETRY_WEEKS = 4   # 값이 비어 있는 주는 마감 후 이 주수 동안 다시 채울 수 있다 (주 1회 실행 → 4번의 재시도)


def _open_week_test(sid: str):
    """이 신호에서 '다시 계산해도 되는 주'인지 판정하는 함수를 돌려준다. 합치기와 AI 채점이 같은 판정을 쓴다.
    - 마감선 이후의 주 → 계산
    - 마감선 이하이지만 값이 비어 있고 마감 후 RETRY_WEEKS 주 이내 → 다시 채움 (일시적 실패로 영구 빈칸 방지)
    - 값이 있는 마감된 주 → 절대 다시 계산하지 않음"""
    old = _load_existing(sid) or {}
    ft = _final_through(sid)
    have = {r["week"] for r in old.get("data", [])}
    retry_from = (date.fromisoformat(ft) - timedelta(weeks=RETRY_WEEKS - 1)).isoformat() if ft else None

    def is_open(week: str) -> bool:
        return not ft or week > ft or (week not in have and week >= retry_from)
    return is_open


def _merge_frozen(sid: str, new_data: list[dict]) -> tuple[list[dict], dict]:
    """마감된 주(≤ finalThrough)의 기존 값은 그대로 — 새로 계산된 값이 와도 무시.
    마감선 이후 주와, 마감 후 RETRY_WEEKS 주 이내의 '빈 주'만 새 값을 쓰고, 마감선을 '끝난 마지막 주'까지 올린다."""
    old = _load_existing(sid) or {}
    ft = _final_through(sid)
    is_open = _open_week_test(sid)
    kept = [r for r in old.get("data", []) if ft and r["week"] <= ft]
    fresh = [r for r in new_data if is_open(r["week"])]
    merged = sorted(kept + fresh, key=lambda r: r["week"])
    new_ft = max(ft or "", _last_completed_week())
    since = old.get("frozenSince") or new_ft
    return merged, {
        "finalThrough": new_ft,
        "frozenSince": since,
        "freezeNote": (f"{since} 까지의 값은 고정 도입 전 사후 일괄 계산값. "
                       "이후 주는 그 주가 끝난 직후 한 번 계산해 고정."),
    }


def _utc_ts(iso: str) -> int:
    """날짜 문자열 → UTC 기준 초. 컴퓨터 현지 시간(한국 KST)에 따라 주 경계가 어긋나지 않게."""
    return int(datetime.fromisoformat(iso).replace(tzinfo=timezone.utc).timestamp())


def need_env(var: str, signup_url: str) -> str:
    val = os.getenv(var)
    if not val:
        raise EnvironmentError(
            f"환경변수 {var} 미설정. {signup_url} 에서 무료 발급 후:\n"
            f"  export {var}=your_key_here\n"
            f"또는 backend/.env 파일에 {var}=... 추가 후 다시 실행."
        )
    return val


def _history_months() -> list[tuple[int, int]]:
    """대상 지수 시작 월(HISTORY_START)부터 실행 월까지 (연, 월) 목록 — 조회 기간을 코드에 고정하지 않는다.
    (이전엔 A-3 이 2025-05~2026-04 로 고정돼 5월 이후 발표분을 가져오지 못했음)"""
    y, m = int(HISTORY_START[:4]), int(HISTORY_START[5:7])
    out = []
    while (y, m) <= (END_D.year, END_D.month):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


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
                if d is None or not (_history_months()[0] <= (d.year, d.month) <= _history_months()[-1]):
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
                if not (_history_months()[0] <= (d.year, d.month) <= _history_months()[-1]):
                    continue
                monthly.append((d, float(row[gpr_col])))
            except (ValueError, TypeError):
                continue

    if not monthly:
        raise RuntimeError(f"GPR 데이터 추출 실패 (사용 URL: {used_url})")

    data = _ffill_monthly_to_weekly(monthly)
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
            "numericFilters": f"created_at_i>{_utc_ts(START)},created_at_i<{_utc_ts(END)}",
            "hitsPerPage": 200,
        }
        r = requests.get(url, params=params, timeout=30)
        # 한 검색어라도 실패하면 오류로 끝낸다 — 일부만 모인 합계가 마감되어 영구히 남지 않도록 (v2.5)
        r.raise_for_status()
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
        if w > _last_completed_week():   # 진행 중인 주 제외 — 개수·점수 합은 주가 끝나야 의미 (v2.5)
            continue
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
        d = datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).date()
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
                    created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc).date()
                    if not (START_D <= created <= END_D):
                        continue
                    wk = snap_to_monday(created).isoformat()
                    weekly[wk] += 1
                time.sleep(1)
            weeks = (END_D - START_D).days // 7 + 1
            data = []
            for i in range(weeks):
                w = snap_to_monday(START_D + timedelta(weeks=i)).isoformat()
                if w > _last_completed_week():
                    continue
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
        "numericFilters": f"created_at_i>{_utc_ts(START)},created_at_i<{_utc_ts(END)}",
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
        if w > _last_completed_week():   # 진행 중인 주 제외 — 개수·점수 합은 주가 끝나야 의미 (v2.5)
            continue
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
    net_errors = 0
    for year, month in _history_months():
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
                    "data.go.kr 401 Unauthorized — 다음 중 하나일 가능성:\n"
                    "  (1) Itemtrade 서비스 활용신청 미승인 (data.go.kr 마이페이지 확인)\n"
                    "  (2) 신청 후 활성화 대기 중 (보통 1~2시간 소요)\n"
                    "  (3) encoding/decoding 키 혼동 — 마이페이지에서 두 종류 확인"
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
            if isinstance(e, requests.exceptions.RequestException):
                net_errors += 1
        time.sleep(0.3)
    if not monthly and net_errors:
        # 모든 달이 연결 실패면 설정 문제가 아니라 네트워크(해외 IP 차단 등) — 원인을 정확히 보고 (v2.5.1)
        raise requests.exceptions.ConnectionError(
            f"관세청 연결 실패 {net_errors}개월 — 해외 IP 차단 가능성, 한국에서 로컬 수집으로 보충")
    if not monthly:
        raise RuntimeError(
            "관세청 API 응답에서 데이터 추출 실패. "
            "data.go.kr 마이페이지에서 Itemtrade 서비스 활성화 상태 확인 필요."
        )
    data = _ffill_monthly_to_weekly(monthly)
    return data, "real", f"관세청 data.go.kr Itemtrade HS 854232 (메모리) 월간 수출 ({len(monthly)}개월, USD)"


# ──────────────────────────────────────────────────────────────────────────────
# A-4 KOSIS 반도체 재고지수 — KOSIS_API_KEY 필요
# ──────────────────────────────────────────────────────────────────────────────
# v2.5.1: 조회 조건(비밀 아님)을 코드에 고정하고 키만 환경변수에서 읽는다.
# 이전 KOSIS_FULL_URL 은 반도체가 없는 '품목별 광공업 생산·출하량' 표를 가리켜 임의 행이 저장됐었음.
KOSIS_A4_QUERY = {
    "orgId": "101", "tblId": "DT_1F02001",   # 광업제조업동향조사 · 시도/산업별 광공업생산지수(2020=100)
    "itmId": "T12",                          # 생산자제품 재고지수(원지수)
    "objL1": "00",                           # 전국
    "objL2": "C261",                         # 반도체 제조업
    "prdSe": "M",
}


def collect_A4_kosis():
    """KOSIS — 반도체 제조업(C261) 생산자제품 재고지수(원지수, 2020=100), 월간.
    응답이 이 지표가 아니면(달마다 1행이 아니거나 항목·업종 이름이 다르면) 오류로 끝내 기존 파일을 유지한다."""
    key = need_env("KOSIS_API_KEY", "https://kosis.kr/openapi")
    months = _history_months()
    params = {"method": "getList", "apiKey": key, "format": "json", "jsonVD": "Y", **KOSIS_A4_QUERY,
              "startPrdDe": f"{months[0][0]}{months[0][1]:02d}",
              "endPrdDe": f"{months[-1][0]}{months[-1][1]:02d}"}
    r = requests.get("https://kosis.kr/openapi/Param/statisticsParameterData.do", params=params, timeout=60)
    r.raise_for_status()
    arr = r.json()
    if not isinstance(arr, list) or not arr:
        raise RuntimeError(f"KOSIS 응답 비어있음 또는 오류: {str(arr)[:120]}")

    # 응답 검사 — 같은 사고(엉뚱한 표의 임의 행 저장) 재발 방지
    names = {(row.get("ITM_NM", ""), row.get("C2_NM", "")) for row in arr}
    if not all("재고지수" in itm and "반도체" in ind for itm, ind in names):
        raise RuntimeError(f"KOSIS 응답이 반도체 재고지수가 아님: {sorted(names)[:3]}")
    periods = [row.get("PRD_DE", "") for row in arr]
    if len(periods) != len(set(periods)):
        raise RuntimeError("KOSIS 응답에 같은 달이 여러 행 — 조회 조건이 한 계열을 가리키지 않음")

    monthly = []
    for row in arr:
        prd = row["PRD_DE"]  # YYYYMM
        monthly.append((date(int(prd[:4]), int(prd[4:]), 1), float(row["DT"])))
    data = _ffill_monthly_to_weekly(monthly)
    return data, "real", (f"KOSIS 광업제조업동향조사 반도체 제조업(C261) 생산자제품 재고지수(원지수, 2020=100) "
                          f"({len(monthly)}개월, 최신 {max(periods)})")


# ──────────────────────────────────────────────────────────────────────────────
# A-5 AWS Spot 가격 — AWS IAM 키 필요
# ──────────────────────────────────────────────────────────────────────────────
def collect_A5_aws_spot():
    """AWS describe_spot_price_history — m6i.xlarge 90일 history."""
    need_env("AWS_ACCESS_KEY_ID", "https://console.aws.amazon.com/iam (계정 → IAM → Access keys, 무료)")
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


# ──────────────────────────────────────────────────────────────────────────────
# B-1, B-5, B-6 — 구글 뉴스 헤드라인 + Gemini 감성 채점
# ──────────────────────────────────────────────────────────────────────────────
def _llm_sentiment(text: str, prompt_topic: str) -> float:
    """LLM 기반 sentiment (-1~+1) — Gemini 무료 티어 단독 (gemini_client 참고).
    실행당 수십 회 호출되는 대량 작업이라 lite 모델부터 써서 flash 한도를 아낀다.
    모든 모델이 실패하면 EnvironmentError.
    """
    prompt = (
        f"다음 텍스트는 메모리 반도체 회사의 IR 자료다. {prompt_topic}에 대한 sentiment를 "
        f"-1 (매우 부정) ~ +1 (매우 긍정) 사이 한 개의 숫자로만 답변하라. 다른 설명 금지.\n\n"
        f"<text>\n{text[:8000]}\n</text>"
    )
    # max_tokens 1024: flash 계열은 답 전에 '생각'에 토큰을 써서 작게 잡으면 빈 응답이 온다
    txt, used = gemini_generate(prompt, BULK_MODELS, max_tokens=1024)
    if txt:
        m = re.search(r"-?\d+\.?\d*", txt)
        if m:
            return max(-1.0, min(1.0, float(m.group())))
        raise RuntimeError(f"{used} 응답에서 숫자를 찾지 못함: {txt[:40]}")
    raise EnvironmentError(
        f"Gemini sentiment 실패 — {used}\n"
        "GEMINI_API_KEY(https://ai.google.dev, 무료) 설정 또는 무료 한도 소진 여부를 확인."
    )


def _collect_ir_news_sentiment(sid: str, prompt_topic: str, source_label: str) -> tuple[list[dict], str, str]:
    """B-1/B-5/B-6 공통 파이프라인: Google News에서 메모리社 IR/실적 헤드라인 → LLM sentiment.
    PDF 다운로드 + 추출은 회사별 IR 페이지 구조가 자주 바뀌어 불안정 → 뉴스 헤드라인으로 우회.
    """
    import feedparser

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

    # 값이 있는 마감된 주는 채점하지 않는다 (run_one 이 기존 값을 그대로 씀 → Gemini 호출도 절약).
    # 판정은 _merge_frozen 과 같은 _open_week_test 를 쓴다.
    ft = _final_through(sid)
    is_open = _open_week_test(sid)
    open_weeks = [wk for wk in sorted(weekly_text) if is_open(wk)]

    weekly_score = []
    n_llm_calls, n_failed = 0, 0
    for wk in open_weeks:
        # 주별 헤드라인 5개 합쳐서 1회 호출
        combined = "\n---\n".join(weekly_text[wk][:5])
        try:
            score = _llm_sentiment(combined, prompt_topic)
            n_llm_calls += 1
            weekly_score.append({"week": wk, "value": round(score, 4)})
        except (EnvironmentError, RuntimeError) as e:
            # 키워드 점수로 대신 채우지 않는다 — 척도가 달라 섞이면 안 되기 때문.
            # 빈칸으로 두면 마감 후 RETRY_WEEKS 주 동안 다음 실행들에서 다시 시도한다 (_open_week_test).
            n_failed += 1
            print(f"  ⚠️ {sid} {wk} 채점 실패, 다음 실행에서 재시도: {str(e).splitlines()[0][:60]}")

    if open_weeks and n_llm_calls == 0:
        raise EnvironmentError(f"{sid} Gemini 채점 전부 실패 ({n_failed}주) — 기존 파일 유지")
    src = (f"Google News '{source_label}' ({len(entries)} entries, "
           f"LLM {n_llm_calls}회 호출, 실패 {n_failed}주, 마감 {ft or '없음'} 이후만 채점)")
    return weekly_score, "real", src


def collect_B1_earnings_sentiment():
    """B-1: 메모리社 실적 발표 sentiment (Google News + LLM)."""
    return _collect_ir_news_sentiment(
        "B-1",
        prompt_topic="quarterly earnings memory pricing outlook",
        source_label="Earnings Call sentiment",
    )


def collect_B5_lta_sentiment():
    """B-5: LTA (장기 계약) 비율 관련 뉴스 sentiment."""
    return _collect_ir_news_sentiment(
        "B-5",
        prompt_topic="long-term agreement LTA contract memory supply ratio",
        source_label="LTA ratio",
    )


def collect_B6_hbm_mix():
    """B-6: HBM 매출 비중 관련 뉴스 sentiment."""
    return _collect_ir_news_sentiment(
        "B-6",
        prompt_topic="HBM revenue mix share growth high bandwidth memory",
        source_label="HBM mix",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Registry + main
# ──────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
# target-dram — DRAM 가격 proxy (메모리 3사 주가 블렌드, Yahoo Finance 무료)
# ──────────────────────────────────────────────────────────────────────────────
# 대상 지수(target-dram)의 기준일. 시장·거시 수집기도 여기서부터 모아 같은 기간을 덮는다
# (검증 백테스트가 대상 지수와 같은 기간의 피처를 쓰도록).
HISTORY_START = "2025-06-16"


def _yf_weekly(ticker: str, start: str = HISTORY_START) -> dict:
    """Yahoo Finance 주간 종가 → {월요일 날짜: 값}. NaN 제외."""
    import yfinance as yf
    df = yf.download(ticker, start=start, end=date.today().isoformat(),
                     interval="1wk", progress=False, auto_adjust=False)
    out = {}
    for idx, row in df.iterrows():
        try:
            c = row["Close"]
            v = float(c.iloc[0] if hasattr(c, "iloc") else c)
            if v == v:  # NaN 제외
                out[snap_to_monday(idx.date()).isoformat()] = v
        except Exception:
            pass
    return out


def _fred_rows(series_id: str, start: str = HISTORY_START) -> list[tuple[date, float]]:
    """FRED 공개 CSV (API 키 불필요) → [(날짜, 값)]. 결측('.')은 제외."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}&coed={date.today().isoformat()}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    rows = []
    for ln in r.text.strip().split("\n")[1:]:
        parts = ln.split(",")
        if len(parts) != 2 or parts[1].strip() in ("", "."):
            continue
        rows.append((date.fromisoformat(parts[0].strip()), float(parts[1])))
    if not rows:
        raise RuntimeError(f"FRED {series_id} 데이터 없음")
    return rows


def _fred_weekly(series_id: str) -> list[dict]:
    """FRED 일간 → 주간 평균 (월요일 표기)."""
    weekly = defaultdict(list)
    for d, v in _fred_rows(series_id):
        weekly[snap_to_monday(d).isoformat()].append(v)
    return [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]


def _ffill_monthly_to_weekly(monthly: list[tuple[date, float]], start: str = HISTORY_START) -> list[dict]:
    """월간 관측 → 월요일 주간으로 forward-fill (관측 전 주는 제외)."""
    monthly = sorted(monthly)
    out, cur = [], -1
    w, last = snap_to_monday(date.fromisoformat(start)), snap_to_monday(date.today())
    while w <= last:
        while cur + 1 < len(monthly) and monthly[cur + 1][0] <= w:
            cur += 1
        if cur >= 0:
            out.append({"week": w.isoformat(), "value": round(monthly[cur][1], 4)})
        w += timedelta(weeks=1)
    return out


def _as_series(d: dict) -> list[dict]:
    return [{"week": w, "value": round(v, 4)} for w, v in sorted(d.items())]


# ──────────────────────────────────────────────────────────────────────────────
# target-dram — DRAM 가격 proxy (메모리 3사 주가 블렌드, Yahoo Finance 무료)
# ──────────────────────────────────────────────────────────────────────────────
def collect_target_dram():
    """DRAM 계약가는 유료(DRAMeXchange/TrendForce)라 무료 proxy 로 대체.
    메모리 3사 주가 가중 블렌드: MU(50%) + SK하이닉스 000660.KS(30%) + 삼성전자 005930.KS(20%).
    각 종목을 고정 기준일(HISTORY_START, 기존 히스토리 base=100) 대비 정규화해 가중합 → 연속성 유지.
    통화(USD/KRW)는 각자 base 대비 비율로 상쇄되어 환율 변환 불필요."""
    mu, sk, ss = _yf_weekly("MU"), _yf_weekly("000660.KS"), _yf_weekly("005930.KS")
    if not (mu and sk and ss):
        raise RuntimeError("메모리 3사 주가 수집 실패 (yfinance 차단 가능성)")
    weeks = sorted(set(mu) & set(sk) & set(ss))
    if len(weeks) < 10:
        raise RuntimeError(f"공통 주 부족 ({len(weeks)}주)")
    base_mu, base_sk, base_ss = mu[weeks[0]], sk[weeks[0]], ss[weeks[0]]
    data = [
        {"week": w,
         "value": round((0.5 * (mu[w] / base_mu) + 0.3 * (sk[w] / base_sk)
                         + 0.2 * (ss[w] / base_ss)) * 100, 4)}
        for w in weeks
    ]
    source = "Yahoo Finance blend: MU (50%) + SK Hynix (30%) + Samsung (20%), normalized to base 100"
    return data, "real-proxy", source


# ──────────────────────────────────────────────────────────────────────────────
# A-1·A-7·거시 6종 — v2.3.1 복구. 이전엔 1회성 backfill.py 에만 있어 2026-07-12 이후 멈춰 있었음.
# ──────────────────────────────────────────────────────────────────────────────
def collect_A1_taiwan_foundry():
    """TSMC 70% + UMC 30% — 각각 기준일=100 으로 정규화한 뒤 가중.
    (backfill.py 는 원주가를 그대로 섞어 TSMC 가 약 98% 를 차지했음)"""
    tsm, umc = _yf_weekly("TSM"), _yf_weekly("UMC")
    weeks = sorted(set(tsm) & set(umc))
    if len(weeks) < 10:
        raise RuntimeError(f"TSM/UMC 공통 주 부족 ({len(weeks)}주)")
    bt, bu = tsm[weeks[0]], umc[weeks[0]]
    data = [{"week": w, "value": round((0.7 * tsm[w] / bt + 0.3 * umc[w] / bu) * 100, 4)} for w in weeks]
    return data, "real", f"Yahoo Finance: TSM (70%) + UMC (30%), 각각 {HISTORY_START}=100 정규화"


def collect_A7_copper():
    data = _as_series(_yf_weekly("HG=F"))
    if not data:
        raise RuntimeError("HG=F 데이터 없음")
    return data, "real", "Yahoo Finance HG=F (COMEX Copper Futures, LME 대체)"


def collect_macro_cu():
    return collect_A7_copper()  # A-7 과 같은 소스 (화면에 두 곳 표시)


def collect_macro_dxy():
    data = _as_series(_yf_weekly("DX-Y.NYB"))
    if not data:
        raise RuntimeError("DX-Y.NYB 데이터 없음")
    return data, "real", "Yahoo Finance DX-Y.NYB (US Dollar Index)"


def collect_macro_krw():
    data = _as_series(_yf_weekly("KRW=X"))
    if not data:
        raise RuntimeError("KRW=X 데이터 없음")
    return data, "real", "Yahoo Finance KRW=X (USD/KRW spot)"


def collect_macro_fed():
    return _fred_weekly("DFF"), "real", "FRED CSV DFF (Effective Federal Funds Rate)"


def collect_macro_ust10():
    return _fred_weekly("DGS10"), "real", "FRED CSV DGS10 (10-Year Treasury Constant Maturity Rate, %)"


def collect_macro_pmi():
    """ISM PMI 대체 — 산업생산지수(INDPRO, 월간)를 월요일 주간으로 forward-fill."""
    data = _ffill_monthly_to_weekly(_fred_rows("INDPRO"))
    return data, "real", "FRED CSV INDPRO (Industrial Production Index, monthly→forward-fill weekly, PMI 대체)"


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
    "target-dram": collect_target_dram,
    "A-1": collect_A1_taiwan_foundry,
    "A-7": collect_A7_copper,
    "macro-cu": collect_macro_cu,
    "macro-dxy": collect_macro_dxy,
    "macro-krw": collect_macro_krw,
    "macro-fed": collect_macro_fed,
    "macro-ust10": collect_macro_ust10,
    "macro-pmi": collect_macro_pmi,
}


def run_one(sid: str) -> dict:
    fn = COLLECTORS.get(sid)
    if not fn:
        return {"signalId": sid, "status": "unknown"}
    try:
        data, mode, source = fn()
        frozen = None
        if sid in FREEZE_SIGNALS:
            data, frozen = _merge_frozen(sid, data)
        r = write_signal(sid, data, source, mode, frozen)
        return {"signalId": sid, "status": "ok", "weeks": r["weeks"], "source": source}
    except requests.exceptions.RequestException as e:
        # 네트워크 오류는 OSError(=EnvironmentError) 계열이라 먼저 잡는다 — '설정 필요'로 잘못 보고되던 문제 (v2.5)
        return {"signalId": sid, "status": "failed", "reason": f"네트워크 오류(다음 실행에서 재시도): {e}"}
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
