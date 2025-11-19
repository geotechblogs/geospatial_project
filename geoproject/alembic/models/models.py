import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Locations(Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "public"}
    location_id = sa.Column(
        sa.String(), primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    description = sa.Column(sa.String(255))
    timestamp = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    geometry = sa.Column(
        Geometry("GEOMETRY", srid=4326, spatial_index=True), nullable=False
    )
