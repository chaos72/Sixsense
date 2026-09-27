"""pytest 공통 설정 — 파이프라인 모듈을 가져올 수 있게 경로를 잡고, 신호 파일은 임시 폴더에서만 다룬다."""
import json
import os
import socket
import sys
from pathlib import Path

import pytest

# 돌연변이 시험(tests/mutation_check.py)은 버그를 되살린 복사본 경로를 SIXSENSE_PIPELINES 로 넘긴다
PIPELINES = Path(os.environ.get("SIXSENSE_PIPELINES") or Path(__file__).resolve().parents[1] / "pipelines")
sys.path.insert(0, str(PIPELINES))


@pytest.fixture
def ac(tmp_path, monkeypatch):
    """auto_collectors 모듈 — 신호 파일 폴더를 임시 폴더로 바꿔 실제 데이터를 건드리지 않는다."""
    import auto_collectors
    monkeypatch.setattr(auto_collectors, "HIST_DIR", tmp_path)
    return auto_collectors


@pytest.fixture
def write_signal_file(tmp_path):
    def _write(sid, rows, **extra):
        payload = {"signalId": sid, "source": "test", "collectedAt": "2026-09-24", "data": rows, **extra}
        (tmp_path / f"{sid}.json").write_text(json.dumps(payload))
        return payload
    return _write


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status_code, self.text = payload, status, json.dumps(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


@pytest.fixture(autouse=True)
def _block_internet(monkeypatch):
    """시험 중 외부 인터넷 접속 차단 (v2.6.3) — 시험은 인터넷 없이, 내 컴퓨터 안(127.0.0.1)만. 돌연변이 시험에서 옛 코드가
    실제 인터넷에 접속해 결과가 인터넷 상태에 좌우되던 문제도 막는다."""
    real = socket.getaddrinfo

    def guarded(host, *a, **k):
        if host not in _LOCAL_HOSTS:
            raise OSError(f"시험 중 외부 인터넷 접속 금지: {host}")
        return real(host, *a, **k)
    monkeypatch.setattr(socket, "getaddrinfo", guarded)
