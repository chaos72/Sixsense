"""gemini_client.py — 파이프라인 공용 LLM 호출 (Google Gemini 무료 티어 전용).

LLM 정책: GPT·Gemini·Claude 중 하나만, 무료로 — API 무료 사용분이 있는 것은 Gemini 뿐이라 단독 사용.
중국 모델·오픈소스 모델은 사용하지 않는다.

무료 한도는 '모델별'로 따로 잡힌다. 그래서 한 모델이 막히면 다음 모델로 넘어가고,
하루 한도 초과(429 PerDay)·폐기(404) 모델은 이번 실행 동안 다시 부르지 않는다.
분당 제한(429 PerMinute)·과부하(503)는 일시적이므로 다음 호출에서 다시 시도한다.
"""
import os

import requests

# 품질이 중요한 작업(번역·뉴스 분류·인사이트) — 상위 flash 모델부터.
QUALITY_MODELS = (
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
)
# 대량 단순 작업(감성 점수 — 실행당 수십 회) — lite 부터 써서 flash 한도를 번역·인사이트용으로 남긴다.
BULK_MODELS = (
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
)

_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
_exhausted: set = set()


def available(models=QUALITY_MODELS) -> tuple:
    """이번 실행에서 아직 하루 한도가 남은(또는 폐기되지 않은) 모델만."""
    return tuple(m for m in models if m not in _exhausted)


def gemini_generate(prompt: str, models=QUALITY_MODELS, max_tokens: int = 4096,
                    temperature: float = 0.0, json_mode: bool = False,
                    timeout: int = 60) -> tuple:
    """성공 시 (텍스트, 사용 모델), 전부 실패 시 (None, 실패 사유 요약)."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return None, "GEMINI_API_KEY 없음"

    config = {"maxOutputTokens": max_tokens, "temperature": temperature}
    if json_mode:
        config["responseMimeType"] = "application/json"

    errors = []
    for model in models:
        if model in _exhausted:
            continue
        try:
            r = requests.post(_URL.format(model), params={"key": key},
                              json={"contents": [{"parts": [{"text": prompt}]}],
                                    "generationConfig": config},
                              timeout=timeout)
        except requests.RequestException as e:
            errors.append(f"{model} 네트워크({str(e)[:40]})")
            continue

        if r.status_code == 200:
            cand = (r.json().get("candidates") or [{}])[0]
            text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])).strip()
            if text:
                return text, model
            # 2.5/3 flash 는 답하기 전 '생각'에 출력 토큰을 쓰므로 한도가 작으면 빈 응답이 올 수 있음
            errors.append(f"{model} 빈 응답({cand.get('finishReason')})")
            continue

        if r.status_code == 404 or (r.status_code == 429 and "PerDay" in r.text):
            _exhausted.add(model)
        errors.append(f"{model} HTTP {r.status_code}")

    return None, "; ".join(errors) or "사용 가능한 Gemini 모델 없음(이번 실행 한도 소진)"
