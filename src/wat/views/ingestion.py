from pydantic import BaseModel


class Ingestion(BaseModel):
    friendly_name: str
    workflow_id: str
    active: bool


async def get(name: str) -> Ingestion:
    pass
