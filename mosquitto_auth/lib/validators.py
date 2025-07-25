from typing import Annotated
from pydantic.types import StringConstraints
from pydantic import BaseModel, ValidationError

UsernameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
]

PasswordStr = Annotated[
    str,
    StringConstraints(
        min_length=6,
        max_length=64
    )
]

def validate_single_user(username: str, password: str) -> tuple[str, str]:
    """Valida um par username/password individualmente"""
    class TempUser(BaseModel):
        username: UsernameStr
        password: PasswordStr
    
    try:
        validated = TempUser(username=username, password=password)
        return validated.username, validated.password
    except ValidationError as e:
        raise ValueError(f"Invalid user credentials: {e.errors()}")

def validate_users_dict(users_dict: dict[str, str]) -> dict[str, str]:
    """Valida um dicionário completo de usuários"""
    validated_users = {}
    for username, password in users_dict.items():
        valid_user, valid_pass = validate_single_user(username, password)
        validated_users[valid_user] = valid_pass
    return validated_users