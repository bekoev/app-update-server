from io import BytesIO
from logging import Logger

from fastapi import UploadFile

from app.api.errors import ApiNotFoundError
from app.models.update_file import UpdateFileInfo, UpdateFileInfoToCreate
from app.services.update_files.storage.file_info_repository import FileInfoRepository
from app.services.update_files.storage.interfaces import BLOBRepositoryInterface
from app.settings import AppSettings


class UpdateFileService:
    def __init__(
        self,
        repository: BLOBRepositoryInterface,
        file_info_repository: FileInfoRepository,
        config: AppSettings,
        logger: Logger,
    ) -> None:
        self.blob_repository = repository
        self.file_infos = file_info_repository
        self.capacity = config.file_storage_capacity
        self.logger = logger

    async def create(self, file: UploadFile, comment: str | None) -> UpdateFileInfo:
        await self._ensure_capacity()
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

    async def _ensure_capacity(self) -> None:
        current_files = await self.file_infos.get_all()
        # Expect that current_files are already sorted by creation time (desc)
        current_count = len(current_files)
        if current_count < self.capacity:
            return

        # Leave space for one extra file by removing oldest files
        files_to_remove = current_count - self.capacity + 1
        for file in current_files[-files_to_remove:]:
            try:
                await self.blob_repository.delete(file.id)
            except FileNotFoundError:
                pass
            await self.file_infos.delete(file.id)
