from pydantic import BaseModel


class MarzbanResponse(BaseModel):
    status: int
    content: dict | list | None
