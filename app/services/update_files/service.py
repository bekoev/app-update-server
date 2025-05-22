from io import BytesIO
from logging import Logger
from uuid import UUID

from fastapi import UploadFile

from app.models.update_file import UpdateFileInfo, UpdateFileInfoToCreate
from app.services.update_files.storage.interface import BLOBRepositoryInterface
from app.services.update_files.storage.repository import FileInfoRepository


class UpdateFileService:
    def __init__(
        self,
        repository: BLOBRepositoryInterface,
        file_info_repository: FileInfoRepository,
        logger: Logger,
    ) -> None:
        self.blob_repository = repository
        self.file_infos = file_info_repository
        self.logger = logger

    async def create(
        self, file: UploadFile, info: UpdateFileInfoToCreate
    ) -> UpdateFileInfo:
        created_info = await self.file_infos.create(info)
        await self.blob_repository.create(id=created_info.id, file=file)
        return created_info

    async def get_all_infos(self) -> list[UpdateFileInfo]:
        return await self.file_infos.get_all()

    async def get_file_by_id(self, object_id: UUID) -> BytesIO:
        return await self.blob_repository.get_by_id(object_id)
