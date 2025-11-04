import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"

    AUTH_PASSWORD: str = "QWERTY"

    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "hackathon"

    FLAIR_MODEL_NAME: str = "flair/ner-english-large"
    FLAIR_CACHE_DIR: str = "./models/flair_cache"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_WORKERS: int = 4

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 200

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    ERROR_LOG_RETENTION_DAYS: int = 30
    ERROR_LOG_AUTO_CLEANUP: bool = True
    ERROR_LOG_CLEANUP_RESOLVED_ONLY: bool = True

    DETECT_INVALID_ENTITIES: int = 0

    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: str = "pdf,docx,doc,txt"

    RATE_LIMIT_PER_HOUR: int = 1000

    TESSERACT_CMD: str = "/usr/bin/tesseract"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "auto"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ALLOWED_EXTENSIONS_LIST(self) -> list:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()

