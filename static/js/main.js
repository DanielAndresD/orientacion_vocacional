// Funciones globales para la aplicación

// Inicializar tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

// Función para descargar reporte individual
function downloadStudentReport(studentId) {
    // Crear contenido HTML del reporte
    const student = window.studentData[studentId];
    if (!student) return;

    const reportContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte Vocacional - ${student.nombre}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #3498db; color: white; padding: 20px; border-radius: 10px; }
                .section { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }
                .career-item { background: white; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ddd; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Orientación Vocacional</h1>
                <h2>${student.nombre}</h2>
            </div>
            
            <div class="section">
                <h3>Información Personal</h3>
                <p><strong>Edad:</strong> ${student.edad} años</p>
                <p><strong>Localidad:</strong> ${student.localidad}</p>
                <p><strong>Estrato:</strong> ${student.estrato}</p>
            </div>
            
            <div class="section">
                <h3>Perfil Vocacional</h3>
                <p><strong>${student.perfil}</strong></p>
                <p>${student.descripcion}</p>
            </div>
            
            <div class="section">
                <h3>Carreras Recomendadas</h3>
                ${student.carreras.map(carrera => `
                    <div class="career-item">
                        <strong>${carrera}</strong>
                    </div>
                `).join('')}
            </div>
            
            <div class="section">
                <h3>Instituciones Sugeridas</h3>
                <ul>
                    ${student.instituciones.map(inst => `<li>${inst}</li>`).join('')}
                </ul>
            </div>
            
            <footer style="margin-top: 40px; text-align: center; color: #666;">
                <p>Generado el ${new Date().toLocaleDateString()} - Sistema de Orientación Vocacional Ciudad Bolívar</p>
            </footer>
        </body>
        </html>
    `;

    // Crear y descargar archivo
    const blob = new Blob([reportContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_vocacional_${student.nombre.replace(/\s+/g, '_')}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Función para descargar todos los reportes
function generateHTMLReports() {
    if (!window.studentData) {
        alert('No hay datos de estudiantes disponibles');
        return;
    }

    // Crear ZIP con todos los reportes (implementación básica)
    alert('Funcionalidad de descarga masiva en desarrollo. Por ahora use la descarga individual.');
    
    // Para una implementación completa, necesitaríamos una librería JS para ZIP
    // o hacerlo desde el backend con Python
}

// Función para mostrar análisis completo
// Función para mostrar análisis completo - VERSIÓN CORREGIDA
function showFullAnalysis(studentId) {
    const student = window.studentData[studentId];
    if (!student) return;

    const modalBody = document.getElementById('studentModalBody');
    
    // Parsear el contenido raw para mostrar mejor
    const analysisContent = student.analysis_raw || '';
    
    // Crear HTML estructurado en lugar del texto crudo
    modalBody.innerHTML = `
        <div class="student-analysis-detail">
            <div class="personal-info mb-4">
                <h5 class="text-primary mb-3">
                    <i class="fas fa-user me-2"></i>Información Personal
                </h5>
                <div class="row">
                    <div class="col-md-3">
                        <strong>Edad:</strong><br>
                        <span class="text-muted">${student.edad} años</span>
                    </div>
                    <div class="col-md-4">
                        <strong>Localidad:</strong><br>
                        <span class="text-muted">${student.localidad}</span>
                    </div>
                    <div class="col-md-3">
                        <strong>Estrato:</strong><br>
                        <span class="text-muted">${student.estrato}</span>
                    </div>
                    <div class="col-md-2">
                        <strong>Fuente:</strong><br>
                        <span class="text-muted">${student.fuente}</span>
                    </div>
                </div>
            </div>

            <div class="profile-section mb-4">
                <h5 class="text-primary mb-3">
                    <i class="fas fa-chart-line me-2"></i>Perfil Detectado
                </h5>
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">Evaluación vocacional robusta</h6>
                        <p class="card-text text-muted">Análisis basado en patrones de intereses y habilidades</p>
                    </div>
                </div>
            </div>

            <div class="careers-section mb-4">
                <h5 class="text-primary mb-3">
                    <i class="fas fa-graduation-cap me-2"></i>Carreras Recomendadas
                </h5>
                ${student.carreras && student.carreras.length > 0 ? 
                    student.carreras.map((carrera, index) => `
                        <div class="card mb-2">
                            <div class="card-body">
                                <h6 class="card-title">${index + 1}. ${carrera}</h6>
                                <p class="card-text text-muted">
                                    <small>Descripción detallada no disponible en este momento. 
                                    Se recomienda investigar más sobre esta carrera.</small>
                                </p>
                            </div>
                        </div>
                    `).join('') : 
                    '<p class="text-muted">No hay carreras recomendadas disponibles</p>'
                }
            </div>

            <div class="institutions-section">
                <h5 class="text-primary mb-3">
                    <i class="fas fa-university me-2"></i>Instituciones Sugeridas
                </h5>
                ${student.instituciones && student.instituciones.length > 0 ? 
                    `<ul class="list-group">
                        ${student.instituciones.map(inst => `
                            <li class="list-group-item">${inst}</li>
                        `).join('')}
                    </ul>` : 
                    '<p class="text-muted">No hay instituciones sugeridas disponibles</p>'
                }
            </div>

            ${analysisContent ? `
            <div class="raw-analysis mt-4">
                <h6 class="text-info mb-3">
                    <i class="fas fa-file-code me-2"></i>Análisis Original
                </h6>
                <div style="max-height: 200px; overflow-y: auto; background: #f8f9fa; padding: 1rem; border-radius: 5px; font-size: 0.8rem; white-space: pre-wrap; font-family: monospace;">
                    ${analysisContent}
                </div>
            </div>
            ` : ''}
        </div>
    `;

    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('studentModal'));
    modal.show();
}

// Función temporal para ver la estructura de datos
function debugStudentData(studentId) {
    const student = window.studentData[studentId];
    console.log('Estructura del estudiante:', student);
    console.log('Carreras:', student.carreras);
    
    // Verificar si hay más datos disponibles
    for (let key in student) {
        console.log(`${key}:`, student[key]);
    }
}

// Llama a esta función para ver qué datos tienes realmente
// debugStudentData('id_del_estudiante');