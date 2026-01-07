"""
pUUID Base Implementation.

Provides the abstract base class and version-specific implementations for Prefixed UUIDs.
"""

from abc import ABC, abstractmethod
from typing import Self, final, overload, override
from uuid import UUID, uuid1, uuid3, uuid4, uuid5, uuid6, uuid7, uuid8

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


@final
class ERR_MSG:
    UUID_VERSION_MISMATCH = "Expected 'UUID' with version '{expected}', got '{actual}'"
    FACTORY_UNSUPPORTED = "'PUUID.factory' is only supported for 'PUUIDv1', 'PUUIDv4', 'PUUIDv6', 'PUUIDv7' and 'PUUIDv8'!"
    PREFIX_DESERIALIZATION_ERROR = "Unable to deserialize prefix '{prefix}', separator '_' or UUID for '{classname}' from '{serial_puuid}'!"
    INVALID_TYPE_FOR_SERIAL_PUUID = "'{classname}' can not be created from invalid type '{type}' with value '{value}'!"
    INVALID_PUUIDv1_ARGS = "Invalid 'PUUIDv1' arguments: Provide either 'node' and 'clock_seq' or a 'uuid'!"
    INVALID_PUUIDv3_ARGS = "Invalid 'PUUIDv3' arguments: Provide either 'namespace' and 'name' or a 'uuid'!"
    INVALID_PUUIDv5_ARGS = "Invalid 'PUUIDv5' arguments: Provide either 'namespace' and 'name' or a 'uuid'!"
    INVALID_PUUIDv6_ARGS = "Invalid 'PUUIDv6' arguments: Provide either 'node' and 'clock_seq' or a 'uuid'!"
    INVALID_PUUIDv8_ARGS = (
        "Invalid 'PUUIDv8' arguments: Provide either 'a', 'b' and 'c' or 'uuid'!"
    )


class PUUIDError(Exception):
    """Base exception for pUUID related errors."""

    message: str

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message


################################################################################
#### PUUID
################################################################################


