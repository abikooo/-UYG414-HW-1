from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API key that clients need to send in the X-API-Key header
    API_KEY: str = "dev-secret-key"

    # set this in .env to use real OpenAI analysis; leave empty to use the fallback
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    LOG_LEVEL: str = "INFO"

    APP_NAME: str = "SmartText API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
