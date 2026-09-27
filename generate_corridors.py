import project_config as cfg
import models
import utils
import os

def generate_corridor(route):
    """Generates the ROW corridor for the given route."""
    print(f"Generating corridor for route: {route.name}")
    centerline_layer = route.centerline
    gdb_path = os.path.join(cfg.PROJECT_ROOT, "ProjectCorridors.gdb")
    layer_name = utils.clean_string(f"{route.name}Corridor")

    os.makedirs(gdb_path, exist_ok=True)

    centerline_layer.load_data()
    try:
        buffered_gdf = centerline_layer._gdf.copy()
        buffered_gdf["geometry"] = buffered_gdf.buffer(cfg.ROW_WIDTH_FEET, cap_style='flat')
        print(f"Buffered geometry for route: {route.name}")

        buffered_gdf.to_file(
            filename=gdb_path,
            layer=layer_name,
            driver="OpenFileGDB"
        )
        print(f"Corridor for route: {route.name} has been generated and saved.")

        route.corridor = models.GISLayer(
            name=f"{route.name} Corridor",
            source_type=models.GISFileType.GDB_FEATURE_CLASS,
            epsg_code=cfg.PROJECT_CRS,
            source_path=os.path.join(gdb_path, layer_name),
        )
    finally:
        centerline_layer.unload()
        del buffered_gdf

def generate_corridors():
    for route in cfg.ROUTES_CONFIG:
        # generate corridor for each route
        generate_corridor(route)
    print("All corridors have been generated and saved.")