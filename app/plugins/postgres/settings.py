from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    protocol: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 5432

    user: str = "user"
    password: str = "password"

    db: str = "test"

    model_config = SettingsConfigDict(
        env_prefix="postgres_",
        env_file=".env",
        frozen=True,
        extra="ignore",
    )

    @property
    def url(self):
        _url = (
            f"{self.protocol}://{self.user}"
            f":{self.password}@{self.host}:{self.port}/{self.db}"
        )
        return _url

    @property
    def opts(self):
        return {}
