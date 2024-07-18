import json

from pydantic import BaseModel
import httpx

from .marzban_response import MarzbanResponse
from .enums.system import Protocol, Network, Security
from .token import Token
from .utils import raise_exception_on_status


class Stats(BaseModel):
    version: str
    mem_total: int
    mem_used: int
    cpu_cores: int
    cpu_usage: float
    total_user: int
    users_active: int
    incoming_bandwidth: int
    outgoing_bandwidth: int
    incoming_bandwidth_speed: int
    outgoing_bandwidth_speed: int


class Inbound(BaseModel):
    tag: str
    protocol: Protocol
    network: Network
    tls: Security
    port: int


class System(BaseModel):
    stats: Stats
    inbounds: list[Inbound]


class Marzban:
    """The Marzban class represents a connection to a Marzban server. It provides a way to interact with the server, sending and receiving data."""

    def __init__(
        self,
        *,
        host: str,
        port: int = 8000,
        ssl: bool = False,
        username: str,
        password: str,
    ) -> None:
        """Initializes a new instance of the Marzban class.

        :param host: The hostname or IP address of the Marzban server.
        :param port: The port number to use for the connection. Defaults to 8000.
        :param ssl: A boolean indicating whether to use SSL/TLS encryption for the connection. Defaults to False.
        :param username: The username to use for authentication.
        :param password: The password to use for authentication.
        :return: A new instance of the Marzban class.
        """
        self.host = host
        self.port = port
        self.ssl = ssl
        self.protocol = "https" if ssl else "http"
        self.username = username
        self.password = password

    async def _send_request(
        self,
        *,
        method: str,
        path: str,
        data: dict | list | None = {},
        as_content: bool = True,
        query_params: dict | None = None,
        auth: bool = True,
    ) -> MarzbanResponse:
        """Send request to marzban api"""
        headers = None
        if auth:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            }
        url = f"{self.protocol}://{self.host}:{self.port}{path}"
        async with httpx.AsyncClient(headers=headers) as client:
            if as_content:
                content = json.dumps(data) if data is not None else None
                response = await client.request(
                    method=method,
                    url=url,
                    content=content,
                    params=query_params,
                )
            else:
                response = await client.request(
                    method=method,
                    url=url,
                    data=data,
                    params=query_params,
                )
        return MarzbanResponse(status=response.status_code, content=response.json())

    async def get_token(self) -> None:
        """Gets a token from the Marzban server."""
        url = "/api/admin/token"
        data = {"username": self.username, "password": self.password}
        response: MarzbanResponse = await self._send_request(
            method="POST", path=url, data=data, as_content=False, auth=False
        )
        raise_exception_on_status(response)
        self.token = Token(**response.content)

    async def get_system(self) -> System:
        """Gets the stats and inbounds from the Marzban server."""
        url = "/api/system"
        response: MarzbanResponse = await self._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        stats = Stats(**response.content)

        url = "/api/inbounds"
        response: MarzbanResponse = await self._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        inbounds: list[Inbound] = []
        for _, proto_inbounds in response.content.items():
            for inbound in list(proto_inbounds):
                inbounds.append(Inbound(**inbound))
        return System(stats=stats, inbounds=inbounds)
