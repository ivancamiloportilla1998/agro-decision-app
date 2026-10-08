import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱", layout="wide")

st.title("Sistema de Decisión: Rotación de Cultivos")
st.write("Herramienta de análisis integrando datos satelitales (NASA) y condiciones del suelo local.")

# Creamos dos columnas para organizar la interfaz
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parámetros Locales")
    tipo_suelo = st.selectbox("Tipo de Suelo", ["Arcilloso", "Franco", "Arenoso"])
    precipitacion = st.slider("Precipitación esperada (mm)", 0, 1000, 500)
    
    st.subheader("Análisis de Rotación")
    if st.button("Generar Recomendación"):
        st.info("Simulando análisis con datos satelitales...")
        # Lógica básica de recomendación simulada
        if tipo_suelo == "Arcilloso" and precipitacion > 600:
            st.success("Recomendación: Rotación con Arroz o cultivos tolerantes a alta humedad.")
        elif tipo_suelo == "Arenoso" and precipitacion < 400:
            st.warning("Recomendación: Rotación con Sorgo o cultivos resistentes a sequía.")
        else:
            st.success("Recomendación: Rotación tradicional (Ej. Maíz - Frijol).")

with col2:
    st.subheader("Mapa de Parcelas (Ipiales, Nariño)")
    # Coordenadas aproximadas de Ipiales
    df_mapa = pd.DataFrame({
        'lat': [0.8243],
        'lon': [-77.6377]
    })
    
    # Streamlit dibuja el mapa automáticamente
    st.map(df_mapa, zoom=12)
    st.caption("Ubicación de referencia para el análisis de datos climáticos.")
