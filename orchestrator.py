from fileinput import filename
import project_config as cfg
from parcel_analysis import main as analyze_parcels
import generate_corridors

def main():
    generate_corridors()

if __name__ == "__main__":
    main()