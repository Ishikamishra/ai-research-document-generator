import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-pro-latest')

try:
    response = model.generate_content("Say hello in one sentence")
    print("✅ Gemini API Connection Successful!")
    print(f"AI Response: {response.text}")
except Exception as e:
    print("❌ Gemini API Connection Failed!")
    print(f"Error: {str(e)}")