"""collect_news_events.py — 실시간 RSS → LLM 구조화 → news/events JSON

매주 화요일 06:00 KST 자동 실행 대상. DRAM 관련 RSS 피드(TechNews / Digitimes /
Google News 영어·한국어)에서 최근 30일 헤드라인을 수집해, Gemini로 일괄 분류/번역/
영향 분석한 뒤 점수 절댓값 상위 10건 news + 그중 지정학·규제·재해성 5건 events 를
구조화된 JSON 으로 저장한다.

출력:
    backend/data/news/latest.json    — UI S-006/S-007 입력
    backend/data/events/latest.json  — UI S-010/S-011 입력
"""
from __future__ import annotations
import os
import re
import json
import time
from pathlib import Path
from datetime import date, datetime, timedelta

import requests

# 프로젝트 루트 .env 로드 (auto_collectors와 동일 패턴)
ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / ".env"
if ENV.exists():
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and not os.environ.get(k):
            os.environ[k] = v

OUT_NEWS = ROOT / "backend/data/news/latest.json"
OUT_EVENTS = ROOT / "backend/data/events/latest.json"
OUT_NEWS.parent.mkdir(parents=True, exist_ok=True)
OUT_EVENTS.parent.mkdir(parents=True, exist_ok=True)

LOOKBACK_DAYS = 30

# auto_collectors.collect_B2_rss_sentiment 의 RSS 피드 재사용
RSS_FEEDS = [
    "https://technews.tw/category/semiconductor/feed/",
    "https://technews.tw/category/ai/feed/",
    "https://technews.tw/feed/",
    "https://www.digitimes.com.tw/rss/news.xml",
]
GOOGLE_NEWS_QUERIES = [
    # ── DRAM / 반도체 직접 관련 (news 후보) ──
    ("Taiwan semiconductor", "en"),
    ("DRAM memory price", "en"),
    ("HBM Nvidia", "en"),
    ("Samsung memory", "en"),
    ("SK Hynix HBM", "en"),
    ("Micron DRAM", "en"),
    ("AI server memory demand", "en"),
    ("DDR5 server", "en"),
    ("chip export ban China", "en"),
    ("Taiwan Strait tension", "en"),
    ("半導體 台灣", "zh-TW"),
    ("記憶體 DRAM", "zh-TW"),
    ("메모리 반도체", "ko"),
    ("DDR5 서버", "ko"),
    # ── USER-REQUESTED EXTENSION (2026-05-18 #8) — 글로벌 이벤트 후보 (events 다양화) ──
    # 물리적 충돌 (전쟁/테러/쿠데타)
    ("Ukraine war", "en"),
    ("Israel Iran conflict", "en"),
    ("Middle East war", "en"),
    ("terror attack", "en"),
    ("coup d'etat", "en"),
    ("우크라이나 전쟁", "ko"),
    ("이스라엘 이란", "ko"),
    # 기상이변 (지진/태풍/쓰나미)
    ("major earthquake", "en"),
    ("typhoon Asia", "en"),
    ("tsunami warning", "en"),
    ("지진 규모", "ko"),
    ("태풍 일본 대만", "ko"),
    # 금융 위기 (환율/유가/금리)
    ("Fed rate decision", "en"),
    ("crude oil price surge", "en"),
    ("US Treasury 10-year yield", "en"),
    ("USD KRW exchange rate", "en"),
    ("연준 금리", "ko"),
    ("국제 유가", "ko"),
    ("원달러 환율", "ko"),
    ("10년물 국채", "ko"),
]
for q, lang in GOOGLE_NEWS_QUERIES:
    RSS_FEEDS.append(
        f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl={lang}-US&gl=US&ceid=US:{lang.split('-')[0]}"
    )

