import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱", layout="wide")

# --- 1. INICIALIZACIÓN DE VARIABLES (MEMORIA) ---
if 'lat' not in st.session_state:
    st.session_state['lat'] = 0.8243
if 'lon' not in st.session_state:
    st.session_state['lon'] = -77.6377
if 'lugar_texto' not in st.session_state:
    st.session_state['lugar_texto'] = "Ipiales, Nariño"

def obtener_nombre_lugar(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res = requests.get(url, headers={'User-Agent': 'AgroApp/1.0'}).json()
        if 'address' in res:
            ciudad = res['address'].get('city', res['address'].get('town', res['address'].get('village', res['address'].get('county', ''))))
            estado = res['address'].get('state', '')
            if ciudad and estado:
                return f"{ciudad}, {estado}"
            return res.get('display_name', "Ubicación rural").split(",")[0]
        return "Ubicación en el mapa"
    except:
        return f"Lat: {lat:.2f}, Lon: {lon:.2f}"

st.title("🌱 Sistema de Decisión: Rotación de Cultivos")
st.markdown("**Desafío:** Integración de datos satelitales (NASA), suelo local, cultivos y prioridades del agricultor.")

# --- 2. COLUMNAS PRINCIPALES (PROCESAMOS EL MAPA PRIMERO) ---
col1, col2 = st.columns([1.2, 1])

with col2:
    st.subheader("Mapa Interactivo")
    m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=11)
    folium.Marker(
        [st.session_state['lat'], st.session_state['lon']], 
        popup=st.session_state['lugar_texto'], 
        icon=folium.Icon(color="red")
    ).add_to(m)
    
    # Renderizamos el mapa
    mapa_datos = st_folium(m, width=500, height=450, key="mapa_interactivo")
    
    # Capturamos el clic inmediatamente
    if mapa_datos and mapa_datos.get("last_clicked"):
        clic_lat = mapa_datos["last_clicked"]["lat"]
        clic_lon = mapa_datos["last_clicked"]["lng"]
        
        # Si las coordenadas cambian, actualizamos todo y recargamos la app
        if clic_lat != st.session_state['lat'] or clic_lon != st.session_state['lon']:
            st.session_state['lat'] = clic_lat
            st.session_state['lon'] = clic_lon
            st.session_state['lugar_texto'] = obtener_nombre_lugar(clic_lat, clic_lon)
            st.rerun()

# --- 3. BARRA LATERAL (SE ACTUALIZA CON EL CLIC) ---
st.sidebar.header("📍 Ubicación del Terreno")
st.sidebar.info("👆 Clic en el mapa, busca por texto, o ingresa coordenadas manuales.")

metodo = st.sidebar.radio("Método de búsqueda:", ["Buscar por Texto", "Coordenadas Manuales"])

if metodo == "Buscar por Texto":
    nuevo_lugar = st.sidebar.text_input("Lugar:", value=st.session_state['lugar_texto'])
    if st.sidebar.button("Buscar en el mapa"):
        try:
            url_geo = f"https://nominatim.openstreetmap.org/search?q={nuevo_lugar}&format=json&limit=1"
            res = requests.get(url_geo, headers={'User-Agent': 'AgroApp/1.0'}).json()
            if res:
                st.session_state['lat'] = float(res[0]['lat'])
                st.session_state['lon'] = float(res[0]['lon'])
                st.session_state['lugar_texto'] = nuevo_lugar
                st.rerun()
            else:
                st.sidebar.error("Lugar no encontrado.")
        except Exception:
            st.sidebar.error("Error al buscar.")
else:
    nueva_lat = st.sidebar.number_input("Latitud:", value=float(st.session_state['lat']), format="%.6f")
    nueva_lon = st.sidebar.number_input("Longitud:", value=float(st.session_state['lon']), format="%.6f")
    if st.sidebar.button("Actualizar Mapa"):
        st.session_state['lat'] = nueva_lat
        st.session_state['lon'] = nueva_lon
        st.session_state['lugar_texto'] = obtener_nombre_lugar(nueva_lat, nueva_lon)
        st.rerun()

# Mostramos un resumen claro en la barra lateral
st.sidebar.markdown("---")
st.sidebar.success(f"**Ubicación Confirmada:**\n{st.session_state['lugar_texto']}\n\n*(Lat: {st.session_state['lat']:.4f}, Lon: {st.session_state['lon']:.4f})*")

# --- 4. ANÁLISIS DE LA NASA (COLUMNA IZQUIERDA) ---
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
    if st.button("Consultar NASA POWER y Generar Rotación"):
        with st.spinner(f"Extrayendo datos para {st.session_state['lugar_texto']}..."):
            try:
                url_nasa = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR&community=AG&longitude={st.session_state['lon']}&latitude={st.session_state['lat']}&format=JSON"
                nasa_req = requests.get(url_nasa).json()
                
                temp_historica = nasa_req['properties']['parameter']['T2M']['ANN']
                precip_historica = nasa_req['properties']['parameter']['PRECTOTCORR']['ANN']
                
                col_met1, col_met2 = st.columns(2)
                col_met1.metric("🌡️ Temp. Promedio", f"{round(temp_historica, 1)} °C")
                col_met2.metric("🌧️ Precip. Promedio", f"{round(precip_historica, 2)} mm/día")
                
                st.subheader("Estrategia Recomendada")
                if "Conservar agua" in prioridad:
                    st.success("💡 **Resiliencia Hídrica:** Sorgo ➔ Quinua ➔ Frijol de secano")
                    st.caption("Justificación: La quinua y el sorgo soportan las variaciones de lluvia y previenen erosión eólica en épocas secas.")
                elif "Nitrógeno" in prioridad:
                    st.success("💡 **Salud del Suelo:** Maíz ➔ Arveja (Leguminosa) ➔ Avena de cobertura")
                    st.caption("Justificación: Las leguminosas fijan nitrógeno atmosférico, reduciendo fertilizantes y mejorando el suelo.")
                else:
                    st.success("💡 **Rentabilidad Optimizada:** Papa ➔ Maíz ➔ Zanahoria/Cebolla")
                    st.caption("Justificación: Alta rotación comercial. Requiere riego constante y abonos para recuperar desgaste de nutrientes.")
            except Exception as e:
                st.error("Error al conectar con la NASA. La ubicación podría estar fuera de rango.")
