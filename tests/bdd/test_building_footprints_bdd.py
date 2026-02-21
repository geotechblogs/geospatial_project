from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient

scenarios("building_footprints.feature")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given(
    "the database has building footprints within the query area",
    target_fixture="db_ready",
)
def db_has_building_footprints(configured_mock_get_all_building_footprints):
    """Fixture wires up the mock session with building footprint data."""
    return True


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when(
    parsers.parse(
        'I request building footprints with geometry type "{geom_type}" '
        "at coordinates [{lng:g}, {lat:g}]"
    ),
    target_fixture="response",
)
def request_building_footprints(
    client: TestClient, geom_type: str, lng: float, lat: float
):
    payload = {"geometry": {"type": geom_type, "coordinates": [lng, lat]}}
    return client.post("/api/v1/building_footprints", json=payload)


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then(parsers.parse("the response status code should be {status_code:d}"))
def check_status_code(response, status_code: int):
    assert response.status_code == status_code


@then(parsers.parse("the response should contain {count:d} building footprint"))
def check_footprint_count(response, count: int):
    assert len(response.json()["building_footprints"]) == count


@then(parsers.parse("the first building footprint should have location_id {value:d}"))
def check_location_id(response, value: int):
    assert response.json()["building_footprints"][0]["location_id"] == value


@then(parsers.parse("the first building footprint should have confidence {value:g}"))
def check_confidence(response, value: float):
    assert response.json()["building_footprints"][0]["confidence"] == value


@then(parsers.parse("the first building footprint should have area_meters {value:g}"))
def check_area_meters(response, value: float):
    assert response.json()["building_footprints"][0]["area_meters"] == value
