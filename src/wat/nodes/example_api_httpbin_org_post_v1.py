from typing import Any

import httpx

url = "https://httpbin.org/post"


async def execute(id_: str, config: dict[str, str], state: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={})
    return "completed" if r.status_code == 200 else "error", {
        "httpbin_post_response_url": r.json()["url"]
    }  # success, state updates
