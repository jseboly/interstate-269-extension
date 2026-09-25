"""
Preparation of data for the Interstate 269 Extension project.
This script handles the initial processing and cleaning of raw data
to make it suitable for analysis and mapping purposes.
"""
import pandas as pd
import project_config as cfg
import utils

def prepare_centerlines():
    cl_layers = []
    for segment in cfg.CORRIDOR_CONFIG:
        cl_layers.append(utils.initialize_layer(segment, cfg.PROJECT_CRS))
        print(f"Prepared centerline layer for segment: {segment['name']}")
    combined_cls = pd.concat(
        [d["layer_object"] for d in cl_layers if "layer_object" in d], 
        ignore_index=True
        )
    return cl_layers, combined_cls

def prepare_corridors(cl_layers):
    corridor_layers = []
    for cl in cl_layers:
        corridor = cl.copy()
        corridor_gdf = cl["layer_object"].copy()
        corridor_gdf['geometry'] = corridor_gdf.buffer(distance=cfg.ROW_WIDTH_FEET)
        corridor["layer_object"] = corridor_gdf
        corridor_layers.append(corridor)
        print(f"Prepared corridor layer for: {cl['name']}")
    combined_corridors = pd.concat(
        [d["layer_object"] for d in corridor_layers if "layer_object" in d], 
        ignore_index=True
        )
    return corridor_layers, combined_corridors

def prepare_parcels(corridors):
    parcel_layers = []
    for parcel in cfg.PARCEL_SOURCES:
        parcel_layers.append(
            utils.initialize_layer(parcel, cfg.PROJECT_CRS, extent=corridors))
        print(f"Prepared parcel layer for: {parcel['name']}")
    return parcel_layers

def prepare_roads(corridors):
    road_layers = []
    for road in cfg.ROAD_SOURCES:
        road_layers.append(
            utils.initialize_layer(road, cfg.PROJECT_CRS, extent=corridors))
        print(f"Prepared road layer for: {road['name']}")
    return road_layers

def prepare_structures(corridors):
    structure_layers = []
    for structure in cfg.STRUCTURES_SOURCES:
        structure_layers.append(
            utils.initialize_layer(structure, cfg.PROJECT_CRS, extent=corridors))
        print(f"Prepared structure layer for: {structure['name']}")
    return structure_layers

def prepare_environmental_data(corridors):
    environmental_layers = []
    for env_data in cfg.ENVIRONMENTAL_SOURCES:
        environmental_layers.append(
            utils.initialize_layer(env_data, cfg.PROJECT_CRS, extent=corridors))
        print(f"Prepared environmental layer for: {env_data['name']}")
    return environmental_layers

def prepare_railroad_data(corridors):
    railroad_layers = []
    for railroad in cfg.RAILROAD_SOURCES:
        railroad_layers.append(
            utils.initialize_layer(railroad, cfg.PROJECT_CRS, extent=corridors))
        print(f"Prepared railroad layer for: {railroad['name']}")
    return railroad_layers

def prepare_datasets():
    cl_layers, combined_cls = prepare_centerlines()
    corridor_layers, combined_corridors = prepare_corridors(cl_layers)
    parcel_layers = prepare_parcels(combined_corridors)
    road_layers = prepare_roads(combined_corridors)
    structure_layers = prepare_structures(combined_corridors)
    environmental_layers = prepare_environmental_data(combined_corridors)
    railroad_layers = prepare_railroad_data(combined_corridors)

    return (cl_layers, combined_cls, corridor_layers, combined_corridors, 
            parcel_layers, road_layers, structure_layers, environmental_layers, 
            railroad_layers)