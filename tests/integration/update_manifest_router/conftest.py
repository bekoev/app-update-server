import pytest

from app.core.containers import Container
from app.entities.update_manifest import UpdateManifestEntity
from tests.integration.utils.db.db_seeder import DbTestDataHandler


@pytest.fixture
def update_manifest() -> dict:
    return {
        "version": "1.2.0",
        "url": "https://example.com/downloads/app-1.2.0.zip",
    }


@pytest.fixture(autouse=True)
async def prepare_db_data(db_client, update_manifest):
    """Prepare test DB for tests."""

    restore_db = DbTestDataHandler(db_client)
    restore_db.add_entity_info(UpdateManifestEntity, [update_manifest])

    await restore_db.clear_database()
    await restore_db.seed_database()
    yield
    await restore_db.clear_database()


class CRMClientMock:
    async def check_token(self, token: str) -> bool:
        return token == "crm-token-123"


@pytest.fixture(autouse=True)
def mock_crm_client(app_container: Container):
    app_container.crm_client.override(CRMClientMock())
    yield
    app_container.crm_client.reset_override()
