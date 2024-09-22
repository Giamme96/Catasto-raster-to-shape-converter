import requests
import numpy as np
import cv2
from PIL import Image
import io
from owslib.wms import WebMapService

wms = None

def InitializeWms() -> None:
    """
    Initialize target Wms.
    """
    global wms

    wms = WebMapService("https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?", version="1.3.0")
    
def GetImgFromWMS(row):
    """
    Retrieve map (img) from Wms.
    """
    global wms

    print("Feature: ", row["id"])
    try:
        img =  wms.getmap(layers=["CP.CadastralParcel", "fabbricati"],
                          srs="EPSG:6706",
                          bbox=(row["min_lat_scaled"], row["min_lon_scaled"], row["max_lat_scaled"], row["max_lon_scaled"]),
                          size=(2048, 2048),
                          format="image/png",
                          transparent=True
                          )
        img_data = img.read()
        img_pil = Image.open(io.BytesIO(img_data))
        img_cv2 = np.array(img_pil)
        img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_RGB2BGR)
        return img_cv2
    except Exception as e:
        raise ValueError(f"Errore nella chiamata al WMS: {e}")

def GetRequest(row):
    """
    Request features on Point from Ade.
    """
    global session

    try:
        response = session.get(f'https://wms.cartografia.agenziaentrate.gov.it/inspire/ajax/ajax.php?op=getDatiOggetto&lon={row["shape_centroid"].x}&lat={row["shape_centroid"].y}')

        if response.status_code == 200:
            if response.json() == "ERRX-2":
                print(f"Servizio down: {e}")
            else:
                print("Get - OK")
                return response.json()
        elif response.status_code == 500:
            print("SLM - KO")
            InitializeSession()
            return GetRequest(row)

    except Exception as e:
        print(f"Errore nella richiesta di Feature: {e}")
        return None

def InitializeSession() -> None:
    """
    Initialize session.
    """
    global session
    session = requests.Session()

def RequestFeatureOnPoint(row, lista_features_response: list) -> None:
    """
    Handle responses from GetRequest

    :param lista_features_response: Target list for responses.
    """
    global session

    response = GetRequest(row)

    if (response != None) & (response != "ERRX-2"):

        lista_features_response.append(response)
