"""재발 방지 시험 (v2.6) — 2026-09 에 실제로 일어난 사고 하나마다 시험 하나 이상.

시험 이름의 사고 번호는 CHANGELOG 버전과 대응한다. 새 사고가 나면 여기에 시험을 먼저 추가한다.
외부 API·Gemini 는 가짜 응답으로 대체 — 인터넷 없이 수 초 안에 끝난다.
"""
import json
import time
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
import pytest
import requests

from conftest import FakeResponse


def _rows(pairs):
    return [{"week": w, "value": v} for w, v in pairs]


# ───────────── v2.3.2 · 과거 값이 실행마다 바뀌던 사고 (B-6 이틀 사이 38주 중 29주 변경) ─────────────
def test_v232_마감된_주는_새_값이_와도_바뀌지_않음(ac, write_signal_file, monkeypatch):
    write_signal_file("B-6", _rows([("2026-09-07", 0.8), ("2026-09-14", 0.5)]), finalThrough="2026-09-14")
    monkeypatch.setattr(ac, "_last_completed_week", lambda: "2026-09-14")
    merged, _ = ac._merge_frozen("B-6", _rows([("2026-09-07", -0.9), ("2026-09-14", -0.9), ("2026-09-21", 0.1)]))
    got = {r["week"]: r["value"] for r in merged}
    assert got["2026-09-07"] == 0.8 and got["2026-09-14"] == 0.5 and got["2026-09-21"] == 0.1


def test_v232_마감된_오래된_빈_주는_나중에_끼워넣지_않음(ac, write_signal_file, monkeypatch):
    write_signal_file("B-6", _rows([("2026-09-14", 0.5)]), finalThrough="2026-09-14")
    monkeypatch.setattr(ac, "_last_completed_week", lambda: "2026-09-14")
    merged, _ = ac._merge_frozen("B-6", _rows([("2025-07-07", 0.3)]))
    assert "2025-07-07" not in {r["week"] for r in merged}


def test_v232_첫_실행은_새_데이터를_그대로_씀(ac):
    merged, meta = ac._merge_frozen("B-9", _rows([("2026-09-14", 1.0)]))
    assert merged == _rows([("2026-09-14", 1.0)]) and meta["finalThrough"]


# ───────────── v2.5 오류1 · 채점 실패 주가 영구 빈칸이 되던 사고 ─────────────
def test_v25_실패한_주는_다음_실행에서_채워지고_그_뒤엔_고정(ac, write_signal_file, monkeypatch):
    write_signal_file("B-6", _rows([("2026-09-14", 0.5)]), finalThrough="2026-09-14")
    monkeypatch.setattr(ac, "_last_completed_week", lambda: "2026-09-21")
    merged, meta = ac._merge_frozen("B-6", _rows([("2026-09-28", 0.4)]))          # 9/21 채점 실패
    write_signal_file("B-6", merged, finalThrough=meta["finalThrough"])
    monkeypatch.setattr(ac, "_last_completed_week", lambda: "2026-09-28")
    merged, meta = ac._merge_frozen("B-6", _rows([("2026-09-21", 0.7)]))          # 다음 실행에서 성공
    assert {r["week"]: r["value"] for r in merged}.get("2026-09-21") == 0.7
    write_signal_file("B-6", merged, finalThrough=meta["finalThrough"])
    merged, _ = ac._merge_frozen("B-6", _rows([("2026-09-21", -0.9)]))           # 채워진 뒤엔 고정
    assert {r["week"]: r["value"] for r in merged}["2026-09-21"] == 0.7


def test_v25_전부_마감되면_Gemini를_부르지_않음(ac, write_signal_file, monkeypatch):
    write_signal_file("B-6", _rows([("2026-09-14", 0.5)]), finalThrough="2026-12-28")
    entry = {"published_parsed": time.struct_time((2026, 9, 15, 0, 0, 0, 1, 258, 0)), "title": "HBM demand", "summary": ""}
    monkeypatch.setattr(ac.feeds, "get_feed", lambda url: _feed([entry]))
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "START_D", date(2026, 1, 1))
    calls = []
    monkeypatch.setattr(ac, "_llm_sentiment", lambda *a, **k: calls.append(1) or 0.5)
    data, _, _ = ac._collect_ir_news_sentiment("B-6", "HBM", "HBM mix")
    assert calls == [] and data == []


