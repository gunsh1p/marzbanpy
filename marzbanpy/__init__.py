from .marzban import Marzban
from . import types

__all__ = ("Marzban", "types")

async def test():
    admin = await types.Admin.current(Marzban())