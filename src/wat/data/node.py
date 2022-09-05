from typing import Any

from edgedb import AsyncIOClient

from ..db import inject_client
from ..lib import edge

_node_instance_attributes_query = """node, state, workflow :{ id }"""
_node_attributes_query = """name, version, template, base, type, config"""


@inject_client
async def add_instance(
    node_instance: dict[str, Any],
    node: str,
    workflow: str,
    client: AsyncIOClient,
):
    res = await client.query(
        """
        with new_instance := (
            insert NodeInstance {
                node := ( select Node filter .id = $node )
                state := $state,
                workflow := ( select Workflow filter .id = $workflow ),
                depends := $depends,
            }
        )
        select new_instance { %s }
        """
        % _node_instance_attributes_query,
        node=node,
        workflow=workflow,
    )
    result = edge.obj_to_dict(res[0])
    return result


@inject_client
async def update_node_instance_relationships(
    instance_id: str,
    parents: list[str],
    depends_on: list[str],
    decision_options: list[str],
    client,
):
    async for tx in client.transaction():
        async with tx:
            for parent in parents:
                await client.query(
                    """
                    update NodeInstance
                        filter .id = $instance_id
                        set {
                            parents += (
                                select detached NodeInstance filter .id = <uuid>$parent
                            )
                        };
                    """,
                    parent,
                )
            for dep in depends_on:
                await client.query(
                    """
                    update NodeInstance
                        filter .id = $instance_id
                        set {
                            depends_on += (
                                select detached NodeInstace filter .id = <uuid>$dep
                            )
                    }
                    """,
                    dep,
                )
            await client.query(
                """
                    update NodeInstance
                        filter .id = $instance_id
                        set {
                            decision_options := array<uuid>$decision_options
                        }
                """,
                decision_options,
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
