from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth Service"
    DATABASE_URL: str = "postgresql://postgres:postgres@auth-db:5432/auth_db"
    JWT_SECRET_KEY: str = "change-this-in-production-long-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
