from sqlalchemy.orm import Session
from geoproject.models.locations import DBLocations
from geoproject.config.database import get_session
from geoproject.models.locations import LocationCreateUpdate, LocationResponse
from fastapi import Depends, HTTPException
from uuid import UUID
from geoalchemy2.shape import to_shape
from geoalchemy2 import WKTElement
from typing import cast
from datetime import datetime


def create_location_service(
    location: LocationCreateUpdate, db: Session = Depends(get_session)
):
    db_location = DBLocations(
        description=location.description, geometry=location.geometry
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    geometry = to_shape(cast(WKTElement, db_location.geometry)).__geo_interface__
    return LocationResponse(
        location_id=cast(UUID, db_location.location_id),
        timestamp=cast(datetime, db_location.timestamp),
        description=cast(str, db_location.description),
        geometry=geometry,
    )


def get_all_locations_service(db: Session = Depends(get_session)):
    results = db.query(DBLocations).all()
    locations = []
    for result in results:
        geometry = to_shape(cast(WKTElement, result.geometry)).__geo_interface__
        locations.append(
            LocationResponse(
                location_id=cast(UUID, result.location_id),
                timestamp=cast(datetime, result.timestamp),
                description=cast(str, result.description),
                geometry=geometry,
            )
        )
    return locations


def get_location_by_id(
    location_id: UUID, db: Session = Depends(get_session)
) -> DBLocations | None:
    return (
        db.query(DBLocations)
        .filter(DBLocations.location_id == str(location_id))
        .first()
    )


def get_location_by_id_service(location_id: UUID, db: Session = Depends(get_session)):
    result = get_location_by_id(location_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Location not found")
    geometry = to_shape(cast(WKTElement, result.geometry)).__geo_interface__
    return LocationResponse(
        location_id=cast(UUID, result.location_id),
        timestamp=cast(datetime, result.timestamp),
        description=cast(str, result.description),
        geometry=geometry,
    )


def update_location_service(
    location_id: UUID,
    location: LocationCreateUpdate,
    db: Session = Depends(get_session),
):
    location_data = location.model_dump(exclude_unset=True)
    db_location = get_location_by_id(location_id, db)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    db_location.description = location_data["description"]
    db_location.geometry = location_data["geometry"]
    db.commit()
    db.refresh(db_location)
    geometry = to_shape(cast(WKTElement, db_location.geometry)).__geo_interface__
    return LocationResponse(
        location_id=cast(UUID, db_location.location_id),
        timestamp=cast(datetime, db_location.timestamp),
        description=cast(str, db_location.description),
        geometry=geometry,
    )


def delete_location_service(location_id: UUID, db: Session = Depends(get_session)):
    db_location = get_location_by_id(location_id, db)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(db_location)
    db.commit()
    geometry = to_shape(cast(WKTElement, db_location.geometry)).__geo_interface__
    return LocationResponse(
        location_id=cast(UUID, db_location.location_id),
        timestamp=cast(datetime, db_location.timestamp),
        description=cast(str, db_location.description),
        geometry=geometry,
    )
