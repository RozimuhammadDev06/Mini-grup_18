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


# Multimodal models that support image input, in order of preference
MULTIMODAL_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
TEXT_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]


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

    models_to_try = MULTIMODAL_MODELS if image is not None else TEXT_MODELS
    last_error = None

    for model_name in models_to_try:
        contents = []
        if user_message and str(user_message).strip():
            contents.append(types.Part.from_text(str(user_message)))
        if image is not None:
            try:
                raw, mime = _to_bytes_and_mime(image)
                contents.append(types.Part.from_bytes(raw, mime_type=mime))
            except Exception as exc:
                raise RuntimeError(f"Failed to process image: {exc}") from exc

        try:
            response = get_client().models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a helpful customer service assistant "
                        "for Muhammadsodiq's project."
                    ),
                ),
            )
            text = response.text or ""
            # Check if the model responded with "cannot read image" message
            if "does not support image" in text.lower() or "cannot read" in text.lower():
                last_error = RuntimeError(text)
                continue
            return text
        except Exception as exc:
            msg = str(exc).lower()
            last_error = exc
            if "does not support image" in msg or "image input" in msg or "cannot read" in msg:
                # Try next model
                continue
            raise

    # All multimodal models failed — try text-only fallback
    if image is not None and user_message and str(user_message).strip():
        try:
            response = get_client().models.generate_content(
                model=models_to_try[0],
                contents=[types.Part.from_text(str(user_message))],
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a helpful customer service assistant "
                        "for Muhammadsodiq's project."
                    ),
                ),
            )
            text = response.text or ""
            if text and "cannot read" not in text.lower() and "does not support image" not in text.lower():
                return text
        except Exception:
            pass

    # All models failed
    if last_error is not None:
        raise RuntimeError(
            "No available Gemini model supports image input. "
            "Send text only or use a multimodal model (e.g. gemini-2.0-flash)."
        ) from last_error
    raise RuntimeError("AI request failed.")


if __name__ == "__main__":
    print(send_to_ai("Hello, who are you?"))