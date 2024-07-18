from enum import Enum


class Flow(str, Enum):
    NONE = ""
    XTLS = "xtls-rprx-vision"


class CipherMethod(str, Enum):
    AES128 = "aes-128-gcm"
    AES256 = "aes-256-gcm"
    CHACHA20 = "chacha20-ietf-poly1305"


class DataLimitResetStrategy(str, Enum):
    NO_RESET = "no_reset"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class UserStatus(str, Enum):
    ACTIVE = "active"
    DSIABLED = "disabled"
    LIMITED = "limited"
    EXPIRED = "expired"
    ON_HOLD = "on_hold"
