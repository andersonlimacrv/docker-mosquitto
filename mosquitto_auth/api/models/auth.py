from pydantic import BaseModel

class WsAuthPayload(BaseModel):
    type: str
    api_key: str
