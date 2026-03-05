from typing import List, Dict, Any, Optional
from sources.base import DataSource
from sinks.base import DataSink
from models.schemas import IngestResponse


class PipelineOrchestrator:
    def __init__(
        self,
        source: DataSource,
        sink: DataSink,
        batch_size: int = 1000
    ):
        self.source = source
        self.sink = sink
        self.batch_size = batch_size

    async def execute(self) -> IngestResponse:
        try:
            data = await self.source.fetch()

            if not data:
                return IngestResponse(
                    status="success",
                    records_processed=0,
                    message="No data to process"
                )

            total = len(data)
            processed = 0

            for i in range(0, total, self.batch_size):
                batch = data[i:i + self.batch_size]
                count = await self.sink.write(batch)
                processed += count

            return IngestResponse(
                status="success",
                records_processed=processed,
                message=f"Successfully processed {processed} records"
            )

        except Exception as e:
            return IngestResponse(
                status="error",
                records_processed=0,
                message=str(e)
            )

    async def validate(self) -> Dict[str, bool]:
        return {
            "source": await self.source.validate(),
            "sink": await self.sink.validate()
        }

    async def health_check(self) -> Dict[str, Any]:
        validation = await self.validate()
        return {
            "status": "healthy" if all(validation.values()) else "unhealthy",
            "source_type": self.source.source_type,
            "sink_type": self.sink.sink_type,
            "validation": validation
        }
