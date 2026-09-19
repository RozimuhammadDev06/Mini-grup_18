from google import genai
from google.genai import types

# Initialize client (replace with your actual API key)
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("AQ.Ab8RN6L_2tYYcz1oHgn9JCA_K9V8bbNYQcAj0rLgtLpLskx8K"))

# 1. Define how the AI should behave overall
chat_config = types.GenerateContentConfig(
    system_instruction="You are a helpful customer service assistant for Muhammadsodiq's store. You can answer general questions, chat about any topic, and assist the customer."
)

# 2. Start the chat session
chat = client.chats.create(
    model='gemini-3.5-flash',
    config=chat_config
)

print("AI: Welcome! Ask me anything. (Type 'quit' to exit)")

# 3. Keep the conversation going until the user quits
while True:
    user_input = input("Customer: ")
    
    if user_input.lower() == 'quit':
        print("AI: Goodbye!")
        break
        
    # Send the customer's message to the AI
    response = chat.send_message(user_input)
    
    print(f"\nAI: {response.text}\n")