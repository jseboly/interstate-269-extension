from dataclasses import dataclass, field
from enum import Enum
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
class GISLayer: # A reference to a GIS file with information about its source and contents
    name: str
    source_path: str
    source_type: GISFileType
    epsg_code: int = 4326
    description: str = ""
    
    # Internal attribute holding the GeoDataFrame, hidden from initial creation
    _gdf: Optional[gpd.GeoDataFrame] = field(default=None, repr=False, init=False)
    
    # Other optional attributes
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
                self._gdf = self._load_from_feature_service(
                    self.source_path, bbox=self.bbox)
            elif self.source_type == GISFileType.SHAPEFILE:
                self._gdf = gpd.read_file(
                    self.source_path
                    ).to_crs(self.epsg_code)
            else:
                gdb_path, fc_name = os.path.split(self.source_path)
                self._gdf = gpd.read_file(
                    gdb_path, layer=fc_name
                    ).to_crs(self.epsg_code)
        return self._gdf

    def _load_from_feature_service(
        self, url: str, bbox=None, timeout: float = 30
    ) -> gpd.GeoDataFrame:
        """
        Handles REST / Web Feature Service loads with server-side spatial filtering.
        """        
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
        Fetches all matching object IDs, then retrieves features in batches to
        avoid the service's per-query record limit.
        """
        from collections import deque
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

        ids_params = {
            **params,
            "f": "json",
            "returnIdsOnly": "true",
            "returnGeometry": "false",
        }
        ids_response = requests.get(query_url, params=ids_params, timeout=timeout)
        ids_response.raise_for_status()
        ids_payload = ids_response.json()
        if (
            not isinstance(ids_payload, dict)
            or not isinstance(ids_payload.get("objectIds"), list)
            or (
                ids_payload["objectIds"]
                and not isinstance(ids_payload.get("objectIdFieldName"), str)
            )
        ):
            raise ValueError(
                f"ArcGIS ID query returned an unexpected payload for {url!r}: "
                f"{ids_payload}"
            )
        object_ids = ids_payload["objectIds"]
        object_id_field = ids_payload.get("objectIdFieldName")

        crs = self.epsg_code
        if not object_ids:
            return gpd.GeoDataFrame(geometry=[], crs=crs)

        batch_size = 1000
        pending_batches = deque(
            object_ids[start:start + batch_size]
            for start in range(0, len(object_ids), batch_size)
        )
        features = []
        object_id_field_key = object_id_field.casefold()

        while pending_batches:
            batch = pending_batches.popleft()
            batch_params = {
                **params,
                "objectIds": ",".join(str(object_id) for object_id in batch),
            }
            response = requests.get(
                query_url, params=batch_params, timeout=timeout
            )
            response.raise_for_status()
            payload = response.json()
            if (
                not isinstance(payload, dict)
                or not isinstance(payload.get("features"), list)
            ):
                raise ValueError(
                    f"ArcGIS feature query returned an unexpected payload for "
                    f"{url!r}: {payload}"
                )

            batch_features = payload["features"]
            returned_ids = {
                str(value)
                for feature in batch_features
                for key, value in (feature.get("properties") or {}).items()
                if str(key).casefold() == object_id_field_key and value is not None
            }
            requested_ids = {str(object_id) for object_id in batch}
            has_missing_features = (
                len(batch_features) != len(batch)
                or returned_ids != requested_ids
            )
            exceeded_limit = payload.get("exceededTransferLimit", False)
            if exceeded_limit or has_missing_features:
                if len(batch) == 1:
                    raise ValueError(
                        f"ArcGIS feature query could not retrieve object ID "
                        f"{batch[0]!r} from {url!r}; "
                        f"exceededTransferLimit={exceeded_limit}."
                    )
                midpoint = len(batch) // 2
                pending_batches.appendleft(batch[midpoint:])
                pending_batches.appendleft(batch[:midpoint])
                continue

            if len(features) == 0 and isinstance(payload.get("crs"), dict):
                crs_name = payload["crs"].get("properties", {}).get("name")
                if (
                    isinstance(crs_name, str)
                    and crs_name.upper().startswith("EPSG:")
                ):
                    try:
                        crs = int(crs_name.split(":", 1)[1])
                    except ValueError:
                        pass
            features.extend(batch_features)

        return gpd.GeoDataFrame.from_features(features, crs=crs)

    def unload(self) -> None:
        """Explicitly clear RAM if the data is no longer needed."""
        self._gdf = None
        print(f"Unloaded {self.name} geodataframe.")

@dataclass
class ProjectRoute: # A reference to a project route option to be analyzed
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

    def calculate_basic_metrics(self) -> None:
        """
        Calculates total length for the route and area of the corridor.
        """
        centerline = self.centerline.load_data()
        try:
            self.total_length = centerline.geometry.length.sum()
            print(f"Total length for route {self.name}: {self.total_length}")
        except Exception as e:
            print(f"Error occurred while calculating total length for route "
                  f"{self.name}: {e}")
        finally:
            self.centerline.unload()

        corridor = self.corridor.load_data()
        try:
            self.total_area = corridor.geometry.area.sum()
            print(f"Total area for route {self.name}: {self.total_area}")
        except Exception as e:
            print(f"Error occurred while calculating total area for route "
                  f"{self.name}: {e}")
        finally:
            self.corridor.unload()