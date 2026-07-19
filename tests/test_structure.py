import sys
import os

print("🧪 Probando instalación básica...")

try:
    # Test 1: Python básico
    print("✅ Python básico funciona")
    
    # Test 2: Flask
    import flask
    print(f"✅ Flask version: {flask.__version__}")
    
    # Test 3: Pandas (sin cargar módulos complejos)
    import pandas as pd
    print("✅ Pandas importado")
    
    # Test 4: Crear DataFrame simple
    data = {'test': [1, 2, 3]}
    df = pd.DataFrame(data)
    print("✅ DataFrame creado correctamente")
    
    print("\n🎉 ¡Todas las pruebas pasaron!")
    print("✅ El entorno está listo para desarrollar")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Solución: Ejecuta 'pip install -r requirements.txt' nuevamente")