from abc import ABC, abstractmethod
from io import BytesIO

from fastapi import UploadFile


class BLOBRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, object_id: str, file: UploadFile) -> None: ...

    @abstractmethod
    async def get(self, object_id: str) -> BytesIO: ...

    @abstractmethod
    async def delete(self, object_id: str) -> None: ...
