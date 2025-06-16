"""Generate Kindle book cover variants using AI models.

This script supports multiple AI providers with fallbacks:
1. OpenAI DALL·E 3 (primary)
2. Stability AI SDXL (fallback)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

import openai
import requests
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# ---------- Constants ---------- #
OUTPUT_DIR = Path("output/book_covers")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_DIR = OUTPUT_DIR / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

N_VARIANTS = 3

# Replicate configuration - using a known working SDXL model
REPLICATE_MODEL = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

# ---------- Prompt template ---------- #
PROMPT_TEMPLATE = """
Create a professional book cover design for:

Title: "{title}"
Subtitle: "{subtitle}"
Author: {author}

Design requirements:
- Modern, clean, professional appearance
- Bold, readable typography suitable for thumbnail size
- Color scheme that conveys innovation and technology (blues, teals, grays)
- Abstract tech elements or geometric patterns
- Ensure title is the most prominent text element
- Professional book cover layout with proper text hierarchy
"""

# ================= Overlay Style Constants =================
# All sizing and style constants are here for easy tuning.
KDP_FINAL_SIZE = (2560, 1600)  # (width, height)
OVERLAY_RENDER_SCALE = 2  # Render at 2x for sharpness
RENDER_SIZE = (KDP_FINAL_SIZE[0]*OVERLAY_RENDER_SCALE, KDP_FINAL_SIZE[1]*OVERLAY_RENDER_SCALE)
FONTS_DIR = Path(__file__).parent.parent / "assets/fonts"
FONT_MONTSERRAT_BOLD = str(FONTS_DIR / "Montserrat-Bold.ttf")
FONT_MONTSERRAT_REGULAR = str(FONTS_DIR / "Montserrat-Regular.ttf")

# Default style (can be overridden via CLI)
DEFAULT_TITLE_SIZE_PCT = 0.12
DEFAULT_SUBTITLE_SIZE_PCT = 0.07
DEFAULT_AUTHOR_SIZE_PCT = 0.05
DEFAULT_TITLE_COLOR = "#FFFFFF"
DEFAULT_SUBTITLE_COLOR = "#1E78B4"
DEFAULT_AUTHOR_COLOR = "#5A5A5A"
DEFAULT_TITLE_TOP_PAD_PCT = 0.14  # distance from top as % of height
TEXT_STROKE_WIDTH = 6  # in rendered (2x) pixels
TEXT_SHADOW_OFFSET = (8, 8)  # in rendered (2x) pixels
TEXT_SHADOW_COLOR = (0, 0, 0, 120)  # RGBA

# ---------- Helper Functions ---------- #

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Attempt to load Montserrat font; fall back gracefully."""
    candidate_paths = [
        FONT_MONTSERRAT_BOLD if bold else FONT_MONTSERRAT_REGULAR,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for p in candidate_paths:
        try:
            if Path(p).exists():
                return ImageFont.truetype(p, size=size)
        except OSError:
            continue
    # Finally, default bitmap font
    print("⚠️  Falling back to default font; custom font unavailable or unreadable.")
    return ImageFont.load_default()

def setup_openai_client() -> Optional[openai.OpenAI]:
    """Initialize and return OpenAI client if API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("   ⚠️ OPENAI_API_KEY not set. Skipping DALL·E.")
        return None
    return openai.OpenAI(api_key=api_key)

def setup_replicate_client():
    """Initialize and return Replicate client if API key is available."""
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("   ⚠️ REPLICATE_API_TOKEN not set. Skipping SDXL.")
        return None
    try:
        import replicate
        return replicate.Client(api_token=api_token)
    except ImportError:
        print("   ⚠️ replicate package not installed. Install with: pip install replicate")
        return None

def generate_with_openai(client: openai.OpenAI, prompt: str) -> Optional[str]:
    """Generate image using OpenAI's DALL·E."""
    try:
        print("   🎨 Calling OpenAI DALL·E...")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url",
        )
        url = response.data[0].url
        print(f"   ✅ OpenAI success: {url[:50]}...")
        return url
    except Exception as e:
        print(f"   ❌ OpenAI failed: {e}")
        return None

