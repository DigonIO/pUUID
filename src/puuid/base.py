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

        try:
            prefix, serialized_uuid = serial_puuid.split("_", 1)
            deserialized_uuid = UUID(serialized_uuid)

            if prefix != cls._prefix:
                raise ValueError

            return cls(deserialized_uuid)

        except ValueError:
            raise PUUIDError(
                f"Unable to deserialize prefix '{cls._prefix}', separator '_' or UUID for '{cls.__name__}' from '{serial_puuid}'!"
            )

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
                    except PUUIDError as err:
                        raise ValueError(str(err)) from err
                case _:
                    raise ValueError(
                        f"'{cls.__name__}' can not be created from invalid type '{type(value)}' with value '{value}'!"
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
