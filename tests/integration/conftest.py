import os

import httpx
import pytest
from dependency_injector import providers

from app.api.server import create_app
from app.core.containers import container
from app.plugins.postgres.plugin import PostgresPlugin
from app.plugins.postgres.settings import PostgresSettings


@pytest.fixture(scope="session", autouse=True)
def mock_db_for_tests():
    """Point tests to a separate database."""
    os.environ["postgres_db"] = "autotest"
    container.db.override(
        providers.Singleton(
            PostgresPlugin,
            logger=container.logger.provided,
            config=PostgresSettings(),
        )
    )
    yield
    container.db.reset_override()


@pytest.fixture(scope="session")
def app():
    return create_app(container)


@pytest.fixture(scope="session")
async def app_client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://0.0.0.0") as ac:
        yield ac


@pytest.fixture(scope="session")
def db_client(app):
    return container.db()
