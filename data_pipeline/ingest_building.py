import duckdb
from geoproject.core.config import get_settings
import re
from typing import Optional, Callable, Generator
from data_pipeline.constants import OPEN_BUILDINGS_BUCKET, COUNTRY_LIST
from data_pipeline.utils import get_country_from_aoi

IngestionFunction = Generator[Callable[[str], None], None, None]


def get_db_params_from_url(url: str) -> str:
    conn_params = re.split(r"(?<!/)/", url)
    params_server = conn_params[1].lstrip("/").split("@")
    params_auth = params_server[0].split(":")
    params_network = params_server[1].split(":")
    db_user = params_auth[0]
    db_password = params_auth[1]
    db_host = params_network[0]
    db_port = params_network[1]
    db_name = conn_params[-1]
    return f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"


def get_spatial_filter_polygon_wkt(filter_polygon_wkt: Optional[str] = None):
    spatial_filter = ""
    if filter_polygon_wkt:
        spatial_filter = (
            f"ST_Intersects(geometry, ST_GeomFromText('{filter_polygon_wkt}'))"
        )
    return spatial_filter


def query_open_buildings(
    filter_polygon_wkt: str,
    confidence: float = 0.75,
) -> None:
    country_iso = get_country_from_aoi(filter_polygon_wkt)
    if country_iso not in COUNTRY_LIST:
        raise ValueError(
            f"Country {country_iso} is not in the list of countries for Open Buildings."
        )

    settings = get_settings()
    connection_url = settings.db_url
    con = duckdb.connect()
    pg_conn_string = get_db_params_from_url(connection_url)

    # 1. Install/Load Extensions
    con.sql("INSTALL spatial; LOAD spatial;")
    con.sql("INSTALL httpfs; LOAD httpfs;")
    con.sql("INSTALL postgres; LOAD postgres;")

    # 2. Configure Anonymous S3 Access (REQUIRED for public buckets)
    con.sql("SET s3_region='us-west-2';")

    # Optional: Set a specific timeout for remote connection
    con.sql("SET http_timeout=30;")

    # 2. Attach your Production PostGIS DB
    con.sql(f"ATTACH '{pg_conn_string}' AS prod_db (TYPE POSTGRES);")
    s3_url = f"{OPEN_BUILDINGS_BUCKET}/country_iso={country_iso}/{country_iso}.parquet"
    print(f"Querying remote Parquet for {country_iso}...")
    spatial_filter = get_spatial_filter_polygon_wkt(filter_polygon_wkt)

    # 4. The "ETL" Query
    try:
        query = f"""INSERT INTO prod_db.public.building_footprints (geom, confidence, area_meters)
            SELECT
                ST_AsWKB(geometry) as geom,
                confidence,
                area_in_meters as area_meters
            FROM read_parquet('{s3_url}')
            WHERE confidence > {confidence} OR confidence IS NULL AND {spatial_filter};"""
        con.sql(query)
        print(f"Successfully loaded buildings for {country_iso} into PostGIS.")

    except Exception as e:
        print(f"Failed to load buildings for {country_iso}: {e}")

    finally:
        con.close()


def get_open_buildings_dependency() -> IngestionFunction:
    yield query_open_buildings
