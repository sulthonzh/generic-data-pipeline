import pytest
import subprocess
import time
import httpx
import orjson


@pytest.fixture(scope="module")
def docker_compose_setup():
    subprocess.run(
        ["docker-compose", "up", "-d"],
        cwd="/Users/sulthonzh/Data/projects/quadbyte/acumen-strategy/assesment",
        capture_output=True
    )
    time.sleep(10)
    yield
    subprocess.run(
        ["docker-compose", "down"],
        cwd="/Users/sulthonzh/Data/projects/quadbyte/acumen-strategy/assesment",
        capture_output=True
    )


class TestPipelineE2E:
    @pytest.mark.e2e
    def test_mock_server_health(self, docker_compose_setup):
        response = httpx.get("http://localhost:5001/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_mock_server_customers(self, docker_compose_setup):
        response = httpx.get("http://localhost:5001/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 20

    @pytest.mark.e2e
    def test_pipeline_service_health(self, docker_compose_setup):
        response = httpx.get("http://localhost:8000/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_full_pipeline_ingestion(self, docker_compose_setup):
        response = httpx.post("http://localhost:8000/api/ingest")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["records_processed"] > 0

    @pytest.mark.e2e
    def test_retrieve_customers_after_ingestion(self, docker_compose_setup):
        httpx.post("http://localhost:8000/api/ingest")
        time.sleep(1)

        response = httpx.get("http://localhost:8000/api/customers?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["data"]) > 0

    @pytest.mark.e2e
    def test_get_specific_customer(self, docker_compose_setup):
        httpx.post("http://localhost:8000/api/ingest")
        time.sleep(1)

        response = httpx.get("http://localhost:8000/api/customers/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST001"
        assert "first_name" in data
