from contextlib import AbstractAsyncContextManager
from logging import Logger
from typing import Callable

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.entities.update_manifest import UpdateManifestEntity
from app.models.update_manifest import UpdateManifest
from app.services.update_manifest.storage.interface import (
    UpdateManifestRepositoryInterface,
)


class UpdateManifestRepositoryDB(UpdateManifestRepositoryInterface):
    def __init__(
        self,
        db_session: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.db_session: Callable[..., AbstractAsyncContextManager[AsyncSession]] = (
            db_session
        )
        self.logger = logger

    async def set(self, new_manifest: UpdateManifest) -> None:
        async with self.db_session() as session:
            await self._remove_all_txn(session)
            db_object = UpdateManifestEntity(
                version=new_manifest.version,
                url=new_manifest.url,
            )
            session.add(db_object)
            await session.commit()

    async def get(self) -> UpdateManifest | None:
        async with self.db_session() as session:
            query = select(UpdateManifestEntity)
            db_object = (await session.execute(query)).scalar_one_or_none()
            if db_object is None:
                return None
            return UpdateManifest.model_validate(db_object, from_attributes=True)

    async def delete(self) -> None:
        async with self.db_session() as session:
            await self._remove_all_txn(session)
            await session.commit()

    async def _remove_all_txn(self, session: AsyncSession) -> None:
        await session.execute(
            text(f"TRUNCATE TABLE {UpdateManifestEntity.__tablename__}")
        )
