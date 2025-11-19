import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from pydantic import ConfigDict

Base = declarative_base()


class DBLocations(Base):
    __tablename__ = "locations"
    location_id = sa.Column(
        sa.String(), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    timestamp = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    description = sa.Column(sa.String(255))
    geometry = sa.Column(
        Geometry("GEOMETRY", srid=4326, spatial_index=True), nullable=False
    )


class LocationCreate(BaseModel):
    description: str
    geometry: str


class LocationUpdate(BaseModel):
    description: str
    geometry: str


class LocationResponse(BaseModel):
    location_id: UUID
    timestamp: datetime
    description: str
    geometry: dict

    model_config = ConfigDict(from_attributes=True)


class AllLocations(BaseModel):
    locations: list[LocationResponse]
