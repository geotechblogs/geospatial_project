from fastapi import FastAPI
from geoproject.api.v1.location import router as locations_router
from geoproject.api.v1.building_footprints import router as building_footprints_router
from geoproject.core.config import get_settings
import uvicorn

settings = get_settings()

app = FastAPI(
    exception_handlers={},
    **settings.fastapi_kwargs,
)

# Set the full resource path as the prefix.
# This means /api/v1/locations is the new base for the router.
app.include_router(locations_router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(
    building_footprints_router,
    prefix="/api/v1/building_footprints",
    tags=["building_footprints"],
)


@app.get("/")
def read_root():
    # Updated message to reflect the correct access path
    return {"message": "geoproject app running! Access locations at /api/v1/locations"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
