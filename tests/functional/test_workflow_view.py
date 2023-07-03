create_wf_body = {
    "name": "string",
    "version": 0,
    "template": True,
    "template_active": True,
    "state": "string",
    "start_requirements": [],
}


async def test_workflow_create(client_auth):
    res = await client_auth.post(
        url="/workflows",
        json=create_wf_body,
    )
    assert res.json()["id"]


async def test_workflow_create_fail_start_reqs_dont_exist(client_auth):
    sr = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    res = await client_auth.post(
        url="/workflows",
        json=create_wf_body | {"start_requirements": [sr]},
    )
    assert res.status_code == 422
    assert sr in res.text