def test_v232_Gemini가_전부_실패하면_키워드로_채우지_않고_파일_유지(ac, write_signal_file, monkeypatch):
    before = write_signal_file("B-6", _rows([("2026-09-14", 0.5)]), finalThrough="2026-09-07")
    entry = {"published_parsed": time.struct_time((2026, 9, 15, 0, 0, 0, 1, 258, 0)), "title": "HBM growth surge", "summary": ""}
    monkeypatch.setattr(ac.feeds, "get_feed", lambda url: _feed([entry]))
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "START_D", date(2026, 1, 1))

    def boom(*a, **k):
        raise EnvironmentError("Gemini 모의 실패")
    monkeypatch.setattr(ac, "_llm_sentiment", boom)
    monkeypatch.setitem(ac.COLLECTORS, "B-6", lambda: ac._collect_ir_news_sentiment("B-6", "HBM", "HBM mix"))
    r = ac.run_one("B-6")
    assert r["status"] == "needs_setup"
    assert json.loads((ac.HIST_DIR / "B-6.json").read_text())["data"] == before["data"]


# ───────────── v2.3.2 · 월간 통계가 실행 요일에 따라 다른 달 값을 넣던 사고 ─────────────
def test_v232_월간_통계는_목요일_금요일_실행_결과가_같음(ac, monkeypatch):
    monthly = [(date(2026, 4, 1), 1.0), (date(2026, 5, 1), 2.0)]
    out = []
    for end in (date(2026, 9, 24), date(2026, 9, 25)):
        monkeypatch.setattr(ac, "END_D", end)
        out.append(ac._ffill_monthly_to_weekly(monthly, start="2026-03-30"))
    assert out[0] == out[1]
    assert all(date.fromisoformat(r["week"]).weekday() == 0 for r in out[0])


# ───────────── v2.5 오류6 · 기준 날짜가 컴퓨터 현지 시간이던 사고 ─────────────
def test_v25_기준_날짜는_UTC(monkeypatch):
    """한국 월요일 새벽(UTC 로는 일요일)에 돌려도 끝나지 않은 주를 마감하지 않도록 기준 날짜는 UTC.
    현지 날짜와 UTC 날짜가 다른 순간을 흉내 내 모듈을 다시 읽고, UTC 날짜를 쓰는지 확인한다."""
    import importlib
    import auto_collectors
    monkeypatch.delenv("SIXSENSE_END", raising=False)

    class FakeDT(datetime):
        @classmethod
        def now(cls, tz=None):                       # UTC 로는 일요일 20:00, 한국은 월요일 05:00
            base = datetime(2026, 9, 27, 20, 0, tzinfo=timezone.utc)
            return base if tz is not None else base.replace(tzinfo=None) + (datetime(2026, 9, 28, 5) - datetime(2026, 9, 27, 20))

    class FakeDate(date):
        @classmethod
        def today(cls):
            return date(2026, 9, 28)                 # 현지(한국) 날짜
    import datetime as dtmod
    monkeypatch.setattr(dtmod, "datetime", FakeDT)
    monkeypatch.setattr(dtmod, "date", FakeDate)
    try:
        m = importlib.reload(auto_collectors)
        assert m.END_D == date(2026, 9, 27)           # UTC 날짜 (현지 날짜 9/28 이 아님)
    finally:
        monkeypatch.undo()
        importlib.reload(auto_collectors)


# ───────────── v2.5 오류2 · B-7·B-3 진행 중인 주가 0 으로 표시되던 사고 ─────────────
def test_v25_HN_점수는_끝난_주까지만_저장(ac, monkeypatch):
    monkeypatch.setattr(ac, "END_D", date(2026, 9, 21))       # 월요일 정기 실행
    monkeypatch.setattr(ac, "END", "2026-09-21")
    monkeypatch.setattr(ac, "START_D", date(2026, 8, 3))
    monkeypatch.setattr(ac, "START", "2026-08-03")
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac.requests, "get", lambda *a, **k: FakeResponse(
        {"hits": [{"created_at": "2026-09-15T10:00:00Z", "points": 5}]}))
    data, _, _ = ac.collect_B7_bom_hn()
    assert data[-1]["week"] == "2026-09-14" and data[-1]["value"] > 0
    data, _, _ = ac.collect_B3_reddit()
    assert max(r["week"] for r in data) == "2026-09-14"


def test_v25_HN_검색어_하나라도_실패하면_일부_합계를_저장하지_않음(ac, monkeypatch):
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def flaky(*a, **k):
        calls["n"] += 1
        return FakeResponse({"hits": []}, status=500 if calls["n"] == 2 else 200)
    monkeypatch.setattr(ac.requests, "get", flaky)
    with pytest.raises(requests.exceptions.HTTPError):
        ac.collect_B7_bom_hn()


# ───────────── v2.4.1 · A-4 가 엉뚱한 표의 임의 행(약 492만)이던 사고 ─────────────
GOOD_A4 = [{"PRD_DE": "202606", "DT": "88.7", "ITM_NM": "생산자제품 재고지수(원지수)", "C2_NM": "반도체 제조업"}]


