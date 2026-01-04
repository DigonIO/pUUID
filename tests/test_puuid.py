from typing import Literal
from uuid import UUID, uuid4

import pytest

from puuid import PUUID, PUUIDError


class UserUUID(PUUID[Literal["user"]]):
    _prefix = "user"


def test_create_random() -> None:
    user_id = UserUUID()
    assert isinstance(user_id, UserUUID)


def test_create_with_UUID() -> None:

    known_uuid = uuid4()
    user_id = UserUUID(value=known_uuid)
    assert isinstance(user_id, UserUUID)

    serial_user_id = f"user_{known_uuid}"
    assert user_id.to_string() == serial_user_id
    assert str(user_id) == serial_user_id


def test_create_from_str() -> None:
    serial_user_id = f"user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"

    user_id = UserUUID.from_string(serial_user_id)
    assert str(user_id) == serial_user_id


def test_create_from_str_with_error() -> None:
    serial_user_id = f"invoice_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"

    with pytest.raises(PUUIDError) as err:
        user_id = UserUUID.from_string(serial_user_id)

    err_msg = f"Expected prefix 'user' for '{serial_user_id}'!"
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

    user_id = UserUUID(value=uuid_instance)
    assert user_id.prefix() == "user"
    assert user_id.uuid == uuid_instance
    assert isinstance(hash(user_id), int)
