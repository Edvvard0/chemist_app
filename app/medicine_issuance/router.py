from fastapi import APIRouter

from app.database import SessionDep
from app.medicine_issuance.dao import MedicineIssuanceDAO
from app.medicine_issuance.schemas import SMedicineIssuance, SMedicineIssuanceStatus

router = APIRouter(prefix="/med_issuance",
                   tags=["MedicineIssuance"])


@router.post("")
async def create_med_issuance(session: SessionDep, med_issuance: SMedicineIssuance):
    await MedicineIssuanceDAO.add(session, **med_issuance.model_dump())
    return {"message": "med_issuance add"}


@router.get("{med_issuance_id}")
async def get_med_issuance(session: SessionDep, med_issuance_id: int) -> SMedicineIssuance:
    med_issuance = await MedicineIssuanceDAO.find_one_or_none_by_id(session, med_issuance_id)
    return med_issuance


@router.post("status/{med_issuance_id}")
async def change_status_med_issuance(session: SessionDep, data: SMedicineIssuanceStatus):
    await MedicineIssuanceDAO.change_status(session, **data.model_dump())
    return {"message": "статус успешно изменен"}
