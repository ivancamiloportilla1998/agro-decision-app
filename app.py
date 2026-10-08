import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Gestión de Cultivos", page_icon="", layout="wide")

# --- FUNCIÓN PARA CARGAR EL ARCHIVO CSS EXTERNO ---
def cargar_css(nombre_archivo):
    try:
        with open(nombre_archivo) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Si el archivo aún no se crea, la app sigue funcionando normal

cargar_css("style.css")

st.title(" Sistema de Decisión: Rotación de Cultivos")
st.markdown("**Desafío:** Inteligencia geoespacial, pisos térmicos y selección de capas cartográficas para análisis agrícola.")

# --- 1. ESTADO DE LA APLICACIÓN ---
if 'lat' not in st.session_state:
    st.session_state['lat'] = 0.8243
if 'lon' not in st.session_state:
    st.session_state['lon'] = -77.6377
if 'lugar' not in st.session_state:
    st.session_state['lugar'] = "Ipiales, Nariño"
if 'es_apto' not in st.session_state:
    st.session_state['es_apto'] = True
if 'razon_no_apto' not in st.session_state:
    st.session_state['razon_no_apto'] = ""

# --- 2. VALIDACIÓN DE APTITUD DE SUELO Y AGUA ---
def validar_terreno(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
        headers = {'User-Agent': 'AgroDecisionApp_Precision/12.0'} 
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return "Zona de análisis", True, ""
            
        res = response.json()
        
        if lat < -60 or lat > 80: 
            return "Zona Polar / Inviable", False, "Latitud extrema no apta para agricultura."
            
        if 'error' in res:
            return "Ubicación en alta mar o remota", False, "No se detecta superficie terrestre (Océano o masa de agua)."
            
        if 'class' in res:
            clase = res['class']
            tipo = res.get('type', '')
            
            if clase in ['water', 'waterway'] or tipo in ['ocean', 'sea', 'water', 'bay', 'strait', 'reef']:
                return "Cuerpo de agua / Océano", False, "No se puede realizar agricultura en el mar o cuerpos de agua."
            
            if clase in ['highway', 'building', 'railway'] and tipo not in ['track', 'path']:
                return "Zona urbana / Infraestructura vial", False, "Infraestructura construida, no apta para siembra."

        if 'display_name' in res:
            partes = res['display_name'].split(',')
            nombre_lugar = f"{partes[0].strip()}, {partes[min(1, len(partes)-1)].strip()}"
            return nombre_lugar, True, ""
            
        return "Terreno abierto", True, ""
        
    except Exception:
        return "Terreno rural", True, ""

# --- 3. BARRA LATERAL ---
st.sidebar.header("📍 Ubicación del Terreno")

st.sidebar.subheader("🛰️ Ubicación Actual (GPS)")
st.sidebar.write("Haz clic para detectar tu posición exacta:")
location = streamlit_geolocation()

if location.get('latitude') and location.get('longitude'):
    gps_lat = location['latitude']
    gps_lon = location['longitude']
    if gps_lat != st.session_state['lat'] or gps_lon != st.session_state['lon']:
        nombre, apto, razon = validar_terreno(gps_lat, gps_lon)
        st.session_state['lat'] = gps_lat
        st.session_state['lon'] = gps_lon
        st.session_state['lugar'] = nombre
        st.session_state['es_apto'] = apto
        st.session_state['razon_no_apto'] = razon
        st.rerun()

st.sidebar.markdown("---")
metodo = st.sidebar.radio("Otras opciones de búsqueda:",
                          ["👆 Clic en el mapa", "🔍 Escribir el nombre", "📍 Ingresar coordenadas"])

if metodo == "🔍 Escribir el nombre":
    nuevo_lugar = st.sidebar.text_input("Lugar (Ej: Pupiales, Nariño):", value=st.session_state['lugar'])
    if st.sidebar.button("Buscar"):
        try:
            url_geo = f"https://nominatim.openstreetmap.org/search?q={nuevo_lugar}&format=json&limit=1"
            res = requests.get(url_geo, headers={'User-Agent': 'AgroApp/1.0'}).json()
            if res:
                nueva_lat = float(res[0]['lat'])
                nueva_lon = float(res[0]['lon'])
                nombre, apto, razon = validar_terreno(nueva_lat, nueva_lon)
                st.session_state['lat'] = nueva_lat
                st.session_state['lon'] = nueva_lon
                st.session_state['lugar'] = nuevo_lugar
                st.session_state['es_apto'] = apto
                st.session_state['razon_no_apto'] = razon
                st.rerun()
            else:
                st.sidebar.error("Lugar no encontrado.")
        except:
            st.sidebar.error("Error al buscar.")

elif metodo == "📍 Ingresar coordenadas":
    nueva_lat = st.sidebar.number_input("Latitud:", value=float(st.session_state['lat']), format="%.6f")
    nueva_lon = st.sidebar.number_input("Longitud:", value=float(st.session_state['lon']), format="%.6f")
    if st.sidebar.button("Actualizar Mapa"):
        nombre, apto, razon = validar_terreno(nueva_lat, nueva_lon)
        st.session_state['lat'] = nueva_lat
        st.session_state['lon'] = nueva_lon
        st.session_state['lugar'] = nombre
        st.session_state['es_apto'] = apto
        st.session_state['razon_no_apto'] = razon
        st.rerun()

else: # 👆 Clic en el mapa
    st.sidebar.info("Haz clic sobre tu lote o terreno agrícola en el mapa.")
    st.sidebar.markdown("### 📌 Punto Seleccionado:")
    
    if st.session_state.get('es_apto', True):
        st.sidebar.success(f"**Lugar:** {st.session_state['lugar']}")
    else:
        st.sidebar.error(f"⛔ **Zona No Apta:** \n{st.session_state['lugar']}\n\n*{st.session_state['razon_no_apto']}*")
        
    st.sidebar.warning(f"**Latitud:** {st.session_state['lat']:.4f} \n\n**Longitud:** {st.session_state['lon']:.4f}")

# --- 4. SELECTOR DE TIPO DE MAPA ---
st.sidebar.markdown("---")
st.sidebar.header("🗺️ Estilo de Capa Cartográfica")
tipo_mapa = st.sidebar.selectbox(
    "Selecciona el tipo de mapa:",
    [
        "Satélite (Alta Resolución)",
        "Topográfico y Relieve (Curvas de Nivel)",
        "Político y Vial (Calles y Límites)"
    ]
)

LAT = st.session_state['lat']
LON = st.session_state['lon']

# --- 5. INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1.2, 1])

with col2:
    st.subheader(f"Mapa Interactivo ({tipo_mapa})")
    st.caption("Cambia el tipo de capa en la barra lateral según lo que necesites analizar.")
    
    if tipo_mapa == "Satélite (Alta Resolución)":
        m = folium.Map(
            location=[LAT, LON], 
            zoom_start=14,
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri &mdash; Source: Esri, i-cubed, USDA, USGS'
        )
    elif tipo_mapa == "Topográfico y Relieve (Curvas de Nivel)":
        m = folium.Map(
            location=[LAT, LON], 
            zoom_start=14,
            tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            attr='OpenTopoMap (CC-BY-SA)'
        )
    else:
        m = folium.Map(location=[LAT, LON], zoom_start=14, tiles='openstreetmap')
    
    color_marcador = "green" if st.session_state.get('es_apto', True) else "red"
    icono_marc = "leaf" if st.session_state.get('es_apto', True) else "ban"
    
    folium.Marker([LAT, LON], popup=st.session_state['lugar'], icon=folium.Icon(color=color_marcador, icon=icono_marc)).add_to(m)
    
    mapa_datos = st_folium(m, width=500, height=450, key="mapa_dinamico")
    
    if mapa_datos and mapa_datos.get("last_clicked"):
        clic_lat = mapa_datos["last_clicked"]["lat"]
        clic_lon = mapa_datos["last_clicked"]["lng"]
        
        if abs(clic_lat - LAT) > 0.0001 or abs(clic_lon - LON) > 0.0001:
            nombre, apto, razon = validar_terreno(clic_lat, clic_lon)
            st.session_state['lat'] = clic_lat
            st.session_state['lon'] = clic_lon
            st.session_state['lugar'] = nombre
            st.session_state['es_apto'] = apto
            st.session_state['razon_no_apto'] = razon
            st.rerun()

with col1:
    st.subheader("Parámetros y Análisis")
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        tipo_suelo = st.selectbox("Tipo de Suelo", ["Arcilloso", "Franco", "Arenoso"])
    with col_input2:
        prioridad = st.selectbox("Prioridad", 
                                 ["Conservar agua (Resiliencia hídrica)", 
                                  "Mejorar salud (Fijar Nitrógeno)", 
                                  "Maximizar rentabilidad"])
    
    st.subheader("Observaciones Satelitales (NASA)")
    
    if not st.session_state.get('es_apto', True):
        st.error(f"⚠️ **ANÁLISIS BLOQUEADO:** {st.session_state['razon_no_apto']} Por favor, selecciona un terreno firme con potencial agrícola en el mapa.")
    else:
        if st.button("Consultar NASA POWER y Generar Rotación"):
            with st.spinner(f"Extrayendo temperatura y clima de la NASA para las coordenadas ({LAT:.4f}, {LON:.4f})..."):
                try:
                    url_nasa = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR&community=AG&longitude={LON}&latitude={LAT}&format=JSON"
                    nasa_req = requests.get(url_nasa).json()
                    
                    temp_historica = nasa_req['properties']['parameter']['T2M']['ANN']
                    precip_historica = nasa_req['properties']['parameter']['PRECTOTCORR']['ANN']
                    
                    if temp_historica >= 24:
                        piso_termico = "Cálido (> 24 °C - Tierras bajas tropicales)"
                        if "Conservar agua" in prioridad:
                            rotacion = "Sorgo ➔ Yuca ➔ Fríjol caupí de secano"
                            justificacion = "Cultivos tolerantes a altas tasas de evapotranspiración en zonas cálidas."
                        elif "Nitrógeno" in prioridad:
                            rotacion = "Maíz tropical ➔ Fríjol zaragoza ➔ Abono verde (Crotalaria)"
                            justificacion = "Leguminosas tropicales fijan nitrógeno rápidamente bajo alta radiación solar."
                        else:
                            rotacion = "Plátano ➔ Cítricos ➔ Papaya / Frutales comerciales"
                            justificacion = "Rentabilidad comercial adaptada al trópico bajo."
                            
                    elif 18 <= temp_historica < 24:
                        piso_termico = "Templado / Medio (18 °C - 24 °C - Eje Cafetero / Piedemonte)"
                        if "Conservar agua" in prioridad:
                            rotacion = "Maíz de secano ➔ Fríjol cargamanto ➔ Sorgo forrajero"
                            justificacion = "Secuencia óptima para retener humedad en suelos de ladera templada."
                        elif "Nitrógeno" in prioridad:
                            rotacion = "Café con sombrío ➔ Fríjol arbustivo ➔ Gandul (Fijador)"
                            justificacion = "El gandul protege el suelo y aporta biomasa rica en nitrógeno."
                        else:
                            rotacion = "Aguacate Hass ➔ Café ➔ Tomate de árbol"
                            justificacion = "Alto valor comercial con requerimientos de suelos francos bien drenados."
                            
                    elif 12 <= temp_historica < 18:
                        piso_termico = "Frío / Andino (12 °C - 18 °C - Altiplano / Nariño)"
                        if "Conservar agua" in prioridad:
                            rotacion = "Quinua ➔ Cebada ➔ Frijol de altura"
                            justificacion = "La quinua y la cebada soportan heladas moderadas y déficit hídrico temporal."
                        elif "Nitrógeno" in prioridad:
                            rotacion = "Maíz de altura ➔ Arveja ➔ Avena de cobertura"
                            justificacion = "La arveja rompe ciclos patógenos y fija nitrógeno biológico en climas fríos."
                        else:
                            rotacion = "Papa ➔ Maíz ➔ Hortalizas de ciclo corto (Zanahoria/Cebolla)"
                            justificacion = "Alta intensidad productiva tradicional de los altiplanos andinos."
                    else:
                        piso_termico = "Muy Frío / Alta Montaña / Páramo (< 12 °C)"
                        rotacion = "Zona de Alta Fragilidad Ambiental (No recomendado para agricultura intensiva)"
                        justificacion = "Temperaturas bajo 12 °C y alta humedad limitan la agricultura y protegen fuentes hídricas."

                    col_met1, col_met2 = st.columns(2)
                    col_met1.metric("🌡️ Temp. Promedio (NASA)", f"{round(temp_historica, 1)} °C")
                    col_met2.metric("🌧️ Precip. Promedio", f"{round(precip_historica, 2)} mm/día")
                    
                    st.info(f"🏔️ **Piso Térmico Identificado:** {piso_termico}")
                    
                    st.subheader("Estrategia Recomendada")
                    st.success(f"💡 **Rotación Sugerida:** {rotacion}")
                    st.caption(f"**Justificación Agroclimática:** {justificacion}")
                    
                except Exception as e:
                    st.error(f"Error al procesar los datos satelitales de la NASA. Detalle: {e}")
