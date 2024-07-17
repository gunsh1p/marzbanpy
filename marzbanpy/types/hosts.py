from enum import Enum

from pydantic import BaseModel

class Security(str, Enum):
    DEFAULT = "inbounds_default"
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

class Host(BaseModel):
    remark: str
    address: str
    port: int | None = None
    sni: str
    host: str
    path: str | None = None
    security: Security
    alpn: ALPN
    fingerpring: Fingerprint
    allowinsecure: bool | None = None
    fragment_setting: str | None = None
    mux_enable: bool
    random_user_agent: bool