class PUUID[TPrefix: str](ABC):
    """Abstract Base Class for Prefixed UUIDs."""

    _prefix: TPrefix
    _serial: str
    _uuid: UUID

    @abstractmethod
    def __init__(self, *, uuid: UUID) -> None: ...

    @classmethod
    def prefix(cls) -> TPrefix:
        """
        Return the defined prefix for the class.

        Returns
        -------
        TPrefix
            The prefix string.
        """
        return cls._prefix

    @property
    def uuid(self) -> UUID:
        """
        Return the underlying UUID object.

        Returns
        -------
        UUID
            The native UUID instance.
        """
        return self._uuid

    def to_string(self) -> str:
        """
        Return the string representation of the Prefixed UUID.

        Returns
        -------
        str
            The formatted string (e.g., `<prefix>_<uuid-hex-string>`).
        """
        return self._serial

    @classmethod
    def factory(cls) -> Self:
        """
        Create a new instance using default generation.

        Supported by version variants that allow generation without arguments.

        Returns
        -------
        Self
            A new instance of the pUUID class.

        Raises
        ------
        PUUIDError
            If the variant does not support parameterless generation.
        """
        raise PUUIDError(ERR_MSG.FACTORY_UNSUPPORTED)

    @classmethod
    def from_string(cls, serial_puuid: str) -> Self:
        """
        Create a pUUID instance from its string representation.

        Parameters
        ----------
        serial_puuid : str
            The prefixed UUID string (e.g., `user_550e8400-e29b...`).

        Returns
        -------
        Self
            The deserialized pUUID instance.

        Raises
        ------
        PUUIDError
            If the string is malformed or the prefix does not match.
        """
        try:
            if "_" not in serial_puuid:
                raise ValueError("Missing separator")

            prefix, serialized_uuid = serial_puuid.split("_", 1)

            if prefix != cls._prefix:
                raise ValueError("Prefix mismatch")

            uuid = UUID(serialized_uuid)
            return cls(uuid=uuid)

        except ValueError as err:
            raise PUUIDError(
                ERR_MSG.PREFIX_DESERIALIZATION_ERROR.format(
                    prefix=cls._prefix,
                    classname=cls.__name__,
                    serial_puuid=serial_puuid,
                )
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
                ERR_MSG.INVALID_TYPE_FOR_SERIAL_PUUID.format(
                    classname=cls.__name__, type=type(value), value=value
                )
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
    """Prefixed UUID Version 1 (MAC address and time)."""

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
        """
        Initialize a PUUIDv1.

        Parameters
        ----------
        node : int | None, optional
            Hardware address. If None, `uuid1` generates a random value.
        clock_seq : int | None, optional
            Clock sequence.
        uuid : UUID | None, optional
            Existing UUID v1 instance.

        Raises
        ------
        PUUIDError
            If arguments are inconsistent or the UUID version is incorrect.
        """
        match node, clock_seq, uuid:
            case int() | None, int() | None, None:
                self._uuid = uuid1(node, clock_seq)
            case None, None, UUID(version=1):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    ERR_MSG.UUID_VERSION_MISMATCH.format(expected=1, actual=version)
                )
            case _:
                raise PUUIDError(ERR_MSG.INVALID_PUUIDv1_ARGS)

        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv1 instance using current time and MAC address.

        Returns
        -------
        Self
            A new pUUID v1 instance.
        """
        return cls()


################################################################################
#### PUUIDv3
################################################################################


class PUUIDv3[TPrefix: str](PUUID[TPrefix]):
    """Prefixed UUID Version 3 (MD5 hash of namespace and name)."""

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
        """
        Initialize a PUUIDv3.

        Parameters
        ----------
        namespace : UUID | None, optional
            Namespace UUID.
        name : str | bytes | None, optional
            The name used for hashing.
        uuid : UUID | None, optional
            Existing UUID v3 instance.

        Raises
        ------
        PUUIDError
            If arguments are inconsistent or the UUID version is incorrect.
        """
        match namespace, name, uuid:
            case UUID(), str() | bytes(), None:
                self._uuid = uuid3(namespace, name)
            case None, None, UUID(version=3):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    ERR_MSG.UUID_VERSION_MISMATCH.format(expected=3, actual=version)
                )
            case _:
                raise PUUIDError(ERR_MSG.INVALID_PUUIDv3_ARGS)

        self._serial = f"{self._prefix}_{self._uuid}"


################################################################################
#### PUUIDv4
################################################################################


class PUUIDv4[TPrefix: str](PUUID[TPrefix]):
    """Prefixed UUID Version 4 (randomly generated)."""

    _uuid: UUID
    _serial: str

    def __init__(self, uuid: UUID | None = None) -> None:
        """
        Initialize a PUUIDv4.

        Parameters
        ----------
        uuid : UUID | None, optional
            Existing UUID v4 instance. If None, a new random UUID is generated.

        Raises
        ------
        PUUIDError
            If the provided UUID is not version 4.
        """
        if uuid is not None and uuid.version != 4:
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=4, actual=uuid.version)
            )
        self._uuid = uuid if uuid else uuid4()
        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv4 instance using random generation.

        Returns
        -------
        Self
            A new pUUID v4 instance.
        """
        return cls()


################################################################################
#### PUUIDv5
################################################################################


