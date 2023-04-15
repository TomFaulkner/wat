import logging
from functools import partial
from typing import Any

import pydantic

from .. import process
from ..data import node, workflows

logger = logging.getLogger(__name__)


async def create(workflow: dict, tx) -> dict[str, Any]:
    return await workflows.add(workflow, client=tx)


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
    wf = await workflows.get_active_template_by_id(wf_id, client=tx)
    wf = _strip_wf(wf.copy())
    node_instances = wf.pop("node_instances")
    start_requirements = wf.pop("start_requirements")
    if start_requirements:
        wf["start_requirements"] = [str(sr["id"]) for sr in start_requirements]
    else:
        wf["start_requirements"] = []
    new_wf = await create(wf, tx)

    add_instance = partial(node.add_instance, workflow=new_wf["id"])
    await _create_node_instances(node_instances, add_instance, _adapter_upd_ni_rels, tx)
    return await workflows.get_by_id(new_wf["id"], client=tx)


class NoStartState(Exception):
    """This workflow requires a starting attributes."""

    def __init__(self, requirements: dict):
        self.requirements = requirements


def _validate_start_requirements(
    start_reqs: dict, attributes: dict | None
) -> pydantic.BaseModel:
    if not attributes:
        raise NoStartState(requirements=start_reqs)
    fields = {}
    for f in start_reqs:
        if f["default_value"]:
            fields[f["name"]] = f["default_value"]
            continue
        fields[f["name"]] = (f["type"], ...)
    model = pydantic.create_model("StartRequirements", **fields)
    return model(**attributes)


async def execute_workflow(wf_id: str, suppress_updates=False, tx=None):
    wf = await workflows.get_by_id(wf_id, client=tx)
    await process.execute_wf(wf)

    # TODO: try and test this
    if not suppress_updates or not tx:
        await workflows.update_flow_state(
            wf["flowstate"]["id"], wf["flowstate"]["state"], tx
        )
        await workflows.update_state(wf_id, wf["state"], tx)
        for ni in wf["node_instances"]:
            await node.update_instance_state(ni["id"], ni["state"], client=tx)
    return True


async def create_and_run(tx, wf_id: str, start: dict[str, Any] | None = None):
    """Start an new workflow instance.

    This should be the main way workflows are started."""

    wf = await create_instance(wf_id, tx=tx)
    start_attrs = {}
    if wf["start_requirements"]:
        start_attrs = _validate_start_requirements(
            wf["start_requirements"], start
        ).dict()

    await workflows.update_flow_state(wf["flowstate"]["id"], start_attrs, tx)
    await execute_workflow(wf["id"], tx=tx)
    return await workflows.get_by_id(wf["id"], client=tx)


async def get_by_id(wf_id: str) -> dict[str, Any]:
    return await workflows.get_by_id(wf_id)


async def get(template_only=False, active_template_only=False) -> list[dict[str, Any]]:
    return await workflows.get(
        template_only=template_only, active_template_only=active_template_only
    )


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
