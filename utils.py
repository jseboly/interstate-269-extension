import geopandas as gpd
import os
import json
from pathlib import Path
import requests
from shapely.geometry.base import BaseGeometry

def get_feature_service_metadata(service_url, timeout=60):
    metadata_response = requests.get(
        service_url,
        params={"f": "json"},
        timeout=timeout,
    )
    metadata_response.raise_for_status()
    metadata = metadata_response.json()
    if "error" in metadata:
        raise RuntimeError(
            f"Unable to read Feature Service metadata: "
            f"{metadata['error']}"
        )
    service_sr = (
            metadata.get("extent", {}).get("spatialReference")
            or metadata.get("spatialReference")
        )
    if service_sr is None:
        raise RuntimeError(
            "Could not determine the Feature Service spatial reference."
        )
    return metadata, service_sr

def prepare_extent_geometry(extent, extent_crs):
    """
    Returns
    -------
    extent_geometry : BaseGeometry or None
        The prepared extent geometry.
    source_crs : CRS or None
        The source CRS of the extent geometry.
    Returns the prepared extent geometry and its source CRS.
    """
    extent_geometry = None

    if extent is not None:

        # GeoDataFrame
        if isinstance(extent, gpd.GeoDataFrame):

            if extent.crs is None:
                raise ValueError(
                    "The extent GeoDataFrame does not have a CRS."
                )

            if len(extent) == 0:
                raise ValueError(
                    "The extent GeoDataFrame contains no geometries."
                )

            extent_geometry = extent.geometry.union_all()
            source_crs = extent.crs

        # GeoSeries
        elif isinstance(extent, gpd.GeoSeries):

            if extent.crs is None:
                raise ValueError(
                    "The extent GeoSeries does not have a CRS."
                )

            if len(extent) == 0:
                raise ValueError(
                    "The extent GeoSeries contains no geometries."
                )

            extent_geometry = extent.union_all()
            source_crs = extent.crs

        # Shapely geometry
        elif isinstance(extent, BaseGeometry):

            extent_geometry = extent

            if extent_crs is None:
                raise ValueError(
                    "extent_crs must be provided when extent is "
                    "a Shapely geometry."
                )

            source_crs = extent_crs

        else:
            raise TypeError(
                "extent must be a GeoDataFrame, GeoSeries, "
                "or Shapely geometry."
            )
    return extent_geometry, source_crs

def reproject_extent_geometry(extent_geometry, source_crs, service_sr):
    """
    Reproject the extent geometry to the Feature Service's spatial reference.
    """
    extent_gdf = gpd.GeoDataFrame(geometry=[extent_geometry], crs=source_crs)
    service_epsg = service_sr.get("wkid")

    if service_epsg is not None:
        extent_gdf = extent_gdf.to_crs(epsg=service_epsg)
    else:
        raise RuntimeError(
            "Feature Service uses a spatial reference that could "
            "not be converted to an EPSG code."
        )
    extent_geometry = extent_gdf.geometry.iloc[0]
    return extent_geometry

def build_query_parameters(
    extent_geometry=None,
    out_fields="*",
    return_geometry=True,
    page_size=1000,
    service_sr=None,
):
    """
    Build the query parameters for an ArcGIS Feature Service query request.
    """
    query_params = { "outFields": out_fields, "returnGeometry": return_geometry } 
    
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "resultOffset": 0,
        "resultRecordCount": page_size,
    }

    if extent_geometry is not None:

        # ArcGIS expects an envelope for the geometry parameter.
        bounds = extent_geometry.bounds

        xmin, ymin, xmax, ymax = bounds

        params["geometry"] = json.dumps({
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
            "spatialReference": service_sr,
        })

        params["geometryType"] = "esriGeometryEnvelope"
        params["spatialRel"] = "esriSpatialRelIntersects"

    return params

def fetch_feature_service_features(
    service_url,
    params,
    output_path,
    timeout=60
):

    """
    Fetch features from an ArcGIS Feature Service layer based on the provided 
    query parameters.
    """ 
    query_url = f"{service_url}/query"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_features = 0
    first_feature = True

    with requests.Session() as session:
        with output_path.open("w", encoding="utf-8") as output:
            output.write(
                '{"type":"FeatureCollection","features":['
            )

            while True:
                response = session.get(
                    query_url,
                    params=params,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    raise RuntimeError(
                        f"ArcGIS query failed: {data['error']}"
                    )
                
                features = data.get("features", [])
                for feature in features:
                    if not first_feature:
                        output.write(",")
                    json.dump(
                        feature,
                        output,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    first_feature = False
                    total_features += 1
                print(
                    f"Exported {total_features:,} features...",
                    end="\r",
                )

                # Stop when ArcGIS says there are no more results.
                if (
                    not data.get("exceededTransferLimit", False)
                    or not features
                ):
                    break

                params["resultOffset"] += len(features)

            output.write("]}")
    return total_features

def export_feature_service_to_geojson(
    service_url,
    output_path,
    extent=None,
    extent_crs=None,
    page_size=1000,
    timeout=60,
):
    """
    Export all features from an ArcGIS Feature Service layer to GeoJSON.

    Parameters
    ----------
    service_url : str
        URL of the ArcGIS Feature Service layer.

    output_path : str or pathlib.Path
        Path to the output GeoJSON file.

    extent : GeoSeries, GeoDataFrame, or Shapely geometry, optional
        Geometry used to spatially filter the features.
        If a GeoSeries or GeoDataFrame is provided, its CRS is used
        automatically.
        If a Shapely geometry is provided, extent_crs must also be
        provided.

    extent_crs : str or CRS, optional
        CRS of a Shapely extent geometry.
        Examples:
            "EPSG:4326"
            "EPSG:3857"
        Not required when extent is a GeoSeries or GeoDataFrame.

    page_size : int, optional
        Number of features requested per page.

    timeout : int or float, optional
        HTTP request timeout in seconds.

    Notes
    The extent geometry is transformed to the Feature Service's
    spatial reference before being sent to ArcGIS.
    """

    output_path = Path(output_path)
    query_url = f"{service_url.rstrip('/')}/query"

    # Get Feature Service metadata
    _, service_sr = get_feature_service_metadata(
        service_url, 
        timeout=timeout
        )
    
    # Prepare optional extent
    extent_geometry, source_crs = prepare_extent_geometry(
        extent=extent,
        extent_crs=extent_crs
    )

    # Reproject the extent geometry to the Feature Service's spatial reference
    extent_geometry = reproject_extent_geometry(
        extent_geometry=extent_geometry,
        source_crs=source_crs,
        service_sr=service_sr
    )

    # Build query parameters
    query_params = build_query_parameters(
        extent_geometry=extent_geometry,
        out_fields="*",
        return_geometry=True,
        page_size=page_size,
        service_sr=service_sr
    )

    # Fetch features from the Feature Service
    total_features = fetch_feature_service_features(
        query_url=query_url,
        params=query_params,
        output_path=output_path,
        page_size=page_size,
        timeout=timeout
    )
    
    print(f"Finished. Exported {total_features} features.")
    print(f"Output: {output_path}")
    return output_path

def initialize_layer(layer_dict, desired_crs, extent=None):
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
    elif layer_type == "FeatureService":
        geojson_path = os.path.join(os.getcwd(), f"{layer_dict['name']}.geojson")
        export_feature_service_to_geojson(
            service_url=layer_path,
            output_path=geojson_path,
            extent=extent
        )
        layer_dict["layer_object"] = gpd.read_file(geojson_path).to_crs(desired_crs)
    else:
        raise ValueError(f"Unsupported layer type: {layer_type}")
    return layer_dict
