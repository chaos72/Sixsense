"""Sixsense FastAPI backend — Phase 5 in-memory implementation.

PORTED FROM: PRD §15 API Specification, Design §4
Design Ref: Design §2.2.2 사용자 조회 플로우

Implementation notes:
- 15 endpoints (14 GET + 1 POST)
- In-memory data from app/data.json (mirrors frontend mock)
- No DB / no Redis / no JWT — Phase 5 minimal viable backend
- CORS open for localhost dev (frontend :5173)
- HITL POST queues a fake retrain job for L1/L3 test purposes
"""
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_PATH = Path(__file__).parent / "data.json"
DATA: dict[str, Any] = json.loads(DATA_PATH.read_text())

app = FastAPI(
    title="Sixsense API",
    description="Server DRAM Price Intelligence Dashboard — Phase 5 backend (in-memory)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


# In-memory HITL retrain queue (for POST + polling tests)
RETRAIN_JOBS: dict[str, dict[str, Any]] = {}

# USER-REQUESTED EXTENSION (2026-05-18 #7) — 수동 갱신 작업 큐 (S-001 풋바 "🔄 수동 갱신")
REFRESH_JOBS: dict[str, dict[str, Any]] = {}
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
VENV_PY = BACKEND_DIR / ".venv/bin/python3"

REFRESH_STAGES = [
    ("auto_collectors",      "데이터 수집 (정형 7 + 비정형 7 + 거시 5 + 타겟 1 = 20 신호)", ["--all"]),
    ("collect_news_events",  "뉴스/이벤트 수집 (RSS 14쿼리 → LLM 분류)",                    []),
    ("forecast_v2",          "예측 모델 재학습 (Prophet + GBR + LSTM)",                      []),
    ("build_insight",        "예측분석 인사이트 생성 (LLM 종합 판단)",                       []),
    ("build_frontend_data",  "프론트엔드 데이터 빌드 (data.js)",                             []),
]


def _run_refresh_pipeline(job_id: str):
    job = REFRESH_JOBS[job_id]
    job["status"] = "running"
    job["startedAt"] = time.time()
    env = {**os.environ}
    # 프로젝트 루트 .env 로드 (각 스크립트가 자체적으로도 읽지만 안전 차원)
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

    try:
        for idx, (stage_id, stage_label, extra_args) in enumerate(REFRESH_STAGES, start=1):
            job["currentStep"] = idx
            job["stage"] = stage_label
            script = BACKEND_DIR / f"pipelines/{stage_id}.py"
            if not script.exists():
                job["status"] = "failed"
                job["error"] = f"파이프라인 스크립트 없음: {script}"
                return
            t0 = time.time()
            result = subprocess.run(
                [str(VENV_PY), str(script), *extra_args],
                cwd=str(BACKEND_DIR),
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )
            dur = round(time.time() - t0, 1)
            tail = (result.stdout or result.stderr or "").strip().splitlines()
            last_line = tail[-1][:200] if tail else "(no output)"
            log_entry = {
                "step": idx, "stage": stage_label, "durSec": dur,
                "ok": result.returncode == 0, "lastLine": last_line,
            }
            job["logs"].append(log_entry)
            if result.returncode != 0:
                job["status"] = "failed"
                job["error"] = (result.stderr or result.stdout or "")[-800:]
                job["finishedAt"] = time.time()
                return
        job["status"] = "done"
        job["stage"] = "완료"
        job["finishedAt"] = time.time()
        job["totalDurSec"] = round(job["finishedAt"] - job["startedAt"], 1)
    except subprocess.TimeoutExpired:
        job["status"] = "failed"
        job["error"] = f"타임아웃 (10분 초과) — 단계: {job.get('stage')}"
        job["finishedAt"] = time.time()
    except Exception as e:
        job["status"] = "failed"
        job["error"] = f"{type(e).__name__}: {str(e)[:500]}"
        job["finishedAt"] = time.time()


# ──────────────────────────────────────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "Sixsense API",
        "version": "0.1.0",
        "endpoints": 15,
        "data_loaded": list(DATA.keys()),
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "ts": time.time()}


