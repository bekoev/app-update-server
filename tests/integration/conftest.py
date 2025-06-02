import os
from collections.abc import AsyncGenerator

import httpx
import pytest
from dependency_injector import providers

from app.api.server import create_app
from app.core.containers import Container, container
from app.plugins.postgres.plugin import PostgresPlugin
from app.plugins.postgres.settings import PostgresSettings
from app.settings import AppSettings


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
async def app_client(app) -> AsyncGenerator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://0.0.0.0") as ac:
        yield ac


@pytest.fixture()
def app_container(app) -> Container:
    return app.state.container


@pytest.fixture()
def db_client(app_container: Container) -> PostgresPlugin:
    return app_container.db()


@pytest.fixture()
def app_config(app_container: Container) -> AppSettings:
    return app_container.config().app
