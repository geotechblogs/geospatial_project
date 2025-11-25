import geopandas as gpd
from shapely import wkt
from functools import lru_cache

import country_converter as coco
from typing import Optional
from data_pipeline.constants import COUNTRY_LIST

WORLD_BOUNDARIES_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"


@lru_cache(maxsize=1)
def get_world_boundaries():
    print("Loading world boundaries into memory...")
    try:
        return gpd.read_file(WORLD_BOUNDARIES_URL)
    except Exception as e:
        print(f"Error loading boundaries: {e}")
        return None


def get_iso3_from_name(country_name: str) -> Optional[str]:
    """
    Converts a country name (or common variant) to its ISO 3 code.
    Args:
        country_name: The name of the country (e.g., "Nigeria", "Tanzania, United Republic of").
    Returns:
        The three-letter ISO 3 code (e.g., "NGA", "TZA"), or None if not found.
    """
    try:
        iso3_code = coco.convert(names=country_name, to="ISO3", not_found=None)

        if iso3_code is None or iso3_code == country_name:
            return None

        return iso3_code

    except Exception:
        return None


def get_country_from_aoi(aoi_wkt: str) -> str:
    """
    Determines the country for an AOI using pure Python (GeoPandas).
    """
    world_gdf = get_world_boundaries()

    if world_gdf is None:
        return "Error: Could not load country data."

    try:
        aoi_geom = wkt.loads(aoi_wkt)
        aoi_gdf = gpd.GeoDataFrame(geometry=[aoi_geom], crs="EPSG:4326")

        if world_gdf.crs is None:
            world_gdf.set_crs("EPSG:4326", inplace=True)

        joined = gpd.sjoin(aoi_gdf, world_gdf, how="inner", predicate="intersects")
        if not joined.empty:
            country_code = "".join(joined.WB_A3.values)
            if country_code in COUNTRY_LIST:
                return country_code
        return "Unknown (Ocean or No Match)"

    except Exception as e:
        return f"Processing Error: {e}"
