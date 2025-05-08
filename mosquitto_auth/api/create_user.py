import asyncio
from fastapi import APIRouter, HTTPException, Header, Depends, Request
from pydantic import BaseModel
from mosquitto_auth.api.config import API_KEY, PASSWD_FILE_PATH
from mosquitto_auth.client.generate_users_password import generate_password_file

router = APIRouter()

async def verify_api_key(request: Request, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return True  


class UserCreateRequest(BaseModel):
    username: str
    password: str


@router.post("/create", dependencies=[Depends(verify_api_key)])
async def create_user(data: UserCreateRequest):
    try:
        await asyncio.to_thread(
            generate_password_file,
            {data.username: data.password},
            PASSWD_FILE_PATH
        )
        return {"message": f"User '{data.username}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
