from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
import os
from typing import Optional
import pandas as pd
import geopandas as gpd

class GISFileType(str, Enum):
    SHAPEFILE = "shapefile"
    GDB_FEATURE_CLASS = "file_gdb_feature_class"
    GPKG_FEATURE_CLASS = "geopackage_feature_class"
    FEATURE_SERVICE = "feature_service"

@dataclass
class GISLayer:
    name: str
    source_path: str
    source_type: GISFileType
    epsg_code: int = 4326
    description: str = ""
    
    # Internal attribute holding the GeoDataFrame, hidden from initial creation
    _gdf: Optional[gpd.GeoDataFrame] = field(default=None, repr=False, init=False)
    name_field: Optional[str] = None
    id_field: Optional[str] = None
    type_field: Optional[str] = None
    bbox: Optional[tuple] = None

    def load_data(self) -> gpd.GeoDataFrame:
        """
        Lazy-loads and caches the GeoDataFrame.
        Reads from disk only on the first call to layer.load_data().
        """
        if self._gdf is None:
            print(f"Reading {self.name} geometry into geodataframe...")
            if self.source_type == GISFileType.FEATURE_SERVICE:
                self._gdf = self._load_from_feature_service(self.source_path, bbox=self.bbox)
            elif self.source_type == GISFileType.SHAPEFILE:
                self._gdf = gpd.read_file(self.source_path).to_crs(self.epsg_code)
            else:
                gdb_path, fc_name = os.path.split(self.source_path)
                self._gdf = gpd.read_file(gdb_path, layer=fc_name).to_crs(self.epsg_code)
        return self._gdf

    def _load_from_feature_service(
        self, url: str, bbox=None, timeout: float = 30
    ) -> gpd.GeoDataFrame:
        """Handles REST / Web Feature Service loads with server-side spatial filtering."""
        
        # Method A: Standard GeoPandas read using GDAL/Fiona driver
        try:
            return gpd.read_file(url, bbox=bbox)
        except Exception as read_error:
            # Method B: Fallback using Esri JSON / ArcGIS REST query params
            try:
                return self._fetch_arcgis_rest_query(
                    url, bbox=bbox, timeout=timeout
                )
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Could not load feature service {url!r}. "
                    f"GeoPandas error: {read_error}; "
                    f"REST fallback error: {fallback_error}"
                ) from fallback_error

    def _fetch_arcgis_rest_query(
        self, url: str, bbox=None, timeout: float = 600
    ) -> gpd.GeoDataFrame:
        """
        Manual fallback for ArcGIS REST Feature Layer /query endpoints.
        Constructs a REST query with spatial envelope filtering and parses the
        GeoJSON response directly.
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

        response = requests.get(query_url, params=params, timeout=timeout)
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict) or "features" not in payload:
            raise ValueError(
                f"ArcGIS query returned an unexpected payload for {url!r}: "
                f"{payload[:200] if isinstance(payload, str) else payload}"
            )

        crs = self.epsg_code
        if isinstance(payload.get("crs"), dict):
            crs_name = payload["crs"].get("properties", {}).get("name")
            if isinstance(crs_name, str) and crs_name.upper().startswith("EPSG:"):
                try:
                    crs = int(crs_name.split(":", 1)[1])
                except ValueError:
                    pass

        return gpd.GeoDataFrame.from_features(payload["features"], crs=crs)

    def unload(self) -> None:
        """Explicitly clear RAM if the data is no longer needed."""
        self._gdf = None
        print(f"Unloaded {self.name} geodataframe.")

@dataclass
class ProjectRoute:
    name: str    
    centerline: GISLayer
    corridor: GISLayer = field(default=None)
    total_length: float = field(default=None)
    total_area: float = field(default=None)
    line_list: pd.DataFrame = field(default=None)
    permits: dict = field(default_factory=dict)
    env_constraints: dict = field(default_factory=dict)
    structures: pd.DataFrame = field(default=None)
    description: str = field(default="")