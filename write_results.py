import json
import math
from pathlib import Path

import pandas as pd

import project_config as cfg


FEET_PER_MILE = 5280
SQUARE_FEET_PER_ACRE = 43560


def _owner_type_counts(line_list):
    """Count parcels and distinct owner names for each owner type."""
    if line_list is None:
        return None

    owner_types = (
        line_list["OwnerType"]
        if "OwnerType" in line_list.columns
        else ["not_classified"] * len(line_list)
    )
    owners = (
        line_list["Owner"]
        if "Owner" in line_list.columns
        else [None] * len(line_list)
    )
    counts = {}
    for owner_type, owner in zip(owner_types, owners):
        category = (
            "not_classified"
            if pd.isna(owner_type) or not str(owner_type).strip()
            else str(owner_type).strip()
        )
        category_counts = counts.setdefault(
            category, {"landowners": set(), "parcels": 0}
        )
        category_counts["parcels"] += 1
        if not pd.isna(owner) and str(owner).strip():
            category_counts["landowners"].add(str(owner).strip().casefold())

    all_landowners = set().union(
        *(category_counts["landowners"] for category_counts in counts.values())
    )
    return {
        "total_landowners": len(all_landowners),
        "by_type": {
            category: {
                "landowners": len(category_counts["landowners"]),
                "parcels": category_counts["parcels"],
            }
            for category, category_counts in counts.items()
        },
    }


def collect_route_summaries(routes):
    """Collect the lightweight metrics needed to render the route summary."""
    summaries = []
    for route in routes:
        parcel_count = (
            len(route.line_list) if route.line_list is not None else None
        )
        owner_type_counts = _owner_type_counts(route.line_list)
        permit_crossing_count = (
            sum(len(crossings) for crossings in route.permits.values())
            if route.permits is not None and (
                route.permits or not cfg.PERMIT_SOURCES
            )
            else None
        )
        permit_type_counts = (
            {
                permit_type: len(crossings)
                for permit_type, crossings in route.permits.items()
            }
            if route.permits is not None
            else None
        )
        environmental_type_counts = (
            {
                feature_type: len(features)
                for feature_type, features in route.env_constraints.items()
            }
            if route.env_constraints is not None and (
                route.env_constraints or not cfg.ENVIRONMENTAL_SOURCES
            )
            else None
        )
        summaries.append({
            "name": route.name,
            "total_length": (
                float(route.total_length)
                if route.total_length is not None
                else None
            ),
            "total_area": (
                float(route.total_area) if route.total_area is not None else None
            ),
            "parcel_count": parcel_count,
            "permit_crossing_count": permit_crossing_count,
            "owner_type_counts": owner_type_counts,
            "landowner_count": (
                owner_type_counts["total_landowners"]
                if owner_type_counts is not None
                else None
            ),
            "permit_type_counts": permit_type_counts,
            "environmental_type_counts": environmental_type_counts,
            "structure_count": (
                len(route.structures)
                if route.structures is not None
                else None
            ),
        })
    return summaries


def save_cache(summaries):
    """Persist completed route summary inputs for writer-only iterations."""
    cache_path = Path(cfg.RESULTS_CACHE_FILE)
    temporary_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(summaries, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    temporary_path.replace(cache_path)
    print(f"Analysis summary cache written to {cache_path}")


def load_cache():
    """Load cached route summary inputs, reporting missing or invalid caches."""
    cache_path = Path(cfg.RESULTS_CACHE_FILE)
    try:
        summaries = json.loads(cache_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"No analysis summary cache found at {cache_path}. "
            "Run orchestrator.py once without --write-results-only first."
        ) from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Analysis summary cache at {cache_path} is not valid JSON."
        ) from error

    required_fields = {
        "name",
        "total_length",
        "total_area",
        "parcel_count",
        "permit_crossing_count",
    }
    if not isinstance(summaries, list) or any(
        not isinstance(summary, dict)
        or not required_fields.issubset(summary)
        for summary in summaries
    ):
        raise ValueError(
            f"Analysis summary cache at {cache_path} has an invalid format."
        )
    return summaries


