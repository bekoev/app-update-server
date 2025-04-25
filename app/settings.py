from pydantic_settings import BaseSettings, SettingsConfigDict
from app.plugins.logger.settings import LoggerSettings
from app.plugins.postgres.settings import PostgresSettings


class AppSettings(BaseSettings):
    """General settings app"""

    name: str = "AppName"
    version: str = "0.0.0"
    host: str = "localhost"
    port: int = 8080
    reloader: bool = False
    developer_router: bool = True
    root_path: str = ""
    openapi_url: str = "/openapi.json"

    model_config = SettingsConfigDict(
        env_prefix="app_",
        env_file=".env",
        frozen=True,
        extra="ignore",
    )


class MainSettings:
    def __init__(
        self,
        db: PostgresSettings,
        logger: LoggerSettings,
        app: AppSettings,
    ) -> None:
        self.db = db
        self.logger = logger
        self.app = app