@pytest.mark.parametrize("payload,ok", [
    (GOOD_A4, True),
    ([{"PRD_DE": "202606", "DT": "4923610", "ITM_NM": "품목별재고량", "C2_NM": "칼라강판"}], False),
    (GOOD_A4 + [dict(GOOD_A4[0], DT="90")], False),
    ([], False),
    ({"err": "20", "errMsg": "인증키 오류"}, False),
], ids=["정상", "엉뚱한_표", "같은_달_여러_행", "빈_응답", "오류_응답"])
def test_v241_A4_응답이_반도체_재고지수가_아니면_저장하지_않음(ac, monkeypatch, payload, ok):
    monkeypatch.setenv("KOSIS_API_KEY", "test")
    monkeypatch.setattr(ac.requests, "get", lambda *a, **k: FakeResponse(payload))
    if ok:
        data, _, src = ac.collect_A4_kosis()
        assert data and "반도체" in src
    else:
        with pytest.raises(RuntimeError):
            ac.collect_A4_kosis()


# ───────────── v2.5.1 · 관세청 차단을 '서비스 활성화 확인'으로 잘못 안내 / v2.5 · 네트워크 오류를 '설정 필요'로 ─────────────
def test_v251_A3_전부_연결_실패면_네트워크_오류로_보고(ac, monkeypatch):
    monkeypatch.setenv("KCS_API_KEY", "test")
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)

    def blocked(*a, **k):
        raise requests.exceptions.ConnectionError("Max retries exceeded")
    monkeypatch.setattr(ac.requests, "get", blocked)
    r = ac.run_one("A-3")
    assert r["status"] == "failed" and "네트워크" in r["reason"]


def test_v25_run_one은_네트워크_오류와_설정_오류를_구분(ac, monkeypatch):
    def net():
        raise requests.exceptions.ConnectionError("Connection aborted")

    def cfg():
        raise EnvironmentError("환경변수 X 미설정")
    monkeypatch.setitem(ac.COLLECTORS, "T-net", net)
    monkeypatch.setitem(ac.COLLECTORS, "T-cfg", cfg)
    assert ac.run_one("T-net")["status"] == "failed"
    assert ac.run_one("T-cfg")["status"] == "needs_setup"


# ───────────── v2.3.1 · A-1 '70/30' 이 실제로는 TSMC 98% 이던 사고 ─────────────
def test_v231_A1은_각각_정규화한_뒤_70_30(ac, monkeypatch):
    series = {"TSM": {"2026-01-05": 200.0, "2026-01-12": 400.0}, "UMC": {"2026-01-05": 10.0, "2026-01-12": 10.0}}
    for i in range(10):                                   # 공통 주 10주 이상 필요
        w = pd.Timestamp("2026-01-19") + pd.Timedelta(weeks=i)
        series["TSM"][w.date().isoformat()] = 400.0
        series["UMC"][w.date().isoformat()] = 10.0
    monkeypatch.setattr(ac, "_yf_weekly", lambda t, start=None: series[t])
    data, _, _ = ac.collect_A1_taiwan_foundry()
    v = {r["week"]: r["value"] for r in data}
    assert v["2026-01-05"] == pytest.approx(100.0)
    assert v["2026-01-12"] == pytest.approx(0.7 * 200 + 0.3 * 100)   # TSM 2배, UMC 그대로 → 170


# ───────────── v2.4 / v2.5 · 불합격 이유 설명의 숫자 안전장치 오판 ─────────────
FACTS = {"데이터_주수": 67, "현재_지수_pt": 750.43, "합격기준_p": 0.05,
         "방식A": {"모델_평균오차_pct": 33.84, "기준선_평균오차_pct": 15.69, "p값": 0.686,
                 "지금_4주뒤_예측_pt": 749.25, "지금_4주뒤_예측_변화_pct": -3.12},
         "방식B": {"지금_4주뒤_예측_변화_pct": 10.37}}


@pytest.mark.parametrize("text,ok", [
    ("오차 33.84%, 기준선 15.69%", True),
    ("오차 33.8%와 15.7%", True),
    ("p값은 0.686입니다.", True),
    ("p값은 0.7입니다.", False),               # v2.4: 0.146 → 0.1 로 줄여 쓴 문장을 통과시켰던 사고
    ("정확도는 85%", False),
    ("18.15%포인트 더 틀렸다", False),
    ("1,200번", False),
    ("749.3 pt", True),                        # v2.4.1: 749.25 반올림을 거부했던 사고
    ("727.7pt로 하락할 것", False),            # 입력에 없는 수준값
    ("749.25pt로 하락할 것", True),            # v2.5: 수준값 뒤 '하락'을 거부했던 사고
    ("-3.12%", True), ("+3.12%", False), ("-10.37%", False),
    ("3.12% 하락", True), ("3.12% 상승", False), ("10.37% 절감", False), ("10.37% 상승", True),
])
def test_v24_v25_숫자_안전장치(text, ok):
    from build_insight import unknown_numbers
    assert (not unknown_numbers(text, FACTS)) == ok


