from fastapi import APIRouter, HTTPException
from mosquitto_auth.api.dependencies import ApiKeyDep
from mosquitto_auth.api.models.users_file import UserListCreate
from mosquitto_auth.api.config import settings
import asyncio

router = APIRouter()

@router.post("/create-all", response_model=dict, status_code=201)
async def create_all_users(
    users_data: UserListCreate,
    auth: ApiKeyDep
):
    pass