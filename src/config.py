from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_REGION: str
    MINIO_BUCKET: str
    MINIO_ENDPOINT_URL: str
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file="../.env")

    # class Config:
    #     env_file = ".env"

settings = Settings()