def test_v25_설명에_틀린_숫자가_있으면_한_번_다시_쓰게_하고_두_번_틀리면_표시_안_함(tmp_path, monkeypatch):
    import build_insight as bi
    v = {"dataWeeks": 67, "current": {"week": "2026-09-21", "value": 750.43}, "verdict": "불합격",
         "passRule": "r", "baseline": "b", "variants": [
             {"name": "방식", "overall": {"n": 231, "modelMape": 33.84, "naiveMape": 15.69, "winRate": 15.2,
                                          "pValue": 0.686, "dirAcc": 32.0, "alwaysUpDirAcc": 70.6, "underRate": 92.2},
              "procurement": {"modelPct": 9.31, "waitCount": 33, "waitCorrect": 7},
              "forecast": [{"h": 4, "value": 749.25, "changePct": -3.12}]}]}
    f = tmp_path / "v.json"
    f.write_text(json.dumps(v, ensure_ascii=False))
    monkeypatch.setattr(bi, "VALIDATION", f)
    seq = [({"explanation": "4주 뒤 예측은 727.7 pt"}, "모의"), ({"explanation": "4주 뒤 예측은 749.3 pt"}, "모의")]
    monkeypatch.setattr(bi, "call_gemini", lambda p: seq.pop(0))
    r = bi.explain_validation()
    assert r["status"] == "ok" and r["attempts"] == 2
    seq2 = [({"explanation": "727.7 pt"}, "모의"), ({"explanation": "728.9 pt"}, "모의")]
    monkeypatch.setattr(bi, "call_gemini", lambda p: seq2.pop(0))
    assert bi.explain_validation()["status"] == "rejected"


# ───────────── v2.5 · p값(부호검정)이 겹치는 예측을 독립으로 보아 작게 나오던 사고 ─────────────
def test_v25_DM_검정_정답():
    from honest_backtest import dm_test_p
    rng = np.random.default_rng(0)
    base = np.abs(rng.normal(10, 3, 33))
    assert dm_test_p(base * 0.5, base, 4) < 0.01       # 모델이 확실히 나음
    assert dm_test_p(base * 1.5, base, 4) > 0.99       # 모델이 확실히 못함
    assert dm_test_p(base, base, 4) >= 0.05            # 같으면 합격 아님


# ───────────── v2.4 · 지금 예측이 검증과 다른 모델이거나 미래 정보를 쓰면 안 됨 ─────────────
def test_v24_지금_예측은_검증과_같은_모델이고_정답_확정_구간으로만_학습(monkeypatch):
    import honest_backtest as hb
    n = 40
    idx = pd.date_range("2025-06-16", periods=n, freq="W-MON")
    y = pd.Series(np.linspace(100, 200, n), index=idx)
    X = pd.DataFrame({"f": np.arange(n, dtype=float)}, index=idx)
    seen = []

    class Spy:
        def fit(self, Xt, yt):
            seen.append(len(Xt))
            assert not yt.isna().any()
        def predict(self, Xp):
            return np.array([0.0])
    monkeypatch.setattr(hb, "_model", lambda: Spy())
    fc = hb.current_forecast(X, y, "return")
    assert [f["h"] for f in fc] == list(range(1, hb.H_MAX + 1))
    assert seen == [n - h for h in range(1, hb.H_MAX + 1)]     # h 주 뒤 정답이 있는 행만
    assert all(date.fromisoformat(f["week"]).weekday() == 0 for f in fc)


# ───────────── v2.5 · 뉴스 단계가 LLM 번호 "3" 에서 멈추던 사고 ─────────────
@pytest.mark.parametrize("v,exp", [(3, 2), ("3", 2), ("N3", 2), ("E10", 9), ("n 7", 6),
                                   (None, -1), ("x", -1), (0, -1), (True, -1)])
def test_v25_v26_LLM_기사_번호_해석(v, exp):
    """v2.5: 번호 "3" 에서 멈춤 → v2.6: 지시문이 'N3' 형식이라 v2.5 수정이 10건을 조용히 0건으로 만든 사고."""
    from collect_news_events import _as_index
    assert _as_index(v) == exp


