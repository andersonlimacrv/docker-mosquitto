from typing import Annotated
import asyncio
from fastapi import HTTPException, Depends, status, WebSocket
from fastapi.security import APIKeyHeader
from pydantic import ValidationError
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.api.models.auth import WsAuthPayload

api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=True)

async def verify_api_key(api_key: Annotated[str, Depends(api_key_scheme)]) -> str:
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key

ApiKeyDep: Annotated[str, Depends(verify_api_key)] = Depends(verify_api_key)

async def verify_websocket_auth(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        raw_message = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
    except asyncio.TimeoutError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication timeout")
        raise

    try:
        payload = WsAuthPayload.model_validate_json(raw_message)
    except ValidationError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid auth payload format")
        raise

    if payload.type != "auth" or payload.api_key != settings.API_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid API Key")
        raise

    await websocket.send_text("_")
    websocket.state.api_key = payload.api_key

AuthWsDep = Depends(verify_websocket_auth)