from datetime import datetime

from httpx import AsyncClient

from app.settings import AppSettings


async def test_getting_update_file_infos(
    app_client: AsyncClient, app_config: AppSettings, update_files: list[dict]
):
    headers = {"Authorization": f"Bearer {app_config.api_key}"}
    response = await app_client.get("/service/update-files", headers=headers)
    assert response.status_code == 200
    result = response.json()
    fields = ("name", "size", "comment")
    for resulted, expected in zip(
        sorted(result, key=lambda x: x["name"]),
        sorted(update_files, key=lambda x: x["name"]),
    ):
        assert all((resulted.get(f) == expected.get(f) for f in fields))
        assert datetime.fromisoformat(resulted["created_at"]) == expected["created_at"]
