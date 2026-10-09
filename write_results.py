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
    return owner_type.replace("_", " ").capitalize()


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

    return "\n".join((header, divider, *rows))

def generate_executive_summary():
    """Generate the executive summary section."""
    summaries = collect_route_summaries(cfg.ROUTES_CONFIG)
    table = _summary_table(summaries)
    results = (
        "# Analysis Results\n\n"
        "## Executive Summary\n\n"
        "Comparison of summary metrics across route alternatives.\n\n"
        f"{table}\n\n"
    )
    Path(cfg.RESULTS_FILE).write_text(results, encoding="utf-8")
    print(f"Route summary written to {cfg.RESULTS_FILE}")


def main():
    """Write results to the configured file."""
    generate_executive_summary()