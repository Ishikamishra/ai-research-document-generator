from openai import OpenAI
from config import OPENAI_API_KEY

# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY)

try:
    # Test the connection
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence"}
        ],
        max_tokens=50
    )
    
    print("✅ API Connection Successful!")
    print(f"AI Response: {response.choices[0].message.content}")
    
except Exception as e:
    print("❌ API Connection Failed!")
    print(f"Error: {str(e)}")