"""
pUUID base implementation.

Provides the abstract base class and version-specific implementations for prefixed UUIDs.
"""

import annotationlib
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Final,
    Literal,
    Self,
    TypeAliasType,
    final,
    get_args,
    get_origin,
    override,
)
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid4, uuid5, uuid6, uuid7, uuid8

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import core_schema

    _PYDANTIC_AVAILABLE = True
else:
    try:
        from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
        from pydantic.json_schema import JsonSchemaValue
        from pydantic_core import core_schema

        _PYDANTIC_AVAILABLE = True
    except ModuleNotFoundError:
        _PYDANTIC_AVAILABLE = False

        class GetCoreSchemaHandler: ...

        class _CoreSchema: ...

        @final
        class core_schema:
            CoreSchema = _CoreSchema


@final
class ERR_MSG:
    UUID_VERSION_MISMATCH = "Expected 'UUID' with version '{expected}', got '{actual}'"
    PREFIX_DESERIALIZATION_ERROR = "Unable to deserialize prefix '{prefix}', separator '_' or UUID for '{classname}' from '{serial_puuid}'!"
    INVALID_TYPE_FOR_SERIAL_PUUID = "'{classname}' can not be created from invalid type '{type}' with value '{value}'!"
    EMPTY_PREFIX_DISALLOWED = "Empty prefix is not allowed for '{classname}'!"


class PUUIDError(Exception):
    """Base exception for pUUID related errors."""

    message: str

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message


################################################################################
#### utilities
################################################################################


def _evaluate_type_alias(value: object) -> object:
    """
    Resolve a PEP 695 `type Alias = ...` (TypeAliasType) to its underlying value.
    """
    if isinstance(value, TypeAliasType):
        return annotationlib.call_evaluate_function(
            value.evaluate_value,
            annotationlib.Format.VALUE,
            owner=value,
        )
    return value


def _try_extract_literal_string(item: object) -> str | None:
    """
    If `item` is `Literal["..."]` (possibly via a `type` alias), return its string.
    Otherwise return None.
    """
    evaluated = _evaluate_type_alias(item)
    if get_origin(evaluated) is Literal:
        args = get_args(evaluated)
        if len(args) == 1 and isinstance(args[0], str):
            return args[0]
    return None


################################################################################
#### PUUIDBase
################################################################################


class PUUIDBase[TPrefix: str](ABC):
    """Abstract Generic Base Class for Prefixed UUIDs."""

    _prefix: ClassVar[str] = ""
    _serial: str | None = None
    _uuid: UUID

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Automatic prefix assignment from the type parameter
        for base in getattr(cls, "__orig_bases__", []):
            origin = get_origin(base)
            if origin is not None and issubclass(origin, PUUIDBase):
                args = get_args(base)
                if args:
                    prefix = _try_extract_literal_string(args[0])
                    if prefix is None:  # e.g. args[0] is TypeVar TPrefix
                        return
                    if prefix == "":
                        raise PUUIDError(
                            ERR_MSG.EMPTY_PREFIX_DISALLOWED.format(
                                classname=cls.__name__
                            )
                        )
                    cls._prefix = prefix
                    return
        raise AssertionError(
            "Something unexpected happened in the usage of the PUUID library"
        )

    @abstractmethod
    def __init__(self, uuid: UUID, *, check_version: bool = True) -> None: ...

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        instance = super().__new__(cls)
        if not cls._prefix:
            raise PUUIDError(
                ERR_MSG.EMPTY_PREFIX_DISALLOWED.format(classname=cls.__name__)
            )
        return instance

    @classmethod
    def prefix(cls) -> str:
        """
        Return the defined prefix for the class.

        Returns
        -------
        str
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

    def _format_serial(self) -> str:
        return f"{type(self)._prefix}_{self._uuid}"

    def to_string(self) -> str:
        """
        Return the string representation of the Prefixed UUID.

        Returns
        -------
        str
            The formatted string (e.g., `<prefix>_<uuid-hex-string>`).
        """
        if self._serial is not None:
            return self._serial

        serial = self._format_serial()
        self._serial = serial
        return serial

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
        return self.to_string()

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PUUIDBase):
            return False

        return (self._prefix, self._uuid) == (other._prefix, other._uuid)

    @override
    def __hash__(self) -> int:
        return hash((type(self)._prefix, self._uuid))

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: object,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        if not _PYDANTIC_AVAILABLE:
            raise ModuleNotFoundError(
                "pydantic is an optional dependency. Install with: pip install 'pUUID[pydantic]'"
            )

        def validate(value: object) -> PUUIDBase[TPrefix]:
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

        def serialize(value: PUUIDBase[TPrefix]) -> str:
            return value.to_string()

        def wrap_validate(value: object, handler: Any) -> PUUIDBase[TPrefix]:
            return validate(value)

        return core_schema.json_or_python_schema(
            json_schema=core_schema.no_info_wrap_validator_function(
                wrap_validate,
                core_schema.str_schema(),
            ),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        version = getattr(cls, "VERSION", 0)
        match version:
            case 1:
                examples = [f"{cls._prefix}_{uuid1()}" for _ in range(3)]
            case 3:
                examples = [
                    f"{cls._prefix}_{uuid3(namespace=NAMESPACE_DNS, name="digon.io")}"
                    for _ in range(3)
                ]
            case 4:
                examples = [f"{cls._prefix}_{uuid4()}" for _ in range(3)]
            case 5:
                examples = [
                    f"{cls._prefix}_{uuid5(namespace=NAMESPACE_DNS, name="digon.io")}"
                    for _ in range(3)
                ]
            case 6:
                examples = [f"{cls._prefix}_{uuid6()}" for _ in range(3)]
            case 7:
                examples = [f"{cls._prefix}_{uuid7()}" for _ in range(3)]
            case 8:
                examples = [f"{cls._prefix}_{uuid8()}" for _ in range(3)]
            case _:
                raise PUUIDError()

        return {
            "type": "string",
            "title": cls.__name__,
            "description": f"Prefixed UUID with prefix '{cls._prefix}'",
            "examples": examples,
            "pattern": rf"^{cls._prefix}_[0-9a-fA-F-]{{36}}$",
        }


################################################################################
#### PUUIDv1
################################################################################


class PUUIDv1[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 1 (MAC address and time)."""

    VERSION: Final[int] = 1

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv1.

        Parameters
        ----------
        uuid : UUID
            An UUIDv1 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 1):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=1, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(
        cls,
        *,
        node: int | None = None,
        clock_seq: int | None = None,
    ) -> Self:
        """
        Create a new PUUIDv1 instance. using current time and MAC address.

        Parameters
        ----------
        node : int | None, optional
            MAC address.
        clock_seq : int | None, optional
            The current time.

        Returns
        -------
        Self
            A new PUUIDv1 instance.
        """

        return cls(uuid1(node, clock_seq), check_version=False)


