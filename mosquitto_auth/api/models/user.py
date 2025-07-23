from pydantic import BaseModel, ConfigDict
from typing import List
from mosquitto_auth.core.validators import UsernameStr, PasswordStr

class UserCreate(BaseModel):
    username: UsernameStr
    password: PasswordStr

class UserPublic(BaseModel):
    username: UsernameStr

class UserResponse(BaseModel):
    username: str
    status: str
    message: str

class ManyUserCreate(BaseModel):
    users: List[UserCreate]
    overwrite_file: bool

class UserList(BaseModel):
    users: List[UserPublic]

class UserPasswordUpdate(BaseModel):
    username: UsernameStr
    new_password: PasswordStr

class UserBulkResponse(BaseModel):
    message: str
    details: dict

class BulkUserDetails(BaseModel):
    success: List[str]
    failed: List[str]
