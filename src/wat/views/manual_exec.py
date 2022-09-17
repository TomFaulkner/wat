from fastapi import APIRouter

from ..svc import workflow

router = APIRouter()


@router.post("/manual_exec")
async def manual_exec(wf_id: str):
    return await workflow.execute_workflow(wf_id, suppress_updates=True)


def init_app(app):
    app.include_router(router)
