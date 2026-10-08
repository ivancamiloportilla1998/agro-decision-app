def evaluar_agroclima(temp, precip, temp_min, tipo_suelo, prioridad):
    # 1. Pisos Térmicos
    if temp >= 24:
        piso = "Cálido (> 24 °C - Tierras bajas tropicales)"
        if "Conservar agua" in prioridad:
            rotacion = "Sorgo ➔ Yuca ➔ Fríjol caupí de secano"
            justificacion = "Cultivos altamente tolerantes a altas tasas de evapotranspiración en zonas cálidas."
        elif "Nitrógeno" in prioridad:
            rotacion = "Maíz tropical ➔ Fríjol zaragoza ➔ Abono verde (Crotalaria)"
            justificacion = "Leguminosas tropicales fijan nitrógeno rápidamente bajo alta radiación solar."
        else:
            rotacion = "Plátano ➔ Cítricos ➔ Papaya / Frutales comerciales"
            justificacion = "Rentabilidad comercial adaptada al trópico bajo."
    elif 18 <= temp < 24:
        piso = "Templado / Medio (18 °C - 24 °C - Eje Cafetero / Piedemonte)"
        if "Conservar agua" in prioridad:
            rotacion = "Maíz de secano ➔ Fríjol cargamanto ➔ Sorgo forrajero"
            justificacion = "Secuencia óptima para retener humedad en suelos de ladera templada."
        elif "Nitrógeno" in prioridad:
            rotacion = "Café con sombrío ➔ Fríjol arbustivo ➔ Gandul (Fijador)"
            justificacion = "El gandul protege el suelo y aporta biomasa rica en nitrógeno al sistema."
        else:
            rotacion = "Aguacate Hass ➔ Café ➔ Tomate de árbol"
            justificacion = "Alto valor comercial con requerimientos de suelos francos bien drenados."
    elif 12 <= temp < 18:
        piso = "Frío / Andino (12 °C - 18 °C - Altiplano / Nariño)"
        if "Conservar agua" in prioridad:
            rotacion = "Quinua ➔ Cebada ➔ Frijol de altura"
            justificacion = "La quinua y la cebada soportan heladas moderadas y déficit hídrico temporal."
        elif "Nitrógeno" in prioridad:
            rotacion = "Maíz de altura ➔ Arveja ➔ Avena de cobertura"
            justificacion = "La arveja rompe ciclos patógenos y fija nitrógeno biológico en climas fríos."
        else:
            rotacion = "Papa ➔ Maíz ➔ Hortalizas de ciclo corto (Zanahoria/Cebolla)"
            justificacion = "Alta intensidad productiva tradicional de los altiplanos andinos."
    else:
        piso = "Muy Frío / Alta Montaña / Páramo (< 12 °C)"
        rotacion = "Zona de Alta Fragilidad Ambiental (No recomendado para agricultura intensiva)"
        justificacion = "Temperaturas bajo 12 °C y alta humedad limitan la agricultura y protegen fuentes hídricas."

    # 2. Módulo de Alertas de Riesgo Climático
    riesgos = []
    if temp_min < 6:
        riesgos.append("⚠️ **Riesgo Crítico de Heladas Nocturnas:** Temperatura mínima baja detectada. Se aconseja uso de coberturas térmicas o cultivos resistentes.")
    if precip > 8:
        riesgos.append(f"⚠️ **Riesgo de Saturación / Inundación:** Precipitación elevada para suelo {tipo_suelo.lower()}. Es obligatorio establecer zanjas o canales de drenaje.")
    elif precip < 1.5:
        riesgos.append("⚠️ **Riesgo de Déficit Hídrico:** Precipitación escasa. Se requiere sistema de riego complementario.")
    
    if not riesgos:
        riesgos.append("✅ **Riesgo Climático Bajo:** Condiciones meteorológicas estables para la rotación.")

    return piso, rotacion, justificacion, riesgos
