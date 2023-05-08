from fastapi import APIRouter, Depends

from ..lib import depends
from ..svc import workflow

router = APIRouter()


@router.post("/manual_exec")
async def manual_exec(wf_id: str, tx=Depends(depends.edge_tx)):
    return await workflow.execute_workflow(wf_id, suppress_updates=True, tx=tx)


def init_app(app):
    app.include_router(router)
