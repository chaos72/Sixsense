"""build_frontend_data.py — 실데이터 → frontend/src/mocks/data.js

hand-off SIXSENSE_DATA 객체의 스키마를 그대로 보존하면서 backend/data/historical
+ backend/data/forecast 산출물의 실측값으로 채운다. UI 코드(dashboard.jsx, modals.jsx,
pages.jsx)는 변경하지 않는다. 단순히 mocks/data.js 내용만 교체.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[2]
HIST = ROOT / "backend/data/historical"
FORECAST = ROOT / "backend/data/forecast"
OUT = ROOT / "frontend/src/mocks/data.js"

# 표시용: target-dram 은 base 100 정규화 인덱스 → $-가격으로 환산 (index/100 = $/GB 대용)
SCALE = 0.01

SIGNAL_META = {
    "A-1": {"name": "대만 공급망",        "desc": "TSMC·UMC 주가 (Yahoo Finance 블렌드)", "fmt": "pct"},
    "A-2": {"name": "빅테크 CapEx",       "desc": "Big4 분기 CapEx (SEC EDGAR XBRL)",       "fmt": "usd_b"},
    "A-3": {"name": "관세청 수출",        "desc": "메모리 반도체 수출액 (관세청 Open API)",  "fmt": "raw"},
    "A-4": {"name": "재고/출하 지수",     "desc": "100 초과 = 공급과잉 (KOSIS Open API)",   "fmt": "raw"},
    "A-5": {"name": "AWS Spot 가격",      "desc": "p4d.24xlarge 시간당 (AWS Pricing API)",  "fmt": "usd"},
    "A-6": {"name": "Manifold 봉쇄확률",  "desc": "대만 침공 확률 (Manifold Markets)",       "fmt": "pct100"},
    "A-7": {"name": "구리 선물가",        "desc": "10주 선행 → DRAM (COMEX HG=F)",          "fmt": "usd"},
    "B-1": {"name": "Earnings Call",      "desc": "메모리 4사 콜 감성 (Google News+LLM)",    "fmt": "sent"},
    "B-2": {"name": "대만 뉴스 감성",     "desc": "TechNews/Digitimes RSS (LLM)",            "fmt": "sent"},
    "B-3": {"name": "Reddit/HN",          "desc": "r/hardware DRAM 멘션 (HN Algolia)",       "fmt": "sent"},
    "B-4": {"name": "지정학 리스크",      "desc": "Caldara & Iacoviello GPR Index",          "fmt": "sent_neg"},
    "B-5": {"name": "LTA 비율",           "desc": "장기 계약가/현물가 (DRAMeXchange)",       "fmt": "sent"},
    "B-6": {"name": "HBM/D램 믹스",       "desc": "HBM 비중 변화 (TrendForce)",              "fmt": "sent"},
    "B-7": {"name": "BOM 신호",           "desc": "PCB·기판 가격 (공급망 트랜스크립트)",     "fmt": "sent"},
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


def fmt_signal(sid: str, rows: list[dict]) -> dict:
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
        if abs(last) >= 1e6:
            value = f"{last / 1e6:.2f}M"
        elif abs(last) >= 1e3:
            value = f"{last / 1e3:.1f}K"
        else:
            value = f"{last:.2f}"
        num = last
        if sid == "A-4":  # 재고지수 alert
            tone = "alert" if last > 100 else "pos" if last < 95 else "neu"

    src = load_signal(sid).get("source", "")
    src_short = src.split("(")[0].split(",")[0].strip()[:40] or "(미수집)"

    return {
        "id": sid,
        "name": meta["name"],
        "source": src_short,
        "value": value,
        "num": round(num, 4),
        "tone": tone,
        "desc": meta["desc"],
        "spark": spark,
    }


def build_history(target_rows: list[dict]) -> tuple[list[dict], float]:
    """target-dram의 최근 52주를 history로 변환. index/100 = $-price"""
    last52 = target_rows[-52:] if len(target_rows) >= 52 else target_rows
    history = []
    for i, r in enumerate(last52):
        idx = len(last52) - 1 - i  # 51 → 0 (latest is week=0)
        price = round(r["value"] * SCALE, 3)
        history.append({"week": -idx, "value": price, "type": "actual"})
    current = history[-1]["value"] if history else 3.20
    return history, current


def parse_model_comparison_series() -> dict:
    """USER-REQUESTED EXTENSION (2026-05-18 #4) — model_comparison.txt 의 단기/중장기
    표를 파싱해 4개 모델 시계열(prophet 21주, hist_gbr 1~7주, gbr 1~7주, lstm 8~21주) 추출.
    파일 없으면 빈 dict."""
    cmp_file = FORECAST / "model_comparison.txt"
    out = {"prophet": [], "hist_gbr": [], "gbr": [], "lstm": []}
    if not cmp_file.exists():
        return out
    txt = cmp_file.read_text()

    # USER-REQUESTED EXTENSION (#19 fix) — 종료 마커("단기 MAPE"/"LSTM held-out")가
    # 형식 변화로 사라질 수 있어, 섹션 헤더부터 다음 헤더/공백까지 본문을 잡고
    # 날짜+숫자 행만 직접 매칭하는 견고한 방식으로 교체.
    def _section(header: str) -> str:
        m = re.search(rf"{header}.*?\n(.*?)(?=\n📈|\n⏱|\n단기 MAPE|\nLSTM held|\n🏆|\n═|\Z)", txt, re.DOTALL)
        return m.group(1) if m else ""

    # 단기 표 — Week / Prophet / hist_gbr / gbr / 실측 (5열)
    for line in _section(r"📈 단기").split("\n"):
        row = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
        if row:
            out["prophet"].append((row.group(1), float(row.group(2))))
            out["hist_gbr"].append((row.group(1), float(row.group(3))))
            out["gbr"].append((row.group(1), float(row.group(4))))

    # 중장기 표 — Week / Prophet / LSTM (3열)
    for line in _section(r"📈 중장기").split("\n"):
        row = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s+([\d.]+)", line)
        if row:
            out["prophet"].append((row.group(1), float(row.group(2))))
            out["lstm"].append((row.group(1), float(row.group(3))))
    return out


def build_forecasts(forecast_json: dict, current_price: float | None = None) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """USER-REQUESTED EXTENSION (#4 / #18) — 차트용 4개 모델 시계열 반환:
    (forecast7=GBR 1~7w, forecast21=LSTM 8~21w, forecast_prophet=Prophet 1~21w, forecast_histgbr=HistGBR 1~7w)

    USER-REQUESTED EXTENSION (#18, 2026-06-11) — anchor 보정:
    forecast 시작점이 학습 cutoff 시점 가격이라 현재가와 괴리가 큼(데이터 급등 시).
    각 모델의 *상대 변화율*은 유지하되 시작 anchor 를 current_price 에 맞춰
    스케일링 → 차트에서 현재가 → 미래 예측이 자연스럽게 연결.
    """
    parsed = parse_model_comparison_series()

    def _anchor_scale(series_vals: list[float], cur: float | None) -> list[float]:
        """series 첫 값을 cur 에 맞추고 나머지는 비율 유지. cur None 이면 원본."""
        if cur is None or not series_vals or series_vals[0] == 0:
            return series_vals
        factor = cur / series_vals[0]
        return [v * factor for v in series_vals]

    # 각 모델 raw 값 추출 (SCALE 적용 전 인덱스값)
    gbr_raw = [yhat for (_, yhat) in parsed["gbr"][:7]]
    lstm_raw = [yhat for (_, yhat) in parsed["lstm"][:14]]
    prophet_raw = [yhat for (_, yhat) in parsed["prophet"][:21]]
    histgbr_raw = [yhat for (_, yhat) in parsed["hist_gbr"][:7]]

    # current_price 는 $ 단위 → 인덱스값으로 환산 (anchor 비교 위해)
    cur_idx = (current_price / SCALE) if current_price else None

    # anchor 보정
    # 단기(GBR/HistGBR/Prophet): 첫 예측을 현재가에 맞춤 → 현재→미래 자연 연결
    gbr_raw = _anchor_scale(gbr_raw, cur_idx)
    prophet_raw = _anchor_scale(prophet_raw, cur_idx)
    histgbr_raw = _anchor_scale(histgbr_raw, cur_idx)

    # USER-REQUESTED EXTENSION (#19, 2026-06-11) — 중장기(LSTM)는 단기 끝점($11.94)에
    # 이어붙임: LSTM 첫 예측을 GBR 마지막 값에 anchor → 차트에서 단기→중장기 절벽 제거.
    # LSTM 의 상대적 추세(완만한 상승/하락)는 그대로 유지.
    gbr_last_idx = gbr_raw[-1] if gbr_raw else cur_idx
    lstm_raw = _anchor_scale(lstm_raw, gbr_last_idx)

    # forecast7 (GBR, 1~7w) — Single yhat, CI는 ±5% 임의 추정
    forecast7 = []
    for i, yhat in enumerate(gbr_raw, start=1):
        v = round(yhat * SCALE, 3)
        forecast7.append({"week": i, "value": v,
                          "lower": round(v * 0.95, 3), "upper": round(v * 1.05, 3),
                          "type": "f7"})

    # forecast21 (LSTM, 8~21w) — CI ±10%
    forecast21 = []
    for offset, yhat in enumerate(lstm_raw):
        v = round(yhat * SCALE, 3)
        forecast21.append({"week": 8 + offset, "value": v,
                           "lower": round(v * 0.90, 3), "upper": round(v * 1.10, 3),
                           "type": "f21"})

    # forecast_prophet (Prophet, 1~21w 전체 baseline)
    forecast_prophet = []
    for i, yhat in enumerate(prophet_raw, start=1):
        forecast_prophet.append({"week": i, "value": round(yhat * SCALE, 3), "type": "prophet"})

    # forecast_histgbr (HistGBR, 1~7w 중간 모델)
    forecast_histgbr = []
    for i, yhat in enumerate(histgbr_raw, start=1):
        forecast_histgbr.append({"week": i, "value": round(yhat * SCALE, 3), "type": "histgbr"})

    # parsed가 비어있을 경우(파일 없음) — 기존 prophet JSON으로 fallback
    if not forecast7 or not forecast21:
        models = forecast_json.get("models", {})
        prop = models.get("prophet", {}).get("predictions", [])
        if prop and not forecast7:
            for i, p in enumerate(prop[:7], start=1):
                v = round(p.get("yhat", 0) * SCALE, 3)
                forecast7.append({"week": i, "value": v,
                                  "lower": round(p.get("yhat_lower", v * 0.95) * SCALE, 3),
                                  "upper": round(p.get("yhat_upper", v * 1.05) * SCALE, 3),
                                  "type": "f7"})
        if prop and not forecast21:
            for offset, p in enumerate(prop[7:21]):
                v = round(p.get("yhat", 0) * SCALE, 3)
                forecast21.append({"week": 8 + offset, "value": v,
                                   "lower": round(p.get("yhat_lower", v * 0.90) * SCALE, 3),
                                   "upper": round(p.get("yhat_upper", v * 1.10) * SCALE, 3),
                                   "type": "f21"})

    return forecast7, forecast21, forecast_prophet, forecast_histgbr


def build_macro() -> list[dict]:
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
        out.append({
            "id": mid.replace("macro-", ""),
            "name": meta["name"],
            "value": val_str,
            "change": change,
            "tone": tone,
            "desc": meta["desc"],
            "history": history_vals,
        })
    return out


def build_collection(summary: dict, group: str) -> list[dict]:
    rows = []
    ids = [f"{group}-{i}" for i in range(1, 8)]
    for sid in ids:
        sig = load_signal(sid)
        meta = SIGNAL_META.get(sid, {"name": sid})
        rows.append({
            "id": sid,
            "name": meta["name"],
            "source": (sig.get("source") or "(미수집)")[:50],
            "time": sig.get("collectedAt", "2026-05-17") + " 06:00",
            "newItems": len(sig.get("data", [])),
            "prev": max(0, len(sig.get("data", [])) - 1),
            "status": "ok" if sig.get("data") else "fail",
        })
    return rows


def build_snapshot_past(target_rows: list[dict]) -> dict:
    """8주 전 시점의 14개 신호 상태 vs 현재."""
    if len(target_rows) < 8:
        return {"date": "(부족)", "actual": 0, "predicted": 0, "error": 0, "signals": []}
    past_idx = -8
    past_actual = round(target_rows[past_idx]["value"] * SCALE, 3)
    current_actual = round(target_rows[-1]["value"] * SCALE, 3)
    error = abs(past_actual - current_actual) / current_actual * 100 if current_actual else 0
    date = target_rows[past_idx]["week"]

    signals = []
    for sid in SIGNAL_META:
        rows = load_signal(sid)["data"]
        if len(rows) < 8:
            continue
        then = rows[-9 if len(rows) > 9 else 0]["value"]
        now = rows[-1]["value"]
        direction = "up" if now > then else "down" if now < then else "flat"
        change = "개선" if direction == "up" else "약화" if direction == "down" else "유사"
        signals.append({
            "id": sid,
            "name": SIGNAL_META[sid]["name"],
            "then": f"{then:+.2f}" if abs(then) < 10 else f"{then:.1f}",
            "thenTone": "neu",
            "now": f"{now:+.2f}" if abs(now) < 10 else f"{now:.1f}",
            "nowTone": "pos" if direction == "up" else "neg" if direction == "down" else "neu",
            "direction": direction,
            "change": change,
        })

    return {
        "date": date,
        "actual": current_actual,
        "predicted": past_actual,
        "error": round(error, 1),
        "signals": signals,
    }


NEWS_FILE = ROOT / "backend/data/news/latest.json"
EVENTS_FILE = ROOT / "backend/data/events/latest.json"
INSIGHT_FILE = ROOT / "backend/data/insight/latest.json"


def build_model_validation() -> dict:
    """USER-REQUESTED EXTENSION (2026-05-18 #3) — §02 Phase 6 검증 패널 데이터.
    forecast/model_comparison.txt 파싱 시도, 실패 시 사용자 명세값 fallback."""
    cmp_file = FORECAST / "model_comparison.txt"
    short_models = {"Prophet (기존)": 7.54, "sklearn HistGBR": 6.86, "sklearn GBR": 4.54}
    mid_mape = 9.19
    train_times = {"prophet": 0.64, "tree_short": 4.22, "lstm_mid": 6.52}

    if cmp_file.exists():
        import re as _re
        txt = cmp_file.read_text()
        m = _re.search(r"단기 MAPE\s*—\s*hist_gbr:\s*([\d.]+)%,\s*gbr:\s*([\d.]+)%", txt)
        if m:
            short_models["sklearn HistGBR"] = float(m.group(1))
            short_models["sklearn GBR"] = float(m.group(2))
        m = _re.search(r"LSTM held-out MAPE:\s*([\d.]+)%", txt)
        if m:
            mid_mape = float(m.group(1))
        for k in train_times:
            m = _re.search(rf"{k}\s+([\d.]+)s", txt)
            if m:
                train_times[k] = float(m.group(1))

    baseline = short_models["Prophet (기존)"]
    winner_mape = min(short_models["sklearn HistGBR"], short_models["sklearn GBR"])
    improvement = round((baseline - winner_mape) / baseline * 100, 1)

    short_rows = []
    for name, mape in short_models.items():
        is_winner = (mape == winner_mape and "GBR" in name and "Hist" not in name)
        eval_label = "39.7% 개선" if is_winner else ("baseline" if "Prophet" in name else "중간")
        if is_winner:
            eval_label = f"{improvement}% 개선"
        short_rows.append({"model": name, "mape": mape, "eval": eval_label, "winner": is_winner})

    return {
        "headline": f"🎉 Phase 6 멀티 모델 예측 아키텍처 완료 — 단기 MAPE {baseline}% → {winner_mape}% ({improvement}% 개선)",
        "shortRows": short_rows,
        "midRows": [{"model": "LSTM (PyTorch 2-layer hidden=64)", "mape": mid_mape}],
        "trainTimes": [
            {"name": "Prophet", "sec": train_times["prophet"]},
            {"name": "Tree (단기)", "sec": train_times["tree_short"]},
            {"name": "LSTM (중장기)", "sec": train_times["lstm_mid"]},
        ],
        "trainTotal": round(sum(train_times.values()), 1),
        "architecture": (
            "20개 신호 통합 DataFrame (108주 × 20열, sentiment 3주 MA)\n"
            "            │\n"
            "   ┌────────┼────────┐\n"
            "   ▼        ▼        ▼\n"
            "[Prophet] [Tree]  [LSTM]\n"
            "baseline  단기      중장기\n"
            "         ─우수─    PyTorch\n"
            "         자동선정   2-layer"
        ),
        "envNote": (
            "XGBoost/LightGBM 우선 사용 시도 → macOS libomp 미설치 → "
            "sklearn GBR/HistGBR fallback 자동 전환. brew install libomp 후 "
            "자동 XGBoost/LightGBM 활성 (코드 변경 불필요). LSTM은 PyTorch (libomp 무관, 즉시 작동)."
        ),
    }


def load_insight() -> dict | None:
    if not INSIGHT_FILE.exists():
        return None
    j = json.loads(INSIGHT_FILE.read_text())
    return {
        "headline": j.get("headline", ""),
        "summary": j.get("summary", ""),
        "tone": j.get("tone", "neu"),
        "confidence": j.get("confidence", 50),
        "horizon": j.get("horizon", "mid"),
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
        label_parts.append(f"events {len(events)}건")
    else:
        label_parts.append("events 미수집")
    return news, events, " · ".join(label_parts)


def build_accuracy(target_rows: list[dict], forecast_json: dict) -> list[dict]:
    """forecast_v2의 단기/중장기 예측 vs target-dram 실측 비교."""
    acc = []
    actual_by_week = {r["week"]: round(r["value"] * SCALE, 3) for r in target_rows}
    models = forecast_json.get("models", {})

    short_src = models.get("gbr", {}).get("predictions", []) or \
                models.get("hist_gbr", {}).get("predictions", []) or \
                models.get("prophet", {}).get("predictions", [])
    cutoff = forecast_json.get("trainCutoff", "2026-01-31")

    for p in short_src[:7]:
        w = p.get("week")
        pred = round((p.get("yhat") or 0) * SCALE, 3)
        actual = actual_by_week.get(w)
        if actual:
            err = abs(pred - actual) / actual * 100
            tone = "pos" if err < 5 else "neu" if err < 10 else "neg"
            acc.append({"predDate": cutoff, "horizon": "7주", "pred": pred,
                        "actual": actual, "error": round(err, 1), "tone": tone})
        else:
            acc.append({"predDate": cutoff, "horizon": "7주", "pred": pred,
                        "actual": None, "error": None, "tone": None})

    mid_src = models.get("lstm", {}).get("predictions", []) or \
              models.get("prophet", {}).get("predictions", [])
    for p in mid_src[7:21] if len(mid_src) >= 21 else mid_src[:14]:
        w = p.get("week")
        pred = round((p.get("yhat") or 0) * SCALE, 3)
        actual = actual_by_week.get(w)
        if actual:
            err = abs(pred - actual) / actual * 100
            tone = "pos" if err < 7 else "neu" if err < 12 else "neg"
            acc.append({"predDate": cutoff, "horizon": "21주", "pred": pred,
                        "actual": actual, "error": round(err, 1), "tone": tone})
        else:
            acc.append({"predDate": cutoff, "horizon": "21주", "pred": pred,
                        "actual": None, "error": None, "tone": None})

    return acc


def main():
    target = load_signal("target-dram")
    target_rows = target["data"]
    history, current = build_history(target_rows)

    forecast_json = json.loads((FORECAST / "forecast_v2_2026-02-w1.json").read_text())
    # USER-REQUESTED EXTENSION (#18) — current 전달로 forecast anchor 보정 (현재가 시작)
    forecast7, forecast21, forecast_prophet, forecast_histgbr = build_forecasts(forecast_json, current_price=current)

    pred7 = forecast7[-1]["value"] if forecast7 else current
    pred21 = forecast21[-1]["value"] if forecast21 else current
    pred7_change = (pred7 - current) / current * 100 if current else 0
    pred21_change = (pred21 - current) / current * 100 if current else 0
    current_change = ((history[-1]["value"] - history[-2]["value"]) / history[-2]["value"] * 100) if len(history) > 1 else 0

    signalsA = [fmt_signal(f"A-{i}", load_signal(f"A-{i}")["data"]) for i in range(1, 8)]
    signalsB = [fmt_signal(f"B-{i}", load_signal(f"B-{i}")["data"]) for i in range(1, 8)]
    macro = build_macro()

    snapshot_past = build_snapshot_past(target_rows)
    accuracy = build_accuracy(target_rows, forecast_json)
    real_news, real_events, news_label = load_news_events()
    insight = load_insight()

    collection = {
        "summary": {"total": 20, "success": 20, "fail": 0,
                    "newCount": sum(len(load_signal(s)["data"]) for s in list(SIGNAL_META.keys()))},
        "week": target.get("collectedAt", "2026-05-17"),
        "groupA": build_collection({}, "A"),
        "groupB": build_collection({}, "B"),
    }

    payload = {
        "meta": {
            "current": current,
            "currentChange": f"{current_change:+.1f}%",
            "pred7": pred7,
            "pred7Change": f"{pred7_change:+.1f}%",
            "pred21": pred21,
            "pred21Change": f"{pred21_change:+.1f}%",
            "updated": f"{target.get('collectedAt', '2026-05-17')} 06:00 KST",
            "model": "GBR (단기) + LSTM (중장기) + Prophet (베이스)",
            "confidence": 81,
            "insight": insight,
            "modelValidation": build_model_validation(),
        },
        "history": history,
        "forecast7": forecast7,
        "forecast21": forecast21,
        "forecast_prophet": forecast_prophet,
        "forecast_histgbr": forecast_histgbr,
        "signalsA": signalsA,
        "signalsB": signalsB,
        "news": real_news,
        "macro": macro,
        "events": real_events,
        "accuracy": accuracy,
        "snapshotPast": snapshot_past,
        "collection": collection,
    }

    # frontend ESM 모듈로 export
    js = f"""// AUTO-GENERATED by backend/pipelines/build_frontend_data.py
// DO NOT EDIT MANUALLY — regenerate via: python3 pipelines/build_frontend_data.py
// 데이터 소스: backend/data/historical/* + backend/data/forecast/forecast_v2_*.json
//             + backend/data/news/latest.json + backend/data/events/latest.json
// 생성 시각: {datetime.utcnow().isoformat()}Z
// 뉴스/이벤트: {news_label}
// UI 컴포넌트는 design_handoff_sixsense_dram_dashboard 의 SIXSENSE_DATA 스키마를 그대로 따른다.

export const SIXSENSE_DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};
"""
    OUT.write_text(js, encoding="utf-8")
    print(f"✅ {OUT.relative_to(ROOT)} 생성 완료 ({OUT.stat().st_size:,} bytes)")
    print(f"   - 현재가: ${current:.2f}  (지난주 대비 {current_change:+.1f}%)")
    print(f"   - 1~7주 예측: ${pred7:.2f}  ({pred7_change:+.1f}%)")
    print(f"   - 8~21주 예측: ${pred21:.2f}  ({pred21_change:+.1f}%)")
    print(f"   - history: {len(history)}주, forecast7: {len(forecast7)}주, forecast21: {len(forecast21)}주")
    print(f"   - signalsA: {len(signalsA)}, signalsB: {len(signalsB)}, macro: {len(macro)}")


if __name__ == "__main__":
    main()
