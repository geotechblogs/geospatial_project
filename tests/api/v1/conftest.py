import pytest
from fastapi.testclient import TestClient
from typing import Generator, Any
from geoproject.main import app
from geoproject.config.database import get_session
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from geoproject.models.locations import DBLocations
import uuid
from datetime import datetime, timezone
from geoalchemy2 import WKTElement
from sqlalchemy import Column
from typing import cast

MOCK_DB_SESSION = MagicMock(spec=Session)


def override_get_session() -> Generator[Session, None, None]:
    yield MOCK_DB_SESSION


@pytest.fixture
def configured_mock_session():
    def mock_refresh(instance: DBLocations, *args, **kwargs):
        instance.location_id = cast(Column[str], str(uuid.uuid4()))
        instance.timestamp = cast(Column[datetime], datetime.now(timezone.utc))

    MOCK_DB_SESSION.reset_mock()
    MOCK_DB_SESSION.refresh.side_effect = mock_refresh


@pytest.fixture
def configured_mock_get_all_locations() -> None:
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
    return None


@pytest.fixture
def configured_mock_get_location_by_id() -> None:
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
    return None


@pytest.fixture
def client() -> Generator[TestClient, Any, Any]:
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
