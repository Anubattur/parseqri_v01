from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # Default to 30 days
    
    # Optional Redis configuration (can be disabled)
    REDIS_URL: Optional[str] = None
    
    # Optional ChromaDB configuration
    CHROMA_PERSIST_DIR: Optional[str] = "./data/chroma_storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()