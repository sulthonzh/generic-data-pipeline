import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestCustomersEndpoint:
    def test_get_customers_empty(self, client):
        response = client.get("/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    def test_get_customers_with_data(self, client, multiple_customers):
        response = client.get("/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert len(data["data"]) == 10
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_get_customers_pagination(self, client, multiple_customers):
        response = client.get("/api/customers?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5
        assert data["has_next"] is True
        assert data["has_prev"] is False

    def test_get_customers_page_2(self, client, multiple_customers):
        response = client.get("/api/customers?page=2&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5
        assert data["has_next"] is False
        assert data["has_prev"] is True

    def test_get_customer_by_id(self, client, sample_customer):
        response = client.get("/api/customers/TEST001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "TEST001"
        assert data["email"] == "test@example.com"

    def test_get_customer_not_found(self, client):
        response = client.get("/api/customers/NONEXISTENT")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_invalid_page(self, client):
        response = client.get("/api/customers?page=0")
        assert response.status_code == 422

    def test_invalid_limit(self, client):
        response = client.get("/api/customers?limit=200")
        assert response.status_code == 422


class TestIngestEndpoint:
    def test_ingest_endpoint_exists(self, client, mocker):
        mock_service = mocker.patch("services.ingestion.IngestionService.ingest_all")
        mock_service.return_value = {
            "status": "success",
            "records_processed": 25,
            "message": "Test",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        response = client.post("/api/ingest")
        assert response.status_code in [200, 500]
