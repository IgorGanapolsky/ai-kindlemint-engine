#!/usr/bin/env python3
"""
EMERGENCY FIX: Regenerate Volume 2 with proper empty cells in puzzles
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from generate_volume_2_complete import (
    create_volume_2_structure,
    fix_metadata_compliance,
    generate_volume_2_pdf,
    get_solve_time,
    get_solving_techniques,
)
from PIL import Image, ImageDraw, ImageFont
from unified_sudoku_generator import generate_sudoku_with_solution

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))


def create_puzzle_image_fixed(grid, output_path, is_solution=False, initial_grid=None):
    """Create high-quality Sudoku grid image WITH PROPER EMPTY CELLS"""

    # Image settings for large print
    cell_size = 60
    grid_size = cell_size * 9
    border = 20
    img_size = grid_size + (border * 2)

    # Create image
    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)

    # Try to load a nice font, fallback to default
    try:
        font_size = 36
        font = ImageFont.load_default()
        # Try to make it bigger
        try:
            font = ImageFont.truetype("Arial", font_size)
            font_bold = ImageFont.truetype("Arial Bold", font_size)
        except:
            font_bold = font
    except:
        font = ImageFont.load_default()
        font_bold = font

    # Draw grid lines
    for i in range(10):
        line_width = 4 if i % 3 == 0 else 2
        color = "black"

        # Vertical lines
        x = border + i * cell_size
        draw.line([(x, border), (x, border + grid_size)],
                  fill=color, width=line_width)

        # Horizontal lines
        y = border + i * cell_size
        draw.line([(border, y), (border + grid_size, y)],
                  fill=color, width=line_width)

    # CRITICAL FIX: Fill numbers ONLY for non-zero cells
    filled_count = 0
    empty_count = 0

    for row in range(9):
        for col in range(9):
            number = grid[row][col]

            if number != 0:  # ONLY draw if not zero
                filled_count += 1
                x = border + col * cell_size + cell_size // 2
                y = border + row * cell_size + cell_size // 2

                # Choose font based on whether it's a clue or solution
                if is_solution and initial_grid and initial_grid[row][col] == 0:
                    # Solution number - lighter color
                    text_color = "gray"
                    use_font = font
                else:
                    # Clue number - bold and black
                    text_color = "black"
                    use_font = font_bold

                # Draw the number
                text = str(number)
                # Use textbbox for newer PIL versions
                try:
                    bbox = draw.textbbox((0, 0), text, font=use_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    # Fallback for older PIL
                    text_width, text_height = draw.textsize(
                        text, font=use_font)

                text_x = x - text_width // 2
                text_y = y - text_height // 2

                draw.text((text_x, text_y), text,
                          fill=text_color, font=use_font)
            else:
                empty_count += 1

    # Save image
    img.save(output_path, "PNG", quality=95)

    print(
        f"  → Generated {'solution' if is_solution else 'puzzle'} image: {filled_count} filled, {empty_count} empty cells"
    )
    return filled_count, empty_count


def regenerate_all_puzzle_images(base_dir):
    """Regenerate all puzzle images with verification"""

    puzzles_dir = base_dir / "puzzles"
    metadata_dir = base_dir / "metadata"

    print("\n🔧 EMERGENCY FIX: Regenerating all puzzle images...")
    print("=" * 60)

    # Load collection metadata
    with open(metadata_dir / "sudoku_collection.json") as f:
        collection = json.load(f)

    failed_puzzles = []

    for puzzle_id in collection["puzzles"]:
        # Load puzzle metadata
        with open(metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json") as f:
            puzzle_data = json.load(f)

        print(f"\nPuzzle {puzzle_id:03d} ({puzzle_data['difficulty']}):")

        # Generate puzzle image
        puzzle_path = puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"
        filled, empty = create_puzzle_image_fixed(
            puzzle_data["initial_grid"], puzzle_path, is_solution=False
        )

        # Verify puzzle has empty cells
        expected_empty = 81 - puzzle_data["clue_count"]
        if empty != expected_empty:
            print(
                f"  ❌ ERROR: Expected {expected_empty} empty cells, got {empty}")
            failed_puzzles.append(puzzle_id)
        else:
            print(f"  ✅ Verified: {empty} empty cells (correct)")

        # Generate solution image
        solution_path = puzzles_dir / f"sudoku_solution_{puzzle_id:03d}.png"
        create_puzzle_image_fixed(
            puzzle_data["solution_grid"],
            solution_path,
            is_solution=True,
            initial_grid=puzzle_data["initial_grid"],
        )

    return failed_puzzles


if __name__ == "__main__":
    print("🚨 EMERGENCY VOLUME 2 FIX")
    print("Fixing puzzle images to show empty cells...")

    base_dir = Path(
        "../books/active_production/Large_Print_Sudoku_Masters/volume_2")

    # Regenerate all images
    failed = regenerate_all_puzzle_images(base_dir)

    if failed:
        print(f"\n❌ Failed puzzles: {failed}")
        sys.exit(1)

    print("\n✅ All puzzle images regenerated successfully!")

    # Regenerate PDF
    print("\n📚 Regenerating PDF with fixed images...")
    if generate_volume_2_pdf(base_dir):
        print("\n✅ EMERGENCY FIX COMPLETE!")
        print(
            f"Fixed PDF: {base_dir}/paperback/Large_Print_Sudoku_Masters_Volume_2_Interior.pdf"
        )
    else:
        print("\n❌ PDF generation failed")
        sys.exit(1)
