from app.api.errors import ApiUnauthorizedError
from app.services.crm.client import CRMClient
from app.settings import AppSettings


class AuthService:
    def __init__(
        self,
        config: AppSettings,
        crm_client: CRMClient,
    ):
        self.config = config
        self.crm = crm_client

    async def check_access_by_api_key(self, scheme: str, token: str) -> None:
        if all((scheme == "Bearer", token == self.config.api_key)):
            return None
        raise ApiUnauthorizedError

    async def check_access_by_crm_token(self, scheme: str, token: str) -> None:
        if scheme != "Bearer":
            raise ApiUnauthorizedError
        if not await self.crm.check_token(token):
            raise ApiUnauthorizedError
        return None
