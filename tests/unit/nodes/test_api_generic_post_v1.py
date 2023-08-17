import pytest
from pytest_httpx import HTTPXMock

import wat.schemas.node_instance_config as ni_config
from wat.nodes import api_generic_post_v1 as api


# execute
async def test_execute_happy_simple(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"response": True})
    config = ni_config.Config(
        api_call=(
            {
                "url": "test_url",
                "method": "POST",
                "send_body": {
                    "state_vars": ["name", "age"],
                    "key_translation": {"name": "llamo", "age": "edad"},
                    "body_format": "json",
                },
                "send_body_type": "json",
                "response_body": {
                    "body_format": "json",
                    "key_translation": {"response": ("response", True)},
                },
            }
        )
    ).dict()
    state = {"name": "Tom", "age": 43}

    status, state_update = await api.execute("1234", config, state)
    assert status == "completed"
    assert state_update == {"response": True}


# _response_handler
def test__response_handler_200_no_hold():
    status, state_update = api._response_handler(
        200, {"response": True}, "1234", {"response": ("response", True)}, None
    )
    assert status == "completed"
    assert state_update == {"response": True}


def test__response_handler_200_callback():
    status, state_update = api._response_handler(
        200, {"response": True}, "1234", {"response": ("response", True)}, "callback"
    )
    assert status == "waiting"
    assert state_update == {
        "1234": {
            "callback_count": 0,
            "updates": [],
        }
    }


def test__response_handler_200_polling():
    status, state_update = api._response_handler(
        200, {"response": True}, "1234", {"response": ("response", True)}, "polling"
    )
    assert status == "polling"
    assert state_update == {
        "1234": {
            "poll_count": 0,
            "updates": [],
        }
    }


def test__response_handler_400():
    with pytest.raises(api.APISendingException):
        api._response_handler(
            400, {"response": True}, "1234", {"response": ("response", True)}, None
        )


def test__response_handler_500():
    with pytest.raises(api.APISendingException):
        api._response_handler(
            500, {"response": True}, "1234", {"response": ("response", True)}, None
        )


# _state_response_translation
def test__state_response_translation_no_change():
    assert api._state_response_translation(
        {"response": ("response", True)}, {"response": True}
    ) == {"response": True}


def test__state_response_translation_rename():
    assert api._state_response_translation(
        {"response": ("new_name", True)}, {"response": True}
    ) == {"new_name": True}


def test__state_response_translation_required_missing():
    with pytest.raises(api.APIResponseMissingField):
        api._state_response_translation(
            {"response": ("new_name", True), "missing": ("missing", True)},
            {"response": True},
        )


def test__state_response_translation_not_required_missing():
    assert api._state_response_translation(
        {"response": ("response", True), "missing": ("missing", False)},
        {"response": True},
    ) == {"response": True}
