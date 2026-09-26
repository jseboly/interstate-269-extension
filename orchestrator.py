from fileinput import filename
import project_config as cfg
import prep_data
from parcel_analysis import main as analyze_parcels

def main():
    cl_layers, combined_cls = prep_data.prepare_centerlines()
    corridor_layers, combined_corridors = prep_data.prepare_corridors(cl_layers)
    with open(cfg.RESULTS_FILE, "w") as file:
        analyze_parcels(file, cl_layers, corridor_layers, combined_corridors)

if __name__ == "__main__":
    main()