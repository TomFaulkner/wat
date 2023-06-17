import asyncio
import logging

from arq import create_pool
from arq.connections import RedisSettings
from edgedb import create_async_client
from httpx import AsyncClient

from wat.svc.workflow import start_workflow_arq


async def download_content(ctx, url):
    session: AsyncClient = ctx["session"]
    response = await session.get(url)
    print(f"{url}: {response.text:.80}...")
    return len(response.text)


async def startup(ctx):
    logging.basicConfig(
        format="%(levelname)s: %(module)s:%(lineno)d: %(message)s", level=logging.DEBUG
    )
    ctx["session"] = AsyncClient()
    ctx["edge_client"] = create_async_client()


async def shutdown(ctx):
    await ctx["session"].aclose()


async def main():
    redis = await create_pool(RedisSettings())

    for url in ("https://facebook.com", "https://microsoft.com", "https://github.com"):
        await redis.enqueue_job("test", url)


# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings,
# see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [
        download_content,
        start_workflow_arq,
    ]  # must restart worker for this to work
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings()
    log_results = True


if __name__ == "__main__":
    asyncio.run(main())
