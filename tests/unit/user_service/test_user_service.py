from app.models.user import User
from app.services.user.user_service import UserService
from tests.unit.user_service.dataset import users_data


async def test_get_users(user_service: UserService):
    users: list[User] = await user_service.get_all()
    users = [u.model_dump() for u in users]
    for user in users:
        for key, value in user.items():
            if key == "created_at":
                user[key] = value.isoformat()
            if key == "id":
                user[key] = str(value)

    assert sorted(users, key=lambda x: x["id"]) == sorted(
        users_data, key=lambda x: x["id"]
    )
