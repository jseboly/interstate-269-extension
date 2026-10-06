import pandas as pd
import project_config as cfg
import utils
from analyze_parcels import get_entry_distances
import shapely
from shapely import Point

def main():
    for route in cfg.ROUTES_CONFIG:
        route.centerline.load_data()
        try:
            route_gdf = utils.clean_line_features(route.centerline._gdf)
            route_line = route_gdf.geometry.iloc[0]
            for layer in cfg.ENVIRONMENTAL_SOURCES:
                print(f"Analyzing route {route.name} with environmental layer {layer.name}...")
                layer.load_data()
                try:
                    layer_gdf = layer._gdf
                    layer_gdf = layer_gdf[layer_gdf.geometry.notnull() & ~layer_gdf.is_empty].copy()

                    if layer_gdf.empty:
                        print(f"Skipping {layer.name} for {route.name}: no valid geometries loaded.")
                        route.env_constraints[layer.description] = pd.DataFrame(
                            columns=["UniqueID", "Name"]
                        )
                        continue

                    layer_geom_type = layer_gdf.geometry.iloc[0].geom_type
                    fields_to_keep = [
                        field
                        for field in (layer.id_field, layer.name_field)
                        if field is not None and field in layer_gdf.columns
                    ]
                    fields_to_keep.append("geometry")

                    impacts = layer_gdf.loc[
                        layer_gdf.intersects(route_line), fields_to_keep
                        ].copy()
                    impacts = impacts.rename(columns={
                        field: output_name
                        for field, output_name in (
                            (layer.id_field, "UniqueID"),
                            (layer.name_field, "Name"),
                        )
                        if field in impacts.columns
                    })

                    if impacts.empty:
                        print(f"No intersecting features found for {layer.name} on {route.name}.")
                        route.env_constraints[layer.description] = pd.DataFrame(
                            columns=["UniqueID", "Name"]
                        )
                        continue

                    if layer_geom_type in ["LineString", "MultiLineString"]:
                        impacts["start_meas"] = impacts.geometry.map(
                            lambda geom: utils.get_crossing_m_value(geom, route_line)
                            )
                        impacts = impacts.dropna(subset=["start_meas"]).copy()
                    elif layer_geom_type in ["Polygon", "MultiPolygon"]:
                        distances = impacts.geometry.apply(
                            lambda poly: get_entry_distances(poly, route_line)
                        )
                        valid_distances = distances.dropna()
                        if valid_distances.empty:
                            route.env_constraints[layer.description] = pd.DataFrame(
                                columns=["UniqueID", "Name"]
                            )
                            continue

                        impacts[["start_meas", "end_meas"]] = pd.DataFrame(
                            valid_distances.tolist(), index=valid_distances.index
                        )
                    route.env_constraints[layer.description] = impacts.sort_values(
                                    by='start_meas', 
                                    ignore_index=True
                                    ).drop(columns=['geometry'])
                    print(f"Finished analyzing route {route.name} with environmental layer {layer.name}")
                except Exception as e:
                    print(f"Error occurred while analyzing layer {layer.name}: {e}")
                finally:
                    layer.unload()
        except Exception as e:
            print(f"Error occurred while analyzing route {route.name}: {e}")
        finally:
            route.centerline.unload()

def get_crossing_m_value(geometry, route_line):
    intersection = geometry.intersection(route_line)
    if intersection.is_empty:
        return None

    coords = shapely.get_coordinates(intersection)
    if len(coords) == 0:
        return None

    return min(route_line.project(Point(coords_i)) for coords_i in coords)
