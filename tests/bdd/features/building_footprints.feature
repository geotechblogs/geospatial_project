Feature: Building Footprints API
  As an API consumer
  I want to query building footprints by geometry
  So that I can retrieve footprint data for a given area

  Scenario: Query building footprints with a valid geometry
    Given the database has building footprints within the query area
    When I request building footprints with geometry type "Point" at coordinates [102.0, 0.5]
    Then the response status code should be 200
    And the response should contain 1 building footprint
    And the first building footprint should have location_id 10
    And the first building footprint should have confidence 0.5
    And the first building footprint should have area_meters 100.0
