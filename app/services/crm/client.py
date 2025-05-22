from urllib.parse import urljoin

from fastapi import status
from httpx import AsyncClient

from app.settings import AppSettings


class CRMClient:
    def __init__(
        self,
        config: AppSettings,
        http_client: AsyncClient,
    ):
        self.http_client = http_client
        self.crm_url = config.crm_url_base

    async def check_token(self, token: str) -> bool:
        response = await self.http_client.post(
            urljoin(self.crm_url, "/1/validate-token"),
            headers={"Authorization": f"Bearer {token}"},
        )
        return response.status_code == status.HTTP_200_OK
