from typing import Literal

from puuid import PUUIDv4


class UserID_class(PUUIDv4[Literal["user"]]): ...