def test_v26_N_번호로_온_Gemini_뉴스가_모두_살아남음(monkeypatch):
    import collect_news_events as cne
    pool = [{"date": "2026-09-2%d" % i, "title": f"DRAM news {i}", "source": "src", "summary": "s", "link": ""}
            for i in range(10)]
    enriched = [{"idx": f"N{i + 1}", "tone": "pos", "score": 0.5, "title_ko": f"메모리 뉴스 {i}",
                 "summary_ko": "요약"} for i in range(10)]
    assert len(cne.merge_news_only(enriched, pool)) == 10


# ───────────── v2.3.1 · 기준금리·월간 통계를 '갱신 중단'으로 잘못 경보 ─────────────
def test_v231_신선도_기준은_신호_주기별():
    from build_frontend_data import frozen_limit, freshness
    assert frozen_limit("macro-fed") is None
    assert frozen_limit("A-3") == 17 and frozen_limit("A-2") == 26 and frozen_limit("B-6") == 8
    rows = _rows([(f"2026-{m:02d}-{d:02d}", 1.0) for m, d in [(6, 1), (6, 8), (6, 15), (6, 22), (6, 29),
                                                              (7, 6), (7, 13), (7, 20), (7, 27), (8, 3)]])
    assert freshness(rows, "2026-09-24", "2026-09-24", "macro-fed")["stale"] is False
    assert freshness(rows, "2026-09-24", "2026-09-24", "B-6")["stale"] is True


# ───────────── v2.6 장치 2 · 값이 그 지표가 맞는지 자동 검사 ─────────────
def test_v26_A4에_492만이_들어오면_자동_검사가_잡음():
    from data_checks import check_payload
    bad = {"source": "KOSIS 반도체 재고지수", "data": _rows([("2026-09-14", 4923610.0)])}
    good = {"source": "KOSIS 광업제조업동향조사 반도체 제조업(C261) 생산자제품 재고지수", "data": _rows([("2026-09-14", 106.5)])}
    assert any("정상 범위" in p for p in check_payload("A-4", bad))
    assert check_payload("A-4", good) == []


def test_v26_출처가_다른_표면_자동_검사가_잡음():
    from data_checks import check_payload
    wrong = {"source": "KOSIS 품목별 광공업 생산·출하·재고·내수·수출량", "data": _rows([("2026-09-14", 100.0)])}
    assert any("출처" in p for p in check_payload("A-4", wrong))


def test_v26_월요일_아닌_날짜_중복_무한대를_잡음():
    from data_checks import check_payload
    assert any("월요일" in p for p in check_payload("B-6", {"source": "Google News", "data": _rows([("2026-09-13", 0.1)])}))
    assert any("두 번" in p for p in check_payload("B-6", {"source": "Google News", "data": _rows([("2026-09-14", 0.1), ("2026-09-14", 0.2)])}))
    assert any("무한대" in p for p in check_payload("B-6", {"source": "Google News", "data": _rows([("2026-09-14", float("inf"))])}))


def test_v26_자동_검사에_걸린_신호는_화면_요약_검증에서_제외(monkeypatch):
    import build_frontend_data as bfd
    import data_checks
    monkeypatch.setattr(data_checks, "check_all", lambda: {"A-4": ["정상 범위 밖"]})
    inv = bfd.invalid_signals()
    assert "A-4" in inv and "자동 데이터 검사 실패" in inv["A-4"]


def test_v26_화면_데이터_뉴스_0건을_잡음(tmp_path):
    from data_checks import check_frontend_data
    d = {"history": [], "collection": {}, "validation": None, "news": [], "events": [{"a": 1}]}
    f = tmp_path / "data.js"
    f.write_text("export const SIXSENSE_DATA = " + json.dumps(d) + ";\n")
    assert any("뉴스 0건" in p for p in check_frontend_data(f))


def test_v25_화면_데이터_예측_기준_주_불일치를_잡음(tmp_path):
    from data_checks import check_frontend_data
    d = {"history": [{"date": "2026-09-21", "value": 1}], "collection": {},
         "validation": {"current": {"week": "2026-09-14"}, "variants": [{"key": "return", "forecast": [{"h": 1}], "pass": False}]}}
    f = tmp_path / "data.js"
    f.write_text("export const SIXSENSE_DATA = " + json.dumps(d) + ";\n")
    assert any("기준 주" in p for p in check_frontend_data(f))


