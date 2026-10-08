import requests

def validar_terreno(lat, lon):
    """Valida si el punto geográfico es apto para agricultura (filtra agua y ciudades densas)."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
        headers = {'User-Agent': 'AgroDecisionApp_Geo/17.0'} 
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return "Terreno agrícola", True, ""
            
        res = response.json()
        if lat < -60 or lat > 80: 
            return "Zona Polar / Inviable", False, "Latitud extrema no apta para agricultura."
        if 'error' in res:
            return "Ubicación en alta mar o remota", False, "No se detecta superficie terrestre."
            
        if 'class' in res:
            clase = res['class']
            tipo = res.get('type', '')
            if clase in ['water', 'waterway'] or tipo in ['ocean', 'sea', 'water', 'bay', 'strait', 'reef']:
                return "Cuerpo de agua / Océano", False, "No se puede realizar agricultura en el mar o cuerpos de agua."
            if clase in ['highway', 'building', 'railway'] and tipo not in ['track', 'path']:
                return "Zona urbana / Infraestructura vial", False, "Infraestructura construida, no apta para siembra."

        if 'display_name' in res:
            partes = res['display_name'].split(',')
            nombre = f"{partes[0].strip()}, {partes[min(1, len(partes)-1)].strip()}"
            return nombre, True, ""
            
        return "Terreno abierto", True, ""
    except Exception:
        return f"Lat: {lat:.4f}, Lon: {lon:.4f}", True, ""

def buscar_sugerencias(query):
    """Busca sugerencias en tiempo real priorizando Colombia."""
    try:
        if not query or len(query.strip()) < 3:
            return {}
        # Búsqueda optimizada priorizando Colombia
        url = f"https://nominatim.openstreetmap.org/search?q={query},+Colombia&format=json&limit=5"
        headers = {'User-Agent': 'AgroApp_Autocomplete/2.0'}
        res = requests.get(url, headers=headers, timeout=5).json()
        
        if res and isinstance(res, list):
            return {item['display_name']: (float(item['lat']), float(item['lon'])) for item in res if 'lat' in item and 'lon' in item}
        return {}
    except Exception:
        return {}
