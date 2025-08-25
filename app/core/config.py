from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # JWT Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # App Settings
    project_name: str = "FastAPI"
    version: str = "1.0.0"
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()