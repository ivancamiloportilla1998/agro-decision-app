from fpdf import FPDF
import datetime

def generar_reporte_pdf(lugar, lat, lon, suelo_info, clima_info, piso, rotacion, justificacion, riesgos, impacto):
    pdf = FPDF()
    pdf.add_page()
    
    # Título Principal
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 10, "REPORTE TECNICO AGROCLIMATICO", ln=True, align="C")
    
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Sistema de Decision: Rotacion de Cultivos (NASA POWER & SoilGrids)", ln=True, align="C")
    
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.cell(0, 6, f"Fecha de Emision: {fecha}", ln=True, align="C")
    pdf.ln(4)
    
    def limpiar(texto):
        if not texto:
            return ""
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Sección 1: Ubicación
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 7, "1. Ubicacion del Terreno", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, limpiar(f"Lugar: {lugar}"), ln=True)
    pdf.cell(0, 6, f"Coordenadas: Lat {lat:.4f}, Lon {lon:.4f}", ln=True)
    pdf.ln(2)

    # Sección 2: Suelo
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 7, "2. Propiedades Edaficas (Suelo Automatizado)", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, limpiar(f"Tipo Textural: {suelo_info['tipo_suelo']}"), ln=True)
    pdf.cell(0, 6, f"Fracciones: Arcilla {suelo_info['arcilla']}% | Arena {suelo_info['arena']}% | Limo {suelo_info['limo']}%", ln=True)
    pdf.cell(0, 6, limpiar(f"Fuente: {suelo_info['fuente']}"), ln=True)
    pdf.ln(2)

    # Sección 3: Clima NASA
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 7, "3. Observaciones de la Tierra (NASA POWER)", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, f"Temperatura Media Anual: {clima_info['temp_anual']:.1f} C", ln=True)
    pdf.cell(0, 6, f"Temperatura Minima Promedio: {clima_info['temp_min_anual']:.1f} C", ln=True)
    pdf.cell(0, 6, f"Precipitacion Promedio Diaria: {clima_info['precip_anual']:.2f} mm/dia", ln=True)
    pdf.ln(2)

    # Sección 4: Piso Térmico y Rotación
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 7, "4. Zonificacion y Estrategia Recomendada", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, limpiar(f"Piso Termico: {piso}"), ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, limpiar(f"Rotacion Sugerida: {rotacion}"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, limpiar(f"Justificacion Agronomica: {justificacion}"))
    pdf.ln(2)

    # Sección 5: Impacto Económico y Sostenibilidad
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 7, "5. Impacto Economico y Sostenibilidad", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 5, limpiar(f"- Enfoque: {impacto['titulo']}"), ln=True)
    pdf.cell(0, 5, limpiar(f"- Fertilizantes: {impacto['fertilizante']}"), ln=True)
    pdf.cell(0, 5, limpiar(f"- Recurso Hidrico: {impacto['agua']}"), ln=True)
    pdf.cell(0, 5, limpiar(f"- Salud del Suelo: {impacto['suelo']}"), ln=True)
    pdf.ln(2)

    # Sección 6: Riesgos
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(45, 106, 79)
    pdf.cell(0, 7, "6. Evaluacion de Riesgos Climaticos Extremos", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(40, 40, 40)
    for r in riesgos:
        texto_riesgo = r.replace("⚠️", "[Alerta]").replace("✅", "[OK]")
        pdf.multi_cell(0, 5, limpiar(f"- {texto_riesgo}"))
        
    return bytes(pdf.output())
