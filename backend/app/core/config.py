from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Prediccion de Demanda"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "mysql+aiomysql://root:123456@localhost:3307/tesis_inventario"
    SECRET_KEY: str = "smartinventory-tesis-2026-secret-key-fijo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    MODELS_PATH: str = "ml_models"
    PREDICTION_CONFIDENCE_LEVEL: float = 0.95

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
