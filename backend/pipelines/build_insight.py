"""build_insight.py — 현재 상태를 LLM(Claude 우선)에게 종합 분석시켜 인사이트 JSON 생성

매주 화요일 06:00 KST 자동 실행 대상 (auto_collectors → collect_news_events →
forecast_v2 → **build_insight** → build_frontend_data 순서).

입력:
  - backend/data/historical/{A-*, B-*, macro-*, target-dram}.json (최신값)
  - backend/data/forecast/forecast_v2_*.json (Multi-model 예측)
  - backend/data/news/latest.json (Top 10 news headlines)

LLM 우선순위:
  1. Anthropic Claude (사용자가 KAIST CAIO 과제로 "100% Claude 관점" 요청)
  2. Gemini 2.5 Flash (fallback)
  3. 휴리스틱 (둘 다 실패 시)

출력:
  backend/data/insight/latest.json — meta.insight 로 frontend에 주입됨
"""
from __future__ import annotations
import os
import re
import json
from pathlib import Path
from datetime import date, datetime

import requests

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

HIST = ROOT / "backend/data/historical"
FORECAST = ROOT / "backend/data/forecast"
NEWS = ROOT / "backend/data/news/latest.json"
OUT = ROOT / "backend/data/insight/latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

SIGNAL_NAMES = {
    "A-1": "대만 공급망", "A-2": "빅테크 CapEx", "A-3": "관세청 수출",
    "A-4": "재고/출하 지수", "A-5": "AWS Spot", "A-6": "Manifold 봉쇄확률",
    "A-7": "구리 선물가",
    "B-1": "Earnings Call 감성", "B-2": "대만 뉴스 감성", "B-3": "Reddit/HN",
    "B-4": "지정학 리스크 (GPR)", "B-5": "LTA 비율",
    "B-6": "HBM/D램 믹스", "B-7": "BOM 신호",
}


def latest(sid: str) -> float | None:
    p = HIST / f"{sid}.json"
    if not p.exists():
        return None
    rows = json.loads(p.read_text()).get("data", [])
    return rows[-1]["value"] if rows else None


