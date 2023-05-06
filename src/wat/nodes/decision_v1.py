from typing import Any

from .decision import make_decision


async def execute(config: dict[str, Any], state: dict[str, Any]) -> tuple[int, dict]:
    return make_decision(config, state), {}
