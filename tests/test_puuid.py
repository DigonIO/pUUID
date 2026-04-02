import typing
from typing import Literal, TypeVar
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid4, uuid5, uuid6, uuid7, uuid8

import pytest

from puuid import (
    PUUIDError,
    PUUIDv1,
    PUUIDv3,
    PUUIDv4,
    PUUIDv5,
    PUUIDv6,
    PUUIDv7,
    PUUIDv8,
)
from puuid.base import ERR_MSG, PUUIDBase


class UserUUID(PUUIDv4[Literal["user"]]): ...


class Version1UUID(PUUIDv1[Literal["ver1"]]): ...


class Version3UUID(PUUIDv3[Literal["ver3"]]): ...


class Version4UUID(PUUIDv4[Literal["ver4"]]): ...


class Version5UUID(PUUIDv5[Literal["ver5"]]): ...


class Version6UUID(PUUIDv6[Literal["ver6"]]): ...


class Version7UUID(PUUIDv7[Literal["ver7"]]): ...


class Version8UUID(PUUIDv8[Literal["ver8"]]): ...


def test_class_getitem_typevar_returns_generic_alias() -> None:
    T = TypeVar("T", bound=str)
    res = PUUIDv4[T]  # pyright: ignore[reportGeneralTypeIssues]
    assert isinstance(res, typing._GenericAlias)  # type: ignore


def test_class_getitem_non_literal_returns_generic_alias() -> None:
    res = PUUIDv4[str]
    assert isinstance(res, typing._GenericAlias)  # type: ignore


def test_class_getitem_literal_non_string_returns_generic_alias() -> None:
    res = PUUIDv4.__class_getitem__(Literal[1])  # type: ignore
    assert isinstance(res, typing._GenericAlias)  # type: ignore


@pytest.mark.parametrize(
    "uuid_cls, uuid, prefix",
    [
        (UserUUID, uuid4(), "user"),
        (Version1UUID, uuid1(), "ver1"),
        (Version3UUID, uuid3(NAMESPACE_DNS, "digon.io"), "ver3"),
        (Version4UUID, uuid4(), "ver4"),
        (Version5UUID, uuid5(NAMESPACE_DNS, "digon.io"), "ver5"),
        (Version6UUID, uuid6(), "ver6"),
        (Version7UUID, uuid7(), "ver7"),
        (Version8UUID, uuid8(), "ver8"),
    ],
)
def test_init_with_uuid_for_all_versions(
    uuid_cls: type[
        UserUUID
        | Version1UUID
        | Version3UUID
        | Version4UUID
        | Version5UUID
        | Version6UUID
        | Version7UUID
        | Version8UUID
    ],
    uuid: UUID,
    prefix: str,
) -> None:
    assert uuid_cls.prefix() == prefix
    instance = uuid_cls(uuid=uuid)
    assert instance.prefix() == prefix


@pytest.mark.parametrize(
    "uuid_specialized, uuid_generic",
    [
        (Version1UUID, PUUIDv1),
        (Version4UUID, PUUIDv4),
        (Version6UUID, PUUIDv6),
        (Version7UUID, PUUIDv7),
        (Version8UUID, PUUIDv8),
    ],
)
def test_factory_for_v1_v4_v6_v7_v8(
    uuid_specialized: type[
        Version1UUID | Version4UUID | Version6UUID | Version7UUID | Version8UUID
    ],
    uuid_generic: type[PUUIDBase[str]],
) -> None:
    instance = uuid_specialized.factory()
    assert isinstance(instance, uuid_generic)


type UserPrefix = Literal["user"]


@pytest.mark.parametrize(
    "uuid_cls, uuid, err_msg",
    [
        (
            Version1UUID,
            uuid4(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=1, actual=4),
        ),
        (
            Version3UUID,
            uuid4(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=3, actual=4),
        ),
        (
            Version4UUID,
            uuid6(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=4, actual=6),
        ),
        (
            Version5UUID,
            uuid6(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=5, actual=6),
        ),
        (
            Version6UUID,
            uuid7(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=6, actual=7),
        ),
        (
            Version7UUID,
            uuid8(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=7, actual=8),
        ),
        (
            Version8UUID,
            uuid1(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=8, actual=1),
        ),
    ],
)
def test_init_failure_with_uuid_for_all_versions(
    uuid_cls: type[
        Version1UUID
        | Version3UUID
        | Version4UUID
        | Version5UUID
        | Version6UUID
        | Version7UUID
        | Version8UUID
    ],
    uuid: UUID,
    err_msg: str,
) -> None:
    with pytest.raises(PUUIDError) as err:
        uuid_cls(uuid=uuid)
    assert err.value.message == err_msg


