import re
import geopandas as gpd
from shapely import Point
import shapely

def clean_string(text: str, replace_with: str = "") -> str:
    """
    Removes all spaces, whitespace characters, and special characters from a string,
    leaving only letters, numbers, and underscores.
    """
    # [^\w] or [^a-zA-Z0-9_] matches any character that is NOT alphanumeric or underscore
    return re.sub(r'[^a-zA-Z0-9_]', replace_with, text)

def pull_gdb_from_path(path: str) -> str:
    """
    Extracts the name of the geodatabase (GDB) from a given file path.
    """
    return next((p for p in [path] + list(path.parents) if p.suffix.lower() == ".gdb"), None)

def clean_line_features(line_gdf):
    """Ensures that the route is represented as a single-line GeoDataFrame."""
    print("Cleaning line features...")
    clean_lines = line_gdf[~line_gdf.is_empty & line_gdf.geometry.notnull()].copy()
    clean_lines = clean_lines[clean_lines.geometry.type.isin(["LineString", "MultiLineString"]) ]
    single_lines = clean_lines.explode(index_parts=False)
    target_line = single_lines.unary_union
    return gpd.GeoDataFrame(geometry=[target_line], crs=clean_lines.crs)

def get_crossing_m_value(geometry, route_line):
    intersection = geometry.intersection(route_line)
    return min(
        route_line.project(Point(coords))
        for coords in shapely.get_coordinates(intersection)
    )