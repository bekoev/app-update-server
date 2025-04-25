from datetime import datetime, timedelta

import pytest
from app.api.errors import EntityNotFound
from app.models.user import User, UserToCreate
from app.services.user.user_repository import UserRepository
from tests.integration.user_service import dataset


async def test_user_repo(user_repo: UserRepository):
    """Provide test coverage for app/services/base_repository.py"""

    test_started = datetime.now()
    new_user = await user_repo.create(
        UserToCreate(created_at=test_started + timedelta(seconds=1))
    )
    assert new_user.id
    two_more_users = [
        await user_repo.create(
            UserToCreate(created_at=test_started + timedelta(seconds=2))
        ),
        await user_repo.create(
            UserToCreate(created_at=test_started + timedelta(seconds=3))
        ),
    ]
    result = await user_repo.get_all()
    first_entry: User = result[0]
    assert str(first_entry.id) == dataset.users_data[0]["id"]
    assert len(result) == len(dataset.users_data) + 3
    assert sum(u.created_at > test_started for u in result) == 3

    new_user.created_at = test_started - timedelta(seconds=10)
    await user_repo.update(new_user)
    result = await user_repo.get_all()
    assert sum(u.created_at > test_started for u in result) == 2

    two_more_users = [
        await user_repo.create(
            UserToCreate(created_at=test_started + timedelta(seconds=4))
        ),
        await user_repo.create(
            UserToCreate(created_at=test_started + timedelta(seconds=5))
        ),
    ]
    result = await user_repo.get_all()
    assert sum(u.created_at > test_started for u in result) == 4
    two_more_users[0].created_at = test_started - timedelta(seconds=11)
    two_more_users[1].created_at = test_started - timedelta(seconds=12)

    await user_repo.bulk_update(two_more_users)
    result = await user_repo.get_all()
    assert sum(u.created_at > test_started for u in result) == 2
    assert len(result) == 8

    await user_repo.delete_by_id(dataset.users_data[0]["id"])
    result = await user_repo.get_all()
    assert len(result) == 7

    second_user = await user_repo.get_by_id(dataset.users_data[1]["id"])
    assert second_user.created_at.isoformat() == dataset.users_data[1]["created_at"]

    with pytest.raises(EntityNotFound):
        await user_repo.get_by_id(dataset.users_data[0]["id"])
