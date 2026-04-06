import os
from dotenv import load_dotenv
import google.generativeai as genai
from gemini_api import generate_feedback

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing Gemini with key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API Key found in .env")
    exit(1)

genai.configure(api_key=api_key)

question = "Tell me about your background?"
answer = "I am a Fresher with keen interest in Data Science and Machine Learning."

try:
    print("🚀 Calling Gemini Feedback API...")
    feedback = generate_feedback(question, answer)
    print("✅ Feedback generated successfully!")
    print(f"Feedback Preview: {feedback[:100]}...")
except Exception as e:
    print(f"❌ Gemini Failed: {e}")
