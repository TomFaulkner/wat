from typing import Any


async def execute(config: dict[str, Any], state: dict[str, Any]):
    print(f"Hello {state['greeting_name']}")
    return True, {}  # success, state updates
