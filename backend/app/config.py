"""
Application configuration using Pydantic Settings.

Loads database URL and app settings from environment variables
or a .env file. This separates configuration from code — a core
principle of twelve-factor app design.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central configuration class.

    Attributes:
        APP_NAME:       Display name of the application.
        DEBUG:          Toggle debug mode (verbose logging, auto-reload).
        DATABASE_URL:   SQLAlchemy-compatible connection string.
                        Defaults to a local SQLite file for development.
        SECRET_KEY:     Key used for JWT signing and other crypto operations.
        ALGORITHM:      JWT signing algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES: Token lifetime in minutes.
    """

    APP_NAME: str = "Job Finder API"
    DEBUG: bool = True

    # Database — default to SQLite for easy local development
    DATABASE_URL: str = "sqlite:///./job_finder.db"

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance used across the application
settings = Settings()
