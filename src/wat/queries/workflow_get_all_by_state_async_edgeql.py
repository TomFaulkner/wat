# AUTOGENERATED FROM 'queries/workflow_get_all_by_state.edgeql' WITH:
#     $ edgedb-py --target async


from __future__ import annotations

import dataclasses
import datetime
import uuid

import edgedb
import pydantic


class NoPydanticValidation:
    @classmethod
    def __get_validators__(cls):
        from pydantic.dataclasses import dataclass as pydantic_dataclass

        pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class WorkflowGetAllByStateResultFlowstate(NoPydanticValidation):
    id: uuid.UUID
    state: str
    created: datetime.datetime | None
    last_updated: datetime.datetime | None


@dataclasses.dataclass
class WorkflowGetAllByStateResultIngestionItem(NoPydanticValidation):
    id: uuid.UUID
    friendly_name: str
    active: bool


@dataclasses.dataclass
class WorkflowGetAllByStateResultNodeInstancesItemNode(NoPydanticValidation):
    id: uuid.UUID
    name: str
    version: int
    config: str
    base: str
    type: str | None


@dataclasses.dataclass
class WorkflowGetAllByStateResultNodeInstancesItemParentsItem(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class WorkflowGetAllByStateResultNodeInstancesItemWorkflow(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class WorkflowGetAllByStateResultNodeInstancesItem(NoPydanticValidation):
    id: uuid.UUID
    state: str
    parents: list[WorkflowGetAllByStateResultNodeInstancesItemParentsItem]
    children: list[WorkflowGetAllByStateResultNodeInstancesItemParentsItem]
    sequence: int | None
    depends: int
    depends_on: list[WorkflowGetAllByStateResultNodeInstancesItemParentsItem]
    required_state: list[str] | None
    config: str | None
    node: WorkflowGetAllByStateResultNodeInstancesItemNode
    workflow: WorkflowGetAllByStateResultNodeInstancesItemWorkflow


@dataclasses.dataclass
class WorkflowGetAllByStateResultStartRequirementsItem(NoPydanticValidation):
    id: uuid.UUID
    name: str
    type: str
    default_value: str | None


@dataclasses.dataclass
class WorkflowGetAllByStateResult(NoPydanticValidation):
    id: uuid.UUID
    name: str | None
    version: int | None
    template: bool | None
    template_active: bool | None
    ingestion: list[WorkflowGetAllByStateResultIngestionItem]
    locations: str | None
    state: str
    flowstate: WorkflowGetAllByStateResultFlowstate | None
    start_requirements: list[WorkflowGetAllByStateResultStartRequirementsItem]
    node_instances: list[WorkflowGetAllByStateResultNodeInstancesItem]


async def workflow_get_all_by_state(
    executor: edgedb.AsyncIOExecutor,
    *,
    state: str,
) -> list[WorkflowGetAllByStateResult]:
    return await executor.query(
        """\
        select Workflow {
            id,
            name,
            version,
            template,
            template_active,
            ingestion :{ friendly_name, active },
            locations,

            state,
            flowstate :{ state, created, last_updated },
            start_requirements :{ name, type, default_value },

            node_instances :{
              state,
              parents,
              children,
              sequence,
              depends,
              depends_on,
              required_state,
              config,
              node :{
                name,
                version,
                config,
                base,
                type
              },
              workflow,
            },
        } filter .state = <str>$state;\
        """,
        state=state,
    )


class WorkflowGetAllByState(pydantic.BaseModel):
    state: str
