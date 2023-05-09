from uuid import UUID

from fastapi import APIRouter, Depends

from wat.svc.workflow import callback as cb

from ..lib import context, depends

router = APIRouter()


@router.post("/cb/{ni_id}")
async def callback(ni_id: UUID, body: dict, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        return await cb(str(ni_id), body, tx)


def init_app(app):
    app.include_router(router)
