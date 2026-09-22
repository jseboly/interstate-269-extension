#Obtain data for linear infrastructure study and load into QGIS view
from qgis.core import *
import qgis.utils

#Configure GIS service urls to be imported here
SERVICE_URLS = [
    {
        "Name":"Arkansas Parcels",
        "Type":"arcgisfeatureserver",
        "URL":"https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Planning_Cadastre/FeatureServer/6"
    },
    {
        "Name":"Tennessee Parcels",
        "Type":"arcgismapserver",
        "URL":"https://scgis.shelbycountytn.gov/serverhigh/rest/services/Parcel/CERTParcel/MapServer/0"
    },
]

def add_service_layer_to_display(service):
    url = service["URL"]
    if service["Type"] == "arcgisfeatureserver":
        uri = f"crs='EPSG:3857' url='{url}'"
        feature_layer = QgsVectorLayer(uri, service["Name"], service["Type"])
        if feature_layer.isValid():
            QgsProject.instance().addMapLayer(feature_layer)
            print(f"Success: {service['Name']} added to display.")
            return feature_layer
        else:
            print(f"Error: {service['Name']} failed to load.")
    elif service["Type"] == "arcgismapserver":
        uri = f"crs='EPSG:3857' format='PNG32' url='{url}'"
        map_layer = QgsRasterLayer(uri, service["Name"], service["Type"])
        if map_layer.isValid():
            QgsProject.instance().addMapLayer(map_layer)
            print(f"Success: {service['Name']} added to display.")
            return map_layer
        else:
            print(f"Error: {service['Name']} failed to load.")
    

def main():
    print("Executing...")
    created_layers = []
    for service in SERVICE_URLS:
        layer_reference = add_service_layer_to_display(service)
        layer_info = {"Name":service['Name'], "Layer":layer_reference}
        created_layers.append(layer_info)
    print("Complete.")
    
main()
