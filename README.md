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
### Corridors (CORRIDOR_CONFIG)
Defines the alternative routes being analyzed. One or more entries are required. Each entry in the list requires:

name: Display name for the corridor option.

description: Summary of the route alignment.

source_path: Local file path or Geodatabase feature class path (uses os.path.join(PROJECT_ROOT, ...) for portability).

### Analysis data sources
Data sources can be local vector datasets or remote REST Feature Services. Each entry is structured as a dictionary containing:

* name: Label for the layer.
* source_type: Data type indicator 
  * valid values: "Shapefile", "FileGDBFeatureClass", "Geopackage", "FeatureService"
* source_path: Relative file path or full ArcGIS REST Feature Service URL.
* owner_field / parcel_id_field (Parcels only): Attribute field mappings required for ownership impact reporting.

### Project Settings
Global spatial and analysis parameters applied across the pipeline:
* PROJECT_CRS: Projected Coordinate Reference System used for geometric calculations. 
* ROW_WIDTH_FEET (default: 150): Right-of-Way (ROW) buffer distance in feet applied to corridor centerlines for footprint impact analysis.

### Customizing Configuration
To adjust the analysis for new routes, updated parameters, or different layers:
* Change ROW Width: Modify ROW_WIDTH_FEET = <new_distance> to expand or contract the buffer zones.
* Add a Route Option: Append a new dictionary entry to the CORRIDOR_CONFIG list specifying its path within ProposedRoutes.gdb.
* Swap Data Layers: Update source_path URLs or local paths under the appropriate source list (ENVIRONMENTAL_SOURCES, PARCEL_SOURCES, etc.).

