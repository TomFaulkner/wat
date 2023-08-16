import pytest

from wat.lib.state import (
    MissingBodyStateKeys,
    MissingTranslation,
    _key_translation,
    filter_state,
    process_state,
)
from wat.schemas.node_instance_config import SendBody


def test__key_translation_happy():
    state = {"name": "Tom", "age": 43}
    translations = {"name": "llamo", "age": "edad"}

    assert _key_translation(translations, state) == {"llamo": "Tom", "edad": 43}


def test__key_translation_missing():
    state = {"name": "Tom", "age": 43}
    translations = {"name": "llamo", "birth_year": "edad"}

    with pytest.raises(MissingTranslation):
        _key_translation(translations, state)


def test_filter_state_extra_keys():
    state = {"name": "Tom", "age": 43}
    assert filter_state(state, {"name"}) == {"name": "Tom"}


def test_filter_state_missing_keys():
    state = {"llamo": "Tom", "age": 43}
    with pytest.raises(MissingBodyStateKeys):
        filter_state(state, {"name"})


def test_process_state_happy():
    sb = SendBody(
        body_format="json",
        state_vars=["name", "age"],
        key_translation={"name": "llamo", "age": "edad"},
    )
    state = {"name": "Tom", "age": 43}

    assert process_state(sb, state) == {"llamo": "Tom", "edad": 43}


def test_process_state_no_state_vars():
    sb = SendBody(
        body_format="json",
        state_vars=[],
        key_translation={"name": "llamo", "age": "edad"},
    )
    state = {"name": "Tom", "age": 43}

    assert process_state(sb, state) == {}


def test_process_state_no_translation():
    sb = SendBody(
        body_format="json",
        state_vars=["name", "age"],
        key_translation={},
    )
    state = {"name": "Tom", "age": 43}

    assert process_state(sb, state) == {"name": "Tom", "age": 43}
