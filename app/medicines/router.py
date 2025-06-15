import datetime

from fastapi import APIRouter

from app.database import SessionDep
from app.exception import ExpiredMedicinesException
from app.medicines.dao import MedicineDAO
from app.medicines.schemas import SMedicine, SMedicineAdd

router = APIRouter(prefix="/medicine",
                   tags=["Medicine"])


@router.get("/")
async def get_medicines(session: SessionDep) -> list[SMedicine]:
    medicine = await MedicineDAO.find_all(session)
    return medicine


@router.get("/{medicine_id}")
async def get_current_medicine(medicine_id: int, session: SessionDep) -> SMedicine | None:
    medicine = await MedicineDAO.find_one_or_none_by_id(session, medicine_id)
    return medicine


@router.post("/")
async def create_medicine(data: SMedicineAdd ,session: SessionDep):
    if data.expiration_date < datetime.date.today():
        raise ExpiredMedicinesException

    await MedicineDAO.add(session, **data.model_dump())
    return {"message": "medicine add"}


@router.delete("/{medicine_id}")
async def delete_current_medicine(medicine_id: int, session: SessionDep):
    await MedicineDAO.delete(session, id=medicine_id)
    return {"message": "medicine delete"}