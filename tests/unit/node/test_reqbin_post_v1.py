"""Example API module.

This calls an Internet API and is not mocked.
"""
from wat.nodes.example_api_httpbin_org_post_v1 import execute, url


async def test_execute():
    # this test depends on the internet
    assert ("completed", {"httpbin_post_response_url": url}) == await execute(
        "some id", {}, {}
    ), "this test could fail due to internet issues"


async def test_execute_mocked(httpx_mock):
    # same test as above but httpx mocked
    # https://colin-b.github.io/pytest_httpx/
    httpx_mock.add_response(json={"url": url})
    assert ("completed", {"httpbin_post_response_url": url}) == await execute(
        "some id", {}, {}
    )