# ──────────────────────────────────────────────────────────────────────────────
# 1. GET /api/snapshot — S-001 가격 + 예측 + 메타
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/snapshot")
def get_snapshot():
    m = DATA["meta"]
    return {
        "currentPrice": {
            "value": m["current"],
            "unit": "/GB",
            "code": "DDR5 8Gb",
            "change_pct": m["currentChange"],
        },
        "forecast7": {
            "value": m["pred7"],
            "change_pct": m["pred7Change"],
            "model": m["model"],
            "confidence": m["confidence"] / 100,
        },
        "forecast21": {
            "value": m["pred21"],
            "change_pct": m["pred21Change"],
            "model": "lstm_v1.0",
            "confidence": 0.74,
        },
        "updatedAt": m["updated"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# 2. GET /api/history — S-001 52주 가격 + 21주 예측
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/history")
def get_history():
    return {
        "history": DATA["history"],
        "forecast7": DATA["forecast7"],
        "forecast21": DATA["forecast21"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# 3. GET /api/signals — S-001 14신호
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/signals")
def get_signals():
    return {"groupA": DATA["signalsA"], "groupB": DATA["signalsB"]}


# ──────────────────────────────────────────────────────────────────────────────
# 4. GET /api/signals/:id — S-003, S-004 신호 상세
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/signals/{signal_id}")
def get_signal(signal_id: str):
    sid = signal_id.upper()
    for group_key in ("signalsA", "signalsB"):
        for s in DATA[group_key]:
            if s.get("id") == sid:
                return s
    raise HTTPException(
        status_code=404,
        detail={"error": "RESOURCE_NOT_FOUND", "message": f"신호 ID '{sid}'을 찾을 수 없습니다."},
    )


# ──────────────────────────────────────────────────────────────────────────────
# 5. GET /api/news — S-006 뉴스 목록
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/news")
def get_news(
    sentiment: Optional[str] = Query(None, description="pos|neu|neg"),
    source: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    items = DATA["news"]
    if sentiment:
        items = [n for n in items if n.get("tone") == sentiment]
    if source:
        items = [n for n in items if n.get("source") == source]
    return {"items": items[:limit], "total": len(items)}


# ──────────────────────────────────────────────────────────────────────────────
# 6. GET /api/news/:idx — S-007 뉴스 상세 (mock uses index)
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/news/{news_idx}")
def get_news_one(news_idx: int):
    items = DATA["news"]
    if news_idx < 0 or news_idx >= len(items):
        raise HTTPException(
            status_code=404,
            detail={"error": "RESOURCE_NOT_FOUND", "message": f"뉴스 인덱스 {news_idx} 없음"},
        )
    return items[news_idx]


# ──────────────────────────────────────────────────────────────────────────────
# 7. GET /api/macro — S-001/S-008 거시지표 5종
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/macro")
def get_macro():
    return {"items": DATA["macro"]}


# ──────────────────────────────────────────────────────────────────────────────
# 8. GET /api/macro/:id — S-008 거시지표 상세
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/macro/{macro_id}")
def get_macro_one(macro_id: str):
    for m in DATA["macro"]:
        if m.get("id") == macro_id or m.get("name", "").lower().startswith(macro_id.lower()):
            return m
    raise HTTPException(
        status_code=404,
        detail={"error": "RESOURCE_NOT_FOUND", "message": f"거시지표 '{macro_id}' 없음"},
    )


# ──────────────────────────────────────────────────────────────────────────────
# 9. GET /api/events — S-010 이벤트 목록
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/events")
def get_events(risk: Optional[str] = Query(None, description="high|mid|low")):
    items = DATA["events"]
    if risk:
        items = [e for e in items if e.get("risk") == risk]
    return {"items": items, "total": len(items)}


# ──────────────────────────────────────────────────────────────────────────────
# 10. GET /api/events/:idx — S-011 이벤트 상세
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/events/{event_idx}")
def get_event_one(event_idx: int):
    items = DATA["events"]
    if event_idx < 0 or event_idx >= len(items):
        raise HTTPException(
            status_code=404,
            detail={"error": "RESOURCE_NOT_FOUND", "message": f"이벤트 인덱스 {event_idx} 없음"},
        )
    return items[event_idx]


# ──────────────────────────────────────────────────────────────────────────────
# 11. GET /api/forecast/:horizon — S-002 예측 근거
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/forecast/{horizon}")
def get_forecast(horizon: int):
    if horizon not in (7, 21):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VALIDATION_FAILED",
                "message": "horizon은 7 또는 21만 가능",
                "fieldErrors": {"horizon": "7 또는 21"},
            },
        )
    data = DATA["forecast7"] if horizon == 7 else DATA["forecast21"]
    final = data[-1]
    return {
        "horizon": horizon,
        "createdAt": DATA["meta"]["updated"],
        "model": DATA["meta"]["model"] if horizon == 7 else "lstm_v1.0",
        "confidence": DATA["meta"]["confidence"] / 100 if horizon == 7 else 0.74,
        "valueRange": {
            "value": final.get("value"),
            "lower": final.get("lower"),
            "upper": final.get("upper"),
        },
        "weeklyTable": data,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 12. GET /api/accuracy — S-012 정확도 이력
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/accuracy")
def get_accuracy(horizon: Optional[int] = None, limit: int = Query(100, ge=1, le=500)):
    items = DATA["accuracy"]
    if horizon:
        items = [a for a in items if a.get("horizon") == horizon]
    return {"items": items[:limit], "total": len(items)}


# ──────────────────────────────────────────────────────────────────────────────
# 13. GET /api/accuracy/:idx — S-013 신호 비교
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/accuracy/{accuracy_idx}")
def get_accuracy_one(accuracy_idx: int):
    items = DATA["accuracy"]
    if accuracy_idx < 0 or accuracy_idx >= len(items):
        raise HTTPException(
            status_code=404,
            detail={"error": "RESOURCE_NOT_FOUND", "message": f"정확도 인덱스 {accuracy_idx} 없음"},
        )
    row = items[accuracy_idx]
    return {
        "row": row,
        "thenSignals": DATA.get("snapshotPast", DATA["signalsA"]),
        "nowSignals": DATA["signalsA"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# 14. GET /api/collection — S-014 수집 현황
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/api/collection")
def get_collection():
    return {"items": DATA["collection"]}


# ──────────────────────────────────────────────────────────────────────────────
# 15. POST /api/hitl/rules — HITL 임계치 저장 (Design §2.2.3)
# ──────────────────────────────────────────────────────────────────────────────
class HITLRuleUpdate(BaseModel):
    id: str
    value: float


class HITLRequest(BaseModel):
    signalId: str
    rules: list[HITLRuleUpdate]
    comment: Optional[str] = None


@app.post("/api/hitl/rules", status_code=202)
def post_hitl_rules(body: HITLRequest):
    if not body.rules:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VALIDATION_FAILED",
                "message": "rules 배열이 비어있음",
                "fieldErrors": {"rules": "최소 1개 규칙 필요"},
            },
        )
    job_id = f"rj_{uuid.uuid4().hex[:12]}"
    RETRAIN_JOBS[job_id] = {
        "status": "processing",
        "signalId": body.signalId,
        "rules": [r.dict() for r in body.rules],
        "comment": body.comment,
        "createdAt": time.time(),
        "etaSeconds": 30,
    }
    # In a real impl, this would enqueue a background job.
    # For test purposes we mark "done" immediately on next poll.
    return {
        "status": "processing",
        "queueId": job_id,
        "etaSeconds": 30,
        "pollUrl": f"/api/hitl/jobs/{job_id}",
    }


# Bonus: HITL job polling (for L3 E2E test)
@app.get("/api/hitl/jobs/{job_id}")
def get_hitl_job(job_id: str):
    if job_id not in RETRAIN_JOBS:
        raise HTTPException(
            status_code=404,
            detail={"error": "RESOURCE_NOT_FOUND", "message": "재학습 작업 없음"},
        )
    job = RETRAIN_JOBS[job_id]
    # First poll: still processing. Second poll: done (simulate quick retrain for tests).
    if time.time() - job["createdAt"] > 1:
        job["status"] = "done"
        job["beforeResult"] = {"matchRate": 0.85}
        job["afterResult"] = {"matchRate": 0.92}
    return job


# ──────────────────────────────────────────────────────────────────────────────
# USER-REQUESTED EXTENSION (2026-05-18 #7) — 수동 갱신 (S-001 §09 풋바 버튼)
# ──────────────────────────────────────────────────────────────────────────────
@app.post("/api/refresh", status_code=202)
def post_refresh():
    """5단계 파이프라인 백그라운드 실행 (auto_collectors → news → forecast → insight → build).
    이미 진행 중인 작업이 있으면 그 job_id 반환 (중복 실행 방지)."""
    for jid, j in REFRESH_JOBS.items():
        if j["status"] in ("queued", "running"):
            return {
                "queueId": jid, "status": j["status"], "stage": j.get("stage"),
                "currentStep": j.get("currentStep", 0), "totalSteps": len(REFRESH_STAGES),
                "pollUrl": f"/api/refresh/jobs/{jid}", "reused": True,
            }
    job_id = f"rf_{uuid.uuid4().hex[:12]}"
    REFRESH_JOBS[job_id] = {
        "status": "queued",
        "stage": "대기 중",
        "currentStep": 0,
        "totalSteps": len(REFRESH_STAGES),
        "logs": [],
        "createdAt": time.time(),
    }
    # subprocess가 길어 BackgroundTasks 보다 스레드 사용 (uvicorn worker 차단 방지)
    threading.Thread(target=_run_refresh_pipeline, args=(job_id,), daemon=True).start()
    return {
        "queueId": job_id, "status": "queued",
        "totalSteps": len(REFRESH_STAGES),
        "pollUrl": f"/api/refresh/jobs/{job_id}",
    }


@app.get("/api/refresh/jobs/{job_id}")
def get_refresh_job(job_id: str):
    if job_id not in REFRESH_JOBS:
        raise HTTPException(
            status_code=404,
            detail={"error": "JOB_NOT_FOUND", "message": "수동 갱신 작업 없음"},
        )
    job = REFRESH_JOBS[job_id]
    return {
        "queueId": job_id,
        "status": job["status"],
        "stage": job.get("stage"),
        "currentStep": job.get("currentStep", 0),
        "totalSteps": job.get("totalSteps", len(REFRESH_STAGES)),
        "logs": job.get("logs", []),
        "error": job.get("error"),
        "totalDurSec": job.get("totalDurSec"),
        "createdAt": job.get("createdAt"),
        "finishedAt": job.get("finishedAt"),
    }


@app.get("/api/refresh/stages")
def get_refresh_stages():
    """수동 갱신 파이프라인의 단계 메타데이터 (UI 사전 표시용)."""
    return {
        "stages": [
            {"step": i + 1, "id": sid, "label": label}
            for i, (sid, label, _) in enumerate(REFRESH_STAGES)
        ],
        "totalSteps": len(REFRESH_STAGES),
    }
