from io import BytesIO
from logging import Logger
from pathlib import Path

import aiofiles
import aiofiles.os
from fastapi import UploadFile

from app.services.update_files.storage.interfaces import BLOBRepositoryInterface
from app.settings import AppSettings


class BLOBRepository(BLOBRepositoryInterface):
    def __init__(
        self,
        config: AppSettings,
        logger: Logger,
    ):
        self.storage_path = Path(config.file_storage_path)
        self.logger = logger

    async def create(self, object_id: str, file: UploadFile) -> None:
        """Raises: OSError"""

        async with aiofiles.open(self.storage_path / object_id, mode="wb") as f:
            # load the entire file into memory
            content = await file.read()
            self.logger.debug(f"Writing {file.filename=}")
            await f.write(content)

    async def get(self, object_id: str) -> BytesIO:
        """Raises: FileNotFoundError and other OSError-based exceptions"""

        async with aiofiles.open(self.storage_path / object_id, mode="rb") as f:
            # load the entire file into memory
            content = await f.read()
            return BytesIO(content)

    async def delete(self, object_id: str) -> None:
        await aiofiles.os.remove(self.storage_path / object_id)
