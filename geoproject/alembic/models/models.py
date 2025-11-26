import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.sql import func

from sqlalchemy.dialects.postgresql import UUID
from geoproject.config.database import Base


class Locations(Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "public"}
    location_id = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    description = sa.Column(sa.String(255))
    timestamp = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    geometry = sa.Column(
        Geometry("GEOMETRY", srid=4326, spatial_index=True), nullable=False
    )


class BuildingFootprints(Base):
    __tablename__ = "building_footprints"
    __table_args__ = {"schema": "public"}
    id = sa.Column(
        sa.Integer,
        primary_key=True,
    )
    confidence = sa.Column(sa.Float)
    area_meters = sa.Column(sa.Float)
    geometry = sa.Column(
        Geometry("POLYGON", srid=4326, spatial_index=True), nullable=False
    )
