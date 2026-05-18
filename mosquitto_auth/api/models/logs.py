from pydantic import BaseModel

class LogsResponse(BaseModel):
    limit: int
    logs: list[str]
