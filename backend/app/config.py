"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "TeamFlow"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: int
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./teamflow.db"
    
    # Web API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
