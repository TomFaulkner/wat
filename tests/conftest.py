import asyncio
import os
from collections.abc import Generator
from contextlib import suppress
from pathlib import Path

import edgedb
import pytest
from httpx import AsyncClient


class RollbackTransaction(Exception):
    """Just here to rollback edgedb transactions."""


def _drop_db():
    try:
        db_client = edgedb.create_client()
        db_client.execute("DROP DATABASE _test")
    finally:
        db_client.close()


def _create_db():
    creation_db_client = edgedb.create_client()
    try:
        with suppress(edgedb.errors.UnknownDatabaseError):
            _drop_db()
        creation_db_client.execute("CREATE DATABASE _test;")
    finally:
        creation_db_client.close()
        del creation_db_client
    edgedb.create_client(database="_test").query("select 3.14")


def _migrate_db():
    try:
        db_client = edgedb.create_client()
        for migration_file in os.listdir("dbschema/migrations"):
            with Path(f"dbschema/migrations/{migration_file}").open() as f:
                migration_body = f.read()
                db_client.execute(migration_body)
    finally:
        db_client.close()


@pytest.fixture
def settings():
    from wat.depends import get_settings

    return get_settings()


@pytest.fixture
def db():
    try:
        # _create_db()
        # _migrate_db()

        yield
    finally:
        # _drop_db()
        pass


@pytest.fixture
async def tx(db):
    with suppress(RollbackTransaction):
        client = edgedb.create_async_client()
        try:
            async for tx in client.transaction():
                async with tx:
                    yield tx
            # abstract raise to an inner function
            raise RollbackTransaction()  # noqa: TRY301
        finally:
            with suppress(Exception):
                await client.aclose()


@pytest.fixture
async def app():
    from wat.main import get_app

    return get_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def client_auth(client):
    # TODO: fill this in when the time comes
    yield client


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