def build_prompt() -> tuple[str, dict]:
    """LLM 입력 프롬프트 + 원시 컨텍스트 빌드."""
    target_rows = json.loads((HIST / "target-dram.json").read_text())["data"]
    last_idx = target_rows[-1]["value"]  # base 100 index
    prev_idx = target_rows[-2]["value"] if len(target_rows) > 1 else last_idx
    wow = (last_idx - prev_idx) / prev_idx * 100 if prev_idx else 0
    current_usd = round(last_idx * 0.01, 2)  # build_frontend_data.py 의 SCALE와 동일

    # model_comparison.txt 우선 — build_frontend_data.py 와 동일 소스 사용 (인사이트/대시보드 가격 일치 보장)
    # USER-REQUESTED EXTENSION (#18) — anchor 보정: 첫 예측값을 현재가에 맞춰 비율 유지.
    # build_frontend_data.py 의 _anchor_scale 과 동일 로직 → 차트/인사이트 가격 일치.
    pred7_idx = pred21_idx = None
    gbr_first = lstm_first = None
    cmp_file = FORECAST / "model_comparison.txt"
    if cmp_file.exists():
        txt = cmp_file.read_text()
        # USER-REQUESTED EXTENSION (#19 fix) — 종료 마커 의존 제거, 날짜+숫자 행 직접 매칭
        def _sec(header):
            m = re.search(rf"{header}.*?\n(.*?)(?=\n📈|\n⏱|\n단기 MAPE|\nLSTM held|\n🏆|\n═|\Z)", txt, re.DOTALL)
            return m.group(1) if m else ""
        rows = [r for r in (re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
                            for line in _sec(r"📈 단기").split("\n")) if r]
        if rows:
            gbr_first = float(rows[0].group(4))    # GBR 첫 주
            pred7_idx = float(rows[-1].group(4))   # GBR 마지막 주
        rows = [r for r in (re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([\d.]+)", line)
                            for line in _sec(r"📈 중장기").split("\n")) if r]
        if rows:
            lstm_first = float(rows[0].group(3))   # LSTM 첫 주
            pred21_idx = float(rows[-1].group(3))  # LSTM 마지막 주

    # anchor 보정 — build_frontend_data.py 와 동일 로직 (차트/인사이트 가격 일치)
    # 단기(GBR): 첫 예측을 현재가(last_idx)에 맞춤
    gbr_last_anchored = pred7_idx
    if gbr_first and pred7_idx and gbr_first != 0:
        pred7_idx = pred7_idx * (last_idx / gbr_first)
        gbr_last_anchored = pred7_idx  # GBR 끝점(= 단기 7주 예측, anchor 후)
    # USER-REQUESTED EXTENSION (#19) — 중장기(LSTM): 단기 GBR 끝점에 이어붙임.
    # LSTM 첫 예측을 GBR 마지막 값에 anchor → 차트 절벽 제거 + 인사이트 일관.
    if lstm_first and pred21_idx and lstm_first != 0:
        pred21_idx = pred21_idx * (gbr_last_anchored / lstm_first)

    # Fallback: forecast JSON
    if pred7_idx is None or pred21_idx is None:
        forecast = json.loads((FORECAST / "forecast_v2_2026-02-w1.json").read_text())
        models = forecast.get("models", {})
        prophet = models.get("prophet", {}).get("predictions", [])
        lstm = models.get("lstm_mid", {}).get("predictions", []) or models.get("lstm", {}).get("predictions", [])
        if pred7_idx is None and prophet:
            pred7_idx = prophet[6].get("yhat", last_idx) if len(prophet) >= 7 else last_idx
        if pred21_idx is None:
            mid_src = lstm if lstm else prophet
            pred21_idx = mid_src[20].get("yhat", last_idx) if len(mid_src) >= 21 else (mid_src[-1].get("yhat", last_idx) if mid_src else last_idx)

    pred7 = round(pred7_idx * 0.01, 2)
    pred7_pct = (pred7 - current_usd) / current_usd * 100 if current_usd else 0
    pred21 = round(pred21_idx * 0.01, 2)
    pred21_pct = (pred21 - current_usd) / current_usd * 100 if current_usd else 0

    # 신호 요약
    sig_lines = []
    for sid, name in SIGNAL_NAMES.items():
        v = latest(sid)
        if v is None:
            continue
        if -10 < v < 10:
            sig_lines.append(f"  {sid} {name}: {v:+.2f}")
        elif abs(v) >= 1e6:
            sig_lines.append(f"  {sid} {name}: {v / 1e6:.2f}M")
        elif abs(v) >= 1e3:
            sig_lines.append(f"  {sid} {name}: {v / 1e3:.1f}K")
        else:
            sig_lines.append(f"  {sid} {name}: {v:.2f}")

    # 거시
    macro_lines = []
    for mid, name in [("macro-fed", "Fed Rate"), ("macro-dxy", "DXY"),
                       ("macro-pmi", "INDPRO/PMI"), ("macro-krw", "USD/KRW"),
                       ("macro-cu", "Copper")]:
        v = latest(mid)
        if v is not None:
            macro_lines.append(f"  {name}: {v:.2f}")

    # 뉴스 헤드라인 (top 5)
    news_lines = []
    if NEWS.exists():
        news = json.loads(NEWS.read_text()).get("news", [])
        for n in news[:5]:
            tag = "📈" if n["tone"] == "pos" else "📉" if n["tone"] == "neg" else "▪"
            news_lines.append(f"  {tag} [{n['date']}] {n['title']} (score {n['score']:+.2f}, conf {n['conf']}%)")

    ctx = {
        "current_usd": current_usd,
        "wow_pct": round(wow, 1),
        "pred7": pred7, "pred7_pct": round(pred7_pct, 1),
        "pred21": pred21, "pred21_pct": round(pred21_pct, 1),
        "signals": sig_lines,
        "macro": macro_lines,
        "news": news_lines,
    }

    prompt = f"""당신은 서버 DRAM 가격 의사결정을 돕는 시장 전략 애널리스트입니다.
아래 실데이터를 종합하여 KAIST CAIO 6조 Sixsense 대시보드의 "예측분석 인사이트" 카드용 종합 판단을 작성하세요.

【현재 가격】
  현재가: ${current_usd:.2f} (지난주 대비 {wow:+.1f}%)
  GBR 단기 예측 7주 후: ${pred7:.2f} ({pred7_pct:+.1f}%)
  LSTM 중장기 예측 21주 후: ${pred21:.2f} ({pred21_pct:+.1f}%)

【14개 프록시 신호 최신값】
{chr(10).join(sig_lines)}

【거시경제】
{chr(10).join(macro_lines)}

【최근 30일 핵심 뉴스 (Top 5)】
{chr(10).join(news_lines) if news_lines else "  (뉴스 데이터 없음)"}

다음 JSON 스키마로만 답변하세요. 한국어로, 마크다운/설명 금지:
{{
  "headline": "22자 이내 강조 메시지 (예: 'AI 수요 견인, 장기 상승 전환')",
  "summary": "**280~360자** 사이 종합 분석 — 가격 방향, 핵심 근거 3개(신호+뉴스+거시), 단기와 중장기의 차이, 워치 포인트 1~2개를 자연스럽게 연결한 한 단락. ★ **반드시 마지막을 마침표(.)로 완결**할 것. '...' '…' '등' '강력한' 처럼 끊긴 어구로 끝내지 말 것 (잘림 금지). 모든 문장이 주어+서술어로 완결되어야 함. **중요한 단어·수치 3~5개**를 **이중 별표**로 감싸서 강조하라. 예: '**AI 수요**가 **+36%**의 **장기 상승**을 견인합니다.'",
  "tone": "pos|neu|neg",
  "confidence": 0~100,
  "horizon_tilt": "short|mid|long — 어느 호라이즌이 가장 결정적인가",
  "key_signals": ["A-2", "B-4"]
}}"""
    return prompt, ctx


