from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg2://app_user:app_password@db:5432/llm_sql_lab"
    openai_base_url: str = "http://host.docker.internal:1234/v1"
    openai_api_key: str = "lm-studio"
    openai_model: str = "meta-llama-3-8b-instruct"
    default_scenario: str = "C0"
    log_dir: str = "logs"
    allow_write_operations: bool = False
    ablation_disabled_layer: str = "output_filter"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
