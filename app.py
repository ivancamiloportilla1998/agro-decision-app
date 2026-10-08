import streamlit as st

st.set_page_config(page_title="Gestión de Cultivos", page_icon="🌱")

st.title("🌱 Sistema de Decisión: Rotación de Cultivos")
st.write("Herramienta de análisis integrando datos satelitales (NASA) y condiciones del suelo local.")

st.sidebar.header("Parámetros Locales")
tipo_suelo = st.sidebar.selectbox("Tipo de Suelo", ["Arcilloso", "Franco", "Arenoso"])
precipitacion = st.sidebar.slider("Precipitación esperada (mm)", 0, 1000, 500)

if st.button("Analizar Rotación Recomendada"):
    st.success(f"Analizando datos para suelo {tipo_suelo} con {precipitacion}mm de lluvia...")
