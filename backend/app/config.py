from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str
    postgres_url: str = "postgresql+asyncpg://nexus:nexus123@localhost:5432/nexus_db"
    redis_url: str = "redis://localhost:6379"
    chroma_persist_dir: str = "./chroma_data"
    environment: str = "development"
    secret_key: str = "nexus-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()