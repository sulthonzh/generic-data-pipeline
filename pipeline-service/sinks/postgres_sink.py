from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import get_db
from repositories.customer import CustomerRepository
from sinks.base import DataSink
from datetime import datetime, timezone


class PostgresSink(DataSink):
    def __init__(self, db: Session):
        self.db = db
        self.repository = CustomerRepository(db)

    @property
    def sink_type(self) -> str:
        return "postgres"

    async def write(self, data: List[Dict[str, Any]]) -> int:
        if not data:
            return 0

        count = 0
        for record in data:
            customer_id = record.get("customer_id")
            if not customer_id:
                continue

            clean_record = self._clean_record(record)
            self.repository.upsert(customer_id, clean_record)
            count += 1

        self.db.commit()
        return count

    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        clean = {}
        for key, value in record.items():
            if value is None:
                continue

            if key == "created_at" and isinstance(value, str):
                continue

            if key == "date_of_birth" and isinstance(value, str):
                clean[key] = value
            elif key not in ("customer_id", "created_at"):
                clean[key] = value

        return clean

    async def validate(self) -> bool:
        try:
            self.db.execute("SELECT 1")
            return True
        except Exception:
            return False
