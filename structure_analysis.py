import pandas as pd
import geopandas as gpd
import project_config as cfg

def main():
    cfg.STRUCTURES_SOURCE.load_data()
    structure_gdf = cfg.STRUCTURES_SOURCE._gdf
    try:
        for route in cfg.ROUTES_CONFIG:
            route.corridor.load_data()
            try:
                print(f"Performing structure analysis for route {route.name}...")
                corridor_gdf = route.corridor._gdf
                print(f"Analyzing structure layer for route {route.name}...")
                impacted_structures = gpd.sjoin(
                        structure_gdf, 
                        corridor_gdf[['geometry']],
                        how='inner', 
                        predicate='intersects'
                    ).copy()
                route.structures = impacted_structures.drop(columns=['geometry'])
            except Exception as e:
                print(f"Error occurred while analyzing route {route.name}: {e}")
            finally:
                route.corridor.unload()
    except Exception as e:
        print(f"Error occurred while analyzing structures: {e}")
    finally:
        cfg.STRUCTURES_SOURCE.unload()
