import logging
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..lib import context, depends
from ..svc import workflow

router = APIRouter()


# not currently used, delete?
class States(str, Enum):
    started: "started"
    cancelled: "cancelled"
    completed: "completed"
    error: "error"
    waiting: "waiting"
    template: "template"


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
    default_value: str


class StartRequirements(BaseModel):
    attribs: list[StateAttributes]


class Workflow(WorkflowCreate):
    id: UUID
    state: str
    flowstate: FlowState
    node_instances: Any
    start_requirements: StartRequirements | None


@router.post("/workflows", response_model=Workflow)
async def post(workflow_: WorkflowCreate, tx=Depends(depends.edge_tx)) -> Workflow:
    start_state = "template" if workflow_.template else "waiting"
    wf = workflow_.dict() | {"state": start_state}
    return Workflow(**(await workflow.create(wf, tx)))


@router.get("/workflows/{wf_id}", response_model=Workflow)
async def get(wf_id: UUID) -> Workflow:
    with context.raise_data_errors():
        return Workflow(**(await workflow.get_by_id(wf_id)))


logger = logging.getLogger(__name__)


@router.get("/workflows", response_model=list[Workflow])
async def get_all(template_only=False, active_template_only=False) -> list[Workflow]:
    with context.raise_data_errors():
        workflows = await workflow.get(template_only, active_template_only)
        return [Workflow(**(wf)) for wf in workflows]


@router.post("/workflows/create_instance", response_model=Workflow)
async def instance(wf_id: UUID, tx=Depends(depends.edge_tx)) -> Workflow:
    with context.raise_data_errors():
        return await workflow.create_instance(wf_id, tx)


@router.post("/workflows/create_and_run", response_model=Workflow)
async def car(wf_id: UUID, tx=Depends(depends.edge_tx)):
    return await workflow.create_and_run(str(wf_id), tx=tx)


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


def init_app(app):
    app.include_router(router)
