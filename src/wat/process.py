import logging
from importlib import import_module
from pprint import pformat
from typing import Any

logger = logging.getLogger(__name__)


async def _execute_wf(wf):
    node_ran = False
    for instance in wf["node_instances"]:
        if instance["state"] == "waiting":
            match instance["node"]["base"]:
                case "action":
                    module_name = (
                        f"{instance['node']['name']}_v{instance['node']['version']}"
                    )
                    try:
                        success, state_update = await _execute_action_node(
                            instance, wf["flowstate"]["state"], module_name
                        )
                    except Exception as e:
                        instance["state"] = "error"
                        logger.exception(
                            "Workflow (%s:%s) failed to run %s: %s",
                            wf["id"],
                            instance["id"],
                            module_name,
                            str(e),
                        )
                        continue

                    if success:
                        wf["flowstate"]["state"].update(state_update)
                        instance["state"] = "completed"
                        node_ran = True
                case "decision":
                    # node already knows its children
                    # but, per workflow how does a decision node know which child is
                    # which?
                    # this could be based on array index, assuming the node
                    # instances are always copied in same order
                    # above doesn't work because parents don't know their children
                    # do i need a new field for decision nodes to know their children?
                    # cancel child node that wasn't among the elect
                    pass
                case "start":
                    instance["state"] = "completed"
                    wf["state"] = "started"
                case "finish":
                    instance["state"] = "completed"
                    wf["state"] = "completed"
    return node_ran


async def _execute_action_node(
    node_instance, state, module_name
) -> tuple[bool, dict[str, Any]]:
    module = import_module(f"wat.nodes.{module_name}")
    return await module.execute(node_instance["node"]["config"], state)


async def execute_wf(workflow):
    logger.debug(workflow)

    node_ran = True

    ran_at_least_one = False
    while node_ran and _has_available_instance(workflow["node_instances"]):
        logger.debug(pformat(workflow))
        node_ran = await _execute_wf(workflow)
        if not ran_at_least_one:
            ran_at_least_one = node_ran
        for ni in workflow["node_instances"]:
            if not ni["state"] == "blocked":
                continue
            parent_ids = _parent_ids(ni)
            parents = _get_parent_nodes(parent_ids, workflow["node_instances"])
            if blocked_node_can_run(ni, parents, parent_ids):
                ni["state"] = "waiting"

    logger.debug(pformat(workflow))
    return ran_at_least_one


def _has_available_instance(node_instances):
    return any(ni for ni in node_instances if ni["state"] in ("waiting", "blocked"))


def blocked_node_can_run(node, parents, parent_ids) -> bool:
    completed_parents = [p for p in parents if p["state"] == "completed"]
    if not len(completed_parents) >= node["depends"]:
        return False

    completed_ids = {cp["id"] for cp in completed_parents}
    depends_ids = {cp["id"] for cp in node["depends_on"]}
    if not completed_ids >= depends_ids:
        return False

    return True


def _get_parent_nodes(parent_ids, node_instances):
    return [p for p in node_instances if p["id"] in parent_ids]


def _parent_ids(node):
    return {p["id"] for p in node["parents"]}
