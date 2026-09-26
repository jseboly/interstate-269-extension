# configuration settings for the highway infrastructure project
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_FILE = os.path.join(PROJECT_ROOT, "analysis_results.md")

# corridors to analyze
CORRIDOR_CONFIG = [
    {
        "name": "North Option",
        "source_type": "FileGDBFeatureClass",
        "description": ("northern route option connecting Millington with I-55 "
                        "at Turrell, Arkansas"),
        "source_path": os.path.join(PROJECT_ROOT, "ProposedRoutes.gdb", 
                                    "NorthOption")
    },
    {
        "name": "South Option",
        "source_type": "FileGDBFeatureClass",
        "description": ("southern route option connecting Millington with I-40 "
                        "at West Memphis, Arkansas"),
        "source_path": os.path.join(PROJECT_ROOT, "ProposedRoutes.gdb", 
                                    "SouthOption")
    }
]

# data sources
PARCEL_SOURCES = [
    {
        "name": "Tennessee Parcels",
        "source_type": "Shapefile",
        "source_path": os.path.join(PROJECT_ROOT, "ShelbyCountyParcels.shp"),
        "owner_field": "OWNER",
        "parcel_id_field": "PARCELID"
    },
    {
        "name": "Arkansas Parcels",
        "source_type": "FeatureService",
        "source_path": "https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Planning_Cadastre/FeatureServer/6",
        "owner_field": "OWNER",
        "parcel_id_field": "PARCELID"
    }
]

ROADS_SOURCES = [
    {
        "name": "Interstates",
        "source_type": "FeatureService",
        "source_path": "https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/3"
    },
    {
        "name": "US Highways",
        "source_type": "FeatureService",
        "source_path": "https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/4"
    },
    {
        "name": "State Highways",
        "source_type": "FeatureService",
        "source_path": "https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/5"
    },
    {
        "name": "Local Roads",
        "source_type": "FeatureService",
        "source_path": "https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/7"
    }
]

RAILROADS_SOURCES = [
    {
        "name": "Railroads",
        "source_type": "FeatureService",
        "source_path": "https://cartowfs.nationalmap.gov/arcgis/rest/services/transportation/FeatureServer/6"
    }
]

ENVIRONMENTAL_SOURCES = [
    {
        "name": "Wetlands",
        "source_type": "FeatureService",
        "source_path": "https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/USA_Wetlands/FeatureServer/0"
    },
    {
        "name": "Water Bodies",
        "source_type": "FeatureService",
        "source_path": "https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Hydrography_Dataset_Plus_Medium_Resolution/FeatureServer/1"
    },
    {
        "name": "Streams",
        "source_type": "FeatureService",
        "source_path": "https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Hydrography_Dataset_Plus_Medium_Resolution/FeatureServer/2"
    },
    {
        "name": "Flood Zones",
        "source_type": "FeatureService",
        "source_path": "https://services5.arcgis.com/7weheFjxuNkGGiZi/arcgis/rest/services/National_Flood_Hazard_Layer/FeatureServer/0"
    },
    {
        "name": "Protected Areas",
        "source_type": "FeatureService",
        "source_path": "https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/PADUS_Protection_Status_by_GAP_Status_Code/FeatureServer/0"
    }
]

STRUCTURES_SOURCES = [
    {
        "name": "Structures",
        "source_type": "FeatureService",
        "source_path": "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/USA_Structures_View/FeatureServer/0"
    }
]

# project settings
PROJECT_CRS = "EPSG:2274"
ROW_WIDTH_FEET = 150
