from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Log Intelligence Service"
    API_KEY: str = "dev-secret-key"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/logs_db"
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-haiku-20240307"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
