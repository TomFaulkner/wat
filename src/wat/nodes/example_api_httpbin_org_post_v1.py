from typing import Any

import httpx

url = "https://httpbin.org/post"


async def execute(config: dict[str, str], state: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={})
    return r.status_code == 200, {
        "httpbin_post_response_url": r.json()["url"]
    }  # success, state updates