def call_anthropic(prompt: str) -> tuple[dict | None, str]:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return None, "Anthropic 키 없음"
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
    except Exception as e:
        return None, f"Anthropic 네트워크 실패: {str(e)[:80]}"
    if r.status_code != 200:
        return None, f"Anthropic HTTP {r.status_code}: {r.text[:120]}"
    try:
        txt = r.json()["content"][0]["text"].strip()
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt).strip()
        obj = json.loads(txt)
        return obj, "Anthropic claude-haiku-4-5"
    except Exception as e:
        return None, f"Anthropic 파싱 실패: {str(e)[:80]}"


def call_gemini(prompt: str) -> tuple[dict | None, str]:
    key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    if not key:
        return None, "Gemini 키 없음"
    for model in ("gemini-2.5-flash", "gemini-2.0-flash"):
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": 8192,
                        "temperature": 0.2,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=60,
            )
        except Exception as e:
            print(f"  Gemini {model} 네트워크: {str(e)[:60]}")
            continue
        if r.status_code != 200:
            print(f"  Gemini {model} HTTP {r.status_code}")
            continue
        try:
            txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt).strip()
            return json.loads(txt), f"Gemini {model}"
        except Exception as e:
            print(f"  Gemini {model} 파싱 실패: {str(e)[:60]}")
    return None, "Gemini 모두 실패"


# USER-REQUESTED EXTENSION (#18) — Groq fallback 추가 (Gemini 한도 소진 대비).
# collect_news_events 와 동일하게 Groq llama-3.3 (무료 14400/day) 를 3순위로.
def call_groq(prompt: str) -> tuple[dict | None, str]:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return None, "Groq 키 없음"
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "너는 시장 분석가다. 반드시 순수 JSON 객체 하나만 출력하라. 마크다운 코드펜스나 설명 텍스트 없이 { 로 시작해 } 로 끝나는 JSON 만."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2048,
                "temperature": 0.2,
            },
            timeout=60,
        )
    except Exception as e:
        return None, f"Groq 네트워크: {str(e)[:50]}"
    if r.status_code != 200:
        return None, f"Groq HTTP {r.status_code}"
    try:
        txt = r.json()["choices"][0]["message"]["content"].strip()
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt).strip()
        return json.loads(txt), "Groq llama-3.3"
    except Exception as e:
        return None, f"Groq 파싱 실패: {str(e)[:50]}"


