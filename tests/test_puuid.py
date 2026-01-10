import random
from typing import Literal
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid4, uuid5, uuid6, uuid7, uuid8

import pytest

from puuid import (
    PUUIDBase,
    PUUIDError,
    PUUIDv1,
    PUUIDv3,
    PUUIDv4,
    PUUIDv5,
    PUUIDv6,
    PUUIDv7,
    PUUIDv8,
)
from puuid.base import ERR_MSG

UserUUID = PUUIDv4[Literal["user"]]
Version1UUID = PUUIDv1[Literal["ver1"]]
Version3UUID = PUUIDv3[Literal["ver3"]]
Version4UUID = PUUIDv4[Literal["ver4"]]
Version5UUID = PUUIDv5[Literal["ver5"]]
Version6UUID = PUUIDv6[Literal["ver6"]]
Version7UUID = PUUIDv7[Literal["ver7"]]
Version8UUID = PUUIDv8[Literal["ver8"]]


# For Backwards compatibility checks
class Version1UUIDBack(PUUIDv1[Literal["ver1b"]]): ...


class Version3UUIDBack(PUUIDv3[Literal["ver3b"]]):
    _prefix = "ver3b"  # <- type no longer in sync with `Literal["ver3b"]` as in v1.0.0


@pytest.mark.parametrize(
    "uuid_cls, uuid, prefix",
    [
        (UserUUID, uuid4(), "user"),
        (Version1UUID, uuid1(), "ver1"),
        (Version1UUIDBack, uuid1(), "ver1b"),
        (Version3UUID, uuid3(NAMESPACE_DNS, "digon.io"), "ver3"),
        (Version3UUIDBack, uuid3(NAMESPACE_DNS, "digon.io"), "ver3b"),
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
        | Version1UUIDBack
        | Version3UUID
        | Version3UUIDBack
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
    "uuid_realized, uuid_generic",
    [
        (Version1UUID, PUUIDv1),
        (Version1UUIDBack, PUUIDv1),
        (Version4UUID, PUUIDv4),
        (Version6UUID, PUUIDv6),
        (Version7UUID, PUUIDv7),
        (Version8UUID, PUUIDv8),
    ],
)
def test_factory_for_v1_v4_v6_v7_v8(
    uuid_realized: type[PUUIDBase[Literal["vers"]]], uuid_generic: type[PUUIDBase[str]]
) -> None:
    instance = uuid_realized.factory()
    assert isinstance(instance, uuid_generic)


type UserPrefix = Literal["user"]


def test_type_identity_caching() -> None:
    a = list["str"]
    b = list["str"]
    assert a is not b
    # the above passes for default generics, but due to caching our implementation might come as a surprise to some
    user_a = PUUIDv4[UserPrefix]
    user_b = PUUIDv4[Literal["user"]]
    user_c = PUUIDv4[Literal["user"]]
    assert user_a is user_b
    assert user_b is user_c


@pytest.mark.parametrize(
    "uuid_cls, uuid, err_msg",
    [
        (
            Version1UUID,
            uuid4(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=1, actual=4),
        ),
        (
            Version1UUIDBack,
            uuid4(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=1, actual=4),
        ),
        (
            Version3UUID,
            uuid4(),
            ERR_MSG.UUID_VERSION_MISMATCH.format(expected=3, actual=4),
        ),
        (
            Version3UUIDBack,
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
        | Version1UUIDBack
        | Version3UUID
        | Version3UUIDBack
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
    "uuid_cls, node, clock_seq, uuid",
    [
        (Version1UUID, None, None, None),
        (Version1UUIDBack, None, None, None),
        (Version6UUID, None, None, None),
    ],
)
def test_init_with_none_for_v1_and_v6(
    uuid_cls: type[Version1UUID | Version1UUIDBack | Version6UUID],
    node: int | None,
    clock_seq: int | None,
    uuid: UUID | None,
) -> None:

    assert uuid_cls()
    assert uuid_cls(node=node, clock_seq=clock_seq)


@pytest.mark.parametrize(
    "uuid_cls, node, clock_seq",
    [
        (Version1UUID, 123, 123),
        (Version1UUIDBack, 123, 123),
        (Version6UUID, 123, 123),
    ],
)
def test_init_with_node_clock_for_v1_and_v6(
    uuid_cls: type[Version1UUID | Version6UUID],
    node: int | None,
    clock_seq: int | None,
) -> None:
    assert uuid_cls(node=node, clock_seq=clock_seq)


@pytest.mark.parametrize(
    "uuid_cls, node, clock_seq, uuid, err_msg",
    [
        (Version1UUID, 123, 123, uuid1(), ERR_MSG.INVALID_PUUIDv1_ARGS),
        (Version1UUID, None, 123, uuid1(), ERR_MSG.INVALID_PUUIDv1_ARGS),
        (Version1UUID, 123, None, uuid1(), ERR_MSG.INVALID_PUUIDv1_ARGS),
        (Version1UUIDBack, 123, 123, uuid1(), ERR_MSG.INVALID_PUUIDv1_ARGS),
        (Version1UUIDBack, None, 123, uuid1(), ERR_MSG.INVALID_PUUIDv1_ARGS),
        (Version1UUIDBack, 123, None, uuid1(), ERR_MSG.INVALID_PUUIDv1_ARGS),
        (Version6UUID, 123, 123, uuid6(), ERR_MSG.INVALID_PUUIDv6_ARGS),
        (Version6UUID, None, 123, uuid6(), ERR_MSG.INVALID_PUUIDv6_ARGS),
        (Version6UUID, 123, None, uuid6(), ERR_MSG.INVALID_PUUIDv6_ARGS),
    ],
)
def test_init_with_invalid_args_for_v1_and_v6(
    uuid_cls: type[Version1UUID | Version1UUIDBack | Version6UUID],
    node: int | None,
    clock_seq: int | None,
    uuid: UUID,
    err_msg: str,
) -> None:
    with pytest.raises(PUUIDError) as err:
        uuid_cls(node=node, clock_seq=clock_seq, uuid=uuid)  # type: ignore
    assert err.value.message == err_msg


################################################################################
#### PUUID v3 & v5
################################################################################


@pytest.mark.parametrize(
    "uuid_realized, uuid_generic, namespace, name",
    [
        (Version3UUID, PUUIDv3, NAMESPACE_DNS, "digon.io"),
        (Version3UUIDBack, PUUIDv3, NAMESPACE_DNS, "digon.io"),
        (Version5UUID, PUUIDv5, NAMESPACE_DNS, "digon.io"),
    ],
)
def test_init_namespace_name_for_v3_v5(
    uuid_realized: type[Version3UUID] | type[Version3UUIDBack] | type[Version5UUID],
    uuid_generic: type[PUUIDv3[str]] | type[PUUIDv5[str]],
    namespace: UUID,
    name: str,
) -> None:
    instance = uuid_realized(namespace=namespace, name=name)
    assert isinstance(instance, uuid_generic)
    assert isinstance(uuid_realized(namespace=namespace, name=name), uuid_generic)


@pytest.mark.parametrize(
    "uuid_cls, namespace, name, uuid, err_msg",
    [
        (
            Version3UUID,
            NAMESPACE_DNS,
            "digon.io",
            uuid3(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv3_ARGS,
        ),
        (
            Version3UUID,
            None,
            "digon.io",
            uuid3(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv3_ARGS,
        ),
        (
            Version3UUID,
            NAMESPACE_DNS,
            None,
            uuid3(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv3_ARGS,
        ),
        (
            Version3UUIDBack,
            NAMESPACE_DNS,
            "digon.io",
            uuid3(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv3_ARGS,
        ),
        (
            Version3UUIDBack,
            None,
            "digon.io",
            uuid3(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv3_ARGS,
        ),
        (
            Version3UUIDBack,
            NAMESPACE_DNS,
            None,
            uuid3(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv3_ARGS,
        ),
        (
            Version5UUID,
            NAMESPACE_DNS,
            "digon.io",
            uuid5(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv5_ARGS,
        ),
        (
            Version5UUID,
            None,
            "digon.io",
            uuid5(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv5_ARGS,
        ),
        (
            Version5UUID,
            NAMESPACE_DNS,
            None,
            uuid5(NAMESPACE_DNS, "digon.io"),
            ERR_MSG.INVALID_PUUIDv5_ARGS,
        ),
    ],
)
def test_init_invalid_args_for_v3_v5(
    uuid_cls: type[Version3UUID] | type[Version3UUIDBack] | type[Version5UUID],
    namespace: UUID,
    name: str,
    uuid: UUID,
    err_msg: str,
) -> None:
    with pytest.raises(PUUIDError) as err:
        uuid_cls(namespace=namespace, name=name, uuid=uuid)  # type: ignore
    assert err.value.message == err_msg


@pytest.mark.parametrize(
    "uuid_cls",
    [
        Version3UUID,
        Version3UUIDBack,
        Version5UUID,
    ],
)
def test_unsupported_factory(
    uuid_cls: type[Version3UUID | Version3UUIDBack | Version5UUID],
) -> None:
    with pytest.raises(PUUIDError) as err:
        uuid_cls.factory()
    assert err.value.message == ERR_MSG.FACTORY_UNSUPPORTED


################################################################################
#### PUUID v8
################################################################################

a = random.getrandbits(48)
b = random.getrandbits(12)
c = random.getrandbits(62)


@pytest.mark.parametrize(
    "uuid_cls, a, b, c, uuid, err_msg",
    [
        (
            Version8UUID,
            a,
            b,
            c,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
        (
            Version8UUID,
            None,
            b,
            c,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
        (
            Version8UUID,
            a,
            None,
            c,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
        (
            Version8UUID,
            a,
            b,
            None,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
        (
            Version8UUID,
            a,
            None,
            None,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
        (
            Version8UUID,
            None,
            b,
            None,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
        (
            Version8UUID,
            None,
            None,
            c,
            uuid8(),
            ERR_MSG.INVALID_PUUIDv8_ARGS,
        ),
    ],
)
def test_init_invalid_args_for_v8(
    uuid_cls: type[Version3UUID] | type[Version3UUIDBack] | type[Version5UUID],
    a: int,
    b: int,
    c: int,
    uuid: UUID,
    err_msg: str,
) -> None:
    with pytest.raises(PUUIDError) as err:
        uuid_cls(a=a, b=b, c=c, uuid=uuid)  # type: ignore
    assert err.value.message == err_msg


################################################################################
#### PUUID other
################################################################################


def test_create_random() -> None:
    user_id = UserUUID()
    assert isinstance(user_id, PUUIDv4)


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

    assert UserUUID() != "Digon.IO GmbH"


def test_util_functions() -> None:
    uuid_instance = uuid4()

    user_id = UserUUID(uuid=uuid_instance)
    assert user_id.prefix() == "user"
    assert user_id.uuid == uuid_instance
    assert isinstance(hash(user_id), int)


type EmptyPrefix = Literal[""]


def test_disallow_empty_prefix() -> None:
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
