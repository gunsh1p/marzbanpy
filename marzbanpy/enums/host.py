from enum import Enum


class Security(str, Enum):
    DEFAULT = "inbound_default"
    TLS = "tls"
    NONE = "none"


class ALPN(str, Enum):
    NONE = ""
    H3 = "h3"
    H2 = "h2"
    H1 = "http/1.1"
    ALL = "h3,h2,http/1.1"
    H3H2 = "h3,h2"
    H2H1 = "h2,http/1.1"


class Fingerprint(str, Enum):
    NONE = ""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    IOS = "ios"
    ANDROID = "android"
    EDGE = "edge"
    F360 = "360"
    QQ = "qq"
    RANDOM = "random"
    RANDOMIZED = "randomized"
