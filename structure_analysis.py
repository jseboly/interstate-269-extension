import geopandas as gpd
import project_config as cfg

def main():
    """
    Analyze structures within the corridor of each route.
    """
    cfg.STRUCTURES_SOURCE.load_data()
    structure_gdf = cfg.STRUCTURES_SOURCE._gdf
    try:
        for route in cfg.ROUTES_CONFIG:
            route.corridor.load_data()
            try:
                print(f"Performing structure analysis for route {route.name}...")
                corridor_gdf = route.corridor._gdf
                impacted_structures = gpd.sjoin(
                        structure_gdf, 
                        corridor_gdf[['geometry']],
                        how='inner', 
                        predicate='intersects'
                    ).copy()
                route.structures = impacted_structures.drop(columns=['geometry'])
                print(f"{len(impacted_structures)} structures found within the "
                      f"corridor of route {route.name}.")
            except Exception as e:
                print(f"Error occurred while analyzing route {route.name}: {e}")
            finally:
                route.corridor.unload()
    except Exception as e:
        print(f"Error occurred while analyzing structures: {e}")
    finally:
        print("Structure analysis completed.")
        cfg.STRUCTURES_SOURCE.unload()