TOPIC_KEYWORDS = [
    # DRAM/반도체
    "伺服器", "記憶體", "半導體", "DRAM", "HBM", "NAND", "SSD",
    "AI", "輝達", "Nvidia", "三星", "Samsung", "海力士", "SK", "美光", "Micron",
    "晶片", "chip", "memory", "server", "semiconductor", "fab",
    "메모리", "반도체", "서버", "DDR",
    # USER-REQUESTED EXTENSION (#8) — 글로벌 이벤트 토픽 키워드
    # 물리적 충돌
    "war", "conflict", "terror", "coup", "invasion", "ceasefire", "military strike",
    "전쟁", "테러", "쿠데타", "충돌", "공습",
    # 기상이변
    "earthquake", "typhoon", "tsunami", "hurricane", "flood", "wildfire", "magnitude",
    "지진", "태풍", "쓰나미", "허리케인", "홍수", "규모",
    # 금융 위기
    "Fed", "rate cut", "rate hike", "inflation", "crude oil", "OPEC",
    "Treasury yield", "exchange rate", "currency crisis",
    "연준", "금리", "유가", "환율", "국채", "인플레이션",
]
# 가격 영향이 강한 단어 (사전 랭킹용 휴리스틱)
STRONG_WORDS = [
    "ban", "restrict", "export", "tariff", "shortage", "surge", "rally", "collapse",
    "earthquake", "strike", "war", "invasion", "sanction", "investment", "capex",
    "production cut", "감산", "증설", "수출규제", "지진", "파업", "긴장",
    "BIS", "CHIPS", "Fed", "rate cut", "rate hike",
    # USER-REQUESTED EXTENSION (#8)
    "missile", "ceasefire", "terror", "coup", "magnitude", "tsunami", "typhoon",
    "hurricane", "inflation", "OPEC", "crude", "Treasury yield", "currency crisis",
    "전쟁", "테러", "쿠데타", "공습", "유가", "환율 급등", "국채", "연준",
]


# USER-REQUESTED EXTENSION (#8) — 사용자 정의 이벤트 카테고리 매핑 (휴리스틱 + LLM 공통)
# 각 카테고리에 키워드 매핑 — 휴리스틱이 LLM 실패 시 자동 분류
EVENT_CATEGORIES = {
    "물리적 충돌": {
        "keywords": [
            "war", "conflict", "invasion", "missile", "ceasefire", "terror",
            "coup", "military strike", "armed", "battle", "Ukraine", "Israel",
            "Iran", "Gaza", "Hamas",
            "전쟁", "테러", "쿠데타", "공습", "충돌", "교전",
        ],
        "default_risk": "high",
    },
    "기상이변": {
        "keywords": [
            "earthquake", "magnitude", "typhoon", "tsunami", "hurricane",
            "flood", "wildfire", "volcano", "cyclone",
            "지진", "태풍", "쓰나미", "허리케인", "홍수", "화산", "규모",
        ],
        "default_risk": "mid",
    },
    "금융 위기": {
        "keywords": [
            "Fed rate", "rate cut", "rate hike", "inflation", "CPI",
            "crude oil", "OPEC", "Brent", "WTI",
            "Treasury yield", "10-year yield", "exchange rate", "currency crisis",
            "DXY", "FOMC",
            "연준", "금리", "유가", "환율", "국채", "인플레이션", "FOMC",
        ],
        "default_risk": "mid",
    },
    # 기타: 위 3개에 안 맞으면 자동 할당
}


def classify_category(text: str) -> tuple[str, str]:
    """텍스트 → (category, default_risk). 우선순위: 기상이변 > 금융 위기 > 물리적 충돌 > 기타.
    USER-REQUESTED EXTENSION (#8 fix): word-boundary 매칭 — "warning"의 "war" 같은
    오인 방지. 기상이변(지진/태풍)은 자체 키워드가 명확하므로 우선순위로 검사."""
    low = " " + text.lower() + " "  # 양끝 공백으로 단순 단어 경계 보호
    # 우선순위: 기상이변 → 금융 위기 → 물리적 충돌 → 기타
    priority = ["기상이변", "금융 위기", "물리적 충돌"]
    for cat in priority:
        spec = EVENT_CATEGORIES[cat]
        for kw in spec["keywords"]:
            kw_low = kw.lower()
            # 정규식 word boundary — 영문은 \b, 한글은 단순 substring (한글 단어 boundary 까다로움)
            if re.search(r'[A-Za-z]', kw_low):
                pattern = r'\b' + re.escape(kw_low) + r'\b'
                if re.search(pattern, low):
                    return cat, spec["default_risk"]
            else:
                if kw_low in low:
                    return cat, spec["default_risk"]
    return "기타", "low"


