#!/usr/bin/env python3
"""
Add DALL-E cover prompts to all metadata files
"""

import glob
import json
import os


def get_cover_prompt(title: str, series_name: str, book_type: str) -> str:
    """Generate appropriate DALL-E cover prompt based on book details"""

    base_style = (
        "Professional book cover design, clean modern layout, high contrast typography"
    )

    if "Sudoku" in title:
        theme = (
            "sudoku puzzle grids in background, mathematical symbols, number patterns"
        )
        colors = "deep blue and white color scheme with gold accents"
    elif "Crossword" in title:
        theme = "crossword puzzle grids in background, letter tiles, word patterns"
        colors = "elegant green and cream color scheme with silver accents"
    else:
        theme = "puzzle elements, brain training symbols, geometric patterns"
        colors = "professional blue and white color scheme"

    if "Large Print" in title:
        typography = "extra large, bold, easy-to-read fonts, senior-friendly design"
    else:
        typography = "clear, professional typography, modern sans-serif fonts"

    format_spec = f"designed for {book_type} format"

    prompt = f"""Create a {base_style}. Title: '{title}'. Include {theme}. Use {colors}. Feature {typography}. The cover should be {format_spec}, eye-catching for Amazon KDP marketplace, appealing to puzzle enthusiasts and seniors. Include subtle brain/mind imagery to suggest cognitive benefits. Ensure text is highly readable and professional appearance suitable for bookstore shelves."""

    return prompt


def add_cover_prompts():
    """Add cover prompts to all metadata files"""
    base_dir = "/Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine"

    # Find all metadata files
    patterns = [
        "**/books/active_production/**/*metadata*.json",
        "**/books/active_production/**/amazon_kdp_metadata.json",
        "**/books/active_production/**/kindle_metadata.json",
        "**/books/active_production/**/paperback_metadata.json",
    ]

    all_files = set()
    for pattern in patterns:
        files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
        all_files.update(files)

    print(f"Adding cover prompts to {len(all_files)} metadata files...")
    print()

    for file_path in sorted(all_files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Skip if already has cover design
            if "cover_design" in data:
                print(
                    f"✓ Already has cover design: {os.path.relpath(file_path, base_dir)}"
                )
                continue

            # Extract book details
            title = data.get("title", "Puzzle Book")
            series_data = data.get("series", {})
            if isinstance(series_data, dict):
                series_name = series_data.get("name", "Puzzle Series")
            else:
                series_name = str(series_data) if series_data else "Puzzle Series"

            # Determine book type from path
            if "/paperback/" in file_path:
                book_type = "paperback"
            elif "/hardcover/" in file_path:
                book_type = "hardcover"
            elif "/kindle/" in file_path:
                book_type = "kindle ebook"
            else:
                book_type = "book"

            # Generate cover prompt
            dalle_prompt = get_cover_prompt(title, series_name, book_type)

            # Add cover design to metadata
            data["cover_design"] = {
                "dalle_prompt": dalle_prompt,
                "style": "professional puzzle book cover",
                "target_audience": "puzzle enthusiasts, seniors, brain training seekers",
                "format_optimized": book_type,
                "created_date": "2025-06-27",
            }

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✓ Added cover prompt: {os.path.relpath(file_path, base_dir)}")

        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")

    print()
    print("✓ Cover prompts added to all metadata files")


if __name__ == "__main__":
    add_cover_prompts()
