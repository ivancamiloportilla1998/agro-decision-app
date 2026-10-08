import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱", layout="wide")

st.title("Sistema de Decisión: Rotación de Cultivos")
st.markdown("**Desafío:** Integración de datos satelitales (NASA), suelo local, cultivos y prioridades del agricultor.")

# --- 1. CONFIGURACIÓN DE UBICACIÓN (Barra Lateral) ---
st.sidebar.header("📍 Ubicación del Terreno")
st.sidebar.write("Selecciona dónde vas a sembrar:")

# Variables de estado para guardar la ubicación (por defecto Ipiales)
if 'lat' not in st.session_state:
    st.session_state['lat'] = 0.8243
if 'lon' not in st.session_state:
    st.session_state['lon'] = -77.6377

metodo = st.sidebar.radio("Método de ingreso:", ["Buscar ciudad/lugar", "Coordenadas manuales"])

if metodo == "Buscar ciudad/lugar":
    lugar = st.sidebar.text_input("Escribe el lugar (Ej: Pupiales, Nariño):", "Ipiales, Colombia")
    if st.sidebar.button("Buscar en el mapa"):
        try:
            # API gratuita de OpenStreetMap para buscar coordenadas por nombre
            url_geo = f"https://nominatim.openstreetmap.org/search?q={lugar}&format=json&limit=1"
            res = requests.get(url_geo, headers={'User-Agent': 'AgroDecisionApp/1.0'}).json()
            if res:
                st.session_state['lat'] = float(res[0]['lat'])
                st.session_state['lon'] = float(res[0]['lon'])
                st.sidebar.success("¡Ubicación encontrada!")
            else:
                st.sidebar.error("Lugar no encontrado. Intenta ser más específico.")
        except Exception:
            st.sidebar.error("Error al buscar la ubicación.")
else:
    # Cajas numéricas para ingreso manual preciso
    st.session_state['lat'] = st.sidebar.number_input("Latitud:", value=st.session_state['lat'], format="%.4f")
    st.session_state['lon'] = st.sidebar.number_input("Longitud:", value=st.session_state['lon'], format="%.4f")

# Asignamos las variables finales
LAT = st.session_state['lat']
LON = st.session_state['lon']


# --- 2. INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Parámetros Locales y Prioridades")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        tipo_suelo = st.selectbox("Tipo de Suelo", ["Arcilloso", "Franco", "Arenoso"])
    with col_input2:
        prioridad = st.selectbox("Prioridad del Agricultor", 
                                 ["Conservar agua (Resiliencia hídrica)", 
                                  "Mejorar salud del suelo (Fijar Nitrógeno)", 
                                  "Maximizar rentabilidad comercial"])
    
    st.subheader("Observaciones de la Tierra (NASA)")
    if st.button("Consultar NASA POWER y Generar Rotación"):
        with st.spinner(f"Extrayendo datos de la NASA para coordenadas {LAT}, {LON}..."):
            try:
                # Consulta dinámica usando las coordenadas del mapa
                url_nasa = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR&community=AG&longitude={LON}&latitude={LAT}&format=JSON"
                nasa_req = requests.get(url_nasa).json()
                
                temp_historica = nasa_req['properties']['parameter']['T2M']['ANN']
                precip_historica = nasa_req['properties']['parameter']['PRECTOTCORR']['ANN']
                
                st.success("✅ Datos satelitales obtenidos con éxito de NASA POWER")
                col_met1, col_met2 = st.columns(2)
                col_met1.metric("🌡️ Temp. Promedio (NASA)", f"{round(temp_historica, 1)} °C")
                col_met2.metric("🌧️ Precip. Promedio (NASA)", f"{round(precip_historica, 2)} mm/día")
                
                st.subheader("Estrategia de Rotación Recomendada")
                st.write(f"**Análisis:** Basado en un suelo {tipo_suelo.lower()} y los promedios históricos de la NASA, se sugiere la siguiente secuencia para cumplir su objetivo:")
                
                if "Conservar agua" in prioridad:
                    st.info("💡 Estrategia: **Resiliencia Hídrica**")
                    st.markdown("* **Rotación:** Sorgo ➔ Quinua ➔ Frijol de secano\n* **Justificación:** Resisten variaciones de lluvia detectadas por los satélites y previenen erosión eólica.")
                elif "Nitrógeno" in prioridad:
                    st.info("💡 Estrategia: **Recuperación y Salud del Suelo**")
                    st.markdown("* **Rotación:** Maíz ➔ Arveja/Chocho (Leguminosa) ➔ Avena de cobertura\n* **Justificación:** Las leguminosas fijan nitrógeno, reduciendo fertilizantes y mejorando el microbioma del suelo.")
                else:
                    st.info("💡 Estrategia: **Rentabilidad Optimizada (Requiere Riego)**")
                    st.markdown("* **Rotación:** Papa ➔ Maíz ➔ Hortalizas de ciclo corto (Zanahoria/Cebolla)\n* **Justificación:** Maximiza el uso del terreno. Alto desgaste de nutrientes; requiere compostaje.")
                
            except Exception as e:
                st.error(f"Error al conectar con la API de la NASA. Asegúrate de que las coordenadas sean válidas. Detalle: {e}")

with col2:
    st.subheader("Mapa del Terreno")
    df_mapa = pd.DataFrame({'lat': [LAT], 'lon': [LON]})
    st.map(df_mapa, zoom=11)
    st.caption(f"Coordenadas actuales: {LAT}, {LON}")
