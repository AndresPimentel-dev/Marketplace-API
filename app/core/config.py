from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsClass(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "askjdffgjdasvbfsdavfjvasdfjdvas"
    # se pone para que ignore variables de entorno extras como la db password
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = SettingsClass()