# ───────────── v2.6.1 · A-3 8월 1건 시간 초과 → 7월 값으로 되돌아가 배포된 사고 (2026-09-27 미국 서버) ─────────────
def test_v261_A3_한_달이라도_연결_실패면_전체_실패(ac, monkeypatch):
    monkeypatch.setenv("KCS_API_KEY", "test")
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "END_D", date(2026, 9, 25))
    calls = {"n": 0}

    def flaky(url, params=None, timeout=None):
        calls["n"] += 1
        if params["strtYymm"] == "202608":
            raise requests.exceptions.ReadTimeout("Read timed out")
        return FakeResponse({"response": {"body": {"items": {"item": [{"expDlr": "1000000000"}]}}}})
    monkeypatch.setattr(ac.requests, "get", flaky)
    r = ac.run_one("A-3")
    assert r["status"] == "failed" and "네트워크" in r["reason"]
    assert not (ac.HIST_DIR / "A-3.json").exists()           # 일부 달만으로 저장하지 않음


def test_v261_최신_관측이_후퇴하면_저장하지_않고_기존_값_유지(ac, write_signal_file, monkeypatch):
    old = write_signal_file("A-3", _rows([("2026-07-06", 13.5e9), ("2026-08-03", 15.7e9), ("2026-08-10", 15.7e9)]))
    monkeypatch.setitem(ac.COLLECTORS, "A-3", lambda: (_rows([("2026-07-06", 13.5e9), ("2026-08-03", 13.5e9),
                                                                ("2026-08-10", 13.5e9)]), "real", "관세청 854232"))
    r = ac.run_one("A-3")
    assert r["status"] == "failed" and "후퇴" in r["reason"]
    assert json.loads((ac.HIST_DIR / "A-3.json").read_text())["data"] == old["data"]


def test_v261_정상_갱신은_후퇴_검사를_통과(ac, write_signal_file, monkeypatch):
    write_signal_file("A-7", _rows([("2026-09-07", 6.5), ("2026-09-14", 6.6)]))
    monkeypatch.setitem(ac.COLLECTORS, "A-7", lambda: (_rows([("2026-09-07", 6.5), ("2026-09-14", 6.6),
                                                                ("2026-09-21", 6.7)]), "real", "HG=F"))
    assert ac.run_one("A-7")["status"] == "ok"


# ───────────── v2.6.2 · 뉴스 피드 일부가 조용히 실패해도 나머지로 점수를 내 저장하던 위험 (B-2, B-1·B-5·B-6) ─────────────
# feedparser 는 연결이 끊겨도 오류를 내지 않고 빈 결과(응답 코드 없음)를 돌려준다.
def _feed(entries, status=200, bozo=False):
    return type("F", (), {"entries": entries, "status": status, "bozo": bozo, "get": lambda self, k, d=None: getattr(self, k, d)})()


def _news_entry(title="DRAM memory surge growth"):
    return {"published_parsed": time.struct_time((2026, 9, 22, 0, 0, 0, 1, 265, 0)), "title": title, "summary": ""}


def test_v262_B2_피드_하나라도_연결_실패면_저장하지_않고_기존_값_유지(ac, write_signal_file, monkeypatch):
    old = write_signal_file("B-2", _rows([("2026-09-14", 0.1)]), finalThrough="2026-09-07")
    urls = []

    def flaky(url):
        urls.append(url)
        return _feed([], status=None) if len(urls) == 3 else _feed([_news_entry()])   # 3번째 피드만 연결 실패
    monkeypatch.setattr(ac.feeds, "get_feed", flaky)
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "START_D", date(2026, 1, 1))
    r = ac.run_one("B-2")
    assert r["status"] == "failed" and "피드" in r["reason"], r
    assert json.loads((ac.HIST_DIR / "B-2.json").read_text())["data"] == old["data"]


def test_v262_B2_경고_표시만_있고_기사가_있는_피드는_정상(ac, monkeypatch):
    monkeypatch.setattr(ac.feeds, "get_feed", lambda url: _feed([_news_entry()], bozo=True))   # Digitimes 실측과 같은 모양
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "START_D", date(2026, 1, 1))
    assert ac.run_one("B-2")["status"] == "ok"


def test_v262_B6_공통_수집기도_피드_하나라도_실패면_전체_실패(ac, write_signal_file, monkeypatch):
    old = write_signal_file("B-6", _rows([("2026-09-14", 0.5)]), finalThrough="2026-09-07")
    urls = []

    def flaky(url):
        urls.append(url)
        return _feed([], status=500) if len(urls) == 2 else _feed([_news_entry()])
    monkeypatch.setattr(ac.feeds, "get_feed", flaky)
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "START_D", date(2026, 1, 1))
    monkeypatch.setattr(ac, "_llm_sentiment", lambda *a, **k: 0.3)
    monkeypatch.setitem(ac.COLLECTORS, "B-6", lambda: ac._collect_ir_news_sentiment("B-6", "HBM", "HBM mix"))
    r = ac.run_one("B-6")
    assert r["status"] == "failed" and "피드" in r["reason"], r
    assert json.loads((ac.HIST_DIR / "B-6.json").read_text())["data"] == old["data"]


