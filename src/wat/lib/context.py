import logging
from contextlib import asynccontextmanager, contextmanager

import edgedb
from fastapi import HTTPException, status

from ..db import inject_client

logger = logging.getLogger(__name__)


no_results_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="No result found.",
)

multiple_results_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="An error occurred, multiple results found for a single item query.",
)


@contextmanager
def raise_data_errors():
    try:
        yield
    except edgedb.NoDataError as e:
        logger.error(str(e))  # noqa: TRY400 use logger.exception
        raise no_results_exception
    except edgedb.ResultCardinalityMismatchError as e:
        logger.error(str(e))  # noqa: TRY400 use logger.exception
        raise multiple_results_exception


@asynccontextmanager
@inject_client
async def edge_tx(client: edgedb.AsyncIOClient):
    """Yields an EdgeDB atomic transaction.
    Prefer depends.edge_tx if doing atomic transactions in a view.
    """
    async for tx in client.transaction():
        async with tx:
            yield tx
