
# 📄 Sistema Automatizado de Orientación Vocacional (Chikaná)

**Autor:** Daniel Andrés Dávila Lesmes  
**Contacto:** danielandresd998@gmail.com  
**Versión:** 01  
**Fecha:** 2025 - 11  

---

## 🚀 Descripción del Proyecto

Este proyecto es una herramienta de automatización diseñada para la **orientación vocacional integral** de jóvenes en contextos de vulnerabilidad, específicamente adaptada para la localidad de Ciudad Bolívar, Bogotá. El sistema sistematiza intereses y aptitudes mediante un proceso ETL (Extracción, Transformación y Carga), analiza perfiles mediante Inteligencia Artificial y genera reportes personalizados de rutas educativas.

### Características Clave

* **Procesamiento de Datos:** Ingesta y normalización de más de 45 variables de formularios de estudiantes, procesando información masiva de manera eficiente.
* **Análisis Híbrido (IA + Heurística):** El motor `AIAnalyzer` utiliza Gemini 2.0 Flash para análisis profundo, con un sistema de *fallback* robusto basado en lógica heurística que garantiza la continuidad del servicio.
* **Anonimización y Ética:** El sistema procesa exclusivamente variables de perfil, excluyendo datos personales sensibles (nombres, teléfonos, correos) de las peticiones a la IA, garantizando la privacidad.
* **Reportes Multiformato:** Generación automática de informes en PDF, TXT y HTML, organizados por sesiones y comprimidos en archivos `.zip` para facilitar su entrega.

---

## 🛡️ Declaración de Privacidad y Ética

Para garantizar la seguridad de los jóvenes participantes, el sistema ha sido diseñado bajo los siguientes principios:

* **Anonimización Estricta:** Antes de cualquier interacción con modelos de IA, se eliminan los identificadores personales, trabajando únicamente con datos de intereses, aptitudes y entorno socioeconómico.
* **Guía Técnica (No Mandatoria):** El informe generado actúa como una **guía técnica complementaria**. Se enfatiza que las recomendaciones no son definitivas y deben ser validadas en espacios de reflexión profesional.
* **Gestión Segura:** Los datos se procesan en directorios temporales (`/temp`) que aseguran que la información sensible no persista innecesariamente en el servidor.

---

## 🏗️ Estructura del Proyecto

El proyecto sigue una arquitectura modular centrada en el despliegue de un servicio Flask:

```text
/
├── app.py                # Orquestador central (Flask)
├── /src                  # Lógica de negocio (ETL, IA, PDFs)
│   ├── ai_analyzer.py    # Análisis de perfiles y rutas
│   ├── excel_processor.py # Ingesta de datos
│   ├── pdf_generator.py  # Generación de reportes
│   └── email_sender.py   # Módulo de notificaciones
├── /static               # Recursos frontend
│   ├── /css              # Hojas de estilo
│   ├── /js               # Scripts de cliente
│   └── /images           # Recursos gráficos
├── /templates            # Interfaz web (Jinja2)
├── /temp                 # Directorios de trabajo seguros
├── .env                  # Configuración de variables de entorno
└── README.md

```

---

## ⚙️ Prerrequisitos e Instalación

Para ejecutar el sistema localmente:

1. **Requisitos:** Python 3.9+, Flask, Pandas, FPDF2, Google Generative AI.


2. **Instalación de dependencias:**
```bash
pip install -r requirements.txt

```


3. **Configuración:** Crea un archivo `.env` en la raíz con tu clave de API:
```env
GEMINI_API_KEY=tu_api_key_aqui

```


4. **Ejecución:**
```bash
python app.py

```



---

## 📊 Metodología de Evaluación

El sistema clasifica a los estudiantes en perfiles (ej. Tecnológico-Digital, Socio-Humanístico, Científico-Analítico) basándose en un sistema de *scoring* sobre sus actividades, materias y habilidades identificadas. Esta clasificación permite al sistema sugerir rutas educativas que van desde niveles **técnicos y tecnológicos (SENA)** hasta **profesionales (Universidades Públicas)**, fomentando la articulación educativa.

---

**Copyright © 2026. Todos los derechos reservados.**

```

```
