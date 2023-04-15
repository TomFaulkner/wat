from uuid import UUID

import pytest

from wat.nodes import decision

uuids = [
    UUID("d4f421e5-d4a3-4cce-a271-af18226ad83f"),
    UUID("76727b9a-969a-47eb-8b9f-7d8dafa692f1"),
    UUID("5d677c55-e7e1-4a2c-b42f-fe4263098601"),
]

choices = {
    True: 1,
    False: 0,
    "other": 2,
}  # assert len(choices) == len(ni.decision_options)


def test__decide_bool_any():
    ni_config = {
        "decision": {
            "choices": {True: 1, False: 0},  # this could be a default?
            "rules": [
                {"op": "eq", "operand_1": 72, "operand_2": 72, "operand_types": "int"},
                {"op": "lt", "operand_1": 72, "operand_2": 72, "operand_types": "int"},
            ],
            "strategy": "any",
        }
    }

    res = decision._decide(ni_config)
    assert res == 1


def test__decide_bool_all():
    ni_config = {
        "decision": {
            "choices": {True: 1, False: 0},
            "rules": [
                {"op": "lt", "operand_1": 72, "operand_2": 64, "operand_types": "int"},
                {"op": "gt", "operand_1": 72, "operand_2": 64, "operand_types": "int"},
            ],
            "strategy": "all",
        }
    }

    res = decision._decide(ni_config)
    assert res == 0


def test__decide_bool_choices_must_match_strategy():
    ni_config = {
        "decision": {
            "choices": {True: 1, "False": 0},
            "rules": [
                {"op": "lt", "operand_1": 72, "operand_2": 64, "operand_types": "int"},
                {"op": "gt", "operand_1": 72, "operand_2": 64, "operand_types": "int"},
            ],
            "strategy": "all",
        }
    }

    with pytest.raises(decision.ChoicesMustMatchStrategy):
        decision._decide(ni_config)


def test_make_decision_from_state():
    ni_config = {
        "decision": {
            "choices": {True: 1, False: 0},
            "rules": [
                {
                    "op": "eq",
                    "operand_1": "{{state.temperature}}",
                    "operand_2": 72,
                    "operand_types": "int",
                },
            ],
            "strategy": "any",
        }
    }

    res = decision.make_decision(ni_config, {"temperature": 72})
    assert res == 1


def test__parse_state():
    state = {"temperature": 72, "something": "else"}
    res = decision._parse_state("{{state.temperature}}", state)
    assert res == "72"


def test__parse_state_no_vars():
    state = {}
    res = decision._parse_state("", state)
    assert res == ""


def test__pull_from_state():
    state = {"temp": 72, "too_hot": 92}
    res = decision._pull_from_state(
        state,
        {
            "op": "eq",
            "operand_1": "{{state.temp}}",
            "operand_2": "{{state.too_hot}}",
            "operand_types": "int",
        },
    )
    assert res == {"op": "eq", "operand_1": 72, "operand_2": 92, "operand_types": "int"}
