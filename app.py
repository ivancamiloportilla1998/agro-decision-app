import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱", layout="wide")

st.title("🌱 Sistema de Decisión: Rotación de Cultivos")
st.markdown("**Desafío:** Integración de datos satelitales (NASA), suelo local, cultivos y prioridades del agricultor.")

# --- 1. ESTADO DE LA APLICACIÓN ---
if 'lat' not in st.session_state:
    st.session_state['lat'] = 0.8243
if 'lon' not in st.session_state:
    st.session_state['lon'] = -77.6377
if 'lugar' not in st.session_state:
    st.session_state['lugar'] = "Ipiales, Nariño"

# --- 2. FUNCIONES DE GEOCODIFICACIÓN MEJORADA ---
def obtener_nombre_lugar(lat, lon):
    try:
        # Se añade zoom=10 para obtener ciudad/municipio y se mejora el User-Agent para evitar bloqueos
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
        headers = {'User-Agent': 'AgroDecisionApp_Col/2.0 (investigacion_agricola)'}
        res = requests.get(url, headers=headers).json()
        
        if 'display_name' in res:
            partes = res['display_name'].split(',')
            if len(partes) > 1:
                return f"{partes[0].strip()}, {partes[1].strip()}"
            return partes[0]
        return "Zona Rural Detectada"
    except Exception:
        return "Terreno agrícola (Sin nombre registrado)"

# --- 3. BARRA LATERAL (MENÚ DE UBICACIÓN) ---
st.sidebar.header("📍 Ubicación del Terreno")

metodo = st.sidebar.radio("¿Cómo deseas ubicar tu terreno?",
                          ["👆 Clic en el mapa", "🔍 Escribir el nombre", "📍 Ingresar coordenadas"])

if metodo == "🔍 Escribir el nombre":
    nuevo_lugar = st.sidebar.text_input("Lugar (Ej: Pupiales, Nariño):", value=st.session_state['lugar'])
    if st.sidebar.button("Buscar"):
        try:
            url_geo = f"https://nominatim.openstreetmap.org/search?q={nuevo_lugar}&format=json&limit=1"
            res = requests.get(url_geo, headers={'User-Agent': 'AgroDecisionApp_Col/2.0'}).json()
            if res:
                st.session_state['lat'] = float(res[0]['lat'])
                st.session_state['lon'] = float(res[0]['lon'])
                st.session_state['lugar'] = nuevo_lugar
                st.rerun()
            else:
                st.sidebar.error("Lugar no encontrado.")
        except:
            st.sidebar.error("Error de conexión al buscar.")

elif metodo == "📍 Ingresar coordenadas":
    nueva_lat = st.sidebar.number_input("Latitud:", value=float(st.session_state['lat']), format="%.6f")
    nueva_lon = st.sidebar.number_input("Longitud:", value=float(st.session_state['lon']), format="%.6f")
    if st.sidebar.button("Actualizar Mapa"):
        st.session_state['lat'] = nueva_lat
        st.session_state['lon'] = nueva_lon
        st.session_state['lugar'] = obtener_nombre_lugar(nueva_lat, nueva_lon)
        st.rerun()

else: # 👆 Clic en el mapa
    st.sidebar.info("Haz clic en cualquier punto del mapa interactivo para seleccionarlo.")
    
    # SOLUCIÓN: En lugar de cajas grises, mostramos tarjetas de color resaltadas
    st.sidebar.markdown("### 📌 Terreno Seleccionado:")
    st.sidebar.success(f"**Lugar:** {st.session_state['lugar']}")
    st.sidebar.warning(f"**Latitud:** {st.session_state['lat']:.4f} \n\n**Longitud:** {st.session_state['lon']:.4f}")

LAT = st.session_state['lat']
LON = st.session_state['lon']

# --- 4. INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1.2, 1])

with col2:
    st.subheader("Mapa Interactivo")
    m = folium.Map(location=[LAT, LON], zoom_start=11)
    folium.Marker([LAT, LON], popup=st.session_state['lugar'], icon=folium.Icon(color="red")).add_to(m)
    
    mapa_datos = st_folium(m, width=500, height=450, key="mapa_agro")
    
    if mapa_datos and mapa_datos.get("last_clicked"):
        clic_lat = mapa_datos["last_clicked"]["lat"]
        clic_lon = mapa_datos["last_clicked"]["lng"]
        
        if abs(clic_lat - LAT) > 0.0001 or abs(clic_lon - LON) > 0.0001:
            st.session_state['lat'] = clic_lat
            st.session_state['lon'] = clic_lon
            st.session_state['lugar'] = obtener_nombre_lugar(clic_lat, clic_lon)
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
    if st.button("Consultar NASA POWER y Generar Rotación"):
        with st.spinner(f"Procesando datos para: {st.session_state['lugar']}..."):
            try:
                url_nasa = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR&community=AG&longitude={LON}&latitude={LAT}&format=JSON"
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
                    st.caption("Justificación: Las leguminosas fijan nitrógeno atmosférico, reduciendo la dependencia de fertilizantes y mejorando el suelo.")
                else:
                    st.success("💡 **Rentabilidad Optimizada:** Papa ➔ Maíz ➔ Zanahoria/Cebolla")
                    st.caption("Justificación: Alta rotación comercial. Requiere riego constante y enmiendas orgánicas para recuperar desgaste de nutrientes.")
            except Exception as e:
                st.error("Error al conectar con los servidores de la NASA. Intenta probar con otra ubicación.")
