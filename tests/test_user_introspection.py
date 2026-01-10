import inspect
import pydoc
import uuid
from types import GenericAlias
from typing import Literal, TypeIs, cast, get_args, get_origin

from puuid import PUUIDv7

UserUUID = PUUIDv7[Literal["user"]]


def _is_generic_alias_tuple(value: object) -> TypeIs[tuple[GenericAlias, ...]]:
    if not isinstance(value, tuple):
        return False

    # pyright keeps tuple element types as Unknown when the tuple came from `object`.
    items = cast(tuple[object, ...], value)

    for item in items:
        if not isinstance(item, GenericAlias):
            return False

    return True


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
    user_uuid_cls = PUUIDv7[Literal["user"]]

    orig_bases_obj = getattr(user_uuid_cls, "__orig_bases__", None)
    assert _is_generic_alias_tuple(orig_bases_obj)

    assert len(orig_bases_obj) >= 1
    orig_base = orig_bases_obj[0]

    assert get_origin(orig_base).__name__ == "PUUIDv7"
    assert get_args(orig_base)[0] is Literal["user"]
