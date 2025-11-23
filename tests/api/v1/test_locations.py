import pytest
import uuid
from fastapi.testclient import TestClient
from typing import Dict, Any, Generator


@pytest.mark.parametrize(
    "location_data",
    [
        {
            "description": "Test Location",
            "geometry": {
                "type": "Point",
                "coordinates": [102.0, 0.5],
            },
        }
    ],
)
def test_create_location_should_return_correct_location(
    client: TestClient,
    configured_mock_session: Generator[None, None, None],
    location_data: Dict[str, Any],
):
    response = client.post("/api/v1/locations", json=location_data)

    assert response.status_code == 200
    assert response.json()["description"] == location_data["description"]
    assert response.json()["geometry"] == location_data["geometry"]


def test_get_all_locations_should_return_all_locations(
    client: TestClient, configured_mock_get_all_locations: Generator[None, None, None]
):
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    assert len(response.json()["locations"]) == 1


def test_get_location_by_id_should_return_correct_location(
    client: TestClient, configured_mock_get_location_by_id: Generator[None, None, None]
):
    response = client.get(f"/api/v1/locations/{uuid.uuid4()}")
    assert response.status_code == 200
    assert response.json()["description"] == "Test Location"
    assert response.json()["geometry"] == {"type": "Point", "coordinates": [102.0, 0.5]}


def test_update_location_should_return_correct_location(
    client: TestClient, configured_mock_get_location_by_id: Generator[None, None, None]
):
    response = client.put(
        f"/api/v1/locations/{uuid.uuid4()}", json={"description": "Updated Location"}
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated Location"
    assert response.json()["geometry"] == {"type": "Point", "coordinates": [102.0, 0.5]}


def test_delete_location_should_return_correct_location(
    client: TestClient, configured_mock_get_location_by_id: Generator[None, None, None]
):
    response = client.delete(f"/api/v1/locations/{uuid.uuid4()}")
    assert response.status_code == 200
    assert response.json()["description"] == "Test Location"
    assert response.json()["geometry"] == {"type": "Point", "coordinates": [102.0, 0.5]}


def test_create_location_should_return_422_without_description(client: TestClient):
    response = client.post(
        "/api/v1/locations",
        json={"geometry": {"type": "Point", "coordinates": [102.0, 0.5]}},
    )
    assert response.status_code == 422


def test_create_location_should_return_default_geometry(client: TestClient):
    response = client.post("/api/v1/locations", json={"description": "Test Location"})
    assert response.status_code == 200
    assert response.json()["geometry"] == {"type": "Point", "coordinates": [0.0, 0.0]}
