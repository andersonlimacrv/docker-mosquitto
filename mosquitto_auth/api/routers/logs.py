from __future__ import annotations

import asyncio
from collections import deque

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.api.models.logs import LogsResponse

router = APIRouter()
ws_router = APIRouter()

def read_last_lines(path: str, limit: int) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return list(deque(f, maxlen=limit))

@router.get("", response_model=LogsResponse, status_code=status.HTTP_200_OK)
def get_logs(limit: int = Query(default=10, ge=1, le=1000)):
    try:
        logs = read_last_lines(settings.LOG_FILE_PATH, limit)
        return LogsResponse(limit=limit, logs=logs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Log file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")

@router.get("/download", response_class=FileResponse, status_code=200)
def download_logs():
    log_path = settings.LOG_FILE_PATH
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Broker log file not found.")
    return FileResponse(path=log_path, filename="mosquitto.log", media_type="text/plain")

@ws_router.websocket("/stream")
async def logs_ws(websocket: WebSocket):
    raw_limit = websocket.query_params.get("limit", "10")
    try:
        limit = int(raw_limit)
        if limit < 1: limit = 1
        elif limit > 1000: limit = 1000
    except ValueError:
        limit = 10

    for line in read_last_lines(settings.LOG_FILE_PATH, limit):
        await websocket.send_text(line.rstrip("\n"))

    try:
        with open(settings.LOG_FILE_PATH, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    await websocket.send_text(line.rstrip("\n"))
                else:
                    await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        return