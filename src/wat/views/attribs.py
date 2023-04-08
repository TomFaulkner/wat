from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..data import queries_async as q
from ..lib import depends

router = APIRouter()


@router.post("/attributes", response_model=q.StateAttributesAddResult)
async def add_attribute(
    attribs: q.StateAttributesAdd, tx=Depends(depends.edge_tx)
) -> q.StateAttributesAddResult:
    return await q.state_attributes_add(tx, **attribs.dict())


@router.get("/attributes/{id}", response_model=q.StateAttributesAddResult)
async def get_attributes_by_id(
    id: UUID, tx=Depends(depends.edge_tx)
) -> q.StateAttributesAddResult | None:
    res = await q.state_attributes_get_by_id(tx, id=id)
    if not res:
        raise HTTPException(status_code=404)
    return res


@router.get("/attributes", response_model=list[q.StateAttributesAddResult])
async def get_attributes(
    tx=Depends(depends.edge_tx),
) -> list[q.StateAttributesAddResult]:
    return await q.state_attributes_get_all(tx)


def init_app(app):
    app.include_router(router)
