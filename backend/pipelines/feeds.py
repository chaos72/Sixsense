"""뉴스 피드 받기 — 대기 시간 제한 (v2.6.3)

feedparser.parse(주소) 는 대기 시간 제한이 없어, 응답 없는 피드 하나가 주간 작업(한도 30분) 전체를 붙잡을 수 있었다.
여기서는 받기 전체(주소 조회·연결·주소 이동·본문)를 별도 작업 줄에서 하고 바깥에서 TOTAL_TIMEOUT 초만 기다린다.
받는 도중에 시간을 재는 방식은 쓰지 않는다 — 조금씩 느리게 오는 응답에서는 받는 도구가 조각이 찰 때까지 기다려
시간 검사가 실행되지 않았다(재현: 제한 2초에 20초 걸림).
(2026-09-27 실측: 피드 49개의 기사 제목이 기존 feedparser.parse(주소) 방식과 완전히 동일)

auto_collectors(B-2·B-1·B-5·B-6)와 collect_news_events(화면 뉴스 목록)가 같이 쓴다.
"""
from __future__ import annotations

import threading

import feedparser
import requests

CONNECT_TIMEOUT = 10   # 연결까지 (작업 줄 안쪽 제한)
READ_TIMEOUT = 30      # 응답 조각 사이 간격 (작업 줄 안쪽 제한)
TOTAL_TIMEOUT = 60     # 피드 하나 전체 — 이 시간이 지나면 결과를 기다리지 않는다


def _download(url: str):
    r = requests.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), headers={"User-Agent": feedparser.USER_AGENT})
    headers = {k.lower(): v for k, v in r.headers.items()}
    headers.setdefault("content-location", r.url)      # 상대 주소 링크를 최종 주소 기준으로 풀기 (옛 방식과 같게)
    f = feedparser.parse(r.content, response_headers=headers)
    f["status"] = r.status_code
    f["href"] = r.url
    return f


def get_feed(url: str):
    """피드 하나를 받아 해석한 결과(FeedParserDict). 결과의 status 는 최종 응답 코드.
    연결 실패·시간 초과는 requests 오류(RequestException)로 올린다."""
    box: dict = {}

    def work():
        try:
            box["feed"] = _download(url)
        except BaseException as e:      # 작업 줄 안의 오류를 바깥으로 전달
            box["error"] = e
    t = threading.Thread(target=work, daemon=True)   # 배경용: 버려져도 프로그램 종료를 막지 않음
    t.start()
    t.join(TOTAL_TIMEOUT)
    if t.is_alive():
        raise requests.exceptions.Timeout(f"피드 전체 시간 {TOTAL_TIMEOUT}초 초과")
    if "error" in box:
        raise box["error"]
    return box["feed"]
