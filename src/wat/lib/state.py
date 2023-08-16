from typing import Any

from wat.schemas.node_instance_config import SendBody


class MissingTranslation(ValueError):
    """A translation key was missing."""

    def __init__(self, missing: list[str]):
        super().__init__(
            f"Keys were missing in state key translation: {', '.join(missing)}"
        )


class MissingBodyStateKeys(ValueError):
    """A translation key was missing."""

    def __init__(self, missing: set[str]):
        super().__init__(
            f"Keys were missing in body state requirements: {', '.join(missing)}"
        )


State = dict[str, Any]


def _key_translation(key_translation: dict[str, str], state: State) -> State:
    results: State = {}
    missing = []
    for state_name, rename in key_translation.items():
        try:
            results[rename] = state[state_name]
        except KeyError:
            missing.append(state_name)
    if missing:
        raise MissingTranslation(missing=missing)
    return results


def filter_state(state: State, keys: set[str]) -> State:
    if not set(state).issuperset(keys):
        raise MissingBodyStateKeys(missing=keys.difference(set(state)))
    return {k: v for k, v in state.items() if k in keys}


def process_state(config_send_body: SendBody, state: State):
    if config_send_body.state_vars:
        state = filter_state(state, set(config_send_body.state_vars))
        if config_send_body.key_translation:
            return _key_translation(config_send_body.key_translation, state)
        else:
            return state
    return {}


def format_body(config_send_body: SendBody, state: State):
    send_state = process_state(config_send_body, state)
    match config_send_body.body_format:
        case "json":
            return send_state

        case "xml":
            # TODO: handle xml
            pass

        case "jinja":
            # TODO: handle jinja templates
            # uses send_body.template
            pass
