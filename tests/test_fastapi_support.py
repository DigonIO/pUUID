import re
from typing import Literal

import pytest

pytest.importorskip("fastapi", reason="FastAPI is an optional dependency")
pytest.importorskip("httpx", reason="httpx is required for FastAPI TestClient")
pytest.importorskip("pydantic", reason="Pydantic is an optional dependency")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from puuid import PUUIDError, PUUIDv4, PUUIDv7
from puuid.base import ERR_MSG


class UserUUID(PUUIDv4[Literal["user"]]): ...


class DocUUID(PUUIDv7[Literal["doc"]]): ...


class Payload(BaseModel):
    user_id: UserUUID
    doc_id: DocUUID | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="PUUID test API")

    def get_path_param(user_id: UserUUID) -> DocUUID:
        # fake doc lookup:
        return DocUUID()

    def post_payload(payload: Payload) -> Payload:
        return payload

    app.get("/path_param/{user_id}")(get_path_param)
    app.post("/payload")(post_payload)

    return app


@pytest.fixture(scope="module")
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope="module")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_openapi_spec__path_param(client: TestClient) -> None:
    response = client.get("/openapi.json")  # pyright: ignore[reportUnknownMemberType]
    spec = response.json()

    match spec:
        case {
            "paths": {
                "/path_param/{user_id}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "user_id",
                                "schema": {
                                    "type": "string",
                                    "examples": [
                                        str(param_example_0),
                                        *_param_examples_rem,
                                    ],
                                    "pattern": str(param_pattern_str),
                                },
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "string",
                                            "examples": [
                                                str(response_example_0),
                                                *_response_examples_rem,
                                            ],
                                            "pattern": str(response_pattern_str),
                                        }
                                    }
                                },
                            },
                        },
                    },
                }
            }
        }:
            ...
        case _:
            raise AssertionError

    assert param_example_0.startswith("user_")
    assert response_example_0.startswith("doc_")

    pattern_0 = re.compile(param_pattern_str)
    _user_id = UserUUID.from_string(param_example_0)
    assert pattern_0.fullmatch(param_example_0)
    assert pattern_0.fullmatch("user_1a3e0e89-a2d8-4950-bafa-24020e09b2a6")
    assert not pattern_0.fullmatch("user_1a3e0e89-a2d8-4950-bafa-24020e09b2a6X")
    assert not pattern_0.fullmatch("_1a3e0e89-a2d8-4950-bafa-24020e09b2a6")

    pattern_1 = re.compile(response_pattern_str)
    _doc_id = DocUUID.from_string(response_example_0)
    assert pattern_1.fullmatch("doc_1a3e0e89-a2d8-4950-bafa-24020e09b2a6")
    assert pattern_1.fullmatch(response_example_0)

    assert not pattern_1.fullmatch("user_1a3e0e89-a2d8-4950-bafa-24020e09b2a6")


def test_openapi_spec__payload(client: TestClient) -> None:
    response = client.get("/openapi.json")  # pyright: ignore[reportUnknownMemberType]
    spec = response.json()
    match spec:
        case {
            "paths": {
                "/payload": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Payload-Input"
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Payload-Output"
                                        }
                                    }
                                },
                            },
                        },
                    },
                }
            },
            "components": {
                "schemas": {
                    "Payload-Input": {
                        "properties": {
                            "user_id": {
                                "pattern": user_pattern_input_str,
                                "title": "UserUUID",
                                "examples": user_examples_input,
                            },
                            "doc_id": {
                                "anyOf": [
                                    {
                                        "pattern": doc_pattern_input_str,
                                        "title": "DocUUID",
                                        "examples": doc_examples_input,
                                    },
                                    {"type": "null"},
                                ],
                            },
                        },
                        "required": ["user_id"],
                        "title": "Payload",
                    },
                    "Payload-Output": {
                        "properties": {
                            "user_id": {
                                "pattern": user_pattern_output_str,
                                "title": "UserUUID",
                                "examples": user_examples_output,
                            },
                            "doc_id": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                        "pattern": doc_pattern_output_str,
                                        "title": "DocUUID",
                                        "examples": doc_examples_output,
                                    },
                                    {"type": "null"},
                                ],
                            },
                        },
                        "required": ["user_id"],
                        "title": "Payload",
                    },
                }
            },
        }:
            ...
        case _:
            raise AssertionError

    user_pattern_input = re.compile(user_pattern_input_str)
    user_pattern_output = re.compile(user_pattern_output_str)
    doc_pattern_input = re.compile(doc_pattern_input_str)
    doc_pattern_output = re.compile(doc_pattern_output_str)

    for user_example in [*user_examples_input, *user_examples_output]:
        _user_id = UserUUID.from_string(user_example)
        assert user_pattern_input.fullmatch(user_example)
        assert user_pattern_output.fullmatch(user_example)
        assert not doc_pattern_input.fullmatch(user_example)
        assert not doc_pattern_output.fullmatch(user_example)
        with pytest.raises(PUUIDError) as err_1:
            _other_id = DocUUID.from_string(user_example)
        assert err_1.value.message == ERR_MSG.PREFIX_DESERIALIZATION_ERROR.format(
            prefix="doc", classname="DocUUID", serial_puuid=user_example
        )

    for doc_example in [*doc_examples_input, *doc_examples_output]:
        _doc_id = DocUUID.from_string(doc_example)
        assert not user_pattern_input.fullmatch(doc_example)
        assert not user_pattern_output.fullmatch(doc_example)
        assert doc_pattern_input.fullmatch(doc_example)
        assert doc_pattern_output.fullmatch(doc_example)

        with pytest.raises(PUUIDError) as err_1:
            _user_id = UserUUID.from_string(doc_example)
        assert err_1.value.message == ERR_MSG.PREFIX_DESERIALIZATION_ERROR.format(
            prefix="user", classname="UserUUID", serial_puuid=doc_example
        )


def test_fastapi_puid(client: TestClient) -> None:
    puid = UserUUID()
    response = client.get(f"/path_param/{puid.to_string()}")
    doc_id = DocUUID.from_string(response.json())

    bad_response = client.get(f"/path_param/{doc_id.to_string()}")
    assert bad_response.status_code == 422

    match bad_response.json():
        case {
            "detail": [
                {
                    "type": "value_error",
                    "loc": ["path", "user_id"],
                    "msg": msg,
                    "input": input_val,
                    "ctx": {"error": {}},
                }
            ]
        }:
            ...
        case _:
            raise AssertionError

    assert input_val == doc_id.to_string()
    assert f"Value error, {ERR_MSG.PREFIX_DESERIALIZATION_ERROR.format(
        prefix="user", classname="UserUUID", serial_puuid=input_val
    )}" == msg


def test_payload(client: TestClient) -> None:
    uid = UserUUID()
    doc = DocUUID()
    payload = {"user_id": uid.to_string(), "doc_id": doc.to_string()}

    response = client.post("/payload", json=payload)
    assert response.status_code == 200
    assert response.json() == payload

    invalid_payload = {"user_id": doc.to_string()}
    response = client.post("/payload", json=invalid_payload)
    assert response.status_code == 422
