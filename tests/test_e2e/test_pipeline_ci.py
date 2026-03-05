import pytest
import httpx
import os
import time


@pytest.mark.e2e
class TestPipelineE2ECI:
    """E2E tests that run in CI with pre-started services."""

    @pytest.fixture(autouse=True)
    def wait_for_services(self):
        """Wait a moment for services to be ready."""
        time.sleep(2)
        yield

    def test_mock_server_health(self):
        mock_url = os.getenv("MOCK_SERVER_URL", "http://localhost:5000")
        response = httpx.get(f"{mock_url}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_mock_server_customers(self):
        mock_url = os.getenv("MOCK_SERVER_URL", "http://localhost:5000")
        response = httpx.get(f"{mock_url}/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 20

    def test_pipeline_service_health(self):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        response = httpx.get(f"{pipeline_url}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_full_pipeline_ingestion(self):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        response = httpx.post(f"{pipeline_url}/api/ingest")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["records_processed"] > 0

    def test_retrieve_customers_after_ingestion(self):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        httpx.post(f"{pipeline_url}/api/ingest")
        time.sleep(1)

        response = httpx.get(f"{pipeline_url}/api/customers?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["data"]) > 0

    def test_get_specific_customer(self):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        httpx.post(f"{pipeline_url}/api/ingest")
        time.sleep(1)

        response = httpx.get(f"{pipeline_url}/api/customers/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST001"
        assert "first_name" in data
