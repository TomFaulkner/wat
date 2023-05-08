import logging
from datetime import datetime
from typing import Any
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from ..data import queries_async as q
from ..lib import context, depends
from ..svc import workflow

logger = logging.getLogger(__name__)

router = APIRouter()


class FlowState(BaseModel):
    state: dict
    created: datetime
    last_updated: datetime


class WorkflowCreate(BaseModel):
    template: bool = False
    template_active: bool = False


class StateAttributes(BaseModel):
    name: str
    type: str
    default_value: str | None


class Workflow(WorkflowCreate):
    id: UUID
    name: str | None
    version: int | None
    state: str
    flowstate: FlowState
    node_instances: Any
    start_requirements: list[StateAttributes]


@router.post("/workflows", response_model=Workflow)
async def post(workflow_: WorkflowCreate, tx=Depends(depends.edge_tx)) -> Workflow:
    start_state = "template" if workflow_.template else "waiting"
    wf = workflow_.dict() | {"state": start_state}
    return Workflow(**(await workflow.create(wf, tx)))


@router.get("/workflows/{wf_id}", response_model=Workflow)
async def get(wf_id: UUID) -> Workflow:
    with context.raise_data_errors():
        return Workflow(**(await workflow.get_by_id(wf_id)))


@router.get("/workflows", response_model=list[Workflow])
async def get_all(template_only=False, active_template_only=False) -> list[Workflow]:
    with context.raise_data_errors():
        workflows = await workflow.get(template_only, active_template_only)
        return [Workflow(**(wf)) for wf in workflows]


@router.post("/workflows/create_instance", response_model=Workflow)
async def instance(wf_id: UUID, tx=Depends(depends.edge_tx)) -> Workflow:
    with context.raise_data_errors():
        return await workflow.create_instance(wf_id, tx)


class StartAttributes(BaseModel):
    start: dict | None


@router.post("/workflows/create_and_run", response_model=Workflow)
async def car(wf_id: UUID, start: StartAttributes, tx=Depends(depends.edge_tx)):
    try:
        return await workflow.create_and_run(tx, str(wf_id), start.start)
    except workflow.NoStartState as e:
        raise HTTPException(
            422, f"This workflow requires starting attributes. {e.requirements}"
        ) from e
    except pydantic.error_wrappers.ValidationError as e:
        raise HTTPException(422, str(e)) from e


@router.put("/workflows/{wf_id}/flowstate", response_model=FlowState)
async def replace_flowstate(
    wf_id: UUID, new_state: dict, tx=Depends(depends.edge_tx)
) -> FlowState:
    with context.raise_data_errors():
        return await workflow.replace_flow_state(wf_id, new_state, tx)


@router.patch("/workflows/{wf_id}/flowstate", response_model=FlowState)
async def update_flowstate(
    wf_id: UUID, new_state: dict, tx=Depends(depends.edge_tx)
) -> FlowState:
    with context.raise_data_errors():
        return await workflow.update_flow_state(wf_id, new_state, tx)


@router.patch("/workflows/{wf_id}/start_requirements")
async def replace_start_requirements(
    wf_id: UUID, attribute_ids: list[UUID], tx=Depends(depends.edge_tx)
) -> None:
    with context.raise_data_errors():
        await q.workflow_start_requirements_replace(
            tx, id=wf_id, state_ids=attribute_ids
        )


@router.patch("/workflows/{wf_id}/start_requirements")
async def add_start_requirements(
    wf_id: UUID, attribute_ids: list[UUID], tx=Depends(depends.edge_tx)
) -> None:
    with context.raise_data_errors():
        await q.workflow_start_requirements_add(tx, id=wf_id, state_ids=attribute_ids)


def init_app(app):
    app.include_router(router)
