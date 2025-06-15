import logging

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.core.models import WriteOffMed
from app.core.schemas import OrderStatus, StockReport, MedicineStock, WarehouseStockReport
from app.dao.base import BaseDAO
from app.medicines.models import Medicine
from app.warehouse_medicine.models import WarehouseMedicine
from app.warehouses.models import Warehouse


class CoreDAO(BaseDAO):
    model = WriteOffMed

    @classmethod
    async def write_off_medicine(
            cls,
            session: AsyncSession,
            medicine_id: int,
            warehouse_id: int,
            reason: str
    ) -> None:
        """
        Списывает всё количество лекарства с указанного склада, создает запись в таблице write_offs
        и удаляет запись из warehouse_medicines.

        Args:
            session: Асинхронная сессия SQLAlchemy
            medicine_id: ID лекарства
            warehouse_id: ID склада
            reason: Причина списания

        Raises:
            HTTPException: Если лекарство не найдено или количество равно нулю
        """

        query = select(WarehouseMedicine).where(
            WarehouseMedicine.medicines_id == medicine_id,
            WarehouseMedicine.warehouses_id == warehouse_id
        )
        result = await session.execute(query)
        warehouse_med = result.scalar_one_or_none()

        print(warehouse_med)

        if not warehouse_med:
            raise HTTPException(
                status_code=404,
                detail="Лекарство не найдено на указанном складе"
            )

        if warehouse_med.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Количество лекарства на складе равно нулю"
            )


        write_off = WriteOffMed(
            medicines_id=medicine_id,
            warehouse_id=warehouse_id,
            reason=reason,
            write_off_date=func.now()
        )
        session.add(write_off)


        await session.execute(
            delete(WarehouseMedicine).where(
                WarehouseMedicine.medicines_id == medicine_id,
                WarehouseMedicine.warehouses_id == warehouse_id
            )
        )

        await session.commit()

    @classmethod
    async def get_stock_report(cls, session: AsyncSession) -> StockReport:
        """
        Возвращает отчет о необходимости заказа лекарств по всем складам.

        Args:
            session: Асинхронная сессия SQLAlchemy

        Returns:
            StockReport: Отчет с данными по складам и лекарствам

        Raises:
            HTTPException: Если произошла ошибка базы данных
        """
        logging.info("Начало формирования отчета о запасах лекарств")
        try:
            # Получаем все склады
            query = select(Warehouse)
            result = await session.execute(query)
            warehouses = result.scalars().all()

            warehouse_reports = []
            for warehouse in warehouses:
                # Получаем все лекарства на складе
                query = select(WarehouseMedicine, Medicine.name).join(
                    Medicine,
                    WarehouseMedicine.medicines_id == Medicine.id
                ).where(
                    WarehouseMedicine.warehouses_id == warehouse.id
                )
                result = await session.execute(query)
                medicines_data = result.all()

                # Формируем список лекарств для склада
                medicine_stocks = []
                for wm, medicine_name in medicines_data:
                    # Определяем статус срочности
                    if wm.quantity >= 100:
                        order_status = OrderStatus.SUFFICIENT
                    elif wm.quantity < 20:
                        order_status = OrderStatus.URGENT
                    else:  # 20 <= quantity < 50
                        order_status = OrderStatus.NEEDS_ORDER

                    medicine_stocks.append(
                        MedicineStock(
                            medicine_name=medicine_name,
                            quantity=wm.quantity,
                            order_status=order_status
                        )
                    )

                # Добавляем отчет по складу
                warehouse_reports.append(
                    WarehouseStockReport(
                        warehouse_name=warehouse.name,
                        warehouse_address=warehouse.address,
                        medicines=medicine_stocks
                    )
                )

            report = StockReport(warehouses=warehouse_reports)
            logging.info("Отчет о запасах успешно сформирован")
            return report

        except SQLAlchemyError as e:
            logging.error(f"Database Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
        except Exception as e:
            logging.error(f"Unknown Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unknown Error: {str(e)}")