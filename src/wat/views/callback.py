from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from wat.proc.exc import CallbackNoNodeFound
from wat.svc.workflow import callback as cb

from ..lib import context, depends

router = APIRouter()


@router.post("/cb/{ni_id}")
async def callback(ni_id: UUID, body: dict, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        try:
            return await cb(str(ni_id), body, tx)
        except CallbackNoNodeFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e


def init_app(app):
    app.include_router(router)
