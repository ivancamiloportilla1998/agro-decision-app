import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Gestión de Cultivos", page_icon="", layout="wide")

st.title("Sistema de Decisión: Rotación de Cultivos")
st.markdown("**Desafío:** Integración de datos satelitales (NASA), suelo local, cultivos y prioridades del agricultor.")

# --- 1. ESTADO DE LA APLICACIÓN ---
if 'lat' not in st.session_state:
    st.session_state['lat'] = 0.8243
if 'lon' not in st.session_state:
    st.session_state['lon'] = -77.6377
if 'lugar' not in st.session_state:
    st.session_state['lugar'] = "Ipiales, Nariño"
if 'es_apto' not in st.session_state:
    st.session_state['es_apto'] = True

# --- 2. MOTOR ESTRICTO DE GEOCODIFICACIÓN ---
def validar_terreno(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18"
        # User agent único para evitar bloqueos del servidor
        headers = {'User-Agent': 'AgroDecisionApp_Ivan_V4 (investigacion)'} 
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return "Error en satélite (No se puede verificar el terreno)", False
            
        res = response.json()
        if 'error' in res:
            return "Coordenadas inválidas", False
            
        es_apto = True
        
        # FILTRO URBANO ESTRICTO:
        if 'class' in res:
            clase = res['class']
            tipo = res.get('type', '')
            
            # Infraestructura y vías
            if clase in ['highway', 'building', 'amenity', 'leisure', 'shop', 'office', 'historic', 'man_made', 'craft', 'tourism', 'railway']:
                es_apto = False
            
            # Uso de suelo no agrícola
            if clase == 'landuse' and tipo in ['residential', 'commercial', 'retail', 'industrial', 'construction']:
                es_apto = False
        
        # Extraer el nombre exacto de la calle, edificio o zona
        if 'display_name' in res:
            partes = res['display_name'].split(',')
            nombre_lugar = f"{partes[0].strip()}, {partes[min(1, len(partes)-1)].strip()}"
            return nombre_lugar, es_apto
            
        return "Zona Desconocida", False
        
    except Exception as e:
        # Si hay cualquier error de red, NO asumimos que es agrícola
        return "Fallo de conexión al verificar el suelo", False

# --- 3. BARRA LATERAL (MENÚ DE UBICACIÓN) ---
st.sidebar.header("📍 Ubicación del Terreno")

metodo = st.sidebar.radio("¿Cómo deseas ubicar tu terreno?",
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
                nombre, apto = validar_terreno(nueva_lat, nueva_lon)
                st.session_state['lat'] = nueva_lat
                st.session_state['lon'] = nueva_lon
                st.session_state['lugar'] = nombre
                st.session_state['es_apto'] = apto
                st.rerun()
            else:
                st.sidebar.error("Lugar no encontrado.")
        except:
            st.sidebar.error("Error de conexión al buscar.")

elif metodo == "📍 Ingresar coordenadas":
    nueva_lat = st.sidebar.number_input("Latitud:", value=float(st.session_state['lat']), format="%.6f")
    nueva_lon = st.sidebar.number_input("Longitud:", value=float(st.session_state['lon']), format="%.6f")
    if st.sidebar.button("Actualizar Mapa"):
        nombre, apto = validar_terreno(nueva_lat, nueva_lon)
        st.session_state['lat'] = nueva_lat
        st.session_state['lon'] = nueva_lon
        st.session_state['lugar'] = nombre
        st.session_state['es_apto'] = apto
        st.rerun()

else: # 👆 Clic en el mapa
    st.sidebar.info("Haz clic en cualquier punto del mapa interactivo para seleccionarlo.")
    
    st.sidebar.markdown("### 📌 Terreno Seleccionado:")
    if st.session_state.get('es_apto', True):
        st.sidebar.success(f"**Lugar:** {st.session_state['lugar']}")
    else:
        st.sidebar.error(f"⛔ **Zona Urbana / Infraestructura:** \n{st.session_state['lugar']}\n\n*Terreno no apto para siembra.*")
        
    st.sidebar.warning(f"**Latitud:** {st.session_state['lat']:.4f} \n\n**Longitud:** {st.session_state['lon']:.4f}")

LAT = st.session_state['lat']
LON = st.session_state['lon']

# --- 4. INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1.2, 1])

with col2:
    st.subheader("Mapa Interactivo")
    # Zoom más cercano si es urbano para evidenciar el error
    m = folium.Map(location=[LAT, LON], zoom_start=16 if not st.session_state.get('es_apto', True) else 13)
    
    color_marcador = "green" if st.session_state.get('es_apto', True) else "red"
    icono = "leaf" if st.session_state.get('es_apto', True) else "remove-circle"
    
    folium.Marker([LAT, LON], popup=st.session_state['lugar'], icon=folium.Icon(color=color_marcador, icon=icono)).add_to(m)
    
    mapa_datos = st_folium(m, width=500, height=450, key="mapa_agro")
    
    if mapa_datos and mapa_datos.get("last_clicked"):
        clic_lat = mapa_datos["last_clicked"]["lat"]
        clic_lon = mapa_datos["last_clicked"]["lng"]
        
        if abs(clic_lat - LAT) > 0.0001 or abs(clic_lon - LON) > 0.0001:
            nombre, apto = validar_terreno(clic_lat, clic_lon)
            st.session_state['lat'] = clic_lat
            st.session_state['lon'] = clic_lon
            st.session_state['lugar'] = nombre
            st.session_state['es_apto'] = apto
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
        # Bloqueo total si es zona urbana/carretera
        st.error("⚠️ **ANÁLISIS BLOQUEADO:** Has seleccionado una edificación, vía pública o zona urbana. Selecciona un área rural o terreno abierto en el mapa para habilitar la simulación satelital.")
    else:
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
