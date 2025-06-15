from celery import shared_task

from app.database import get_session
from app.warehouse_medicine.dao import WarehouseMedicineDAO

import logging


@shared_task
async def check_expired_medicines():
    """
    Фоновая задача для проверки и списания просроченных лекарств.
    """
    logging.info("Запуск задачи проверки просроченных лекарств")
    async with get_session() as session:
        try:
            await WarehouseMedicineDAO.check_and_write_off_expired(session)
        except Exception as e:
            logging.error(f"Ошибка при выполнении проверки просрочки: {str(e)}")
            raise