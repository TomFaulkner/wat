import logging
import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import ParamSpec, TypeVar

import edgedb
from edgedb import AsyncIOClient, create_async_client
from fastapi.encoders import jsonable_encoder
from pydantic import json

client: AsyncIOClient | None = None

logger = logging.getLogger(__name__)


async def create_pool() -> None:
    global client
    client = create_async_client()
    if not client:
        logger.critical("Can't connect to Database!")
    return client


async def get_client() -> AsyncGenerator[AsyncIOClient, None]:
    global client
    if not client:
        client = await create_pool()
    yield client


class NoClientError(AttributeError):
    """Client is None. This shouldn't happen."""


@asynccontextmanager
async def client_context() -> AsyncGenerator[AsyncIOClient, None]:
    try:
        global client
        if not client:
            client = await create_pool()
            if client is None:
                raise NoClientError  # noqa: TRY301  raise inside try/except
        yield client
    finally:
        pass


_P = ParamSpec("_P")
_R = TypeVar("_R")


def inject_client(func: Callable[_P, _R]) -> Callable[_P, _R]:
    def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        if "client" not in kwargs:
            return func(*args, client=client, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def _encode_obj(obj):
    answer = {}
    for attr in dir(obj):
        val = getattr(obj, attr)
        answer[attr] = jsonable_encoder(val)
    return answer


def _encode_set(obj):
    return [jsonable_encoder(x) for x in obj]


def _encode_array(obj):
    return [i for i in obj]


json.ENCODERS_BY_TYPE[uuid.UUID] = lambda obj: str(obj)
json.ENCODERS_BY_TYPE[edgedb.Set] = _encode_set
json.ENCODERS_BY_TYPE[edgedb.Object] = _encode_obj
json.ENCODERS_BY_TYPE[edgedb.Array] = _encode_array
