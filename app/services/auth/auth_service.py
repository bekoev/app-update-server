from app.api.errors import ApiUnauthorizedError
from app.settings import AppSettings


class AuthService:
    def __init__(
        self,
        config: AppSettings,
    ):
        self.config = config

    async def check_client_app_access(self, scheme: str, token: str) -> None:
        if all((scheme == "Bearer", token == self.config.api_key)):
            return None
        raise ApiUnauthorizedError
