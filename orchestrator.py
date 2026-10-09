import argparse
from generate_corridors import main as generate_corridors
from analyze_parcels import main as analyze_parcels
from permit_analysis import main as analyze_permits
from environmental_analysis import main as analyze_env
from structure_analysis import main as analyze_structures
from write_results import (
    collect_route_summaries,
    load_cache,
    main as write_results,
    save_cache,
)
import project_config as cfg


def main(write_results_only=True):
    if write_results_only:
        write_results(load_cache())
        return

    generate_corridors()
    for route in cfg.ROUTES_CONFIG:
        route.calculate_basic_metrics()
    analyze_parcels()
    analyze_permits()
    analyze_env()
    analyze_structures()
    summaries = collect_route_summaries(cfg.ROUTES_CONFIG)
    save_cache(summaries)
    write_results(summaries)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-results-only",
        action="store_true",
        help="Regenerate Results.md from the last saved analysis summary.",
    )
    args = parser.parse_args()
    main(write_results_only=args.write_results_only)