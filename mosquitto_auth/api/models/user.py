from pydantic import BaseModel, ConfigDict
from typing import List
from mosquitto_auth.core.validators import UsernameStr, PasswordStr

class UserCreate(BaseModel):
    username: UsernameStr
    password: PasswordStr

class UserDelete(BaseModel):
    username: UsernameStr

class UserResponse(BaseModel):
    username: str
    status: str

class ManyUserCreate(BaseModel):
    users: List[UserCreate]
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": {
                    "john_doe": "s3cr3tP@ss",
                    "admin": "Str0ngP@ss!"
                }
            }
        }
    )