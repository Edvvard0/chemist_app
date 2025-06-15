from app.dao.base import BaseDAO
from app.medicines.models import Medicine


class MedicineDAO(BaseDAO):
    model = Medicine