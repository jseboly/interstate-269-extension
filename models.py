from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import pandas as pd
import geopandas as gpd

class GISFileType(str, Enum):
    SHAPEFILE = "shapefile"
    GDB_FEATURE_CLASS = "file_gdb_feature_class"
    GPKG_FEATURE_CLASS = "geopackage_feature_class"
    FEATURE_SERVICE = "feature_service"
    MAP_SERVICE = "map_service"

@dataclass
class GISLayer:
    name: str
    description: str = ""
    source_path: str
    source_type = GISFileType
    spatial_reference: int = 4326
    
    # Internal attribute holding the GeoDataFrame, hidden from initial creation
    _gdf: Optional[gpd.GeoDataFrame] = field(default=None, repr=False, init=False)

    @property
    def data(self) -> gpd.GeoDataFrame:
        """
        Lazy-loads and caches the GeoDataFrame.
        Reads from disk ONLY on the first call to layer.data.
        """
        if self._gdf is None:
            print(f"Reading {self.name} geometry into geodataframe...")
            self._gdf = gpd.read_file(self.source_path)
        return self._gdf

    def unload(self) -> None:
        """Explicitly clear RAM if the data is no longer needed."""
        self._gdf = None
        print(f"Unloaded {self.name} geodataframe.")

@dataclass
class ProjectRoute:
    name: str
    description: str = ""
    centerline: GISLayer
    corridor: GISLayer = None
    total_length: float = None
    total_area: float = None
    line_list: pd.DataFrame = None
    permits: dict = None
    env_constraints: dict = None
    structures: dict = None