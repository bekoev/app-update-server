from io import BytesIO
from logging import Logger
from uuid import UUID

from fastapi import UploadFile

from app.services.update_files.storage.interface import UpdateFileRepositoryInterface


class UpdateFileService:
    def __init__(
        self,
        repository: UpdateFileRepositoryInterface,
        logger: Logger,
    ) -> None:
        self.repository = repository
        self.logger = logger

    async def create(self, file: UploadFile) -> UUID:
        return await self.repository.create(file)

    async def get_all_ids(self) -> list[UUID]:
        return await self.repository.get_all_ids()

    async def get_by_id(self, object_id: UUID) -> BytesIO:
        return await self.repository.get_by_id(object_id)

    async def delete_by_id(self, object_id: UUID) -> None:
        return await self.repository.delete_by_id(object_id)
