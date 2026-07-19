import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from src.excel_processor import ExcelProcessor
from src.ai_analyzer import AIAnalyzer
import tempfile
import shutil
import logging
from dotenv import load_dotenv
from src.pdf_generator import PDFGenerator
import zipfile
import json
import html
# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'orientacion-vocacional-ciudad-bolivar-2024'
app.config['UPLOAD_FOLDER'] = 'temp/uploads'
app.config['PROCESSED_FOLDER'] = 'temp/processed'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

def ensure_directories():
    """Asegurar que existen todas las carpetas necesarias"""
    directories = [
        'temp/uploads',
        'temp/processed', 
        'temp/html_exports',
        'temp/text_exports',
        'temp/pdfs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directorio asegurado: {directory}")

# Crear directorios necesarios
ensure_directories()

def escape_js(value):
    """Filtro personalizado para escapar strings para JavaScript"""
    if value is None:
        return ''
    return html.escape(str(value))

# Registrar el filtro en Jinja2
app.jinja_env.filters['escapejs'] = escape_js

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se subió ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Solo se permiten archivos Excel (.xlsx, .xls)'}), 400
        
        # Guardar archivo temporal
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f'Archivo guardado: {filepath}')
        
        # Procesar Excel
        processor = ExcelProcessor(filepath)
        students_data = processor.process_excel()
        
        # Analizar con IA
        analyzer = AIAnalyzer()
        analysis_results = analyzer.analyze_students(students_data)
        
        # Guardar resultados temporalmente
        session_id = f"session_{int(pd.Timestamp.now().timestamp())}"
        results_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{session_id}.json")
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'students_data': students_data,
                'analysis_results': analysis_results,
                'session_id': session_id
            }, f, ensure_ascii=False, indent=2)
        
        # Estadísticas del análisis
        successful_analysis = sum(1 for r in analysis_results if r.get('success', False))
        gemini_analyses = sum(1 for r in analysis_results if r.get('source', '').startswith('gemini'))
        
        return jsonify({
            'success': True,
            'message': f'✅ Procesamiento completado. {len(students_data)} estudiantes analizados.',
            'stats': {
                'total_estudiantes': len(students_data),
                'analisis_exitosos': successful_analysis,
                'analisis_gemini': gemini_analyses,
                'session_id': session_id
            },
            'redirect_url': f'/results/{session_id}',
            'sample_analysis': analysis_results[0] if analysis_results else None
        })
        
    except Exception as e:
        logger.error(f'Error en process_excel: {str(e)}')
        return jsonify({'error': f'Error procesando el archivo: {str(e)}'}), 500

@app.route('/generate-pdfs/<session_id>')
def generate_pdfs(session_id):
    """Genera PDFs para una sesión de análisis"""
    try:
        results_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{session_id}.json")
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Resultados no encontrados'}), 404
        
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generar PDFs
        pdf_generator = PDFGenerator()
        pdf_session_dir = pdf_generator.generate_pdfs(data['analysis_results'])
        
        # Crear ZIP con todos los PDFs
        zip_path = pdf_generator.create_zip_all_pdfs(pdf_session_dir)
        
        return jsonify({
            'success': True,
            'message': f'PDFs generados para {len(data["analysis_results"])} estudiantes',
            'zip_path': zip_path,
            'download_url': f'/download-zip/{os.path.basename(zip_path)}'
        })
        
    except Exception as e:
        logger.error(f'Error generando PDFs: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/download-student-pdf/<student_id>')
def download_student_pdf(student_id):
    # Lógica para generar PDF individual
    pass

