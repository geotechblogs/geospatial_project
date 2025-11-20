from fastapi import APIRouter, Depends
from geoproject.config.database import get_session
from geoproject.services.locations import (
    create_location_service,
    get_all_locations_service,
    get_location_by_id_service,
    update_location_service,
    delete_location_service,
)
from geoproject.models.locations import (
    LocationCreateUpdate,
    LocationResponse,
    AllLocations,
)
from uuid import UUID
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=AllLocations)
def get_all_locations(db: Session = Depends(get_session)):
    return AllLocations(locations=get_all_locations_service(db))


@router.get("/{location_id}", response_model=LocationResponse)
def get_location_by_id(location_id: UUID, db: Session = Depends(get_session)):
    return get_location_by_id_service(location_id, db)


@router.post("/", response_model=LocationResponse)
def create_location(location: LocationCreateUpdate, db: Session = Depends(get_session)):
    return create_location_service(location, db)


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: UUID,
    location: LocationCreateUpdate,
    db: Session = Depends(get_session),
):
    return update_location_service(location_id, location, db)


@router.delete("/{location_id}", response_model=LocationResponse)
def delete_location(location_id: UUID, db: Session = Depends(get_session)):
    return delete_location_service(location_id, db)
