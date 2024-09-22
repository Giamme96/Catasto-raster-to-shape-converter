import os
import pickle
import pandas as pd

def CreateFolder() -> None:

    try:
        os.listdir("IO")
    except:
        os.mkdir("IO")

def ExportPickle(lista_gdf: list, output_pickle: str, lista_layer_to_export: list) -> None:

    for gdf, name in zip(lista_gdf, lista_layer_to_export):
        with open(f"{output_pickle}_{name}.pkl", "wb") as f:
            pickle.dump(gdf, f)
    print("Pickle: OK")

def ExportGDB(lista_gdf: list, output_gdb: str, lista_layer_to_export: list)  -> None:

    for gdf, name in zip(lista_gdf, lista_layer_to_export):
        gdf.to_file(f"{output_gdb}_{name}.gdb", layer=name, driver="FileGDB")
    print("GDB: OK")

def ExportShapefile(lista_gdf: list, output_shapefile: str, lista_layer_to_export: list) -> None:

    for gdf, name in zip(lista_gdf, lista_layer_to_export):
        gdf.to_file(f"{output_shapefile}_{name}.shp")
    print("Shapefile: OK")

def ExportExcel(lista_gdf: list, output_excel: str, output_crs: int) -> None:

    df_merged = pd.concat([lista_gdf[0].to_crs(output_crs), lista_gdf[1].to_crs(output_crs)], ignore_index=True)
    df_merged.to_excel(f"{output_excel}.xlsx", sheet_name="Fabbricati_e_particelle" ,index=False)
    print("Excel: OK")