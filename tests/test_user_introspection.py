import inspect
import pydoc
from typing import Literal, get_origin, get_args
from puuid import PUUIDv7
import uuid

UserUUID = PUUIDv7[Literal["user"]]


def test_dynamic_class_introspection_name_module() -> None:
    assert UserUUID.__name__ == "PUUIDv7_user"
    assert UserUUID.__module__ == "puuid.base"


def test_dynamic_class_introspection_signature() -> None:
    sig = inspect.signature(UserUUID)
    assert "uuid" in sig.parameters
    assert sig.parameters["uuid"].annotation == uuid.UUID | None


def test_dynamic_class_introspection_doc() -> None:
    doc_output = pydoc.render_doc(UserUUID)

    assert "PUUIDv7_user" in doc_output

    assert (
        "Prefixed UUID Version 7" in doc_output
    )  # Should inherit docstring from PUUIDv7


def test_subclass_introspection() -> None:
    # Test inheritance from a specialized type
    class CustomUser(PUUIDv7[Literal["user"]]):
        """A custom subclass."""

        pass

    # Check that the MRO (Method Resolution Order) is logical
    mro = inspect.getmro(CustomUser)

    # Expect: CustomUser -> PUUIDv7_user (dynamic) -> PUUIDv7 (base) -> ...
    assert mro[0] == CustomUser
    assert mro[1].__name__ == "PUUIDv7_user"
    assert "PUUIDv7" in [c.__name__ for c in mro]

    # Ensure the signature remains valid for the subclass
    sig = inspect.signature(CustomUser)
    assert "uuid" in sig.parameters


def test_origin_bases_integrity() -> None:
    # Verify that we haven't lost the generic origin information
    # required by some type-checking libraries at runtime
    UserUUID = PUUIDv7[Literal["user"]]

    assert hasattr(UserUUID, "__orig_bases__")
    # The first base should represent the GenericAlias PUUIDv7[Literal["user"]]
    orig_base = UserUUID.__orig_bases__[0]

    assert get_origin(orig_base).__name__ == "PUUIDv7"
    assert get_args(orig_base)[0] is Literal["user"]
