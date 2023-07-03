import edgedb


async def test_edgedb_fixture(tx):
    result = await tx.query("select Workflow;")
    assert isinstance(result, edgedb.Set)
