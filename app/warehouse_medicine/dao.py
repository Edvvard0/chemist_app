from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, delete, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import WriteOffMed
from app.dao.base import BaseDAO
from app.medicines.models import Medicine
from app.warehouse_medicine.models import WarehouseMedicine


class WarehouseMedicineDAO(BaseDAO):
    model = WarehouseMedicine

    @classmethod
    async def find_full_info_wm(cls, session: AsyncSession, wm_id: int, options=None):

        query = select(WarehouseMedicine).filter_by(**{"id": wm_id})
        if options:
            query = query.options(*options)
        rez = await session.execute(query)
        otv = rez.scalar_one_or_none()

        return otv

    @classmethod
    async def total_quantity(cls, session: AsyncSession, medicine_id: int):

        query = select(func.sum(WarehouseMedicine.quantity)).filter_by(**{"medicines_id": medicine_id})

        rez = await session.execute(query)
        otv = rez.scalar_one_or_none()

        return otv

    @classmethod
    async def transfer_medicine(
            cls,
            session: AsyncSession,
            medicine_id: int,
            from_warehouse_id: int,
            to_warehouse_id: int,
            quantity: int
    ) -> None:
        """
        Перемещает указанное количество лекарства с одного склада на другой.

        Args:
            session: Асинхронная сессия SQLAlchemy
            medicine_id: ID лекарства
            from_warehouse_id: ID исходного склада
            to_warehouse_id: ID целевого склада
            quantity: Количество для перемещения

        Raises:
            HTTPException: Если лекарство не найдено, недостаточно количества или склады недоступны
        """
        # Проверяем наличие лекарства на исходном складе
        query = select(WarehouseMedicine).where(
            WarehouseMedicine.medicines_id == medicine_id,
            WarehouseMedicine.warehouses_id == from_warehouse_id
        )
        result = await session.execute(query)
        from_warehouse_med = result.scalar_one_or_none()

        if not from_warehouse_med:
            raise HTTPException(
                status_code=404,
                detail=f"Лекарство с ID {medicine_id} не найдено на складе с ID {from_warehouse_id}"
            )

        if from_warehouse_med.quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно количества лекарства на складе (доступно: {from_warehouse_med.quantity})"
            )

        # Проверяем, есть ли лекарство на целевом складе
        query = select(WarehouseMedicine).where(
            WarehouseMedicine.medicines_id == medicine_id,
            WarehouseMedicine.warehouses_id == to_warehouse_id
        )
        result = await session.execute(query)
        to_warehouse_med = result.scalar_one_or_none()

        if from_warehouse_med.quantity == quantity:
            await session.execute(
                delete(WarehouseMedicine).where(
                    WarehouseMedicine.medicines_id == medicine_id,
                    WarehouseMedicine.warehouses_id == from_warehouse_id
                )
            )
        else:
            await session.execute(
                update(WarehouseMedicine)
                .where(
                    WarehouseMedicine.medicines_id == medicine_id,
                    WarehouseMedicine.warehouses_id == from_warehouse_id
                )
                .values(quantity=WarehouseMedicine.quantity - quantity)
            )

        # Увеличиваем количество на целевом складе или создаем новую запись
        if to_warehouse_med:
            await session.execute(
                update(WarehouseMedicine)
                .where(
                    WarehouseMedicine.medicines_id == medicine_id,
                    WarehouseMedicine.warehouses_id == to_warehouse_id
                )
                .values(quantity=WarehouseMedicine.quantity + quantity)
            )
        else:
            new_record = WarehouseMedicine(
                medicines_id=medicine_id,
                warehouses_id=to_warehouse_id,
                quantity=quantity,
                delivery_date=from_warehouse_med.delivery_date
            )
            session.add(new_record)


        await session.commit()

    @classmethod
    async def check_and_write_off_expired(cls, session: AsyncSession) -> None:
        """
        Проверяет лекарства с истекшим сроком годности и списывает их.

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        
        try:
            # Находим все записи warehouse_medicines с просроченными лекарствами
            query = select(WarehouseMedicine).join(
                Medicine,
                WarehouseMedicine.medicines_id == Medicine.id
            ).where(
                Medicine.expiration_date < date.today()
            )
            result = await session.execute(query)
            expired_meds = result.scalars().all()

            if not expired_meds:
                print("Просроченные лекарства не найдены")
                return

            for med in expired_meds:
                # Создаем запись о списании
                write_off = WriteOffMed(
                    medicines_id=med.medicines_id,
                    warehouse_id=med.warehouses_id,
                    reason="Истек срок годности",
                    write_off_date=func.now()
                )
                session.add(write_off)

                # Удаляем запись из warehouse_medicines
                await session.execute(
                    delete(WarehouseMedicine).where(
                        WarehouseMedicine.medicines_id == med.medicines_id,
                        WarehouseMedicine.warehouses_id == med.warehouses_id
                    )
                )
                print(f"Списано {med.quantity} единиц лекарства {med.medicines_id} "
                      f"со склада {med.warehouses_id} (просрочено)")

            await session.commit()
            print(f"Списано {len(expired_meds)} просроченных записей")

        except SQLAlchemyError as e:
            await session.rollback()
            print(f"Database Error: {str(e)}")
            raise
        except Exception as e:
            await session.rollback()
            print(f"Unknown Error: {str(e)}")
            raise