# 지역 자동 추출 (영문/한글)
REGION_KEYWORDS = {
    "우크라이나": ["Ukraine", "Kyiv", "우크라이나"],
    "이스라엘": ["Israel", "Tel Aviv", "Gaza", "이스라엘"],
    "이란": ["Iran", "Tehran", "이란"],
    "중국": ["China", "Beijing", "중국"],
    "대만": ["Taiwan", "Taipei", "대만"],
    "한국": ["Korea", "Seoul", "한국", "Samsung", "Hynix"],
    "일본": ["Japan", "Tokyo", "Osaka", "일본"],
    "미국": ["United States", "U.S.", "US ", "America", "Fed", "Washington", "미국", "연준"],
    "유럽": ["Europe", "EU", "ECB", "Germany", "France", "UK", "유럽"],
    "중동": ["Middle East", "Saudi", "OPEC", "중동"],
    "러시아": ["Russia", "Moscow", "Putin", "러시아"],
    "글로벌": [],
}


def classify_region(text: str) -> str:
    low = text.lower()
    for region, kws in REGION_KEYWORDS.items():
        if any(kw.lower() in low for kw in kws):
            return region
    return "글로벌"


def fetch_entries() -> list[dict]:
    try:
        import feedparser
    except ImportError:
        raise SystemExit("feedparser 미설치: pip install feedparser")

    cutoff = date.today() - timedelta(days=LOOKBACK_DAYS)
    seen_titles = set()
    entries = []

    for url in RSS_FEEDS:
        try:
            f = feedparser.parse(url)
            for e in f.entries:
                pub = e.get("published_parsed") or e.get("updated_parsed")
                if not pub:
                    continue
                d = date(pub.tm_year, pub.tm_mon, pub.tm_mday)
                if d < cutoff:
                    continue
                title = (e.get("title") or "").strip()
                if not title or title in seen_titles:
                    continue
                summary = re.sub(r"<[^>]+>", " ", e.get("summary") or "").strip()
                text = (title + " " + summary)[:600]
                if not any(kw.lower() in text.lower() for kw in TOPIC_KEYWORDS):
                    continue
                seen_titles.add(title)
                # 소스 추출 (Google News는 title 뒤에 " - SourceName" 패턴)
                src = "RSS"
                m = re.search(r" - ([A-Za-z][A-Za-z0-9 .&·-]{2,40})$", title)
                if m:
                    src = m.group(1).strip()
                    title = title[:m.start()].strip()
                elif "technews.tw" in url:
                    src = "TechNews"
                elif "digitimes" in url:
                    src = "Digitimes"

                entries.append({
                    "date": d.isoformat(),
                    "title": title,
                    "summary": summary[:400],
                    "source": src,
                    "link": e.get("link", ""),
                })
        except Exception as exc:
            print(f"  ⚠️  {url[:60]}: {str(exc)[:80]}")
        time.sleep(0.15)

    return entries


def pre_rank(entries: list[dict]) -> list[dict]:
    """LLM 호출 전 휴리스틱 랭킹 — 점수 = 강도단어 hit + 최신성."""
    today = date.today()
    scored = []
    for e in entries:
        text = (e["title"] + " " + e["summary"]).lower()
        kw_hits = sum(1 for w in STRONG_WORDS if w.lower() in text)
        days_old = (today - date.fromisoformat(e["date"])).days
        recency = max(0, LOOKBACK_DAYS - days_old) / LOOKBACK_DAYS  # 0~1
        score = kw_hits * 1.0 + recency * 0.5
        scored.append((score, e))
    scored.sort(key=lambda x: -x[0])
    # USER-REQUESTED EXTENSION (#8) — 30건으로 늘려 LLM/휴리스틱 다양성 확보 (글로벌 이벤트 후보 증가)
    return [e for _, e in scored[:30]]


