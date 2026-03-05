from abc import ABC, abstractmethod
from typing import List, Dict, Any


class DataSink(ABC):
    @abstractmethod
    async def write(self, data: List[Dict[str, Any]]) -> int:
        pass

    @abstractmethod
    async def validate(self) -> bool:
        pass

    @property
    @abstractmethod
    def sink_type(self) -> str:
        pass
