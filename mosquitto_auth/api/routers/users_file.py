from fastapi import APIRouter, HTTPException
from mosquitto_auth.api.dependencies import ApiKeyDep
from mosquitto_auth.api.models.users_file import UserListCreate
from mosquitto_auth.client.generate_users_password import generate_password_file
from mosquitto_auth.api.config import settings
import asyncio

router = APIRouter()

@router.post("/create-all", response_model=dict, status_code=201)
async def create_all_users(
    users_data: UserListCreate,
    auth: ApiKeyDep
):
    try:
        await asyncio.to_thread(
            generate_password_file,
            users_data.users,
            settings.PASSWD_FILE_PATH
        )

        return {
            "message": f"{len(users_data.users)} usuários criados com sucesso. Os anteriores foram substituídos.",
            "users": list(users_data.users.keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))