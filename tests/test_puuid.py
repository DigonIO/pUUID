from typing import Literal
from uuid import UUID, uuid4

import pytest

from puuid import PUUIDError, PUUIDv1, PUUIDv4, PUUIDv5


class ItemUUID(PUUIDv1[Literal["item"]]):
    _prefix = "item"


ItemUUID()


class UserUUID(PUUIDv4[Literal["user"]]):
    _prefix = "user"


def test_create_random() -> None:
    user_id = UserUUID()
    assert isinstance(user_id, UserUUID)


def test_create_with_UUID() -> None:

    known_uuid = uuid4()
    user_id = UserUUID(uuid=known_uuid)
    assert isinstance(user_id, UserUUID)

    serial_user_id = f"user_{known_uuid}"
    assert user_id.to_string() == serial_user_id
    assert str(user_id) == serial_user_id


def test_create_from_str() -> None:
    serial_user_id = f"user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"

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
        user_id = UserUUID.from_string(serial_user_id)

    err_msg = f"Unable to deserialize prefix 'user', separator '_' or UUID for 'UserUUID' from '{serial_user_id}'!"
    assert err.value.message == err_msg


def test_factory() -> None:
    user_id = UserUUID.factory()
    assert isinstance(user_id, UserUUID)


def test_equal() -> None:
    serial_user_1 = f"user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"
    serial_user_2 = f"user_1a3e0e89-a2d8-4950-bafa-24020e09b2a6"

    assert UserUUID.from_string(serial_user_1) == UserUUID.from_string(serial_user_1)
    assert UserUUID.from_string(serial_user_1) != UserUUID.from_string(serial_user_2)

    assert UserUUID() != "Digon.IO GmbH"


def test_util_functions() -> None:
    uuid_instance = uuid4()

    user_id = UserUUID(uuid=uuid_instance)
    assert user_id.prefix() == "user"
    assert user_id.uuid == uuid_instance
    assert isinstance(hash(user_id), int)
