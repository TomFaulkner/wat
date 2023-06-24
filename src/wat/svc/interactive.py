import json
import logging
from functools import wraps
from typing import Any, TypedDict

import jwt
import pydantic

import wat.queries.lane_get_async_edgeql as lane
from wat.data import node, workflows
from wat.lib.pyd import ModelConfig, create_model_from_dict

logger = logging.getLogger(__name__)


class Token(pydantic.BaseModel):
    system: str
    system_identifier: str


class LaneException(Exception):
    pass


class LaneNotFound(LaneException):
    def __init__(self, error: str):
        super().__init__(error)


class LaneInvalidToken(LaneException):
    def __init__(self, error: str):
        super().__init__(error)


async def _check_lane_token(token: str | Token, tx):
    try:
        unverified = Token(**jwt.decode(token, options={"verify_signature": False}))
    except jwt.exceptions.DecodeError as e:
        raise LaneInvalidToken(error="Unparseable token.") from e

    logger.info(
        "Looking up Lane: %s: %s", unverified.system, unverified.system_identifier
    )
    try:
        db_lane = (
            await lane.lane_get(
                tx,
                system=unverified.system,
                system_identifier=unverified.system_identifier,
            )
        )[0]
    except IndexError:
        raise LaneNotFound(error="Lane Token not found.") from None
    return Token(**jwt.decode(token, db_lane.key.key, algorithms=["RS256"]))


def check_lane_token(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        t = await _check_lane_token(kwargs.pop("token"), kwargs["tx"])
        return await f(*args, token=t, **kwargs)

    return wrapper


def _ni_from_wf(wf, ni_id: str) -> dict[str, Any] | None:
    for ni in wf["node_instances"]:
        if str(ni["id"]) == ni_id:
            return ni


class NodeInstanceNotFound(ValueError):
    """Node Instance wasn't found"""


class InteractiveNodeMissingConfig(ValueError):
    """Interactive Node instance doesn't have a prompt."""


class NodeInstanceNotReady(ValueError):
    """Node Instance not in pending state"""


async def _get_wf_and_ni(ni_id: str, tx=None) -> tuple[dict, dict]:
    wf_id_obj = await node.get_node_instance_parent_workflow(ni_id, tx)
    if wf_id_obj is None:
        raise NodeInstanceNotFound
    wf = await workflows.get_by_id(str(wf_id_obj.workflow.id))
    ni = _ni_from_wf(wf, ni_id)
    if not ni:
        raise NodeInstanceNotFound
    if not ni["state"] == "pending":
        raise NodeInstanceNotReady
    return wf, ni


class NodeModelConfig(TypedDict):
    name: str
    model: ModelConfig


def _parse_prompt(node_config_model: NodeModelConfig):
    return create_model_from_dict(node_config_model["name"], node_config_model["model"])


@check_lane_token
async def fetch_ni_prompts(ni_id: str, token: str | Token = "", tx=None):
    _, ni = await _get_wf_and_ni(ni_id, tx)
    if ni["config"] != "{}":
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


@check_lane_token
async def get_next_interactive_node(
    wf_id: str, token: str | Token = "", tx=None
) -> str | None:
    wf = await workflows.get_by_id(wf_id)
    int_ni = _filter_for_interactive_nodes(wf["node_instances"])
    if not int_ni:
        return None
    return str(int_ni["id"])


@check_lane_token
async def post(ni_id: str, body: dict, token: str | Token = "", tx=None):
    wf, ni = await _get_wf_and_ni(ni_id, tx)
    obj = _parse_prompt(json.loads(ni["config"])["prompt"])(**body)
    await workflows.update_flow_state(str(wf["flowstate"]["id"]), obj.dict(), tx)
    await node.update_instance_state(ni_id, "completed", client=tx)
