from datetime import datetime

import pytest
from dependency_injector import providers

from app.core.containers import container
from app.models.user import User
from app.services.user.user_service import UserService
from tests.unit.user_service.dataset import users_data


class UserRepositoryMock:
    async def get_all(self) -> list[User]:
        return [
            User(created_at=datetime.fromisoformat(u["created_at"]), id=u["id"])
            for u in users_data
        ]


@pytest.fixture(scope="package")
async def user_service():
    """Mock UserService dependencies."""
    container.user_service.override(
        providers.Factory(
            UserService, repository=UserRepositoryMock(), logger=container.logger
        )
    )
    yield container.user_service()
    container.user_service.reset_override()
