from io import BytesIO
from logging import Logger

from fastapi import UploadFile

from app.api.errors import ApiNotFoundError
from app.models.update_file import UpdateFileInfo, UpdateFileInfoToCreate
from app.services.update_files.storage.file_info_repository import FileInfoRepository
from app.services.update_files.storage.interfaces import BLOBRepositoryInterface


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

    async def create(self, file: UploadFile, comment: str | None) -> UpdateFileInfo:
        created_info = await self.file_infos.create(
            UpdateFileInfoToCreate(name=file.filename, size=file.size, comment=comment)
        )
        try:
            await self.blob_repository.create(object_id=created_info.id, file=file)
        except Exception:
            await self.file_infos.delete(created_info.id)
            raise
        return created_info

    async def get_all_infos(self) -> list[UpdateFileInfo]:
        return await self.file_infos.get_all()

    async def get_file(self, object_id: str) -> BytesIO:
        try:
            return await self.blob_repository.get(object_id)
        except FileNotFoundError:
            raise ApiNotFoundError

    async def delete_file(self, object_id: str) -> None:
        try:
            await self.blob_repository.delete(object_id)
        except FileNotFoundError:
            raise ApiNotFoundError
