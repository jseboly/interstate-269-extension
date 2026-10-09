import json
import math
from pathlib import Path

import project_config as cfg


FEET_PER_MILE = 5280
SQUARE_FEET_PER_ACRE = 43560


def collect_route_summaries(routes):
    """Collect the lightweight metrics needed to render the route summary."""
    summaries = []
    for route in routes:
        parcel_count = (
            len(route.line_list) if route.line_list is not None else None
        )
        permit_crossing_count = (
            sum(len(crossings) for crossings in route.permits.values())
            if route.permits is not None and (
                route.permits or not cfg.PERMIT_SOURCES
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


def _route_summary(summary):
    return (
        f"| {summary['name']} "
        f"| {_format_measurement(summary['total_length'], FEET_PER_MILE)} "
        f"| {_format_measurement(summary['total_area'], SQUARE_FEET_PER_ACRE)} "
        f"| {_format_count(summary['parcel_count'])} "
        f"| {_format_count(summary['permit_crossing_count'])} |"
    )


def main(summaries=None):
    """Write a compact comparison of route metrics to the configured results file."""
    if summaries is None:
        summaries = collect_route_summaries(cfg.ROUTES_CONFIG)
    table_rows = "\n".join(_route_summary(summary) for summary in summaries)
    results = (
        "# Analysis Results\n\n"
        "## Executive Summary\n\n"
        "Comparison of the route alternatives based on the completed GIS analysis.\n\n"
        "| Route | Total length (mi) | Total area (acres) | Parcel count | "
        "Permit crossing count |\n"
        "|:--|--:|--:|--:|--:|\n"
        f"{table_rows}\n\n"
        "Length is the summed centerline length; area is the summed corridor "
        "polygon area. Parcel count is the number of records in each route's "
        "parcel line list. Permit crossing count is the total of recorded "
        "crossings across all configured permit layers.\n"
    )
    Path(cfg.RESULTS_FILE).write_text(results, encoding="utf-8")
    print(f"Route summary written to {cfg.RESULTS_FILE}")