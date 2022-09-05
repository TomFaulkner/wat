import json

from edgedb import AsyncIOClient

from ..db import inject_client
from ..lib import edge

_workflow_attributes_query = """
    id,
    template,
    template_active,
    state,
    flowstate :{ state, created, last_updated },
    node_instances :{ state, parents, children, depends, depends_on, node :{ name, version, config, base, type } },
"""  # noqa: E501 line too long


@inject_client
async def add(workflow, client: AsyncIOClient):
    res = await client.query(
        """
        with new_workflow := (
            insert Workflow {
                template := <bool>$template,
                template_active := <bool>$template_active,
                state := <str>$state,
                flowstate := (
                    insert FlowState {
                        state := <json>'',
                        created := datetime_current(),
                        last_updated := datetime_current(),
                    }
                )
            }
        )
        select new_workflow { %s };
        """
        % _workflow_attributes_query,
        **workflow,
    )
    result = edge.obj_to_dict(res[0])
    result["flowstate"]["state"] = json.loads(result["flowstate"]["state"])
    return result


@inject_client
async def get_by_id(wf_id: str, client: AsyncIOClient):
    res = await client.query(
        """
        select Workflow { %s } filter .id = <uuid>$wf_id;
        """
        % _workflow_attributes_query,
        wf_id=wf_id,
    )
    result = edge.obj_to_dict(res[0])
    result["flowstate"]["state"] = json.loads(result["flowstate"]["state"])
    return result
