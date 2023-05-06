from typing import Any

from edgedb import AsyncIOClient

from ..db import inject_client
from ..lib import edge

_node_instance_attributes_query = """node, state, workflow :{ id }, required_state"""
_node_attributes_query = """name, version, template, base, type, config"""


async def add_instance(
    node_instance: dict[str, Any],
    workflow: str,
    tx,
):
    res = await tx.query(
        """
        with new_instance := (
            insert NodeInstance {
                node := ( select Node filter .id = <uuid>$node ),
                state := <str>$state,
                workflow := ( select Workflow filter .id = <uuid>$workflow ),
                depends := <int16>$depends,
                required_state := <array<str>>$required_state,
                sequence := <int16>$sequence
            }
        )
        select new_instance { %s }
        """
        % _node_instance_attributes_query,
        node=node_instance["node"]["id"],
        state=node_instance["state"],
        workflow=workflow,
        depends=node_instance["depends"],
        required_state=node_instance["required_state"] or [],
        sequence=node_instance.get("sequence", 0),
    )
    result = edge.obj_to_dict(res[0])
    return result


async def update_node_instance_relationships(
    instance_id: str,
    parents: list[dict[str, str]],
    depends_on: list[str],
    tx,
):
    for parent in parents:
        await tx.query(
            """
            update NodeInstance
                filter .id = <uuid>$instance_id
                set {
                    parents += (
                        select detached NodeInstance filter .id = <uuid>$parent
                    )
                };
            """,
            instance_id=instance_id,
            parent=parent["id"],
        )
    for dep in depends_on:
        await tx.query(
            """
            update NodeInstance
                filter .id = <uuid>$instance_id
                set {
                    depends_on += (
                        select detached NodeInstace filter .id = <uuid>$dep
                    )
            }
            """,
            instance_id=instance_id,
            dep=dep,
        )


@inject_client
async def add_node(
    node: dict[str, Any],
    client: AsyncIOClient,
):
    res = await client.query(
        """
        with new_node := (
            insert Node {
                name := $name,
                version := <int16>$version,
                template := <bool>$template,

                base := $base,
                type := $type,
            }
        )
        select new_instance { %s }
        """
        % _node_instance_attributes_query,
        node=node["name"],
        version=node["version"],
        template=node["template"],
        base=node["base"],
        type=node["type"],
    )
    result = edge.obj_to_dict(res[0])
    return result


@inject_client
async def update_instance_state(
    instance_id: str,
    state: str,
    client: AsyncIOClient,
) -> None:
    await client.query(
        """
        update NodeInstance
          filter .id = <uuid>$instance_id
          set {
            state := <str>$state
          }
        """,
        instance_id=instance_id,
        state=state,
    )
