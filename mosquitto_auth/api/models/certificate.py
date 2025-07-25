from pydantic import BaseModel
from mosquitto_auth.lib.validators import UsernameStr
from typing import Optional

class CertificateCreate(BaseModel):
    username: UsernameStr
    days: Optional[int] = 365 

class CertificateResponse(BaseModel):
    username: str
    status: str
    message: str
    cert_path: str | None = None
    key_path: str | None = None

class CertificateVerificationResponse(BaseModel):
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    signature_status: Optional[str] = None
