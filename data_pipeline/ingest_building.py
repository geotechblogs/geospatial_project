import duckdb
from geoproject.core.config import get_settings
from typing import Callable, Generator
from data_pipeline.constants import OPEN_BUILDINGS_BUCKET, COUNTRY_LIST
from data_pipeline.utils import get_country_from_aoi
from sqlalchemy.engine.url import make_url
from shapely import wkt as shapely_wkt
from loguru import logger

IngestionFunction = Generator[Callable[[str], None], None, None]


def get_bbox_from_wkt(filter_polygon_wkt: str) -> tuple[float, float, float, float]:
    geom = shapely_wkt.loads(filter_polygon_wkt)
    min_lon, min_lat, max_lon, max_lat = geom.bounds
    return min_lon, min_lat, max_lon, max_lat


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
    url = make_url(connection_url)
    pg_conn_string = f"dbname={url.database} user={url.username} password={url.password} host={url.host} port={url.port}"

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
    logger.info(f"Querying remote Parquet for {country_iso}...")

    min_lon, min_lat, max_lon, max_lat = get_bbox_from_wkt(filter_polygon_wkt)

    # 4. The "ETL" Query
    # Bbox filter on latitude/longitude enables Parquet row group pruning (predicate pushdown),
    # dramatically reducing S3 data read before the precise ST_Intersects check.
    try:
        query = f"""INSERT INTO prod_db.public.building_footprints (geom, confidence, area_meters)
            SELECT
                ST_AsWKB(geometry) as geom,
                confidence,
                area_in_meters as area_meters
            FROM read_parquet('{s3_url}')
            WHERE ST_YMax(geometry) >= {min_lat} AND ST_YMin(geometry) <= {max_lat}
              AND ST_XMax(geometry) >= {min_lon} AND ST_XMin(geometry) <= {max_lon}
              AND ST_Intersects(geometry, ST_GeomFromText('{filter_polygon_wkt}'))
              AND (confidence > {confidence} OR confidence IS NULL);"""
        con.sql(query)
        logger.info(f"Successfully loaded buildings for {country_iso} into PostGIS.")

    except Exception as e:
        logger.error(f"Failed to load buildings for {country_iso}: {e}")

    finally:
        con.close()


def get_open_buildings_dependency() -> IngestionFunction:
    yield query_open_buildings
