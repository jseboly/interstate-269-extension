import geopandas as gpd
import os

def initialize_layer(layer_dict, desired_crs):
    layer_type = layer_dict.get("source_type")
    layer_path = layer_dict.get("source_path")
    
    if layer_type == "FileGDBFeatureClass":
        gdb_path, fc_name = os.path.split(layer_path)
        layer_dict["layer_object"] = gpd.read_file(gdb_path, layer=fc_name).to_crs(desired_crs)
    elif layer_type == "Shapefile":
        layer_dict["layer_object"] = gpd.read_file(layer_path).to_crs(desired_crs)
    elif layer_type == "Geopackage":
        gpkg_path, layer_name = os.path.split(layer_path)
        layer_dict["layer_object"] = gpd.read_file(gpkg_path, layer=layer_name).to_crs(desired_crs)
    else:
        raise ValueError(f"Unsupported layer type: {layer_type}")
    return layer_dict
