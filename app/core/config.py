import os
from typing import Any, Dict, List, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: Optional[PostgresDsn] = None

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Gmail API settings
    GMAIL_USER_EMAIL: str = os.getenv(
        "GMAIL_USER_EMAIL", "raghavendraks.work@gmail.com"
    )
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    GMAIL_CREDENTIALS_PATH: str = os.getenv(
        "GMAIL_CREDENTIALS_PATH", "credentials.json"
    )
    GMAIL_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "GMAIL_SERVICE_ACCOUNT_PATH", "service-account.json"
    )

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            path=f"{os.getenv('POSTGRES_DB', 'email_rules')}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
