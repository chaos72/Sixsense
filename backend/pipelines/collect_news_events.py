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
    # ── USER-REQUESTED EXTENSION (2026-05-18 #9) — 국내 반도체 이슈 (파업/정전/화재) 직접 쿼리 ──
    ("Samsung union strike", "en"),
    ("SK Hynix labor strike", "en"),
    ("Korea chip fab blackout", "en"),
    ("Samsung semiconductor incident", "en"),
    ("삼성전자 파업", "ko"),
    ("삼성 노조 협상", "ko"),
    ("SK하이닉스 파업", "ko"),
    ("반도체 공장 정전", "ko"),
    ("반도체 공장 화재", "ko"),
    ("평택 화성 청주 공장", "ko"),
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
    # USER-REQUESTED EXTENSION (#9) — 국내 반도체 이슈
    "Samsung strike", "Hynix strike", "fab fire", "fab blackout", "labor union",
    "삼성 파업", "하이닉스 파업", "정전", "화재", "노조", "공장",
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


# USER-REQUESTED EXTENSION (#8/#9) — 사용자 정의 5개 이벤트 카테고리 매핑
EVENT_CATEGORIES = {
    # USER-REQUESTED EXTENSION (#9) — 국내 반도체 이슈 (파업/정전/화재 등 한국 메모리 직접 영향) 1순위 분류
    "국내 반도체": {
        "keywords": [
            "Samsung strike", "Samsung labor", "Samsung union",
            "SK Hynix strike", "SK Hynix labor", "Hynix union",
            "Korea memory plant", "Korea chip fab", "Korea semiconductor",
            "Pyeongtaek fab", "Hwaseong fab", "Icheon fab", "Cheongju fab",
            "fab fire", "fab blackout", "fab power outage", "fab incident",
            "삼성 파업", "삼성전자 파업", "삼성 노조",
            "하이닉스 파업", "SK하이닉스 파업", "하이닉스 노조",
            "한국 반도체 정전", "메모리 팹", "반도체 공장 화재", "정전 사고",
            "평택 공장", "화성 공장", "이천 공장", "청주 공장",
        ],
        "default_risk": "high",
    },
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
    # 기타: 위 4개에 안 맞으면 자동 할당
}


def classify_category(text: str) -> tuple[str, str]:
    """텍스트 → (category, default_risk).
    USER-REQUESTED EXTENSION (#9): 우선순위 국내 반도체 → 기상이변 → 금융 위기 → 물리적 충돌 → 기타.

    국내 반도체는 **한국 메모리 회사명** + **부정 이벤트 키워드** 동시 매칭으로 robust 분류
    (예: 'Samsung Electronics union talks collapse' → 국내 반도체).
    그 외 카테고리는 기존 word-boundary 키워드 매칭."""
    low = " " + text.lower() + " "

    # 1순위: 국내 반도체 — 회사명 + 이벤트 조합 매칭 (강한 시그널)
    KR_CHIP_COMPANIES = ["samsung", "hynix", "sk hynix", "skhynix",
                          "삼성", "하이닉스", "sk하이닉스", "samsung electronics"]
    KR_CHIP_EVENT_KW = ["strike", "union", "labor", "blackout", "fire", "outage",
                         "incident", "shutdown", "halt",
                         "파업", "노조", "정전", "화재", "공장", "사고", "가동 중단"]
    if any(co in low for co in KR_CHIP_COMPANIES) and any(ev in low for ev in KR_CHIP_EVENT_KW):
        return "국내 반도체", "high"
    # 또한 EVENT_CATEGORIES["국내 반도체"]의 직접 매칭도 fallback (구체적 팹명 등)
    for kw in EVENT_CATEGORIES["국내 반도체"]["keywords"]:
        kw_low = kw.lower()
        if re.search(r'[A-Za-z]', kw_low):
            if re.search(r'\b' + re.escape(kw_low) + r'\b', low):
                return "국내 반도체", "high"
        else:
            if kw_low in low:
                return "국내 반도체", "high"

    # 2~4순위: 기존 word-boundary 매칭
    for cat in ("기상이변", "금융 위기", "물리적 충돌"):
        spec = EVENT_CATEGORIES[cat]
        for kw in spec["keywords"]:
            kw_low = kw.lower()
            if re.search(r'[A-Za-z]', kw_low):
                if re.search(r'\b' + re.escape(kw_low) + r'\b', low):
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


