import pytest
from unittest.mock import MagicMock, patch, call

from data_pipeline.ingest_building import (
    get_bbox_from_wkt,
    query_open_buildings,
)

# Simple rectangle: lon 10–30, lat 20–40
SIMPLE_RECT_WKT = "POLYGON((10.0 20.0, 30.0 20.0, 30.0 40.0, 10.0 40.0, 10.0 20.0))"

# Small AOI around Mexico City: lon -99.2 to -99.1, lat 19.3 to 19.4
MEXICO_CITY_AOI_WKT = (
    "POLYGON((-99.2 19.3, -99.1 19.3, -99.1 19.4, -99.2 19.4, -99.2 19.3))"
)


class TestGetBboxFromWkt:
    def test_simple_rectangle_returns_correct_bounds(self):
        min_lon, min_lat, max_lon, max_lat = get_bbox_from_wkt(SIMPLE_RECT_WKT)

        assert min_lon == pytest.approx(10.0)
        assert min_lat == pytest.approx(20.0)
        assert max_lon == pytest.approx(30.0)
        assert max_lat == pytest.approx(40.0)

    def test_irregular_polygon_returns_envelope_bounds(self):
        triangle_wkt = "POLYGON((0.0 0.0, 5.0 10.0, 10.0 0.0, 0.0 0.0))"

        min_lon, min_lat, max_lon, max_lat = get_bbox_from_wkt(triangle_wkt)

        assert min_lon == pytest.approx(0.0)
        assert min_lat == pytest.approx(0.0)
        assert max_lon == pytest.approx(10.0)
        assert max_lat == pytest.approx(10.0)

    def test_negative_coordinates_return_correct_bounds(self):
        wkt = "POLYGON((-10.0 -5.0, 5.0 -5.0, 5.0 15.0, -10.0 15.0, -10.0 -5.0))"

        min_lon, min_lat, max_lon, max_lat = get_bbox_from_wkt(wkt)

        assert min_lon == pytest.approx(-10.0)
        assert min_lat == pytest.approx(-5.0)
        assert max_lon == pytest.approx(5.0)
        assert max_lat == pytest.approx(15.0)

    def test_return_order_is_min_lon_min_lat_max_lon_max_lat(self):
        min_lon, min_lat, max_lon, max_lat = get_bbox_from_wkt(MEXICO_CITY_AOI_WKT)

        assert min_lon == pytest.approx(-99.2)
        assert min_lat == pytest.approx(19.3)
        assert max_lon == pytest.approx(-99.1)
        assert max_lat == pytest.approx(19.4)


class TestQueryOpenBuildings:
    @pytest.fixture
    def duckdb_con(self):
        return MagicMock()

    @pytest.fixture
    def fake_settings(self):
        settings = MagicMock()
        settings.db_url = "postgresql://user:password@localhost:5432/geoproject_db"
        return settings

    def _get_etl_query(self, con_mock: MagicMock) -> str:
        sql_calls = [c.args[0] for c in con_mock.sql.call_args_list]
        return next(q for q in sql_calls if "INSERT INTO" in q)

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_etl_query_contains_latitude_bbox_filter(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings

        query_open_buildings(MEXICO_CITY_AOI_WKT)

        etl_query = self._get_etl_query(duckdb_con)
        assert "latitude BETWEEN" in etl_query

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_etl_query_contains_longitude_bbox_filter(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings

        query_open_buildings(MEXICO_CITY_AOI_WKT)

        etl_query = self._get_etl_query(duckdb_con)
        assert "longitude BETWEEN" in etl_query

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_etl_query_bbox_values_match_aoi_bounds(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings

        query_open_buildings(MEXICO_CITY_AOI_WKT)

        etl_query = self._get_etl_query(duckdb_con)
        # AOI: lon -99.2 to -99.1, lat 19.3 to 19.4
        assert "19.3" in etl_query
        assert "19.4" in etl_query
        assert "-99.2" in etl_query
        assert "-99.1" in etl_query

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_etl_query_still_contains_st_intersects(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings

        query_open_buildings(MEXICO_CITY_AOI_WKT)

        etl_query = self._get_etl_query(duckdb_con)
        assert "ST_Intersects" in etl_query

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_bbox_filter_appears_before_st_intersects(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings

        query_open_buildings(MEXICO_CITY_AOI_WKT)

        etl_query = self._get_etl_query(duckdb_con)
        assert etl_query.index("latitude BETWEEN") < etl_query.index("ST_Intersects")

    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    def test_raises_value_error_for_unsupported_country(self, mock_get_country):
        mock_get_country.return_value = "ZZZ"

        with pytest.raises(ValueError, match="Country ZZZ is not in the list"):
            query_open_buildings(MEXICO_CITY_AOI_WKT)

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_connection_is_closed_on_success(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings

        query_open_buildings(MEXICO_CITY_AOI_WKT)

        duckdb_con.close.assert_called_once()

    @patch("data_pipeline.ingest_building.get_settings")
    @patch("data_pipeline.ingest_building.get_country_from_aoi")
    @patch("data_pipeline.ingest_building.duckdb.connect")
    def test_connection_is_closed_on_etl_error(
        self, mock_connect, mock_get_country, mock_get_settings, duckdb_con, fake_settings
    ):
        mock_connect.return_value = duckdb_con
        mock_get_country.return_value = "MEX"
        mock_get_settings.return_value = fake_settings
        # Make the INSERT call raise
        duckdb_con.sql.side_effect = lambda q: (_ for _ in ()).throw(
            Exception("DuckDB failure")
        ) if "INSERT INTO" in q else None

        query_open_buildings(MEXICO_CITY_AOI_WKT)  # should not propagate

        duckdb_con.close.assert_called_once()
