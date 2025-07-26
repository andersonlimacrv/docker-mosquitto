from pydantic import BaseModel
from typing import Optional

class CreateCA(BaseModel):
  common_name: Optional[str] = "ROOT_BROKER_CA"
  days: Optional[int] = 3650


class CACreateResponse(BaseModel):
  ca_key: Optional[str] 
  ca_crt: Optional[str]
  ca_srl: Optional[str]
  common_name: Optional[str]
  valid_days: Optional[int]
