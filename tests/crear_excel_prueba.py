import pandas as pd
import random

def crear_excel_prueba():
    # Datos de ejemplo para un estudiante
    datos_estudiante = {
        'Marca temporal': ['2024-01-15 10:30:00'],
        '1. Nombre completo': ['María González Pérez'],
        '2. Correo electrónico': ['maria.gonzalez@ejemplo.com'],
        '3. Teléfono de contacto (WhatsApp)': ['3214567890'],
        '4. Fecha de Nacimiento': ['2005-08-15'],
        '5. Edad actual': ['18'],
        '6. Colegio actual o último cursado': ['Colegio Ciudad Bolívar IED'],
        '7. Año de graduación (o expectativa)': ['2024'],
        '8. Departamento y Ciudad/Municipio de residencia': ['Bogotá D.C., Bogotá'],
        '9. Barrio o localidad de residencia': ['Ciudad Bolívar'],
        '10. Nivel socioeconómico familiar estimado (Estrato)': ['2'],
        '11. Sexo Biológico': ['Femenino'],
        '12. Identidad de Género': ['Mujer'],
        '13. Orientación Sexual': ['Heterosexual'],
        '14. Pertenencia Étnica o Racial': ['Ninguna (Mestizo/Blanco)'],
        '15. ¿Perteneces a alguna población con condiciones de vulnerabilidad?': ['Ninguna de las anteriores'],
        '16. ¿Tienes alguna Discapacidad? (Si aplica la anterior)': ['Ninguna'],
        '17. ¿Cuentas con acceso propio y estable a Internet en casa?': ['Sí, pero con limitaciones'],
        '18. ¿Cuentas con computador o equipo propio para estudiar?': ['No, uso uno compartido'],
        
        # Preguntas vocacionales
        '1. Marca las actividades que MÁS disfrutas hacer (Máx. 3):': ['Ayudar o enseñar a otros, Cuidar o asistir a personas/animales, Investigar y leer por largos períodos'],
        '2. Marca las actividades que MENOS disfrutas o evitarías hacer (Máx. 3):': ['Resolver problemas o cálculos complejos, Trabajar con números y lógica'],
        '3. ¿Qué materias disfrutas MÁS en el colegio? (Máx. 2):': ['Lenguaje, Sociales, Historia'],
        '4. ¿Qué materias disfrutas MENOS? (Máx. 2):': ['Matemáticas, Física, Química'],
        '5. Marca las habilidades con las que MÁS te identificas (Máx. 3):': ['Empatizar y escuchar (social), Comunicar ideas y persuadir (oral/escrito)'],
        '6. ¿Qué herramientas o recursos utilizas con más frecuencia? (Máx. 2):': ['Libros de texto o artículos académicos'],
        '7. ¿Te ves creando productos tangibles (ej. edificios, máquinas) o servicios/sistemas (ej. software, planes)?': ['Servicios/Sistemas'],
        '8. ¿Prefieres tareas que requieren mucha precisión y detalle o tareas que priorizan la visión general?': ['Visión general'],
        '9. ¿Te atrae más el diagnóstico (entender la raíz del problema) o la intervención (aplicar la solución)?': ['Intervención/Ejecución'],
        '10. ¿Cómo aprendes MEJOR?': ['Discutiendo (aprendizaje social/grupal)'],
        '11. ¿Qué tipo de entorno te resulta más agradable para trabajar/estudiar?': ['Aula o espacio educativo'],
        '12. ¿Cómo te describes al estudiar o trabajar en un proyecto? (Máx. 2):': ['Empático y colaborador, Líder y comunicativo'],
        '13. ¿Prefieres trabajar en proyectos a corto plazo (resultados rápidos) o a largo plazo (profundo desarrollo)?': ['Largo Plazo'],
        '14. ¿Cómo manejas el trabajo bajo presión o con fechas límite estrictas?': ['3'],
        '15. ¿Te gusta la uniformidad y seguir procedimientos estrictos o prefieres la flexibilidad y probar nuevos métodos?': ['Flexibilidad y nuevos métodos'],
        '16. ¿Qué rol te sentirías más cómodo asumiendo en un equipo?': ['El que media y mantiene la armonía'],
        '17. ¿Tu trabajo ideal es principalmente de naturaleza administrativa (gestión de recursos/personal) o técnica (ejecución especializada)?': ['Principalmente Administrativa'],
        '18. ¿Qué tan importante es para ti tener una rutina de trabajo diaria predecible?': ['3'],
        '19. ¿Qué te motiva MÁS al pensar en tu futuro profesional?': ['Aportar a mi comunidad (impacto social)'],
        '20. ¿Qué valor te representa mejor en tu futuro trabajo?': ['Solidaridad (Ayuda a otros)'],
        '21. ¿Qué tipo de impacto te gustaría generar con tu trabajo?': ['Social o educativo'],
        '22. ¿Qué te gustaría mejorar o cambiar en tu comunidad o entorno con tu profesión?': ['Mejorar el acceso a educación de calidad'],
        '23. ¿Qué tan importante es que tu trabajo te permita viajar o estar en constante movimiento?': ['2'],
        '24. ¿Estarías dispuesto a trabajar en zonas de riesgo o de difícil acceso si eso implica un mayor impacto?': ['Sí'],
        '25. ¿Qué te atrae más de las áreas creativas (Arte/Diseño)?': ['La expresión personal y artística'],
        '26. ¿Qué te atrae más de las áreas de salud/cuidado?': ['El contacto directo y el servicio al paciente'],
        '27. ¿Qué carreras o áreas te llaman más la atención?': ['Psicología, Trabajo Social, Educación'],
        '28. ¿Hay alguna profesión o área que definitivamente NO te gustaría estudiar? ¿Por qué?': ['Ingenierías, porque no me gustan las matemáticas'],
        '29. ¿Has tomado algún curso o taller práctico (SENA, cursos online, etc.)? Si sí, ¿en qué área?': ['Taller de liderazgo comunitario en el SENA'],
        '30. ¿Qué tan cómodo te sientes al usar herramientas de estadística o análisis de datos?': ['2'],
        '31. ¿Qué tan importante es que la carrera elegida tenga una rápida salida laboral?': ['4'],
        '32. ¿Qué tan importante es la posibilidad de hacer Posgrados o Especializaciones en tu carrera?': ['3'],
        '33. ¿Qué tipo de formación te gustaría seguir al graduarte?': ['Universitaria (4–5 años)'],
        '34. ¿Qué tan importante es que el lugar de estudio quede cerca de tu casa?': ['4'],
        '35. ¿Podrías asumir algún costo para tus estudios?': ['Bajo costo (matrícula subsidiada)'],
        '36. ¿Te gustaría estudiar mientras trabajas?': ['Dependería del horario'],
        '37. ¿Qué obstáculos crees que podrían dificultar tu camino educativo? (Máx. 2):': ['Dinero, Transporte'],
        '38. ¿Preferirías trabajar en el sector público, privado o no tienes preferencia?': ['Sector Público (Estado, gobierno)'],
        '39. ¿Qué tipo de jornada de estudio prefieres?': ['Mañana'],
        '40. ¿Estarías dispuesto a estudiar fuera de tu ciudad/localidad?': ['No'],
        '41. ¿Cuentas con apoyo familiar (emocional/logístico) para tus estudios?': ['Sí'],
        '42. ¿Consideras que tus habilidades digitales son adecuadas para la formación virtual/tecnológica?': ['2'],
        '43. ¿Estarías dispuesto a iniciar con un Nivel Técnico (1-2 años) para luego articular a un Nivel Profesional?': ['Sí'],
        '44. ¿Qué significa para ti "tener éxito" en tu carrera?': ['Poder ayudar a mi comunidad y sentirme realizado'],
        '45. Nota Adicional: ¿Hay algo más que el orientador deba saber sobre tu vocación o tus circunstancias?': ['Me gustaría trabajar con niños y jóvenes en situación vulnerable']
    }
    
    # Crear DataFrame
    df = pd.DataFrame(datos_estudiante)
    
    # Guardar Excel
    nombre_archivo = 'estudiantes_prueba.xlsx'
    df.to_excel(nombre_archivo, index=False)
    print(f"✅ Archivo de prueba creado: {nombre_archivo}")
    print(f"📍 Ubicación: {os.path.abspath(nombre_archivo)}")
    
    return nombre_archivo

if __name__ == "__main__":
    crear_excel_prueba()