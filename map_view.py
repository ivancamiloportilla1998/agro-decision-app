import folium

def generar_mapa_interactivo(lat, lon, lugar, tipo_mapa, es_apto):
    """Construye y retorna el objeto Folium Map según el estilo seleccionado."""
    if tipo_mapa == "Satélite":
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=14, 
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
            attr='Esri'
        )
    elif tipo_mapa == "Topográfico":
        m = folium.Map(
            location=[lat, lon], 
            zoom_start=14, 
            tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 
            attr='OpenTopoMap'
        )
    else:
        m = folium.Map(location=[lat, lon], zoom_start=14, tiles='openstreetmap')
    
    color_m = "green" if es_apto else "red"
    folium.Marker([lat, lon], popup=lugar, icon=folium.Icon(color=color_m)).add_to(m)
    return m
