import json
from functools import partial

from edgedb import AsyncIOClient

from ..db import inject_client
from ..lib import edge

_workflow_attributes_query = """
    id,
    template,
    template_active,
    state,
    flowstate :{ state, created, last_updated },
    node_instances :{ state, parents, children, depends, depends_on, decision_options, node :{ name, version, config, base, type } },
"""  # noqa: E501 line too long

_flowstate_attributes_query = "id, state, created, last_updated"


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
async def get_by_id(
    wf_id: str, client: AsyncIOClient, template_only=False, active_template_only=False
):
    template_filter = "and .template = true" if template_only else ""
    active_template_filter = (
        "and .template_active = true" if active_template_only else ""
    )
    res = await client.query_required_single(
        """
        select Workflow { %s } filter .id = <uuid>$wf_id %s %s;
        """
        % (_workflow_attributes_query, template_filter, active_template_filter),
        wf_id=wf_id,
    )
    result = edge.obj_to_dict(res)
    result["flowstate"]["state"] = json.loads(result["flowstate"]["state"])
    return result


get_template_by_id = partial(get_by_id, template_only=True)
get_active_template_by_id = partial(
    get_by_id, template_only=True, active_template_only=True
)


async def update_flow_state(fs_id: str, new_state: dict, tx) -> dict:
    res = await tx.query_required_single(
        """
        update FlowState
            filter .id = <uuid>$fs_id
            set {
                last_updated := datetime_current(),
                state := <json>$new_state
            };
        select FlowState {%s} filter .id = <uuid>$fs_id;
        """
        % _flowstate_attributes_query,
        fs_id=fs_id,
        new_state=json.dumps(new_state),
    )
    result = edge.obj_to_dict(res)
    result["state"] = json.loads(res.state)
    return result
