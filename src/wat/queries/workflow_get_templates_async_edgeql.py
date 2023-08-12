# AUTOGENERATED FROM 'queries/workflow_get_templates.edgeql' WITH:
#     $ edgedb-py --target async


from __future__ import annotations

import dataclasses
import datetime
import uuid

import edgedb


class NoPydanticValidation:
    @classmethod
    def __get_validators__(cls):
        from pydantic.dataclasses import dataclass as pydantic_dataclass

        pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class WorkflowGetTemplatesResultFlowstate(NoPydanticValidation):
    id: uuid.UUID
    state: str
    created: datetime.datetime | None
    last_updated: datetime.datetime | None


@dataclasses.dataclass
class WorkflowGetTemplatesResultIngestionItem(NoPydanticValidation):
    id: uuid.UUID
    friendly_name: str
    active: bool


@dataclasses.dataclass
class WorkflowGetTemplatesResultNodeInstancesItemNode(NoPydanticValidation):
    id: uuid.UUID
    name: str
    version: int
    config: str
    base: str
    type: str | None


@dataclasses.dataclass
class WorkflowGetTemplatesResultNodeInstancesItemParentsItem(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class WorkflowGetTemplatesResultNodeInstancesItemWorkflow(NoPydanticValidation):
    id: uuid.UUID


@dataclasses.dataclass
class WorkflowGetTemplatesResultNodeInstancesItem(NoPydanticValidation):
    id: uuid.UUID
    state: str
    parents: list[WorkflowGetTemplatesResultNodeInstancesItemParentsItem]
    children: list[WorkflowGetTemplatesResultNodeInstancesItemParentsItem]
    sequence: int | None
    depends: int
    depends_on: list[WorkflowGetTemplatesResultNodeInstancesItemParentsItem]
    required_state: list[str] | None
    config: str | None
    node: WorkflowGetTemplatesResultNodeInstancesItemNode
    workflow: WorkflowGetTemplatesResultNodeInstancesItemWorkflow


@dataclasses.dataclass
class WorkflowGetTemplatesResultStartRequirementsItem(NoPydanticValidation):
    id: uuid.UUID
    name: str
    type: str
    default_value: str | None


@dataclasses.dataclass
class WorkflowGetTemplatesResult(NoPydanticValidation):
    id: uuid.UUID
    name: str | None
    version: int | None
    template: bool | None
    template_active: bool | None
    ingestion: list[WorkflowGetTemplatesResultIngestionItem]
    state: str
    flowstate: WorkflowGetTemplatesResultFlowstate | None
    start_requirements: list[WorkflowGetTemplatesResultStartRequirementsItem]
    node_instances: list[WorkflowGetTemplatesResultNodeInstancesItem]


async def workflow_get_templates(
    executor: edgedb.AsyncIOExecutor,
) -> list[WorkflowGetTemplatesResult]:
    return await executor.query(
        """\
        select Workflow {
            id,
            name,
            version,
            template,
            template_active,
            ingestion :{ friendly_name, active },

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
        } filter .template = true and .template_active = true;\
        """,
    )
