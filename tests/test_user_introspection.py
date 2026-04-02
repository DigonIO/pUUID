import inspect
import pydoc
import uuid
from typing import Literal, get_args, get_origin

from puuid import PUUIDv7


class UserUUID(PUUIDv7[Literal["user"]]): ...


def test_dynamic_class_introspection_name_module() -> None:
    assert UserUUID.__name__ == "UserUUID"
    assert UserUUID.__module__ == "tests.test_user_introspection"


def test_dynamic_class_introspection_signature() -> None:
    sig = inspect.signature(UserUUID)
    assert "uuid" in sig.parameters
    assert sig.parameters["uuid"].annotation == uuid.UUID


def test_dynamic_class_introspection_doc() -> None:
    doc_output = pydoc.render_doc(UserUUID)

    assert "UserUUID" in doc_output
    assert (
        "Initialize a PUUIDv7." in doc_output
    )  # Should inherit __init__ docstring from PUUIDv7


def test_subclass_introspection() -> None:
    # Test inheritance from a specialized type
    class CustomUser(PUUIDv7[Literal["user"]]):
        """A custom subclass."""

        pass

    # Check that the MRO (Method Resolution Order) is logical
    mro = inspect.getmro(CustomUser)

    # Expect: CustomUser -> PUUIDv7 (base) -> ...
    assert mro[0] == CustomUser
    assert mro[1].__name__ == "PUUIDv7"

    # Ensure the signature remains valid for the subclass
    sig = inspect.signature(CustomUser)
    assert "uuid" in sig.parameters


def test_origin_bases_integrity() -> None:
    # Verify that we haven't lost the generic origin information
    user_uuid_cls = PUUIDv7[Literal["user"]]

    origin = get_origin(user_uuid_cls)
    assert origin is not None
    assert origin.__name__ == "PUUIDv7"

    assert get_args(user_uuid_cls)[0] is Literal["user"]
