from contextlib import contextmanager
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from wat.svc import interactive

from ..lib import context, depends

router = APIRouter()


@contextmanager
def raise_lane_errors():
    try:
        yield
    except interactive.LaneException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    except interactive.NodeInstanceNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node Instance not found."
        ) from e
    except interactive.NodeInstanceNotReady as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node Instance not in pending state.",
        ) from e
    except interactive.InteractiveNodeMissingConfig as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Node Instance config is unprocessable.",
        ) from e


@router.post("/i/{ni_id}")
async def interactive_post(
    ni_id: UUID, body: dict, token: str, tx=Depends(depends.edge_tx)
):
    with context.raise_data_errors(), raise_lane_errors():
        return await interactive.post(str(ni_id), body, token=token, tx=tx)


@router.get("/i/{ni_id}")
async def interactive_get(ni_id: UUID, token: str, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors(), raise_lane_errors():
        return await interactive.fetch_ni_prompts(str(ni_id), token=token, tx=tx)


@router.get("/i/{wf_id}/next")
async def next_interactive_get(wf_id: UUID, token: str, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors(), raise_lane_errors():
        return await interactive.get_next_interactive_node(
            str(wf_id), token=token, tx=tx
        )


def init_app(app):
    app.include_router(router)
