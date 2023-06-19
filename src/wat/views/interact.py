from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from wat.proc.exc import CallbackNoNodeFound
from wat.svc import interactive

from ..lib import context, depends

router = APIRouter()


@router.post("/i/{ni_id}")
async def interactive_post(ni_id: UUID, body: dict, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        try:
            return await interactive.post(str(ni_id), body, tx)
        except CallbackNoNodeFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e


@router.get("/i/{ni_id}")
async def interactive_get(ni_id: UUID, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        try:
            return await interactive.fetch_ni_prompts(str(ni_id), tx)
        except CallbackNoNodeFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e


@router.get("/i/{wf_id}/next")
async def next_interactive_get(wf_id: UUID, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        try:
            return await interactive.get_next_interactive_node(str(wf_id), tx)
        except CallbackNoNodeFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e


def init_app(app):
    app.include_router(router)
