import pytest

from app.core.containers import Container
from tests.integration.utils.db.db_seeder import DbTestDataHandler


@pytest.fixture(scope="function", autouse=True)
async def prepare_db_data(db_client):
    """Prepare test DB for tests."""

    restore_db = DbTestDataHandler(db_client)
    # If necessary, add more entities:
    # restore_db.add_entity_info(Users, entity_data)

    await restore_db.clear_database()
    await restore_db.seed_database()
    yield
    await restore_db.clear_database()


@pytest.fixture(scope="function")
def app_container(app) -> Container:
    return app.state.container
