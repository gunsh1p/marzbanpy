from enum import Enum


class Protocol(str, Enum):
    VMESS = "vmess"
    VLESS = "vless"
    TROJAN = "trojan"
    SHADOWSOCKS = "shadowsocks"


class Network(str, Enum):
    TCP = "tcp"
    WS = "ws"
    H2 = "h2"
    GRPC = "grpc"
    QUIC = "quic"
    KCP = "kcp"
    HTTPUPGRADE = "httpupgrade"
    SPLITHTTP = "splithttp"


class Security(str, Enum):
    NONE = "none"
    TLS = "tls"
    REALITY = "reality"
