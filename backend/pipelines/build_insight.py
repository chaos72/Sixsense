"""build_insight.py — 수집된 사실을 LLM(Gemini)으로 요약해 '시장 신호 요약' 카드 JSON 생성

매주 화요일 06:00 KST 자동 실행 (auto_collectors → collect_news_events → honest_backtest →
forecast_v2(참고) → **build_insight** → build_frontend_data).

입력 (사실만 — 요약에는 예측 수치를 넣지 않음. 예측은 별도 "왜 불합격인가" 설명에서만 다룸):
  - backend/data/historical/{A-*, B-*, macro-*, target-dram}.json (최신값·기준일)
  - backend/data/validation/latest.json (예측 검증 결과)
  - backend/data/news/latest.json (핵심 뉴스)

LLM 정책 (2026-09 변경):
  GPT·Gemini·Claude 중 하나만, 무료로 — API 무료 사용분이 있는 Gemini 단독 (gemini_client).
  중국·오픈소스 모델 미사용. Gemini 가 모두 실패하면 휴리스틱.
  (이전 "Claude 우선"은 크레딧 소진으로 실제로는 동작하지 않고 있었음)

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

from gemini_client import QUALITY_MODELS, available, gemini_generate

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
NEWS = ROOT / "backend/data/news/latest.json"
VALIDATION = ROOT / "backend/data/validation/latest.json"
OUT = ROOT / "backend/data/insight/latest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

# 화면과 같은 신호 이름·제외 목록·신선도 기준을 쓴다 (한 곳에서만 정의)
from build_frontend_data import (EXCLUDED_SIGNALS, MACRO_META, SIGNAL_META, UNIT_LABEL,
                                 freshness)


def _load(sid: str) -> dict:
    p = HIST / f"{sid}.json"
    return json.loads(p.read_text()) if p.exists() else {"data": []}


def build_prompt() -> tuple[str, dict]:
    """LLM 입력 — 수집된 사실과 예측 검증 결과만. 예측 수치는 넣지 않는다."""
    target = json.loads((HIST / "target-dram.json").read_text())
    rows = target["data"]
    ref_date = target.get("collectedAt") or rows[-1]["week"]
    vals = [r["value"] for r in rows]

    def chg(n):
        return round((vals[-1] / vals[-1 - n] - 1) * 100, 1) if len(vals) > n else None

    sig_lines, allowed = [], []
    for sid, meta in SIGNAL_META.items():
        sig = _load(sid); r = sig["data"]
        if sid in EXCLUDED_SIGNALS or not r:
            continue
        stale = freshness(r, sig.get("collectedAt"), ref_date, sid)["stale"]
        v = r[-1]["value"]
        # 부호(+/-)는 감성 점수에만 — 가격·지수에 '+0.13'을 붙이면 LLM 이 '상승'으로 오독한다
        if meta["fmt"] == "sent":
            v_txt = f"{v:+.2f} (감성 점수, -1~+1)"
        elif abs(v) >= 1e6:
            v_txt = f"{v:,.0f}"
        else:
            v_txt = f"{v:.3f}".rstrip("0").rstrip(".")
        sig_lines.append(f"  {sid} {meta['name']}: {v_txt} (기준 {r[-1]['week']}"
                         f"{', 갱신 중단' if stale else ''}) — {meta['desc']}")
        if not stale:
            allowed.append(sid)

    macro_lines = []
    for mid, meta in MACRO_META.items():
        sig = _load(mid); r = sig["data"]
        if r:
            stale = freshness(r, sig.get("collectedAt"), ref_date, mid)["stale"]
            macro_lines.append(f"  {meta['name']}: {r[-1]['value']:.2f} (기준 {r[-1]['week']}"
                               f"{', 갱신 중단 — 현재 상황 판단에 쓰지 말 것' if stale else ''})")

    news_lines = []
    if NEWS.exists():
        for n in json.loads(NEWS.read_text()).get("news", [])[:5]:
            news_lines.append(f"  [{n['date']}] {n['title']} (감성 {n['score']:+.2f})")

    v = json.loads(VALIDATION.read_text()) if VALIDATION.exists() else {}
    vo = (v.get("variants") or [{}])[0].get("overall", {})
    verdict = v.get("verdict", "결과 없음")

    ctx = {"current": round(vals[-1], 2), "change1w": chg(1), "change4w": chg(4), "change13w": chg(13),
           "verdict": verdict, "signals": sig_lines, "macro": macro_lines, "news": news_lines,
           "allowed": allowed}

    prompt = f"""당신은 메모리 반도체 시장 '모니터링 대시보드'의 요약 작성자입니다.

