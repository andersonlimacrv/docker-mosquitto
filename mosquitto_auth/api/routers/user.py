import asyncio
from fastapi import APIRouter, HTTPException
from mosquitto_auth.api.dependencies import ApiKeyDep
from mosquitto_auth.api.models.user import UserCreateRequest
from mosquitto_auth.client.generate_users_password import generate_password_file
from mosquitto_auth.api.config import settings

router = APIRouter()

@router.post("/create")
async def create_user(
    data: UserCreateRequest,
    auth: ApiKeyDep  
):
    try:
        await asyncio.to_thread(
            generate_password_file,
            {data.username: data.password},
            settings.PASSWD_FILE_PATH
        )
        return {"message": f"User '{data.username}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))