from typing import TypeVar, Type
from datetime import datetime
import uuid

from pydantic import BaseModel

from .base import Base
from ..marzban import Marzban
from ..marzban_response import MarzbanResponse
from ..enums.user import Flow, CipherMethod
from ..utils import raise_exception_on_status

USER = TypeVar("USER", bound="User")


class Proxy(BaseModel):
    id: uuid.UUID | None = None
    flow: Flow | None = None
    password: str | None = None
    method: CipherMethod | None = None


class User(Base):
    exists: bool = False

    def __init__(
        self,
        *,
        username: str,
        expire: datetime,
        data_limit: int,
        proxies: dict[str, Proxy],
        inbounds: dict[str, list[str]],
    ) -> None: ...
