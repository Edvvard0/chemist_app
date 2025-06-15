from fastapi import APIRouter

from app.database import SessionDep
from app.warehouses.dao import WarehouseDAO
from app.warehouses.schemas import SWarehouse, SWarehouseAdd

router = APIRouter(prefix="/warehouses",
                   tags=["Warehouses"])


@router.get("/")
async def get_warehouses(session: SessionDep) -> list[SWarehouse]:
    warehouses = await WarehouseDAO.find_all(session)
    return warehouses


@router.get("/{warehouses_id}")
async def get_current_warehouses(warehouses_id: int, session: SessionDep) -> SWarehouse | None:
    warehouses = await WarehouseDAO.find_one_or_none_by_id(session, warehouses_id)
    return warehouses


@router.post("/")
async def create_warehouses(data: SWarehouseAdd ,session: SessionDep):
    await WarehouseDAO.add(session, **data.model_dump())
    return {"message": "warehouses add"}


@router.delete("/{warehouses_id}")
async def delete_current_warehouses(warehouses_id: int, session: SessionDep):
    await WarehouseDAO.delete(session, id=warehouses_id)
    return {"message": "warehouses delete"}
