from datetime import datetime

import pytest
from app.core.containers import Container

from app.entities.user import UserEntity
from tests.integration.user_service.dataset import users_data
from tests.integration.utils.db.db_seeder import DbTestDataHandler


@pytest.fixture(scope="function", autouse=True)
async def prepare_db_data(db_client):
    """Prepare test DB for tests."""
    print(f"DB FOR TESTS: {db_client.config.url.split('/')[-1]}")
    entity_data = [
        {k: datetime.fromisoformat(v) if k == "created_at" else v for k, v in u.items()}
        for u in users_data
    ]
    restore_db = DbTestDataHandler(db_client, UserEntity, entity_data)
    # If necessary, add more entities:
    # restore_db.add_entity_info(Users, entity_data)

    await restore_db.clear_database()
    # run_migrations("migrations", core_config.db_url_test)  # TODO
    await restore_db.seed_database()
    # restart_index(engine=restore_db.engine)  # TODO check if needed
    # await asyncio.sleep(1)  # TODO check if needed
    yield
    await restore_db.clear_database()


@pytest.fixture(scope="function")
def app_container(app) -> Container:
    return app.state.container


@pytest.fixture(scope="function")
def user_repo(app_container: Container):
    return app_container.user_repository()
