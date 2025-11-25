from geoproject.models.building_footprints import DBBuildingFootprint
from geoproject.models.building_footprints import (
    BuildingFootprintRequest,
    BuildingFootprint,
)
from geoproject.config.database import get_session
from fastapi import Depends
from fastapi import HTTPException
from geoalchemy2 import WKTElement

from geoalchemy2.shape import to_shape
from typing import cast
from sqlalchemy.orm import Session
from data_pipeline.ingest_building import (
    IngestionFunction,
    get_open_buildings_dependency,
)
from shapely.geometry import shape


def get_building_footprints(
    building_footprint_request: BuildingFootprintRequest,
    db: Session = Depends(get_session),
    get_open_buildings: IngestionFunction = Depends(get_open_buildings_dependency),
) -> list[BuildingFootprint]:
    geometry = shape(building_footprint_request.geometry)
    input_geom = WKTElement(geometry.wkt, srid=4326)

    query = db.query(DBBuildingFootprint).filter(
        DBBuildingFootprint.geom.ST_Within(input_geom)
    )
    if query.count() == 0:
        get_open_buildings(geometry.wkt)  # type: ignore
        query = db.query(DBBuildingFootprint).filter(
            DBBuildingFootprint.geom.ST_Within(input_geom)
        )
    if query.count() == 0:
        raise HTTPException(status_code=404, detail="No building footprints found")
    results = query.all()
    building_footprints = []
    for result in results:
        geom_data = cast(WKTElement, result.geom)
        output_geometry = to_shape(geom_data).__geo_interface__
        building_footprints.append(
            BuildingFootprint(
                location_id=cast(int, result.id),
                confidence=cast(float, result.confidence),
                area_meters=cast(float, result.area_meters),
                geometry=output_geometry,
            )
        )
    return building_footprints
