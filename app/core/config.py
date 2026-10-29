from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsClass(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    WEBHOOK_SECRET: str
    # se pone para que ignore variables de entorno extras como la db password
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = SettingsClass()
