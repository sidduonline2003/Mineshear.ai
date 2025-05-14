from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Tools Website Backend"
    API_V1_STR: str = "/api/v1"

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[str] = None # Path to your Firebase service account key JSON file

    # LLM API (Example)
    # OPENAI_API_KEY: Optional[str] = None

    # Image Scraping API (Example)
    # UNSPLASH_ACCESS_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" # Ignore extra fields from .env

settings = Settings()
