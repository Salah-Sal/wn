from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "WordNet Explorer API"
    debug: bool = True
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5000", "http://0.0.0.0:5000"]
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