def _parse_or_recover_array(txt: str) -> list | None:
    """완전 JSON 파싱 시도 → 실패 시 마지막 완전한 `}` 까지 잘라 재시도."""
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # 잘림 복구: 마지막 닫힌 객체 위치 찾기
        depth = 0
        last_complete = -1
        in_str = False
        esc = False
        for i, ch in enumerate(txt):
            if esc:
                esc = False
                continue
            if ch == "\\" and in_str:
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 1:  # 배열 안의 객체 1개 닫힘
                    last_complete = i
        if last_complete > 0:
            try:
                return json.loads(txt[:last_complete + 1] + "]")
            except json.JSONDecodeError:
                return None
    return None


def llm_enrich(entries: list[dict]) -> list[dict] | None:
    """Gemini 단일 호출로 entries 일괄 enrich → JSON 배열 반환.
    실패 시 None.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    if not gemini_key:
        return None

    bullets = "\n".join(
        f"{i+1}. [{e['date']} · {e['source']}] {e['title']} — {e['summary'][:140]}"
        for i, e in enumerate(entries)
    )
    schema = """[
  {
    "idx": 1,                              // 입력 번호 (1~N)
    "title_ko": "한국어 제목 (30자 이내)",
    "summary_ko": "한국어 요약 2-3 문장",
    "score": 0.85,                         // -1.0 (매우 부정) ~ +1.0 (매우 긍정)
    "tone": "pos|neu|neg",
    "conf": 82,                            // 신뢰도 0~100
    "type": "물리적 충돌|기상이변|금융 위기|기타",   // ★ 정확히 4개 중 하나만
    "region": "미국|중국|대만|한국|일본|우크라이나|이스라엘|이란|중동|러시아|유럽|글로벌|...",
    "risk": "high|mid|low",                // 사건 위험도
    "impact": "공급↓|공급↑|수요↑|수요↓|물류↑|가격?",
    "short": {"tone":"pos|neu|neg", "text":"1~7주 영향 1문장"},
    "mid":   {"tone":"pos|neu|neg", "text":"8~21주 영향 1문장"},
    "long":  {"tone":"pos|neu|neg", "text":"21주 이후 영향 1문장"},
    "linked": ["A-2", "B-4"]               // 관련 신호 ID 1~3개
  }
]"""

    prompt = f"""너는 서버 DRAM 가격에 영향을 줄 수 있는 글로벌 이벤트를 모니터링하는 시장 정보 애널리스트다.
다음 {len(entries)}개의 헤드라인 중 **DRAM 가격에 영향이 가능한 상위 10~12개**를 골라
아래 JSON 스키마로만 답변하라. 마크다운/설명 금지, 순수 JSON 배열만 출력.

★ type 분류 (정확히 4가지 중 하나만 선택):
  - "물리적 충돌": 전쟁, 테러, 쿠데타, 군사 충돌, 미사일/공습
  - "기상이변": 지진, 태풍, 쓰나미, 허리케인, 홍수, 화산
  - "금융 위기": 환율 급변, 유가 급등락, 10년물 국채금리, Fed/연준 금리, 인플레이션
  - "기타": 위 3개에 해당하지 않는 모든 것 (파업, 수출규제, 정책 등)

★ 카테고리 다양성 강제: 가능하면 4개 카테고리에서 각 2~3건씩 분포하도록 선택.

신호 ID 참조:
  A-1 대만 공급망 | A-2 빅테크 CapEx | A-3 관세청 수출 | A-4 재고/출하 | A-5 AWS Spot | A-6 봉쇄확률 | A-7 구리
  B-1 Earnings Call | B-2 대만 뉴스 | B-3 Reddit/HN | B-4 지정학(GPR) | B-5 LTA비율 | B-6 HBM/D램 | B-7 BOM

