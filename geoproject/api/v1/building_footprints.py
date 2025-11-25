from fastapi import APIRouter, Depends
from geoproject.config.database import get_session
from geoproject.services.building_footprints import get_building_footprints
from geoproject.models.building_footprints import (
    BuildingFootprints,
    BuildingFootprintRequest,
)
from sqlalchemy.orm import Session
from data_pipeline.ingest_building import (
    get_open_buildings_dependency,
    IngestionFunction,
)

router = APIRouter()


@router.post("/", response_model=BuildingFootprints)
def get_all_building_footprints(
    building_footprint_request: BuildingFootprintRequest,
    db: Session = Depends(get_session),
    get_open_buildings: IngestionFunction = Depends(get_open_buildings_dependency),
):
    list_footprints = get_building_footprints(
        building_footprint_request=building_footprint_request,
        get_open_buildings=get_open_buildings,
        db=db,
    )
    return BuildingFootprints(building_footprints=list_footprints)
