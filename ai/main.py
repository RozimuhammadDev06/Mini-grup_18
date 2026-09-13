from ai_service import send_to_ai
# Inside main.py
from ai_service import send_to_ai  # Brings in your AI function

user_input = input("Ask something: ")
reply = send_to_ai(user_input)
print(reply)

# Trigger this function when a user presses a search or chat button
customer_text = "Hi, can you help me find products?"
ai_response = send_to_ai(customer_text)

print(ai_response)