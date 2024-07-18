from typing import TypeVar, Type

from pydantic import BaseModel

from .base import Base
from ..marzban import Marzban
from ..marzban_response import MarzbanResponse
from ..enums.host import Security, ALPN, Fingerprint
from ..utils import raise_exception_on_status

HOSTS = TypeVar("HOSTS", bound="Hosts")


class Host(BaseModel):
    remark: str
    address: str
    port: int | None = None
    sni: str | None = None
    host: str | None = None
    path: str | None = None
    security: Security = Security.DEFAULT
    alpn: ALPN = ALPN.NONE
    fingerprint: Fingerprint = Fingerprint.NONE
    allowinsecure: bool | None = None
    fragment_setting: str | None = None
    mux_enable: bool = False
    random_user_agent: bool = False


class Hosts(Base):
    def __init__(self, hosts: dict[str, list[Host]]) -> None:
        self.hosts = hosts

    async def update(self, panel: Marzban) -> None:
        url = "/api/hosts"
        data = {}
        for k, v in self.hosts.items():
            data[k] = [host.model_dump() for host in v]
        response: MarzbanResponse = await panel._send_request(
            method="PUT", path=url, data=data
        )
        raise_exception_on_status(response)

    @classmethod
    async def get(cls: Type[HOSTS], panel: Marzban) -> HOSTS:
        url = "/api/hosts"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        hosts = {}
        for k, v in response.content.items():
            hosts[k] = [Host(**host) for host in v]
        return cls(hosts=hosts)
