from pathlib import Path

from pydantic import BaseSettings, Field


# Настройки
class TestSettings(BaseSettings):
    pg_host: str = Field("auth_postgres", env="API_PG_HOST")
    pg_port: str = Field("5432", env="API_PG_PORT")
    pg_user: str = Field("admin_auth_db", env="AUTH_POSTGRES_USER")
    pg_password: str = Field("123qwe", env="AUTH_POSTGRES_PASSWORD")
    redis_host: str = Field("auth_redis", env="AUTH_REDIS_HOST")
    redis_port: str = Field("6379", env="AUTH_REDIS_PORT")
    service_host: str = Field("auth_api", env="AUTH_API_HOST")
    service_port: str = Field("8000", env="AUTH_API_PORT")
    service_url: str = f"http://auth_api:8000"
    base_dir: str = str(Path(__file__).resolve().parent)


test_settings = TestSettings()
