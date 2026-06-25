from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Predicción de Demanda"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "mysql+aiomysql://root:@localhost:3306/tesis_inventario"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    MODELS_PATH: str = "ml_models"
    PREDICTION_CONFIDENCE_LEVEL: float = 0.95

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
