from typing import TypeVar, Type

from ..marzban import Marzban
from .marzban_response import MarzbanResponse
from ..exceptions import (
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ValidationError,
)

ADMIN = TypeVar("ADMIN", bound="Admin")


class Admin:
    exists: bool = False

    def __init__(
        self,
        *,
        username: str,
        password: str | None = None,
        is_sudo: bool = False,
        telegram_id: int = 0,
        discord_webhook: str = "",
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
            response: MarzbanResponse = await panel._send_request(
                method="PUT", url=url, data=data
            )
        else:
            data["username"] = self.username
            response: MarzbanResponse = await panel._send_request(
                method="POST", url=url, data=data
            )

        match response.status:
            case 401:
                raise UnauthorizedError()
            case 403:
                raise ForbiddenError()
            case 404:
                detail: str = response.content["detail"]
                raise NotFoundError(detail)
            case 409:
                detail: str = response.content["detail"]
                raise ConflictError(detail)
            case 422:
                detail: dict = response.content["detail"]
                raise ValidationError(detail)
        self.exists = True

    async def delete(self, panel: Marzban) -> None:
        url = f"/api/admin/{self.username}"
        response: MarzbanResponse = await panel._send_request(method="DELETE", url=url)

        match response.status:
            case 401:
                raise UnauthorizedError()
            case 403:
                raise ForbiddenError()
            case 404:
                detail: str = response.content["detail"]
                raise NotFoundError(detail)
            case 422:
                detail: dict = response.content["detail"]
                raise ValidationError(detail)
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
        response: MarzbanResponse = await panel._send_request(
            method="POST", url=url, data=data
        )

        match response.status:
            case 401:
                raise UnauthorizedError()
            case 403:
                raise ForbiddenError()
            case 409:
                detail: str = response.content["detail"]
                raise ConflictError(detail)
            case 422:
                detail: dict = response.content["detail"]
                raise ValidationError(detail)
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
    async def current(cls: Type[ADMIN], panel: Marzban) -> ADMIN:
        url = "/api/admin"
        response: MarzbanResponse = await panel._send_request(method="GET", url=url)

        if response.status == 401:
            raise UnauthorizedError()
        admin: ADMIN = cls(**response.content)
        admin.exists = True
        return admin

    @classmethod
    async def list(
        cls: Type[ADMIN],
        panel: Marzban,
        *,
        offset: int | None = None,
        limit: int | None = None,
        username: str | None = None,
    ) -> list[ADMIN]:
        url = "/api/admins"
        query_params = {"offset": offset, "limit": limit, "username": username}
        response: MarzbanResponse = await panel._send_request(
            method="GET", url=url, query_params=query_params
        )

        match response.status:
            case 401:
                raise UnauthorizedError()
            case 403:
                raise ForbiddenError()
        admins: list[ADMIN] = []
        for data in response.content:
            admin: ADMIN = cls(**data)
            admin.exists = True
            admins.append(admin)
        return admins
