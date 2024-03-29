# AUTOGENERATED FROM 'queries/state_attributes_add.edgeql' WITH:
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
class StateAttributesAddResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    type: str
    default_value: str | None


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


class StateAttributesAdd(pydantic.BaseModel):
    name: str
    type: str
    default_value: str
