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
                "depends": 0,
                "depends_on": [],
                "id": "550f616e-36a6-11ed-a892-abe733d6e265",
                "node": {
                    "base": "action",
                    "config": {},
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "hello_world",
                    "type": "api",
                    "version": 1,
                },
                "parents": [],
                "required_state": ["greeting_name"],
                "state": "pending",
            },
            {
                "children": [{"id": "ffffffff-2bd2-11ed-b25b-ab922a707b03"}],
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
                "children": [{"id": "ffffffff-2bd2-11ed-b25b-ab922a707b03"}],
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
                "depends": 2,
                "depends_on": [
                    {"id": "550f616e-36a6-11ed-a892-abe733d6e265"},
                    {"id": "550fdce8-36a6-11ed-a892-3369233e6ccb"},
                ],
                "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                "node": {
                    "base": "finish",
                    "config": {},
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


@pytest.fixture
def mock_workflow_w_api():
    return {
        "template": True,
        "template_active": True,
        "id": "550ef5da-36a6-11ed-a892-bb8818cce9dc",
        "state": "waiting",
        "flowstate": {
            "state": {},
            "created": "2022-09-17T16:32:33.786748+00:00",
            "last_updated": "2022-09-17T16:32:33.786751+00:00",
        },
        "node_instances": [
            {
                "children": [],
                "depends": 0,
                "depends_on": [],
                "id": "550f616e-36a6-11ed-a892-abe733d6e265",
                "node": {
                    "base": "action",
                    "config": {},
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "example_api_httpbin_org_post",
                    "type": "api",
                    "version": 1,
                },
                "parents": [],
                "required_state": [],
                "state": "pending",
            },
            {
                "children": [],
                "depends": 1,
                "depends_on": [],
                "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                "node": {
                    "base": "finish",
                    "config": {},
                    "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                    "name": "finish",
                    "type": "flow",
                    "version": 1,
                },
                "parents": [
                    {"id": "550f616e-36a6-11ed-a892-abe733d6e265"},
                ],
                "required_state": [],
                "state": "blocked",
            },
        ],
    }


@pytest.fixture
def mock_workflow_w_decision():
    return {
        "template": True,
        "template_active": True,
        "id": "550ef5da-36a6-11ed-a892-bb8818cce9dc",
        "state": "waiting",
        "flowstate": {
            "state": {"greeting_name": "Tom", "temperature": 72},
            "created": "2022-09-17T16:32:33.786748+00:00",
            "last_updated": "2022-09-17T16:32:33.786751+00:00",
        },
        "node_instances": [
            {
                "children": [
                    {"id": "550fdce8-36a6-11ed-a892-3369233e6ccb"},
                    {"id": "550fa37c-36a6-11ed-a892-e3bf2af53985"},
                ],
                "depends": 0,
                "depends_on": [],
                "id": "550f616e-36a6-11ed-a892-abe733d6e265",
                "node": {
                    "base": "decision",
                    "config": {
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
                    },
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "decision",
                    "type": "decision",
                    "version": 1,
                },
                "parents": [],
                "required_state": ["temperature"],
                "state": "pending",
            },
            {
                "children": [{"id": "ffffffff-2bd2-11ed-b25b-ab922a707b03"}],
                "depends": 1,
                "depends_on": [],
                "id": "550fdce8-36a6-11ed-a892-3369233e6ccb",
                "sequence": 1,
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
                "children": [{"id": "ffffffff-2bd2-11ed-b25b-ab922a707b03"}],
                "depends": -1,
                "depends_on": [],
                "id": "550fa37c-36a6-11ed-a892-e3bf2af53985",
                "sequence": 0,
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
                "depends": 2,
                "depends_on": [
                    {"id": "550f616e-36a6-11ed-a892-abe733d6e265"},
                    {"id": "550fdce8-36a6-11ed-a892-3369233e6ccb"},
                ],
                "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                "node": {
                    "base": "finish",
                    "config": {},
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


@pytest.fixture
def mock_workflow_w_polling():
    return {
        "template": True,
        "template_active": True,
        "id": "550ef5da-36a6-11ed-a892-bb8818cce9dc",
        "state": "waiting",
        "flowstate": {
            "state": {
                "550f616e-36a6-11ed-a892-abe733d6e265": {
                    "obj_id": "another-uuid",
                    "poll_count": 0,
                }
            },
            "created": "2022-09-17T16:32:33.786748+00:00",
            "last_updated": "2022-09-17T16:32:33.786751+00:00",
        },
        "node_instances": [
            {
                "children": [],
                "depends": 0,
                "depends_on": [],
                "id": "550f616e-36a6-11ed-a892-abe733d6e265",
                "node": {
                    "base": "action",
                    "config": {},
                    "id": "9a465bea-2bd2-11ed-b25b-ab922a707b03",
                    "name": "example_api_send_and_poll",
                    "type": "api",
                    "version": 1,
                },
                "parents": [],
                "required_state": [],
                "state": "polling",
            },
            {
                "children": [],
                "depends": 1,
                "depends_on": [],
                "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                "node": {
                    "base": "finish",
                    "config": {},
                    "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                    "name": "finish",
                    "type": "flow",
                    "version": 1,
                },
                "parents": [
                    {"id": "550f616e-36a6-11ed-a892-abe733d6e265"},
                ],
                "required_state": [],
                "state": "blocked",
            },
        ],
    }


async def test_execute_wf(mock_workflow):
    await process.execute_wf(mock_workflow)

    assert mock_workflow["state"] == "completed"


async def test_execute_wf_with_real_api_node(mock_workflow_w_api, httpx_mock):
    url = "https://httpbin.org/post"
    httpx_mock.add_response(json={"url": url})

    await process.execute_wf(mock_workflow_w_api)

    assert mock_workflow_w_api["state"] == "completed"
    assert mock_workflow_w_api["flowstate"]["state"]["httpbin_post_response_url"] == url


async def test_execute_wf_w_polling(mock_workflow_w_polling, httpx_mock):
    httpx_mock.add_response(json={"complete": True})

    await process.execute_wf(mock_workflow_w_polling)

    assert mock_workflow_w_polling["state"] == "completed"


async def test_execute_wf_with_decision_node(mock_workflow_w_decision):
    elect_id = "550fdce8-36a6-11ed-a892-3369233e6ccb"
    not_my_people_id = "550fa37c-36a6-11ed-a892-e3bf2af53985"

    await process.execute_wf(mock_workflow_w_decision)

    elect = {}
    not_my_people = {}
    for ni in mock_workflow_w_decision["node_instances"]:
        if elect and not_my_people:
            break
        if ni["id"] == elect_id:
            elect = ni
        if ni["id"] == not_my_people_id:
            not_my_people = ni
    assert elect["state"] == "completed"
    assert not_my_people["state"] == "cancelled"


def test__cancel_children():
    children = [
        {"sequence": 0, "state": "pending"},
        {"sequence": 1, "state": "blocked"},
        {"sequence": 2, "state": "pending"},
    ]
    expected = children.copy()
    expected[2]["state"] = "cancelled"

    res = process._cancel_children(2, children)
    assert res == expected


def test__find_children():
    ni = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    ids = ({"id": "1"}, {"id": "3"})

    res = process._find_children(ni, ids)

    assert len(res) == 2
    assert res[0]["id"] == "1"
    assert res[1]["id"] == "3"
