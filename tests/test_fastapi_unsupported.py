from typing import Literal

import pytest

pytest.importorskip("fastapi", reason="FastAPI is an optional dependency")
pytest.importorskip("httpx", reason="httpx is required for FastAPI TestClient")
pytest.importorskip("pydantic", reason="Pydantic is an optional dependency")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from puuid import PUUIDv4, PUUIDv7
from puuid.base import PUUIDBase, PUUIDError

UserUUID = PUUIDv4[Literal["user"]]
DocUUID = PUUIDv7[Literal["doc"]]


def create_app_empty_str() -> FastAPI:
    app = FastAPI(title="PUUID test API with bare str PUUID endpoint")

    def get_bad_empty(puuid: PUUIDBase[Literal[""]]) -> str:
        return "Don't do this (intentionally not allowed)"

    app.get("/path_param/{puuid}")(get_bad_empty)

    return app


def create_app_v4_empty_str() -> FastAPI:
    app = FastAPI(title="PUUID test API with bare str PUUID endpoint")

    def get_bad_v4_empty(puuid: PUUIDBase[Literal[""]]) -> str:
        return "Don't do this (intentionally not allowed)"

    app.get("/path_param/{puuid}")(get_bad_v4_empty)

    return app


def create_app_bare_str() -> FastAPI:
    app = FastAPI(title="PUUID test API with bare str PUUID endpoint")

    def get_bad(puuid: PUUIDBase[str]) -> str:
        return "Don't do this (underspecified)"

    app.get("/path_param/{puuid}")(get_bad)

    return app


def create_app_bare_v4_str() -> FastAPI:
    app = FastAPI(title="PUUID test API with bare str PUUID endpoint")

    def get_bad_v4(puuid: PUUIDv4[str]) -> str:
        return "Don't do this (underspecified)"

    app.get("/path_param_v4/{puuid}")(get_bad_v4)

    return app


################################################################################
# UNUSED fixtures
################################################################################
# We might be able to support de/serialization of less specialized endpoints in
# the future (e.g. `PUUIDBase[str]`, `PUUIDv4[str]`,
#   `PUUIDBase[Literal["user"]]`)
# but this needs additional exploration (e.g. do we dynamically create the
# needed classes, do we look up all possible PUUIDs within the app from a
# registy? What of this is actually possible within the constraints of
# FastAPI/Pydantic)


@pytest.fixture(scope="module")
def app_bare_str() -> FastAPI:
    return create_app_bare_str()


@pytest.fixture(scope="module")
def client_bare_str(app_bare_str: FastAPI) -> TestClient:
    return TestClient(app_bare_str)


@pytest.fixture(scope="module")
def app_bare_v4_str() -> FastAPI:
    return create_app_bare_v4_str()


@pytest.fixture(scope="module")
def client_bare_v4_str(app_bare_v4_str: FastAPI) -> TestClient:
    return TestClient(app_bare_v4_str)


################################################################################
# UNUSED fixtures end
################################################################################


def test_instanciate_bad_api() -> None:
    with pytest.raises(PUUIDError):
        create_app_empty_str()

    with pytest.raises(PUUIDError):
        create_app_v4_empty_str()

    with pytest.raises(AssertionError):
        create_app_bare_str()

    with pytest.raises(AssertionError):
        create_app_bare_v4_str()