def _format_measurement(value, divisor=1):
    """Format a numeric measurement, or label it when analysis has not run."""
    if value is None:
        return "Not available"

    try:
        measurement = float(value) / divisor
    except (TypeError, ValueError, OverflowError):
        return "Not available"

    if not math.isfinite(measurement):
        return "Not available"
    return f"{measurement:,.2f}"


def _format_count(value):
    return f"{value:,}" if value is not None else "Not available"


def _format_owner_type(owner_type):
    if pd.isna(owner_type):
        return "Not Classified"
    return str(owner_type).replace("_", " ").title()


def _markdown_cell(value):
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def _markdown_table(data, columns, empty_message):
    if data is None:
        return "Not available."
    if data.empty:
        return empty_message

    available_columns = [
        (column, label)
        for column, label in columns
        if column in data.columns
    ]
    if not available_columns:
        return "No reportable fields available."

    headers = [label for _, label in available_columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, record in data.iterrows():
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(record[column])
                for column, _ in available_columns
            )
            + " |"
        )
    return "\n".join(lines)


def _combine_layer_records(layer_data):
    records = []
    for feature_type, data in (layer_data or {}).items():
        if data is None:
            continue
        for _, record in data.iterrows():
            records.append({
                "Type": feature_type,
                **record.to_dict(),
            })
    return pd.DataFrame(records)


def _route_detail_sections(route):
    parcel_data = route.line_list
    if parcel_data is not None and "OwnerType" in parcel_data.columns:
        parcel_data = parcel_data.copy()
        parcel_data["OwnerType"] = parcel_data["OwnerType"].map(
            _format_owner_type
        )

    parcel_columns = (
        ("ParcelID", "Parcel ID"),
        ("Owner", "Owner"),
        ("OwnerType", "Owner type"),
        ("entry_distance", "Entry milepost"),
        ("exit_distance", "Exit milepost"),
        ("feet_crossed", "Length crossed (ft)"),
        ("parcel_area_acres", "Parcel area (acres)"),
        ("corridor_area_acres", "Corridor area (acres)"),
    )
    sections = [
        f"## {route.name} Details\n",
        "### Parcel Line List\n",
        _markdown_table(
            parcel_data,
            parcel_columns,
            "No parcels found.",
        ),
        "\n",
        "### Permit Crossing List\n",
    ]

    permits = _combine_layer_records(route.permits)
    sections.append(_markdown_table(
        permits if route.permits is not None else None,
        (
            ("Type", "Type"),
            ("UniqueID", "ID"),
            ("Name", "Name"),
            ("Measure", "Milepost"),
        ),
        "No permit crossings found.",
    ))
    sections.extend(("\n", "### Environmental constraints\n"))
    environmental = _combine_layer_records(route.env_constraints)
    sections.append(_markdown_table(
        environmental if route.env_constraints is not None else None,
        (
            ("Type", "Type"),
            ("UniqueID", "ID"),
            ("Name", "Name"),
            ("start_meas", "Start milepost"),
            ("end_meas", "End milepost"),
            ("length_feet", "Length affected (ft)"),
            ("area_acres", "Area affected (acres)"),
        ),
        "No environmental constraints found.",
    ))

    sections.extend(("\n", "### Structures\n"))
    structure_columns = []
    structure_source = cfg.STRUCTURES_SOURCE
    structure_name_field = structure_source.name_field
    structure_id_field = structure_source.id_field
    if route.structures is not None:
        structure_columns.append((structure_id_field, "ID"))
        if structure_name_field:
            structure_columns.append(
                (structure_name_field, "Type")
            )
        name_column = next(
            (
                column for column in route.structures.columns
                if str(column).casefold() == "name"
            ),
            None,
        )
        if name_column is not None and name_column != structure_name_field:
            structure_columns.append((name_column, "Name"))
    sections.append(_markdown_table(
        route.structures,
        structure_columns,
        "No structures found.",
    ))
    sections.append("\n")
    return "\n".join(sections)


