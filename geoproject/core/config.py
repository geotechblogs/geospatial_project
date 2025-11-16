from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
import multiprocessing
import tempfile
from functools import lru_cache
from typing import Any, Callable, Dict

load_dotenv()

SupplySettings = Callable[..., "ApplicationConfig"]


class ApplicationConfig(BaseSettings):
    log_level: str = "INFO"

    workers_per_core: int = 1
    max_workers: int = 2
    workers: int | None = min(
        workers_per_core * multiprocessing.cpu_count(), max_workers
    )
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    graceful_timeout: int = 240
    timeout: int = 240
    keep_alive: int = 5
    worker_class: str = "uvicorn.workers.UvicornWorker"
    reload: bool = True

    # Fastapi
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "geoproject"
    version: str = "0.0.1"

    loguru_diagnose: bool = False
    loguru_backtrace: bool = False

    delivery_storage_path: str = tempfile.gettempdir()
    model_config = SettingsConfigDict(case_sensitive=False, validate_assignment=True)

    # database
    db_user: str = ""
    db_password: str = ""
    db_name: str = "postgres"

    @property
    def loguru_kwargs(self) -> Dict[str, Any]:
        """This returns a dictionary of the most commonly used keyword
        arguments when initializing a loguru instance.
        """
        loguru_kwargs: Dict[str, Any] = {
            "loguru_diagnose": self.loguru_diagnose,
            "loguru_backtrace": self.loguru_backtrace,
        }
        return loguru_kwargs

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        fastapi_kwargs: Dict[str, Any] = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "description": "NeoRPG game version",
            "version": self.version,
            "description": "A FastAPI service for geospatial data processing.",
        }
        return fastapi_kwargs

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@localhost/{self.db_name}"

@lru_cache()
def get_settings() -> ApplicationConfig:
    """This function returns a cached instance of the Settings object.

    Caching is used to prevent re-reading the environment every time the
    settings are used in an endpoint.
    """
    return ApplicationConfig()
