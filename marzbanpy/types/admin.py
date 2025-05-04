from typing import TypeVar, Type

from .base import Base
from ..marzban import Marzban
from ..marzban_response import MarzbanResponse
from ..utils import raise_exception_on_status

ADMIN = TypeVar("ADMIN", bound="Admin")


class Admin(Base):
    exists: bool = False

    def __init__(
        self,
        *,
        username: str,
        password: str = "",
        is_sudo: bool = False,
        telegram_id: int = 0,
        discord_webhook: str = "",
        **extra,
    ) -> None:
        self.username = username
        self.password = password
        self.is_sudo = is_sudo
        self.telegram_id = telegram_id
        self.discord_webhook = discord_webhook

    async def save(self, panel: Marzban) -> None:
        url = "/api/admin"
        data = {
            "password": self.password,
            "is_sudo": self.is_sudo,
            "telegram_id": self.telegram_id,
            "discord_webhook": self.discord_webhook,
        }
        if self.exists:
            url += f"/{self.username}"
            response: MarzbanResponse = await panel._send_request(method="PUT", path=url, data=data)
        else:
            data["username"] = self.username
            response: MarzbanResponse = await panel._send_request(
                method="POST", path=url, data=data
            )
        raise_exception_on_status(response)
        self.exists = True

    async def delete(self, panel: Marzban) -> None:
        url = f"/api/admin/{self.username}"
        response: MarzbanResponse = await panel._send_request(method="DELETE", path=url)
        raise_exception_on_status(response)
        self.exists = False

    @classmethod
    async def create(
        cls: Type[ADMIN],
        panel: Marzban,
        *,
        username: str,
        password: str,
        is_sudo: bool = False,
        telegram_id: int = 0,
        discord_webhook: str = "",
    ) -> ADMIN:
        url = "/api/admin"
        data = {
            "username": username,
            "password": password,
            "is_sudo": is_sudo,
            "telegram_id": telegram_id,
            "discord_webhook": discord_webhook,
        }
        response: MarzbanResponse = await panel._send_request(method="POST", path=url, data=data)
        raise_exception_on_status(response)
        admin: ADMIN = cls(
            username=username,
            password=password,
            is_sudo=is_sudo,
            telegram_id=telegram_id,
            discord_webhook=discord_webhook,
        )
        admin.exists = True
        return admin

    @classmethod
    async def get_or_none(cls: Type[ADMIN], panel: Marzban, *, username: str) -> ADMIN | None:
        url = "/api/admins"
        query_params = {"offset": 0, "limit": 0, "username": username}
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        for data in response.content:
            if data["username"] == username:
                admin: ADMIN = cls(**data)
                admin.exists = True
                return admin
        return None

    @classmethod
    async def current(cls: Type[ADMIN], panel: Marzban) -> ADMIN:
        url = "/api/admin"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        admin: ADMIN = cls(**response.content)
        admin.exists = True
        return admin

    @classmethod
    async def all(
        cls: Type[ADMIN],
        panel: Marzban,
        *,
        offset: int = 0,
        limit: int = 0,
        username: str = "",
    ) -> list[ADMIN]:
        url = "/api/admins"
        query_params = {"offset": offset, "limit": limit, "username": username}
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        admins: list[ADMIN] = []
        for data in response.content:
            admin: ADMIN = cls(**data)
            admin.exists = True
            admins.append(admin)
        return admins
