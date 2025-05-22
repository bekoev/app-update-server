from collections.abc import AsyncGenerator

from httpx import AsyncClient


async def http_client_session() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient() as session:
        yield session
