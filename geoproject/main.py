from fastapi import FastAPI
from geoproject.core.config import get_settings
import uvicorn

settings = get_settings()
app = FastAPI(
    exception_handlers={},
    **settings.fastapi_kwargs,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=True,
    )
