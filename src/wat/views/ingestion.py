import pydantic
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from wat.queries import ingestion_create_async_edgeql as qcreate
from wat.queries import ingestion_get_async_edgeql as qget
from wat.svc import workflow

from ..lib import context, depends

router = APIRouter()


class Ingestion(BaseModel):
    friendly_name: str
    workflow_id: str
    active: bool


@router.get("/ir/{name}", response_model=qget.IngestionGetResult)
async def get(name: str, tx=Depends(depends.edge_tx)) -> qget.IngestionGetResult:
    return (await qget.ingestion_get(tx, friendly_name=name))[0]


@router.post("/ir", response_model=qcreate.IngestionCreateResult)
async def create(
    body: qcreate.IngestionCreate, tx=Depends(depends.edge_tx)
) -> qcreate.IngestionCreateResult:
    return await qcreate.ingestion_create(tx, **body.dict())


class StartAttributes(BaseModel):
    start: dict


@router.post("/ir/{name}", response_model=qget.IngestionGetResult)
async def instance(
    name: str,
    start: StartAttributes,
    background_tasks: BackgroundTasks,
    queue: bool = True,
    tx=Depends(depends.edge_tx),
):
    with context.raise_data_errors():
        ir_lookup = (await qget.ingestion_get(tx, friendly_name=name))[0]
        wf = await workflow.create_instance(str(ir_lookup.workflow.id), tx)
        try:
            start_attributes = workflow.validate_workflow(wf, start.start)
        except workflow.NoStartState as e:
            raise HTTPException(
                422, f"This workflow requires starting attributes. {e.requirements}"
            ) from e
        except pydantic.ValidationError as e:
            raise HTTPException(422, str(e)) from e
        await workflow.update_flow_state(wf, start_attributes, tx)
        if queue:
            background_tasks.add_task(workflow.enqueue_wf, str(wf["id"]))
        return await workflow.get_by_id(wf["id"], tx=tx)


def init_app(app):
    app.include_router(router)
