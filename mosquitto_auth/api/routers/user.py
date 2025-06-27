from fastapi import APIRouter, HTTPException, status
from mosquitto_auth.api.dependencies import ApiKeyDep
from mosquitto_auth.api.models.user import UserCreate, UserResponse
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

router = APIRouter()
manager = MosquittoUserManager()

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adiciona um único usuário"
)
async def create_user(
    user_data: UserCreate,
    auth: ApiKeyDep
) -> UserResponse:
    """
    - **username**: Nome de usuário válido (3-20 caracteres alfanuméricos)
    - **password**: Senha forte (mínimo 6 caracteres)
    """
    try:
        if not manager.add_user(user_data.username, user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao adicionar usuário {user_data.username}"
            )

        return UserResponse(
            username=user_data.username,
            status="created"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

