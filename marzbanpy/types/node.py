from typing import Type, TypeVar
from datetime import datetime

from pydantic import BaseModel

from .base import Base
from ..marzban import Marzban
from ..enums.node import NodeStatus
from ..marzban_response import MarzbanResponse
from ..utils import raise_exception_on_status

NODE = TypeVar("NODE", bound="Node")
TIME_FORMAT = "%Y-%m-%dT%X"


class NodeSettings(BaseModel):
    min_node_version: str
    certificate: str


class NodeUsage(BaseModel):
    node_id: int | None
    node_name: str
    uplink: int
    downlink: int


class Node(Base):
    exists: bool = False

    def __init__(
        self,
        *,
        name: str,
        address: str,
        id: int | None = None,
        port: int = 62050,
        api_port: int = 62051,
        add_as_new_host: bool | None = None,
        usage_coefficient: float = 1,
        xray_version: str | None = None,
        status: NodeStatus | None = None,
        message: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.address = address
        self.port = port
        self.api_port = api_port
        self.add_as_new_host = add_as_new_host
        self.usage_coefficient = usage_coefficient
        self.xray_version = xray_version
        self.status = NodeStatus(status) if status is not None else None
        self.message = message

    async def save(self, panel: Marzban) -> None:
        url = "/api/node"
        data = {
            "name": self.name,
            "address": self.address,
            "port": self.port,
            "api_port": self.api_port,
            "usage_coefficient": self.usage_coefficient,
        }
        if self.exists:
            url += f"/{self.id}"
            data["status"] = self.status.value
            response: MarzbanResponse = await panel._send_request(
                method="PUT", path=url, data=data
            )
        else:
            data["add_as_new_host"] = self.add_as_new_host
            response: MarzbanResponse = await panel._send_request(
                method="POST", path=url, data=data
            )
        raise_exception_on_status(response)
        self.id = response.content["id"]
        self.add_as_new_host = None
        self.xray_version = response.content["xray_version"]
        self.status = NodeStatus(response.content["status"])
        self.message = response.content["message"]
        self.exists = True

    async def delete(self, panel: Marzban) -> None:
        url = f"/api/node/{self.id}"
        response: MarzbanResponse = await panel._send_request(method="DELETE", path=url)
        raise_exception_on_status(response)
        self.exists = False

    async def reconnect(self, panel: Marzban) -> None:
        url = f"/api/node/{self.id}/reconnect"
        response: MarzbanResponse = await panel._send_request(method="POST", path=url)
        raise_exception_on_status(response)

    @staticmethod
    async def get_settings(panel: Marzban) -> NodeSettings:
        url = "/api/node/settings"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        return NodeSettings(**response.content)

    @staticmethod
    async def usage(
        panel: Marzban, start: datetime | None = None, end: datetime | None = None
    ) -> list[NodeUsage]:
        url = "/api/nodes/usage"
        query_params = {}
        if isinstance(start, datetime):
            query_params["start"] = start.strftime(TIME_FORMAT)
        if isinstance(end, datetime):
            query_params["end"] = end.strftime(TIME_FORMAT)
        response: MarzbanResponse = await panel._send_request(
            method="GET", path=url, query_params=query_params
        )
        raise_exception_on_status(response)
        usages: list[NodeUsage] = []
        for data in response.content["usage"]:
            usages.append(NodeUsage(**data))
        return usages

    @classmethod
    async def get(cls: Type[NODE], panel: Marzban, id: int) -> NODE:
        url = f"/api/node/{id}"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        node = cls(**response.content)
        node.exists = True
        return node

    @classmethod
    async def all(cls: Type[NODE], panel: Marzban) -> list[NODE]:
        url = "/api/nodes"
        response: MarzbanResponse = await panel._send_request(method="GET", path=url)
        raise_exception_on_status(response)
        nodes: list[NODE] = []
        for data in response.content:
            node = cls(**data)
            node.exists = True
            nodes.append(node)
        return nodes
