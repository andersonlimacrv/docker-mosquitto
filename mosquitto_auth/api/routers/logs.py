from __future__ import annotations

import asyncio
import json
from collections import deque

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from mosquitto_auth.api.core.config import settings

router = APIRouter()


def read_last_lines(path: str, limit: int) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return list(deque(f, maxlen=limit))


def validate_api_key(api_key: str | None) -> bool:
    return bool(api_key) and api_key == settings.API_KEY


@router.get("/")
def get_logs(
    limit: int = Query(
        default=10,
        ge=1,
        le=1000,
        description="Quantity of last lines of log to return",
    ),
):
    try:
        logs = read_last_lines(settings.LOG_FILE_PATH, limit)
        return {
            "limit": limit,
            "logs": logs,
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not found.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading log file: {e}",
        )


@router.websocket("/ws")
async def logs_ws(websocket: WebSocket):
    await websocket.accept()

    # limit via query param: /logs/ws?limit=10
    raw_limit = websocket.query_params.get("limit", "10")
    try:
        limit = int(raw_limit)
        if limit < 1:
            limit = 1
        elif limit > 1000:
            limit = 1000
    except ValueError:
        limit = 10

    try:
        # Primeira mensagem = auth
        raw_message = await asyncio.wait_for(
            websocket.receive_text(),
            timeout=5,
        )

        try:
            payload = json.loads(raw_message)
        except json.JSONDecodeError:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid auth payload",
            )
            return

        if payload.get("type") != "auth" or not validate_api_key(payload.get("api_key")):
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid API Key",
            )
            return

        await websocket.send_json({
            "type": "auth",
            "ok": True,
        })

        # Envia as últimas linhas logo após autenticar
        for line in read_last_lines(settings.LOG_FILE_PATH, limit):
            await websocket.send_text(line.rstrip("\n"))

        # Continua fazendo tail do arquivo
        with open(settings.LOG_FILE_PATH, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)  # vai pro final do arquivo

            while True:
                line = f.readline()

                if line:
                    await websocket.send_text(line.rstrip("\n"))
                else:
                    await asyncio.sleep(0.2)

    except asyncio.TimeoutError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication timeout",
        )
    except WebSocketDisconnect:
        return