헤드라인:
{bullets}

스키마:
{schema}
"""

    for model in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b"):
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": 16384,
                        "temperature": 0.0,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=90,
            )
        except Exception as exc:
            print(f"  ⚠️  Gemini {model} 네트워크: {str(exc)[:80]}")
            continue
        if r.status_code != 200:
            print(f"  ⚠️  Gemini {model} HTTP {r.status_code}: {r.text[:160]}")
            continue
        try:
            j = r.json()
            txt = j["candidates"][0]["content"]["parts"][0]["text"].strip()
            # 코드펜스 제거
            txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt).strip()
            arr = _parse_or_recover_array(txt)
            if isinstance(arr, list) and arr:
                print(f"  ✅ Gemini {model} → {len(arr)}건 enrich")
                return arr
        except Exception as exc:
            print(f"  ⚠️  Gemini {model} 파싱 실패: {str(exc)[:120]}")
            continue
    return None


def merge(enriched: list[dict], pool: list[dict]) -> tuple[list[dict], list[dict]]:
    """enrich 결과 + 원본 entries 병합 → news[] / events[] 분리.
    USER-REQUESTED EXTENSION (#8): events 는 4 카테고리(물리적 충돌/기상이변/금융 위기/기타)
    중 우선순위(high→mid→low) + 다양성으로 10건 보장."""
    news = []
    events = []
    ALLOWED_TYPES = {"물리적 충돌", "기상이변", "금융 위기", "기타"}

    for item in enriched:
        idx = item.get("idx", 0) - 1
        if not (0 <= idx < len(pool)):
            continue
        src_entry = pool[idx]
        tone = (item.get("tone") or "neu").lower()
        if tone not in {"pos", "neu", "neg"}:
            tone = "neu"
        score = float(item.get("score") or 0.0)
        score = max(-1.0, min(1.0, score))

        news_item = {
            "date": src_entry["date"],
            "title": item.get("title_ko") or src_entry["title"][:60],
            "titleEn": src_entry["title"],
            "source": src_entry["source"],
            "score": round(score, 2),
            "tone": tone,
            "conf": int(item.get("conf") or 70),
            "hot": abs(score) >= 0.6,
            "summary": item.get("summary_ko") or src_entry["summary"][:200],
            "effects": {
                "short": item.get("short") or {"tone": tone, "text": "단기 영향 분석 중"},
                "mid":   item.get("mid")   or {"tone": tone, "text": "중기 영향 분석 중"},
                "long":  item.get("long")  or {"tone": tone, "text": "장기 영향 분석 중"},
            },
            "linked": [f"{s} 관련" for s in (item.get("linked") or [])[:3]],
            "link": src_entry.get("link", ""),
        }
        news.append(news_item)

        # ── events 분류 — 4 카테고리 강제, LLM이 제대로 분류 안 했으면 휴리스틱 보완
        ev_type = item.get("type", "")
        if ev_type not in ALLOWED_TYPES:
            ev_type, _ = classify_category(src_entry["title"] + " " + src_entry["summary"])
        ev_region = item.get("region") or classify_region(src_entry["title"] + " " + src_entry["summary"])
        events.append({
            "id": f"ev-{len(events)+1}",
            "type": ev_type,
            "region": ev_region,
            "risk": (item.get("risk") or EVENT_CATEGORIES.get(ev_type, {}).get("default_risk", "mid")).lower(),
            "title": news_item["title"],
            "impact": item.get("impact") or "가격?",
            "date": src_entry["date"],
            "summary": news_item["summary"],
            "effects": news_item["effects"],
            "links": [len(news) - 1],
            "affects": item.get("linked") or [],
        })

    news.sort(key=lambda n: -abs(n["score"]))
    events = diversify_events(events, target=10)
    return news[:10], events


def diversify_events(events: list[dict], target: int = 10) -> list[dict]:
    """우선순위 + 카테고리 다양성으로 events 정렬.
    1) high > mid > low risk, 2) 4 카테고리 라운드-로빈, 3) 날짜 역순."""
    risk_order = {"high": 0, "mid": 1, "low": 2}
    by_cat: dict[str, list[dict]] = {"물리적 충돌": [], "기상이변": [], "금융 위기": [], "기타": []}
    for e in events:
        cat = e["type"] if e["type"] in by_cat else "기타"
        by_cat.setdefault(cat, []).append(e)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda e: (risk_order.get(e["risk"], 3), -hash(e["date"]) % 1000))

    out: list[dict] = []
    # 라운드-로빈으로 카테고리 다양성 보장
    while len(out) < target and any(by_cat.values()):
        for cat in ("물리적 충돌", "기상이변", "금융 위기", "기타"):
            if by_cat[cat] and len(out) < target:
                out.append(by_cat[cat].pop(0))

    # ID 재부여
    for i, e in enumerate(out, start=1):
        e["id"] = f"ev-{i}"
    return out


def heuristic_fallback(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """USER-REQUESTED EXTENSION (#8) — LLM 실패 시:
    1) news 10건 (DRAM 관련 우선)
    2) events 10건 보장 — 4 카테고리 (물리적 충돌/기상이변/금융 위기/기타) 다양성 분배 +
       위험도 우선순위 + 지역 자동 분류"""
    POS = ("growth", "surge", "rally", "shortage", "boost", "expand", "investment",
           "감산", "증설", "rate cut", "금리 인하")
    NEG = ("ban", "restrict", "decline", "drop", "oversupply", "수출규제", "지진",
           "긴장", "war", "전쟁", "테러", "tsunami", "쓰나미", "쿠데타", "crisis", "위기",
           "rate hike", "금리 인상", "missile", "공습")

    news = []
    for e in entries[:10]:
        text = (e["title"] + " " + e["summary"]).lower()
        pos = sum(1 for w in POS if w in text)
        neg = sum(1 for w in NEG if w in text)
        score = round((pos - neg) / max(1, pos + neg + 1), 2)
        tone = "pos" if score > 0.2 else "neg" if score < -0.2 else "neu"
        news.append({
            "date": e["date"],
            "title": e["title"][:70],
            "titleEn": e["title"],
            "source": e["source"],
            "score": score,
            "tone": tone,
            "conf": 50,
            "hot": abs(score) >= 0.5,
            "summary": e["summary"][:200] or "(요약 없음 — RSS 본문 부족)",
            "effects": {
                "short": {"tone": tone, "text": "LLM 비활성 — 휴리스틱 분류"},
                "mid":   {"tone": tone, "text": "LLM 비활성 — 휴리스틱 분류"},
                "long":  {"tone": tone, "text": "LLM 비활성 — 휴리스틱 분류"},
            },
            "linked": [],
            "link": e.get("link", ""),
        })

    # ── events: 모든 entries 를 4 카테고리로 분류 + impact/risk 자동 부여
    events_raw = []
    for e in entries:
        text = e["title"] + " " + e["summary"]
        cat, default_risk = classify_category(text)
        region = classify_region(text)
        text_low = text.lower()
        # 위험도 보정 — 강한 단어 있으면 risk 상승
        critical = ("magnitude 7", "magnitude 8", "magnitude 9", "war declar",
                    "invasion", "ceasefire collapse", "rate hike 0.75",
                    "currency collapse", "전쟁 선포", "규모 7", "규모 8")
        risk = "high" if any(c in text_low for c in critical) else default_risk
        # impact 추정
        if cat == "물리적 충돌":
            impact = "공급↓"
        elif cat == "기상이변":
            impact = "공급↓"
        elif cat == "금융 위기":
            if any(w in text_low for w in ("rate hike", "금리 인상", "달러 강세", "유가 급등")):
                impact = "물류↑"
            else:
                impact = "가격?"
        else:
            impact = "가격?"

        tone_short = "neg" if cat in {"물리적 충돌", "기상이변"} else ("neg" if "급등" in text_low or "hike" in text_low else "neu")
        events_raw.append({
            "id": f"ev-tmp",
            "type": cat,
            "region": region,
            "risk": risk,
            "title": e["title"][:80],
            "impact": impact,
            "date": e["date"],
            "summary": e["summary"][:200] or f"({cat} · {region} — RSS 요약 부족)",
            "effects": {
                "short": {"tone": tone_short, "text": f"단기 영향 평가 (휴리스틱 · {cat})"},
                "mid":   {"tone": "neu",       "text": f"중기 영향 평가 (휴리스틱 · {cat})"},
                "long":  {"tone": "neu",       "text": f"장기 영향 평가 (휴리스틱 · {cat})"},
            },
            "links": [], "affects": [],
        })

    events = diversify_events(events_raw, target=10)

    # 10건 미만이면 placeholder 추가 (각 카테고리당 1건씩 채움)
    if len(events) < 10:
        placeholders = [
            {"type": "물리적 충돌", "region": "중동", "risk": "mid", "title": "[모니터링] 중동 군사 긴장 추적", "impact": "공급↓"},
            {"type": "기상이변",   "region": "일본", "risk": "low", "title": "[모니터링] 동아시아 태풍 시즌 관찰", "impact": "물류↑"},
            {"type": "금융 위기",   "region": "미국", "risk": "mid", "title": "[모니터링] Fed 금리 정책 추적", "impact": "환율?"},
            {"type": "기타",        "region": "글로벌", "risk": "low", "title": "[모니터링] 글로벌 무역 정책 추적", "impact": "가격?"},
        ]
        for p in placeholders:
            if len(events) >= 10:
                break
            events.append({
                "id": f"ev-tmp", **p,
                "date": entries[0]["date"] if entries else "2026-05-18",
                "summary": "관련 헤드라인 미수집 (RSS 30일 윈도우 외) — 다음 주 수집 대기.",
                "effects": {"short": {"tone": "neu", "text": "(placeholder)"},
                             "mid":   {"tone": "neu", "text": "(placeholder)"},
                             "long":  {"tone": "neu", "text": "(placeholder)"}},
                "links": [], "affects": [],
            })
        # ID 재부여
        for i, e in enumerate(events, start=1):
            e["id"] = f"ev-{i}"

    return news, events


def main():
    print(f"[1/4] RSS 수집 (최근 {LOOKBACK_DAYS}일)…")
    entries = fetch_entries()
    print(f"  → 토픽 매칭 {len(entries)}건 (중복 제거 후)")
    if not entries:
        raise SystemExit("❌ RSS 결과 0건 — 네트워크/피드 확인")

    print(f"[2/4] 휴리스틱 사전 랭킹 → 상위 30건")
    top30 = pre_rank(entries)
    print(f"  → {len(top30)}건 선정")

    print(f"[3/4] Gemini 일괄 enrich (1 LLM call)…")
    enriched = llm_enrich(top30)
    if enriched:
        news, events = merge(enriched, top30)
        method = "Gemini LLM 분류"
    else:
        print(f"  ⚠️  LLM 실패 → 휴리스틱 fallback")
        news, events = heuristic_fallback(top30)
        method = "키워드 휴리스틱"

    print(f"[4/4] 저장")
    payload_news = {
        "collectedAt": date.today().isoformat(),
        "method": method,
        "lookbackDays": LOOKBACK_DAYS,
        "rawCount": len(entries),
        "news": news,
    }
    payload_events = {
        "collectedAt": date.today().isoformat(),
        "method": method,
        "events": events,
    }
    OUT_NEWS.write_text(json.dumps(payload_news, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_EVENTS.write_text(json.dumps(payload_events, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {OUT_NEWS.relative_to(ROOT)} ({len(news)}건)")
    print(f"  ✅ {OUT_EVENTS.relative_to(ROOT)} ({len(events)}건)")


if __name__ == "__main__":
    main()