# USER-REQUESTED EXTENSION (#9) — 휴리스틱 한국어 요약 자동 생성
def korean_summary(category: str, region: str, title: str, raw_summary: str) -> str:
    """카테고리·지역·제목 키워드 기반 한국어 요약 1~2문장 자동 생성.
    LLM 미가용 시 영문 RSS summary 대신 사용 (사용자 요청: 요약을 반드시 한글로 표시)."""
    low = (title + " " + raw_summary).lower()
    suffix = " (LLM 비활성 — 휴리스틱 요약)"

    if category == "국내 반도체":
        if any(k in low for k in ("strike", "파업", "union", "노조", "labor")):
            return f"한국 메모리 산업 직접 이슈 — 노사 협상 결렬 등 파업 관련 보도. 메모리 공장 가동 중단 시 단기 공급 차질 가능, 가격 상승 압력.{suffix}"
        if any(k in low for k in ("blackout", "정전", "power outage")):
            return f"한국 메모리 공장 정전 사고 보도 — 웨이퍼 폐기 및 라인 복구로 단기 공급 충격 가능. DRAM 현물가 영향 모니터링.{suffix}"
        if any(k in low for k in ("fire", "화재")):
            return f"한국 메모리 공장 화재 보도 — 단기 생산 차질 + 보험/복구 비용 발생 가능. 공급 차질 규모 추적 필요.{suffix}"
        return f"한국 메모리 산업 직접 이슈 ({region}) — 공급/생산 영향 모니터링 필요.{suffix}"

    if category == "물리적 충돌":
        if "ukraine" in low or "우크라이나" in low:
            return f"우크라이나 분쟁 관련 보도 — 글로벌 공급망 리스크 프리미엄 상승 및 에너지/원자재 가격 변동성 확대 가능.{suffix}"
        if any(k in low for k in ("israel", "iran", "gaza", "hamas", "lebanon")):
            return f"중동 군사 긴장 보도 ({region}) — 유가 상승 압력 + 호르무즈 해협 물류 차질 가능. DRAM 직접 영향은 제한적이나 거시 환경 악화.{suffix}"
        if "terror" in low or "테러" in low:
            return f"테러 사건 보도 ({region}) — 국지적 리스크 신호. DRAM 가격 직접 영향은 제한적.{suffix}"
        if "coup" in low or "쿠데타" in low:
            return f"쿠데타·정변 보도 ({region}) — 지역 정세 불안 모니터링.{suffix}"
        return f"물리적 충돌 보도 ({region}) — 지정학 리스크 신호 모니터링 필요.{suffix}"

    if category == "기상이변":
        if any(k in low for k in ("earthquake", "지진", "magnitude")):
            m = re.search(r"magnitude\s*([\d.]+)|규모\s*([\d.]+)|([\d.]+)-magnitude", low)
            mag_str = (m.group(1) or m.group(2) or m.group(3)) if m else "?"
            if region == "일본":
                return f"일본 규모 {mag_str} 지진 — 일본 NAND/소재 공급(키오시아 등) 단기 영향 모니터링. DRAM 직접 영향은 제한적.{suffix}"
            if region == "대만":
                return f"대만 규모 {mag_str} 지진 — TSMC/UMC 팹 가동 일시 중단 시 DRAM 공급망 직접 영향 가능.{suffix}"
            return f"{region} 규모 {mag_str} 지진 — 지역 공급망 영향 모니터링.{suffix}"
        if "typhoon" in low or "태풍" in low:
            return f"{region} 태풍 — 동아시아 물류/항만 단기 차질 가능. DRAM 운송 지연 가능성.{suffix}"
        if "tsunami" in low or "쓰나미" in low:
            return f"{region} 쓰나미 경보 — 연안 반도체 공장 가동 점검 필요.{suffix}"
        return f"{region} 기상이변 보도 — 공급망 영향 모니터링.{suffix}"

    if category == "금융 위기":
        if any(k in low for k in ("fed", "rate cut", "rate hike", "연준", "금리")):
            direction = "인하" if ("cut" in low or "인하" in low) else "인상" if ("hike" in low or "인상" in low) else "조정"
            return f"Fed 금리 {direction} 관련 보도 — 강달러/약달러 전환 → 한국 수출가격(USD 결제) 환변동 영향. DRAM CapEx 자금조달 비용 변화 가능.{suffix}"
        if any(k in low for k in ("crude", "oil", "opec", "유가", "brent", "wti")):
            return f"국제 유가 변동 보도 ({region}) — 에너지/물류비 변동으로 메모리 제조원가 + 운송비 영향.{suffix}"
        if any(k in low for k in ("treasury", "yield", "국채")):
            return f"10년물 국채금리 변동 ({region}) — 위험자산 선호도 변화로 반도체 주가/CapEx 의사결정 영향.{suffix}"
        if any(k in low for k in ("exchange", "krw", "환율", "dxy")):
            return f"환율 변동 보도 ({region}) — USD/KRW 변동은 한국 메모리 수출가격에 직접 영향.{suffix}"
        if any(k in low for k in ("inflation", "인플레이션", "cpi")):
            return f"인플레이션 지표 ({region}) — 금리 결정 변수, 거시 환경 변화 모니터링.{suffix}"
        return f"금융 위기 신호 ({region}) — 거시 환경 변동 모니터링.{suffix}"

    return f"{region} {category} 관련 보도 — 추가 분석 필요.{suffix}"


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
    "type": "국내 반도체|물리적 충돌|기상이변|금융 위기|기타",   // ★ 정확히 5개 중 하나만
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