################################################################################
#### PUUID v1 & v6
################################################################################


@pytest.mark.parametrize(
    "uuid_cls, node, clock_seq",
    [
        (Version1UUID, 123, 123),
        (Version6UUID, 123, 123),
    ],
)
def test_init_with_node_clock_for_v1_and_v6(
    uuid_cls: type[Version1UUID | Version6UUID],
    node: int | None,
    clock_seq: int | None,
) -> None:
    assert uuid_cls.factory(node=node, clock_seq=clock_seq)


################################################################################
#### PUUID other
################################################################################


def test_create_with_UUID() -> None:
    known_uuid = uuid4()
    user_id = UserUUID(uuid=known_uuid)
    assert isinstance(user_id, PUUIDv4)

    serial_user_id = f"user_{known_uuid}"
    assert user_id.to_string() == serial_user_id
    assert str(user_id) == serial_user_id


def test_create_from_str() -> None:
    serial_user_id = "user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"

    user_id = UserUUID.from_string(serial_user_id)
    assert str(user_id) == serial_user_id


@pytest.mark.parametrize(
    "serial_user_id",
    [
        "invoice_1a3e0e89-a2d8-4950-bafa-24020e09b2a6",
        "_1a3e0e89-a2d8-4950-bafa-24020e09b2a5",
        "1a3e0e89-a2d8-4950-bafa-24020e09b2a5",
        "user_   ",
        "invoice_",
        "user",
        "_",
        "user1a3e0e89-a2d8-4950-bafa-24020e09b2a5",
    ],
)
def test_create_from_invalid_str(serial_user_id: str) -> None:
    with pytest.raises(PUUIDError) as err:
        _ = UserUUID.from_string(serial_user_id)

    err_msg = (
        "Unable to deserialize prefix 'user', separator '_' or UUID for "
        f"'{UserUUID.__name__}' from '{serial_user_id}'!"
    )
    assert err.value.message == err_msg


def test_factory() -> None:
    user_id = UserUUID.factory()
    assert type(user_id) is UserUUID


def test_equal() -> None:
    serial_user_1 = "user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"
    serial_user_2 = "user_1a3e0e89-a2d8-4950-bafa-24020e09b2a6"

    assert UserUUID.from_string(serial_user_1) == UserUUID.from_string(serial_user_1)
    assert UserUUID.from_string(serial_user_1) != UserUUID.from_string(serial_user_2)

    assert UserUUID.factory() != "Digon.IO GmbH"


def test_util_functions() -> None:
    uuid_instance = uuid4()

    user_id = UserUUID(uuid=uuid_instance)
    assert user_id.prefix() == "user"
    assert user_id.uuid == uuid_instance
    assert isinstance(hash(user_id), int)


type EmptyPrefix = Literal[""]


@pytest.mark.xfail(reason="Desired behavior, but unclear how to achieve")
def test_disallow_empty_prefix_base() -> None:
    with pytest.raises(PUUIDError) as excinfo:
        _a = PUUIDv4[Literal[""]]
    assert (
        f"Empty prefix is not allowed for '{PUUIDv4.__name__}'!"
        == excinfo.value.message
    )

    with pytest.raises(PUUIDError) as excinfo:
        _b = PUUIDv7[EmptyPrefix]
    assert (
        f"Empty prefix is not allowed for '{PUUIDv7.__name__}'!"
        == excinfo.value.message
    )


def test_disallow_empty_prefix() -> None:
    with pytest.raises(PUUIDError) as excinfo:

        class Fake1(PUUIDv4[Literal[""]]): ...  # pyright: ignore[reportUnusedClass]

    assert "Empty prefix is not allowed for 'Fake1'!" == excinfo.value.message


def test_disallow_str_type_instanciate() -> None:

    a = PUUIDBase[str]
    with pytest.raises(TypeError) as excinfo_1:
        a()  # type: ignore

    assert excinfo_1.value.args == (
        "Can't instantiate abstract class PUUIDBase without an implementation for abstract method '__init__'",
    )

    b = PUUIDv4[str]
    with pytest.raises(PUUIDError) as excinfo_2:
        b.factory()
    assert excinfo_2.value.message == ERR_MSG.EMPTY_PREFIX_DISALLOWED.format(
        classname="PUUIDv4"
    )
    with pytest.raises(PUUIDError) as excinfo_3:
        PUUIDv4[str].factory()
    assert excinfo_3.value.message == ERR_MSG.EMPTY_PREFIX_DISALLOWED.format(
        classname="PUUIDv4"
    )


def test_to_string_is_cached() -> None:
    user_id = UserUUID.factory()
    s1 = user_id.to_string()
    s2 = user_id.to_string()
    assert s1 is s2  # second call returns the cached string object
