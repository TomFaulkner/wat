import logging
from collections.abc import Sequence
from importlib import import_module
from pprint import pformat
from typing import Any

logger = logging.getLogger(__name__)


async def _execute_action_node(
    node_instance, state, module_name
) -> tuple[bool, dict[str, Any]]:
    module = import_module(f"wat.nodes.{module_name}")
    return await module.execute(node_instance["node"]["config"], state)


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


async def _execute_wf(wf) -> bool:
    node_ran = False
    for instance in wf["node_instances"]:
        if instance["state"] == "waiting" and _check_required_state(
            instance, wf["flowstate"]["state"]
        ):
            logger.debug("Executing %s", instance["id"])
            match instance["node"]["base"]:
                case "action":
                    module_name = (
                        f"{instance['node']['name']}_v{instance['node']['version']}"
                    )
                    # TODO: move this try/except to a decorator or another function
                    try:
                        success, state_update = await _execute_action_node(
                            instance, wf["flowstate"]["state"], module_name
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

                    if success:  # TODO: include this in the decorator
                        wf["flowstate"]["state"].update(state_update)
                        instance["state"] = "completed"
                        node_ran = True

                case "decision":
                    module_name = (
                        f"{instance['node']['name']}_v{instance['node']['version']}"
                    )
                    try:  # TODO: see above TODO
                        decision, state_update = await _execute_decision_node(
                            instance, wf["flowstate"]["state"], module_name
                        )
                        children = _find_children(
                            wf["node_instances"], instance["children"]
                        )
                        _cancel_children(decision, children)  # mutates children

                        wf["flowstate"]["state"].update(state_update)
                        instance["state"] = "completed"
                        node_ran = True
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

    return node_ran


def _has_available_instance(node_instances):
    return any(ni for ni in node_instances if ni["state"] in ("waiting", "blocked"))


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


async def execute_wf(workflow) -> bool:
    logger.debug("Executing wf:%s ::: %s", workflow["id"], workflow)

    node_ran = True

    ran_at_least_one = False
    while node_ran and _has_available_instance(workflow["node_instances"]):
        node_ran = await _execute_wf(workflow)
        logger.debug(
            "Node states: %s", [ni["state"] for ni in workflow["node_instances"]]
        )
        if not ran_at_least_one:
            ran_at_least_one = node_ran

        # TODO: move this to its own function, try_update_to_waiting_state or similar
        for ni in workflow["node_instances"]:
            logger.debug("Examining NI %s", ni["id"])
            if ni["state"] != "blocked":
                continue

            parent_ids = _parent_ids(ni)
            parents = _get_parent_nodes(parent_ids, workflow["node_instances"])
            if blocked_node_can_run(
                ni, parents, parent_ids, workflow["flowstate"]["state"]
            ):
                ni["state"] = "waiting"

    logger.debug("Ending execute_wf: %s", pformat(workflow))
    return ran_at_least_one
