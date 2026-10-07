from generate_corridors import main as generate_corridors
from analyze_parcels import main as analyze_parcels
from permit_analysis import main as analyze_permits
from environmental_analysis import main as analyze_env
from structure_analysis import main as analyze_structures
import project_config as cfg

def main():
    generate_corridors()
    for route in cfg.ROUTES_CONFIG:
        route.calculate_basic_metrics()
    analyze_parcels()
    analyze_permits()
    analyze_env()
    analyze_structures()
    # write_results()

if __name__ == "__main__":
    main()