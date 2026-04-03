from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Log Intelligence Service"
    DATABASE_URL: str = "postgresql://postgres:postgres@log-db:5432/logs_db"
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-haiku-20240307"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
