import asyncio
from fastapi import APIRouter, HTTPException, status
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager


router = APIRouter()
user_manager = MosquittoUserManager


@router.get(
  "",
  response_model=str,
  status_code=status.HTTP_200_OK,
)
async def get_certificate() -> str:
  try:
    message_test = 'test'  
    return message_test
  except RuntimeError as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )