from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel

Model = dict[str, tuple[str, Any]]


class Prompt(BaseModel):
    name: str
    model: Model


class ApiCall(BaseModel):
    url: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    hold_method: Literal["callback", "polling"] | None

    response_validation: Model | None
    body_validation: Model | None

    response_state_prefix: str | None


class Operand(str, Enum):
    eq = "eq"
    ne = "dne"
    gt = "gt"
    gte = "gte"
    lt = "lt"
    lte = "lte"


class OperandTypes(str, Enum):
    bool = "bool"
    int = "int"
    str = "str"


class Rules(BaseModel):
    op: Operand
    operand_1: str
    operand_2: str
    operand_types: OperandTypes


class Decision(BaseModel):
    strategy: Literal[
        "all",
        "any",
        # do i want these? then does op need to include math?
        # or maybe a decision math node
        # maybe even a decision switch/case node
        "sum",
        "diff",
    ]
    choices: dict[bool | int | str, int]
    rules: list[Rules]


class Config(BaseModel):
    prompt: Prompt | None
    model: Model | None
    api_call: ApiCall | None
    decision: Decision | None