@app.route('/download-zip/<filename>')
def download_zip(filename):
    """Descarga el ZIP con todos los PDFs"""
    try:
        zip_path = os.path.join('temp/pdfs', filename)
        
        if not os.path.exists(zip_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        return send_file(zip_path, as_attachment=True, download_name=f"orientacion_vocacional_{filename}")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Sistema de Orientación Vocacional funcionando'})

@app.route('/results/<session_id>')
def show_results(session_id):
    """Muestra los resultados en HTML y guarda el HTML para descarga"""
    try:
        results_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{session_id}.json")
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Resultados no encontrados'}), 404
        
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Calcular estadísticas mejoradas
        total_careers = 0
        successful_results = []
        
        for result in data['analysis_results']:
            if result.get('success'):
                successful_results.append(result)
                carreras = result.get('analysis_parsed', {}).get('carreras_recomendadas', [])
                total_careers += len(carreras)
        
        # Renderizar el HTML
        html_content = render_template('results.html', 
                            results=successful_results,
                            session_id=session_id,
                            total_students=len(successful_results),
                            total_careers=total_careers)
        
        # Guardar el HTML para descarga
        html_dir = os.path.join('temp', 'html_exports')
        os.makedirs(html_dir, exist_ok=True)
        html_file = os.path.join(html_dir, f"{session_id}.html")
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML guardado para descarga: {html_file}")
        
        return html_content
        
    except Exception as e:
        logger.error(f'Error mostrando resultados: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/download-html/<session_id>')
def download_html(session_id):
    """Descargar el HTML generado para una sesión"""
    try:
        html_dir = os.path.join('temp', 'html_exports')
        html_file = os.path.join(html_dir, f"{session_id}.html")
        
        if not os.path.exists(html_file):
            return jsonify({'error': 'Archivo HTML no encontrado'}), 404
        
        return send_file(
            html_file,
            as_attachment=True,
            download_name=f"resultados_orientacion_{session_id}.html",
            mimetype='text/html'
        )
        
    except Exception as e:
        logger.error(f'Error descargando HTML: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/download-json/<session_id>')
def download_json(session_id):
    """Descargar los datos completos en JSON"""
    try:
        results_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{session_id}.json")
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Resultados no encontrados'}), 404
        
        return send_file(
            results_file,
            as_attachment=True,
            download_name=f"datos_completos_{session_id}.json",
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f'Error descargando JSON: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/download-txt/<session_id>')
def download_txt(session_id):
    """Descargar resumen en texto plano"""
    try:
        results_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{session_id}.json")
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Resultados no encontrados'}), 404
        
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generar contenido de texto mejorado
        text_content = f"RESULTADOS ORIENTACIÓN VOCACIONAL - SISTEMA CIUDAD BOLÍVAR 2024\n"
        text_content += "=" * 60 + "\n"
        text_content += f"Sesión: {session_id}\n"
        text_content += f"Total estudiantes analizados: {len(data['analysis_results'])}\n"
        text_content += f"Fecha de generación: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n"
        text_content += "=" * 60 + "\n\n"
        
        for i, result in enumerate(data['analysis_results'], 1):
            if result.get('success'):
                text_content += f"ESTUDIANTE {i}: {result.get('nombre', 'N/A')}\n"
                text_content += f"Localidad: {result.get('localidad', 'N/A')}\n"
                text_content += f"Edad: {result.get('edad', 'N/A')} años\n"
                text_content += f"Estrato: {result.get('estrato', 'N/A')}\n"
                text_content += f"Fuente de análisis: {result.get('source', 'N/A')}\n"
                
                # Información del perfil
                parsed = result.get('analysis_parsed', {})
                text_content += f"Perfil detectado: {parsed.get('perfil_detectado', 'N/A')}\n"
                text_content += f"Descripción: {parsed.get('descripcion_perfil', 'N/A')}\n"
                
                text_content += "CARRERAS RECOMENDADAS:\n"
                carreras = parsed.get('carreras_recomendadas', [])
                for j, carrera in enumerate(carreras, 1):
                    text_content += f"  {j}. {carrera}\n"
                
                text_content += "INSTITUCIONES SUGERIDAS:\n"
                instituciones = parsed.get('instituciones_sugeridas', [])
                for j, institucion in enumerate(instituciones, 1):
                    text_content += f"  {j}. {institucion}\n"
                
                text_content += "-" * 50 + "\n\n"
        
        # Guardar archivo temporal de texto
        txt_dir = os.path.join('temp', 'text_exports')
        os.makedirs(txt_dir, exist_ok=True)
        txt_file = os.path.join(txt_dir, f"{session_id}.txt")
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return send_file(
            txt_file,
            as_attachment=True,
            download_name=f"resumen_orientacion_{session_id}.txt",
            mimetype='text/plain'
        )
        
    except Exception as e:
        logger.error(f'Error descargando TXT: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Ruta para debug del parsing
@app.route('/debug-parsing/<session_id>')
def debug_parsing(session_id):
    """Ruta para debug del parsing de análisis"""
    try:
        results_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{session_id}.json")
        
        if not os.path.exists(results_file):
            return jsonify({'error': 'Resultados no encontrados'}), 404
        
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        debug_info = []
        for result in data['analysis_results'][:3]:  # Solo primeros 3 para debug
            debug_info.append({
                'nombre': result.get('nombre'),
                'source': result.get('source'),
                'analysis_parsed': result.get('analysis_parsed'),
                'carreras_count': len(result.get('analysis_parsed', {}).get('carreras_recomendadas', [])),
                'instituciones_count': len(result.get('analysis_parsed', {}).get('instituciones_sugeridas', []))
            })
        
        return jsonify({
            'session_id': session_id,
            'total_estudiantes': len(data['analysis_results']),
            'debug_samples': debug_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info('Iniciando aplicación de Orientación Vocacional...')
    app.run(debug=True, host='0.0.0.0', port=5000)