import streamlit as st
import pandas as pd
import requests

# Configuración de la página
st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱", layout="wide")

st.title("Sistema de Decisión: Rotación de Cultivos")
st.write("Herramienta de análisis integrando datos climáticos en tiempo real y condiciones del suelo local.")

# Coordenadas fijas para Ipiales, Nariño (pueden ser dinámicas en el futuro)
LAT = 0.8243
LON = -77.6377

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parámetros Locales")
    tipo_suelo = st.selectbox("Tipo de Suelo", ["Arcilloso", "Franco", "Arenoso"])
    
    st.markdown("### Telemetría Climática")
    st.info(f"📍 Coordenadas de análisis: {LAT}, {LON}")
    
    if st.button("Consultar Clima y Generar Recomendación"):
        with st.spinner('Conectando con la API meteorológica...'):
            try:
                # Llamada a la API de Open-Meteo
                url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=precipitation_sum&timezone=America%2FBogota"
                respuesta = requests.get(url)
                datos = respuesta.json()
                
                # Extracción de variables clave
                temp_actual = datos['current_weather']['temperature']
                precip_hoy = datos['daily']['precipitation_sum'][0]
                
                # Mostrar métricas en la interfaz
                col_met1, col_met2 = st.columns(2)
                col_met1.metric(label="🌡️ Temp. Actual", value=f"{temp_actual} °C")
                col_met2.metric(label="🌧️ Precipitación (Hoy)", value=f"{precip_hoy} mm")
                
                st.subheader("Análisis de Rotación")
                # Lógica de recomendación basada en los datos extraídos
                if tipo_suelo == "Arcilloso" and precip_hoy > 10:
                    st.warning("⚠️ Suelo arcilloso con alta precipitación. Riesgo de encharcamiento. Recomendación: Retrasar siembra o elegir cultivos tolerantes a hipoxia radical.")
                elif tipo_suelo == "Arenoso" and precip_hoy < 2:
                    st.error("⚠️ Suelo arenoso (baja retención) y precipitación nula. Riesgo severo de estrés hídrico. Recomendación: Asegurar sistema de riego antes de rotar.")
                else:
                    st.success("✅ Condiciones agrometeorológicas estables. Recomendación: Proceder con rotación planificada (Ej. Maíz - Frijol) para mantener nitrógeno en el suelo.")
                    
            except Exception as e:
                st.error("Error al conectar con la fuente de datos. Intenta nuevamente.")

with col2:
    st.subheader("Mapa de Parcelas")
    df_mapa = pd.DataFrame({'lat': [LAT], 'lon': [LON]})
    st.map(df_mapa, zoom=12)
    st.caption("Ubicación satelital para la extracción de datos.")