def test_v262_피드_판정_경계(ac):
    assert ac._feed_failed(_feed([], status=None)) and ac._feed_failed(_feed([], status=404))
    assert ac._feed_failed(_feed([], bozo=True))                        # 읽기 실패 + 기사 0건 → 실패
    assert ac._feed_failed(_feed([_news_entry()], bozo=True)) is None   # 경고만 있고 기사 있음 → 정상 (Digitimes)
    assert ac._feed_failed(_feed([_news_entry()], status=302)) is None  # 주소 이동 후 정상 (구글 뉴스 zh-TW)
    assert ac._feed_failed(_feed([], status=200)) is None               # 검색 결과가 정말 없는 경우 → 정상


# ───────────── v2.6.2 · 후퇴 방지 장치 오탐 — 진행 중인 주 값이 우연히 전주와 같자 B-2 저장 거부 (2026-09-27 미국 서버) ─────────────
def test_v262_주간_신호의_이번주_값이_전주와_같아도_정상_저장(ac, write_signal_file, monkeypatch):
    write_signal_file("B-2", _rows([("2026-09-14", 0.0889), ("2026-09-21", 0.087)]), finalThrough="2026-09-14")
    monkeypatch.setattr(ac, "_last_completed_week", lambda: "2026-09-14")
    monkeypatch.setitem(ac.COLLECTORS, "B-2", lambda: (_rows([("2026-09-14", 0.0889), ("2026-09-21", 0.0889)]),
                                                        "real", "Google News RSS"))
    r = ac.run_one("B-2")
    assert r["status"] == "ok", r
    assert json.loads((ac.HIST_DIR / "B-2.json").read_text())["data"][-1] == {"week": "2026-09-21", "value": 0.0889}


