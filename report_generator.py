import datetime

def generar_reporte_texto(lugar, lat, lon, suelo_info, clima_info, piso, rotacion, justificacion, riesgos):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    reporte = f"""==================================================
 REPORTE TÉCNICO DE INTELIGENCIA AGROCLIMÁTICA
 Sistema de Decisión: Rotación de Cultivos (NASA POWER & SoilGrids)
==================================================
 Fecha de Emisión: {fecha}
 Ubicación: {lugar}
 Coordenadas: Lat {lat:.4f}, Lon {lon:.4f}

--------------------------------------------------
 1. PROPIEDADES EDÁFICAS (SUELO AUTOMATIZADO)
--------------------------------------------------
- Tipo Textural: {suelo_info['tipo_suelo']}
- Fracciones: Arcilla {suelo_info['arcilla']}% | Arena {suelo_info['arena']}% | Limo {suelo_info['limo']}%
- Fuente: {suelo_info['fuente']}

--------------------------------------------------
 2. OBSERVACIONES DE LA TIERRA (NASA POWER)
--------------------------------------------------
- Temperatura Media Anual: {clima_info['temp_anual']:.1f} °C
- Temperatura Mínima Promedio: {clima_info['temp_min_anual']:.1f} °C
- Precipitación Promedio Diaria: {clima_info['precip_anual']:.2f} mm/día

--------------------------------------------------
 3. ZONIFICACIÓN Y PISO TÉRMICO
--------------------------------------------------
- Clasificación: {piso}

--------------------------------------------------
 4. ESTRATEGIA DE ROTACIÓN RECOMENDADA
--------------------------------------------------
- Secuencia: {rotacion}
- Justificación Agronómica: {justificacion}

--------------------------------------------------
 5. EVALUACIÓN DE RIESGOS CLIMÁTICOS EXTREMOS
--------------------------------------------------
"""
    for r in riesgos:
        reporte += f"- {r}\n"
        
    reporte += "\n==================================================\nPlataforma de Apoyo a la Decisión Agrícola (Desafío NASA)\n=================================================="
    return reporte
