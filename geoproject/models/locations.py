import sqlalchemy as sa
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from pydantic import ConfigDict, field_validator, Field
from shapely.geometry import shape  # type: ignore
from typing import Dict, Optional
from geoproject.config.database import Base


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


class LocationCreateUpdate(BaseModel):
    description: str
    geometry: Optional[WKTElement] = Field(
        default_factory=lambda: WKTElement("POINT (0 0)", srid=4326)
    )

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )

    @field_validator("geometry", mode="before")
    def validate_geometry(cls, geojson_data: Dict) -> WKTElement:
        if not isinstance(geojson_data, Dict):
            raise ValueError("Geometry must be a valid GeoJSON dictionary.")
        try:
            geometry = shape(geojson_data)
            return WKTElement(geometry.wkt, srid=4326)
        except Exception:
            raise ValueError("Geometry must be a valid GeoJSON dictionary.")


class LocationResponse(BaseModel):
    location_id: UUID
    timestamp: datetime
    description: str
    geometry: dict

    model_config = ConfigDict(from_attributes=True)


class AllLocations(BaseModel):
    locations: list[LocationResponse]
