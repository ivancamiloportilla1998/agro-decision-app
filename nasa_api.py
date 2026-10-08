import requests

def obtener_datos_nasa(lat, lon):
    """Consulta la API de NASA POWER para extraer temperatura media, mínima y precipitación."""
    try:
        url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR,T2M_MIN&community=AG&longitude={lon}&latitude={lat}&format=JSON"
        res = requests.get(url, timeout=10).json()
        
        props = res['properties']['parameter']
        temp_ann = props['T2M']['ANN']
        precip_ann = props['PRECTOTCORR']['ANN']
        temp_min_ann = props['T2M_MIN']['ANN']
        
        return {
            "temp_anual": temp_ann,
            "precip_anual": precip_ann,
            "temp_min_anual": temp_min_ann,
            "exito": True
        }
    except Exception as e:
        return {"exito": False, "error": str(e)}
