"""
Decision making functionality.

See make_decision.
"""
import logging
from copy import deepcopy
from typing import Any

import jinja2

from wat.schemas.node_instance_config import Config as C

logger = logging.getLogger(__name__)


Config = dict[str, Any]


class InvalidOperator(ValueError):
    def __init__(self, op: str):
        super().__init__(f"{op} is not a valid operator")


def _op_bool(op: str, one: Any, two: Any) -> bool:
    match op:
        case "eq":
            return one == two
        case "dne":
            return one != two
        case "lt":
            return one < two
        case "lte":
            return one <= two
        case "gt":
            return one > two
        case "gte":
            return one >= two
    raise InvalidOperator(op)


def _parse_state(
    state_line: str, state: dict[str, Any]
) -> str:  # add other sources for data if necessary
    template = jinja2.Template(state_line)
    res = template.render(state=state)
    logger.debug("Parsing %s with result %s using state: %s", state_line, res, state)
    return res


def _pull_from_state(state: dict[str, Any], rule: dict[str, Any]):
    types = {
        "str": str,
        "int": int,
        "bool": bool,
    }
    for operand in ("operand_1", "operand_2"):
        if isinstance(rule[operand], str):
            parsed = _parse_state(rule[operand], state)
            rule[operand] = types[rule["operand_types"]](parsed)
    return rule


class InvalidStrategy(ValueError):
    def __init__(self, strategy: str):
        super().__init__(f"{strategy} is not a valid strategy.")


class ChoicesMustMatchStrategy(ValueError):
    """For a boolean [any|all] operation choices must be True and False"""


def _decide(
    config: Config,
) -> int:
    match config["decision"]["strategy"]:
        case "any" | "all":
            logger.debug("Decision based on any/all boolean")
            if not set(config["decision"]["choices"]) == {True, False}:
                raise ChoicesMustMatchStrategy()

            result = {"any": any, "all": all}[config["decision"]["strategy"]](
                [
                    _op_bool(r["op"], r["operand_1"], r["operand_2"])
                    for r in config["decision"]["rules"]
                ]
            )
            return config["decision"]["choices"][result]

        case "sum" | "diff":
            raise NotImplementedError()

    raise InvalidStrategy(config["decision"]["strategy"])


def make_decision(config: Config, state: dict[str, Any]) -> int:
    # TODO: maybe take both configs and merge them here, node | node_instance
    C(**config)
    config = deepcopy(config)
    config["decision"]["rules"] = [
        _pull_from_state(state, rule) for rule in config["decision"]["rules"]
    ]
    return _decide(config)
