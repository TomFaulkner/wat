import logging
from typing import Any

import httpx

from wat.config import settings

logger = logging.getLogger(__name__)

url = f"{settings.dummy_hostname}/callback"
self = f"{settings.site_hostname}"


class APISendingException(ValueError):
    """Outbound API call returned a none 2xx/4xx code."""


async def execute(id_: str, config: dict[str, str], state: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{url}",
            json={
                "url": f"{self}/cb/{id_}",
                "body": {"snack": "ice cream"},
            },
        )
    j = r.json()
    match r.status_code:
        case 200:
            return "completed", {"post_response_url": r.json()["url"]}
        case 202:
            match config.get("hold_method"):
                case "callback":
                    return "waiting", {
                        id_: {"callback_count": 0, "obj_id": j["id"], "updates": []}
                    }
                case "polling":
                    return "polling", {f"{id_}": {"poll_count": 0, "obj_id": j["id"]}}
                case _:
                    return "completed", {"post_response_url": r.json()["url"]}
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
