import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ExcelProcessor:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = None
        
    def process_excel(self) -> List[Dict[str, Any]]:
        """Procesa el archivo Excel y extrae todos los datos relevantes"""
        try:
            # Leer el Excel
            self.df = pd.read_excel(self.filepath)
            logger.info(f"Excel cargado: {len(self.df)} filas, {len(self.df.columns)} columnas")
            
            # Mostrar las columnas disponibles para debug
            logger.info("Columnas disponibles:")
            for col in self.df.columns:
                logger.info(f"  - {col}")
            
            students_data = []
            
            for index, row in self.df.iterrows():
                student = self._process_student_row(row)
                if student:
                    students_data.append(student)
            
            logger.info(f"✅ Procesados {len(students_data)} estudiantes")
            return students_data
            
        except Exception as e:
            logger.error(f"❌ Error procesando Excel: {str(e)}")
            raise

    def _process_student_row(self, row) -> Dict[str, Any]:
        """Procesa una fila individual del Excel"""
        try:
            # Información personal básica (mapeo directo)
            student = {
                'documento_id': f"est_{int(row.name) + 1}",
                'nombre_completo': self._get_value(row, '1. Nombre completo'),
                'correo': self._get_value(row, '2. Correo electrónico'),
                'telefono': self._get_value(row, '3. Teléfono de contacto (WhatsApp)'),
                'fecha_nacimiento': self._get_value(row, '4. Fecha de Nacimiento'),
                'edad': self._get_value(row, '5. Edad actual'),
                'colegio': self._get_value(row, '6. Colegio actual o último cursado'),
                'ano_graduacion': self._get_value(row, '7. Año de graduación (o expectativa)'),
                'ciudad_residencia': self._get_value(row, '8. Departamento y Ciudad/Municipio de residencia'),
                'barrio': self._get_value(row, '9. Barrio o localidad de residencia'),
                'estrato': self._get_value(row, '10. Nivel socioeconómico familiar estimado (Estrato)'),
                'sexo_biologico': self._get_value(row, '11. Sexo Biológico'),
                'identidad_genero': self._get_value(row, '12. Identidad de Género'),
                'orientacion_sexual': self._get_value(row, '13. Orientación Sexual'),
                'pertenencia_etnica': self._get_value(row, '14. Pertenencia Étnica o Racial'),
                'poblacion_vulnerable': self._get_value(row, '15. ¿Perteneces a alguna población con condiciones de vulnerabilidad?'),
                'discapacidad': self._get_value(row, '16. ¿Tienes alguna Discapacidad? (Si aplica la anterior)'),
                'acceso_internet': self._get_value(row, '17. ¿Cuentas con acceso propio y estable a Internet en casa?'),
                'equipo_computo': self._get_value(row, '18. ¿Cuentas con computador o equipo propio para estudiar?'),
            }
            
            # PREFERENCIAS VOCACIONALES - Sección 1
            student.update({
                'actividades_mas_gusta': self._get_value(row, '1. Marca las actividades que MÁS disfrutas hacer (Máx. 3):'),
                'actividades_menos_gusta': self._get_value(row, '2. Marca las actividades que MENOS disfrutas o evitarías hacer (Máx. 3):'),
                'materias_mas_gusta': self._get_value(row, '3. ¿Qué materias disfrutas MÁS en el colegio? (Máx. 2):'),
                'materias_menos_gusta': self._get_value(row, '4. ¿Qué materias disfrutas MENOS? (Máx. 2):'),
                'habilidades_identifica': self._get_value(row, '5. Marca las habilidades con las que MÁS te identificas (Máx. 3):'),
                'herramientas_frecuentes': self._get_value(row, '6. ¿Qué herramientas o recursos utilizas con más frecuencia? (Máx. 2):'),
                'productos_servicios': self._get_value(row, '7. ¿Te ves creando productos tangibles (ej. edificios, máquinas) o servicios/sistemas (ej. software, planes)?'),
                'precision_vision': self._get_value(row, '8. ¿Prefieres tareas que requieren mucha precisión y detalle o tareas que priorizan la visión general?'),
                'diagnostico_intervencion': self._get_value(row, '9. ¿Te atrae más el diagnóstico (entender la raíz del problema) o la intervención (aplicar la solución)?'),
                'aprendizaje_mejor': self._get_value(row, '10. ¿Cómo aprendes MEJOR?'),
                'entorno_trabajo': self._get_value(row, '11. ¿Qué tipo de entorno te resulta más agradable para trabajar/estudiar?'),
                'descripcion_estudio': self._get_value(row, '12. ¿Cómo te describes al estudiar o trabajar en un proyecto? (Máx. 2):'),
                'proyectos_corto_largo': self._get_value(row, '13. ¿Prefieres trabajar en proyectos a corto plazo (resultados rápidos) o a largo plazo (profundo desarrollo)?'),
                'trabajo_presion': self._get_value(row, '14. ¿Cómo manejas el trabajo bajo presión o con fechas límite estrictas?'),
                'procedimientos_flexibilidad': self._get_value(row, '15. ¿Te gusta la uniformidad y seguir procedimientos estrictos o prefieres la flexibilidad y probar nuevos métodos?'),
                'rol_equipo': self._get_value(row, '16. ¿Qué rol te sentirías más cómodo asumiendo en un equipo?'),
                'naturaleza_trabajo': self._get_value(row, '17. ¿Tu trabajo ideal es principalmente de naturaleza administrativa (gestión de recursos/personal) o técnica (ejecución especializada)?'),
                'rutina_predecible': self._get_value(row, '18. ¿Qué tan importante es para ti tener una rutina de trabajo diaria predecible?'),
            })
            
            # MOTIVACIONES Y VALORES - Sección 2
            student.update({
                'motivacion_profesional': self._get_value(row, '19. ¿Qué te motiva MÁS al pensar en tu futuro profesional?'),
                'valor_trabajo': self._get_value(row, '20. ¿Qué valor te representa mejor en tu futuro trabajo?'),
                'impacto_trabajo': self._get_value(row, '21. ¿Qué tipo de impacto te gustaría generar con tu trabajo?'),
                'mejorar_comunidad': self._get_value(row, '22. ¿Qué te gustaría mejorar o cambiar en tu comunidad o entorno con tu profesión?'),
                'viajar_movimiento': self._get_value(row, '23. ¿Qué tan importante es que tu trabajo te permita viajar o estar en constante movimiento?'),
                'trabajo_zonas_riesgo': self._get_value(row, '24. ¿Estarías dispuesto a trabajar en zonas de riesgo o de difícil acceso si eso implica un mayor impacto?'),
                'interes_artes': self._get_value(row, '25. ¿Qué te atrae más de las áreas creativas (Arte/Diseño)?'),
                'interes_salud': self._get_value(row, '26. ¿Qué te atrae más de las áreas de salud/cuidado?'),
                'carreras_interes': self._get_value(row, '27. ¿Qué carreras o áreas te llaman más la atención?'),
                'carreras_no_interes': self._get_value(row, '28. ¿Hay alguna profesión o área que definitivamente NO te gustaría estudiar? ¿Por qué?'),
                'cursos_talleres': self._get_value(row, '29. ¿Has tomado algún curso o taller práctico (SENA, cursos online, etc.)? Si sí, ¿en qué área?'),
                'comodidad_estadistica': self._get_value(row, '30. ¿Qué tan cómodo te sientes al usar herramientas de estadística o análisis de datos?'),
            })
            
            # CONTEXTO EDUCATIVO - Sección 3
            student.update({
                'importancia_salida_laboral': self._get_value(row, '31. ¿Qué tan importante es que la carrera elegida tenga una rápida salida laboral?'),
                'importancia_posgrados': self._get_value(row, '32. ¿Qué tan importante es la posibilidad de hacer Posgrados o Especializaciones en tu carrera?'),
                'tipo_formacion': self._get_value(row, '33. ¿Qué tipo de formación te gustaría seguir al graduarte?'),
                'importancia_cercania': self._get_value(row, '34. ¿Qué tan importante es que el lugar de estudio quede cerca de tu casa?'),
                'costo_estudios': self._get_value(row, '35. ¿Podrías asumir algún costo para tus estudios?'),
                'trabajar_estudiar': self._get_value(row, '36. ¿Te gustaría estudiar mientras trabajas?'),
                'obstaculos_educativos': self._get_value(row, '37. ¿Qué obstáculos crees que podrían dificultar tu camino educativo? (Máx. 2):'),
                'sector_preferido': self._get_value(row, '38. ¿Preferirías trabajar en el sector público, privado o no tienes preferencia?'),
                'jornada_estudio': self._get_value(row, '39. ¿Qué tipo de jornada de estudio prefieres?'),
                'estudiar_fuera_ciudad': self._get_value(row, '40. ¿Estarías dispuesto a estudiar fuera de tu ciudad/localidad?'),
                'apoyo_familiar_estudios': self._get_value(row, '41. ¿Cuentas con apoyo familiar (emocional/logístico) para tus estudios?'),
                'habilidades_digitales': self._get_value(row, '42. ¿Consideras que tus habilidades digitales son adecuadas para la formación virtual/tecnológica?'),
                'iniciar_tecnico': self._get_value(row, '43. ¿Estarías dispuesto a iniciar con un Nivel Técnico (1-2 años) para luego articular a un Nivel Profesional?'),
                'exito_carrera': self._get_value(row, '44. ¿Qué significa para ti "tener éxito" en tu carrera?'),
                'nota_adicional': self._get_value(row, '45. Nota Adicional: ¿Hay algo más que el orientador deba saber sobre tu vocación o tus circunstancias?'),
            })
            
            # Limpiar valores NaN
            student = {k: (v if pd.notna(v) else 'N/A') for k, v in student.items()}
            
            # Debug: mostrar información del primer estudiante
            if len([s for s in student.values() if s != 'N/A']) < 5:
                logger.warning(f"⚠️ Estudiante {student['nombre_completo']} tiene muy pocos datos")
            
            return student
            
        except Exception as e:
            logger.error(f"❌ Error procesando fila {row.name}: {str(e)}")
            return None

    def _get_value(self, row, column_name):
        """Obtiene el valor de una columna de forma segura"""
        try:
            if column_name in row:
                value = row[column_name]
                # Convertir a string si es una lista (caso de respuestas múltiples)
                if isinstance(value, list):
                    return ', '.join([str(x) for x in value])
                return str(value) if pd.notna(value) else 'N/A'
            else:
                # Buscar columna por coincidencia parcial
                matching_cols = [col for col in row.index if column_name in str(col)]
                if matching_cols:
                    value = row[matching_cols[0]]
                    return str(value) if pd.notna(value) else 'N/A'
                return 'N/A'
        except Exception as e:
            logger.warning(f"⚠️ No se pudo obtener valor para {column_name}: {str(e)}")
            return 'N/A'

    def get_column_mapping(self):
        """Muestra el mapeo de columnas para debug"""
        if self.df is None:
            return {}
        
        mapping = {}
        for col in self.df.columns:
            # Determinar a qué campo corresponde
            if 'Nombre completo' in col:
                mapping[col] = 'nombre_completo'
            elif 'Barrio' in col:
                mapping[col] = 'barrio'
            elif 'Estrato' in col:
                mapping[col] = 'estrato'
            elif 'actividades que MÁS disfrutas' in col:
                mapping[col] = 'actividades_mas_gusta'
            elif 'actividades que MENOS disfrutas' in col:
                mapping[col] = 'actividades_menos_gusta'
            elif 'materias disfrutas MÁS' in col:
                mapping[col] = 'materias_mas_gusta'
            elif 'materias disfrutas MENOS' in col:
                mapping[col] = 'materias_menos_gusta'
            elif 'habilidades con las que MÁS te identificas' in col:
                mapping[col] = 'habilidades_identifica'
            elif 'carreras o áreas te llaman más la atención' in col:
                mapping[col] = 'carreras_interes'
            # ... agregar más mapeos según sea necesario
        
        return mapping