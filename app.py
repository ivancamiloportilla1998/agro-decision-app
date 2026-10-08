import streamlit as st
import pandas as pd
import requests
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

# Importación de módulos especializados y limpios
from geo_service import validar_terreno, buscar_sugerencias
from map_view import generar_mapa_interactivo
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
st.markdown("**Desafío NASA:** Inteligencia geoespacial modular, autocompletado de lugares, análisis edáfico y reportes en PDF.")

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

# --- 2. BARRA LATERAL ---
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
        texto_busqueda = st.text_input("Escribe el lugar (Ej: Potosí, Pupiales):", "")
        
        if len(texto_busqueda.strip()) >= 3:
            sugerencias = buscar_sugerencias(texto_busqueda)
            if sugerencias:
                seleccion = st.selectbox("Selecciona de la lista:", list(sugerencias.keys()))
                if st.button("Confirmar Ubicación"):
                    sel_lat, sel_lon = sugerencias[seleccion]
                    nombre, apto, razon = validar_terreno(sel_lat, sel_lon)
                    st.session_state['lat'] = sel_lat
                    st.session_state['lon'] = sel_lon
                    st.session_state['lugar'] = nombre
                    st.session_state['es_apto'] = apto
                    st.session_state['razon_no_apto'] = razon
                    st.rerun()
            else:
                st.caption("Buscando coincidencias en Colombia...")
                
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

# --- 3. INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1.2, 1])

with col2:
    st.subheader(f"Mapa Interactivo ({tipo_mapa})")
    
    # Renderizado usando el módulo externo map_view.py
    m = generar_mapa_interactivo(LAT, LON, st.session_state['lugar'], tipo_mapa, st.session_state.get('es_apto', True))
    mapa_datos = st_folium(m, width=500, height=450, key="mapa_dinamico")
    
    # Captura de clic sincronizada con el panel izquierdo
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
