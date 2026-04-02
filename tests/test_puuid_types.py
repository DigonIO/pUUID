# tests/test_puuid_types.py
from typing import Literal
from uuid import NAMESPACE_DNS, UUID

import pytest

from puuid import (
    PUUIDv1,
    PUUIDv3,
    PUUIDv4,
    PUUIDv5,
    PUUIDv6,
    PUUIDv7,
    PUUIDv8,
)
from puuid.base import PUUIDBase

################################################################################
#### isinstance and match/case using inheritance
################################################################################


class UserID(PUUIDv4[Literal["user"]]): ...


class Version1UUID(PUUIDv1[Literal["ver1b"]]): ...


class Version3UUID(PUUIDv3[Literal["ver3"]]): ...


class Version4UUID(PUUIDv4[Literal["ver4"]]): ...


class Version5UUID(PUUIDv5[Literal["ver5"]]): ...


class Version6UUID(PUUIDv6[Literal["ver6"]]): ...


class Version7UUID(PUUIDv7[Literal["ver7"]]): ...


class Version8UUID(PUUIDv8[Literal["ver8"]]): ...


def test_is_or_is_not_instance_with_inheritance() -> None:
    assert isinstance(UserID.factory(), PUUIDv4)
    assert isinstance(UserID.factory(), UserID)
    assert not isinstance(UserID.factory(), Version4UUID)
    assert not isinstance(UserID.factory, PUUIDv4)
    assert not isinstance(UserID.factory, UserID)

    assert isinstance(Version4UUID.factory(), PUUIDv4)
    assert isinstance(Version4UUID.factory(), Version4UUID)
    assert not isinstance(Version4UUID.factory(), UserID)
    assert not isinstance(Version4UUID, PUUIDv4)
    assert not isinstance(Version4UUID, Version4UUID)


@pytest.mark.parametrize(
    "resource_id, result_matrix",
    [
        (UserID.factory(), (True, False, False)),
        (Version4UUID.factory(), (False, True, False)),
        (Version7UUID.factory(), (False, False, True)),
    ],
)
def test_match_case_with_inheritance(
    resource_id: PUUIDBase[str], result_matrix: tuple[bool, bool, bool]
) -> None:
    match resource_id:
        case UserID():
            assert result_matrix[0]
        case Version4UUID():
            assert result_matrix[1]
        case Version7UUID():
            assert result_matrix[2]
        case _:
            assert False


################################################################################
#### PUUID v1 & v6
################################################################################


@pytest.mark.parametrize(
    "uuid_specialized, uuid_generic, node, clock_seq",
    [
        (Version1UUID, PUUIDv1, None, None),
        (Version6UUID, PUUIDv6, None, None),
    ],
)
def test_init_with_none_for_v1_and_v6(
    uuid_specialized: type[Version1UUID] | type[Version6UUID],
    uuid_generic: type[PUUIDv1[str]] | type[PUUIDv6[str]],
    node: int | None,
    clock_seq: int | None,
) -> None:

    instance_default = uuid_specialized.factory()
    assert isinstance(instance_default, uuid_generic)

    instance = uuid_specialized.factory(node=node, clock_seq=clock_seq)
    assert isinstance(instance, uuid_generic)


################################################################################
#### PUUID v3 & v5
################################################################################


@pytest.mark.parametrize(
    "uuid_specialized, uuid_generic, namespace, name",
    [
        (Version3UUID, PUUIDv3, NAMESPACE_DNS, "digon.io"),
        (Version5UUID, PUUIDv5, NAMESPACE_DNS, "digon.io"),
    ],
)
def test_init_namespace_name_for_v3_v5(
    uuid_specialized: type[Version3UUID] | type[Version5UUID],
    uuid_generic: type[PUUIDv3[str]] | type[PUUIDv5[str]],
    namespace: UUID,
    name: str,
) -> None:
    instance = uuid_specialized.factory(namespace=namespace, name=name)
    assert isinstance(instance, uuid_generic)
