from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sources.http_source import MockServerSource
from sinks.postgres_sink import PostgresSink
from services.pipeline import PipelineOrchestrator
from config import settings
from datetime import datetime, timezone
from repositories.customer import CustomerRepository
import time
import httpx
import polars as pl


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.source = MockServerSource()
        self.sink = PostgresSink(db)
        self.repository = CustomerRepository(db)
        self.orchestrator = PipelineOrchestrator(
            source=self.source,
            sink=self.sink,
            batch_size=settings.batch_size
        )

    async def ingest_all(self) -> Dict[str, Any]:
        result = await self.orchestrator.execute()

        return {
            "status": result.status,
            "records_processed": result.records_processed,
            "message": result.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def ingest_large(
        self,
        size: int = 100000,
        batch_size: int = 10000
    ) -> Dict[str, Any]:
        start_time = time.time()

        all_customers = []
        page = 1

        while True:
            async with httpx.AsyncClient(timeout=120.0) as client:
                url = "http://mock-server:5000/api/customers/large"
                resp = await client.get(url, params={
                    "size": size,
                    "batch": batch_size,
                    "page": page
                })
                resp.raise_for_status()

                import orjson
                data = orjson.loads(resp.content)
                customers = data.get("data", [])

            if not customers:
                break

            all_customers.extend(customers)

            if not data.get("has_more", False):
                break

            page += 1

        df = pl.DataFrame(all_customers)

        for i in range(0, len(df), batch_size):
            batch = df[i:i + batch_size]

            for row in batch.to_dicts():
                customer_id = row.get("customer_id")
                if not customer_id:
                    continue

                clean_record = {
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                    "address": row.get("address"),
                    "date_of_birth": row.get("date_of_birth"),
                    "account_balance": row.get("account_balance", 0)
                }

                self.repository.upsert(customer_id, clean_record)

            self.db.commit()

        total_time = time.time() - start_time
        total_processed = len(all_customers)

        return {
            "status": "success",
            "records_processed": total_processed,
            "message": f"Processed {total_processed:,} records",
            "performance": {
                "total_time_seconds": round(total_time, 2),
                "records_per_second": round(total_processed / total_time) if total_time > 0 else 0,
                "batches_processed": (total_processed + batch_size - 1) // batch_size,
                "batch_size": batch_size
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def get_pipeline_status(self) -> Dict[str, Any]:
        return await self.orchestrator.health_check()

    async def close(self):
        await self.source.close()
