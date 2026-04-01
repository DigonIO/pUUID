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

from .util import UserID_class as UserID_class_imported

UserID = PUUIDv4[Literal["user"]]


Version1UUID = PUUIDv1[Literal["ver1"]]
Version3UUID = PUUIDv3[Literal["ver3"]]
Version4UUID = PUUIDv4[Literal["ver4"]]
Version5UUID = PUUIDv5[Literal["ver5"]]
Version6UUID = PUUIDv6[Literal["ver6"]]
Version7UUID = PUUIDv7[Literal["ver7"]]
Version8UUID = PUUIDv8[Literal["ver8"]]

################################################################################
#### isinstance and match/case with parametrized generics
################################################################################


def test_is_or_is_not_instance_of_parametrized_generic() -> None:
    # The code below should not fail and the type checker should not report errors at all here:
    assert isinstance(UserID(), PUUIDv4)
    assert isinstance(UserID(), UserID)
    assert not isinstance(UserID(), Version4UUID)
    assert not isinstance(UserID, PUUIDv4)
    assert not isinstance(UserID, UserID)

    assert isinstance(Version4UUID(), PUUIDv4)
    assert isinstance(Version4UUID(), Version4UUID)
    assert not isinstance(Version4UUID(), UserID)
    assert not isinstance(Version4UUID, PUUIDv4)
    assert not isinstance(Version4UUID, Version4UUID)


@pytest.mark.parametrize(
    "resource_id, result_matrix",
    [
        (UserID(), (True, False, False)),
        (Version4UUID(), (False, True, False)),
        (Version7UUID(), (False, False, True)),
    ],
)
def test_match_case_of_parametrized_generic(
    resource_id: PUUIDBase[str], result_matrix: tuple[bool, bool, bool]
) -> None:
    # The code below should not fail and the type checker should not report errors at all here:
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
#### isinstance and match/case using inheritance
################################################################################


class UserID_class(PUUIDv4[Literal["user"]]): ...


class Version1UUID_class(PUUIDv1[Literal["ver1b"]]): ...


class Version3UUID_class(PUUIDv3[Literal["ver3"]]): ...


class Version4UUID_class(PUUIDv4[Literal["ver4"]]): ...


class Version5UUID_class(PUUIDv5[Literal["ver5"]]): ...


class Version6UUID_class(PUUIDv6[Literal["ver6"]]): ...


class Version7UUID_class(PUUIDv7[Literal["ver7"]]): ...


class Version8UUID_class(PUUIDv8[Literal["ver8"]]): ...


def test_is_or_is_not_instance_with_inheritance() -> None:
    # The code below should not fail and the type checker should not report errors at all here:
    assert isinstance(UserID_class(), PUUIDv4)
    assert isinstance(UserID_class(), UserID_class)
    assert not isinstance(UserID_class(), Version4UUID_class)
    assert not isinstance(UserID_class, PUUIDv4)
    assert not isinstance(UserID_class, UserID_class)

    assert isinstance(Version4UUID_class(), PUUIDv4)
    assert isinstance(Version4UUID_class(), Version4UUID_class)
    assert not isinstance(Version4UUID_class(), UserID_class)
    assert not isinstance(Version4UUID_class, PUUIDv4)
    assert not isinstance(Version4UUID_class, Version4UUID_class)


@pytest.mark.parametrize(
    "resource_id, result_matrix",
    [
        (UserID_class(), (True, False, False)),
        (Version4UUID_class(), (False, True, False)),
        (Version7UUID_class(), (False, False, True)),
    ],
)
def test_match_case_with_inheritance(
    resource_id: PUUIDBase[str], result_matrix: tuple[bool, bool, bool]
) -> None:
    # The code below should not fail and the type checker should not report errors at all here:
    match resource_id:
        case UserID_class():
            assert result_matrix[0]
        case Version4UUID_class():
            assert result_matrix[1]
        case Version7UUID_class():
            assert result_matrix[2]
        case _:
            assert False


################################################################################
#### isinstance and using equivalent definition from somewhere else
################################################################################
# NOTE: the fact that its likely impossible to achieve the test below to pass,
# speaks against going back to subclassing from a PUUIDvX


@pytest.mark.xfail(reason="would be nice to achieve somehow, but is likely impossible")
def test_is_or_is_not_instance_with_imported() -> None:
    assert isinstance(UserID_class(), UserID_class_imported)
    assert isinstance(UserID_class_imported(), UserID_class)


################################################################################
#### isinstance using mixed types
################################################################################
# NOTE: the fact that its likely impossible to achieve consistent API behaviour when
# mixing the class based and parametrized generics syntax, should make us reconsider
# going back to the initial (slightly longer) API design, where one has to actually
# subclass from a PUUIDvX.


def test_is_or_is_not_instance_with_mixed() -> None:
    # The code below should not fail and the type checker should not report errors at all here:
    assert not isinstance(PUUIDv4[Literal["user"]](), Version4UUID_class)
    assert not isinstance(PUUIDv4[Literal["user"]], UserID_class)

    assert isinstance(UserID_class(), PUUIDv4[Literal["user"]])
    assert not isinstance(UserID_class(), PUUIDv4[Literal["ver4"]])
    assert not isinstance(UserID_class, PUUIDv4[Literal["user"]])


@pytest.mark.xfail(reason="would be nice to achieve somehow, but is likely impossible")
def test_is_or_is_not_instance_with_mixed_impossible() -> None:
    assert isinstance(PUUIDv4[Literal["user"]](), UserID_class)


################################################################################
#### PUUID v1 & v6
################################################################################


@pytest.mark.parametrize(
    "uuid_specialized, uuid_generic, node, clock_seq",
    [
        (Version1UUID, PUUIDv1, None, None),
        (Version1UUID_class, PUUIDv1, None, None),
        (Version6UUID, PUUIDv6, None, None),
    ],
)
def test_init_with_none_for_v1_and_v6(
    uuid_specialized: (
        type[Version1UUID] | type[Version1UUID_class] | type[Version6UUID]
    ),
    uuid_generic: type[PUUIDv1[str]] | type[PUUIDv6[str]],
    node: int | None,
    clock_seq: int | None,
) -> None:

    instance_default = uuid_specialized()
    assert isinstance(instance_default, uuid_generic)

    instance = uuid_specialized(node=node, clock_seq=clock_seq)
    assert isinstance(instance, uuid_generic)


################################################################################
#### PUUID v3 & v5
################################################################################


@pytest.mark.parametrize(
    "uuid_specialized, uuid_generic, namespace, name",
    [
        (Version3UUID, PUUIDv3, NAMESPACE_DNS, "digon.io"),
        (Version3UUID_class, PUUIDv3, NAMESPACE_DNS, "digon.io"),
        (Version5UUID, PUUIDv5, NAMESPACE_DNS, "digon.io"),
    ],
)
def test_init_namespace_name_for_v3_v5(
    uuid_specialized: (
        type[Version3UUID] | type[Version3UUID_class] | type[Version5UUID]
    ),
    uuid_generic: type[PUUIDv3[str]] | type[PUUIDv5[str]],
    namespace: UUID,
    name: str,
) -> None:
    instance = uuid_specialized(namespace=namespace, name=name)
    assert isinstance(instance, uuid_generic)
