import pytest
from repositories.base import BaseRepository
from models.customer import Customer


class TestBaseRepository:
    def test_get(self, db_session, sample_customer):
        repo = BaseRepository(Customer, db_session)
        customer = repo.get("TEST001")

        assert customer is not None
        assert customer.customer_id == "TEST001"

    def test_get_multi(self, db_session, multiple_customers):
        repo = BaseRepository(Customer, db_session)
        customers = repo.get_multi(skip=0, limit=5)

        assert len(customers) == 5

    def test_count(self, db_session, multiple_customers):
        repo = BaseRepository(Customer, db_session)
        count = repo.count()

        assert count == 10

    def test_create(self, db_session):
        repo = BaseRepository(Customer, db_session)
        data = {
            "customer_id": "BASE001",
            "first_name": "Base",
            "last_name": "Test",
            "email": "base@example.com",
            "account_balance": 100.0
        }

        customer = repo.create(data)

        assert customer.customer_id == "BASE001"

    def test_update(self, db_session, sample_customer):
        repo = BaseRepository(Customer, db_session)
        updated = repo.update("TEST001", {"first_name": "UpdatedName"})

        assert updated is not None
        assert updated.first_name == "UpdatedName"

    def test_delete(self, db_session, sample_customer):
        repo = BaseRepository(Customer, db_session)
        result = repo.delete("TEST001")

        assert result is True

    def test_exists(self, db_session, sample_customer):
        repo = BaseRepository(Customer, db_session)
        assert repo.exists("TEST001") is True
        assert repo.exists("FAKE") is False
