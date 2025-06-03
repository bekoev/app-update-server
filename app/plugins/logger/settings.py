from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingLVL(StrEnum):
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggerSettings(BaseSettings):
    level: LoggingLVL = LoggingLVL.INFO
    developer_logger: bool | None = None
    file_storage_path: str = "/persistent/log_storage"
    file_max_size: int = 0
    file_backup_count: int = 0

    model_config = SettingsConfigDict(
        env_prefix="logger_",
        env_file=".env",
        frozen=True,
        extra="ignore",
    )


@lru_cache
def get_config():
    return LoggerSettings()
