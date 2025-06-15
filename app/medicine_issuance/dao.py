from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.medicine_issuance.models import MedicineIssuance
from app.warehouse_medicine.models import WarehouseMedicine


class MedicineIssuanceDAO(BaseDAO):
    model = MedicineIssuance

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        query = select(WarehouseMedicine).where(
            WarehouseMedicine.id == values["wm_id"]
        )
        result = await session.execute(query)
        from_warehouse_med = result.scalar_one_or_none()

        if not from_warehouse_med:
            raise HTTPException(
                status_code=404,
                detail=f"Данная запись не найдена"
            )

        if from_warehouse_med.quantity < values["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно количества лекарства на складе (доступно: {from_warehouse_med.quantity})"
            )

        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.commit()

    @classmethod
    async def change_status(cls, session: AsyncSession, **values):
        query = select(MedicineIssuance).where(MedicineIssuance.id == values["med_issuance_id"])
        result = await session.execute(query)
        med_issuance = result.scalar_one_or_none()
        new_status = values["status"]

        if new_status == "accepted":
            query = select(WarehouseMedicine).where(WarehouseMedicine.id == med_issuance.wm_id)
            result = await session.execute(query)
            wm = result.scalar_one_or_none()

            if wm.quantity < med_issuance.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Недостаточно количества лекарства на складе (доступно: {wm.quantity})"
                )

            wm.quantity -= med_issuance.quantity

        med_issuance.status = new_status
        await session.commit()