【중요한 제약】
- 이 대시보드에는 검증을 통과한 가격 예측 모델이 없습니다. 예측 검증 결과: {verdict}
  (워크포워드 백테스트에서 AI 모델 오차 {vo.get('modelMape', '-')}% > 단순 기준선 {vo.get('naiveMape', '-')}%)
- 따라서 가격이 오르거나 내릴 것이라고 예측·전망하지 마세요. 확률·신뢰도·목표가를 만들지 마세요.
- 아래 입력에 있는 사실과 숫자만 사용하세요. 입력에 없는 숫자나 사건을 만들지 마세요.
- '갱신 중단' 표시된 값은 현재 상황의 근거로 쓰지 마세요.

【{UNIT_LABEL} (실제 DRAM 계약가가 아닌 대용 지표, 2025-06-16 = 100)】
  현재 {vals[-1]:.1f} pt · 1주 {chg(1):+.1f}% · 4주 {chg(4):+.1f}% · 13주 {chg(13):+.1f}%

【수집 신호 최신값】
{chr(10).join(sig_lines)}

【거시경제】
{chr(10).join(macro_lines)}

【최근 핵심 뉴스】
{chr(10).join(news_lines) if news_lines else "  (없음)"}

다음 JSON 으로만 답하세요. 한국어, 마크다운·설명 금지:
{{
  "headline": "22자 이내 — 지금 관찰되는 사실 (예측 표현 금지)",
  "summary": "200~320자 한 단락 — 주가지수 흐름, 눈에 띄는 신호·뉴스·거시 사실 2~3개, 주시할 점. 마침표로 완결. 핵심 단어 2~4개를 **이중 별표**로 강조.",
  "tone": "pos|neu|neg — 현재 수집된 신호·뉴스의 전반적 분위기",
  "key_signals": ["입력 신호 중 갱신 중단이 아닌 것의 ID 1~3개: {', '.join(allowed)}"]
}}"""
    return prompt, ctx


def call_gemini(prompt: str) -> tuple[dict | None, str]:
    """Gemini 무료 티어 — 모델별로 호출 → JSON 파싱, 파싱 실패 시 다음 모델."""
    for model in available(QUALITY_MODELS):
        txt, used = gemini_generate(prompt, (model,), max_tokens=8192,
                                    temperature=0.2, json_mode=True)
        if not txt:
            print(f"  {used}")
            continue
        try:
            txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt).strip()
            return json.loads(txt), f"Gemini {model}"
        except Exception as e:
            print(f"  Gemini {model} 파싱 실패: {str(e)[:60]}")
    return None, "Gemini 모두 실패"


def heuristic(ctx: dict) -> dict:
    """LLM 실패 시 — 입력 사실만으로 만든 문장 (고정 전망 문구 없음)."""
    c1, c4, c13 = ctx["change1w"], ctx["change4w"], ctx["change13w"]
    news_n = len(ctx["news"])
    summary = (
        f"**{UNIT_LABEL}**는 {ctx['current']:.1f} pt로 지난주 대비 {c1:+.1f}%, "
        f"4주 {c4:+.1f}%, 13주 {c13:+.1f}% 변했습니다. "
        f"최근 핵심 뉴스 {news_n}건과 수집 신호를 함께 확인하세요. "
        f"가격 예측 모델은 검증 결과 **{ctx['verdict']}**이어서 방향 전망은 제공하지 않습니다."
    )
    tone = "pos" if c4 is not None and c4 > 3 else "neg" if c4 is not None and c4 < -3 else "neu"
    return {"headline": f"주가지수 4주 {c4:+.1f}%", "summary": summary, "tone": tone,
            "key_signals": ctx["allowed"][:2]}


# ──────────────────────────────────────────────────────────────────────────────
# v2.4 — "왜 불합격인가" 설명 (Gemini) + 숫자 안전장치
# 불합격 예측도 화면에 보여주되, 이유를 쉬운 말로 붙인다. LLM 이 숫자를 잘못 옮기면
# 거짓 설명이 되므로, 설명 속 숫자가 입력 수치에 없으면 설명 전체를 버린다.
# ──────────────────────────────────────────────────────────────────────────────
def validation_facts(v: dict) -> dict:
    """설명에 쓸 검증 수치만 추린다 (이 밖의 숫자는 설명에 쓸 수 없음)."""
    facts = {"데이터_주수": v["dataWeeks"], "현재_지수_pt": v.get("current", {}).get("value"),
             "합격기준_p": 0.05}
    for x in v["variants"]:
        o, pr = x["overall"], x["procurement"]
        f4 = next((f for f in x.get("forecast", []) if f["h"] == 4), None)
        facts[x["name"]] = {
            "과거_예측_횟수": o["n"], "모델_평균오차_pct": o["modelMape"], "기준선_평균오차_pct": o["naiveMape"],
            "기준선을_이긴_비율_pct": o["winRate"], "p값": o["pValue"],
            "오르내림_적중률_pct": o["dirAcc"], "항상_오른다_찍기_적중률_pct": o["alwaysUpDirAcc"],
            "예측이_실제보다_낮았던_비율_pct": o.get("underRate"),
            "모델대로_4주_대기시_구매단가_변화_pct": pr["modelPct"], "대기_신호_횟수": pr["waitCount"],
            "대기가_옳았던_횟수": pr["waitCorrect"],
            "지금_4주뒤_예측_pt": f4 and f4["value"], "지금_4주뒤_예측_변화_pct": f4 and f4["changePct"],
        }
    return facts


def _fact_numbers(obj) -> set[float]:
    out = set()
    if isinstance(obj, dict):
        for v in obj.values():
            out |= _fact_numbers(v)
    elif isinstance(obj, (int, float)) and obj is not None:
        out.add(abs(float(obj)))
    return out


def unknown_numbers(text: str, facts: dict) -> list[str]:
    """설명 속 숫자 중 입력 수치(반올림 허용)나 예측 기간(1~7주)으로 설명되지 않는 것."""
    allowed = _fact_numbers(facts) | {float(h) for h in range(1, 8)}
    bad = []
    for tok in re.findall(r"\d+(?:[.,]\d+)*", text):
        x = float(tok.replace(",", ""))
        # 1 이상인 값만 반올림 허용 — p 값처럼 작은 수는 줄여 쓰면 뜻이 달라진다 (0.146 → 0.1 금지)
        if not any(abs(x - a) < 1e-9 or (a >= 1 and (abs(x - round(a, 1)) < 1e-9 or abs(x - round(a)) < 1e-9))
                   for a in allowed):
            bad.append(tok)
    return bad


def explain_validation() -> dict:
    if not VALIDATION.exists():
        return {"status": "failed", "text": "", "model": "", "reason": "검증 결과 없음"}
    v = json.loads(VALIDATION.read_text())
    facts = validation_facts(v)
    prompt = f"""너는 데이터 분석 결과를 비전문가에게 설명하는 사람이다.