def test_v262_월간_값을_이어_붙이는_수집기는_모두_월간_목록에_있음(ac):
    """후퇴 방지 두 번째 검사·신선도 판정이 MONTHLY_SIGNALS 에 의존 — 새 월간 수집기를 목록에 안 넣으면 보호가 조용히 사라진다."""
    import ast
    import inspect
    from build_frontend_data import MONTHLY_SIGNALS, QUARTERLY_SIGNALS
    ffill = set()
    for sid, fn in ac.COLLECTORS.items():
        calls = {n.func.id for n in ast.walk(ast.parse(inspect.getsource(fn)))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        if "_ffill_monthly_to_weekly" in calls:
            ffill.add(sid)
    assert ffill, "월간 수집기를 하나도 못 찾음 — 시험이 헛돎"
    assert ffill <= MONTHLY_SIGNALS | QUARTERLY_SIGNALS, ffill - (MONTHLY_SIGNALS | QUARTERLY_SIGNALS)


# ───────────── v2.6.3 · 피드 대기 시간 제한 없음 — 응답 없는 피드 하나가 주간 작업 전체를 붙잡을 수 있었음 ─────────────
def _local_feed_server(mode, total=10.0):
    """내 컴퓨터 안(127.0.0.1)의 진짜 HTTP 서버. drip: 0.3초마다 1바이트씩 total 초 동안, hang: 아무것도 안 보내고 total 초 대기,
    rel: 상대 주소 링크가 든 정상 RSS. 가짜 시계가 아니라 실제 소켓으로 시험한다 (v2.6.3 — 가짜가 현실과 달라 빈틈을 놓쳤음)."""
    import http.server
    import threading

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                if mode == "hang":
                    time.sleep(total)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
                self.end_headers()
                if mode == "rel":
                    self.wfile.write(b'<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>t</title>'
                                     b'<item><title>DRAM</title><link>/news/1</link>'
                                     b'<pubDate>Tue, 22 Sep 2026 00:00:00 GMT</pubDate></item></channel></rss>')
                    return
                t0 = time.time()
                while time.time() - t0 < total:
                    self.wfile.write(b"<")
                    self.wfile.flush()
                    time.sleep(0.3)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


@pytest.mark.parametrize("mode", ["drip", "hang"])
def test_v263_느리거나_응답_없는_피드는_전체_제한_시간에_중단(mode, monkeypatch):
    import feeds
    srv, base = _local_feed_server(mode)
    monkeypatch.setattr(feeds, "TOTAL_TIMEOUT", 1)
    t0 = time.time()
    try:
        with pytest.raises(requests.exceptions.Timeout):
            feeds.get_feed(base + "/feed")
        assert time.time() - t0 < 3, f"제한 1초인데 {time.time() - t0:.1f}초"
    finally:
        srv.shutdown()


def test_v263_상대_주소_링크는_최종_주소_기준으로_풀림():
    import feeds
    srv, base = _local_feed_server("rel")
    try:
        f = feeds.get_feed(base + "/feed")
        assert f.get("status") == 200 and [e.link for e in f.entries] == [base + "/news/1"]
    finally:
        srv.shutdown()


def test_v263_신호_피드는_첫_실패에서_바로_멈춤(ac, monkeypatch):
    calls = []

    def fake(url):
        calls.append(url)
        if len(calls) == 2:
            raise requests.exceptions.ReadTimeout("모의 시간 초과")
        return _feed([_news_entry()])
    monkeypatch.setattr(ac.feeds, "get_feed", fake)
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    with pytest.raises(requests.exceptions.ConnectionError):
        ac._fetch_feeds([f"https://x/{i}" for i in range(5)], "B-2", pause=0)
    assert len(calls) == 2                                  # 3~5번째는 기다리지 않음


def test_v263_뉴스_목록은_시간_예산을_넘으면_남은_피드를_건너뛰고_받은_기사는_유지(monkeypatch):
    import collect_news_events as cne
    today = date.today()
    clock = {"t": 0.0}

    def fake(url):
        clock["t"] += 200.0                                 # 피드 하나에 200초 걸린 것으로
        return _feed([{"published_parsed": time.struct_time((today.year, today.month, today.day, 0, 0, 0, 0, 1, 0)),
                       "title": f"Samsung HBM memory {url[-1]} - Reuters", "summary": "", "link": "https://x"}])
    monkeypatch.setattr(cne.feeds, "get_feed", fake)
    monkeypatch.setattr(cne.time, "sleep", lambda s: None)
    monkeypatch.setattr(cne.time, "monotonic", lambda: clock["t"])
    got = cne.fetch_entries([f"https://f/{i}" for i in range(6)])
    assert 1 <= len(got) < 6, len(got)                      # 예산 안에서 받은 것만, 전부는 아님


def test_v263_시험_중_외부_인터넷_접속은_막힘():
    import socket
    with pytest.raises(OSError, match="외부 인터넷"):
        socket.create_connection(("example.com", 80), timeout=2)


def test_v263_B2_피드_시간_초과면_저장하지_않고_기존_값_유지(ac, write_signal_file, monkeypatch):
    old = write_signal_file("B-2", _rows([("2026-09-14", 0.1)]), finalThrough="2026-09-07")
    urls = []

    def slow(url):
        urls.append(url)
        if len(urls) == 2:
            raise requests.exceptions.ReadTimeout("모의 시간 초과")
        return _feed([_news_entry()])
    monkeypatch.setattr(ac.feeds, "get_feed", slow)
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac, "START_D", date(2026, 1, 1))
    r = ac.run_one("B-2")
    assert r["status"] == "failed" and "피드" in r["reason"], r
    assert json.loads((ac.HIST_DIR / "B-2.json").read_text())["data"] == old["data"]


def test_v263_뉴스_목록은_피드_하나가_시간_초과돼도_나머지를_수집(monkeypatch):
    import collect_news_events as cne
    today = date.today()
    good = {"published_parsed": time.struct_time((today.year, today.month, today.day, 0, 0, 0, 0, 1, 0)),
            "title": "Samsung HBM memory supply - Reuters", "summary": "", "link": "https://x"}

    def fake(url):
        if "slow" in url:
            raise requests.exceptions.ReadTimeout("모의 시간 초과")
        return _feed([good])
    monkeypatch.setattr(cne.feeds, "get_feed", fake)
    monkeypatch.setattr(cne.time, "sleep", lambda s: None)
    got = cne.fetch_entries(["https://slow.example/feed", "https://ok.example/feed"])
    assert [e["title"] for e in got] == ["Samsung HBM memory supply"]


def test_v263_신호_피드는_느리지만_성공해도_시간_예산을_넘으면_전체_실패(ac, monkeypatch):
    clock = {"t": 0.0}

    def slow_ok(url):
        clock["t"] += 59.0                                  # 제한(60초) 직전까지 걸리지만 성공하는 피드
        return _feed([_news_entry()])
    monkeypatch.setattr(ac.feeds, "get_feed", slow_ok)
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setattr(ac.time, "monotonic", lambda: clock["t"])
    with pytest.raises(requests.exceptions.ConnectionError, match="예산"):
        ac._fetch_feeds([f"https://x/{i}" for i in range(13)], "B-2", pause=0)
    assert clock["t"] <= ac.SIGNAL_FEED_BUDGET + 60         # 13개 × 59초(767초)를 다 기다리지 않음
