# agro-decision-app
# AgroDecision: Sistema Inteligente de Apoyo a la Decisión para Rotación de Cultivos

> **Desafío NASA:** Desarrollado para ayudar a los agricultores a combatir el cambio climático, la variabilidad de lluvias y el deterioro de la salud del suelo mediante observaciones de la Tierra y análisis geoespacial.

---

## 📌 1. El Problema
Los agricultores de todo el mundo se enfrentan a aumentos de temperatura, alteraciones en los patrones de lluvia, escasez de agua y degradación severa de la salud del suelo. Seleccionar estrategias de rotación de cultivos adecuadas sin datos científicos precisos conduce a pérdidas económicas, erosión de los suelos y dependencia excesiva de fertilizantes sintéticos.

## 🚀 2. La Solución
**AgroDecision** es una plataforma web interactiva y modular basada en Python y Streamlit que integra **Observaciones de la Tierra de la NASA** y **datos edáficos globales** para sugerir secuencias óptimas de rotación de cultivos adaptadas al clima real, el piso térmico y las prioridades de sostenibilidad del agricultor.

### ✨ Características Principales:
- **Geolocalización GPS y Clic en Mapa:** Ubicación precisa mediante mapas interactivos (Satélite, Relieve Topográfico y Vías).
- **Filtro Estricto de Aptitud (Geofencing):** Bloquea automáticamente cuerpos de agua (océanos, ríos) e infraestructura urbana para evitar errores de análisis.
- **APIs Científicas en Tiempo Real:** 
  - *NASA POWER API:* Extracción de temperatura media, mínima y precipitación histórica superficial.
  - *SoilGrids (ISRIC):* Extracción automática de propiedades físicas del suelo (arcilla, arena, limo).
- **Motor Agrónomo por Pisos Térmicos:** Clasifica el clima y genera rotaciones orientadas a *resiliencia hídrica*, *fijación de nitrógeno* o *rentabilidad*.
- **Tarjeta de Impacto y Sostenibilidad:** Estima el ahorro en fertilizantes sintéticos y agua por hectárea.
- **Reportes Técnicos en PDF:** Generación instantánea de documentos ejecutivos descargables.
- **Historial de Lotes:** Permite guardar y gestionar múltiples parcelas en sesión local.

---

## 📂 3. Arquitectura del Software (Modularización)
El proyecto está estructurado de forma modular para garantizar escalabilidad, limpieza y fácil mantenimiento:

```text
agro-decision-app/
│
├── app.py                  # Interfaz principal de usuario (UI) y orquestador
├── style.css               # Estilos visuales modernos en tonos verdes corporativos
├── nasa_api.py             # Conector con la API de NASA POWER
├── soil_api.py             # Conector con la API edáfica global SoilGrids (ISRIC)
├── agro_engine.py          # Motor agrónomo, pisos térmicos, riesgos y sostenibilidad
├── geo_service.py          # Servicios de geocodificación inversa y autocompletado
├── map_view.py             # Renderizado dinámico de capas cartográficas con Folium
└── report_generator.py     # Generador de reportes técnicos ejecutivos en PDF (fpdf2)
