import asyncio
from fastapi import APIRouter, HTTPException, status
from mosquitto_auth.api.models.user import UserCreate, UserResponse
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

router = APIRouter()
manager = MosquittoUserManager()

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate
) -> UserResponse:
    """
    - **username**: Nome de usuário válido (3-32 caracteres alfanuméricos)
    - **password**: Senha forte (mínimo 6 caracteres)
    """
    try:
        await asyncio.to_thread(
            manager.add_user,
            user_data.username,
            user_data.password,
            False,
        )
        return UserResponse(username=user_data.username, status="created")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
