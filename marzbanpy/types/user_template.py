from typing import Type, TypeVar
from datetime import timedelta

from .base import Base
from ..marzban import Marzban
from ..marzban_response import MarzbanResponse
from ..utils import raise_exception_on_status

USER_TEMPLATE = TypeVar("USER_TEMPLATE", bound="UserTemplate")


class UserTemplate(Base):
    exists: bool = False

    def __init__(
        self,
        *,
        name: str,
        inbounds: dict[str, list[str]],
        id: int | None = None,
        data_limit: int = 0,
        expire_duration: timedelta | None = None,
        username_prefix: str | None = None,
        username_suffix: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.data_limit = data_limit
        self.expire_duration = expire_duration
        self.username_prefix = username_prefix
        self.username_suffix = username_suffix
        self.inbounds = inbounds

    async def save(self, panel: Marzban) -> None:
        url = "/api/user_template"
        expire_duration = (
            self.expire_duration.total_seconds()
            if isinstance(self.expire_duration, timedelta)
            else 0
        )
        data = {
            "name": self.name,
            "data_limit": self.data_limit,
            "expire_duration": expire_duration,
            "username_prefix": self.username_prefix,
            "username_suffix": self.username_suffix,
            "inbounds": self.inbounds,
        }
        if self.exists:
            url += f"/{self.id}"
            response: MarzbanResponse = await panel._send_request(
                method="PUT", path=url, data=data
            )
        else:
            response: MarzbanResponse = await panel._send_request(
                method="POST", path=url, data=data
            )
        raise_exception_on_status(response)
        self.id = response.content["id"]
        self.exists = True

    async def delete(self, panel: Marzban) -> None:
        url = f"/api/user_template/{self.id}"
        response: MarzbanResponse = await panel._send_request(method="DELETE", path=url)
        raise_exception_on_status(response)
        self.exists = False

    @classmethod
    async def get(cls: Type[USER_TEMPLATE], panel: Marzban, id: int) -> USER_TEMPLATE:
        url = f"/api/user_template/{id}"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        user_template = cls(**response.content)
        user_template.exists = True
        return user_template

    @classmethod
    async def all(
        cls: Type[USER_TEMPLATE],
        panel: Marzban,
        *,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[USER_TEMPLATE]:
        url = "/api/user_template"
        query_params = {}
        if isinstance(offset, int):
            query_params["offset"] = offset
        if isinstance(limit, int):
            query_params["limit"] = limit
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        user_templates: list[USER_TEMPLATE] = []
        for data in response.content:
            user_template = cls(**data)
            user_template.exists = True
            user_templates.append(user_template)
        return user_templates
