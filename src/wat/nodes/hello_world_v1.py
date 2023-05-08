from typing import Any


async def execute(id_: str, config: dict[str, Any], state: dict[str, Any]):
    print(f"Hello {state['greeting_name']} {config}")
    return "completed", {}  # success, state updates
