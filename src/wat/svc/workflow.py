import logging
from functools import partial
from typing import Any

from .. import process
from ..data import node, workflows

logger = logging.getLogger(__name__)


async def create(workflow: dict) -> dict[str, Any]:
    return await workflows.add(workflow)


def _strip_ni(node_instance):
    n = node_instance | {"children": [], "depends_on": []}
    del n["id"]
    return n


def _strip_wf(wf):
    wf["template"] = False
    wf["template_active"] = False
    del wf["id"]
    del wf["flowstate"]
    return wf


async def _create_node_instances(node_instances, create_node, update_node_children, tx):
    """Makes a copy of each node instance and replaces id parents and depends_on with
    new ids.
    """

    ids = {}
    for ni in node_instances:
        stripped_ni = _strip_ni(ni)
        new_node = await create_node(stripped_ni, tx=tx)
        ids[ni["id"]] = new_node["id"]

    for ni in node_instances:
        if not ni["decision_options"] and not ni["depends_on"] and not ni["parents"]:
            continue
        for parent in ni["parents"]:
            parent["id"] = ids[parent["id"]]
        for dep in ni["depends_on"]:
            dep["id"] = ids[dep["id"]]

        ni["decision_options"] = [ids[o] for o in ni["decision_options"] or []]

        ni["id"] = ids[ni["id"]]
        # this needs to be adapted to data.node.update_node_instance_relationships
        # or changed to conform to it
        # probably best to make an adapter function
        await update_node_children(ni, tx)


async def _adapter_upd_ni_rels(ni, tx):
    return await node.update_node_instance_relationships(
        ni["id"], ni["parents"], ni["depends_on"], ni["decision_options"], tx
    )


async def create_instance(wf_id: str, tx) -> dict[str, Any]:
    wf = await workflows.get_active_template_by_id(wf_id)
    wf = _strip_wf(wf.copy())
    node_instances = wf.pop("node_instances")
    new_wf = await create(wf)

    add_instance = partial(node.add_instance, workflow=new_wf["id"])
    await _create_node_instances(node_instances, add_instance, _adapter_upd_ni_rels, tx)
    return await workflows.get_by_id(new_wf["id"])


async def get_by_id(wf_id: str) -> dict[str, Any]:
    return await workflows.get_by_id(wf_id)


async def execute_workflow(wf_id: str, suppress_updates=False):
    wf = await workflows.get_by_id(wf_id)
    await process.execute_wf(wf)
    if not suppress_updates:
        pass
        # update workflow state and node instances

    return True


async def replace_flow_state(wf_id: str, new_state: dict, tx) -> dict:
    wf = await workflows.get_by_id(wf_id)
    res = await workflows.update_flow_state(wf["flowstate"]["id"], new_state, tx)
    logger.debug(
        "WF: %s | Prev State: %s | New State: %s",
        wf_id,
        wf["flowstate"]["state"],
        res["state"],
    )
    return res


async def update_flow_state(wf_id: str, new_state: dict, tx) -> dict:
    wf = await workflows.get_by_id(wf_id)
    state = wf["flowstate"]["state"] | new_state
    res = await workflows.update_flow_state(wf["flowstate"]["id"], state, tx)
    logger.debug(
        "WF: %s | Prev State: %s | New State: %s",
        wf_id,
        wf["flowstate"]["state"],
        res["state"],
    )
    return res
