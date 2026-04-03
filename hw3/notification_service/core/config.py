from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Notification Service"
    DATABASE_URL: str = "postgresql://postgres:postgres@notification-db:5432/notification_db"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
