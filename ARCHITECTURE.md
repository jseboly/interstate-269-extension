# Project architecture

The project is a sequential, in-process GIS analysis pipeline. `orchestrator.py`
coordinates the workflow; configured route and layer objects carry source
metadata and analysis results between stages.

```mermaid
flowchart TD
    subgraph Inputs["Inputs and configuration"]
        Config["project_config.py<br/>CRS, bbox, ROW width,<br/>routes and source layers"]
        RouteData["ProposedRoutes.gdb<br/>North and South centerlines"]
        LocalParcels["ShelbyCountyParcels.shp<br/>local parcel data"]
        RemoteGIS["ArcGIS Feature Services<br/>Arkansas parcels, roads/rail,<br/>environment, structures"]
    end

    subgraph Pipeline["orchestrator.py — sequential workflow"]
        Start["generate_corridors.py"]
        Metrics["ProjectRoute.calculate_basic_metrics()<br/>length and corridor area"]
        Parcels["analyze_parcels.py<br/>merge parcels, measure impacts,<br/>optionally classify owners"]
        Permits["permit_analysis.py<br/>transportation crossings"]
        Environment["environmental_analysis.py<br/>environmental intersections"]
        Structures["structure_analysis.py<br/>structures within corridor"]

        Start --> Metrics --> Parcels --> Permits --> Environment --> Structures
    end

    subgraph Shared["Shared code"]
        Models["models.py<br/>GISLayer loads/unloads data;<br/>ProjectRoute stores route data/results"]
        Utils["utils.py<br/>geometry and string helpers"]
    end

    subgraph Outputs["Runtime state and persisted files"]
        CorridorStore["ProjectCorridors.gdb<br/>buffered corridor feature classes"]
        OwnerCache["owner_classification_cache.json<br/>optional owner classification cache"]
        Memory["Analysis results held on ProjectRoute<br/>line_list, permits, env_constraints,<br/>structures, total_length, total_area"]
        Report["analysis_results.md<br/>configured as RESULTS_FILE;<br/>not currently written by the pipeline"]
    end

    Config --> Start
    Config --> Metrics
    Config --> Parcels
    Config --> Permits
    Config --> Environment
    Config --> Structures
    RouteData --> Start
    RouteData --> Metrics
    RouteData --> Parcels
    RouteData --> Permits
    RouteData --> Environment
    LocalParcels --> Parcels
    RemoteGIS --> Parcels
    RemoteGIS --> Permits
    RemoteGIS --> Environment
    RemoteGIS --> Structures

    Models -. used by .-> Start
    Models -. used by .-> Config
    Utils -. used by .-> Start
    Utils -. used by .-> Parcels
    Utils -. used by .-> Permits
    Utils -. used by .-> Environment

    Start --> CorridorStore
    Start -->|attaches corridor layer| Memory
    Metrics --> Memory
    Parcels --> Memory
    Parcels -. optional read/write .-> OwnerCache
    Permits --> Memory
    Environment --> Memory
    Structures --> Memory
```

## Runtime sequence

The orchestrator runs each analysis stage in order across the configured
routes: it generates and persists right-of-way buffers, calculates basic
metrics, then runs parcel, permit, environmental, and structure analyses. The
analyses load GIS layers through `GISLayer`, process spatial data with
GeoPandas/Shapely, and store their results on each mutable `ProjectRoute`
instance.

Owner classification is optional: when configured with an API key and the
OpenAI SDK, parcel analysis classifies unique owner names and caches results
locally. The cache can contain personal owner names.

The configured `RESULTS_FILE` is not currently consumed by the pipeline.
Aside from corridor feature classes and the optional owner cache, results are
not persisted after the Python process exits.
