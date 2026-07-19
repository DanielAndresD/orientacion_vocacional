import os

print("🔍 Verificando archivo .env...")

# Listar archivos en el directorio actual
print("\n📁 Archivos en el directorio:")
files = os.listdir('.')
for file in files:
    if file.startswith('.') or file in ['app.py', 'requirements.txt']:
        print(f"   {file}")

# Verificar si .env existe
env_exists = os.path.exists('.env')
print(f"\n✅ ¿Archivo .env existe?: {env_exists}")

if env_exists:
    print("\n📄 Contenido de .env:")
    try:
        with open('.env', 'r') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ Error leyendo .env: {e}")
else:
    print("\n❌ El archivo .env NO existe en la raíz del proyecto")