from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/data_collector"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    crawler_concurrent_requests: int = 16
    crawler_download_delay: float = 1.0
    crawler_proxy_enabled: bool = False
    crawler_proxy_url: str = ""

    default_source: str = "brasilapi"
    cnpja_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
