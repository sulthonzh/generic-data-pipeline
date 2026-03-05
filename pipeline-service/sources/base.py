from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DataSource(ABC):
    @abstractmethod
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def validate(self) -> bool:
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        pass
