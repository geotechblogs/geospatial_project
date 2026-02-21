import pytest
import uuid
from datetime import datetime, timezone
from typing import Generator, Any, cast
from unittest.mock import MagicMock, Mock

from fastapi.testclient import TestClient
from sqlalchemy import Column
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

from geoproject.main import app
from geoproject.config.database import get_session
from geoproject.models.locations import DBLocations
from geoproject.models.building_footprints import DBBuildingFootprint
from geoproject.services.building_footprints import (
    IngestionFunction,
    get_open_buildings_dependency,
)

MOCK_DB_SESSION = MagicMock(spec=Session)


def override_get_session() -> Generator[Session, None, None]:
    yield MOCK_DB_SESSION


def override_get_open_buildings() -> Generator[IngestionFunction, None, None]:
    mock_func = MagicMock(spec=IngestionFunction)
    yield cast(IngestionFunction, mock_func)


@pytest.fixture
def configured_mock_session():
    def mock_refresh(instance: DBLocations, *args, **kwargs):
        instance.location_id = cast(Column[str], str(uuid.uuid4()))
        instance.timestamp = cast(Column[datetime], datetime.now(timezone.utc))

    MOCK_DB_SESSION.reset_mock()
    MOCK_DB_SESSION.refresh.side_effect = mock_refresh


@pytest.fixture
def configured_mock_get_all_locations():
    def mock_all_locations():
        return [
            DBLocations(
                location_id=uuid.uuid4(),
                timestamp=datetime.now(timezone.utc),
                description="Test Location",
                geometry=WKTElement("POINT (102.0 0.5)", srid=4326),
            )
        ]

    MOCK_DB_SESSION.reset_mock()
    MOCK_DB_SESSION.query.return_value.all.return_value = mock_all_locations()


@pytest.fixture
def configured_mock_get_location_by_id():
    def mock_get_location_by_id(location_id: uuid.UUID = uuid.uuid4()):
        return DBLocations(
            location_id=location_id,
            timestamp=datetime.now(timezone.utc),
            description="Test Location",
            geometry=WKTElement("POINT (102.0 0.5)", srid=4326),
        )

    MOCK_DB_SESSION.reset_mock()
    MOCK_DB_SESSION.query.return_value.filter.return_value.first.return_value = (
        mock_get_location_by_id()
    )


@pytest.fixture
def configured_mock_get_all_building_footprints():
    mock_results = [
        DBBuildingFootprint(
            id=10,
            confidence=0.5,
            area_meters=100.0,
            geom=WKTElement("POINT (102.0 0.5)", srid=4326),
        )
    ]
    MOCK_DB_SESSION.reset_mock()
    mock_filtered_query = Mock()
    mock_filtered_query.count.return_value = len(mock_results)
    mock_filtered_query.all.return_value = mock_results
    mock_filtered_query.first.return_value = mock_results[0]
    MOCK_DB_SESSION.query.return_value.filter.return_value = mock_filtered_query


@pytest.fixture
def client() -> Generator[TestClient, Any, Any]:
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_open_buildings_dependency] = (
        override_get_open_buildings
    )
    yield TestClient(app)
    app.dependency_overrides.clear()
