from typing import Self, overload, override
from uuid import UUID, uuid1, uuid3, uuid4, uuid5, uuid6, uuid7, uuid8

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from abc import ABC, abstractmethod

_ERROR_UUID_VERSION_MISMATCH = "Expected 'UUID' with version '{expected}', got {actual}"


class PUUIDError(Exception):
    message: str

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message


################################################################################
#### PUUID
################################################################################


class PUUID[TPrefix: str](ABC):
    _prefix: TPrefix
    _serial: str
    _uuid: UUID

    @abstractmethod
    def __init__(self, *, uuid: UUID) -> None: ...

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
        raise PUUIDError("PUUID.factory is only supported for 'PUUIDv1', 'PUUIDv4', 'PUUIDv6', 'PUUIDv7' and 'PUUIDv8'!")

    @classmethod
    def from_string(cls, serial_puuid: str) -> Self:
        try:
            prefix, serialized_uuid = serial_puuid.split("_", 1)
            if prefix != cls._prefix:
                raise ValueError

            uuid = UUID(serialized_uuid)
            return cls(uuid=uuid)

        except ValueError as err:
            raise PUUIDError(
                f"Unable to deserialize prefix '{cls._prefix}', separator '_' or UUID for '{cls.__name__}' from '{serial_puuid}'!"
            ) from err

    @override
    def __str__(self) -> str:
        return self._serial

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, PUUID):
            return self._serial == other._serial
        return False

    @override
    def __hash__(self) -> int:
        return hash((self._prefix, self._uuid))

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: object,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate(value: object) -> PUUID[TPrefix]:

            if isinstance(value, cls):
                return value

            if isinstance(value, str):
                try:
                    return cls.from_string(value)
                except PUUIDError as err:
                    raise ValueError(str(err)) from err

            raise ValueError(
                f"'{cls.__name__}' can not be created from invalid type '{type(value)}' with value '{value}'!"
            )


        def serialize(value: PUUID[TPrefix]) -> str:
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
    _uuid: UUID
    _serial: str


    @overload
    def __init__(
        self, *, node: int | None = None, clock_seq: int | None = None
    ) -> None: ...

    @overload
    def __init__(self, *, uuid: UUID) -> None: ...

    def __init__(
        self,
        *,
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

    @override
    @classmethod
    def factory(cls) -> Self:
        return cls()


################################################################################
#### PUUIDv3
################################################################################


class PUUIDv3[TPrefix: str](PUUID[TPrefix]):
    _uuid: UUID
    _serial: str


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
    _uuid: UUID
    _serial: str

    def __init__(self, uuid: UUID | None = None) -> None:
        if uuid is not None and uuid.version != 4:
            raise PUUIDError(
                _ERROR_UUID_VERSION_MISMATCH.format(expected=4, actual=uuid.version)
            )
        self._uuid = uuid if uuid else uuid4()
        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        return cls()


################################################################################
#### PUUIDv5
################################################################################


class PUUIDv5[TPrefix: str](PUUID[TPrefix]):
    _uuid: UUID
    _serial: str

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


################################################################################
#### PUUIDv6
################################################################################


class PUUIDv6[TPrefix: str](PUUID[TPrefix]):
    _uuid: UUID
    _serial: str

    @overload
    def __init__(
        self, *, node: int | None = None, clock_seq: int | None = None
    ) -> None: ...

    @overload
    def __init__(self, *, uuid: UUID) -> None: ...

    def __init__(
        self,
        *,
        node: int | None = None,
        clock_seq: int | None = None,
        uuid: UUID | None = None,
    ) -> None:

        match node, clock_seq, uuid:
            case int() | None, int() | None, None:
                self._uuid = uuid6(node, clock_seq)
            case None, None, UUID(version=6):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    _ERROR_UUID_VERSION_MISMATCH.format(expected=6, actual=version)
                )
            case _:
                raise PUUIDError(
                    "Invalid 'PUUIDv6' arguments: Provide 'node'/'clock_seq' or only 'uuid'!"
                )

        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        return cls()


################################################################################
#### PUUIDv7
################################################################################


class PUUIDv7[TPrefix: str](PUUID[TPrefix]):
    _uuid: UUID
    _serial: str


    def __init__(self, uuid: UUID | None = None) -> None:
        if uuid is not None and uuid.version != 7:
            raise PUUIDError(
                _ERROR_UUID_VERSION_MISMATCH.format(expected=7, actual=uuid.version)
            )
        self._uuid = uuid if uuid else uuid7()
        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        return cls()


################################################################################
#### PUUIDv8
################################################################################


class PUUIDv8[TPrefix: str](PUUID[TPrefix]):
    _uuid: UUID
    _serial: str

    @overload
    def __init__(
        self, *, a: int | None = None, b: int | None = None, c: int | None = None
    ) -> None: ...

    @overload
    def __init__(self, *, uuid: UUID) -> None: ...

    def __init__(
        self,
        *,
        a: int | None = None,
        b: int | None = None,
        c: int | None = None,
        uuid: UUID | None = None,
    ) -> None:
        match a, b, c, uuid:
            case int() | None, int() | None, int() | None, None:
                self._uuid = uuid8(a, b, c)
            case None, None, None, UUID(version=8):
                self._uuid = uuid
            case None, None, None, UUID(version=version):
                raise PUUIDError(
                    _ERROR_UUID_VERSION_MISMATCH.format(expected=8, actual=version)
                )
            case _:
                raise PUUIDError(
                    "Invalid 'PUUIDv8' arguments: Provide 'a'/'b'/'c' or only 'uuid'!"
                )

        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        return cls()