import os
import logging
import google.generativeai as genai
import time
import re
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import time
load_dotenv()

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        time.sleep(3)  # Retardo de 3 segundos
        # Aquí llamarías a tu método original de la API
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.current_model_name = ""
        self.gemini_available = False
        self.configure_gemini()
        
    def configure_gemini(self):
        """Configura Gemini AI con el mejor modelo disponible"""
        if not self.api_key or self.api_key == 'tu_api_key_de_gemini_aqui':
            logger.warning("🚨 No hay API Key de Gemini configurada")
            self.gemini_available = False
            return
            
        try:
            genai.configure(api_key=self.api_key)
            
            # Usar solo Gemini 2.0 Flash como solicitaste
            model_name = 'models/gemini-2.0-flash'
            
            try:
                self.model = genai.GenerativeModel(model_name)
                self.current_model_name = model_name
                self.gemini_available = True
                logger.info(f"✅ Gemini configurado con: {model_name}")
            except Exception as e:
                logger.error(f"❌ Gemini 2.0 Flash no disponible: {str(e)}")
                self.gemini_available = False
                
        except Exception as e:
            logger.error(f"❌ Error configurando Gemini: {str(e)}")
            self.gemini_available = False

    def analyze_students(self, students_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analiza todos los estudiantes"""
        logger.info(f"🎯 Iniciando análisis de {len(students_data)} estudiantes")
        
        if self.gemini_available:
            logger.info(f"🤖 Usando {self.current_model_name} para análisis")
            return self.analyze_with_gemini(students_data)
        else:
            logger.info("🔄 Usando análisis ALTERNATIVO ROBUSTO")
            return self.analyze_with_robust_alternative(students_data)
        
    def analyze_with_gemini(self, students_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analiza con Gemini AI"""
        logger.info(f"🚀 Gemini analizando {len(students_data)} estudiantes con {self.current_model_name}")
        
        results = []
        successful_count = 0
        
        for i, student in enumerate(students_data):
            logger.info(f"🔍 {i+1}/{len(students_data)}: {student.get('nombre_completo')}")
            
            try:
                result = self.analyze_single_student_gemini(student)
                if result.get('success'):
                    successful_count += 1
                results.append(result)
                logger.info(f"✅ Análisis completado ({successful_count}/{i+1} exitosos)")
            except Exception as e:
                logger.error(f"❌ Error con Gemini, usando alternativa robusta: {str(e)}")
                result = self.robust_alternative_analysis(student)
                result['source'] = 'robust_alternative_fallback'
                result['error'] = str(e)
                results.append(result)
            
            time.sleep(2)  # Pausa más larga para evitar cuota
        
        logger.info(f"✅ Gemini completado: {successful_count}/{len(students_data)} exitosos")
        return results

    def analyze_single_student_gemini(self, student: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza un solo estudiante con Gemini"""
        prompt = self.build_comprehensive_prompt(student)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2000,
                )
            )
            analysis_text = response.text
            
            # Parsear el análisis para extraer información estructurada
            parsed_analysis = self.parse_gemini_analysis(analysis_text)
            
            return self._create_student_result(student, analysis_text, 'gemini', parsed_analysis)
            
        except Exception as e:
            logger.error(f"❌ Error en Gemini API: {str(e)}")
            raise

    def parse_gemini_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parsea el análisis de Gemini y extrae información estructurada de manera robusta
        """
        try:
            # Limpiar el texto
            clean_text = analysis_text.replace('&#34;', '"').replace('&#39;', "'")
            
            # Inicializar datos
            parsed_data = {
                'perfil_detectado': 'Evaluación vocacional integral',
                'descripcion_perfil': 'Análisis basado en patrones de intereses y habilidades',
                'carreras_recomendadas': [],
                'instituciones_sugeridas': [],
                'plan_accion': []
            }
            
            # Extraer perfil detectado
            perfil_patterns = [
                r'PERFIL DETECTADO[:\s]*([^\n]+)',
                r'PERFIL[:\s]*([^\n]+)',
                r'perfil con ([^\.]+)',
            ]
            
            for pattern in perfil_patterns:
                match = re.search(pattern, clean_text, re.IGNORECASE)
                if match:
                    parsed_data['perfil_detectado'] = match.group(1).strip()
                    break
            
            # Extraer descripción del perfil
            desc_patterns = [
                r'(Este joven[^\.]+\.)',
                r'(El estudiante[^\.]+\.)',
                r'presenta un perfil ([^\.]+)',
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, clean_text)
                if match:
                    parsed_data['descripcion_perfil'] = match.group(1).strip()
                    break
            
            # Extraer carreras recomendadas - Múltiples patrones
            carreras = []
            
            # Patrón 1: Lista numerada con emojis
            carrera_patterns = [
                r'\d+\.\s*\*?\*?(.*?)\s*-\s*(.*?)\s*-\s*\d+\s*años',
                r'\d+\.\s*\*?\*?(.*?)\s*-\s*(.*?)(?:\n|$)',
                r'•\s*(.*?)\s*-\s*(.*?)(?:\n|$)',
            ]
            
            for pattern in carrera_patterns:
                matches = re.findall(pattern, clean_text)
                for match in matches:
                    carrera_nombre = match[0].strip()
                    institucion = match[1].strip()
                    carreras.append(f"{carrera_nombre} - {institucion}")
            
            # Patrón 2: Buscar por tipos de opciones
            opcion_patterns = [
                (r'OPCIONES PROFESIONALES.*?\d+\.\s*([^\n-]+)', "Profesional"),
                (r'OPCIONES TECNOLÓGICAS.*?\d+\.\s*([^\n-]+)', "Tecnológica"),
                (r'OPCIONES TÉCNICAS.*?\d+\.\s*([^\n-]+)', "Técnica"),
            ]
            
            for pattern, tipo in opcion_patterns:
                matches = re.findall(pattern, clean_text, re.DOTALL | re.IGNORECASE)
                for carrera in matches:
                    carrera_limpia = carrera.strip()
                    if carrera_limpia and carrera_limpia not in [c.split(' - ')[0] for c in carreras]:
                        carreras.append(f"{carrera_limpia} - {tipo}")
            
            # Si no se encontraron carreras, usar keywords
            if not carreras:
                carrera_keywords = [
                    'Ingeniería de Sistemas', 'Ingeniería Industrial', 
                    'Desarrollo de Software', 'Mantenimiento de Equipos de Cómputo',
                    'Tecnología en', 'Técnico en'
                ]
                
                for keyword in carrera_keywords:
                    if keyword in clean_text:
                        # Buscar contexto alrededor de la keyword
                        start = max(0, clean_text.find(keyword) - 50)
                        end = min(len(clean_text), clean_text.find(keyword) + 100)
                        contexto = clean_text[start:end]
                        
                        # Extraer nombre completo de la carrera
                        carrera_match = re.search(r'([^\.\n]*' + re.escape(keyword) + r'[^\.\n]*)', contexto)
                        if carrera_match:
                            carrera_nombre = carrera_match.group(1).strip()
                            if carrera_nombre not in [c.split(' - ')[0] for c in carreras]:
                                carreras.append(f"{carrera_nombre} - Recomendada")
            
            parsed_data['carreras_recomendadas'] = carreras[:6]  # Máximo 6 carreras
            
            # Extraer instituciones
            instituciones = []
            institucion_patterns = [
                r'SENA',
                r'Universidad Nacional',
                r'Universidad Distrital',
                r'Universidad.*?Calda',
                r'Politécnico',
            ]
            
            for pattern in institucion_patterns:
                if re.search(pattern, clean_text, re.IGNORECASE):
                    inst_nombre = re.search(pattern, clean_text, re.IGNORECASE).group(0)
                    if inst_nombre not in instituciones:
                        instituciones.append(inst_nombre)
            
            # Agregar instituciones de las carreras
            for carrera in carreras:
                if ' - ' in carrera:
                    institucion = carrera.split(' - ')[1]
                    if institucion not in instituciones and len(institucion) < 50:  # Evitar textos largos
                        instituciones.append(institucion)
            
            parsed_data['instituciones_sugeridas'] = instituciones[:5]  # Máximo 5 instituciones
            
            # Extraer plan de acción
            plan_accion = []
            if 'PLAN DE ACCIÓN' in clean_text:
                plan_section = clean_text.split('PLAN DE ACCIÓN')[-1].split('[FIN_ANALISIS]')[0]
                plan_items = re.findall(r'\d+\.\s*([^\n]+)', plan_section)
                plan_accion = [item.strip() for item in plan_items[:5]]  # Máximo 5 items
            
            parsed_data['plan_accion'] = plan_accion
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error en parse_gemini_analysis: {str(e)}")
            # Retornar valores por defecto en caso de error
            return {
                'perfil_detectado': 'Evaluación vocacional integral',
                'descripcion_perfil': 'Análisis basado en patrones de intereses y habilidades',
                'carreras_recomendadas': [
                    "Ingeniería de Sistemas - Universidad Nacional",
                    "Ingeniería Industrial - Universidad Distrital", 
                    "Tecnología en Desarrollo de Software - SENA",
                    "Técnico en Mantenimiento de Equipos de Cómputo - SENA"
                ],
                'instituciones_sugeridas': ['SENA', 'Universidad Distrital', 'Universidad Nacional'],
                'plan_accion': []
            }

    # MÉTODOS ALTERNATIVOS ROBUSTOS (se mantienen igual)
    def analyze_with_robust_alternative(self, students_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Análisis alternativo robusto y coherente"""
        logger.info("🔄 Ejecutando análisis alternativo ROBUSTO")
        results = []
        
        for i, student in enumerate(students_data):
            logger.info(f"🔍 {i+1}/{len(students_data)}: {student.get('nombre_completo')}")
            
            if i > 0:
                time.sleep(0.3)
                
            result = self.robust_alternative_analysis(student)
            results.append(result)
            
        logger.info(f"✅ Análisis alternativo completado para {len(results)} estudiantes")
        return results

    def robust_alternative_analysis(self, student: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis alternativo ROBUSTO usando lógica avanzada"""
        perfil_detallado = self._analizar_perfil_completo(student)
        recomendaciones = self._generar_recomendaciones_inteligentes(perfil_detallado)
        analysis_text = self._generar_analisis_texto_coherente(student, perfil_detallado, recomendaciones)
        
        # Parsear el análisis alternativo también
        parsed_analysis = {
            'perfil_detectado': f"Perfil {perfil_detallado['perfil_principal']}",
            'descripcion_perfil': self._get_descripcion_perfil(
                perfil_detallado['perfil_principal'], 
                perfil_detallado['perfil_secundario']
            ),
            'carreras_recomendadas': [f"{r['carrera']} - {r['institucion']}" for r in recomendaciones],
            'instituciones_sugeridas': list(set([r['institucion'] for r in recomendaciones])),
            'plan_accion': []
        }
        
        return self._create_student_result(student, analysis_text, 'robust_alternative', parsed_analysis)

    def _create_student_result(self, student: Dict[str, Any], analysis_text: str, source: str, parsed_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Crea el resultado estandarizado para el estudiante"""
        if parsed_analysis is None:
            parsed_analysis = {
                'perfil_detectado': 'Evaluación vocacional integral',
                'descripcion_perfil': 'Análisis basado en patrones de intereses y habilidades',
                'carreras_recomendadas': ['Análisis en proceso'],
                'instituciones_sugeridas': ['SENA', 'Universidad Distrital', 'Universidad Nacional'],
                'plan_accion': []
            }
        
        return {
            'student_id': student.get('documento_id'),
            'nombre': student.get('nombre_completo'),
            'edad': student.get('edad', 'N/A'),
            'localidad': student.get('barrio', 'Ciudad Bolívar'),
            'estrato': student.get('estrato', 'N/A'),
            'actividades_mas_gusta': student.get('actividades_mas_gusta', 'N/A'),
            'habilidades_identifica': student.get('habilidades_identifica', 'N/A'),
            'materias_mas_gusta': student.get('materias_mas_gusta', 'N/A'),
            'carreras_interes': student.get('carreras_interes', 'N/A'),
            'analysis_raw': analysis_text,
            'analysis_parsed': parsed_analysis,
            'success': True,
            'source': source,
            'model_used': self.current_model_name if source == 'gemini' else 'robust_alternative'
        }

    # Los demás métodos se mantienen igual (_analizar_perfil_completo, _generar_recomendaciones_inteligentes, etc.)
    def _analizar_perfil_completo(self, student: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el perfil completo del estudiante con lógica avanzada"""
        actividades = student.get('actividades_mas_gusta', '').lower()
        materias = student.get('materias_mas_gusta', '').lower()
        habilidades = student.get('habilidades_identifica', '').lower()
        intereses_carreras = student.get('carreras_interes', '').lower()
        
        puntuaciones = {
            'tecnologico': 0,
            'social': 0,
            'cientifico': 0,
            'artistico': 0,
            'administrativo': 0,
            'salud': 0
        }
        
        # Tecnológico
        tech_keywords = ['programar', 'computador', 'tecnolog', 'sistema', 'digital', 'videojuego', 'internet']
        puntuaciones['tecnologico'] = sum(1 for word in tech_keywords if word in actividades or word in habilidades)
        
        # Social
        social_keywords = ['ayudar', 'enseñar', 'cuidar', 'comunidad', 'social', 'escuchar', 'apoyar']
        puntuaciones['social'] = sum(1 for word in social_keywords if word in actividades)
        
        # Científico
        ciencia_keywords = ['matemática', 'ciencia', 'investigar', 'experimento', 'analizar', 'número']
        puntuaciones['cientifico'] = sum(1 for word in ciencia_keywords if word in materias)
        
        # Artístico
        arte_keywords = ['diseñar', 'crear', 'arte', 'música', 'expresar', 'dibujar', 'escribir']
        puntuaciones['artistico'] = sum(1 for word in arte_keywords if word in actividades)
        
        # Administrativo
        admin_keywords = ['liderar', 'organizar', 'planear', 'proyecto', 'emprender', 'coordinar']
        puntuaciones['administrativo'] = sum(1 for word in admin_keywords if word in actividades)
        
        # Salud
        salud_keywords = ['medicina', 'enfermer', 'salud', 'cuidar', 'biolog', 'anatom']
        puntuaciones['salud'] = sum(1 for word in salud_keywords if word in intereses_carreras)
        
        # Determinar perfil principal y secundario
        perfil_principal = max(puntuaciones, key=puntuaciones.get)
        puntuaciones_sin_principal = {k: v for k, v in puntuaciones.items() if k != perfil_principal}
        perfil_secundario = max(puntuaciones_sin_principal, key=puntuaciones_sin_principal.get)
        
        return {
            'perfil_principal': perfil_principal,
            'perfil_secundario': perfil_secundario,
            'puntuaciones': puntuaciones,
            'confianza': max(puntuaciones.values()) / len(tech_keywords)
        }

    def _generar_recomendaciones_inteligentes(self, perfil: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones inteligentes basadas en el perfil"""
        perfiles_carreras = {
            'tecnologico': [
                {"carrera": "Ingeniería de Sistemas", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Tecnología en Desarrollo de Software", "nivel": "Tecnológico", "institucion": "SENA", "duracion": "3 años"},
                {"carrera": "Técnico en Programación", "nivel": "Técnico", "institucion": "SENA", "duracion": "2 años"},
                {"carrera": "Ingeniería Electrónica", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"}
            ],
            'social': [
                {"carrera": "Trabajo Social", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"},
                {"carrera": "Licenciatura en Pedagogía", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Técnico en Atención a la Primera Infancia", "nivel": "Técnico", "institucion": "SENA", "duracion": "2 años"},
                {"carrera": "Psicología", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"}
            ],
            'cientifico': [
                {"carrera": "Ingeniería Industrial", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Tecnología en Química Industrial", "nivel": "Tecnológico", "institucion": "SENA", "duracion": "3 años"},
                {"carrera": "Matemáticas", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"},
                {"carrera": "Física", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"}
            ],
            'artistico': [
                {"carrera": "Diseño Gráfico", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"},
                {"carrera": "Artes Plásticas", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Técnico en Producción Multimedia", "nivel": "Técnico", "institucion": "SENA", "duracion": "2 años"},
                {"carrera": "Comunicación Social", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"}
            ],
            'administrativo': [
                {"carrera": "Administración de Empresas", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Contaduría Pública", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"},
                {"carrera": "Tecnología en Gestión Empresarial", "nivel": "Tecnológico", "institucion": "SENA", "duracion": "3 años"},
                {"carrera": "Técnico en Administración", "nivel": "Técnico", "institucion": "SENA", "duracion": "2 años"}
            ],
            'salud': [
                {"carrera": "Medicina", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "6 años"},
                {"carrera": "Enfermería", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Tecnología en Regencia de Farmacia", "nivel": "Tecnológico", "institucion": "SENA", "duracion": "3 años"},
                {"carrera": "Técnico en Atención Prehospitalaria", "nivel": "Técnico", "institucion": "SENA", "duracion": "2 años"}
            ]
        }
        
        carreras_principal = perfiles_carreras.get(perfil['perfil_principal'], [])
        carreras_secundario = perfiles_carreras.get(perfil['perfil_secundario'], [])
        
        recomendaciones = []
        if carreras_principal:
            recomendaciones.extend(carreras_principal[:2])
        if carreras_secundario:
            recomendaciones.extend(carreras_secundario[:2])
        
        if len(recomendaciones) < 4:
            opciones_generales = [
                {"carrera": "Ingeniería Industrial", "nivel": "Profesional", "institucion": "Universidad Distrital", "duracion": "5 años"},
                {"carrera": "Administración de Empresas", "nivel": "Profesional", "institucion": "Universidad Nacional", "duracion": "5 años"},
                {"carrera": "Tecnología en Logística", "nivel": "Tecnológico", "institucion": "SENA", "duracion": "3 años"},
                {"carrera": "Técnico en Sistemas", "nivel": "Técnico", "institucion": "SENA", "duracion": "2 años"}
            ]
            recomendaciones.extend(opciones_generales[:4-len(recomendaciones)])
        
        return recomendaciones[:4]

    def _generar_analisis_texto_coherente(self, student: Dict[str, Any], perfil: Dict[str, Any], recomendaciones: List[Dict[str, Any]]) -> str:
        """Genera texto de análisis coherente y profesional"""
        nombre_perfiles = {
            'tecnologico': 'Tecnológico-Digital',
            'social': 'Social-Humanístico', 
            'cientifico': 'Científico-Analítico',
            'artistico': 'Artístico-Creativo',
            'administrativo': 'Administrativo-Empresarial',
            'salud': 'Salud-Asistencial'
        }
        
        perfil_principal_nombre = nombre_perfiles.get(perfil['perfil_principal'], 'Integral')
        perfil_secundario_nombre = nombre_perfiles.get(perfil['perfil_secundario'], 'Complementario')
        
        texto_analisis = f"""
[INICIO_ANALISIS]
**ANÁLISIS VOCACIONAL INTEGRAL**

**PERFIL DETECTADO:** {perfil_principal_nombre} con tendencia {perfil_secundario_nombre}
**NIVEL DE CONFIANZA:** {perfil['confianza']:.1%}

**FORTALEZAS IDENTIFICADAS:**
- Aptitud para áreas {perfil_principal_nombre.split('-')[0].lower()}
- Capacidad complementaria en {perfil_secundario_nombre.split('-')[0].lower()}
- Intereses alineados con el desarrollo profesional

**RUTAS EDUCATIVAS RECOMENDADAS:**

"""

        for i, rec in enumerate(recomendaciones, 1):
            texto_analisis += f"""
**{i}. {rec['carrera']}** - *{rec['nivel']}*
   • **Institución:** {rec['institucion']}
   • **Duración:** {rec['duracion']}
   • **Viabilidad:** {'Alta' if rec['nivel'] == 'Técnico' else 'Media-Alta'}
   • **Match con perfil:** {'Principal' if i <= 2 else 'Secundario'}
"""

        texto_analisis += f"""
**PLAN DE ACCIÓN SUGERIDO:**

1. **INVESTIGACIÓN:** Profundizar en programas del {recomendaciones[0]['institucion']}
2. **PREPARACIÓN:** Reforzar conocimientos en áreas afines
3. **FINANCIACIÓN:** Explorar becas y programas de apoyo
4. **ARTICULACIÓN:** Considerar ruta {recomendaciones[2]['nivel']} → {recomendaciones[0]['nivel']}

**INSTITUCIONES SUGERIDAS:**
- SENA (técnico/tecnológico)
- Universidad Distrital Francisco José de Caldas
- Universidad Nacional de Colombia
- Universidades públicas con programas de acceso preferente

[FIN_ANALISIS]
"""

        return texto_analisis

    def build_comprehensive_prompt(self, student: Dict[str, Any]) -> str:
        """Construye un prompt completo utilizando todos los campos relevantes del formulario"""
        return f"""
Eres un orientador vocacional experto trabajando con jóvenes de Ciudad Bolívar, Bogotá. Analiza este perfil COMPLETO considerando los 63 campos del formulario.

**INSTRUCCIONES CRÍTICAS:**
- Utiliza TODA la información proporcionada para un análisis integral
- Incluye carreras profesionales, tecnológicas y técnicas
- Considera el contexto socioeconómico real pero no limites las opciones
- Sé específico con instituciones y estrategias de acceso

**CONTEXTO PERSONAL Y SOCIOECONÓMICO:**
- Edad: {student.get('edad', 'N/A')} años
- Localidad: {student.get('barrio', 'N/A')}, Ciudad Bolívar
- Estrato: {student.get('estrato', 'N/A')}
- Acceso a internet: {student.get('acceso_internet', 'N/A')}
- Equipo de cómputo: {student.get('equipo_computo', 'N/A')}
- Población vulnerable: {student.get('poblacion_vulnerable', 'N/A')}
- Discapacidad: {student.get('discapacidad', 'N/A')}
- Apoyo familiar: {student.get('apoyo_familiar_estudios', 'N/A')}

**PREFERENCIAS VOCACIONALES DETALLADAS:**

**Intereses y Aptitudes:**
- Actividades que disfruta: {student.get('actividades_mas_gusta', 'N/A')}
- Actividades que evita: {student.get('actividades_menos_gusta', 'N/A')}
- Materias favoritas: {student.get('materias_mas_gusta', 'N/A')}
- Materias menos favoritas: {student.get('materias_menos_gusta', 'N/A')}
- Habilidades identificadas: {student.get('habilidades_identifica', 'N/A')}
- Herramientas que usa: {student.get('herramientas_frecuentes', 'N/A')}

**Estilo de Trabajo y Aprendizaje:**
- Prefiere productos o servicios: {student.get('productos_servicios', 'N/A')}
- Precisión vs visión general: {student.get('precision_vision', 'N/A')}
- Diagnóstico vs intervención: {student.get('diagnostico_intervencion', 'N/A')}
- Estilo de aprendizaje: {student.get('aprendizaje_mejor', 'N/A')}
- Entorno preferido: {student.get('entorno_trabajo', 'N/A')}
- Descripción al estudiar: {student.get('descripcion_estudio', 'N/A')}
- Proyectos corto/largo plazo: {student.get('proyectos_corto_largo', 'N/A')}
- Trabajo bajo presión: {student.get('trabajo_presion', 'N/A')}
- Procedimientos vs flexibilidad: {student.get('procedimientos_flexibilidad', 'N/A')}
- Rol en equipo: {student.get('rol_equipo', 'N/A')}
- Naturaleza del trabajo: {student.get('naturaleza_trabajo', 'N/A')}
- Importancia de rutina: {student.get('rutina_predecible', 'N/A')}

**Motivaciones y Valores:**
- Motivación profesional: {student.get('motivacion_profesional', 'N/A')}
- Valor principal: {student.get('valor_trabajo', 'N/A')}
- Tipo de impacto deseado: {student.get('impacto_trabajo', 'N/A')}
- Mejorar en comunidad: {student.get('mejorar_comunidad', 'N/A')}
- Importancia de viajar: {student.get('viajar_movimiento', 'N/A')}
- Trabajar en zonas de riesgo: {student.get('trabajo_zonas_riesgo', 'N/A')}
- Interés en artes: {student.get('interes_artes', 'N/A')}
- Interés en salud: {student.get('interes_salud', 'N/A')}

**Preferencias Específicas:**
- Carreras de interés: {student.get('carreras_interes', 'N/A')}
- Carreras que descarta: {student.get('carreras_no_interes', 'N/A')}
- Cursos/talleres previos: {student.get('cursos_talleres', 'N/A')}
- Comodidad con estadística: {student.get('comodidad_estadistica', 'N/A')}

**Contexto Educativo y Restricciones:**
- Importancia salida laboral: {student.get('importancia_salida_laboral', 'N/A')}
- Importancia posgrados: {student.get('importancia_posgrados', 'N/A')}
- Tipo de formación deseada: {student.get('tipo_formacion', 'N/A')}
- Importancia cercanía: {student.get('importancia_cercania', 'N/A')}
- Costo que puede asumir: {student.get('costo_estudios', 'N/A')}
- Trabajar mientras estudia: {student.get('trabajar_estudiar', 'N/A')}
- Obstáculos identificados: {student.get('obstaculos_educativos', 'N/A')}
- Sector preferido: {student.get('sector_preferido', 'N/A')}
- Jornada de estudio: {student.get('jornada_estudio', 'N/A')}
- Estudiar fuera de ciudad: {student.get('estudiar_fuera_ciudad', 'N/A')}
- Habilidades digitales: {student.get('habilidades_digitales', 'N/A')}
- Iniciar con técnico: {student.get('iniciar_tecnico', 'N/A')}
- Definición de éxito: {student.get('exito_carrera', 'N/A')}
- Nota adicional: {student.get('nota_adicional', 'N/A')}

**REQUERIMIENTOS PARA EL ANÁLISIS:**

1. **ANÁLISIS INTEGRAL:** Considera TODOS los campos anteriores para un perfil completo
2. **RUTAS ESTRATIFICADAS:** Incluye 4-5 opciones balanceadas entre profesional, tecnológico y técnico
3. **VIABILIDAD REAL:** Considera programas de becas, universidades públicas y rutas articuladas
4. **PERSONALIZACIÓN:** Basa las recomendaciones en las preferencias específicas del estudiante

**FORMATO DE RESPUESTA:**

[INICIO_ANALISIS]
**ANÁLISIS INTEGRAL DEL PERFIL**
[Análisis detallado considerando todos los aspectos del formulario]

**RUTAS EDUCATIVAS RECOMENDADAS:**

**🎓 OPCIONES PROFESIONALES (Universidades Públicas):**
1. [Carrera profesional 1] - [Universidad específica] - [Duración]
   • Match con perfil: [% basado en preferencias]
   • Estrategia de acceso: [Becas, preparación específica]
   • Ventajas: [Alineación con intereses]

2. [Carrera profesional 2] - [Universidad específica] - [Duración]
   • Match con perfil: [% basado en preferencias]
   • Estrategia de acceso: [Programas especiales]
   • Ventajas: [Desarrollo profesional]

**🔄 OPCIONES TECNOLÓGICAS (Transición):**
3. [Carrera tecnológica] - [Institución] - [Duración]
   • Viabilidad: [Alta/Media]
   • Articulación: [Posibilidad de continuar]
   • Ventajas: [Rápida inserción laboral]

**⚡ OPCIONES TÉCNICAS (Inicio inmediato):**
4. [Carrera técnica] - [Institución] - [Duración]
   • Viabilidad: [Muy Alta]
   • Propósito: [Primer paso, experiencia]

**PLAN DE ACCIÓN PERSONALIZADO:**
[Recomendaciones específicas basadas en el perfil completo]

[FIN_ANALISIS]
"""

    def _get_descripcion_perfil(self, perfil_principal: str, perfil_secundario: str) -> str:
        """Genera descripción del perfil basada en combinación de perfiles"""
        combinaciones = {
            ('tecnologico', 'administrativo'): "Perfil técnico-administrativo con capacidad para gestionar proyectos tecnológicos",
            ('tecnologico', 'cientifico'): "Perfil científico-tecnológico ideal para investigación aplicada y desarrollo",
            ('social', 'artistico'): "Perfil socio-artístico para carreras de impacto comunitario y expresión cultural",
            ('social', 'salud'): "Perfil socio-sanitario orientado al cuidado y bienestar de las personas",
            ('administrativo', 'tecnologico'): "Perfil administrativo-tecnológico para gestión de sistemas y procesos",
            ('cientifico', 'tecnologico'): "Perfil científico-tecnológico para innovación y desarrollo tecnológico"
        }
        
        clave = (perfil_principal, perfil_secundario)
        if clave in combinaciones:
            return combinaciones[clave]
        
        descripciones = {
            'tecnologico': "Aptitud para tecnologías, sistemas y soluciones digitales",
            'social': "Vocación de servicio, enseñanza y trabajo comunitario",
            'cientifico': "Capacidad analítica, investigación y método científico", 
            'artistico': "Creatividad, expresión artística y diseño",
            'administrativo': "Habilidades organizativas, liderazgo y gestión",
            'salud': "Interés en cuidado, bienestar y ciencias de la salud"
        }
        
        principal_desc = descripciones.get(perfil_principal, "Capacidades diversas")
        secundario_desc = descripciones.get(perfil_secundario, "habilidades complementarias")
        
        return f"{principal_desc} con {secundario_desc}"

    # Métodos de compatibilidad
    def analyze_with_enhanced_mock(self, students_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.analyze_with_robust_alternative(students_data)

    def enhanced_mock_analysis(self, student: Dict[str, Any]) -> Dict[str, Any]:
        return self.robust_alternative_analysis(student)

    def determinar_perfil_integral(self, student: Dict[str, Any]) -> Dict[str, Any]:
        return self._analizar_perfil_completo(student)