class PUUIDv5[TPrefix: str](PUUID[TPrefix]):
    """Prefixed UUID Version 5 (SHA-1 hash of namespace and name)."""

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
        """
        Initialize a PUUIDv5.

        Parameters
        ----------
        namespace : UUID | None, optional
            Namespace UUID.
        name : str | bytes | None, optional
            The name used for hashing.
        uuid : UUID | None, optional
            Existing UUID v5 instance.

        Raises
        ------
        PUUIDError
            If arguments are inconsistent or the UUID version is incorrect.
        """
        match namespace, name, uuid:
            case UUID(), str() | bytes(), None:
                self._uuid = uuid5(namespace, name)
            case None, None, UUID(version=5):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    ERR_MSG.UUID_VERSION_MISMATCH.format(expected=5, actual=version)
                )
            case _:
                raise PUUIDError(ERR_MSG.INVALID_PUUIDv5_ARGS)

        self._serial = f"{self._prefix}_{self._uuid}"


################################################################################
#### PUUIDv6
################################################################################


class PUUIDv6[TPrefix: str](PUUID[TPrefix]):
    """Prefixed UUID Version 6 (reordered v1 for DB locality)."""

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
        """
        Initialize a PUUIDv6.

        Parameters
        ----------
        node : int | None, optional
            Hardware address.
        clock_seq : int | None, optional
            Clock sequence.
        uuid : UUID | None, optional
            Existing UUID v6 instance.

        Raises
        ------
        PUUIDError
            If arguments are inconsistent or the UUID version is incorrect.
        """
        match node, clock_seq, uuid:
            case int() | None, int() | None, None:
                self._uuid = uuid6(node, clock_seq)
            case None, None, UUID(version=6):
                self._uuid = uuid
            case None, None, UUID(version=version):
                raise PUUIDError(
                    ERR_MSG.UUID_VERSION_MISMATCH.format(expected=6, actual=version)
                )
            case _:
                raise PUUIDError(ERR_MSG.INVALID_PUUIDv6_ARGS)

        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv6 instance using reordered time-based generation.

        Returns
        -------
        Self
            A new pUUID v6 instance optimized for DB locality.
        """
        return cls()


################################################################################
#### PUUIDv7
################################################################################


class PUUIDv7[TPrefix: str](PUUID[TPrefix]):
    """Prefixed UUID Version 7 (time-ordered)."""

    _uuid: UUID
    _serial: str

    def __init__(self, uuid: UUID | None = None) -> None:
        """
        Initialize a PUUIDv7.

        Parameters
        ----------
        uuid : UUID | None, optional
            Existing UUID v7 instance. If None, a new time-ordered UUID is generated.

        Raises
        ------
        PUUIDError
            If the provided UUID is not version 7.
        """
        if uuid is not None and uuid.version != 7:
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=7, actual=uuid.version)
            )
        self._uuid = uuid if uuid else uuid7()
        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv7 instance using time-ordered generation.

        Returns
        -------
        Self
            A new pUUID v7 instance.
        """
        return cls()


################################################################################
#### PUUIDv8
################################################################################


class PUUIDv8[TPrefix: str](PUUID[TPrefix]):
    """Prefixed UUID Version 8 (custom implementation)."""

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
        """
        Initialize a PUUIDv8.

        Parameters
        ----------
        a : int | None, optional
            First custom 48-bit value.
        b : int | None, optional
            Second custom 12-bit value.
        c : int | None, optional
            Third custom 62-bit value.
        uuid : UUID | None, optional
            Existing UUID v8 instance.

        Raises
        ------
        PUUIDError
            If arguments are inconsistent or the UUID version is incorrect.
        """
        match a, b, c, uuid:
            case int() | None, int() | None, int() | None, None:
                self._uuid = uuid8(a, b, c)
            case None, None, None, UUID(version=8):
                self._uuid = uuid
            case None, None, None, UUID(version=version):
                raise PUUIDError(
                    ERR_MSG.UUID_VERSION_MISMATCH.format(expected=8, actual=version)
                )
            case _:
                raise PUUIDError(ERR_MSG.INVALID_PUUIDv8_ARGS)

        self._serial = f"{self._prefix}_{self._uuid}"

    @override
    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv8 instance using custom generation.

        Returns
        -------
        Self
            A new pUUID v8 instance.
        """
        return cls()
