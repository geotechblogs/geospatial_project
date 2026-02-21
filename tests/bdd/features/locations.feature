Feature: Locations API
  As an API consumer
  I want to manage geospatial locations
  So that I can create, read, update, and delete location records

  Scenario: Create a location with description and geometry
    Given the database is ready for creating a location
    When I create a location with description "Test Location" and geometry type "Point" at coordinates [102.0, 0.5]
    Then the response status code should be 200
    And the response description should be "Test Location"
    And the response geometry should be type "Point" at coordinates [102.0, 0.5]

  Scenario: Get all locations
    Given the database has existing locations
    When I request all locations
    Then the response status code should be 200
    And the response should contain 1 location

  Scenario: Get a location by ID
    Given the database has a location with a known ID
    When I request the location by its ID
    Then the response status code should be 200
    And the response description should be "Test Location"
    And the response geometry should be type "Point" at coordinates [102.0, 0.5]

  Scenario: Update a location
    Given the database has a location with a known ID
    When I update the location description to "Updated Location"
    Then the response status code should be 200
    And the response description should be "Updated Location"
    And the response geometry should be type "Point" at coordinates [102.0, 0.5]

  Scenario: Delete a location
    Given the database has a location with a known ID
    When I delete the location
    Then the response status code should be 200
    And the response description should be "Test Location"
    And the response geometry should be type "Point" at coordinates [102.0, 0.5]

  Scenario: Creating a location without a description fails validation
    Given the database is ready for creating a location
    When I create a location without a description
    Then the response status code should be 422

  Scenario: Creating a location without geometry uses default coordinates
    Given the database is ready for creating a location
    When I create a location with only description "Test Location"
    Then the response status code should be 200
    And the response geometry should be type "Point" at coordinates [0.0, 0.0]
