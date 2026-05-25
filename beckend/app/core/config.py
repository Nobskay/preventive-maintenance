"""
Configuration management using Pydantic Settings.

The backend treats environment variables as the deployment contract. Keeping
all operational settings here makes Docker, local development, and hosted
deployments use the same configuration surface.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import logging
import json

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    """Application settings and configuration"""
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_TITLE: str = "Predictive Maintenance API"
    API_VERSION: str = "1.0.0"
    ENABLE_DOCS: bool = True
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "app_user"
    DB_PASSWORD: str = "app_password"
    DB_NAME: str = "predictive_maintenance"
    DB_ECHO: bool = False  # Log all database queries
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    AUTO_CREATE_TABLES: bool = False
    AUTO_SEED_DATA: bool = False
    
    # Server Configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost"
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Features
    ENABLE_MAIL: bool = False
    MAIL_FROM: str = "noreply@maintenance.local"
    
    # ML/AI Features (Future)
    ENABLE_ML_PREDICTIONS: bool = False
    ML_MODEL_PATH: str = "/models/"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Support either JSON arrays or comma-separated env var values."""
        value = self.CORS_ORIGINS.strip()
        if value.startswith("["):
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    
    @property
    def sqlalchemy_database_url(self) -> str:
        """Construct SQLAlchemy database URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Load settings
settings = Settings()

# Configure logging
def configure_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

configure_logging()
