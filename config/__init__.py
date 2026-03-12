"""
Configuration
-------------
Environment-specific configuration classes following the 12-Factor App methodology.
All secrets are loaded from environment variables — never hardcoded.

Usage:
    from config import config_map
    app.config.from_object(config_map["production"])
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration shared across all environments."""

    # ── Core ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    APP_NAME: str = os.environ.get("APP_NAME", "FlaskTemplate")

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    JWT_TOKEN_LOCATION: list = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"

    # ── Cache ─────────────────────────────────────────────────────────────────
    CACHE_TYPE: str = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT: int = 300

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATELIMIT_DEFAULT: str = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL: str = os.environ.get("REDIS_URL", "memory://")

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # ── Pagination ────────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(BaseConfig):
    """Development configuration — verbose logging, SQLite, debug mode."""

    DEBUG: bool = True
    TESTING: bool = False

    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'dev.db')}",
    )
    SQLALCHEMY_ECHO: bool = True  # Log all SQL queries

    CACHE_TYPE: str = "SimpleCache"
    LOG_LEVEL: str = "DEBUG"


class TestingConfig(BaseConfig):
    """Testing configuration — in-memory DB, no rate limiting."""

    DEBUG: bool = True
    TESTING: bool = True

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_ECHO: bool = False

    # Disable rate limiting during tests
    RATELIMIT_ENABLED: bool = False

    # Use faster hashing in tests
    WTF_CSRF_ENABLED: bool = False

    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)


class StagingConfig(BaseConfig):
    """Staging configuration — mirrors production with extra logging."""

    DEBUG: bool = False
    TESTING: bool = False

    SQLALCHEMY_DATABASE_URI: str = os.environ["DATABASE_URL"]
    CACHE_TYPE: str = "RedisCache"
    CACHE_REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    LOG_LEVEL: str = "WARNING"


class ProductionConfig(BaseConfig):
    """Production configuration — hardened, Redis cache, no debug."""

    DEBUG: bool = False
    TESTING: bool = False

    SQLALCHEMY_DATABASE_URI: str = os.environ["DATABASE_URL"]

    # Redis cache
    CACHE_TYPE: str = "RedisCache"
    CACHE_REDIS_URL: str = os.environ["REDIS_URL"]

    # Strict CORS — set your real frontend domain(s)
    CORS_ORIGINS: list = os.environ.get("CORS_ORIGINS", "").split(",")

    # Tighter rate limits in production
    RATELIMIT_DEFAULT: str = "100 per day;30 per hour"

    LOG_LEVEL: str = "ERROR"


# Mapping used by create_app()
config_map: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    # Alias
    "default": DevelopmentConfig,
}
