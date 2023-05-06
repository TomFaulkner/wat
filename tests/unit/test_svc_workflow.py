from wat.svc import workflow


def uuid_generator():
    yield "1p"
    yield "2p"
    yield "3p"


uu = uuid_generator()


async def create_node_instance(node_instance, tx):
    return node_instance | {"id": next(uu)}


node_instances = [
    {
        "id": "1",
        "depends_on": [],
        "parents": [],
    },
    {
        "id": "2",
        "depends_on": [{"id": "1"}],
        "parents": [{"id": "1"}],
    },
    {
        "id": "3",
        "depends_on": [{"id": "1"}, {"id": "2"}],
        "parents": [{"id": "1"}, {"id": "2"}],
    },
]


async def test_create_instance_replaces_ids():
    calls = []

    async def update_node_instance_relationships(node_instance, tx):
        calls.append(node_instance)
        return True

    tx = None
    await workflow._create_node_instances(
        node_instances, create_node_instance, update_node_instance_relationships, tx
    )

    assert calls[0]["id"] == "1p"
    assert not calls[0]["depends_on"]

    assert calls[1]["id"] == "2p"
    assert calls[1]["depends_on"] == [{"id": "1p"}]

    assert calls[2]["id"] == "3p"
    assert calls[2]["depends_on"] == [{"id": "1p"}, {"id": "2p"}]
