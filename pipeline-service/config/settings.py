from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os


class Settings(BaseSettings):
    project_name: str = "Customer Pipeline Service"
    version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")

    database_url: str = Field(
        default="postgresql://postgres:password@postgres:5432/customer_db",
        env="DATABASE_URL"
    )
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_pre_ping: bool = True

    mock_server_url: str = Field(
        default="http://mock-server:5000",
        env="MOCK_SERVER_URL"
    )

    batch_size: int = Field(default=1000, env="BATCH_SIZE")
    timeout: float = Field(default=60.0, env="TIMEOUT")

    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=4, env="WORKERS")

    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    @validator("environment")
    def validate_environment(cls, v):
        return v.lower()

    @validator("log_level")
    def validate_log_level(cls, v):
        return v.upper()

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
