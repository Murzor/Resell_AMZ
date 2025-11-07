from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_PASSWORD: str
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Sentry
    SENTRY_DSN: str = ""
    
    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

