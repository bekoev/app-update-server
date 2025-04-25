from __future__ import annotations

from asyncio import current_task, get_event_loop
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import Logger
from typing import Any

import asyncpg  # type: ignore
from asyncpg import Connection as AsyncConnection
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.plugins.base.plugin import Plugin
from app.plugins.postgres.settings import PostgresSettings


class PostgresPlugin(Plugin):
    healthcheck_name: str = "PostgreSQL"

    def __init__(self, logger: Logger, config: PostgresSettings):
        super().__init__(logger)
        self.config = config
        # self.listener: AsyncConnection | None = None
        self.engine = create_async_engine(url=self.config.url, **self.config.opts)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            ),
            scopefunc=current_task,
        )

    # TODO Integrate plugins to the app's lifecycle
    async def on_startup(self) -> None:
        self.listener: AsyncConnection = await asyncpg.connect(
            self.config.url.replace("+asyncpg", ""),
            loop=get_event_loop(),
            **self.config.opts,
        )

    # TODO Integrate plugins to the app's lifecycle
    async def on_shutdown(self):
        await self._session_factory.close_all()
        await self._session_factory.remove()
        await self.engine.dispose()
        await self.listener.close()

    async def ping(self):
        async with self.engine.begin() as connection:
            return (await connection.execute(text("SELECT 1;"))).one() == (1,)

    # TODO Use in healthchecks or remove
    async def ping_listener(self) -> bool:
        return not self.listener.is_closed()

    async def health_check(self) -> dict[str, Any]:
        return {
            "url": self.config.url,
            "pong": await self.ping(),
        }

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        session: AsyncSession = self._session_factory()

        try:
            yield session
        except Exception as e:
            await session.rollback()

            raise e
        finally:
            await session.close()
            await self._session_factory.remove()
