#!/usr/bin/env python3
"""
Volume-specific DALL-E cover prompts for differentiation
Each volume should have a unique color scheme and subtle theme
"""

VOLUME_COVER_PROMPTS = {
    1: {
        "color_scheme": "calming blues and soft whites",
        "theme": "fresh beginnings, morning sky",
        "accent": "light blue gradient",
        "season": "spring-like freshness",
    },
    2: {
        "color_scheme": "warm greens and earth tones",
        "theme": "growth and nature",
        "accent": "sage green gradient",
        "season": "summer vibrancy",
    },
    3: {
        "color_scheme": "gentle oranges and warm yellows",
        "theme": "autumn warmth",
        "accent": "sunset orange gradient",
        "season": "fall comfort",
    },
    4: {
        "color_scheme": "deep purples and royal blues",
        "theme": "wisdom and depth",
        "accent": "amethyst purple gradient",
        "season": "winter elegance",
    },
}


def get_volume_prompt(
    volume_num,
    title="Large Print Crossword Masters",
    format_type="hardcover",
    spine_width=0.415,
):
    """
    Generate a volume-specific DALL-E prompt with unique color scheme
    """
    if volume_num not in VOLUME_COVER_PROMPTS:
        volume_num = 1  # Default to volume 1 style

    style = VOLUME_COVER_PROMPTS[volume_num]

    prompt = f"""Create a professional book cover for "{title} Volume {volume_num}" - a large print crossword puzzle book designed for seniors.

Design specifications:
- Clean, modern design with {style['color_scheme']}
- Theme: {style['theme']}
- Large, bold title text: "{title}" in high-contrast typography
- Prominent "Volume {volume_num}" indicator with {style['accent']} background
- "LARGE PRINT" badge prominently displayed
- Subtle crossword grid pattern in background (light opacity)
- {style['season']} aesthetic
- Professional typography optimized for senior readability
- Minimalist style that prints well
- Dimensions: 8.5 x 11 inches {format_type} book cover
- Leave {spine_width} inches space for spine text
- High contrast between text and background
- Avoid cluttered or busy designs

Style: Professional, clean, accessible, senior-friendly, {style['season']} themed
Output: Print-ready book cover design"""

    return prompt


def get_series_consistency_guide():
    """
    Guidelines for maintaining consistency across the series
    """
    return """
SERIES CONSISTENCY GUIDELINES:

1. Typography:
   - Same font family across all volumes
   - Consistent title placement and size
   - Volume number in same position (recommend top right or bottom)

2. Layout:
   - Identical grid structure
   - Same "LARGE PRINT" badge style and placement
   - Consistent spine text formatting

3. Branding:
   - Series logo or emblem (if applicable)
   - Publisher information in same location
   - Consistent border or frame style

4. Differentiation:
   - ONLY color scheme changes between volumes
   - Subtle seasonal themes
   - Background gradient variations
   - Keep core design elements identical

5. Quality Standards:
   - 300 DPI resolution
   - CMYK color space
   - Print-safe color values
   - Proper bleed margins (0.125")
"""


if __name__ == "__main__":
    # Example usage
    print("DALL-E Cover Prompts for Large Print Crossword Masters Series\n")
    print("=" * 60)

    for volume in range(1, 5):
        print(f"\nVOLUME {volume}:")
        print("-" * 60)
        print(get_volume_prompt(volume))
        print()

    print("\n" + "=" * 60)
    print(get_series_consistency_guide())
