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
    def load_data(self) -> gpd.GeoDataFrame:
        """
        Lazy-loads and caches the GeoDataFrame.
        Reads from disk ONLY on the first call to layer.load_data.
        """
        if self._gdf is None:
            print(f"Reading {self.name} geometry into geodataframe...")
            if self.source_type == GISFileType.FEATURE_SERVICE:
                self._gdf = self._load_from_feature_service(self.source_path)
            else:
                self._gdf = gpd.read_file(self.source_path)
        return self._gdf

    def _load_from_feature_service(self, url, bbox=None) -> gpd.GeoDataFrame:
        """Handles REST / Web Feature Service loads with server-side spatial filtering."""
        
        # Method A: Standard GeoPandas read using GDAL/Fiona driver
        try:
            return gpd.read_file(url, bbox=bbox)
        except Exception as err:
            # Method B: Fallback using Esri JSON / ArcGIS REST query params
            return self._fetch_arcgis_rest_query(url, bbox=bbox)

    def _fetch_arcgis_rest_query(self, url, bbox = None) -> gpd.GeoDataFrame:
        """
        Manual fallback for ArcGIS REST Feature Layer /query endpoints.
        Constructs a REST query with spatial envelope filtering.
        """
        import requests

        query_url = url.rstrip('/') + '/query' if not url.endswith('/query') else url
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "geojson",
            "outSR": self.epsg_code
        }

        if bbox:
            minx, miny, maxx, maxy = bbox
            params.update({
                "geometry": f"{minx},{miny},{maxx},{maxy}",
                "geometryType": "esriGeometryEnvelope",
                "spatialRel": "esriSpatialRelIntersects",
                "inSR": self.epsg_code
            })

        response = requests.get(query_url, params=params)
        response.raise_for_status()
        return gpd.read_file(response.text)

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