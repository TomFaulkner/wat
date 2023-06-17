import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

url = "http://127.0.0.1:8001/pollable"


async def execute(id_: str, config: dict[str, str], state: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{url}?count=2", json={})
    j = r.json()
    match r.status_code:
        case 200:
            return "completed", {
                "httpbin_post_response_url": r.json()["url"]
            }  # success, state updates
        case 202:
            return "polling", {f"{id_}": {"poll_count": 0, "obj_id": j["id"]}}


async def poll(
    id_: str, config: dict[str, str], state: dict[str, Any]
) -> tuple[str, dict]:
    logger.debug("Received state: %s", state)
    data_state = state[id_]
    obj_id = data_state["obj_id"]

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{url}/{obj_id}")

    if r.status_code != 200:
        return "error", {}

    res = r.json()
    match res["complete"]:
        case True:
            return "completed", {}
        case False:
            return (
                "polling",
                {id_: data_state | {"poll_count": state[f"{id_}"]["poll_count"] + 1}},
            )
        case _:
            raise ValueError()
