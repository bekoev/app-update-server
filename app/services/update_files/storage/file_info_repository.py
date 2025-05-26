from contextlib import AbstractAsyncContextManager
from logging import Logger
from typing import Callable
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.entities.update_file import UpdateFileEntity
from app.models.update_file import UpdateFileInfo, UpdateFileInfoToCreate


class FileInfoRepository:
    def __init__(
        self,
        db_session: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.db_session: Callable[..., AbstractAsyncContextManager[AsyncSession]] = (
            db_session
        )
        self.logger = logger

    async def create(self, new_file_info: UpdateFileInfoToCreate) -> UpdateFileInfo:
        async with self.db_session() as session:
            db_object = UpdateFileEntity(**new_file_info.model_dump())
            session.add(db_object)
            await session.commit()
            await session.refresh(db_object)
            return UpdateFileInfo.model_validate(db_object)

    async def get(self, id: str) -> UpdateFileInfo | None:
        db_id = UUID(hex=id)
        async with self.db_session() as session:
            query = select(UpdateFileEntity).filter_by(id=db_id)
            db_object = (await session.execute(query)).scalar_one_or_none()
            if db_object is None:
                return None
            return UpdateFileInfo.model_validate(db_object)

    async def get_all(self) -> list[UpdateFileInfo]:
        """Get all update file infos ordered by creation timestamp descending."""

        async with self.db_session() as session:
            query = select(UpdateFileEntity).order_by(desc(UpdateFileEntity.created_at))
            db_objects = (await session.execute(query)).scalars().all()
            return TypeAdapter(list[UpdateFileInfo]).validate_python(db_objects)

    async def delete(self, id: str) -> None:
        db_id = UUID(hex=id)
        async with self.db_session() as session:
            query = delete(UpdateFileEntity).filter_by(id=db_id)
            await session.execute(query)
            await session.commit()