def _summary_table(summaries):
    route_headers = "".join(f" {summary['name']} |" for summary in summaries)
    header = f"| Metric |{route_headers}"
    divider = f"|:--|{'|'.join('--:' for _ in summaries)}|"
    metrics = (
        (
            "Total length (mi)",
            "total_length",
            lambda value: _format_measurement(value, FEET_PER_MILE),
        ),
        (
            "Total area (acres)",
            "total_area",
            lambda value: _format_measurement(value, SQUARE_FEET_PER_ACRE),
        ),
    )
    rows = [
        f"| **{label}** |"
        + "".join(f" **{formatter(summary[key])}** |" for summary in summaries)
        for label, key, formatter in metrics
    ]

    owner_types = sorted(
        {
            owner_type
            for summary in summaries
            for owner_type in (
                (summary.get("owner_type_counts") or {}).get("by_type", {})
            )
        },
        key=str.casefold,
    )
    rows.append(
        "| **Landowners by type** |"
        + "".join(
            f" **{_format_count(summary.get('landowner_count'))}** |"
            for summary in summaries
        )
    )
    for owner_type in owner_types:
        label = _format_owner_type(owner_type)
        rows.append(
            f"| {label} |"
            + "".join(
                " Not available |"
                if summary.get("owner_type_counts") is None
                else (
                    f" {summary.get('owner_type_counts', {}).get('by_type', {}).get(owner_type, {}).get('landowners', 0):,} |"
                )
                for summary in summaries
            )
        )

    rows.append(
        "| **Parcels by type** |"
        + "".join(
            f" **{_format_count(summary.get('parcel_count'))}** |" 
            for summary in summaries)
    )
    for owner_type in owner_types:
        label = _format_owner_type(owner_type)
        rows.append(
            f"| {label} |"
            + "".join(
                " Not available |"
                if summary.get("owner_type_counts") is None
                else (
                    f" {summary.get('owner_type_counts', {}).get('by_type', {}).get(owner_type, {}).get('parcels', 0):,} |"
                )
                for summary in summaries
            )
        )

    permit_types = [
        source.description or source.name for source in cfg.PERMIT_SOURCES
    ]
    rows.append(
        "| **Permits by type** |"
        + "".join(
            f" **{_format_count(summary.get('permit_crossing_count'))}** |"
            for summary in summaries
        )
    )
    for permit_type in permit_types:
        rows.append(
            f"| {permit_type} |"
            + "".join(
                " Not available |"
                if summary.get("permit_type_counts") is None
                or permit_type not in summary.get("permit_type_counts", {})
                else f" {summary['permit_type_counts'][permit_type]:,} |"
                for summary in summaries
            )
        )

    environmental_types = list(dict.fromkeys(
        feature_type
        for summary in summaries
        for feature_type in (summary.get("environmental_type_counts") or {})
    ))
    if environmental_types:
        rows.append("| **Environmental features by type** |" + "".join(" |" for _ in summaries))
        for feature_type in environmental_types:
            rows.append(
                f"| {feature_type} |"
                + "".join(
                    " Not available |"
                    if summary.get("environmental_type_counts") is None
                    or feature_type not in summary.get("environmental_type_counts", {})
                    else (
                        f" {summary['environmental_type_counts'][feature_type]:,} |"
                    )
                    for summary in summaries
                )
            )

    rows.append(
        "| Structure count |"
        + "".join(
            f" {_format_count(summary.get('structure_count'))} |"
            for summary in summaries
        )
    )

    return "\n".join((header, divider, *rows))

def generate_executive_summary():
    """Generate the executive summary section."""
    routes = cfg.ROUTES_CONFIG
    summaries = collect_route_summaries(routes)
    table = _summary_table(summaries)
    results = (
        "# Analysis Results\n\n"
        "## Executive Summary\n\n"
        "Comparison of summary metrics across route alternatives.\n\n"
        f"{table}\n\n"
        + "\n".join(_route_detail_sections(route) for route in routes)
    )
    Path(cfg.RESULTS_FILE).write_text(results, encoding="utf-8")
    print(f"Route summary written to {cfg.RESULTS_FILE}")


def main():
    """Write results to the configured file."""
    generate_executive_summary()