★ type 분류 (정확히 5가지 중 하나만 선택, 우선순위 위→아래):
  - "국내 반도체": 삼성/SK하이닉스 파업·노조 협상·정전·화재 등 한국 메모리 산업 직접 이슈
  - "물리적 충돌": 전쟁, 테러, 쿠데타, 군사 충돌, 미사일/공습
  - "기상이변": 지진, 태풍, 쓰나미, 허리케인, 홍수, 화산
  - "금융 위기": 환율 급변, 유가 급등락, 10년물 국채금리, Fed/연준 금리, 인플레이션
  - "기타": 위 4개에 해당하지 않는 모든 것 (수출규제, 정책, 무역 분쟁 등)

★ 카테고리 다양성 강제: 가능하면 5개 카테고리에서 각 2건씩 분포하도록 선택.
★ summary_ko 는 반드시 한국어로 작성 (영문 번역 금지).

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
    USER-REQUESTED EXTENSION (#8/#9): events 는 5 카테고리(국내 반도체/물리적 충돌/기상이변/금융 위기/기타)
    중 우선순위(high→mid→low) + 다양성으로 10건 보장. summary 는 반드시 한국어."""
    news = []
    events = []
    ALLOWED_TYPES = {"국내 반도체", "물리적 충돌", "기상이변", "금융 위기", "기타"}

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

        # ── events 분류 — 5 카테고리 강제, LLM 분류 누락 시 휴리스틱 보완
        ev_type = item.get("type", "")
        if ev_type not in ALLOWED_TYPES:
            ev_type, _ = classify_category(src_entry["title"] + " " + src_entry["summary"])
        ev_region = item.get("region") or classify_region(src_entry["title"] + " " + src_entry["summary"])
        # USER-REQUESTED EXTENSION (#9) — summary 가 영문이면 한국어 템플릿으로 강제 변환
        ev_summary = news_item["summary"]
        if not re.search(r"[가-힣]", ev_summary):
            ev_summary = korean_summary(ev_type, ev_region, news_item["title"], ev_summary)
        events.append({
            "id": f"ev-{len(events)+1}",
            "type": ev_type,
            "region": ev_region,
            "risk": (item.get("risk") or EVENT_CATEGORIES.get(ev_type, {}).get("default_risk", "mid")).lower(),
            "title": news_item["title"],
            "impact": item.get("impact") or "가격?",
            "date": src_entry["date"],
            "summary": ev_summary,
            "effects": news_item["effects"],
            "links": [len(news) - 1],
            "affects": item.get("linked") or [],
        })

    news.sort(key=lambda n: -abs(n["score"]))
    events = diversify_events(events, target=10)
    return news[:10], events


def _make_placeholder(cat: str, fallback_date: str = "2026-05-18") -> dict:
    """USER-REQUESTED EXTENSION (#9) — 5 카테고리 강제 보장용 placeholder."""
    spec = {
        "국내 반도체": {"region": "한국",   "risk": "mid", "title": "[모니터링] 한국 메모리 산업 이슈 추적 (파업/정전/화재)", "impact": "공급↓"},
        "물리적 충돌": {"region": "중동",   "risk": "mid", "title": "[모니터링] 중동 군사 긴장 추적",                       "impact": "공급↓"},
        "기상이변":   {"region": "일본",   "risk": "low", "title": "[모니터링] 동아시아 태풍/지진 관찰",                     "impact": "물류↑"},
        "금융 위기":   {"region": "미국",   "risk": "mid", "title": "[모니터링] Fed 금리 정책 추적",                          "impact": "가격?"},
        "기타":       {"region": "글로벌", "risk": "low", "title": "[모니터링] 글로벌 무역 정책 추적",                       "impact": "가격?"},
    }[cat]
    return {
        "id": "ev-tmp", "type": cat, **spec, "date": fallback_date,
        "summary": f"관련 헤드라인 미수집 (RSS 30일 윈도우 외) — 다음 주 수집 대기. (카테고리: {cat})",
        "effects": {"short": {"tone": "neu", "text": "(placeholder)"},
                     "mid":   {"tone": "neu", "text": "(placeholder)"},
                     "long":  {"tone": "neu", "text": "(placeholder)"}},
        "links": [], "affects": [],
    }


def diversify_events(events: list[dict], target: int = 10) -> list[dict]:
    """USER-REQUESTED EXTENSION (#9) — 5 카테고리 항상 1건 이상 보장 + 라운드-로빈.
    1단계: 5 카테고리 각 1건 (없으면 placeholder)
    2단계: 라운드-로빈으로 target까지 채움 (실데이터 우선)"""
    risk_order = {"high": 0, "mid": 1, "low": 2}
    by_cat: dict[str, list[dict]] = {
        "국내 반도체": [], "물리적 충돌": [], "기상이변": [], "금융 위기": [], "기타": [],
    }
    for e in events:
        cat = e["type"] if e["type"] in by_cat else "기타"
        by_cat[cat].append(e)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda e: (risk_order.get(e["risk"], 3), -hash(e["date"]) % 1000))

    fallback_date = events[0]["date"] if events else "2026-05-18"
    out: list[dict] = []

    # 1단계: 5 카테고리 각 1건 강제 보장 (없으면 placeholder)
    for cat in ("국내 반도체", "물리적 충돌", "기상이변", "금융 위기", "기타"):
        if by_cat[cat]:
            out.append(by_cat[cat].pop(0))
        else:
            out.append(_make_placeholder(cat, fallback_date))

    # 2단계: 라운드-로빈으로 target까지 채움 (실데이터만)
    while len(out) < target and any(by_cat.values()):
        for cat in ("국내 반도체", "물리적 충돌", "기상이변", "금융 위기", "기타"):
            if by_cat[cat] and len(out) < target:
                out.append(by_cat[cat].pop(0))

    # 3단계: 여전히 부족하면 기타 placeholder 추가
    while len(out) < target:
        out.append(_make_placeholder("기타", fallback_date))

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
        critical = ("magnitude 7", "magnitude 8", "magnitude 9", "war declar",
                    "invasion", "ceasefire collapse", "rate hike 0.75",
                    "currency collapse", "전쟁 선포", "규모 7", "규모 8",
                    "strike", "파업", "blackout", "정전", "fab fire", "화재")
        risk = "high" if any(c in text_low for c in critical) else default_risk
        if cat == "국내 반도체":
            impact = "공급↓"
        elif cat == "물리적 충돌":
            impact = "공급↓"
        elif cat == "기상이변":
            impact = "공급↓"
        elif cat == "금융 위기":
            impact = "물류↑" if any(w in text_low for w in ("rate hike", "금리 인상", "달러 강세", "유가 급등")) else "가격?"
        else:
            impact = "가격?"

        tone_short = "neg" if cat in {"국내 반도체", "물리적 충돌", "기상이변"} else ("neg" if "급등" in text_low or "hike" in text_low else "neu")
        # USER-REQUESTED EXTENSION (#9) — 요약 반드시 한국어 (휴리스틱 템플릿 자동 생성)
        kr_summary = korean_summary(cat, region, e["title"], e["summary"])
        events_raw.append({
            "id": "ev-tmp",
            "type": cat,
            "region": region,
            "risk": risk,
            "title": e["title"][:80],
            "impact": impact,
            "date": e["date"],
            "summary": kr_summary,
            "effects": {
                "short": {"tone": tone_short, "text": f"단기 영향 평가 (휴리스틱 · {cat})"},
                "mid":   {"tone": "neu",       "text": f"중기 영향 평가 (휴리스틱 · {cat})"},
                "long":  {"tone": "neu",       "text": f"장기 영향 평가 (휴리스틱 · {cat})"},
            },
            "links": [], "affects": [],
        })

    # USER-REQUESTED EXTENSION (#9) — diversify_events 가 5 카테고리 보장 + 10건 보장 모두 처리
    events = diversify_events(events_raw, target=10)
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
