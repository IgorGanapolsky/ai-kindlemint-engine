#!/usr/bin/env python3
"""
Test individual PNG files to see if they have visual distinction
"""

import sys
from pathlib import Path
from io import BytesIO

sys.path.append(str(Path(__file__).parent))

from emergency_visual_validator import EmergencyVisualValidator
from PIL import Image
import numpy as np


def test_png_visual_distinction():
    """Test if individual PNG files have visual distinction."""

    # Test puzzle 100 PNG specifically
    png_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/sudoku_puzzle_100.png"
    )

    if not png_path.exists():
        print(f"❌ PNG not found: {png_path}")
        return False

    print(f"🔍 Testing PNG file: {png_path}")

    # Load the PNG and analyze it
    try:
        img = Image.open(png_path)
        img_gray = np.array(img.convert("L"))

        print(f"📊 Image size: {img_gray.shape}")

        # Check the pixel values to see if there's distinction
        unique_values = np.unique(img_gray)
        print(f"🎨 Unique pixel values: {len(unique_values)} values")
        print(f"   Range: {np.min(img_gray)} to {np.max(img_gray)}")

        # Check for variety in the middle range (not just black/white)
        middle_values = unique_values[(unique_values > 50) & (unique_values < 200)]
        print(f"🔍 Middle-range values (50-200): {len(middle_values)} values")

        if len(middle_values) > 5:
            print("✅ PNG appears to have varied pixel values (good for distinction)")
        else:
            print("❌ PNG appears to have only extreme values (may lack distinction)")

        # Sample a few cell areas
        h, w = img_gray.shape
        cell_size = min(h, w) // 9

        print(f"\n🔍 Sampling cell areas (estimated cell size: {cell_size}px):")

        for r in range(0, 3):  # Sample first 3 rows
            for c in range(0, 3):  # Sample first 3 cols
                y1 = r * cell_size
                y2 = (r + 1) * cell_size
                x1 = c * cell_size
                x2 = (c + 1) * cell_size

                if y2 < h and x2 < w:
                    cell = img_gray[y1:y2, x1:x2]
                    min_val = np.min(cell)
                    max_val = np.max(cell)
                    avg_val = np.mean(cell)

                    print(
                        f"   Cell ({r},{c}): min={min_val}, max={max_val}, avg={avg_val:.1f}"
                    )

        return True

    except Exception as e:
        print(f"❌ Failed to analyze PNG: {e}")
        return False


def test_multiple_pngs():
    """Test multiple PNG files."""
    puzzle_dir = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles"
    )

    test_puzzles = [98, 100]  # The ones the user showed

    for puzzle_id in test_puzzles:
        print(f"\n{'='*50}")
        print(f"🧪 TESTING PUZZLE {puzzle_id} PNG")
        print("=" * 50)

        png_path = puzzle_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"
        test_png_visual_distinction_for_file(png_path)


def test_png_visual_distinction_for_file(png_path):
    """Test visual distinction for a specific PNG file."""
    if not png_path.exists():
        print(f"❌ PNG not found: {png_path}")
        return

    print(f"🔍 Testing: {png_path.name}")

    try:
        img = Image.open(png_path)
        img_gray = np.array(img.convert("L"))

        # Look for patterns that indicate visual distinction
        h, w = img_gray.shape

        # Check if there are cells with light gray backgrounds (empty cells)
        light_gray_pixels = np.sum((img_gray > 240) & (img_gray < 255))
        total_pixels = img_gray.size
        light_gray_ratio = light_gray_pixels / total_pixels

        print(f"   Light gray pixels (240-255): {light_gray_ratio:.3f} ratio")

        # Check for black text (clues)
        black_pixels = np.sum(img_gray < 50)
        black_ratio = black_pixels / total_pixels

        print(f"   Black pixels (<50): {black_ratio:.3f} ratio")

        # Check for pure white (grid lines/background)
        white_pixels = np.sum(img_gray == 255)
        white_ratio = white_pixels / total_pixels

        print(f"   Pure white pixels: {white_ratio:.3f} ratio")

        if light_gray_ratio > 0.1:
            print("✅ Found light gray areas (likely empty cell backgrounds)")
        else:
            print("❌ No light gray areas found (empty cells may not be styled)")

        if black_ratio > 0.05:
            print("✅ Found black text areas (likely clues)")
        else:
            print("❌ Insufficient black text (clues may be missing)")

    except Exception as e:
        print(f"❌ Error analyzing {png_path.name}: {e}")


if __name__ == "__main__":
    print("🧪 TESTING INDIVIDUAL PNG FILES FOR VISUAL DISTINCTION")
    print("=" * 60)

    # Test the specific file first
    success = test_png_visual_distinction()

    if success:
        print("\n" + "=" * 60)
        # Test multiple files
        test_multiple_pngs()

    print("\n" + "=" * 60)