아래는 메모리 3사 주가지수(실제 DRAM 가격이 아닌 대용 지표)를 예측하는 AI 모델의 검증 결과다.
판정: {v['verdict']} (합격 기준: {v['passRule']}). 기준선 = "{v['baseline']}".

검증 수치(JSON):
{json.dumps(facts, ensure_ascii=False, indent=1)}

용어 (반드시 이 뜻으로 써라):
- p값 = 모델과 기준선의 실력이 같다고 가정할 때, 모델이 이만큼 이길 확률. 작을수록 '우연이 아니라 진짜 낫다'는 뜻이며
  0.05 미만이어야 합격. p값을 '우연이 아닐 확률'이나 '맞을 확률'로 설명하지 마라.
- 평균오차 = 예측이 실제와 평균 몇 % 어긋났는지. 작을수록 좋다.

규칙:
- 이 예측이 왜 {v['verdict']}인지 쉬운 한국어 4~5문장으로 설명하라. 다음 순서를 지켜라:
  ① 판정과 기준 (평균오차 비교, p값)
  ② 원인 — '예측이_실제보다_낮았던_비율'과 '오르내림_적중률'을 '항상_오른다_찍기_적중률'과 비교해,
     모델이 어떤 식으로 틀렸는지(예: 오르는 시장을 계속 낮게 봄) 설명
  ③ 데이터 한계 — 데이터가 '데이터_주수'주뿐이고, 예측 대상이 실제 DRAM 가격이 아닌 주가 대용 지표라는 점
  ④ 두 방식의 지금 4주 뒤 예측이 서로 다르면 그 사실
