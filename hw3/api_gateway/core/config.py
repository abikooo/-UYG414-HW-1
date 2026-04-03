from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    LOG_SERVICE_URL: str = "http://log-service:8002"
    JWT_SECRET_KEY: str = "change-this-in-production-long-secret"
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
