import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

# Importación de módulos especializados
from nasa_api import obtener_datos_nasa
from soil_api import obtener_suelo_soilgrids
from agro_engine import evaluar_agroclima
from report_generator import generar_reporte_pdf

st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱", layout="wide")

# --- CARGAR ESTILO CSS ---
def cargar_css(nombre_archivo):
    try:
        with open(nombre_archivo) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

cargar_css("style.css")

st.title("🌱 Sistema de Decisión: Rotación de Cultivos")
st.markdown("**Desafío NASA:** Inteligencia geoespacial avanzada, autocompletado de lugares, análisis edáfico y reportes en PDF.")

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

# --- 2. VALIDACIÓN DE APTITUD Y NOMBRE DE LUGAR ---
def validar_terreno(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
        headers = {'User-Agent': 'AgroDecisionApp_Precision/16.0'} 
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return "Terreno agrícola", True, ""
            
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
            nombre = f"{partes[0].strip()}, {partes[min(1, len(partes)-1)].strip()}"
            return nombre, True, ""
            
        return "Terreno abierto", True, ""
    except Exception:
        return f"Lat: {lat:.4f}, Lon: {lon:.4f}", True, ""

# --- 3. BARRA LATERAL CON MENÚS DESPLEGABLES ---
st.sidebar.header("🎛️ Panel de Control")

with st.sidebar.expander("📍 Ubicación del Terreno", expanded=True):
    st.write("**🛰️ Ubicación Actual (GPS):**")
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

    st.markdown("---")
    metodo = st.radio("Opciones de búsqueda:", ["👆 Clic en el mapa", "🔍 Buscar con sugerencias", "📍 Coordenadas"])

    if metodo == "🔍 Buscar con sugerencias":
        # Sistema de sugerencias en tiempo real (Autocompletado)
        texto_busqueda = st.text_input("Escribe el lugar (Ej: Potosí, Pupiales):", "")
        
        if len(texto_busqueda) >= 3:
            try:
                # Buscamos priorizando Colombia para mayor precisión
                url_sug = f"https://nominatim.openstreetmap.org/search?q={texto_busqueda},+Colombia&format=json&limit=5"
                sug_res = requests.get(url_sug, headers={'User-Agent': 'AgroApp/2.0'}).json()
                
                if sug_res:
                    opciones = {item['display_name']: (float(item['lat']), float(item['lon'])) for item in sug_res}
                    seleccion = st.selectbox("Selecciona de la lista:", list(opciones.keys()))
                    
                    if st.button("Confirmar Ubicación"):
                        sel_lat, sel_lon = opciones[seleccion]
                        nombre, apto, razon = validar_terreno(sel_lat, sel_lon)
                        st.session_state['lat'] = sel_lat
                        st.session_state['lon'] = sel_lon
                        st.session_state['lugar'] = nombre
                        st.session_state['es_apto'] = apto
                        st.session_state['razon_no_apto'] = razon
                        st.rerun()
                else:
                    st.info("Escribe al menos 3 letras para ver sugerencias...")
            except:
                st.error("Error al buscar sugerencias.")
                
    elif metodo == "📍 Coordenadas":
        nueva_lat = st.number_input("Latitud:", value=float(st.session_state['lat']), format="%.6f")
        nueva_lon = st.number_input("Longitud:", value=float(st.session_state['lon']), format="%.6f")
        if st.button("Actualizar Coordenadas"):
            nombre, apto, razon = validar_terreno(nueva_lat, nueva_lon)
            st.session_state['lat'] = nueva_lat
            st.session_state['lon'] = nueva_lon
            st.session_state['lugar'] = nombre
            st.session_state['es_apto'] = apto
            st.session_state['razon_no_apto'] = razon
            st.rerun()
    else:
        st.info("Haz clic sobre tu lote directamente en el mapa interactivo.")

    st.markdown("### 📌 Punto Seleccionado:")
    if st.session_state.get('es_apto', True):
        st.success(f"**Lugar:** {st.session_state['lugar']}")
    else:
        st.error(f"⛔ No apto: {st.session_state['razon_no_apto']}")
    st.warning(f"Lat: {st.session_state['lat']:.4f} | Lon: {st.session_state['lon']:.4f}")

with st.sidebar.expander("🗺️ Capa Cartográfica", expanded=False):
    tipo_mapa = st.selectbox("Selecciona:", ["Satélite", "Topográfico", "Político/Vial"])

LAT = st.session_state['lat']
LON = st.session_state['lon']

# --- 4. INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1.2, 1])

with col2:
    st.subheader(f"Mapa Interactivo ({tipo_mapa})")
    if tipo_mapa == "Satélite":
        m = folium.Map(location=[LAT, LON], zoom_start=14, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri')
    elif tipo_mapa == "Topográfico":
        m = folium.Map(location=[LAT, LON], zoom_start=14, tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap')
    else:
        m = folium.Map(location=[LAT, LON], zoom_start=14, tiles='openstreetmap')
    
    color_m = "green" if st.session_state.get('es_apto', True) else "red"
    folium.Marker([LAT, LON], popup=st.session_state['lugar'], icon=folium.Icon(color=color_m)).add_to(m)
    
    mapa_datos = st_folium(m, width=500, height=450, key="mapa_dinamico")
    
    # CORREGIDO: Captura de clic y actualización inmediata del panel izquierdo
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
    st.subheader("Parámetros y Análisis Inteligente")
    prioridad = st.selectbox("Prioridad del Agricultor", 
                             ["Conservar agua (Resiliencia hídrica)", 
                              "Mejorar salud (Fijar Nitrógeno)", 
                              "Maximizar rentabilidad"])
    
    if not st.session_state.get('es_apto', True):
        st.error(f"⚠️ **BLOQUEADO:** {st.session_state['razon_no_apto']}")
    else:
        if st.button("🚀 Ejecutar Análisis Satelital NASA & SoilGrids"):
            with st.spinner("Conectando con APIs de la NASA e ISRIC (Suelos)..."):
                suelo_info = obtener_suelo_soilgrids(LAT, LON)
                clima_info = obtener_datos_nasa(LAT, LON)
                
                if not clima_info['exito']:
                    st.error("Error al conectar con la NASA POWER API.")
                else:
                    temp = clima_info['temp_anual']
                    precip = clima_info['precip_anual']
                    temp_min = clima_info['temp_min_anual']
                    
                    piso, rotacion, justificacion, riesgos = evaluar_agroclima(
                        temp, precip, temp_min, suelo_info['tipo_suelo'], prioridad
                    )
                    
                    st.session_state['ultimo_resultado'] = {
                        "suelo": suelo_info, "clima": clima_info, "piso": piso,
                        "rotacion": rotacion, "justificacion": justificacion, "riesgos": riesgos
                    }

        if 'ultimo_resultado' in st.session_state:
            res = st.session_state['ultimo_resultado']
            suelo = res['suelo']
            clima = res['clima']
            
            st.success("✅ Análisis completado con éxito")
            
            cm1, cm2, cm3 = st.columns(3)
            cm1.metric("🌡️ Temp. Media", f"{round(clima['temp_anual'], 1)} °C")
            cm2.metric("🌧️ Precipitación", f"{round(clima['precip_anual'], 1)} mm/d")
            cm3.metric("🧪 Suelo (SoilGrids)", suelo['tipo_suelo'])
            
            st.info(f"🏔️ **Piso Térmico:** {res['piso']}")
            st.subheader("💡 Estrategia de Rotación")
            st.write(f"**{res['rotacion']}**")
            st.caption(f"**Justificación:** {res['justificacion']}")
            
            st.subheader("⚠️ Alertas de Riesgo Climático")
            for r in res['riesgos']:
                st.markdown(f"- {r}")
                
            pdf_bytes = generar_reporte_pdf(
                st.session_state['lugar'], LAT, LON, suelo, clima, 
                res['piso'], res['rotacion'], res['justificacion'], res['riesgos']
            )
            
            st.download_button(
                label="📥 Descargar Reporte Técnico (PDF)",
                data=pdf_bytes,
                file_name=f"Reporte_Agroclimatico_{st.session_state['lugar'].replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
