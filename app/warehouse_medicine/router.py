import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload

from app.database import SessionDep
from app.exception import ExpiredMedicinesException
from app.medicines.router import get_current_medicine
from app.warehouse_medicine.dao import WarehouseMedicineDAO
from app.warehouse_medicine.models import WarehouseMedicine
from app.warehouse_medicine.schemas import SWarehouseMedicine, SWarehouseMedicineAdd, TransferCreate

router = APIRouter(prefix="/warehouse_medicine",
                   tags=["WarehouseMedicine"])


@router.get("/")
async def get_wm(session: SessionDep) -> list[SWarehouseMedicine]:
    wm = await WarehouseMedicineDAO.find_all(session)
    return wm


@router.get("/check")
async def ckeck_wm(session: SessionDep):
    await WarehouseMedicineDAO.check_and_write_off_expired(session)
    return {"message": "товары успешно проверенны"}


@router.get("/{wm_id}")
async def get_current_wm(wm_id: int, session: SessionDep) -> SWarehouseMedicine | None:
    wm = await WarehouseMedicineDAO.find_one_or_none_by_id(session, wm_id)
    return wm


@router.get("/total/{medicine_id}")
async def get_total_quantity(medicine_id: int, session: SessionDep):
    total_quantity = await WarehouseMedicineDAO.total_quantity(session, medicine_id)
    return total_quantity


@router.get("/full_info/{wm_id}")
async def get_full_info_wm(wm_id: int, session: SessionDep):
    wm = await WarehouseMedicineDAO.find_full_info_wm(
        session,
        wm_id,
        options=[selectinload(WarehouseMedicine.medicines),
                 selectinload(WarehouseMedicine.warehouses)]
    )

    return wm


@router.post("/transfer")
async def transfer_medicine(
    transfer_data: TransferCreate,
    session: SessionDep
):


    await WarehouseMedicineDAO.transfer_medicine(
        session,
        transfer_data.medicine_id,
        transfer_data.from_warehouse_id,
        transfer_data.to_warehouse_id,
        transfer_data.quantity
    )

    return {"message": "Препарат успешно перемещен"}

@router.post("/")
async def create_wm(data: SWarehouseMedicineAdd, session: SessionDep):

    medicine = await get_current_medicine(data.medicines_id, session)
    if medicine.expiration_date < datetime.date.today():
        raise ExpiredMedicinesException
    await WarehouseMedicineDAO.add(session, **data.model_dump())
    return {"message": "wm add"}


@router.delete("/{wm_id}")
async def delete_current_wm(wm_id: int, session: SessionDep):
    await WarehouseMedicineDAO.delete(session, id=wm_id)
    return {"message": "wm delete"}