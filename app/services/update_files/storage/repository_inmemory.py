from io import BytesIO
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.services.update_files.storage.interface import UpdateFileRepositoryInterface

files: dict[UUID, bytes] = {}


class UpdateFileRepository(UpdateFileRepositoryInterface):
    async def create(self, file: UploadFile) -> UUID:
        new_id = uuid4()
        files[new_id] = await file.read()
        return new_id

    async def get_all_ids(self) -> list[UUID]:
        return list(files.keys())

    async def get_by_id(self, object_id: UUID) -> BytesIO:
        return BytesIO(files[object_id])

    async def delete_by_id(self, object_id: UUID) -> None:
        if object_id in files:
            del files[object_id]
