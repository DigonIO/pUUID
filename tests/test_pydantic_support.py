from typing import Literal
from unittest.mock import patch

import pytest

pytest.importorskip("pydantic", reason="pydantic is an optional dependency")
pytest.importorskip("pydantic_core", reason="pydantic is an optional dependency")
from pydantic import BaseModel, ValidationError

from puuid import PUUIDError, PUUIDv4, PUUIDv7
from puuid.base import ERR_MSG

UserUUID = PUUIDv4[Literal["user"]]
DocUUID = PUUIDv7[Literal["doc"]]


class User(BaseModel):
    user_id: UserUUID


def test_pydantic_not_available_error() -> None:
    """Test that the property error is raised when pydantic is missing."""
    with patch("puuid.base._PYDANTIC_AVAILABLE", False):
        with pytest.raises(ModuleNotFoundError) as excinfo:
            UserUUID.__get_pydantic_core_schema__(UserUUID, None)  # type: ignore
        assert "pip install 'pUUID[pydantic]'" in str(excinfo.value)


def test_serialization() -> None:
    serial_id = "user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"
    serial_json = f'{{"user_id":"{serial_id}"}}'

    user_id = UserUUID.from_string(serial_id)
    user = User(user_id=user_id)

    assert user.model_dump_json() == serial_json


def test_deserialization() -> None:
    serial_id = "user_1a3e0e89-a2d8-4950-bafa-24020e09b2a5"
    serial_json = f'{{"user_id":"{serial_id}"}}'

    user = User.model_validate_json(serial_json)

    assert user.user_id.to_string() == serial_id


def test_model_schema_json() -> None:
    spec = User.model_json_schema()
    match spec:
        case {
            "properties": {
                "user_id": {
                    "description": "Prefixed UUID with prefix 'user'",
                    "examples": examples,
                    "pattern": "^user_[0-9a-fA-F-]{36}$",
                    "title": "PUUIDv4_user",
                    "type": "string",
                }
            },
            "required": ["user_id"],
            "title": "User",
            "type": "object",
        }:
            ...
        case _:
            assert False

    for example in examples:
        _user_id = UserUUID.from_string(example)

    OtherID = PUUIDv4[Literal["other"]]
    for example in examples:
        with pytest.raises(PUUIDError) as err_1:
            _other_id = OtherID.from_string(example)
        assert err_1.value.message == ERR_MSG.PREFIX_DESERIALIZATION_ERROR.format(
            prefix="other", classname="PUUIDv4_other", serial_puuid=example
        )

        with pytest.raises(PUUIDError) as err_2:
            _doc_id = DocUUID.from_string(example)
        assert err_2.value.message == ERR_MSG.PREFIX_DESERIALIZATION_ERROR.format(
            prefix="doc", classname="PUUIDv7_doc", serial_puuid=example
        )


@pytest.mark.parametrize(
    "serial_id",
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
def test_deserialization_from_invalid_str(serial_id: str) -> None:
    serial_json = f'{{"user_id":"{serial_id}"}}'

    with pytest.raises(ValidationError) as err:
        _ = User.model_validate_json(serial_json)

    err_msg = (
        "Value error, Unable to deserialize prefix 'user', separator '_' or UUID "
        f"for '{UserUUID.__name__}' from '{serial_id}'!"
    )
    assert err.value.errors()[0]["msg"] == err_msg


@pytest.mark.parametrize(
    "serial_id, serial_type",
    [
        ("123", "<class 'int'>"),
        ("2.5", "<class 'float'>"),
        ("[1, 2, 3]", "<class 'list'>"),
    ],
)
def test_deserialization_from_invalid_type(serial_id: str, serial_type: str) -> None:
    serial_json = f'{{"user_id":{serial_id}}}'

    with pytest.raises(ValidationError) as err:
        _ = User.model_validate_json(serial_json)

    err_msg = (
        "Value error, "
        f"'{UserUUID.__name__}' can not be created from invalid type "
        f"'{serial_type}' with value '{serial_id}'!"
    )
    assert err.value.errors()[0]["msg"] == err_msg
