# configuration settings for the highway infrastructure project
import os
import models
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_FILE = os.path.join(PROJECT_ROOT, "Results.md")
RESULTS_CACHE_FILE = os.path.join(PROJECT_ROOT, "analysis_results_cache.json")
PROJECT_CRS = 2274 # NAD 1983 TN State Plane - US Feet
PROJECT_BBOX = (699751.991850, 328985.445673, 804671.224006, 415248.428825)
ROW_WIDTH_FEET = 150 # Width of ROW from centerline on each side

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
        name_field="OWNER",
        id_field="PARCELID"
    ),
    models.GISLayer(
        name="Arkansas Parcels",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Planning_Cadastre/FeatureServer/6",
        epsg_code=PROJECT_CRS,
        bbox=PROJECT_BBOX,
        name_field="ownername",
        id_field="parcelid"
    )
]

PERMIT_SOURCES = [
    models.GISLayer(
        name="Interstates",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/3",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Interstate Highway',
        name_field="name",
        id_field="permanent_identifier"
    ),
    models.GISLayer(
        name="US Highways",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/4",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'US Highway',
        name_field="name",
        id_field="permanent_identifier"
    ),
    models.GISLayer(
        name="State Highways",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/5",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'State Highway',
        name_field="name",
        id_field="permanent_identifier"
    ),
    models.GISLayer(
        name="Local Roads",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/7",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Local Road',
        name_field="name",
        id_field="permanent_identifier"
    ),
    models.GISLayer(
            name="Railroads",
            source_type=models.GISFileType.FEATURE_SERVICE,
            source_path="https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/6",
            bbox=PROJECT_BBOX,
            epsg_code=PROJECT_CRS,
            description = 'Railroad',
            name_field="railowner",
            id_field="permanent_identifier"
        )
]

ENVIRONMENTAL_SOURCES = [
    models.GISLayer(
        name="Wetlands",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/USA_Wetlands/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Wetland',
        name_field="WETLAND_TYPE",
        id_field="OBJECTID"
    ),
    models.GISLayer(
        name="Water Bodies",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Hydrography_Dataset_Plus_Medium_Resolution/FeatureServer/1",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Waterbody',
        name_field="GNIS_NAME",
        id_field="OBJECTID"
    ),
    models.GISLayer(
        name="Streams",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Hydrography_Dataset_Plus_Medium_Resolution/FeatureServer/2",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description='Stream',
        name_field="GNIS_NAME",
        id_field="GNIS_ID"
    ),
    models.GISLayer(
        name="Flood Zones",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/USA_Flood_Hazard_Areas_view/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Flood Zone',
        name_field="FLD_ZONEw",
        id_field="OBJECTID"
    ),
    models.GISLayer(
        name="Protected Areas",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/PADUS_Protection_Status_by_GAP_Status_Code/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Protected Area',
        name_field="Unit_Nm",
        id_field="OBJECTID"
    )
]

STRUCTURES_SOURCE = models.GISLayer(
        name="Structures",
        source_type=models.GISFileType.FEATURE_SERVICE,
        source_path="https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/USA_Structures_View/FeatureServer/0",
        bbox=PROJECT_BBOX,
        epsg_code=PROJECT_CRS,
        description = 'Structure',
        name_field="PRIM_OCC",
        id_field="BUILD_ID"
    )
