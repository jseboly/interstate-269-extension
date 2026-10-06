from generate_corridors import main as generate_corridors
from analyze_parcels import main as analyze_parcels
from permit_analysis import main as analyze_permits
from environmental_analysis import main as analyze_env

def main():
    generate_corridors()
    analyze_parcels()
    analyze_permits()
    analyze_env()

if __name__ == "__main__":
    main()