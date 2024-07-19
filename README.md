# marzbanpy

An unofficial library for marzban panel

## Install

```sh
pip install marzbanpy
```

## Example

```python
import asyncio

from marzbanpy import Marzban
from marzbanpy.types import User
from marzbanpy.enums.user import UserStatus

async def main():
    panel = Marzban(
        host="example.com",
        port=443,
        ssl=True,
        username="admin",
        password="admin123"
    )
    await panel.auth()

    users = await User.all(
        panel, 
        offset=10, 
        limit=10, 
        status=UserStatus.ACTIVE
    )
    print(users)

asyncio.run(main())
```

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Donation

- BTC: `bc1qmrwu6uv00xcvsjvjkwnaw2ky6aenhjgqewg0w4`
- USDT (TRC-20): `TT8HPQHdWTqk2QgAx6S6hYgCmgCip19D1Z`

### License

The project is under the [MIT](https://github.com/gunsh1p/marzbanpy/blob/main/LICENSE) licence

### Contacts

Telegram Channel: [@thegatesofdisorder](https://t.me/thegatesofdisorder)