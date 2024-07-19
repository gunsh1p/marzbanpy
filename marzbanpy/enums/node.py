from enum import Enum


class NodeStatus(str, Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    ERROR = "error"
    DISABLED = "disabled"
