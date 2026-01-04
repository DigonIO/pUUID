from typing import Any, Self
from uuid import UUID, uuid4

from pydantic_core import core_schema


class PUUIDError(Exception):
    message: str

    def __init__(self, message: str = ""):
        self.message = message


class PUUID[TPrefix: str]:
    _prefix: TPrefix
    _serial: str

    def __init__(self, value: UUID | None = None) -> None:
        self._uuid = value or uuid4()
        self._serial = f"{self._prefix}_{self._uuid}"

    @classmethod
    def prefix(cls) -> TPrefix:
        return cls._prefix

    @property
    def uuid(self) -> UUID:
        return self._uuid

    def to_string(self) -> str:
        return self._serial

    @classmethod
    def from_string(cls, serial_puuid: str) -> Self:

        expected = f"{cls._prefix}_"
        if not serial_puuid.startswith(expected):
            raise PUUIDError(f"Expected prefix '{cls._prefix}' for '{serial_puuid}'!")

        serial_uuid = serial_puuid[len(expected) :]
        return cls(value=UUID(serial_uuid))

    @classmethod
    def factory(cls) -> Self:
        return cls()

    def __str__(self) -> str:
        return self._serial

    def __eq__(self, other):
        if isinstance(other, PUUID):
            return self._serial == other._serial
        return False

    def __hash__(self):
        return hash((self._prefix, self._uuid))

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:

        def validate(value: Any) -> PUUID:
            match value:
                case PUUID():
                    return value
                case str():
                    try:
                        return cls.from_string(value)
                    except Exception as e:
                        raise ValueError(str(e)) from e
                case _:
                    raise TypeError(
                        f"'{cls.__name__}' can not be created! '{value!r}' has invalid type!"
                    )

        def serialize(value: PUUID) -> str:
            return value.to_string()

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize,
                return_schema=core_schema.str_schema(),
            ),
        )
