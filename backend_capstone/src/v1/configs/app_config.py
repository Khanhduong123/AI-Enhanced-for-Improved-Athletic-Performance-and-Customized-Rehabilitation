import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List, Union

class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables with sensible defaults
    """
    # App config
    APP_NAME: str = "Exercise Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    
    # MongoDB settings
    MONGO_URI: str = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "exercise_tracker_db")
    
    # Security settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-for-development-only")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Storage settings
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR", "uploaded_videos")
    TEMP_DIR: str = os.environ.get("TEMP_DIR", "temp_videos")
    MAX_UPLOAD_SIZE: int = int(os.environ.get("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))  # 50MB
    
    # CORS settings
    CORS_ORIGINS: Union[List[str], str] = "*"
    
    # Logging settings
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # Server settings
    PORT: int = int(os.environ.get("PORT", "7860"))
    
    # Monitoring settings
    GRAFANA_USER: Optional[str] = None
    GRAFANA_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"  # Allow extra fields in the settings
        
    def get_cors_origins(self) -> List[str]:
        """Convert CORS_ORIGINS to a list if it's a string"""
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

@lru_cache()
def get_settings() -> AppSettings:
    """
    Get cached application settings
    Returns a singleton instance of AppSettings
    """
    return AppSettings()

# Export settings instance for easy import
settings = get_settings() 