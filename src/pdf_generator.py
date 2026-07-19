import os
import logging
from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any, List
import zipfile

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.output_dir = "temp/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_pdfs(self, analysis_results: List[Dict[str, Any]]) -> str:
        """Genera PDFs para todos los estudiantes"""
        logger.info(f"📄 Generando PDFs para {len(analysis_results)} estudiantes")
        
        session_id = f"pdf_session_{int(datetime.now().timestamp())}"
        session_dir = os.path.join(self.output_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        for result in analysis_results:
            if result.get('success'):
                try:
                    # Datos básicos del estudiante
                    student_data = {
                        'student_id': result.get('student_id'),
                        'nombre': result.get('nombre'),
                        'edad': result.get('edad', 'N/A'),
                        'localidad': result.get('localidad', 'Ciudad Bolívar'),
                        'estrato': result.get('estrato', 'N/A'),
                        'analysis_parsed': result.get('analysis_parsed', {})
                    }
                    
                    # Generar PDF corto
                    self.generate_pdf_corto(student_data, session_dir)
                    
                    # Generar PDF detallado
                    self.generate_pdf_detallado(student_data, session_dir)
                    
                    logger.info(f"✅ PDFs generados para {result.get('nombre')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error generando PDFs para {result.get('nombre')}: {str(e)}")
    
        logger.info(f"📁 PDFs guardados en: {session_dir}")
        return session_dir

    def generate_pdf_corto(self, student_data: Dict[str, Any], output_dir: str = None):
        """Genera PDF corto (1 página)"""
        pdf = FPDF()
        pdf.add_page()
        
        # Configuración
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        
        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "INFORME VOCACIONAL - RESUMEN", 0, 1, 'C')
        pdf.ln(5)
        
        # Información del estudiante
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "DATOS DEL ESTUDIANTE", 0, 1)
        pdf.set_font("Arial", size=10)
        
        pdf.cell(0, 6, f"Nombre: {student_data.get('nombre', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Edad: {student_data.get('edad', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Localidad: {student_data.get('localidad', 'Ciudad Bolívar')}", 0, 1)
        pdf.cell(0, 6, f"Estrato: {student_data.get('estrato', 'N/A')}", 0, 1)
        pdf.ln(5)
        
        # Carreras recomendadas
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "CARRERAS RECOMENDADAS", 0, 1)
        pdf.set_font("Arial", size=10)
        
        carreras = student_data.get('analysis_parsed', {}).get('carreras_recomendadas', [])
        if carreras:
            for i, carrera in enumerate(carreras[:3]):  # Máximo 3 carreras
                pdf.cell(0, 6, f"{i+1}. {carrera}", 0, 1)
        else:
            pdf.cell(0, 6, "No hay carreras recomendadas disponibles", 0, 1)
        
        pdf.ln(10)
        
        # Footer
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 6, f"Generado el {datetime.now().strftime('%d/%m/%Y')} - Sistema de Orientación Vocacional", 0, 1, 'C')
        
        # Guardar
        if output_dir is None:
            output_dir = self.output_dir
            
        filename = f"{student_data['student_id']}_corto.pdf"
        filepath = os.path.join(output_dir, filename)
        pdf.output(filepath)
        
        return filepath

    def generate_pdf_detallado(self, student_data: Dict[str, Any], output_dir: str = None):
        """Genera PDF detallado (2-3 páginas)"""
        pdf = FPDF()
        pdf.add_page()
        
        # Configuración
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=11)
        
        # Página 1: Información general
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "INFORME VOCACIONAL DETALLADO", 0, 1, 'C')
        pdf.ln(8)
        
        # Información del estudiante
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "INFORMACIÓN PERSONAL", 0, 1)
        pdf.set_font("Arial", size=10)
        
        info_personal = [
            f"Nombre completo: {student_data.get('nombre', 'N/A')}",
            f"Edad: {student_data.get('edad', 'N/A')} años",
            f"Localidad: {student_data.get('localidad', 'Ciudad Bolívar')}",
            f"Estrato socioeconómico: {student_data.get('estrato', 'N/A')}",
            f"Fecha de análisis: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ]
        
        for info in info_personal:
            pdf.cell(0, 6, info, 0, 1)
        
        pdf.ln(8)
        
        # Perfil vocacional
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "PERFIL VOCACIONAL", 0, 1)
        pdf.set_font("Arial", size=10)
        
        perfil = student_data.get('analysis_parsed', {}).get('perfil_detectado', 'Perfil en evaluación')
        pdf.multi_cell(0, 6, f"Perfil detectado: {perfil}")
        pdf.ln(5)
        
        # Página 2: Carreras recomendadas
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CARRERAS RECOMENDADAS", 0, 1)
        pdf.ln(5)
        
        carreras = student_data.get('analysis_parsed', {}).get('carreras_recomendadas', [])
        if carreras:
            pdf.set_font("Arial", size=10)
            for i, carrera in enumerate(carreras):
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(0, 7, f"{i+1}. {carrera}", 0, 1)
                pdf.set_font("Arial", size=9)
                
                # Descripción de la carrera
                descripcion = self._get_descripcion_carrera(carrera)
                pdf.multi_cell(0, 5, f"   {descripcion}")
                pdf.ln(3)
        else:
            pdf.cell(0, 6, "No hay carreras recomendadas disponibles", 0, 1)
        
        # Página 3: Recomendaciones
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "RECOMENDACIONES Y PRÓXIMOS PASOS", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Arial", size=10)
        recomendaciones = [
            "1. Investigar programas del SENA en Bogotá Sur",
            "2. Explorar becas en instituciones públicas",
            "3. Considerar formación técnica como primer paso",
            "4. Participar en ferias vocacionales locales",
            "5. Consultar con orientadores profesionales",
            "6. Visitar instituciones educativas de la zona",
            "7. Investigar oportunidades de empleo local",
            "8. Considerar programas de educación virtual"
        ]
        
        for recomendacion in recomendaciones:
            pdf.cell(0, 6, recomendacion, 0, 1)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(0, 5, "Este informe es una guía inicial. Se recomienda consultar con profesionales de orientación vocacional para una evaluación más detallada.")
        
        # Footer
        pdf.set_y(-15)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, "Sistema de Orientación Vocacional - Ciudad Bolívar, Bogotá", 0, 0, 'C')
        
        # Guardar
        if output_dir is None:
            output_dir = self.output_dir
            
        filename = f"{student_data['student_id']}_detallado.pdf"
        filepath = os.path.join(output_dir, filename)
        pdf.output(filepath)
        
        return filepath

    def _get_descripcion_carrera(self, carrera: str) -> str:
        """Obtiene descripción de la carrera"""
        if 'SENA' in carrera:
            return "Institución pública con amplia cobertura. Costos accesibles y alta empleabilidad. Programas técnicos y tecnológicos."
        elif 'Técnico' in carrera:
            return "Formación práctica de 1-2 años. Enfoque en habilidades específicas para rápida inserción laboral."
        elif 'Tecnológico' in carrera:
            return "Formación de 2-3 años que combina teoría y práctica. Permite continuar con estudios profesionales."
        elif 'Universidad' in carrera:
            return "Formación profesional de 4-5 años. Enfoque teórico-práctico con amplias oportunidades de desarrollo."
        else:
            return "Carrera con oportunidades de desarrollo en la región de Bogotá."

    def create_zip_all_pdfs(self, session_dir: str) -> str:
        """Crea un ZIP con todos los PDFs"""
        zip_filename = f"orientacion_vocacional_{int(datetime.now().timestamp())}.zip"
        zip_path = os.path.join(self.output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(session_dir):
                for file in files:
                    if file.endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        # Guardar en raíz del ZIP sin estructura de carpetas
                        zipf.write(file_path, file)
        
        logger.info(f"📦 ZIP creado: {zip_path}")
        return zip_path