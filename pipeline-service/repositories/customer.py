from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.customer import Customer
from repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def find_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(
            Customer.email == email
        ).first()

    def upsert(
        self,
        customer_id: str,
        data: Dict[str, Any]
    ) -> tuple[Customer, bool]:
        customer = self.get(customer_id)

        if customer:
            for key, value in data.items():
                if hasattr(customer, key) and value is not None:
                    setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
            return customer, False

        new_customer = self.create({
            "customer_id": customer_id,
            **data
        })
        return new_customer, True

    def bulk_upsert(self, records: List[Dict[str, Any]]) -> int:
        count = 0
        for record in records:
            customer_id = record.pop("customer_id", None)
            if not customer_id:
                continue

            self.upsert(customer_id, record)
            count += 1

        self.db.commit()
        return count

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        search_pattern = f"%{query}%"
        return self.db.query(Customer).filter(
            (Customer.first_name.ilike(search_pattern)) |
            (Customer.last_name.ilike(search_pattern)) |
            (Customer.email.ilike(search_pattern))
        ).offset(skip).limit(limit).all()
