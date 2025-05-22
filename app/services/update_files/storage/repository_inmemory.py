from io import BytesIO
from uuid import UUID

from fastapi import UploadFile

from app.services.update_files.storage.interface import BLOBRepositoryInterface

files: dict[UUID, bytes] = {}


class BLOBRepository(BLOBRepositoryInterface):
    async def create(self, id: UUID, file: UploadFile) -> None:
        files[id] = await file.read()

    async def get_by_id(self, object_id: UUID) -> BytesIO:
        return BytesIO(files[object_id])

    async def delete_by_id(self, object_id: UUID) -> None:
        if object_id in files:
            del files[object_id]
