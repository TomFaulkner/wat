from fastapi import APIRouter
from pydantic import BaseModel

from ..svc import node

router = APIRouter()


class NodeCreate(BaseModel):
    name: str
    version: int
    base: str
    type: str


class Node(NodeCreate):
    id: str
    template: bool


_node_bases = {"start", "finish", "decision", "action"}
_node_types = {"flow", "api", "ingestion", "response", "cron"}


@router.post("/nodes", response_model=Node)
async def post(node_) -> Node:
    return await node.add(node_)


def init_app(app):
    app.include_router(router)