def generate_with_replicate(client, prompt: str) -> Optional[str]:
    """Generate image using Replicate's SDXL."""
    try:
        print("   🎨 Calling Replicate SDXL...")
        print(f"   📝 Model: {REPLICATE_MODEL}")
        print(f"   📝 Prompt: {prompt[:100]}...")
        
        output = client.run(
            REPLICATE_MODEL,
            input={
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "num_outputs": 1,
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "scheduler": "DPMSolverMultistep"
            }
        )
        
        print(f"   📤 Replicate response type: {type(output)}")
        print(f"   📤 Replicate response: {output}")
        
        if isinstance(output, list) and len(output) > 0:
            url = output[0]
            print(f"   ✅ Replicate success: {url}")
            return url
        else:
            print(f"   ❌ Replicate returned unexpected format: {output}")
            return None
            
    except Exception as e:
        print(f"   ❌ Replicate failed: {e}")
        return None

def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def overlay_text_on_cover(img_path, title, subtitle, author, out_path, shadow=True, *,
                          title_size_pct: float, subtitle_size_pct: float, author_size_pct: float,
                          title_color: tuple, subtitle_color: tuple, author_color: tuple,
                          title_top_pad_pct: float):
    # Open and resize background to 2x target size
    # Open and resize background to 2x target size
    img = Image.open(img_path).convert("RGB")
    img = img.resize(RENDER_SIZE, resample=Image.LANCZOS)
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    font_title = load_font(size=int(H * title_size_pct), bold=True)
    font_sub = load_font(size=int(H * subtitle_size_pct), bold=False)
    font_author = load_font(size=int(H * author_size_pct), bold=False)

    def get_text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return w, h

    def draw_text_with_effects(x, y, text, font, fill, stroke_width=0, stroke_fill=None, shadow=False):
        if shadow:
            shadow_x, shadow_y = TEXT_SHADOW_OFFSET
            draw.text((x+shadow_x, y+shadow_y), text, font=font, fill=TEXT_SHADOW_COLOR)
        if stroke_width > 0:
            draw.text((x, y), text, font=font, fill=stroke_fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        draw.text((x, y), text, font=font, fill=fill)

    # Title (centered, top area)
    title_y = int(H * title_top_pad_pct)
    title_w, title_h = get_text_size(title, font_title)
    title_x = (W - title_w) / 2
    draw_text_with_effects(
        title_x, title_y, title, font_title, title_color,
        stroke_width=TEXT_STROKE_WIDTH, stroke_fill=title_color, shadow=shadow
    )

    # Subtitle (centered, below title)
    subtitle_y = title_y + title_h + int(H * 0.04)
    sub_w, sub_h = get_text_size(subtitle, font_sub)
    sub_x = (W - sub_w) / 2
    draw_text_with_effects(
        sub_x, subtitle_y, subtitle, font_sub, subtitle_color,
        stroke_width=TEXT_STROKE_WIDTH, stroke_fill=subtitle_color, shadow=shadow
    )

    # Author (centered, near bottom)
    author_y = int(H * 0.82)
    author_w, author_h = get_text_size(author, font_author)
    author_x = (W - author_w) / 2
    draw_text_with_effects(
        author_x, author_y, author, font_author, author_color,
        stroke_width=TEXT_STROKE_WIDTH, stroke_fill=author_color, shadow=shadow
    )

    # Downscale to KDP size for ultra-crisp text
    img_final = img.resize(KDP_FINAL_SIZE, resample=Image.LANCZOS)
    img_final.save(out_path, "JPEG", quality=95)

def download_image(url: str, dest: Path) -> bool:
    """Download image from URL to destination."""
    try:
        print(f"   📥 Downloading from: {url}")
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = dest.stat().st_size
        print(f"   ✅ Image saved → {dest} ({file_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"   ❌ Failed to download image: {e}")
        return False

def generate_variants(args: argparse.Namespace, add_text: bool) -> list[dict]:
    """Generate cover variants using available AI models."""
    print(f"\n🚀 Setting up AI providers...")
    
    openai_client = setup_openai_client()
    replicate_client = setup_replicate_client()
    
    if not openai_client and not replicate_client:
        print("❌ No AI providers available. Check your API keys.")
        return []
    
    metadata = []
    
    for idx in range(1, N_VARIANTS + 1):
        print(f"\n→ Generating cover v{idx}...")
        
        # Prepare prompt
        prompt = PROMPT_TEMPLATE.format(
            title=args.title,
            subtitle=args.subtitle,
            author=args.author
        ).strip()
        
        # Try OpenAI first
        image_url = None
        if openai_client:
            image_url = generate_with_openai(openai_client, prompt)
        
        # Fallback to Replicate SDXL
        if not image_url and replicate_client:
            image_url = generate_with_replicate(replicate_client, prompt)
        
        # If no image was generated, skip to next variant
        if not image_url:
            print("   ❌ Could not generate image with any provider. Skipping variant.")
            continue
        
        # Download and save the image
        img_path = OUTPUT_DIR / f"cover_v{idx}.jpg"
        if download_image(image_url, img_path):
            # Save plain background (already done)
            if add_text:
                # Overlay text and save to final_*
                final_path = FINAL_DIR / f"final_cover_v{idx}.jpg"
                overlay_text_on_cover(
                    img_path, args.title, args.subtitle, args.author, final_path,
                    shadow=True,
                    title_size_pct=args.title_size,
                    subtitle_size_pct=args.subtitle_size,
                    author_size_pct=args.author_size,
                    title_color=_hex_to_rgb(args.title_color),
                    subtitle_color=_hex_to_rgb(args.subtitle_color),
                    author_color=_hex_to_rgb(args.author_color),
                    title_top_pad_pct=args.title_pad
                )
                print(f"   🖊️  Final cover with text saved → {final_path}")
            metadata.append({
                "filename": img_path.name,
                "title": args.title,
                "subtitle": args.subtitle,
                "author": args.author,
                "prompt": prompt,
                "provider": "OpenAI DALL·E" if "openai" in str(image_url).lower() else "Stability AI SDXL",
                "generated_at": datetime.utcnow().isoformat() + "Z"
            })
    
    return metadata

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate AI-powered book covers.")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--subtitle", required=True, help="Book subtitle")
    parser.add_argument("--author", required=True, help="Author name")
    # Style overrides
    parser.add_argument("--title-size", type=float, default=DEFAULT_TITLE_SIZE_PCT, help="Title font size as % of image height (default 0.12)")
    parser.add_argument("--subtitle-size", type=float, default=DEFAULT_SUBTITLE_SIZE_PCT, help="Subtitle font size % (default 0.07)")
    parser.add_argument("--author-size", type=float, default=DEFAULT_AUTHOR_SIZE_PCT, help="Author font size % (default 0.05)")
    parser.add_argument("--title-color", default=DEFAULT_TITLE_COLOR, help="Hex color for title text (default #FFFFFF)")
    parser.add_argument("--subtitle-color", default=DEFAULT_SUBTITLE_COLOR, help="Hex color for subtitle text")
    parser.add_argument("--author-color", default=DEFAULT_AUTHOR_COLOR, help="Hex color for author text")
    parser.add_argument("--title-pad", type=float, default=DEFAULT_TITLE_TOP_PAD_PCT, help="Top padding for title as % of image height (default 0.14)")
    parser.add_argument("--add-text", action="store_true", help="Overlay title/subtitle/author text on covers")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"📚 Generating {N_VARIANTS} cover variants for:")
    print(f"   Title: {args.title}")
    print(f"   Subtitle: {args.subtitle}")
    print(f"   Author: {args.author}")
    print("=" * 60)
    
    # Generate variants
    metadata = generate_variants(args, add_text=args.add_text)
    
    # Save metadata
    if metadata:
        meta_path = OUTPUT_DIR / "covers_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "book": {
                    "title": args.title,
                    "subtitle": args.subtitle,
                    "author": args.author,
                    "generated_at": datetime.utcnow().isoformat() + "Z"
                },
                "covers": metadata
            }, f, indent=2)
        
        print(f"\n✅ Successfully generated {len(metadata)} covers!")
        print(f"📄 Metadata saved to: {meta_path}")
        print(f"🖼️ Images saved to: {OUTPUT_DIR}")
        if args.add_text:
            print(f"🖼️ Final covers with text saved to: {FINAL_DIR}")
    else:
        print("\n❌ No covers were generated. Check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify your OPENAI_API_KEY in .env file")
        print("   2. Verify your REPLICATE_API_TOKEN in .env file")
        print("   3. Check your internet connection")
        print("   4. Ensure you have credits/access for the AI services")
        sys.exit(1)

if __name__ == "__main__":
    main()
