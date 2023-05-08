from typing import Any

import httpx

url = "http://127.0.0.1:8001/pollable"


async def execute(id_: str, config: dict[str, str], state: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{url}?count=2", json={})
    match r.status_code:
        case 200:
            return "completed", {
                "httpbin_post_response_url": r.json()["url"]
            }  # success, state updates
        case 202:
            return "polling", {f"{id_}_poll_count": 0}


async def poll(
    id_: str, config: dict[str, str], state: dict[str, Any]
) -> tuple[str, dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{url}/{id_}")

    if r.status_code != 200:
        return "error", {}

    res = r.json()
    match res["complete"]:
        case True:
            return "completed", {}
        case False:
            return (
                "polling",
                {f"{id_}_poll_count": state.get(f"{id_}_poll_count", 0) + 1},
            )
