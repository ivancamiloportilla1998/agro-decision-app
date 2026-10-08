import requests

def obtener_suelo_soilgrids(lat, lon):
    """Consulta la API pública de SoilGrids (ISRIC) para obtener textura real del suelo."""
    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}&property=clay&property=sand&property=silt&depth=0-5cm&value=mean"
        res = requests.get(url, timeout=8).json()
        
        layers = res['properties']['layers']
        propiedades = {}
        for layer in layers:
            name = layer['name']
            # Valor medio a 0-5cm en g/kg convertidos a porcentaje (%)
            val = layer['depths'][0]['values']['mean'] / 10.0 
            propiedades[name] = val
        
        clay = propiedades.get('clay', 30)
        sand = propiedades.get('sand', 30)
        silt = propiedades.get('silt', 40)
        
        # Clasificación textural USDA
        if clay >= 40:
            tipo = "Arcilloso"
        elif sand >= 50:
            tipo = "Arenoso"
        else:
            tipo = "Franco"
            
        return {
            "tipo_suelo": tipo,
            "arcilla": round(clay, 1),
            "arena": round(sand, 1),
            "limo": round(silt, 1),
            "fuente": "SoilGrids (ISRIC Global API)"
        }
    except Exception:
        # Fallback en caso de que la API de suelos demore
        return {
            "tipo_suelo": "Franco",
            "arcilla": 30.0,
            "arena": 30.0,
            "limo": 40.0,
            "fuente": "Estimación Regional Estándar"
        }
