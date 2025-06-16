"""Generate Kindle book covers via Google Vertex AI (Gemini/Imagen).

Usage (local):
    export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/secrets/email-outreach-ai.json
    export GEMINI_PROJECT_ID="email-outreach-ai-460404"   # your project

    python scripts/generate_gemini_cover.py \
        --title "KindleMint: Auto-Publish Books with AI" \
        --subtitle "AI-Powered Book Publishing Engine" \
        --author "Igor Ganapolsky" \
        --output output/gemini_cover.png

Notes
-----
* Requires `google-cloud-aiplatform>=1.44.0`.
* The service account must have the `Vertex AI User` role.
* The Vertex Generative AI Images API must be enabled in the project.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any, Dict

from google.cloud import aiplatform
from google.api_core.client_options import ClientOptions

# Default prompt template (%% placeholders will be substituted)
PROMPT_TEMPLATE = (
    "You are a professional book-cover designer.\n"
    "Create a single, front-facing Kindle book cover (portrait, 2560×1600 px, RGB).\n"
    "Exact text to place on the cover:\n"
    "• Title: \"%(title)s\"\n"
    "• Subtitle: \"%(subtitle)s\"\n"
    "• Author name: \"%(author)s\"\n\n"
    "Typography requirements:\n"
    "• Use clean, modern sans-serif fonts.\n"
    "• Title must be the largest element, fully readable at thumbnail size.\n"
    "• Subtitle smaller but clearly legible.\n"
    "• Author name near the bottom.\n"
    "• High contrast: white/light text on teal-blue background motif.\n\n"
    "Layout & style guidance:\n"
    "• Professional tech-startup aesthetic — sleek, minimal, trustworthy.\n"
    "• Primary colours: teal (#0F7CAC) and white.\n"
    "• Include abstract digital-network motifs.\n"
    "• Avoid 3-D mockups; render as a flat, front cover.\n\n"
    "DO NOT generate any additional text or logos beyond Title, Subtitle, Author.\n"
)

MODEL_NAME = "imagegeneration@002"  # Latest public Imagen model as of 2025-06
LOCATION = "us-central1"


def predict_raw(prompt: str, project_id: str) -> bytes:
    """Low-level REST prediction call returning raw bytes of PNG/JPEG."""

    endpoint = (
        f"projects/{project_id}/locations/{LOCATION}/publishers/google/models/{MODEL_NAME}"
    )

    client = aiplatform.gapic.PredictionServiceClient(
        client_options=ClientOptions(api_endpoint=f"{LOCATION}-aiplatform.googleapis.com")
    )

    instances: list[Dict[str, Any]] = [{"prompt": prompt}]
    params: Dict[str, Any] = {"sampleCount": 1}

    response = client.predict(
        endpoint=endpoint,
        instances=[json.loads(json.dumps(i)) for i in instances],  # enforce JSON serialisable
        parameters=json.loads(json.dumps(params)),
    )

    if not response.predictions:
        raise RuntimeError("Vertex prediction returned no outputs.")

    output = response.predictions[0]
    # Vertex Imagen GA/preview variants may use different field names.
    if "bytesBase64" in output:
        b64_str = output["bytesBase64"]
    elif "bytesBase64Encoded" in output:
        b64_str = output["bytesBase64Encoded"]
    elif "b64" in output:
        b64_str = output["b64"]
    else:
        raise RuntimeError(
            f"Unexpected prediction schema: keys={list(output.keys())}.\nFull response: {output}"
        )
    return base64.b64decode(b64_str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a book cover via Vertex AI Gemin/Imagen")
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--output", default="output/gemini_cover.png")
    args = parser.parse_args()

    project_id = os.getenv("GEMINI_PROJECT_ID")
    if not project_id:
        raise SystemExit("GEMINI_PROJECT_ID env var must be set.")

    # Ensure output directory exists
    Path(args.output).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

    # Build prompt
    prompt = PROMPT_TEMPLATE % {
        "title": args.title,
        "subtitle": args.subtitle,
        "author": args.author,
    }

    print("📝 Sending prompt to Vertex AI… (this may take ~30s)")
    image_bytes = predict_raw(prompt, project_id)
    Path(args.output).write_bytes(image_bytes)
    print("✅ Cover saved →", args.output)


if __name__ == "__main__":
    main()
