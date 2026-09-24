"""
Preparation of data for the Interstate 269 Extension project.
This script handles the initial processing and cleaning of raw data
to make it suitable for analysis and mapping purposes.
"""
import geopandas as gpd
import os
import project_config as cfg

def prepare_centerlines():
    cl_layers = []
    for segment in cfg.CORRIDOR_CONFIG:
        # Process each segment of the centerline
        gdb_path, fc_name = os.path.split(segment["source_path"])
        cl_lyr = gpd.read_file(gdb_path, layer=fc_name)
        segment["layer_object"] = cl_lyr
        cl_layers.append(segment)
        print(f"Prepared centerline layer for segment: {segment['name']}")
    return cl_layers

def prepare_parcels(cl_layers):
    
    pass

def prepare_roads():
    pass

def prepare_structures():
    pass

def prepare_environmental_data():
    pass

def prepare_datasets():
    cl_layers = prepare_centerlines()
    parcel_layer = prepare_parcels(cl_layers)
    prepare_roads()
    prepare_structures()
    prepare_environmental_data()

if __name__ == "__main__":
    prepare_datasets()