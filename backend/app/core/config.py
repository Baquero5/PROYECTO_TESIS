from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Prediccion de Demanda"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "mysql+aiomysql://root:123456@localhost:3307/tesis_inventario"
    SECRET_KEY: str = secrets.token_hex(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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
