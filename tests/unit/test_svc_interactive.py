from unittest.mock import AsyncMock

import pytest

from wat.data import node, workflows
from wat.svc import interactive


@pytest.fixture
def mock_workflow():
    return {
        "template": True,
        "template_active": True,
        "id": "550ef5da-36a6-11ed-a892-bb8818cce9dc",
        "state": "waiting",
        "flowstate": {"id": "fs1", "state": {}},
        "node_instances": [
            {
                "children": [],
                "depends": 0,
                "depends_on": [],
                "id": "ffffffff-2bd2-11ed-b25b-ab922a707b03",
                "node": {
                    "base": "interactive",
                    "config": {},
                    "id": "aaaaaaaa-2bd2-11ed-b25b-ab922a707b03",
                    "name": "interactive",
                    "type": "ingestion",
                    "version": 1,
                },
                "parents": [],
                "required_state": [],
                "state": "pending",
                "config": (
                    '{"prompt": {"name": "Video Game", "model":'
                    '{"bits": ["int", 16], "name": ["str", null],'
                    '"popular": ["bool", true]}}}'
                ),
            },
        ],
    }


ni_id = "ffffffff-2bd2-11ed-b25b-ab922a707b03"


async def test_fetch_ni_prompts(mock_workflow, monkeypatch):
    get = AsyncMock(interactive._get_wf_and_ni)
    get.return_value = mock_workflow, mock_workflow["node_instances"][0]
    monkeypatch.setattr(interactive, "_get_wf_and_ni", get)
    monkeypatch.setattr(interactive, "_check_lane_token", lambda _, __: "")

    res = await interactive.fetch_ni_prompts(ni_id, token="", tx=None)
    assert res == {
        "title": "Video Game",
        "type": "object",
        "properties": {
            "bits": {"title": "Bits", "default": 16, "type": "integer"},
            "name": {"title": "Name", "type": "string"},
            "popular": {"title": "Popular", "default": True, "type": "boolean"},
        },
        "required": ["name"],
    }


async def test_post(mock_workflow, monkeypatch):
    get = AsyncMock(interactive._get_wf_and_ni)
    get.return_value = mock_workflow, mock_workflow["node_instances"][0]
    monkeypatch.setattr(interactive, "_get_wf_and_ni", get)

    upd_fs = AsyncMock(workflows.update_flow_state)
    upd_inst_state = AsyncMock(node.update_instance_state)
    monkeypatch.setattr(workflows, "update_flow_state", upd_fs)
    monkeypatch.setattr(node, "update_instance_state", upd_inst_state)

    body = {"bits": 16, "popular": False, "name": "ROTK II"}

    await interactive.post(ni_id, body, token="")

    upd_fs.assert_awaited_with(mock_workflow["flowstate"]["id"], body, None)
    upd_inst_state.assert_awaited_with(
        mock_workflow["node_instances"][0]["id"], "completed", client=None
    )
