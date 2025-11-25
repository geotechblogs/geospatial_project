import pytest
import uuid
from fastapi.testclient import TestClient
from typing import Dict, Any, Generator


@pytest.mark.parametrize(
    "building_footprint_request",
    [
        {
            "geometry": {   
                "type": "Point",
                "coordinates": [102.0, 0.5],
            },
        }
    ],
)
def test_get_all_building_footprints_should_return_correct_location(
    client: TestClient,
    configured_mock_get_all_building_footprints: Generator[None, None, None],
    building_footprint_request: Dict[str, Any],
):
    response = client.post("/api/v1/building_footprints", json=building_footprint_request)
    expected_response = building_footprint_request.copy()
    expected_response["location_id"] = 10
    expected_response["confidence"] = 0.5
    expected_response["area_meters"] = 100.0

    assert response.status_code == 200
    assert response.json()["building_footprints"] == [expected_response]