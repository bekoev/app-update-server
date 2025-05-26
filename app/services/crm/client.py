from logging import Logger
from urllib.parse import urljoin

from fastapi import status
from httpx import AsyncClient

from app.settings import AppSettings


class CRMClient:
    def __init__(
        self,
        config: AppSettings,
        http_client: AsyncClient,
        logger: Logger,
    ):
        self.http_client = http_client
        self.crm_url = config.crm_url_base
        self.logger = logger

    async def check_token(self, token: str) -> bool:
        self.logger.debug("Calling CRM/1/validate-token...")
        response = await self.http_client.post(
            urljoin(self.crm_url, "/1/validate-token"),
            headers={"Authorization": f"Bearer {token}"},
        )
        self.logger.debug(f"Called CRM/1/validate-token: {response.status_code=}")
        return response.status_code == status.HTTP_200_OK
