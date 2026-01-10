"""
pUUID Base Implementation.

Provides the abstract base class and version-specific implementations for Prefixed UUIDs.
"""

import annotationlib
from abc import ABC, abstractmethod
from types import GenericAlias
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Literal,
    ParamSpec,
    Self,
    TypeAliasType,
    TypeIs,
    TypeVar,
    TypeVarTuple,
    final,
    get_args,
    get_origin,
    overload,
    override,
)
from uuid import UUID, uuid1, uuid3, uuid4, uuid5, uuid6, uuid7, uuid8

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import core_schema

    _PYDANTIC_AVAILABLE = True
else:
    try:
        from pydantic import GetCoreSchemaHandler
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
    FACTORY_UNSUPPORTED = "'PUUID.factory' is only supported for 'PUUIDv1', 'PUUIDv4', 'PUUIDv6', 'PUUIDv7' and 'PUUIDv8'!"
    PREFIX_DESERIALIZATION_ERROR = "Unable to deserialize prefix '{prefix}', separator '_' or UUID for '{classname}' from '{serial_puuid}'!"
    INVALID_TYPE_FOR_SERIAL_PUUID = "'{classname}' can not be created from invalid type '{type}' with value '{value}'!"
    EMPTY_PREFIX_DISALLOWED = "Empty prefix is not allowed for '{classname}'!"
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
#### utilities
################################################################################

type _SubscriptionArgs = tuple[object, ...]
type _PUUIDClass = type[PUUIDBase[str]]
type _ClassGetItemReturn = GenericAlias | _PUUIDClass

type _SpecializationCacheKey = tuple[_PUUIDClass, str]
_SPECIALIZATION_CACHE: dict[_SpecializationCacheKey, _PUUIDClass] = {}


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


def _is_object_tuple(value: object) -> TypeIs[tuple[object, ...]]:
    """Narrow `object` to `tuple[object, ...]` for static type checkers."""
    return isinstance(value, tuple)


def _is_deferred_type_arg(item: object) -> bool:
    """
    Return True if `item` is a type-parameter-like argument (TypeVar/ParamSpec/
    TypeVarTuple) for which runtime specialization must not happen.
    """
    if isinstance(item, (TypeVar, ParamSpec, TypeVarTuple)):
        return True
    if _is_object_tuple(item):
        return any(_is_deferred_type_arg(part) for part in item)
    return False


def _unwrap_singleton_tuple(item: object) -> object:
    """
    Normalize subscription arguments: `C[T]` can arrive as `T` or `(T,)`.
    """
    if _is_object_tuple(item) and len(item) == 1:
        return item[0]
    return item


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


@overload
def _normalize_class_getitem_item(
    item: tuple[object, ...],
) -> tuple[_SubscriptionArgs, object]: ...
@overload
def _normalize_class_getitem_item(item: object) -> tuple[_SubscriptionArgs, object]: ...
def _normalize_class_getitem_item(item: object) -> tuple[_SubscriptionArgs, object]:
    args_tuple: _SubscriptionArgs = item if _is_object_tuple(item) else (item,)
    normalized = _unwrap_singleton_tuple(item)
    return args_tuple, normalized


def _is_puuid_class(value: type) -> TypeIs[_PUUIDClass]:
    return issubclass(value, PUUIDBase)


def _build_specialized_puuid_class(
    cls: _PUUIDClass,
    args_tuple: _SubscriptionArgs,
    prefix: str,
) -> _PUUIDClass:
    new_name = f"{cls.__name__}_{prefix}"
    new_cls_untyped = type(
        new_name,
        (cls,),
        {
            "_prefix": prefix,
            "__doc__": cls.__doc__,
            "__module__": cls.__module__,
            "__orig_bases__": (GenericAlias(cls, args_tuple),),
        },
    )

    if not _is_puuid_class(new_cls_untyped):
        raise TypeError(f"Expected a PUUIDBase subclass, got {new_cls_untyped!r}")
    return new_cls_untyped


def _get_or_create_specialization(
    cls: _PUUIDClass,
    args_tuple: _SubscriptionArgs,
    prefix: str,
) -> _PUUIDClass:
    key: _SpecializationCacheKey = (cls, prefix)

    cached = _SPECIALIZATION_CACHE.get(key)
    if cached is not None:
        return cached

    specialized = _build_specialized_puuid_class(cls, args_tuple, prefix)
    _SPECIALIZATION_CACHE[key] = specialized
    return specialized


def _puuid_class_getitem_runtime(cls: _PUUIDClass, item: object) -> _ClassGetItemReturn:
    """
    Runtime specialization hook for `PUUIDBase.__class_getitem__`.

    Returns:
      - GenericAlias for "normal" runtime generic behavior
      - Specialized subclass for `Literal["..."]` prefixes (cached)
    """
    args_tuple, normalized = _normalize_class_getitem_item(item)

    if _is_deferred_type_arg(normalized):
        return GenericAlias(cls, args_tuple)

    prefix = _try_extract_literal_string(normalized)
    if prefix is None:
        return GenericAlias(cls, args_tuple)

    if not prefix:
        raise PUUIDError(ERR_MSG.EMPTY_PREFIX_DISALLOWED.format(classname=cls.__name__))

    return _get_or_create_specialization(cls, args_tuple, prefix)


################################################################################
#### PUUIDBase
################################################################################


class PUUIDBase[TPrefix: str](ABC):
    """Abstract Generic Base Class for Prefixed UUIDs."""

    _prefix: ClassVar[str] = ""
    _serial: str | None
    _uuid: UUID

    @abstractmethod
    def __init__(self, *, uuid: UUID) -> None: ...

    # `__class_getitem__` is only implemented for runtime behavior (dynamic specialization
    # on `Literal["..."]`). Static type checkers already understand `PUUIDBase[T]`
    # subscription and would either ignore or be confused by a custom implementation here.
    # Guarding it behind `if not TYPE_CHECKING` keeps the static generic semantics intact
    # while still enabling the runtime specialization hook.
    if not TYPE_CHECKING:

        @classmethod
        def __class_getitem__(cls, item: object) -> object:
            return _puuid_class_getitem_runtime(cls, item)

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
        cached = self._serial
        if cached is not None:
            return cached

        serial = self._format_serial()
        self._serial = serial
        return serial

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


class PUUIDv1[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 1 (MAC address and time)."""

    _uuid: UUID
    _serial: str | None

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

        self._serial = None

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


class PUUIDv3[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 3 (MD5 hash of namespace and name)."""

    _uuid: UUID
    _serial: str | None

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

        self._serial = None


################################################################################
#### PUUIDv4
################################################################################


class PUUIDv4[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 4 (randomly generated)."""

    _uuid: UUID
    _serial: str | None

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
        self._serial = None

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


class PUUIDv5[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 5 (SHA-1 hash of namespace and name)."""

    _uuid: UUID
    _serial: str | None

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

        self._serial = None


################################################################################
#### PUUIDv6
################################################################################


class PUUIDv6[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 6 (reordered v1 for DB locality)."""

    _uuid: UUID
    _serial: str | None

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

        self._serial = None

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


class PUUIDv7[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 7 (time-ordered)."""

    _uuid: UUID
    _serial: str | None

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
        self._serial = None

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


class PUUIDv8[TPrefix: str](PUUIDBase[TPrefix]):
    """Prefixed UUID Version 8 (custom implementation)."""

    _uuid: UUID
    _serial: str | None

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

        self._serial = None

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
