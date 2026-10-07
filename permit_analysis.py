import project_config as cfg
import utils

def main():
    """
    Analyzes the required permit crossings for each route.
    """
    for route in cfg.ROUTES_CONFIG:
        route.centerline.load_data()
        try:
            route_gdf = utils.clean_line_features(route.centerline._gdf)
            route_line = route_gdf.geometry.iloc[0]
            for layer in cfg.PERMIT_SOURCES:
                print(f"Determining permit crossings for route: "
                    f"{route.name}, layer: {layer.name}...")
                layer.load_data()
                try:
                    layer_gdf = layer._gdf
                    fields_to_keep = [
                        field
                        for field in (layer.id_field, layer.name_field)
                        if field is not None and field in layer_gdf.columns
                    ]
                    fields_to_keep.append("geometry")

                    crossings = layer_gdf.loc[
                        layer_gdf.intersects(route_line), fields_to_keep
                        ].copy()
                    crossings = crossings.rename(columns={
                        field: output_name
                        for field, output_name in (
                            (layer.id_field, "UniqueID"),
                            (layer.name_field, "Name"),
                        )
                        if field in crossings.columns
                    })

                    crossings["Measure"] = crossings.geometry.map(
                        lambda geom: utils.get_crossing_m_value(geom, route_line)
                    )
                    crossings = crossings.sort_values(
                        by='Measure', 
                        ignore_index=True
                        ).drop(columns=['geometry'])
                    route.permits[layer.description] = crossings
                    print(f"Found {len(crossings)} permit crossings for layer "
                          f"{layer.name} on route {route.name}.")
                except Exception as e:
                    print(f"Error processing layer: {layer.name}, {e}")
                finally:
                    layer.unload()
        except Exception as e:
            print(f"Error processing route: {route.name}, {e}")
        finally:
            route.centerline.unload()
