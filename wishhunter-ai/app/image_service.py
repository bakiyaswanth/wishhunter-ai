"""Image generation and Cloud Storage publishing service for WishHunter AI.

Uses gemini-3.1-flash-lite-image in the global region.
Uploads directly in-memory to the public Cloud Storage bucket without local file writes.
"""

import re
import uuid
from typing import Any
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, Modality
from google.cloud import storage

BUCKET_NAME = "bwg3-qwiklabs-gcp-04-28d6773dbc5b"
PROJECT_ID = "qwiklabs-gcp-04-28d6773dbc5b"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"


def generate_item_image_bytes(item_name: str, style_prompt: str = "") -> tuple[bytes, str, str, str]:
    """Generate image bytes for a product using gemini-3.1-flash-lite-image in global region,

    and upload in-memory bytes to Google Cloud Storage.

    Args:
        item_name: Product or setup name.
        style_prompt: Optional styling or visual context.

    Returns:
        Tuple of (image_bytes, mime_type, filename, public_url).
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    contents = (
        f"Studio product photography of {item_name}. "
        "Crisp 4K details, clean elegant background, realistic commercial lighting. "
    )
    if style_prompt:
        contents += f"Style notes: {style_prompt}."

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=GenerateContentConfig(
            response_modalities=[Modality.TEXT, Modality.IMAGE]
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type or "image/jpeg"
            break

    if not image_bytes:
        raise ValueError(f"No image bytes were returned by {MODEL_NAME}.")

    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", item_name.strip().lower())[:30]
    filename = f"{slug}-{uuid.uuid4().hex[:6]}.jpg"

    # Upload in-memory bytes to Cloud Storage
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_path = f"products/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_path}"

    return image_bytes, mime_type, filename, public_url
