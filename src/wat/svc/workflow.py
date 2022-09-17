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


async def _create_node_instances(node_instances, create_node, update_node_children):
    """Makes a copy of each node instance and replaces id parents and depends_on with
    new ids.
    """

    ids = {}
    for ni in node_instances:
        stripped_ni = _strip_ni(ni)
        new_node = await create_node(stripped_ni)
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
        await update_node_children(ni)


async def _adapter_upd_ni_rels(ni):
    return await node.update_node_instance_relationships(
        ni["id"], ni["parents"], ni["depends_on"], ni["decision_options"]
    )


async def create_instance(wf_id: str) -> dict[str, Any]:
    wf = await workflows.get_by_id(wf_id)
    del wf["id"]
    del wf["flowstate"]
    node_instances = wf.pop("node_instances")
    new_wf = await create(wf)

    add_instance = partial(node.add_instance, workflow=new_wf["id"])
    await _create_node_instances(node_instances, add_instance, _adapter_upd_ni_rels)
    return await workflows.get_by_id(new_wf["id"])


async def get_by_id(wf_id: str) -> dict[str, Any]:
    return await workflows.get_by_id(wf_id)


async def execute_workflow(wf_id: str, no_updates=False):
    wf = await workflows.get_by_id(wf_id)
    await process.execute_wf(wf)
    if not no_updates:
        pass
        # update workflow state and node instances

    return True
