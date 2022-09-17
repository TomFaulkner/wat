import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, ParamSpec, TypeVar

import edgedb
from edgedb import AsyncIOClient, create_async_client
from fastapi.encoders import jsonable_encoder
from pydantic import json

client: AsyncIOClient = None


async def create_pool() -> None:
    global client
    client = create_async_client(
        # host=settings.EDGEDB_HOST,
        # database=settings.EDGEDB_DB,
        # user=settings.EDGEDB_USER,
    )


async def get_client() -> AsyncGenerator[AsyncIOClient, None]:
    yield client


@asynccontextmanager
async def client_context() -> AsyncGenerator[AsyncIOClient, None]:
    try:
        yield client
    finally:
        pass


_P = ParamSpec("_P")
_R = TypeVar("_R")


def inject_client(func: Callable[_P, _R]) -> Callable[_P, _R]:
    def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        return func(*args, client=client, **kwargs)

    return wrapper


def _encode_obj(obj):
    answer = {}
    for attr in dir(obj):
        val = getattr(obj, attr)
        answer[attr] = jsonable_encoder(val)
    return answer


def _encode_set(obj):
    return [jsonable_encoder(x) for x in obj]


json.ENCODERS_BY_TYPE[uuid.UUID] = lambda obj: str(obj)
json.ENCODERS_BY_TYPE[edgedb.Set] = _encode_set
json.ENCODERS_BY_TYPE[edgedb.Object] = _encode_obj
