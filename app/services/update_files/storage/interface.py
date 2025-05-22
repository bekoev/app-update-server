from abc import ABC, abstractmethod
from io import BytesIO
from uuid import UUID

from fastapi import UploadFile


class BLOBRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, id: UUID, file: UploadFile) -> None: ...

    @abstractmethod
    async def get_by_id(self, object_id: UUID) -> BytesIO: ...

    @abstractmethod
    async def delete_by_id(self, object_id: UUID) -> None: ...
