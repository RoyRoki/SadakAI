from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.
    
    Loads configuration from environment variables or a .env file.
    Provides type-safe access to application secrets and constants.
    """
    
    # Database connection string
    DATABASE_URL: str = "sqlite:///./sadakai.db"
    
    # Cloudflare R2 / S3 Storage Configuration
    R2_ENDPOINT: Optional[str] = None
    R2_ACCESS_KEY: Optional[str] = None
    R2_SECRET_KEY: Optional[str] = None
    R2_BUCKET: str = "sadakai-images"
    
    # Security & Machine Learning
    API_KEY: str = "dev_api_key"
    MODEL_PATH: str = "model/weights/best.pt"
    
    # Frontend public variables (replicated for convenience)
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    NEXT_PUBLIC_MAP_CENTER_LAT: float = 26.7
    NEXT_PUBLIC_MAP_CENTER_LNG: float = 88.4
    
    class Config:
        """Pydantic configuration class."""
        # Path to environment file
        env_file = ".env"
        # Allow extra environment variables not defined here
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached instance of the application settings.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()
