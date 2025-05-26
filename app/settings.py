from pydantic_settings import BaseSettings, SettingsConfigDict

from app.plugins.logger.settings import LoggerSettings
from app.plugins.postgres.settings import PostgresSettings


class AppSettings(BaseSettings):
    """General settings app"""

    name: str = "app-update-service"
    version: str = "0.0.0"
    host: str = "localhost"
    port: int = 8080
    reloader: bool = False
    root_path: str = ""
    openapi_url: str = "/openapi.json"
    api_key: str = ""
    crm_url_base: str = ""
    file_storage_path: str = "/persistent/file_storage"
    file_storage_capacity: int = 10

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
