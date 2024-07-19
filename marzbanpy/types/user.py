from typing import Type, TypeVar
from datetime import datetime
import uuid

from pydantic import BaseModel

from .base import Base
from .admin import Admin
from ..marzban import Marzban
from ..marzban_response import MarzbanResponse
from ..enums.user import Flow, CipherMethod, DataLimitResetStrategy, UserStatus
from ..utils import raise_exception_on_status

USER = TypeVar("USER", bound="User")
TIME_FORMAT = "%Y-%m-%dT%X"


class Proxy(BaseModel):
    id: uuid.UUID | None = None
    flow: Flow | None = None
    password: str | None = None
    method: CipherMethod | None = None

    def model_dump(self) -> dict:
        data = {}
        if self.id is not None:
            data["id"] = str(self.id)
        if self.flow is not None:
            data["flow"] = self.flow.value
        if self.password is not None:
            data["password"] = self.password
        if self.method is not None:
            data["method"] = self.method.value
        return data


class UserNodeUsage(BaseModel):
    node_id: int | None
    node_name: str
    used_traffic: int


class UsageData(BaseModel):
    username: str
    usages: list[UserNodeUsage]


class User(Base):
    exists: bool = False

    def __init__(
        self,
        *,
        username: str,
        expire: datetime | None = None,
        data_limit: int = 0,
        proxies: dict[str, Proxy],
        inbounds: dict[str, list[str]] = {},
        data_limit_reset_strategy: DataLimitResetStrategy = DataLimitResetStrategy.NO_RESET,
        note: str | None = None,
        sub_updated_at: str | None = None,
        sub_last_user_agent: str | None = None,
        online_at: str | None = None,
        on_hold_expire_duration: int | None = None,
        on_hold_timeout: datetime | str | None = None,
        auto_delete_in_days: int | None = None,
        status: UserStatus = UserStatus.ACTIVE,
        used_traffic: int = 0,
        lifetime_used_traffic: int = 0,
        created_at: str | None = None,
        links: list[str] | None = None,
        subscription_url: str | None = None,
        excluded_inbounds: dict[str, list[str]] | None = None,
        admin: dict | None = None,
    ) -> None:
        self.username = username
        self.expire = expire
        self.data_limit = data_limit
        self.proxies = proxies
        self.inbounds = inbounds
        self.data_limit_reset_strategy = data_limit_reset_strategy
        self.note = note
        self.sub_updated_at = (
            datetime.strptime(sub_updated_at.split(".")[0], TIME_FORMAT)
            if isinstance(sub_updated_at, str)
            else None
        )
        self.sub_last_user_agent = sub_last_user_agent
        self.online_at = (
            datetime.strptime(online_at.split(".")[0], TIME_FORMAT)
            if isinstance(online_at, str)
            else None
        )
        self.on_hold_expire_duration = on_hold_expire_duration
        self.on_hold_timeout = (
            datetime.strptime(on_hold_timeout.split(".")[0], TIME_FORMAT)
            if isinstance(on_hold_timeout, str)
            else on_hold_timeout
        )
        self.auto_delete_in_days = auto_delete_in_days
        self.status = status
        self.used_traffic = used_traffic
        self.lifetime_used_traffic = lifetime_used_traffic
        self.created_at = (
            datetime.strptime(created_at.split(".")[0], TIME_FORMAT)
            if isinstance(created_at, str)
            else None
        )
        self.links = links
        self.subscription_url = subscription_url
        self.excluded_inbounds = excluded_inbounds
        self.admin = Admin(**admin) if admin is not None else None

    async def save(self, panel: Marzban) -> None:
        url = "/api/user"
        on_hold_timeout = (
            self.on_hold_timeout.strftime(TIME_FORMAT)
            if self.on_hold_timeout is not None
            else None
        )
        data = {
            "username": self.username,
            "proxies": {k: v.model_dump() for k, v in self.proxies.items()},
            "inbounds": self.inbounds,
            "expire": self.expire.timestamp() if self.expire is not None else None,
            "data_limit": self.data_limit,
            "data_limit_reset_strategy": self.data_limit_reset_strategy,
            "status": self.status.value,
            "note": self.note,
            "on_hold_timeout": on_hold_timeout,
            "on_hold_expire_duration": self.on_hold_expire_duration,
        }
        if self.exists:
            url += f"/{self.username}"
            response: MarzbanResponse = await panel._send_request(
                method="PUT", path=url, data=data
            )
        else:
            data["username"] = self.username
            response: MarzbanResponse = await panel._send_request(
                method="POST", path=url, data=data
            )
        raise_exception_on_status(response)
        self.admin = Admin(**response.content["admin"])
        self.exists = True

    async def delete(self, panel: Marzban) -> None:
        url = f"/api/user/{self.username}"
        response: MarzbanResponse = await panel._send_request(method="DELETE", path=url)
        raise_exception_on_status(response)
        self.exists = False

    async def reset(self, panel: Marzban) -> None:
        url = f"/api/user/{self.username}/reset"
        response: MarzbanResponse = await panel._send_request(method="POST", path=url)
        raise_exception_on_status(response)
        self.used_traffic = 0

    async def revoke(self, panel: Marzban) -> None:
        url = f"/api/user/{self.username}/revoke_sub"
        response: MarzbanResponse = await panel._send_request(method="POST", path=url)
        raise_exception_on_status(response)
        self.links = response.content["links"]
        self.subscription_url = response.content["subscription_url"]
        self.proxies = {k: Proxy(**v) for k, v in response.content["proxies"].items()}

    async def usage(
        self,
        panel: Marzban,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> UsageData:
        url = f"/api/user/{self.username}/usage"
        query_params = {}
        if start is not None:
            query_params["start"] = start.strftime(TIME_FORMAT)
        if end is not None:
            query_params["end"] = end.strftime(TIME_FORMAT)
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        return UsageData(**response.content)

    async def set_owner(self, panel: Marzban, *, admin: Admin | str) -> None:
        url = f"/api/user/{self.username}/set-owner"
        admin_username = admin if isinstance(admin, str) else admin.username
        query_params = {"admin_username": admin_username}
        response: MarzbanResponse = await panel._send_request(
            method="PUT", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        self.admin = Admin(**response.content["admin"])

    @staticmethod
    async def reset_all(panel: Marzban) -> None:
        url = "/api/users/reset"
        response: MarzbanResponse = await panel._send_request(method="POST", path=url)
        raise_exception_on_status(response)

    @classmethod
    async def create(
        cls: Type[USER],
        panel: Marzban,
        *,
        username: str,
        expire: datetime | None = None,
        data_limit: int = 0,
        proxies: dict[str, Proxy],
        inbounds: dict[str, list[str]] = {},
        data_limit_reset_strategy: DataLimitResetStrategy = DataLimitResetStrategy.NO_RESET,
        note: str | None = None,
        on_hold_expire_duration: int | None = None,
        on_hold_timeout: datetime | None = None,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> USER:
        url = "/api/user"
        on_hold_timeout = (
            on_hold_timeout.strftime(TIME_FORMAT)
            if on_hold_timeout is not None
            else None
        )
        data = {
            "username": username,
            "proxies": {k: v.model_dump() for k, v in proxies.items()},
            "inbounds": inbounds,
            "expire": expire.timestamp() if expire is not None else None,
            "data_limit": data_limit,
            "data_limit_reset_strategy": data_limit_reset_strategy,
            "status": status.value,
            "note": note,
            "on_hold_timeout": on_hold_timeout,
            "on_hold_expire_duration": on_hold_expire_duration,
        }
        response: MarzbanResponse = await panel._send_request(
            method="POST", path=url, data=data
        )
        raise_exception_on_status(response)
        user: USER = cls(**response.content)
        user.exists = True
        return user

    @classmethod
    async def get(cls: Type[USER], panel: Marzban, *, username: str) -> USER:
        url = f"/api/user/{username}"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        user = cls(**response.content)
        user.exists = True
        return user

    @classmethod
    async def all(
        cls: Type[USER],
        panel: Marzban,
        *,
        offset: int = 0,
        limit: int = 0,
        username: list[str] | None = None,
        search: str | None = None,
        admin: list[Admin | str] | None = None,
        status: UserStatus = None,
        sort: str = None,
    ) -> list[USER]:
        url = "/api/users"
        query_params = {
            "offset": offset,
            "limit": limit,
        }
        if isinstance(username, list):
            query_params["username"] = username
        if search is not None:
            query_params["search"] = search
        if isinstance(admin, list):
            query_params["admin"] = [
                v if isinstance(v, str) else v.username for v in admin
            ]
        if status is not None:
            query_params["status"] = status.value
        if sort is not None:
            query_params["sort"] = sort
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        users: list[USER] = []
        for data in response.content["users"]:
            user: USER = cls(**data)
            user.exists = True
            users.append(user)
        return users

    @classmethod
    async def get_expired(
        cls: Type[USER],
        panel: Marzban,
        *,
        expired_before: datetime | None = None,
        expired_after: datetime | None = None,
    ) -> list[str]:
        url = "/api/users/expired"
        query_params = {}
        if expired_before is not None:
            query_params["expired_before"] = expired_before.strftime(TIME_FORMAT)
        if expired_after is not None:
            query_params["expired_after"] = expired_after.strftime(TIME_FORMAT)
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        return response.content

    @classmethod
    async def delete_expired(
        cls: Type[USER],
        panel: Marzban,
        *,
        expired_before: datetime | None = None,
        expired_after: datetime | None = None,
    ) -> list[str]:
        url = "/api/users/expired"
        query_params = {}
        if expired_before is not None:
            query_params["expired_before"] = expired_before.strftime(TIME_FORMAT)
        if expired_after is not None:
            query_params["expired_after"] = expired_after.strftime(TIME_FORMAT)
        response: MarzbanResponse = await panel._send_request(
            method="DELETE", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        return response.content
