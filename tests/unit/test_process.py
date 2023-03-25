import pytest

from wat import process


@pytest.fixture
def mock_workflow():
    return {
        "template": True,
        "template_active": True,
        "id": "550ef5da-36a6-11ed-a892-bb8818cce9dc",
        "state": "waiting",
        "flowstate": {
            "state": {"greeting_name": "Tom"},
            "created": "2022-09-17T16:32:33.786748+00:00",
            "last_updated": "2022-09-17T16:32:33.786751+00:00",
        },
        "node_instances": [
            {
                "children": [
                    {"id": "550fdce8-36a6-11ed-a892-3369233e6ccb"},
                    {"id": "550fa37c-36a6-11ed-a892-e3bf2af53985"},
                ],
                "decision_options": None,
                "depends": 0,
                "depends_on": [],
                "id": "550f616e-36a6-11ed-a892-abe733d6e265",
                "node": {
                    "base": "action",
                    "config": '""',
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "hello_world",
                    "type": "api",
                    "version": 1,
                },
                "parents": [],
                "required_state": ["greeting_name"],
                "state": "waiting",
            },
            {
                "children": ["ffffffff-2bd2-11ed-b25b-ab922a707b03"],
                "decision_options": [],
                "depends": 1,
                "depends_on": [],
                "id": "550fdce8-36a6-11ed-a892-3369233e6ccb",
                "node": {
                    "base": "action",
                    "config": '{"debug_id": "550fdce8-36a6-11ed-a892-3369233e6ccb"}',
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "hello_world",
                    "type": "api",
                    "version": 1,
                },
                "parents": [{"id": "550f616e-36a6-11ed-a892-abe733d6e265"}],
                "required_state": ["greeting_name"],
                "state": "blocked",
            },
            {
                "children": ["ffffffff-2bd2-11ed-b25b-ab922a707b03"],
                "decision_options": [],
                "depends": -1,
                "depends_on": [],
                "id": "550fa37c-36a6-11ed-a892-e3bf2af53985",
                "node": {
                    "base": "action",
                    "config": '{"debug_id": "550fa37c-36a6-11ed-a892-e3bf2af53985"}',
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "hello_world",
                    "type": "api",
                    "version": 1,
                },
                "parents": [{"id": "550f616e-36a6-11ed-a892-abe733d6e265"}],
                "required_state": ["greeting_name"],
                "state": "blocked",
            },
            {
                "children": [],
                "decision_options": [],
                "depends": 2,
                "depends_on": [
                    {"id": "550f616e-36a6-11ed-a892-abe733d6e265"},
                    {"id": "550fdce8-36a6-11ed-a892-3369233e6ccb"},
                ],
                "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                "node": {
                    "base": "finish",
                    "config": '""',
                    "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                    "name": "finish",
                    "type": "flow",
                    "version": 1,
                },
                "parents": [
                    {"id": "550f616e-36a6-11ed-a892-abe733d6e265"},
                    {"id": "550fdce8-36a6-11ed-a892-3369233e6ccb"},
                ],
                "required_state": [],
                "state": "blocked",
            },
        ],
    }


async def test_execute_wf(mock_workflow):
    await process.execute_wf(mock_workflow)
    assert mock_workflow["state"] == "completed"
