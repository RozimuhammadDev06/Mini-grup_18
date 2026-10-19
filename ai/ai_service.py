import io
import os
from functools import lru_cache
from typing import Optional, Union

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    api_key = os.getenv("AQ.Ab8RN6L_2tYYcz1oHgn9JCA_K9V8bbNYQcAj0rLgtLpLskx8K")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to the environment variables or .env file."
        )

    return genai.Client(api_key=api_key)


def _to_bytes_and_mime(image: Union[str, bytes, "Image.Image"]) -> tuple[bytes, str]:
    """Convert an image (path, bytes, or PIL Image) into (raw_bytes, mime_type)."""
    if isinstance(image, str):
        with open(image, "rb") as f:
            raw = f.read()
        pil = Image.open(io.BytesIO(raw))
        pil.load()
    elif isinstance(image, (bytes, bytearray)):
        raw = bytes(image)
        pil = Image.open(io.BytesIO(raw))
        pil.load()
    elif isinstance(image, Image.Image):
        pil = image
        buf = io.BytesIO()
        pil.save(buf, format=pil.format or "PNG")
        raw = buf.getvalue()
    else:
        raise TypeError(f"Unsupported image type: {type(image)!r}")

    mime = Image.MIME.get(pil.format, "image/png")
    return raw, mime


def send_to_ai(
    user_message: str,
    image: Optional[Union[str, bytes, "Image.Image"]] = None,
) -> str:
    """Send a user message (and optional image) to Gemini and return the response text.

    Args:
        user_message: Text prompt. May be empty when an image is supplied.
        image: Optional image — file path, raw bytes, or PIL Image.

    Returns:
        The model's text response.

    Raises:
        ValueError: If both user_message and image are empty/None.
        RuntimeError: If the API key is not configured or the model rejects images.
        TypeError: If image is an unsupported type.
    """
    if (user_message is None or not str(user_message).strip()) and image is None:
        raise ValueError("user_message or image must be provided.")

    contents = []
    if user_message and str(user_message).strip():
        contents.append(types.Part.from_text(str(user_message)))
    if image is not None:
        raw, mime = _to_bytes_and_mime(image)
        contents.append(types.Part.from_bytes(raw, mime_type=mime))

    try:
        response = get_client().models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a helpful customer service assistant "
                    "for Muhammadsodiq's project."
                ),
            ),
        )
    except Exception as exc:
        msg = str(exc).lower()
        if "does not support image" in msg or "image input" in msg or "cannot read" in msg:
            raise RuntimeError(
                "The configured Gemini model does not support image input. "
                "Use a multimodal model (e.g. gemini-2.0-flash) or send text only."
            ) from exc
        raise

    return response.text or ""


if __name__ == "__main__":
    print(send_to_ai("Hello, who are you?"))