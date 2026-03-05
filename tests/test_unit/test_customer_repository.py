import pytest
from repositories.customer import CustomerRepository
from models.customer import Customer


class TestCustomerRepository:
    def test_create_customer(self, db_session):
        repo = CustomerRepository(db_session)
        data = {
            "customer_id": "NEW001",
            "first_name": "New",
            "last_name": "Customer",
            "email": "new@example.com",
            "account_balance": 500.0
        }

        customer = repo.create(data)

        assert customer.customer_id == "NEW001"
        assert customer.first_name == "New"
        assert customer.email == "new@example.com"

    def test_get_customer(self, db_session, sample_customer):
        repo = CustomerRepository(db_session)
        customer = repo.get("TEST001")

        assert customer is not None
        assert customer.customer_id == "TEST001"
        assert customer.email == "test@example.com"

    def test_get_customer_not_found(self, db_session):
        repo = CustomerRepository(db_session)
        customer = repo.get("NONEXISTENT")

        assert customer is None

    def test_get_multi_customers(self, db_session, multiple_customers):
        repo = CustomerRepository(db_session)
        customers = repo.get_multi(skip=0, limit=5)

        assert len(customers) == 5

    def test_count_customers(self, db_session, multiple_customers):
        repo = CustomerRepository(db_session)
        count = repo.count()

        assert count == 10

    def test_upsert_existing_customer(self, db_session, sample_customer):
        repo = CustomerRepository(db_session)
        updated_data = {
            "first_name": "Updated",
            "account_balance": 2000.0
        }

        customer, is_new = repo.upsert("TEST001", updated_data)

        assert is_new is False
        assert customer.first_name == "Updated"
        assert customer.account_balance == 2000.0

    def test_upsert_new_customer(self, db_session):
        repo = CustomerRepository(db_session)
        data = {
            "first_name": "Brand",
            "last_name": "New",
            "email": "brandnew@example.com",
            "account_balance": 100.0
        }

        customer, is_new = repo.upsert("BRAND001", data)

        assert is_new is True
        assert customer.customer_id == "BRAND001"
        assert customer.first_name == "Brand"

    def test_find_by_email(self, db_session, sample_customer):
        repo = CustomerRepository(db_session)
        customer = repo.find_by_email("test@example.com")

        assert customer is not None
        assert customer.customer_id == "TEST001"

    def test_search_customers(self, db_session, multiple_customers):
        repo = CustomerRepository(db_session)
        results = repo.search("First")

        assert len(results) > 0
        assert all("First" in c.first_name for c in results)

    def test_delete_customer(self, db_session, sample_customer):
        repo = CustomerRepository(db_session)
        result = repo.delete("TEST001")

        assert result is True

        customer = repo.get("TEST001")
        assert customer is None

    def test_exists(self, db_session, sample_customer):
        repo = CustomerRepository(db_session)
        assert repo.exists("TEST001") is True
        assert repo.exists("NONEXISTENT") is False
