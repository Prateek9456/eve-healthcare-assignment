from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://eve:evepassword@localhost:5432/eve_diagnostics"
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
