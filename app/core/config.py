import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Task Service"
    API_V1_STR: str = "/api/v1"
    
    # Database URLs (Postgres-only)
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None
    
    # Environment state (dev, prod, test)
    ENV_STATE: str = "dev"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = "20/minute"
    
    def get_database_url(self) -> str:
        """
        Returns the appropriate database URL based on the environment.
        """
        if self.ENV_STATE == "test" and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = 'ignore'

settings = Settings()