from enum import Enum

class Flow(str, Enum):
    NONE = ""
    XTLS = "xtls-rprx-vision"

class CipherMethod(str, Enum):
    AES128 = "aes-128-gcm"
    AES256 = "aes-256-gcm"
    CHACHA20 = "chacha20-ietf-poly1305"