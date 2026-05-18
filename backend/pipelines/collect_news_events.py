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
]
for q, lang in GOOGLE_NEWS_QUERIES:
    RSS_FEEDS.append(
        f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl={lang}-US&gl=US&ceid=US:{lang.split('-')[0]}"
    )

TOPIC_KEYWORDS = [
    "伺服器", "記憶體", "半導體", "DRAM", "HBM", "NAND", "SSD",
    "AI", "輝達", "Nvidia", "三星", "Samsung", "海力士", "SK", "美光", "Micron",
    "晶片", "chip", "memory", "server", "semiconductor", "fab",
    "메모리", "반도체", "서버", "DDR", "HBM",
]
# 가격 영향이 강한 단어 (사전 랭킹용 휴리스틱)
STRONG_WORDS = [
    "ban", "restrict", "export", "tariff", "shortage", "surge", "rally", "collapse",
    "earthquake", "strike", "war", "invasion", "sanction", "investment", "capex",
    "production cut", "감산", "증설", "수출규제", "지진", "파업", "긴장",
    "BIS", "CHIPS", "Fed", "rate cut", "rate hike",
]


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
    return [e for _, e in scored[:20]]


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
    "type": "정치·외교|군사|자연재해|파업|지정학|경제|기술|공급망",
    "region": "미국|중국|대만|한국|일본|글로벌|...",
    "risk": "high|mid|low",                // 사건 위험도
    "impact": "공급↓|공급↑|수요↑|수요↓|물류↑|가격?",
    "short": {"tone":"pos|neu|neg", "text":"1~7주 영향 1문장"},
    "mid":   {"tone":"pos|neu|neg", "text":"8~21주 영향 1문장"},
    "long":  {"tone":"pos|neu|neg", "text":"21주 이후 영향 1문장"},
    "linked": ["A-2", "B-4"]               // 관련 신호 ID 1~3개
  }
]"""

    prompt = f"""너는 서버 DRAM 가격 영향을 분석하는 시장 정보 애널리스트다.
다음 {len(entries)}개의 헤드라인 중 **서버용 DDR5 DRAM 가격에 가장 영향이 큰 상위 10개**를 골라
아래 JSON 스키마로만 답변하라. 마크다운/설명 금지, 순수 JSON 배열만 출력.

신호 ID 참조:
  A-1 대만 공급망 (TSMC/UMC) | A-2 빅테크 CapEx | A-3 관세청 수출 | A-4 재고/출하 | A-5 AWS Spot | A-6 봉쇄확률 | A-7 구리
  B-1 Earnings Call 감성 | B-2 대만 뉴스 | B-3 Reddit/HN | B-4 지정학(GPR) | B-5 LTA비율 | B-6 HBM/D램 믹스 | B-7 BOM

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
    """enrich 결과 + 원본 entries 병합 → news[] / events[] 분리."""
    news = []
    events = []
    EVENT_TYPES = {"정치·외교", "군사", "자연재해", "파업", "지정학"}

    for item in enriched:
        idx = item.get("idx", 0) - 1
        if not (0 <= idx < len(pool)):
            continue
        src_entry = pool[idx]
        # 정규화
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

        # 이벤트 분리
        ev_type = item.get("type", "")
        if ev_type in EVENT_TYPES:
            events.append({
                "id": f"ev-{len(events)+1}",
                "type": ev_type,
                "region": item.get("region") or "글로벌",
                "risk": (item.get("risk") or "mid").lower(),
                "title": news_item["title"],
                "impact": item.get("impact") or "가격?",
                "date": src_entry["date"],
                "summary": news_item["summary"],
                "effects": news_item["effects"],
                "links": [len(news) - 1],
                "affects": item.get("linked") or [],
            })

    # 정렬: news → 점수 절댓값 큰 순, events → risk(high>mid>low) → 날짜
    news.sort(key=lambda n: -abs(n["score"]))
    risk_order = {"high": 0, "mid": 1, "low": 2}
    events.sort(key=lambda e: (risk_order.get(e["risk"], 3), e["date"]))
    return news[:10], events[:8]


def heuristic_fallback(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """LLM 실패 시 휴리스틱만으로 news/events 생성 (구조는 동일)."""
    news = []
    for e in entries[:10]:
        text = (e["title"] + " " + e["summary"]).lower()
        pos = sum(1 for w in ("growth", "surge", "rally", "shortage", "boost", "expand", "investment", "감산", "증설") if w in text)
        neg = sum(1 for w in ("ban", "restrict", "decline", "drop", "oversupply", "수출규제", "지진", "긴장") if w in text)
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

    # 이벤트 키워드 기반
    events = []
    EVENT_KW = {
        "정치·외교": ["ban", "restrict", "tariff", "BIS", "수출규제", "제재", "sanction"],
        "군사":     ["military", "war", "invasion", "tension", "긴장", "Taiwan Strait"],
        "자연재해": ["earthquake", "지진", "flood", "typhoon"],
        "파업":     ["strike", "파업", "labor"],
    }
    for e in entries:
        text = (e["title"] + " " + e["summary"]).lower()
        for tp, kws in EVENT_KW.items():
            if any(k.lower() in text for k in kws):
                events.append({
                    "id": f"ev-{len(events)+1}",
                    "type": tp, "region": "글로벌", "risk": "mid",
                    "title": e["title"][:70], "impact": "공급↓",
                    "date": e["date"], "summary": e["summary"][:200] or "(요약 없음)",
                    "effects": {"short": {"tone": "neg", "text": "(휴리스틱)"},
                                 "mid":   {"tone": "neu", "text": "(휴리스틱)"},
                                 "long":  {"tone": "neu", "text": "(휴리스틱)"}},
                    "links": [], "affects": [],
                })
                break
        if len(events) >= 8:
            break
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
