import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the application."""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Storage paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "storage/uploads")
    PROCESSED_FOLDER: str = os.path.join(BASE_DIR, "storage/processed")
    REPORTS_FOLDER: str = os.path.join(BASE_DIR, "storage/reports")
    
    # Whisper Model settings
    WHISPER_MODEL: str = "base"
    
    class Config:
        env_file = ".env"  # Load settings from .env file if available

settings = Settings()