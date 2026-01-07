from typing import final, override

from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import String, TypeDecorator

from puuid.base import PUUID

_SEPARATOR_LENGTH = 1
_UUID_LENGTH = 36


@final
class SqlPUUID(TypeDecorator[PUUID[str]]):
    """
    SQLAlchemy type for storing Prefixed UUIDs.

    Maps a `PUUID` instance to a `VARCHAR` column in the database and
    reconstructs the specific `PUUID` subclass on retrieval.
    """

    impl = String
    cache_ok = True

    puuid_cls: type[PUUID[str]]

    def __init__(self, puuid_cls: type[PUUID[str]], prefix_length: int = 4) -> None:
        """
        Initialize the SqlPUUID type.

        Parameters
        ----------
        puuid_cls : type[PUUID[str]]
            The pUUID class (e.g., `UserUUID`) to associate with this column.
        prefix_length : int, default 4
            The length of the prefix string to calculate the column width.
        """
        self.puuid_cls = puuid_cls
        varchar_length = prefix_length + _SEPARATOR_LENGTH + _UUID_LENGTH
        super().__init__(length=varchar_length)

    @override
    def process_bind_param(
        self, value: PUUID[str] | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return None
        return value.to_string()

    @override
    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> PUUID[str] | None:
        if value is None:
            return None
        return self.puuid_cls.from_string(value)
