from fastapi import APIRouter, HTTPException

from app.core.dao import CoreDAO
from app.core.schemas import SWriteOff, StockReport
from app.database import SessionDep

router = APIRouter(prefix="/core",
                   tags=["Core"])


@router.post("/")
async def write_off(session: SessionDep, data: SWriteOff):
    await CoreDAO.write_off_medicine(session=session,
                                     medicine_id=data.medicine_id,
                                     warehouse_id=data.warehouses_id,
                                     reason=data.reason)
    return {"message": "Препарат успешно списан"}


@router.get("/stock-report")
async def get_stock_report(
    session: SessionDep
) -> StockReport:
    """
    Возвращает отчет о необходимости заказа лекарств по всем складам.

    Args:
        session: Асинхронная сессия SQLAlchemy

    Returns:
        StockReport: Отчет с данными по складам и лекарствам
    """
    try:
        report = await CoreDAO.get_stock_report(session)
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при формировании отчета: {str(e)}")