################################################################################
#### PUUIDv3
################################################################################


class PUUIDv3[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 3 (MD5 hash of namespace and name)."""

    VERSION: Final[int] = 3

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv3.

        Parameters
        ----------
        uuid : UUID
            An UUIDv3 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 3):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=3, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(cls, *, namespace: UUID, name: str | bytes) -> Self:
        """
        Create a new PUUIDv3.

        Parameters
        ----------
        namespace : UUID | None, optional
            Namespace UUID.
        name : str | bytes | None, optional
            The name used for hashing.

        Returns
        -------
        Self
            A new PUUIDv3 instance.
        """

        return cls(uuid3(namespace, name), check_version=False)


################################################################################
#### PUUIDv4
################################################################################


class PUUIDv4[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 4 (randomly generated)."""

    VERSION: Final[int] = 4

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv4.

        Parameters
        ----------
        uuid : UUID
            An UUIDv4 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 4):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=4, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv4 instance using random generation.

        Returns
        -------
        Self
            A new PUUIDv4 instance.
        """

        return cls(uuid4(), check_version=False)


################################################################################
#### PUUIDv5
################################################################################


class PUUIDv5[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 5 (SHA-1 hash of namespace and name)."""

    VERSION: Final[int] = 5

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv5.

        Parameters
        ----------
        uuid : UUID
            Existing UUIDv5 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 5):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=5, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(
        cls,
        *,
        namespace: UUID,
        name: str | bytes,
    ) -> Self:
        """
        Create a new PUUIDv5 instance using random generation.

        Parameters
        ----------
        namespace : UUID
            Namespace UUID.
        name : str | bytes
            The name used for hashing.

        Returns
        -------
        Self
            A new PUUIDv5 instance.
        """

        return cls(uuid5(namespace=namespace, name=name), check_version=False)


################################################################################
#### PUUIDv6
################################################################################


class PUUIDv6[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 6 (reordered v1 for DB locality)."""

    VERSION: Final[int] = 6

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv6.

        Parameters
        ----------
        uuid : UUID
            An UUIDv6 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 6):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=6, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(
        cls,
        *,
        node: int | None = None,
        clock_seq: int | None = None,
    ) -> Self:
        """
        Create a new PUUIDv6 instance. using current time and MAC address.

        Parameters
        ----------
        node : int | None, optional
            MAC address.
        clock_seq : int | None, optional
            The current time.

        Returns
        -------
        Self
            A new PUUIDv6 instance.
        """

        return cls(uuid6(node, clock_seq), check_version=False)


################################################################################
#### PUUIDv7
################################################################################


class PUUIDv7[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 7 (time-ordered)."""

    VERSION: Final[int] = 7

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv7.

        Parameters
        ----------
        uuid : UUID
            An UUIDv7 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 7):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=7, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(cls) -> Self:
        """
        Create a new PUUIDv7 instance using random generation.

        Returns
        -------
        Self
            A new PUUIDv7 instance.
        """

        return cls(uuid7(), check_version=False)


################################################################################
#### PUUIDv8
################################################################################


class PUUIDv8[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 8 (custom implementation)."""

    VERSION: Final[int] = 8

    def __init__(
        self,
        uuid: UUID,
        *,
        check_version: bool = True,
    ) -> None:
        """
        Initialize a PUUIDv8.

        Parameters
        ----------
        uuid : UUID
            An UUIDv8 instance.

        Raises
        ------
        PUUIDError
            If the UUID version is incorrect.
        """

        if check_version and (uuid.version != 8):
            raise PUUIDError(
                ERR_MSG.UUID_VERSION_MISMATCH.format(expected=8, actual=uuid.version)
            )
        self._uuid = uuid

    @classmethod
    def factory(
        cls,
        *,
        a: int | None = None,
        b: int | None = None,
        c: int | None = None,
    ) -> Self:
        """
        Create a new PUUIDv8 instance using custom generation.

        Parameters
        ----------
        a : int | None, optional
            First custom 48-bit value.
        b : int | None, optional
            Second custom 12-bit value.
        c : int | None, optional
            Third custom 62-bit value.

        Returns
        -------
        Self
            A new PUUIDv8 instance.
        """

        return cls(uuid8(a, b, c), check_version=False)
