from typing import Annotated
from fastapi import HTTPException, Header, Request, Depends
from mosquitto_auth.api.config import settings

async def verify_api_key(
    request: Request,
    x_api_key: Annotated[str, Header(..., description="Chave API para autenticação")]
) -> bool:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return True

ApiKeyDep = Annotated[bool, Depends(verify_api_key)]