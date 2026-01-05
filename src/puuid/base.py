from typing import Any, Self, overload
from uuid import UUID, uuid1, uuid3, uuid4, uuid5

from pydantic_core import core_schema

_ERROR_UUID_VERSION_MISMATCH = "Expected 'UUID' with version '{expected}', got {actual}"


class PUUIDError(Exception):
    message: str

    def __init__(self, message: str = ""):
        self.message = message


################################################################################
#### PUUID
################################################################################


class PUUID[TPrefix: str]:
    _prefix: TPrefix
    _serial: str
    _uuid: UUID

    def __init__(self, *, uuid: UUID | None) -> None:
        raise PUUIDError("Can not instantiate abstract class 'PUUID'!")

    @classmethod
    def prefix(cls) -> TPrefix:
        return cls._prefix

    @property
    def uuid(self) -> UUID:
        return self._uuid

    def to_string(self) -> str:
        return self._serial

    @classmethod
    def factory(cls) -> Self:
        raise PUUIDError("The factory is only available for 'PUUIDv1' and 'PUUIDv4'!")

    @classmethod
    def from_string(cls, serial_puuid: str) -> Self:

        try:
            prefix, serialized_uuid = serial_puuid.split("_", 1)
            if prefix != cls._prefix:
                raise ValueError

            uuid = UUID(serialized_uuid)
            return cls(uuid=uuid)

        except ValueError:
            raise PUUIDError(
                f"Unable to deserialize prefix '{cls._prefix}', separator '_' or UUID for '{cls.__name__}' from '{serial_puuid}'!"
            )

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


################################################################################
#### PUUIDv1
################################################################################


class PUUIDv1[TPrefix: str](PUUID[TPrefix]):

    @overload
    def __init__(
        self, *, node: int | None = None, clock_seq: int | None = None
    ) -> None: ...

    @overload
    def __init__(self, *, uuid: UUID | None) -> None: ...

    def __init__(
        self,
        node: int | None = None,
        clock_seq: int | None = None,
        uuid: UUID | None = None,
    ) -> None:

        match node, clock_seq, uuid:
            case int() | None, int() | None, None:
                self._uuid = uuid1(node, clock_seq)
            case None, None, UUID(version=1):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    _ERROR_UUID_VERSION_MISMATCH.format(expected=1, actual=version)
                )
            case _:
                raise PUUIDError(
                    "Invalid 'PUUIDv1' arguments: Provide 'node'/'clock_seq' or only 'uuid'!"
                )

        self._serial = f"{self._prefix}_{self._uuid}"

    @classmethod
    def factory(cls) -> Self:
        return cls()


################################################################################
#### PUUIDv3
################################################################################


class PUUIDv3[TPrefix: str](PUUID[TPrefix]):

    @overload
    def __init__(self, *, namespace: UUID, name: str | bytes) -> None: ...

    @overload
    def __init__(self, *, uuid: UUID) -> None: ...

    def __init__(
        self,
        *,
        namespace: UUID | None = None,
        name: str | bytes | None = None,
        uuid: UUID | None = None,
    ) -> None:

        match namespace, name, uuid:
            case UUID(), str() | bytes(), None:
                self._uuid = uuid3(namespace, name)
            case None, None, UUID(version=3):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    _ERROR_UUID_VERSION_MISMATCH.format(expected=3, actual=version)
                )
            case _:
                raise PUUIDError(
                    "Invalid 'PUUIDv3' arguments: Provide 'namespace'/'name' or only 'uuid'!"
                )

        self._serial = f"{self._prefix}_{self._uuid}"


################################################################################
#### PUUIDv4
################################################################################


class PUUIDv4[TPrefix: str](PUUID[TPrefix]):

    def __init__(self, uuid: UUID | None = None) -> None:
        if uuid is not None and uuid.version != 4:
            raise PUUIDError(
                _ERROR_UUID_VERSION_MISMATCH.format(expected=4, actual=uuid.version)
            )
        self._uuid = uuid if uuid else uuid4()
        self._serial = f"{self._prefix}_{self._uuid}"

    @classmethod
    def factory(cls) -> Self:
        return cls()


################################################################################
#### PUUIDv5
################################################################################


class PUUIDv5[TPrefix: str](PUUID[TPrefix]):

    @overload
    def __init__(self, *, namespace: UUID, name: str | bytes) -> None: ...

    @overload
    def __init__(self, *, uuid: UUID) -> None: ...

    def __init__(
        self,
        *,
        namespace: UUID | None = None,
        name: str | bytes | None = None,
        uuid: UUID | None = None,
    ) -> None:

        match namespace, name, uuid:
            case UUID(), str() | bytes(), None:
                self._uuid = uuid5(namespace, name)
            case None, None, UUID(version=5):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    _ERROR_UUID_VERSION_MISMATCH.format(expected=5, actual=version)
                )
            case _:
                raise PUUIDError(
                    "Invalid 'PUUIDv5' arguments: Provide 'namespace'/'name' or only 'uuid'!"
                )

        self._serial = f"{self._prefix}_{self._uuid}"
