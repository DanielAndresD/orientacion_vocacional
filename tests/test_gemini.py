import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini_final():
    print("🎯 Probando Gemini 2.0 Flash...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ No hay API Key")
        return
    
    try:
        genai.configure(api_key=api_key)
        
        # Usar gemini-2.0-flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test de orientación vocacional
        prompt = """
        Eres un orientador vocacional. Recomienda 2 carreras para un estudiante de Ciudad Bolívar, Bogotá.
        Responde solo con:
        1. Carrera 1 - Institución
        2. Carrera 2 - Institución
        """
        
        response = model.generate_content(prompt)
        print(f"✅ Gemini 2.0 Flash funciona:")
        print(response.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_final()