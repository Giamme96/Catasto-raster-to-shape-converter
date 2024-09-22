import pandas as pd
import geopandas as gpd
import numpy as np

from shapely.geometry import box
import cv2
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, box

from wms_requests import GetImgFromWMS

def ScaleUpBox(df : pd.DataFrame) -> None:
    """
    Scale the coordinates according to the size of the bbox (so you can eliminate any nearby shapes using the bbox + threshold)

    :param df: Target df, column wise ops.
    """
    small_bbox_threshold: float = 0.00001
    scale_value_small: float = 0.00007
    scale_value_normal: float = 0.00003

    df["bbox_size"] = (df["max_lat"] - df["min_lat"]) * (df["max_lon"] - df["min_lon"])
    df["scale_value"] = np.where(df["bbox_size"] <= small_bbox_threshold, scale_value_small, scale_value_normal)

    df["min_lat_scaled"] = df["min_lat"] - df["scale_value"]
    df["min_lon_scaled"] = df["min_lon"] - df["scale_value"]
    df["max_lat_scaled"] = df["max_lat"] + df["scale_value"]
    df["max_lon_scaled"] = df["max_lon"] + df["scale_value"]

def ExtractShapeFromRaster(row, color_particella, color_fabbricato, lista_gdfs_extracted_shapes_in_bbox: list, input_crs: int) -> None:
    """
    Retrieve img from getmap and call extractor.

    :param color_particella: np.array with raster color of particella
    :param color_fabbricato: np.array with raster color of fabbricato
    :param lista_gdfs_extracted_shapes_in_bbox: list of shapes extracted from bbox
    :param input_crs: input crs used in wms request. List of available CRS is in GetCapabilites of Wms
    """
    img = GetImgFromWMS(row)
    AppendExtractedShapesFromRaster(row, img, color_particella, color_fabbricato, lista_gdfs_extracted_shapes_in_bbox, input_crs)

def AppendExtractedShapesFromRaster(row, img, color_particella, color_fabbricato, lista_gdfs_extracted_shapes_in_bbox: list, input_crs: int) -> None:
    """
    Transform, mask and extract shapes.
    Exclude partial shapes.

    :param color_particella: np.array with raster color of particella
    :param color_fabbricato: np.array with raster color of fabbricato
    :param lista_gdfs_extracted_shapes_in_bbox: list of shapes extracted from bbox
    :param input_crs: input crs used in wms request. List of available CRS is in GetCapabilites of Wms
    """

    # Create mask for 2 object colors
    mask_fabbricato = cv2.inRange(img, color_fabbricato, color_fabbricato)
    mask_particella = cv2.inRange(img, color_particella, color_particella)

    # Upload raster(img)
    with rasterio.MemoryFile() as temp_file:
        with temp_file.open(driver="PNG", width=2048, height=2048, count=3, dtype="uint8") as src:  #count=3 RGB band
            
            src.write(img.transpose(2,0,1)) # Traspose compliant with rasterio

            # Apply transform
            transform = rasterio.transform.from_bounds(row["min_lon_scaled"], row["min_lat_scaled"], row["max_lon_scaled"], row["max_lat_scaled"], 2048, 2048)

            # Extract shapes
            shapes_fabbricato = shapes(mask_fabbricato, mask=mask_fabbricato > 0, transform=transform)            
            shapes_particella = shapes(mask_particella, mask=mask_particella > 0, transform=transform)

            # Compute geometry and assign feature
            geoms_fabbricati = [{"properties": {"tipo": "Fabbricato"}, "geometry": shape(geom)} for geom, value in shapes_fabbricato]
            geoms_particelle = [{"properties": {"tipo": "Particella"}, "geometry": shape(geom)} for geom, value in shapes_particella]
            
            gdf = gpd.GeoDataFrame.from_features(geoms_fabbricati + geoms_particelle, crs=input_crs)

    ExcludeShapesOverlapBbox(row, gdf, lista_gdfs_extracted_shapes_in_bbox)
    
def ExcludeShapesOverlapBbox(row, gdf: gpd.GeoDataFrame, lista_gdfs_extracted_shapes_in_bbox: list):
    """
    Exclude shapes that overlap with bbox. We want only full shapes.

    :param gdf: Gdf with extracted shapes from img
    :param lista_gdfs_extracted_shapes_in_bbox: Target list for extracted and not excluded shapes
    """

    # Reduce scaled bbox
    bbox = box(row["min_lon_scaled"], row["min_lat_scaled"], row["max_lon_scaled"], row["max_lat_scaled"])
    bbox_distance_threshold: float = 0.00002

    bbox_restricted = bbox.buffer(-bbox_distance_threshold)

    # Filter geometries
    gdf = gdf[gdf.geometry.within(bbox_restricted)].reset_index(drop=True)
    
    lista_gdfs_extracted_shapes_in_bbox.append(gdf)

def ComputeAreaAndCentroid(gdf: gpd.GeoDataFrame, area_crs: int, output_crs: int) -> gpd.GeoDataFrame:
    """
    Calcola l'area e il centroide delle geometrie in un GeoDataFrame in un CRS proiettato, 
    quindi converte i centroidi e il GeoDataFrame in CRS 4326.

    :param gdf: GeoDataFrame di input con geometrie da processare.
    :param area_crs: EPSG code per il CRS proiettato usato per il calcolo dell'area.
    :param output_crs: EPSG code per il CRS di output (default 4326).
    :return: GeoDataFrame con area e coordinate del centroide.
    """
    
    # Reproject CRS
    gdf_reprojected = gdf.to_crs(area_crs)
    
    # Area and centroid
    gdf_reprojected["shape_area"] = gdf_reprojected.area
    gdf_reprojected["shape_centroid"] = gdf_reprojected.centroid
    
    # Reproject to output_crs
    gdf_reprojected = gdf_reprojected.to_crs(output_crs)
    gdf_reprojected["shape_centroid"] = gdf_reprojected["shape_centroid"].to_crs(output_crs)
    
    # Centroid coords in output_crs (not as a geometry point)
    gdf_reprojected["shape_centroid_lat"] = gdf_reprojected["shape_centroid"].y
    gdf_reprojected["shape_centroid_lon"] = gdf_reprojected["shape_centroid"].x
    
    return gdf_reprojected

def BufferGdf(gdf: gpd.GeoDataFrame, buffer_size: float):
    """
    Apply a buffer in geometry.

    :param buffer_size: Buffer size in CRS unit.
    """

    gdf["geometry"] = gdf["geometry"].buffer(buffer_size)
    return gdf

def SmoothShape(gdf: gpd.GeoDataFrame, tolerance: float) -> gpd.GeoDataFrame:
    """
    Simplify geometry.
    
    :param tolerance: smoothing value, in CRS unit, lower=detailed, higher=gross
    """

    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    return gdf