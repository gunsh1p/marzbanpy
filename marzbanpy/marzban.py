import httpx

from .types import Token
from .types import MarzbanResponse
from .exceptions import ValidationError


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
        data: dict | list | None,
        query_params: dict | None = None,
        as_content: bool = True,
        auth: bool = True,
    ) -> MarzbanResponse:
        """Send request to marzban api"""
        headers = None
        if auth:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            }
        async with httpx.AsyncClient(headers=headers) as client:
            url = f"{self.protocol}://{self.host}:{self.port}{path}"
            content = data if as_content else None
            data = data if not as_content else None
            params = httpx.QueryParams(**query_params)
            response = await client.request(
                method=method,
                url=url,
                content=content,
                data=data,
                params=params,
            )
        return MarzbanResponse(status=response.status_code, content=response.json())

    async def get_token(self) -> None:
        """Gets a token from the Marzban server."""
        data = {"username": self.username, "password": self.password}
        response: MarzbanResponse = await self._send_request(
            method="POST", url="/api/admin/token", data=data, auth=False
        )
        if response.status == 422:
            detail = response.content["detail"]
            raise ValidationError(detail)
        self.token = Token(**response.content)
