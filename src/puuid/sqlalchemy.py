from typing import final, override

from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import String, TypeDecorator

from puuid.base import PUUIDBase

_SEPARATOR_LENGTH = 1
_UUID_LENGTH = 36


@final
class SqlPUUID[TPrefix: str](TypeDecorator[PUUIDBase[TPrefix]]):
    """
    SQLAlchemy type for storing Prefixed UUIDs.

    Maps a `PUUID` instance to a `VARCHAR` column in the database and
    reconstructs the specific `PUUID` subclass on retrieval.
    """

    impl = String
    cache_ok = True

    puuid_cls: type[PUUIDBase[TPrefix]]

    def __init__(self, puuid_cls: type[PUUIDBase[TPrefix]]) -> None:
        """
        Initialize the SqlPUUID type.

        Parameters
        ----------
        puuid_cls : type[PUUIDBase[TPrefix]]
            The pUUID class (e.g., `PUUIDv4[Literal["user"]]`) to associate with this
            column.
        """
        self.puuid_cls = puuid_cls
        varchar_length = len(puuid_cls.prefix()) + _SEPARATOR_LENGTH + _UUID_LENGTH
        super().__init__(length=varchar_length)

    @override
    def process_bind_param(
        self, value: PUUIDBase[TPrefix] | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None
        return value.to_string()

    @override
    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> PUUIDBase[TPrefix] | None:
        if value is None:
            return None
        return self.puuid_cls.from_string(value)
