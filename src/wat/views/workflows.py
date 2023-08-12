import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

import pydantic
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from wat.lib.edge import obj_to_dict
from wat.queries import workflow_get_by_id_async_edgeql as qwf_by_id
from wat.queries import workflow_get_templates_async_edgeql as q_templates
from wat.queries.state_attributes_get_list_async_edgeql import (
    state_attributes_get_list as attribs_list,
)

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
    default_value: str | None = None


class Ingestion(BaseModel):
    friendly_name: str
    active: bool


class Workflow(WorkflowCreate):
    id: UUID
    name: str | None = None
    version: int | None = None
    locations: dict[str, dict[str, int]] | None
    ingestion: Ingestion
    state: str
    flowstate: FlowState
    node_instances: Any = None
    start_requirements: list[StateAttributes]


class InvalidStartRequirements(ValueError):
    """Start Requirements included invalid uuids."""

    def __init__(self, not_found: set):
        self.missing = [str(nf) for nf in not_found]
        super().__init__(f"Start requirements weren't found: {self.missing}")


async def create(wf: dict, tx) -> workflow.q.WorkflowAddResult:
    start_state = "template" if wf["template"] else "waiting"
    wf["state"] = start_state
    res = await workflow.q.workflow_add(tx, **wf)
    if wf["start_requirements"]:
        # and not res.start_requirements:
        attribs = await attribs_list(tx, start_requirements=wf["start_requirements"])
        if len(attribs) != len(wf["start_requirements"]):
            diff = set(wf["start_requirements"]).difference(set(attribs))
            raise InvalidStartRequirements(not_found=diff)
    return res


@router.post("/workflows", response_model=workflow.q.WorkflowAddResult)
async def post(
    workflow_: workflow.q.WorkflowAdd, tx=Depends(depends.edge_tx)
) -> workflow.q.WorkflowAddResult:
    try:
        return await create(workflow_.dict(), tx)
    except InvalidStartRequirements as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "One or more Start Requirement Attributes "
                f"were not found. {e.missing}",
            ),
        ) from e


@router.get("/workflows/{wf_id}", response_model=qwf_by_id.WorkflowGetByIdResult)
async def get(wf_id: UUID, tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        res = await qwf_by_id.workflow_get_by_id(tx, id=wf_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=("Workflow not found."),
            )
        result = obj_to_dict(res)
        if res.locations:
            result["locations"] = json.loads(res.locations)
        else:
            result["locations"] = {}
        return result


@router.get("/workflows/{wf_id}/graph", response_model=dict)
async def get_graph(wf_id: UUID):
    from graphlib import TopologicalSorter

    with context.raise_data_errors():
        wf = Workflow(**(await workflow.get_by_id(str(wf_id))))
        graph = {
            str(ni["id"]): {str(c["id"]) for c in ni["parents"]}
            for ni in wf.node_instances
        }
        ts = TopologicalSorter(graph)
        g = tuple(ts.static_order())
        instances = {str(ni["id"]): ni for ni in wf.node_instances}
        graph_with_details = {
            ni: {"state": instances[ni]["state"], "name": instances[ni]["node"]["name"]}
            for ni in g
        }

        return graph_with_details


@router.get("/workflows", response_model=list[Workflow])
async def get_all(template_only=False, active_template_only=False) -> list[Workflow]:
    with context.raise_data_errors():
        workflows = await workflow.get(template_only, active_template_only)
        return [Workflow(**(wf)) for wf in workflows]


@router.get(
    "/workflows_by_state",
    response_model=workflow.qwf_by_state.WorkflowGetAllByStateResult,
)
async def get_all_by_state(state: str = "template", tx=Depends(depends.edge_tx)):
    return await workflow.get_by_state(state, tx)


@router.get(
    "/workflow_templates", response_model=q_templates.WorkflowGetTemplatesResult
)
async def templates(tx=Depends(depends.edge_tx)):
    with context.raise_data_errors():
        return await q_templates.workflow_get_templates(tx)


@router.post("/workflows/create_instance", response_model=UUID)
async def instance(wf_id: UUID, tx=Depends(depends.edge_tx)) -> UUID:
    with context.raise_data_errors():
        return await workflow.create_instance(str(wf_id), tx)


class StartAttributes(BaseModel):
    start: dict | None = None


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


@router.post("/workflows/{wf_id}/enqueue")
async def enqueue_wf(wf_id: UUID):
    await workflow.enqueue_wf(str(wf_id))


@router.put("/workflows/{wf_id}/locations", response_model=bool)
async def update_locations(
    wf_id: UUID, update: workflow.Locations, tx=Depends(depends.edge_tx)
) -> bool:
    return await workflow.update_locations(wf_id, update, tx)


def init_app(app):
    app.include_router(router)