- 숫자는 위 JSON 에 있는 값만 써라. 1 이상은 소수 첫째 자리 반올림 가능, p 값 등 1 미만 값은 그대로 써라. 새 숫자를 계산하거나 만들지 마라.
- 두 방식의 지금 예측이 서로 다르면 그 사실도 짚어라.
- 방식 이름은 JSON 의 이름('앱이 쓰던 방식 (가격 수준 예측)', '개선 시도 (변화율 예측)')대로 써라. '현재 앱이 쓰는 방식' 같은 표현 금지.
- 매수·매도·구매 시점 권유 금지. 과장 금지.
JSON 으로만 답하라: {{"explanation": "..."}}"""
    obj, source = call_gemini(prompt)
    text = ((obj or {}).get("explanation") or "").strip()
    if not text:
        return {"status": "failed", "text": "", "model": source, "reason": "Gemini 응답 없음"}
    bad = unknown_numbers(text, facts)
    if bad:
        # 입력에 없는 숫자가 하나라도 있으면 거짓 설명일 수 있으므로 쓰지 않는다
        return {"status": "rejected", "text": "", "model": source,
                "reason": f"입력에 없는 숫자 {bad[:5]} — 설명을 표시하지 않음"}
    return {"status": "ok", "text": text, "model": source, "reason": None}


def main():
    print("[1/3] 컨텍스트 빌드…")
    prompt, ctx = build_prompt()
    print(f"  {UNIT_LABEL} {ctx['current']} pt · 4주 {ctx['change4w']:+.1f}% · 예측 검증 {ctx['verdict']}")
    print(f"  신호 {len(ctx['signals'])}개 · 거시 {len(ctx['macro'])}개 · 뉴스 {len(ctx['news'])}건")

    print("[2/3] LLM 요약 (Gemini)…")
    obj, source = call_gemini(prompt)
    if not obj:
        print(f"  ⚠️  {source} → 휴리스틱 fallback")
        obj, source = heuristic(ctx), "휴리스틱 (LLM 모두 실패)"

    headline = (obj.get("headline") or "").strip()[:50]
    summary = (obj.get("summary") or "").strip()
    # 완결 문장 보장 — 마침표 없이 끝나면 추가, 과도하게 길면 마지막 마침표까지
    if summary and not summary.rstrip().endswith((".", "!", "?", "다", "요")):
        summary = summary.rstrip(" ,;:·…") + "."
    if len(summary) > 400:
        cut = summary[:400].rfind(".")
        summary = summary[:cut + 1] if cut > 200 else summary[:380]
    tone = (obj.get("tone") or "neu").lower()
    if tone not in {"pos", "neu", "neg"}:
        tone = "neu"
    # 입력에 있던(갱신 중단이 아닌) 신호 ID 만 허용 — LLM 이 화면에 없는 신호를 대는 것 방지
    key_signals = [s for s in (obj.get("key_signals") or []) if s in ctx["allowed"]][:3]

    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "model": source,
        "headline": headline,
        "summary": summary,
        "tone": tone,
        "keySignals": key_signals,
        "context": {k: ctx[k] for k in ("current", "change1w", "change4w", "change13w", "verdict")},
        "validationExplanation": explain_validation(),
    }
    print("[3/3] 저장")
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ {OUT.relative_to(ROOT)} · 모델: {source}")
    print(f"     headline: {headline}")
    print(f"     summary ({len(summary)}자): {summary}")
    print(f"     tone={tone} · keySignals={key_signals}")
    ve = payload["validationExplanation"]
    print(f"  {'✅' if ve['status'] == 'ok' else '⚠️ '} 불합격 이유 설명: {ve['status']} · {ve['model']}"
          f"{' · ' + ve['reason'] if ve['reason'] else ''}")
    if ve["text"]:
        print(f"     {ve['text']}")


if __name__ == "__main__":
    main()
