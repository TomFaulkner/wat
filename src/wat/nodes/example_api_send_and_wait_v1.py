import logging
from typing import Any

import httpx

from wat.config import settings

logger = logging.getLogger(__name__)

url = f"{settings.dummy_hostname}/callback"


class APISendingException(ValueError):
    """Outbound API call returned a none 2xx/4xx code."""


async def execute(id_: str, config: dict[str, str], state: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{url}",
            json={
                "url": f"{url}/cb/{id_}",
                "body": {"snack": "ice cream"},
            },
        )
    j = r.json()
    match r.status_code:
        case 200:
            return "completed", {"httpbin_post_response_url": r.json()["url"]}
        case 202:
            return "waiting", {
                id_: {"callback_count": 0, "obj_id": j["id"], "updates": []}
            }
        case _ if 400 <= r.status_code <= 499:
            logger.error(
                "API call failed with code: %s and message: %s url: %s",
                r.status_code,
                r.text,
                url,
            )
            raise APISendingException()
        case _:
            raise APISendingException()


class APICallbackException(ValueError):
    """The API return data lacked expected fields."""


async def callback(
    id_: str, config: dict[str, str], state: dict[str, Any], data: dict
) -> tuple[str, dict]:
    logger.debug("Received state: %s", state)
    data_state = state[id_]
    data_state["obj_id"]

    match data["complete"]:
        case True:
            return "completed", {"snack": data["snack"]}
        case False:
            return (
                "waiting",
                {
                    id_: data_state
                    | {
                        "callback_count": state[id_]["callback_count"] + 1,
                        "updates": state[id_]["updates"].append(data),
                    }
                },
            )
        case _:
            raise APICallbackException()
