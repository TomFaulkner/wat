import json
from typing import Any, TypedDict

from wat.data import node, workflows
from wat.lib.pyd import ModelConfig, create_model_from_dict


def _ni_from_wf(wf, ni_id: str) -> dict[str, Any] | None:
    for ni in wf["node_instances"]:
        if str(ni["id"]) == ni_id:
            return ni


class NodeInstanceNotFound(ValueError):
    """Not Instance wasn't found"""


class InteractiveNodeMissingConfig(ValueError):
    """Interactive Node instance doesn't have a prompt."""


async def _get_wf_and_ni(ni_id: str, tx) -> tuple[dict, dict]:
    wf_id_obj = await node.get_node_instance_parent_workflow(ni_id, tx)
    wf = await workflows.get_by_id(str(wf_id_obj.workflow.id))
    ni = _ni_from_wf(wf, ni_id)
    if not ni:
        raise NodeInstanceNotFound
    return wf, ni


class NodeModelConfig(TypedDict):
    name: str
    model: ModelConfig


def _parse_prompt(node_config_model: NodeModelConfig):
    return create_model_from_dict(node_config_model["name"], node_config_model["model"])


async def fetch_ni_prompts(ni_id: str, tx):
    _, ni = await _get_wf_and_ni(ni_id, tx)
    if ni["config"] != "{}":
        print(ni["config"])
        return _parse_prompt(json.loads(ni["config"])["prompt"]).schema()
    raise InteractiveNodeMissingConfig


def _filter_for_interactive_nodes(nins: list[dict]) -> dict[str, Any] | None:
    try:
        return [
            ni
            for ni in nins
            if ni["state"] == "pending" and ni["node"]["base"] == "interactive"
        ][0]
    except IndexError:
        return None


async def get_next_interactive_node(wf_id: str, tx) -> str | None:
    wf = await workflows.get_by_id(wf_id)
    int_ni = _filter_for_interactive_nodes(wf["node_instances"])
    if not int_ni:
        return None
    return str(int_ni["id"])


async def post(ni_id: str, body: dict, tx):
    wf, ni = await _get_wf_and_ni(ni_id, tx)
    obj = _parse_prompt(json.loads(ni["config"])["prompt"])(**body)
    await workflows.update_flow_state(str(wf["flowstate"]["id"]), obj.dict(), tx)
    await node.update_instance_state(ni_id, "completed", client=tx)
