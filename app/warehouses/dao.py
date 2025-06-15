from app.dao.base import BaseDAO
from app.warehouses.models import Warehouse


class WarehouseDAO(BaseDAO):
    model = Warehouse