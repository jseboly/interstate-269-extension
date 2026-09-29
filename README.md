# Interstate 269 Extension
## Overview
This is a sample linear infrastructure project to demonstrate common GIS workflows and analysis that might be performed when planning a project. This project covers a fictional extension of I-269 in Tennessee and Arkansas, but the scripts can easily be adapted to any project anywhere, for projects like:
* Roads
* Railroads
* Powerlines
* Pipelines
* Telecommunications lines
* Fiber Optic lines

Two options are being considered for this extension. The "North Option" runs 
northwest from Millington, bypasses Meeman-Shelby Forest State Park to the north,
then ties in with Interstate 55 north of Turrell, Arkansas. The "South Option" 
proceeds southwest from Millington, bypasses Meeman-Shelby Forest State Park to
the south, and then continues southwest towards West Memphis, Arkansas and ends
at the I-55 and I-40 interchange.

## Configuration
The project configuration is managed entirely within project_config.py. All paths, data sources, and analysis parameters are defined as Python data structures. 

### Project Settings
Global spatial and analysis parameters applied across the pipeline:
* PROJECT_CRS: Projected Coordinate Reference System used for geometric calculations.
* PROJECT_BBOX: Bounding box to use when pulling data from online sources like feature services. This should encompass the entire area affected by the project. It might be helpful to consult a tool like https://vibhorsingh.com/boundingbox to calculate the bounding box. The bounding box coordinates MUST be in the same coordinate reference system as the one specified in PROJECT_CRS.
* ROW_WIDTH_FEET (default: 150): Right-of-Way (ROW) buffer distance in feet applied to corridor centerlines for footprint impact analysis.

### Corridors (ROUTES_CONFIG)
A list of ProjectRoute objects. Defines the route options being analyzed. One or more entries are required. Here are the attributes:
* name: Display name for the corridor option.
* centerline: a GISLayer object representing the project's centerline. GISLayer objects are explained below.
* description (optional)

### GISLayer objects
In the context of this project, a GISLayer is an object that holds references to GIS data and information about that data. It has the following attributes:
* name: A user-friendly name/label for the layer.
* source_path: The path of the GIS data file to be associated with this layer.
* source_type: SHAPEFILE, GDB_FEATURE_CLASS, GPKG_FEATURE_CLASS, FEATURE_SERVICE
* epsg_code: The desired spatial reference of the data. If the referenced GIS file/service is in a different spatial reference, the data will be projected into the one specified here before any analysis is done.
* description (optional)
* owner_field (optional, used for parcel datasets)
* parcel_id_field (optional, used for parcel datasets)
* bbox (optional, bounding box coordinates)

### Analysis data sources
PARCEL_SOURCES, PERMIT_SOURCES, ENVIRONMENTAL_SOURCES, STRUCTURES_SOURCES

Each of these are lists of GISLayer objects representing reference data to be used for project analysis. The names, source paths, and source types can be changed as desired for the individual project. The layer names are important as they will determine what is used to refer to that layer in the analysis results document. For the parcel sources only, the owner_field and parcel_id_field attributes must be set for the parcel analysis to work.

### Customizing Configuration
To adjust the analysis for new routes, updated parameters, or different layers:
* Change ROW Width: Modify ROW_WIDTH_FEET = <new_distance> to expand or contract the buffer zones.
* Add a Route Option: Append a GisLayer object to the CORRIDOR_CONFIG. 
* Swap Data Layers: Update source_path URLs or local paths under the appropriate source list (ENVIRONMENTAL_SOURCES, PARCEL_SOURCES, etc.).

## Execution
When all configuration settings are ready, run "Orchestrator.py" to perform the analysis. The results of the analysis will be written to the file specified as RESULTS_FILE in the config file. 

## Provided Results
Here is a description of the results that this tool can calculate for you.
### Parcel Analysis
### Crossing Analysis
### Environmental Analysis
### Structure Analysis

