import asyncio
from fastapi import APIRouter, HTTPException, status
from mosquitto_auth.api.models.user import UserCreate, UserPublic, UserResponse, UserBulkResponse,ManyUserCreate, UserPasswordUpdate, UserList
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager
from mosquitto_auth.api.models.status import UserStatus
from mosquitto_auth.api.models.responses import UserMessages

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
    try:
        await asyncio.to_thread(
            manager.add_user,
            user_data.username,
            user_data.password,
        )
        
        message = UserMessages.USER_CREATED.format(username=user_data.username)
        
        return UserResponse(
            username=user_data.username,
            status=UserStatus.CREATED,  
            message=message
        )

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
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "",
    response_model=UserList,
    status_code=status.HTTP_200_OK,
  )
async def get_users() -> UserList:
    try:
        usernames = await asyncio.to_thread(manager.list_users)
        users = [UserPublic(username=username) for username in usernames]
        return UserList(users=users)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse
)
async def delete_user(data: UserPublic):
    try:
        await asyncio.to_thread(manager.delete_user, data.username)
        message = UserMessages.USER_DELETED.format(username=data.username)
        
        return  UserResponse(username=data.username, status=UserStatus.DELETED, message=message)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=UserMessages.USER_NOT_FOUND.format(username=data.username)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )
    

@router.put(
    "/password",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
async def update_user_password(data: UserPasswordUpdate):
    try:
        await asyncio.to_thread(
            manager.edit_password,
            data.username,
            data.new_password
        )
        
        message = UserMessages.PASSWORD_UPDATED.format(username=data.username)

        return UserResponse(
            username=data.username,
            status=UserStatus.UPDATED,
            message=message
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserMessages.USER_NOT_FOUND.format(username=data.username)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.post(
    "/bulk",
    response_model=UserBulkResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_many_users(data: ManyUserCreate):
    failed_users = []

    try:
        await asyncio.to_thread(manager.add_many_users, data.users, data.overwrite_file)

    except RuntimeError as e:
        if "Errors in bulk add:" in str(e):
            error_msgs = str(e).replace("Errors in bulk add: ", "").split("; ")
            failed_users = [msg.split(":")[0] for msg in error_msgs if msg]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    requested_usernames = [user.username for user in data.users]
    failed_set = set(failed_users)

    success_users = [username for username in requested_usernames if username not in failed_set]
    if not success_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[f"{username}: User already exists." for username in failed_users]
        )

    return UserBulkResponse(
        message=UserMessages.MANY_USERS_CREATED,
        details={
            "success": success_users,
            "failed": [f"{username}: User already exists." for username in failed_users]
        }
    )
