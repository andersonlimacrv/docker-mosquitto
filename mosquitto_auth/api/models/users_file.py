from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict
from mosquitto_auth.core.validators import UsernameStr, PasswordStr

class UserListCreate(BaseModel):
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
    
    users: Dict[UsernameStr, PasswordStr] = Field(
        ...,
        description="Dictionary of users with their passwords. Keys are usernames and values are passwords.",
    )

    @field_validator('users', mode='before')
    @classmethod
    def validate_users_dict(cls, value: Dict[str, str]) -> Dict[str, str]:
        if not value:
            raise ValueError("At least one user must be provided")
        return value