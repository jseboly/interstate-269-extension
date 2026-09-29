import pandas as pd
import geopandas as gpd
import project_config as cfg

def merge_parcel_data():
    """Merges parcel data from all configured sources into a single GeoDataFrame."""
    print("Merging parcel data from all sources...")
    clean_gdfs = []
    
    for source in cfg.PARCEL_SOURCES:
        source.load_data()
        gdf = source._gdf

        def resolve_field(field_name):
            if field_name is None:
                return None
            if field_name in gdf.columns:
                return field_name
            matches = [col for col in gdf.columns if str(col).lower() == str(field_name).lower()]
            return matches[0] if matches else None

        owner_key = resolve_field(source.owner_field)
        parcel_key = resolve_field(source.parcel_id_field)

        if owner_key is None or parcel_key is None:
            available = list(gdf.columns)
            raise KeyError(
                f"Could not find required parcel fields for {source.name}. "
                f"Expected owner='{source.owner_field}', parcel_id='{source.parcel_id_field}'. "
                f"Available columns: {available}"
            )

        column_name_mapping = {
            owner_key: "Owner",
            parcel_key: "ParcelID"
        }
        geom_col = gdf.geometry.name
        cols_to_keep = list(column_name_mapping.keys()) + [geom_col]
        cleaned = gdf[cols_to_keep].rename(columns=column_name_mapping)
        clean_gdfs.append(cleaned)

        # Removed as it's now handled in the append above.
        
    merged_gdf = gpd.GeoDataFrame(
        pd.concat(clean_gdfs, ignore_index=True),
        crs=cfg.PROJECT_CRS
    )

    for source in cfg.PARCEL_SOURCES:
        source.unload()
    for cleaned_gdf in clean_gdfs:
        del cleaned_gdf

    return merged_gdf

def clean_line_features(line_gdf):
    """Ensures that the route is represented as a single-line GeoDataFrame."""
    print("Cleaning line features...")
    clean_lines = line_gdf[~line_gdf.is_empty & line_gdf.geometry.notnull()].copy()
    clean_lines = clean_lines[clean_lines.geometry.type.isin(["LineString", "MultiLineString"]) ]
    single_lines = clean_lines.explode(index_parts=False)
    target_line = single_lines.unary_union

    return gpd.GeoDataFrame(geometry=[target_line], crs=clean_lines.crs)

def get_entry_distance(poly_geom, line_geom):
    """Calculates the distance from the start of the line to the intersection
    with the polygon."""
    from shapely.geometry import Point

    intersection = poly_geom.intersection(line_geom)
    if intersection.is_empty:
        return None

    if intersection.geom_type == "Point":
        return line_geom.project(intersection)

    point = None
    if hasattr(intersection, "geoms"):
        for geom in intersection.geoms:
            if geom.geom_type == "Point":
                point = geom
                break
            if geom.geom_type in {"LineString", "LinearRing"}:
                point = Point(geom.coords[0])
                break
    if point is None and hasattr(intersection, "boundary") and not intersection.boundary.is_empty:
        boundary = intersection.boundary
        if boundary.geom_type == "Point":
            point = boundary
        elif hasattr(boundary, "geoms") and boundary.geoms:
            point = boundary.geoms[0]

    if point is None:
        return None

    return line_geom.project(point)

def get_entry_distances(poly_geom, line_geom):
    """Return the min and max distances along the line within the polygon."""
    from shapely.geometry import Point

    intersection = poly_geom.intersection(line_geom)
    if intersection.is_empty:
        return None, None

    def project_parts(geom):
        if geom.is_empty:
            return []

        if geom.geom_type == "Point":
            return [line_geom.project(geom)]

        if geom.geom_type in {"LineString", "LinearRing"}:
            return [
                line_geom.project(Point(coord))
                for coord in geom.coords
            ]

        if hasattr(geom, "geoms"):
            return [
                distance
                for part in geom.geoms
                for distance in project_parts(part)
            ]

        return []

    distances = project_parts(intersection)
    if not distances:
        return None, None

    return min(distances), max(distances)

def generate_line_list(route, parcels):
    print(f"Generating line list for route: {route.name}")
    route.centerline.load_data()
    centerline_gdf = clean_line_features(route.centerline._gdf)

    intersecting_polygons = gpd.sjoin(
        parcels, 
        centerline_gdf[['geometry']], 
        how='inner', 
        predicate='intersects'
    ).copy()

    distances = intersecting_polygons.geometry.apply(
        lambda poly: get_entry_distances(poly, centerline_gdf.geometry.iloc[0])
    )

    intersecting_polygons[["entry_distance", "exit_distance"]] = pd.DataFrame(
        distances.tolist(), index=intersecting_polygons.index
    )

    sorted_polygons = intersecting_polygons.sort_values(by='entry_distance').reset_index(drop=True)
    sorted_polygons["feet_crossed"] = sorted_polygons["exit_distance"] - sorted_polygons["entry_distance"]
    route.line_list = sorted_polygons
    route.centerline.unload()
    del centerline_gdf

def main():
    print("Analyzing parcels...")
    parcels = merge_parcel_data()

    for route in cfg.ROUTES_CONFIG:
        print(f"Analyzing parcels for route: {route.name}")
        generate_line_list(route, parcels)
        print(f"Generated line list for route: {route.name}")

    print("Parcel analysis complete.")