import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing with key starting: {api_key[:10] if api_key else 'None'}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print("Error listing models:", e)
else:
    print("API Key not found")
