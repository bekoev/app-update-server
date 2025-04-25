from httpx import AsyncClient

from tests.integration.user_service.dataset import users_data


async def test_get_users(app_client: AsyncClient):
    response = await app_client.get("/users")
    assert response.status_code == 200
    result = response.json()
    assert sorted(result, key=lambda x: x["id"]) == sorted(
        users_data, key=lambda x: x["id"]
    )
