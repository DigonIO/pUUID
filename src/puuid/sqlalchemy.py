from sqlalchemy.types import String, TypeDecorator

from puuid import PUUID

_SEPARATOR_LENGHT = 1
_UUID_LENGTH = 36


class SqlPUUID(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, puuid_cls: type["PUUID"], prefix_length: int = 4):
        self.puuid_cls = puuid_cls
        varchar_length = prefix_length + _SEPARATOR_LENGHT + _UUID_LENGTH
        super().__init__(length=varchar_length)

    # NOTE: Python => SQLAlchemy
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.to_string()

    # NOTE: SQLAlchemy => Python
    def process_result_value(self, value: str | None, dialect):
        if value is None:
            return None
        return self.puuid_cls.from_string(value)
