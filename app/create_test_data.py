from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import asyncio
import logging

from app.database import async_session_maker
from app.medicine_issuance.models import MedicineIssuance
from app.users.models import User
from app.warehouse_medicine.models import WarehouseMedicine
from app.core.models import WriteOffMed
from app.medicines.models import Medicine

from sqlalchemy.sql import func

from app.warehouses.models import Warehouse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fill_test_data(session: AsyncSession):
    """
    Заполняет таблицы тестовыми данными.
    """
    try:
        # Заполнение таблицы warehouses
        warehouses = [
            Warehouse(name="Склад Москва", address="Москва, ул. Ленина, 1"),
            Warehouse(name="Склад Санкт-Петербург", address="СПб, ул. Невская, 2"),
            Warehouse(name="Склад Казань", address="Казань, ул. Кремлевская, 3"),
            Warehouse(name="Склад Новосибирск", address="Новосибирск, ул. Сибирская, 4"),
            Warehouse(name="Склад Екатеринбург", address="Екатеринбург, ул. Уральская, 5"),
        ]
        session.add_all(warehouses)
        await session.flush()  # Получаем ID для складов
        logger.info("Добавлено 5 складов")

        # Заполнение таблицы users
        users = [
            User(name="Иван Иванов", email="ivan@example.com", password="password1"),
            User(name="Петр Петров", email="petr@example.com", password="password2"),
            User(name="Анна Сидорова", email="anna@example.com", password="password3"),
            User(name="Мария Кузнецова", email="maria@example.com", password="password4"),
            User(name="Сергей Смирнов", email="sergey@example.com", password="password5"),
        ]
        session.add_all(users)
        await session.flush()  # Получаем ID для пользователей
        logger.info("Добавлено 5 пользователей")

        # Заполнение таблицы medicines
        medicines = [
            Medicine(name="Аспирин", description="Обезболивающее", expiration_date=date(2025, 12, 31)),
            Medicine(name="Парацетамол", description="Жаропонижающее", expiration_date=date(2025, 11, 30)),
            Medicine(name="Ибупрофен", description="Противовоспалительное", expiration_date=date(2025, 10, 15)),
            Medicine(name="Амоксициллин", description="Антибиотик", expiration_date=date(2025, 9, 1)),
            Medicine(name="Лоратадин", description="Антигистаминное", expiration_date=date(2025, 8, 20)),
        ]
        session.add_all(medicines)
        await session.flush()  # Получаем ID для лекарств
        logger.info("Добавлено 5 лекарств")

        # Заполнение таблицы warehouse_medicines
        warehouse_medicines = [
            WarehouseMedicine(warehouses_id=warehouses[0].id, medicines_id=medicines[0].id, quantity=100, delivery_date=date(2025, 6, 1)),
            WarehouseMedicine(warehouses_id=warehouses[1].id, medicines_id=medicines[1].id, quantity=150, delivery_date=date(2025, 6, 2)),
            WarehouseMedicine(warehouses_id=warehouses[2].id, medicines_id=medicines[2].id, quantity=200, delivery_date=date(2025, 6, 3)),
            WarehouseMedicine(warehouses_id=warehouses[3].id, medicines_id=medicines[3].id, quantity=80, delivery_date=date(2025, 6, 4)),
            WarehouseMedicine(warehouses_id=warehouses[4].id, medicines_id=medicines[4].id, quantity=120, delivery_date=date(2025, 6, 5)),
        ]
        session.add_all(warehouse_medicines)
        await session.flush()  # Получаем ID для warehouse_medicines
        logger.info("Добавлено 5 записей в warehouse_medicines")

        # Заполнение таблицы medicine_issuances
        medicine_issuances = [
            MedicineIssuance(wm_id=warehouse_medicines[0].id, quantity=10, issuance_date=date(2025, 6, 7), status="pending"),
            MedicineIssuance(wm_id=warehouse_medicines[1].id, quantity=20, issuance_date=date(2025, 6, 6), status="accepted"),
            MedicineIssuance(wm_id=warehouse_medicines[2].id, quantity=15, issuance_date=date(2025, 6, 5), status="rejected"),
            MedicineIssuance(wm_id=warehouse_medicines[3].id, quantity=30, issuance_date=date(2025, 6, 4), status="pending"),
            MedicineIssuance(wm_id=warehouse_medicines[4].id, quantity=25, issuance_date=date(2025, 6, 3), status="accepted"),
        ]
        session.add_all(medicine_issuances)
        await session.flush()
        logger.info("Добавлено 5 записей в medicine_issuances")

        # Заполнение таблицы writeoffmeds
        writeoff_meds = [
            WriteOffMed(medicines_id=medicines[0].id, warehouse_id=warehouses[0].id, reason="Истек срок годности", write_off_date=date(2025, 6, 7)),
            WriteOffMed(medicines_id=medicines[1].id, warehouse_id=warehouses[1].id, reason="Повреждена упаковка", write_off_date=date(2025, 6, 6)),
            WriteOffMed(medicines_id=medicines[2].id, warehouse_id=warehouses[2].id, reason="Истек срок годности", write_off_date=date(2025, 6, 5)),
            WriteOffMed(medicines_id=medicines[3].id, warehouse_id=warehouses[3].id, reason="Утилизация", write_off_date=date(2025, 6, 4)),
            WriteOffMed(medicines_id=medicines[4].id, warehouse_id=warehouses[4].id, reason="Повреждена упаковка", write_off_date=date(2025, 6, 3)),
        ]
        session.add_all(writeoff_meds)
        await session.flush()
        logger.info("Добавлено 5 записей в writeoffmeds")

        await session.commit()
        logger.info("Все тестовые данные успешно добавлены")

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database Error: {str(e)}")
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Unknown Error: {str(e)}")
        raise

async def main():
    async with async_session_maker() as session:
        await fill_test_data(session)

if __name__ == "__main__":
    asyncio.run(main())