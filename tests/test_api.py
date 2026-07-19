import os
from dotenv import load_dotenv

load_dotenv()

def test_env():
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if api_key and api_key.startswith('sk-'):
        print("✅ API Key encontrada y con formato correcto")
        print(f"📋 Primeros 10 caracteres: {api_key[:10]}...")
        return True
    elif api_key:
        print("⚠️  API Key encontrada pero formato inesperado")
        return True
    else:
        print("❌ No se encontró API Key en .env")
        print("💡 Asegúrate de que:")
        print("   - El archivo .env existe en la raíz del proyecto")
        print("   - Contiene: DEEPSEEK_API_KEY=tu_clave_real")
        return False

if __name__ == "__main__":
    test_env()