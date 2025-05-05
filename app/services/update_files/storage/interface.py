from abc import ABC, abstractmethod
from io import BytesIO
from uuid import UUID

from fastapi import UploadFile


class UpdateFileRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, file: UploadFile) -> UUID: ...

    @abstractmethod
    async def get_all_ids(self) -> list[UUID]: ...

    @abstractmethod
    async def get_by_id(self, object_id: UUID) -> BytesIO: ...

    @abstractmethod
    async def delete_by_id(self, object_id: UUID) -> None: ...
