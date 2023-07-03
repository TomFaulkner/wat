# AUTOGENERATED FROM 'queries/ingestion_get.edgeql' WITH:
#     $ edgedb-py --target async


from __future__ import annotations

import dataclasses
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
class IngestionGetResultWorkflowStartRequirementsItem(NoPydanticValidation):
    id: uuid.UUID
    name: str
    type: str
    default_value: str | None


@dataclasses.dataclass
class IngestionGetResultWorkflow(NoPydanticValidation):
    id: uuid.UUID
    start_requirements: list[IngestionGetResultWorkflowStartRequirementsItem]


@dataclasses.dataclass
class IngestionGetResult(NoPydanticValidation):
    id: uuid.UUID
    friendly_name: str
    workflow: IngestionGetResultWorkflow
    active: bool


async def ingestion_get(
    executor: edgedb.AsyncIOExecutor,
    *,
    friendly_name: str,
) -> list[IngestionGetResult]:
    return await executor.query(
        """\
        select IngestionRegistry {
          friendly_name,
          workflow :{
            id,
            start_requirements :{
              name,
              type,
              default_value
            }
          },
          active
        }
        filter .friendly_name = <str>$friendly_name;\
        """,
        friendly_name=friendly_name,
    )


class IngestionGet(pydantic.BaseModel):
    friendly_name: str
