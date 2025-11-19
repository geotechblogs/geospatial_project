from sqlalchemy.orm import Session
from geoproject.models.locations import DBLocations
from geoproject.config.database import get_session
from geoproject.models.locations import LocationCreate, LocationUpdate, LocationResponse
from fastapi import Depends
from uuid import UUID
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape

def create_location_service(location: LocationCreate, db:Session = Depends(get_session)):
    location_data = location.model_dump(exclude_unset=True) 
    wkt_geometry = WKTElement(location_data['geometry'], srid=4326)
    db_location = DBLocations(
        description=location_data['description'],
        geometry=wkt_geometry
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)

    geometry = to_shape(db_location.geometry).__geo_interface__
    return LocationResponse(
        location_id=db_location.location_id,
        timestamp=db_location.timestamp,
        description=db_location.description,
        geometry=geometry
    )

def get_all_locations_service(db:Session = Depends(get_session)):
    results = db.query(DBLocations).all()
    locations = []
    for result in results:
        geometry = to_shape(result.geometry).__geo_interface__
        locations.append(
            LocationResponse(
                location_id=result.location_id,
                timestamp=result.timestamp,
                description=result.description,
                geometry=geometry
            )
        )
    return locations

def get_location_by_id_service(location_id: UUID, db:Session = Depends(get_session)):
    result = db.query(DBLocations).filter(DBLocations.location_id == str(location_id)).first()
    geometry = to_shape(result.geometry).__geo_interface__
    return LocationResponse(
        location_id=result.location_id,
        timestamp=result.timestamp,
        description=result.description,
        geometry=geometry
    )

def update_location_service(location_id: UUID, location: LocationUpdate, db:Session = Depends(get_session)):
    db_location = db.query(DBLocations).filter(DBLocations.location_id == str(location_id)).first()
    db_location.description = location.description
    db_location.geometry = location.geometry
    db.commit()
    db.refresh(db_location)
    geometry = to_shape(db_location.geometry).__geo_interface__
    return LocationResponse(
        location_id=db_location.location_id,
        timestamp=db_location.timestamp,
        description=db_location.description,
        geometry=geometry
    )

def delete_location_service(location_id: UUID, db:Session = Depends(get_session)):
    db_location = db.query(DBLocations).filter(DBLocations.location_id == str(location_id)).first()
    db.delete(db_location)
    db.commit()
    geometry = to_shape(db_location.geometry).__geo_interface__
    return LocationResponse(
        location_id=db_location.location_id,
        timestamp=db_location.timestamp,
        description=db_location.description,
        geometry=geometry
    )

