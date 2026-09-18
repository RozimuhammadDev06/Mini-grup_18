# import os
# from functools import lru_cache

# from dotenv import load_dotenv
# from google import genai
# from google.genai import types

# load_dotenv()


# @lru_cache(maxsize=1)
# def get_client() -> genai.Client:
#     api_key = os.getenv("***REMOVED***")

#     if not api_key:
#         raise RuntimeError(
#             "***REMOVED*** is not configured. "
#             "Add it to the environment variables or .env file."
#         )

#     return genai.Client(api_key=api_key)


# def send_to_ai(user_message: str) -> str:
#     """Send a user message to Gemini and return the response text."""

#     if not user_message or not user_message.strip():
#         raise ValueError("user_message cannot be empty.")

#     response = get_client().models.generate_content(
#         model="gemini-2.5-flash",
#         contents=user_message,
#         config=types.GenerateContentConfig(
#             system_instruction=(
#                 "You are a helpful customer service assistant "
#                 "for Muhammadsodiq's project."
#             ),
#         ),
#     )

#     return response.text or ""


# if __name__ == "__main__":
#     print(send_to_ai("Hello, who are you?"))


import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to the environment variables or .env file."
        )

    return genai.Client(api_key=api_key)


def send_to_ai(user_message: str) -> str:
    """Send a user message to Gemini and return the response text."""

    if not user_message or not user_message.strip():
        raise ValueError("user_message cannot be empty.")

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful customer service assistant "
                "for Muhammadsodiq's project."
            ),
        ),
    )

    return response.text or ""


if __name__ == "__main__":
    print(send_to_ai("Hello, who are you?"))