def heuristic(ctx: dict) -> dict:
    """LLM 실패 시 데이터 기반 250자 요약. 신호+뉴스+모순 해석까지 포함."""
    short_pct = ctx["pred7_pct"]
    mid_pct = ctx["pred21_pct"]
    direction_short = "상승" if short_pct > 2 else "하락" if short_pct < -2 else "횡보"
    direction_mid = "상승" if mid_pct > 5 else "하락" if mid_pct < -5 else "횡보"
    # 모순 감지
    contradiction = (short_pct < -2 and mid_pct > 5) or (short_pct > 2 and mid_pct < -5)
    tone = "pos" if mid_pct > 0 else "neg" if mid_pct < 0 else "neu"
    horizon = "long" if abs(mid_pct) > 20 else "short" if abs(short_pct) > abs(mid_pct) else "mid"

    # 헤드라인 — 강조용 짧은 메시지
    if contradiction and tone == "pos":
        headline = f"단기 조정 후 중장기 강세 ({mid_pct:+.0f}%)"
    elif contradiction and tone == "neg":
        headline = f"단기 반등에도 중장기 약세 ({mid_pct:+.0f}%)"
    elif tone == "pos":
        headline = f"{direction_short}·{direction_mid} 동조, 상승 시그널"
    elif tone == "neg":
        headline = f"{direction_short}·{direction_mid} 동조, 하락 시그널"
    else:
        headline = "뚜렷한 방향성 없음 — 추가 신호 대기"

    # 신호 코멘트
    sig_text = ""
    for line in ctx["signals"]:
        if "A-4" in line:
            # A-4 재고/출하 — 100 초과면 alert
            m = re.search(r":\s*([\d.]+)", line)
            if m and float(m.group(1)) > 100:
                sig_text = f" A-4 재고지수가 {m.group(1)}(>100)로 공급과잉 경계 신호."
                break
            elif m and float(m.group(1)) < 95:
                sig_text = f" A-4 재고지수 {m.group(1)}(<95)로 공급 타이트 신호."
                break

    # 거시 코멘트
    macro_text = ""
    for line in ctx["macro"]:
        if "DXY" in line:
            m = re.search(r":\s*([\d.]+)", line)
            if m:
                v = float(m.group(1))
                macro_text = f" DXY {v:.1f}로 강달러 압력{'↑' if v > 100 else '↓'}."
                break

    # 뉴스 코멘트
    news_text = ""
    if ctx["news"]:
        news_text = f" 최근 30일 핵심 뉴스 {len(ctx['news'])}건이 동반."

    # USER-REQUESTED EXTENSION (#12) — 280~360자 분량, 완결 문장으로 마무리
    summary = (
        f"단기 **GBR** 모델은 7주 후 **${ctx['pred7']:.2f}** (**{short_pct:+.1f}%**)를, "
        f"중장기 **LSTM** 모델은 21주 후 **${ctx['pred21']:.2f}** (**{mid_pct:+.1f}%**)를 가리킵니다. "
        f"{'단기와 중장기의 방향이 **상반**되므로 호라이즌별 의사결정이 필요합니다. ' if contradiction else ''}"
        f"{sig_text.strip()}{macro_text.strip()}{news_text.strip()} "
        f"종합적으로 향후 **AI 서버 수요** 증가세와 **HBM 캡 증설** 속도, **지정학 리스크** 변화를 "
        f"주간 단위로 모니터링하며 호라이즌별로 차별화된 대응이 필요합니다."
    ).strip()
    # 270자 cap 보정
    if len(summary) > 270:
        summary = summary[:250].rsplit(" ", 1)[0] + "…"

    # 키 신호 — 변화 큰 것 자동 선택
    key_signals = []
    if abs(short_pct) > 3 or abs(mid_pct) > 10:
        key_signals.append("A-2")  # CapEx
    if news_text:
        key_signals.append("B-4")  # 지정학
    if not key_signals:
        key_signals = ["A-2", "B-1"]

    return {
        "headline": headline,
        "summary": summary,
        "tone": tone,
        "confidence": 55,
        "horizon_tilt": horizon,
        "key_signals": key_signals[:3],
    }


