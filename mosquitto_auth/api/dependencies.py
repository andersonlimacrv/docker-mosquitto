from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from mosquitto_auth.api.config import settings

api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=True)

async def verify_api_key(api_key: Annotated[str, Depends(api_key_scheme)]) -> str:
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key

ApiKeyDep: Annotated[str, Depends(verify_api_key)] = Depends(verify_api_key)
