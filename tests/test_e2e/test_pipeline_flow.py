import pytest
import subprocess
import time
import httpx
import orjson
import os
import shutil


def _docker_compose_available():
    """Check if docker-compose is available and not in CI."""
    # Skip in CI (GitHub Actions, GitLab CI, etc.)
    if os.getenv("CI"):
        return False
    # Check if docker-compose command exists
    return shutil.which("docker-compose") is not None


@pytest.fixture(scope="module")
def docker_compose_setup():
    """Setup docker-compose only if not in CI and docker-compose is available."""
    if not _docker_compose_available():
        # In CI or no docker-compose - services should already be running
        yield
        return

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
        mock_url = os.getenv("MOCK_SERVER_URL", "http://localhost:5001")
        response = httpx.get(f"{mock_url}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_mock_server_customers(self, docker_compose_setup):
        mock_url = os.getenv("MOCK_SERVER_URL", "http://localhost:5001")
        response = httpx.get(f"{mock_url}/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 20

    @pytest.mark.e2e
    def test_pipeline_service_health(self, docker_compose_setup):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        response = httpx.get(f"{pipeline_url}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_full_pipeline_ingestion(self, docker_compose_setup):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        response = httpx.post(f"{pipeline_url}/api/ingest")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["records_processed"] > 0

    @pytest.mark.e2e
    def test_retrieve_customers_after_ingestion(self, docker_compose_setup):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        httpx.post(f"{pipeline_url}/api/ingest")
        time.sleep(1)

        response = httpx.get(f"{pipeline_url}/api/customers?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["data"]) > 0

    @pytest.mark.e2e
    def test_get_specific_customer(self, docker_compose_setup):
        pipeline_url = os.getenv("PIPELINE_SERVICE_URL", "http://localhost:8000")
        httpx.post(f"{pipeline_url}/api/ingest")
        time.sleep(1)

        response = httpx.get(f"{pipeline_url}/api/customers/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST001"
        assert "first_name" in data
