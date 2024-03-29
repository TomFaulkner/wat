from __future__ import annotations

import uuid

import edgedb
import pydantic

# AUTOGENERATED FROM:
#     'queries/state_attributes_add.edgeql'
#     'queries/state_attributes_get_all.edgeql'
#     'queries/state_attributes_get_by_id.edgeql'
#     'queries/workflow_start_requirements_add.edgeql'
#     'queries/workflow_start_requirements_replace.edgeql'
# WITH:
#     $ edgedb-py --target async --file


class StateAttributesAddResult(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    type: str
    default_value: str | None = None


class WorkflowStartRequirementsAddResult(pydantic.BaseModel):
    id: uuid.UUID


async def state_attributes_add(
    executor: edgedb.AsyncIOExecutor,
    *,
    name: str,
    type: str,
    default_value: str,
) -> StateAttributesAddResult:
    return await executor.query_single(
        """\
        with new_attrib := (
          insert StateAttributes {
            name := <str>$name,
            type := <str>$type,
            default_value := <str>$default_value,
          }
        )
        select new_attrib {
          name,
          type,
          default_value,
        };\
        """,
        name=name,
        type=type,
        default_value=default_value,
    )


async def state_attributes_get_all(
    executor: edgedb.AsyncIOExecutor,
) -> list[StateAttributesAddResult]:
    return await executor.query(
        """\
        select StateAttributes {
          name,
          type,
          default_value
        }
        filter .active = <bool>true;\
        """,
    )


async def state_attributes_get_by_id(
    executor: edgedb.AsyncIOExecutor,
    *,
    id: uuid.UUID,
) -> StateAttributesAddResult | None:
    return await executor.query_single(
        """\
        select StateAttributes {
          name,
          type,
          default_value
        }
        filter .active = <bool>true and .id = <uuid>$id;\
        """,
        id=id,
    )


async def workflow_start_requirements_add(
    executor: edgedb.AsyncIOExecutor,
    *,
    id: uuid.UUID,
    state_ids: list[uuid.UUID],
) -> WorkflowStartRequirementsAddResult | None:
    return await executor.query_single(
        """\
        update Workflow
        filter .id = <uuid>$id
        set {
          start_requirements += (
            select detached StateAttributes
            filter .id in std::array_unpack(<array<uuid>>$state_ids)
          )
        }\
        """,
        id=id,
        state_ids=state_ids,
    )


async def workflow_start_requirements_replace(
    executor: edgedb.AsyncIOExecutor,
    *,
    id: uuid.UUID,
    state_ids: list[uuid.UUID],
) -> WorkflowStartRequirementsAddResult | None:
    return await executor.query_single(
        """\
        update Workflow
        filter .id = <uuid>$id
        set {
          start_requirements := (
            select detached StateAttributes
            filter .id in std::array_unpack(<array<uuid>>$state_ids)
          )
        }\
        """,
        id=id,
        state_ids=state_ids,
    )


class StateAttributesAdd(pydantic.BaseModel):
    name: str
    type: str
    default_value: str


class StateAttributesGetById(pydantic.BaseModel):
    id: uuid.UUID


class WorkflowStartRequirementsAdd(pydantic.BaseModel):
    id: uuid.UUID
    state_ids: list[uuid.UUID]


class WorkflowStartRequirementsReplace(pydantic.BaseModel):
    id: uuid.UUID
    state_ids: list[uuid.UUID]
