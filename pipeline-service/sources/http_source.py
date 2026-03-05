import httpx
import orjson
from typing import List, Dict, Any, Optional
from .base import DataSource
from config import settings


class HTTPSource(DataSource):
    def __init__(
        self,
        base_url: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 60.0
    ):
        self.base_url = base_url.rstrip("/")
        self.endpoint = endpoint.lstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def url(self) -> str:
        return f"{self.base_url}/{self.endpoint}"

    @property
    def source_type(self) -> str:
        return "http"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers
            )
        return self._client

    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        client = await self._get_client()

        params = kwargs.get("params", {})
        response = await client.get(self.url, params=params)
        response.raise_for_status()

        data = orjson.loads(response.content)

        if isinstance(data, dict):
            return data.get("data", [data])

        return data if isinstance(data, list) else []

    async def fetch_paginated(
        self,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        client = await self._get_client()

        response = await client.get(
            self.url,
            params={"page": page, "limit": limit}
        )
        response.raise_for_status()

        return orjson.loads(response.content)

    async def validate(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get(self.url)
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class MockServerSource(HTTPSource):
    def __init__(self):
        super().__init__(
            base_url=settings.mock_server_url,
            endpoint="/api/customers/all",
            timeout=settings.timeout
        )

    @property
    def source_type(self) -> str:
        return "mock_server"

    async def fetch_all_customers(self) -> List[Dict[str, Any]]:
        return await self.fetch()
