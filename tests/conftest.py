import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from database import Base, get_db
from main import app
from models.customer import Customer


TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer_data():
    return {
        "customer_id": "TEST001",
        "first_name": "Test",
        "last_name": "Customer",
        "email": "test@example.com",
        "phone": "+1-555-0001",
        "address": "123 Test St",
        "account_balance": 1000.00
    }


@pytest.fixture
def sample_customer(db_session, sample_customer_data):
    customer = Customer(**sample_customer_data)
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def multiple_customers(db_session):
    customers = []
    for i in range(10):
        customer = Customer(
            customer_id=f"TEST{i:03d}",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            email=f"test{i}@example.com",
            account_balance=100.0 * i
        )
        customers.append(customer)
        db_session.add(customer)
    db_session.commit()
    return customers
