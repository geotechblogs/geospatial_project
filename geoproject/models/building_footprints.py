import sqlalchemy as sa
from pydantic import BaseModel
from pydantic import ConfigDict
from geoproject.config.database import Base
from geoalchemy2 import Geometry
from typing import Optional


class DBBuildingFootprint(Base):
    __tablename__ = "building_footprints"
    id = sa.Column(sa.Integer(), primary_key=True)
    confidence = sa.Column(sa.Float())
    area_meters = sa.Column(sa.Float())
    geom = sa.Column(
        Geometry("GEOMETRY", srid=4326, spatial_index=True), nullable=False
    )


class BuildingFootprintRequest(BaseModel):
    geometry: dict


class BuildingFootprint(BaseModel):
    location_id: int
    confidence: Optional[float] = None
    area_meters: float
    geometry: dict

    model_config = ConfigDict(from_attributes=True)


class BuildingFootprints(BaseModel):
    building_footprints: list[BuildingFootprint]
