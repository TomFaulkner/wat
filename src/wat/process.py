import json
import logging
from collections.abc import Sequence
from importlib import import_module
from pprint import pformat
from typing import Any

from pydantic import BaseModel

from wat.lib import pyd
from wat.proc.exc import CallbackNoNodeFound, NodeInstanceInInvalidState

logger = logging.getLogger(__name__)


async def _execute_action_node(
    node_instance, state, module_name, cb_data: dict | None = None
) -> tuple[str, dict[str, Any]]:
    logger.debug(
        "Executing action node: %s (%s) | %s",
        node_instance["id"],
        node_instance["state"],
        state,
    )
    module = import_module(f"wat.nodes.{module_name}")
    match node_instance["state"]:
        case "pending":
            return await module.execute(
                str(node_instance["id"]),
                node_instance["node"]["config"],
                state,
            )
        case "polling":
            return await module.poll(
                str(node_instance["id"]),
                node_instance["node"]["config"],
                state,
            )
        case "waiting":
            return await module.callback(
                str(node_instance["id"]),
                node_instance["node"]["config"],
                state,
                cb_data,
            )
        case _:
            raise ValueError(node_instance["state"])


DecisionChoiceNumber = int


async def _execute_decision_node(
    node_instance, state, module_name
) -> tuple[DecisionChoiceNumber, dict]:
    module = import_module(f"wat.nodes.{module_name}")
    return await module.execute(node_instance["node"]["config"], state)


def _check_required_state(ni, wf_state):
    if ni["required_state"]:
        for key in ni["required_state"]:
            if not wf_state.get(key):
                logger.info("Can not run %s due to missing state %s", ni["id"], key)
                return False
    return True


def _find_children(
    node_instances: Sequence[dict], children_ids: Sequence[dict[str, str]]
) -> list[dict]:
    ids = [i["id"] for i in children_ids]
    return [ni for ni in node_instances if ni["id"] in ids]


def _cancel_children(elect: int, children: list[dict]):
    for ni in children:
        if ni["sequence"] != elect:
            ni["state"] = "cancelled"
    return children


async def _execute_wf(wf) -> bool:  # one or more nodes completed
    node_completed = False
    for instance in wf["node_instances"]:
        if instance["state"] not in ("pending", "polling") or _check_required_state(
            instance, wf["flowstate"]["state"]
        ):
            continue

        logger.debug("Executing %s", instance["id"])
        match instance["node"]["base"]:
            case "action":
                module_name = (
                    f"{instance['node']['name']}_v{instance['node']['version']}"
                )
                # TODO: move this try/except to a decorator or another function
                try:
                    status, state_update = await _execute_action_node(
                        instance, wf["flowstate"]["state"].copy(), module_name
                    )
                    logger.debug(
                        "_execute_action_node results: %s | %s",
                        status,
                        state_update,
                    )
                except Exception:
                    instance["state"] = "error"
                    logger.exception(
                        "Workflow (%s:%s) failed to run %s",
                        wf["id"],
                        instance["id"],
                        module_name,
                    )
                    continue

                # TODO: include this in the decorator
                wf["flowstate"]["state"].update(state_update)
                instance["state"] = status
                if status == "completed":
                    node_completed = True

            case "decision":
                module_name = (
                    f"{instance['node']['name']}_v{instance['node']['version']}"
                )
                try:  # TODO: see above TODO
                    decision, state_update = await _execute_decision_node(
                        instance, wf["flowstate"]["state"].copy(), module_name
                    )

                    children = _find_children(
                        wf["node_instances"], instance["children"]
                    )
                    _cancel_children(decision, children)  # mutates children

                    wf["flowstate"]["state"].update(state_update)
                    instance["state"] = "completed"
                    node_completed = True
                except Exception:
                    instance["state"] = "error"
                    logger.exception(
                        "Workflow (%s:%s) failed to run %s",
                        wf["id"],
                        instance["id"],
                        module_name,
                    )
                    continue

            case "start":
                logger.info("Started workflow. %s", wf["id"])
                instance["state"] = "completed"
                wf["state"] = "started"

            case "finish":
                instance["state"] = "completed"
                wf["state"] = "completed"
                logger.info("Finished workflow. %s", wf["id"])

    return node_completed


def _has_available_instance(node_instances):
    return any(
        ni for ni in node_instances if ni["state"] in ("pending", "blocked", "polling")
    )


def blocked_node_can_run(node, parents, parent_ids, wf_state) -> bool:
    completed_parents = [p for p in parents if p["state"] == "completed"]
    if not len(completed_parents) >= node["depends"]:
        logger.debug(
            "Node Instance %s can not run. Not enough depends met.", node["id"]
        )
        return False

    completed_ids = {cp["id"] for cp in completed_parents}
    depends_ids = {cp["id"] for cp in node["depends_on"]}
    if not completed_ids >= depends_ids:
        logger.debug(
            "Node Instance %s can not run. Not all depends_on IDs met.", node["id"]
        )
        return False

    logger.debug("Node Instance %s can run.", node["id"])

    return _check_required_state(node, wf_state)


def _get_parent_nodes(parent_ids, node_instances):
    return [p for p in node_instances if p["id"] in parent_ids]


def _parent_ids(node):
    return {p["id"] for p in node["parents"]}


async def execute_wf(workflow) -> dict:
    logger.debug("Executing wf:%s ::: %s", workflow["id"], workflow)

    node_completed = True

    while node_completed and _has_available_instance(workflow["node_instances"]):
        node_completed = await _execute_wf(workflow)
        if __debug__:
            logger.debug(
                "Node states: %s", [ni["state"] for ni in workflow["node_instances"]]
            )

        # TODO: move this to its own function, try_update_to_pending_state or similar
        for ni in workflow["node_instances"]:
            logger.debug("Examining NI %s", ni["id"])
            if ni["state"] != "blocked":
                continue

            parent_ids = _parent_ids(ni)
            parents = _get_parent_nodes(parent_ids, workflow["node_instances"])
            if blocked_node_can_run(
                ni, parents, parent_ids, workflow["flowstate"]["state"]
            ):
                ni["state"] = "pending"

    logger.debug("Ending execute_wf: %s", pformat(workflow))
    return {}  # TODO: should this return a finish nodes results instead (in TODO notes)


def _find_node(n_instances, ni_id: str) -> dict:
    return [ni for ni in n_instances if str(ni["id"]) == ni_id][0]


def _validate_cb_data(model_config, body) -> BaseModel:
    return pyd.create_model_from_dict("CBData", model_config)(**body)


async def handle_callback(workflow, ni_id: str, body: dict):
    # TODO: validate and parse using a pydantic model stored in ni config
    try:
        ni = _find_node(workflow["node_instances"], ni_id)
    except IndexError as e:
        raise CallbackNoNodeFound(ni_id) from e
    if ni["state"] != "waiting":
        raise NodeInstanceInInvalidState(ni["state"])

    config = json.loads(ni["config"])
    body = _validate_cb_data(config["model"], body).dict()

    status, state_update = await _execute_action_node(
        ni,
        workflow["flowstate"]["state"],
        f"{ni['node']['name']}_v{ni['node']['version']}",
        body,
    )
    workflow["flowstate"]["state"].update(state_update)
    ni["state"] = status

    # callback notes
    # TODO: waiting status doesn't block children, not sure if this is still a problem
    # wf: 550ef5da-36a6-11ed-a892-bb8818cce9dc
