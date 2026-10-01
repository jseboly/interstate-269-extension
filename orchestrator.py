from generate_corridors import main as generate_corridors
from analyze_parcels import main as analyze_parcels
from permit_analysis import main as analyze_permits

def main():
    generate_corridors()
    analyze_parcels()
    analyze_permits()

if __name__ == "__main__":
    main()