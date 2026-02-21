import uuid

from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient

scenarios("locations.feature")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("the database is ready for creating a location", target_fixture="db_ready")
def db_ready_for_create(configured_mock_session):
    """Fixture wires up the mock session for location creation."""
    return True


@given("the database has existing locations", target_fixture="db_ready")
def db_has_locations(configured_mock_get_all_locations):
    return True


@given("the database has a location with a known ID", target_fixture="location_id")
def db_has_location_by_id(configured_mock_get_location_by_id):
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when(
    parsers.parse(
        'I create a location with description "{description}" '
        'and geometry type "{geom_type}" at coordinates [{lng:g}, {lat:g}]'
    ),
    target_fixture="response",
)
def create_location(
    client: TestClient, description: str, geom_type: str, lng: float, lat: float
):
    payload = {
        "description": description,
        "geometry": {"type": geom_type, "coordinates": [lng, lat]},
    }
    return client.post("/api/v1/locations", json=payload)


@when("I request all locations", target_fixture="response")
def request_all_locations(client: TestClient):
    return client.get("/api/v1/locations")


@when("I request the location by its ID", target_fixture="response")
def request_location_by_id(client: TestClient, location_id: str):
    return client.get(f"/api/v1/locations/{location_id}")


@when(
    parsers.parse('I update the location description to "{description}"'),
    target_fixture="response",
)
def update_location(client: TestClient, location_id: str, description: str):
    return client.put(
        f"/api/v1/locations/{location_id}",
        json={"description": description},
    )


@when("I delete the location", target_fixture="response")
def delete_location(client: TestClient, location_id: str):
    return client.delete(f"/api/v1/locations/{location_id}")


@when("I create a location without a description", target_fixture="response")
def create_location_without_description(client: TestClient):
    return client.post(
        "/api/v1/locations",
        json={"geometry": {"type": "Point", "coordinates": [102.0, 0.5]}},
    )


@when(
    parsers.parse('I create a location with only description "{description}"'),
    target_fixture="response",
)
def create_location_only_description(client: TestClient, description: str):
    return client.post("/api/v1/locations", json={"description": description})


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then(parsers.parse("the response status code should be {status_code:d}"))
def check_status_code(response, status_code: int):
    assert response.status_code == status_code


@then(parsers.parse('the response description should be "{description}"'))
def check_description(response, description: str):
    assert response.json()["description"] == description


@then(
    parsers.parse(
        'the response geometry should be type "{geom_type}" at coordinates [{lng:g}, {lat:g}]'
    )
)
def check_geometry(response, geom_type: str, lng: float, lat: float):
    geometry = response.json()["geometry"]
    assert geometry == {"type": geom_type, "coordinates": [lng, lat]}


@then(parsers.parse("the response should contain {count:d} location"))
def check_location_count(response, count: int):
    assert len(response.json()["locations"]) == count
