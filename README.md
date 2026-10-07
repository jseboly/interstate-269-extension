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
* description (optional): This should be used to indicate which type of feature is being represented in this layer (e.g. Road, Railroad, Stream, etc.). Whatever is passed to this attribute will appear in the results document as the descriptor for any impacts arising from that layer.
* name_field (optional): For parcel datasets, this should be set to the field containing the landowner names. For others, you may set it to the field that contains names if you want to see those names reflected in the results document.
* id_field (optional): For parcel datasets, this should be set to the field containing the parcel id. For others, it may be set to any field that contains an identifying number/string.
* bbox (optional): bounding box coordinates

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
All landowner parcels intersecting the centerline and corridor for each route will be pulled and arranged in tabluar (line list) form. The start milepost, end milepost, centerline length, and corridor area for each parcel will be included.

Counts, lengths, and areas impacted can be broken down by owner type if owner classification (optional) is enabled. To enable it, install the OpenAI SDK with
`python -m pip install openai` and set `OPENAI_API_KEY` in the environment
before running the analysis. `OWNER_CLASSIFICATION_MODEL` can override the
default model (`gpt-4o-mini`). Without an API key, rows receive
cached classifications when available; uncached rows receive
`OwnerType="not_classified"` and a null `OwnerTypeConfidence`.

When enabled, unique owner names are sent to OpenAI in batches. Results are
stored in `OwnerType` and `OwnerTypeConfidence` columns and cached locally in
`owner_classification_cache.json` for reuse across routes and later runs. The
cache may contain personal owner names. Review your data-handling requirements
before enabling external classification. Confidence is the model's estimate,
not a calibrated probability; ambiguous names are classified as `unknown`.

### Permit Analysis
A permit crossing analysis will be performed for all layers configured in `PERMIT_SOURCES`. The number of crossings by type, a list of crossings (with names if available), and the milepost for each crossing will be pulled.

### Environmental Analysis
An environmental constraint analysis will be performed for all layers configured in `ENVIRONMENTAL_SOURCES`. Environmental layers can be either lines or polygons. For line layers, a list of impacted features with the milepost of their intersection with the route will be generated. For polygon layers, the list of impacted features will include the start milepost, end milepost, length affected, and area affected.

### Structure Analysis
The number of structures within the corridor for each route will also be calculated, along with a list of structures and their types.
