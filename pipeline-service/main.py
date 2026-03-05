from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, Dict, Any

from config import settings
from database import get_db, init_db
from models.customer import Customer
from models.schemas import (
    CustomerResponse,
    PaginatedResponse,
    IngestResponse,
    HealthResponse
)
from repositories.customer import CustomerRepository
from services.ingestion import IngestionService

from datetime import datetime, timezone


class LargeIngestRequest(BaseModel):
    size: int = 100000
    batch_size: int = 10000


class PerformanceResponse(BaseModel):
    test: str
    records: int
    results: Dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        service="pipeline-service",
        timestamp=datetime.now(timezone.utc)
    )


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_data(db: Session = Depends(get_db)):
    service = IngestionService(db)
    try:
        result = await service.ingest_all()
        return IngestResponse(**result)
    finally:
        await service.close()


@app.post("/api/ingest/large", response_model=IngestResponse)
async def ingest_large_data(
    request: LargeIngestRequest,
    db: Session = Depends(get_db)
):
    service = IngestionService(db)
    try:
        result = await service.ingest_large(
            size=request.size,
            batch_size=request.batch_size
        )
        return IngestResponse(**result)
    finally:
        await service.close()


@app.get("/api/performance/test", response_model=PerformanceResponse)
async def performance_test(size: int = Query(10000, ge=100, le=1000000)):
    import time
    import httpx
    import orjson

    start = time.time()

    async with httpx.AsyncClient(timeout=120.0) as client:
        url = f"{settings.mock_server_url}/api/performance/test"
        resp = await client.get(url, params={"size": size})
        resp.raise_for_status()
        data = orjson.loads(resp.content)

    total_time = time.time() - start

    return PerformanceResponse(
        test=data.get("test", "orjson + generation performance"),
        records=size,
        results={
            "network_time_ms": round(total_time * 1000, 2),
            **data.get("results", {})
        }
    )


@app.get("/api/customers", response_model=PaginatedResponse)
async def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    repo = CustomerRepository(db)
    offset = (page - 1) * limit

    total = repo.count()
    customers = repo.get_multi(skip=offset, limit=limit)

    data = [
        CustomerResponse.model_validate(c)
        for c in customers
    ]

    return PaginatedResponse(
        data=data,
        total=total,
        page=page,
        limit=limit,
        has_next=offset + limit < total,
        has_prev=page > 1
    )


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    customer = repo.get(customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerResponse.model_validate(customer)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development
    )
