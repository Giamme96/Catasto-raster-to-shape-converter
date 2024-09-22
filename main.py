import pandas as pd
import geopandas as gpd
import numpy as np

from wms_requests import RequestFeatureOnPoint, InitializeWms, InitializeSession
from geo_operations import SmoothShape, ScaleUpBox, ExtractShapeFromRaster, ComputeAreaAndCentroid, BufferGdf
from io_services import CreateFolder, ExportPickle, ExportGDB, ExportShapefile, ExportExcel

# Paths
input_excel_path: str = r"input_bbox.xlsx"

output_excel: str = r"IO\output_excel"
output_shapefile: str = r"IO\output_shapefile"
output_pickle: str = r"IO\output_gdf"
output_gdb: str = r"IO\output_gdb"
lista_layer_to_export: list = ["Particelle", "Fabbricati"]


lista_features_response = []
lista_gdfs_extracted_shapes_in_bbox = []

color_particella = np.array([189, 236, 253])  # CP.CadastralParcel
color_fabbricato = np.array([19, 128, 236])  # Fabbricati

shape_area_threshold: int = 1 #in CRS unit
buffer_countour_size: float = 0.05 #in CRS unit
simplify_tolerance_size: float = 0.35 #in CRS unit

#CRS
input_crs: int = 6706
output_crs: int = 4326
area_crs: int = 6875

#Folder
CreateFolder()

#Network
InitializeWms()
InitializeSession()

#MAIN

df = pd.read_excel(input_excel_path,
                   usecols=["id", "cod_comune", "sezione", "foglio", "allegato", "sviluppo", "particella", "min_lat", "min_lon", "max_lat", "max_lon"],
                   dtype={"id" : str, "cod_comune" : str, "sezione" : str, "foglio" : str, "allegato" : str, "sviluppo" : str, "particella" : str, "min_lat" : float, "min_lon" : float, "max_lat" : float, "max_lon" : float}
                   )

df = df.head(10)
# Scale up bbox, to be safer with bbox exclusions
ScaleUpBox(df)

# Extract shapes from img
df.apply(ExtractShapeFromRaster, args=(color_particella, color_fabbricato, lista_gdfs_extracted_shapes_in_bbox, input_crs), axis=1)
df_extracted_shapes_in_bbox = pd.concat(lista_gdfs_extracted_shapes_in_bbox)

# Reproject shapes, 4326 is not good for 2d ops.
gdf_reprojected = ComputeAreaAndCentroid(df_extracted_shapes_in_bbox, area_crs, output_crs)

# Filter shapes above "shape_area_threshold" -> min sqm area observed is ~2mq (could be lower)
gdf_reprojected_filtered = gdf_reprojected[gdf_reprojected["shape_area"] > shape_area_threshold]
# Request features of each shape
gdf_reprojected_filtered.apply(RequestFeatureOnPoint, args=(lista_features_response, ), axis=1)
gdf_reprojected_filtered = gdf_reprojected_filtered.reset_index(drop=True)

# Geoportale issues, eg. C351 - sez A - 1 - 51 (37.54099, 15.12095)
lista_features_response_cleaned = [d if isinstance(d, dict) else {} for d in lista_features_response]

# From features to df
df_extracted_features_from_centroid = pd.DataFrame(lista_features_response_cleaned).astype({"SIGLA_PROV": str, "COD_COMUNE": str, "DENOM": str, "SEZIONE": str, "FOGLIO": str, "ALLEGATO": str, "SVILUPPO": str, "NUM_PART": str, "TIPOLOGIA": str}, errors="ignore")

gdf_reprojected_with_features = pd.concat([df_extracted_features_from_centroid, gdf_reprojected_filtered], axis=1)

df_merged = df.merge(gdf_reprojected_with_features, 
                        how="left", 
                        left_on=["cod_comune", "foglio", "particella"], 
                        right_on=["COD_COMUNE", "FOGLIO", "NUM_PART"]
                        )

# Smoothing and filtering
gdf_merged = gpd.GeoDataFrame(df_merged, geometry="geometry", crs=output_crs).to_crs(area_crs)
gdf_buffered = BufferGdf(gdf_merged, buffer_countour_size)
gdf_merged_smoothed = SmoothShape(gdf_buffered, simplify_tolerance_size)

gdf_union_particelle = gdf_merged_smoothed[gdf_merged_smoothed["tipo"] == "Particella"].dissolve(by=["COD_COMUNE", "SEZIONE", "FOGLIO", "ALLEGATO", "SVILUPPO", "NUM_PART", "tipo"], as_index=False, sort=False)
gdf_union_particelle_recalculated = ComputeAreaAndCentroid(gdf_union_particelle, area_crs, output_crs)
gdf_fabbricati = gdf_merged_smoothed[gdf_merged_smoothed["tipo"] == "Fabbricato"]

# Drop 2° geometry column x export
gdf_fabbricati.pop("shape_centroid")
gdf_union_particelle_recalculated.pop("shape_centroid")

# Export results
ExportPickle([gdf_union_particelle_recalculated, gdf_fabbricati], output_pickle, lista_layer_to_export)
# ExportGDB([gdf_union_particelle_recalculated, gdf_fabbricati], output_gdb, lista_layer_to_export)
ExportShapefile([gdf_union_particelle_recalculated, gdf_fabbricati], output_shapefile, lista_layer_to_export)
ExportExcel([gdf_union_particelle_recalculated, gdf_fabbricati], output_excel, output_crs)

print("End")
