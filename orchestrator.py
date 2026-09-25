import prep_data

def main():
    (cl_layers, combined_cls, corridor_layers, combined_corridors, 
     parcel_layers, road_layers, structure_layers, environmental_layers, 
     railroad_layers) = prep_data.prepare_datasets()

if __name__ == "__main__":
    main()