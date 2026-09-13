import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env file explicitly
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

print("--------------------------------------------------")
if not api_key or api_key == "your_actual_gemini_api_key_here":
    print("❌ ERROR: GEMINI_API_KEY is missing or using placeholder text in .env!")
else:
    print("✅ GEMINI_API_KEY successfully loaded from .env")
    
    try:
        client = genai.Client(api_key=api_key)

        # Updated model string to gemini-3.6-flash
        chat = client.chats.create(
            model='gemini-3.6-flash',
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful assistant for Muhammadsodiq's project."
            )
        )

        print("Sending test request to Gemini API...")
        response = chat.send_message("Ping test: respond with 'System online'")
        
        print("\n🤖 AI Response:")
        print(response.text)
        print("--------------------------------------------------")
        print("🎉 SUCCESS: Your AI setup is completely working!")
        
    except Exception as e:
        print("\n❌ API CALL FAILED!")
        print(f"Details: {e}")
        print("--------------------------------------------------")