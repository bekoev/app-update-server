from datetime import datetime

import pytest

from app.entities.update_file import UpdateFileEntity
from tests.integration.utils.db.db_seeder import DbTestDataHandler


@pytest.fixture
def update_files() -> list[dict]:
    return [
        {
            "name": f"file_{i}.bin",
            "size": i * 1000,
            "comment": f"Comment {i}",
            "created_at": datetime.fromisoformat(f"2025-05-31T16:0{i}:05Z"),
        }
        for i in range(5)
    ]


@pytest.fixture(autouse=True)
async def prepare_db_data(db_client, update_files):
    """Prepare test DB for tests."""

    restore_db = DbTestDataHandler(db_client)
    restore_db.add_entity_info(UpdateFileEntity, update_files)

    await restore_db.clear_database()
    await restore_db.seed_database()
    yield
    await restore_db.clear_database()
