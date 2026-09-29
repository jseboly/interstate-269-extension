# configuration settings for the highway infrastructure project
import os
import models
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_FILE = os.path.join(PROJECT_ROOT, "analysis_results.md")
PROJECT_CRS = 2274
PROJECT_BBOX = (699751.991850, 328985.445673, 804671.224006, 415248.428825)
ROW_WIDTH_FEET = 150

# corridors to analyze
ROUTES_CONFIG = [
    models.ProjectRoute(
        name="North Option",
        centerline=models.GISLayer(
            name="North Option",
            source_type=models.GISFileType.GDB_FEATURE_CLASS,
            epsg_code=PROJECT_CRS,
            source_path=os.path.join(PROJECT_ROOT, "ProposedRoutes.gdb", 
                                     "NorthOption")
        ),
        description=("northern route option connecting Millington with I-55 "
                     "at Turrell, Arkansas")
    ),
   
    models.ProjectRoute(
        name="South Option",
        centerline=models.GISLayer(
            name="South Option",
            source_type=models.GISFileType.GDB_FEATURE_CLASS,
            epsg_code=PROJECT_CRS,
            source_path=os.path.join(PROJECT_ROOT, "ProposedRoutes.gdb", 
                                     "SouthOption")
        ),
        description=("southern route option connecting Millington with I-40 "
                     "at West Memphis, Arkansas")
    )
]

# data sources
PARCEL_SOURCES = [
    models.GISLayer(
        name="Tennessee Parcels",
        source_type=models.GISFileType.SHAPEFILE,
        source_path=os.path.join(PROJECT_ROOT, "ShelbyCountyParcels.shp"),
        epsg_code=PROJECT_CRS,
        owner_field="OWNER",
        parcel_id_field="PARCELID"
    ),
    models.GISLayer(
        name="Arkansas Parcels",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Planning_Cadastre/FeatureServer/6",
        epsg_code=PROJECT_CRS,
        bbox=PROJECT_BBOX,
        owner_field="ownername",
        parcel_id_field="parcelid"
    )
]

PERMIT_SOURCES = [
    models.GISLayer(
        name="Interstates",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/3",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="US Highways",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/4",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="State Highways",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/5",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="Local Roads",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/7",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
            name="Railroads",
            source_type=models.GISFileType.FEATURE_SERVICE,
            source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/6",
            bbox=PROJECT_BBOX,
            epsg_code=PROJECT_CRS
        )
]

ENVIRONMENTAL_SOURCES = [
    models.GISLayer(
        name="Wetlands",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/USA_Wetlands/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="Water Bodies",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Hydrography_Dataset_Plus_Medium_Resolution/FeatureServer/1",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="Streams",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Hydrography_Dataset_Plus_Medium_Resolution/FeatureServer/2",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="Flood Zones",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Flood_Hazard_Layer/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    ),
    models.GISLayer(
        name="Protected Areas",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/PADUS_Protection_Status_by_GAP_Status_Code/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    )
]

STRUCTURES_SOURCES = [
    models.GISLayer(
        name="Structures",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/USA_Structures_View/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS
    )
]


