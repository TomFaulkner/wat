import json
import logging
from functools import partial, singledispatch
from typing import Any
from uuid import UUID

import pydantic

import wat.queries.workflow_add_async_edgeql as q
from wat.queries import workflow_get_all_by_state_async_edgeql as qwf_by_state
from wat.queries import workflow_locations_update_async_edgeql as loc_update

from .. import process
from ..data import node, workflows

logger = logging.getLogger(__name__)


async def create(workflow: dict, tx) -> q.WorkflowAddResult:
    start_state = "template" if workflow["template"] else "waiting"
    workflow["state"] = start_state
    return await q.workflow_add(tx, **workflow)


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
        logger.debug("Start ni: %s", ni)
        stripped_ni = _strip_ni(ni)
        logger.debug("Stripped ni: %s", stripped_ni)
        new_node = await create_node(stripped_ni, tx=tx)
        logger.debug("New NI: %s", new_node)
        ids[ni["id"]] = new_node["id"]

    for ni in node_instances:
        for parent in ni["parents"]:
            parent["id"] = ids[parent["id"]]
        for dep in ni["depends_on"]:
            dep["id"] = ids[dep["id"]]

        ni["id"] = ids[ni["id"]]
        # this needs to be adapted to data.node.update_node_instance_relationships
        # or changed to conform to it
        # probably best to make an adapter function
        await update_node_children(ni, tx)

    return ids


async def _adapter_upd_ni_rels(ni, tx):
    return await node.update_node_instance_relationships(
        ni["id"], ni["parents"], ni["depends_on"], tx
    )


def _map_locations(ids, locations):
    new_locations = {}
    for old, new in ids.items():
        new_locations[new] = locations[old]
    return new_locations


class Location(pydantic.BaseModel):
    x: int
    y: int


class Locations(pydantic.BaseModel):
    __root__: dict[UUID, Location]


async def update_locations(wf_id: UUID, update: Locations | dict, tx):
    def _fix_keys(d: dict) -> dict:
        print({str(k): v for k, v in d["__root__"].items()})
        return {str(k): v for k, v in d["__root__"].items()}

    if isinstance(update, Locations):
        update = _fix_keys(update.dict())
    await loc_update.workflow_locations_update(
        tx, id=wf_id, locations=json.dumps(update)
    )
    return True


async def create_instance(wf_id: str, tx) -> UUID:
    wf = await workflows.get_active_template_by_id(wf_id, client=tx)
    locations = wf["locations"]
    logger.debug("Fetched WF template: %s", wf)
    wf = _strip_wf(wf.copy())
    node_instances = wf.pop("node_instances")
    start_requirements = wf.pop("start_requirements")
    if start_requirements:
        wf["start_requirements"] = [str(sr["id"]) for sr in start_requirements]
    else:
        wf["start_requirements"] = []
    new_wf = await create(wf, tx)

    add_instance = partial(node.add_instance, workflow=str(new_wf.id))
    ids = await _create_node_instances(
        node_instances, add_instance, _adapter_upd_ni_rels, tx
    )
    new_locs = _map_locations(ids, json.loads(locations))
    await update_locations(new_wf.id, new_locs, tx)
    return new_wf.id


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


async def execute_workflow(wf_id: str, suppress_updates=False, tx=None) -> bool:
    wf = await workflows.get_by_id(wf_id, client=tx)
    await process.execute_wf(wf)

    # TODO: try and test this
    # TODO: take advantage of the DI tx instead of suppress_updates bool
    if not suppress_updates or not tx:
        await workflows.update_flow_state(
            wf["flowstate"]["id"], wf["flowstate"]["state"], tx
        )
        await workflows.update_state(wf_id, wf["state"], tx)
        for ni in wf["node_instances"]:
            await node.update_instance_state(ni["id"], ni["state"], client=tx)
    return True


async def start_workflow_arq(ctx, wf_id):
    async for tx in ctx["edge_client"].transaction():
        async with tx:
            await workflows.get_by_id(wf_id, client=tx)
            return await execute_workflow(str(wf_id), tx=tx)


async def create_and_run(tx, wf_id: str, start: dict[str, Any] | None = None):
    """Start an new workflow instance.
    Runs in the app rather than the worker.

    This should no longer be the main way workflows are started."""

    wf = await create_instance(wf_id, tx=tx)
    logger.debug("Created WF: %s", wf)
    start_attrs = {}
    if wf["start_requirements"]:
        start_attrs = _validate_start_requirements(
            wf["start_requirements"], start
        ).dict()

    await workflows.update_flow_state(wf["flowstate"]["id"], start_attrs, tx)
    await execute_workflow(wf["id"], tx=tx)
    return await workflows.get_by_id(wf["id"], client=tx)


async def get_by_id(wf_id: str, tx=None) -> dict[str, Any]:
    if tx:
        return await workflows.get_by_id(wf_id, client=tx)

    return await workflows.get_by_id(wf_id)


async def get(template_only=False, active_template_only=False) -> list[dict[str, Any]]:
    return await workflows.get(
        template_only=template_only, active_template_only=active_template_only
    )


async def get_by_state(state: str, tx) -> list:
    return await qwf_by_state.workflow_get_all_by_state(tx, state=state)


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


async def _update_flow_state_from_wf(wf: dict, new_state: dict, tx) -> dict:
    state = wf["flowstate"]["state"] | new_state
    res = await workflows.update_flow_state(wf["flowstate"]["id"], state, tx)
    logger.debug(
        "WF: %s | FS ID: %s | Prev State: %s | New State: %s",
        wf["id"],
        wf["flowstate"]["id"],
        wf["flowstate"]["state"],
        res["state"],
    )
    return res


@singledispatch
async def update_flow_state(wf_id: str, new_state: dict, tx) -> dict:
    wf = await workflows.get_by_id(wf_id, client=tx)
    return await _update_flow_state_from_wf(wf, new_state, tx)


@update_flow_state.register
async def _(wf: dict, new_state: dict, tx) -> dict:
    return await _update_flow_state_from_wf(wf, new_state, tx)


async def update_flow_state_from_flowstate_id(
    flowstate_id: str, new_state: dict, tx
) -> dict:
    await workflows.update_flow_state(flowstate_id, new_state, tx)


async def enqueue_wf(wf_id: str) -> None:
    from arq import create_pool

    redis = await create_pool()
    await redis.enqueue_job("start_workflow_arq", wf_id)


async def callback(ni_id: str, body: dict, tx):
    ni = await node.get_node_instance_parent_workflow(ni_id, tx)
    logger.debug("Callback body: %s", body)
    wf = await workflows.get_by_id(ni.workflow.id)

    await process.handle_callback(wf, ni_id, body)

    await workflows.update_flow_state(
        wf["flowstate"]["id"], wf["flowstate"]["state"], tx
    )
    await workflows.update_state(wf["id"], wf["state"], tx)
    for ni in wf["node_instances"]:
        await node.update_instance_state(ni["id"], ni["state"], client=tx)

    await enqueue_wf(wf["id"])


def validate_workflow(wf, start_attributes: dict[str, Any]) -> dict:
    start = {}
    if wf["start_requirements"]:
        start = _validate_start_requirements(
            wf["start_requirements"], start_attributes
        ).dict()
    return start