def main():
    print("[1/3] 컨텍스트 빌드…")
    prompt, ctx = build_prompt()
    print(f"  현재 ${ctx['current_usd']:.2f} · 7w ${ctx['pred7']:.2f} ({ctx['pred7_pct']:+.1f}%) · 21w ${ctx['pred21']:.2f} ({ctx['pred21_pct']:+.1f}%)")
    print(f"  신호 {len(ctx['signals'])}개 · 거시 {len(ctx['macro'])}개 · 뉴스 {len(ctx['news'])}건")

    print("[2/3] LLM 종합 분석 (Anthropic 우선)…")
    obj, source = call_anthropic(prompt)
    if not obj:
        print(f"  ⚠️  {source} → Gemini fallback")
        obj, source = call_gemini(prompt)
    if not obj:
        print(f"  ⚠️  {source} → Groq fallback")
        obj, source = call_groq(prompt)
    if not obj:
        print(f"  ⚠️  {source} → 휴리스틱 fallback")
        obj = heuristic(ctx)
        source = "휴리스틱 (LLM 모두 실패)"

    # 정규화
    headline = (obj.get("headline") or "").strip()[:50]
    summary = (obj.get("summary") or "").strip()
    # USER-REQUESTED EXTENSION (#12) — 완결 문장 보장
    # 1) 미완성 표기 검출 ("…", "...", "등", "강력한", "포함한") → 마지막 마침표까지만 사용
    truncation_markers = ("…", "...", "등 강력한", "강력한 등", "강력한.", "등.")
    if any(summary.endswith(m) for m in truncation_markers) or summary.endswith("…"):
        last_period = max(summary.rfind("."), summary.rfind("다."), summary.rfind("요."), summary.rfind("니다."))
        if last_period > len(summary) * 0.4:
            summary = summary[:last_period + 1].strip()
    # 2) 마침표 없이 끝나면 자동 추가
    if summary and not summary.rstrip().endswith((".", "!", "?", "다", "요")):
        summary = summary.rstrip(" ,;:·") + "."
    # 3) 최대 400자 cap (안전 장치, 그 이상은 마지막 마침표까지 절단)
    if len(summary) > 400:
        cutoff = summary[:400].rfind(".")
        summary = summary[:cutoff + 1] if cutoff > 200 else summary[:380] + "…"
    tone = (obj.get("tone") or "neu").lower()
    if tone not in {"pos", "neu", "neg"}:
        tone = "neu"
    conf = int(obj.get("confidence") or 50)
    conf = max(0, min(100, conf))
    horizon = (obj.get("horizon_tilt") or "mid").lower()
    if horizon not in {"short", "mid", "long"}:
        horizon = "mid"
    key_signals = [s for s in (obj.get("key_signals") or []) if isinstance(s, str)][:4]

    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "model": source,
        "headline": headline,
        "summary": summary,
        "tone": tone,
        "confidence": conf,
        "horizon": horizon,
        "keySignals": key_signals,
        "context": {
            "current": ctx["current_usd"],
            "wow": ctx["wow_pct"],
            "pred7": ctx["pred7"], "pred7_pct": ctx["pred7_pct"],
            "pred21": ctx["pred21"], "pred21_pct": ctx["pred21_pct"],
        },
    }

    print("[3/3] 저장")
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {OUT.relative_to(ROOT)}")
    print(f"     모델: {source}")
    print(f"     headline: {headline}")
    print(f"     summary ({len(summary)}자): {summary[:80]}…")
    print(f"     tone={tone} · conf={conf}% · horizon={horizon} · keySignals={key_signals}")


if __name__ == "__main__":
    main()
