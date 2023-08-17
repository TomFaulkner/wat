import logging
from typing import Any, Literal

import httpx

from wat.config import settings
from wat.lib.state import format_body
from wat.schemas.node_instance_config import SendBody

logger = logging.getLogger(__name__)

url = f"{settings.dummy_hostname}/callback"
self = f"{settings.site_hostname}"


class APISendingException(ValueError):
    """Outbound API call returned a none 2xx/4xx code."""


class APIResponseMissingField(ValueError):
    """API Response missing expected fields."""

    def __init__(self, fields: list[str]):
        super().__init__(f'API Response missing expected fields: {", ".join(fields)}')


def _response_conversion(
    response_body, response_format: Literal["json", "xml"] = "json"
) -> dict[str, Any]:
    if response_format == "json" or response_format is None:
        return response_body.json()
    return response_body  # handle xml or others


StateResponseKeyTranslations = dict[str, tuple[str, bool]]


def _state_response_translation(
    key_translations: StateResponseKeyTranslations, data: dict[str, Any]
) -> dict[str, Any]:
    """Translates response keys to desired name for state response.

    > _state_response_translation({'someName': ('new_name', True), {'someName': 5}})
    {'new_name': True}
    """
    response: dict[str, Any] = {}
    missing_keys: list[str] = []
    for k, (new_name, required) in key_translations.items():
        try:
            response[new_name] = data[k]
        except KeyError:
            if required:
                missing_keys.append(k)
        if missing_keys:
            raise APIResponseMissingField(fields=missing_keys)
    return response


def _response_handler(
    status_code: int,
    response_body: dict[str, Any],
    id_: str,
    key_translations: StateResponseKeyTranslations,
    hold_method: str | None,
) -> tuple[Literal["waiting", "completed", "polling"], dict[str, Any]]:
    match status_code:
        case 200 | 202:
            match hold_method:
                case "callback":
                    return "waiting", {
                        id_: {
                            "callback_count": 0,
                            "updates": [],
                        }
                    }
                case "polling":
                    return "polling", {f"{id_}": {"poll_count": 0, "updates": []}}
                case _:
                    return "completed", _state_response_translation(
                        key_translations, response_body
                    )
        # TODO: handle 4xx, 5xx
        case _ if 400 <= status_code <= 499:
            logger.error(
                "API call failed with code: %s and message: %s url: %s",
                status_code,
                response_body,
                url,
            )
            raise APISendingException()
        case _:
            raise APISendingException()


async def execute(id_: str, config: dict[str, Any], state: dict[str, Any]):
    body = format_body(SendBody(**config["api_call"]["send_body"]), state)

    async with httpx.AsyncClient() as client:
        r = await client.post(  # do POST/other via config as well
            f"{url}",
            # determine whether to send json= or body= body
            **{config["api_call"]["send_body_type"]: body},
        )
    response_body = _response_conversion(
        r, config.get("api_call", {}).get("response_body_type", "json")
    )

    return _response_handler(
        r.status_code,
        response_body,
        id_,
        config["api_call"]["response_body"]["key_translation"],
        config.get("hold_method"),
    )


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
