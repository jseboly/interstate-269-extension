import re

import geopandas as gpd
import pandas as pd

import project_config as cfg
import utils


SIMPLIFY_TOLERANCE_FEET = 8


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).casefold()).strip("-")


def _text(value, fallback=""):
    if value is None or pd.isna(value):
        return fallback
    return str(value).strip() or fallback


def _row_ids(frame, route_slug, layer_slug):
    frame = frame.copy()
    frame["MapID"] = [
        f"{route_slug}-{layer_slug}-{index:04d}"
        for index in range(1, len(frame) + 1)
    ]
    return frame


def _add_feature(features, geometry, route_name, layer, group, map_id, label, feature_type=""):
    if geometry is None or geometry.is_empty:
        return
    simplified = geometry.simplify(
        SIMPLIFY_TOLERANCE_FEET,
        preserve_topology=True,
    )
    if simplified.is_empty:
        return
    features.append({
        "geometry": simplified,
        "route": route_name,
        "layer": layer,
        "group": group,
        "map_id": map_id,
        "label": label,
        "feature_type": feature_type,
    })


def _add_table_features(features, frame, route_name, route_slug, layer, group, geometry_fn, label_fn, type_fn=None):
    if frame is None:
        return frame
    layer_slug = _slug(layer)
    frame = _row_ids(frame, route_slug, layer_slug)
    for _, row in frame.iterrows():
        geometry = geometry_fn(row)
        _add_feature(
            features,
            geometry,
            route_name,
            layer,
            group,
            row["MapID"],
            label_fn(row),
            type_fn(row) if type_fn else "",
        )
    return frame


def export_map_data(routes=None, output_path=None):
    """Export analyzed route features as a compact GeoJSON file for the website."""
    routes = routes or cfg.ROUTES_CONFIG
    output_path = output_path or cfg.MAP_DATA_FILE
    features = []

    for route in routes:
        route_slug = _slug(route.name)
        route.centerline.load_data()
        route.corridor.load_data()
        try:
            centerline = utils.clean_line_features(route.centerline._gdf)
            corridor = route.corridor._gdf
            corridor_geometry = corridor.geometry.unary_union

            _add_feature(
                features,
                centerline.geometry.iloc[0],
                route.name,
                "Route",
                "Routes",
                f"{route_slug}-route",
                route.name,
            )
            _add_feature(
                features,
                corridor_geometry,
                route.name,
                "Corridor",
                "Corridors",
                f"{route_slug}-corridor",
                f"{route.name} corridor",
            )

            if route.line_list is not None:
                route.line_list = _add_table_features(
                    features,
                    route.line_list,
                    route.name,
                    route_slug,
                    "Parcels",
                    "Parcels",
                    lambda row: row.geometry,
                    lambda row: f"Parcel {_text(row.get('ParcelID'), 'record')}",
                )

            route_line = centerline.geometry.iloc[0]
            for permit_type, frame in (route.permits or {}).items():
                route.permits[permit_type] = _add_table_features(
                    features,
                    frame,
                    route.name,
                    route_slug,
                    permit_type,
                    "Crossings",
                    lambda row: route_line.interpolate(float(row["Measure"]) * 5280),
                    lambda row: _text(row.get("Name"), permit_type),
                    lambda row: permit_type,
                )

            for feature_type, frame in (route.env_constraints or {}).items():
                route.env_constraints[feature_type] = _add_table_features(
                    features,
                    frame,
                    route.name,
                    route_slug,
                    feature_type,
                    "Environment",
                    lambda row: row.geometry,
                    lambda row: _text(row.get("Name"), feature_type),
                    lambda row: feature_type,
                )

            if route.structures is not None:
                route.structures = _add_table_features(
                    features,
                    route.structures,
                    route.name,
                    route_slug,
                    "Structures",
                    "Structures",
                    lambda row: row.geometry.intersection(corridor_geometry),
                    lambda row: _text(row.get("Name"), _text(row.get("PRIM_OCC"), "Structure")),
                    lambda row: _text(row.get("PRIM_OCC")),
                )
        finally:
            route.centerline.unload()
            route.corridor.unload()

    map_frame = gpd.GeoDataFrame(features, geometry="geometry", crs=cfg.PROJECT_CRS)
    map_frame = map_frame.to_crs(epsg=4326)
    map_frame.to_file(output_path, driver="GeoJSON", index=False)
    print(f"Interactive map data written to {output_path}")


if __name__ == "__main__":
    export_map_data()