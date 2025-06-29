#!/usr/bin/env python3
"""
Fix Sudoku Clue Rendering
Regenerates all puzzle PNGs with proper visual distinction between clues and empty cells
"""

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class SudokuClueRenderingFixer:
    """Fix Sudoku puzzle rendering to show clues vs empty cells properly"""

    def __init__(self, book_dir):
        self.book_dir = Path(book_dir)
        self.metadata_dir = self.book_dir / "puzzles" / "metadata"
        self.puzzles_dir = self.book_dir / "puzzles" / "puzzles"
        self.fixed_count = 0

    def create_proper_puzzle_image(self, initial_grid, puzzle_id):
        """Create puzzle image with visual distinction between clues and empty cells"""
        cell_size = 60
        margin = 40
        grid_size = 9
        img_size = grid_size * cell_size + 2 * margin

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        # Try multiple font options for better compatibility
        clue_font = None
        normal_font = None
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]

        # Load fonts - use BOLD for clues
        for font_path in font_paths:
            try:
                clue_font = ImageFont.truetype(
                    font_path, 42
                )  # Larger, bold font for clues
                normal_font = ImageFont.truetype(
                    font_path, 36
                )  # Smaller font if needed
                break
            except:
                continue

        if clue_font is None:
            print("Warning: Using default font")
            clue_font = ImageFont.load_default()
            normal_font = clue_font

        # Draw grid lines
        for i in range(grid_size + 1):
            line_width = 3 if i % 3 == 0 else 1

            # Vertical lines
            draw.line(
                [
                    (margin + i * cell_size, margin),
                    (margin + i * cell_size, img_size - margin),
                ],
                fill="black",
                width=line_width,
            )

            # Horizontal lines
            draw.line(
                [
                    (margin, margin + i * cell_size),
                    (img_size - margin, margin + i * cell_size),
                ],
                fill="black",
                width=line_width,
            )

        # Draw ONLY the clues (non-zero values) from initial_grid
        clues_drawn = 0
        for r in range(grid_size):
            for c in range(grid_size):
                value = initial_grid[r][c]
                if value != 0:  # This is a clue
                    text = str(value)

                    # Get text dimensions for proper centering
                    bbox = draw.textbbox((0, 0), text, font=clue_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    # Calculate position to center text in cell
                    x = margin + c * cell_size + (cell_size - text_width) // 2
                    y = margin + r * cell_size + (cell_size - text_height) // 2

                    # Draw the clue in BLACK and BOLD
                    draw.text((x, y), text, fill="black", font=clue_font)
                    clues_drawn += 1
                else:
                    # This is an empty cell - leave it blank
                    # Optionally, draw a very light gray background to indicate it's fillable
                    cell_x = margin + c * cell_size + 1
                    cell_y = margin + r * cell_size + 1
                    cell_x2 = cell_x + cell_size - 2
                    cell_y2 = cell_y + cell_size - 2

                    # Very light gray to show it's an empty cell
                    draw.rectangle([cell_x, cell_y, cell_x2, cell_y2], fill="#FAFAFA")

        # Save with high quality
        output_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}_FIXED.png"
        img.save(output_path, "PNG", dpi=(300, 300), optimize=False)

        print(
            f"✅ Fixed Puzzle {puzzle_id}: {clues_drawn} clues rendered (empty cells left blank)"
        )
        return output_path, clues_drawn

    def fix_all_puzzles(self):
        """Fix all puzzle images to show proper clue rendering"""
        print("🔧 Fixing Sudoku clue rendering...")

        # Get all puzzle metadata files
        metadata_files = sorted(self.metadata_dir.glob("sudoku_puzzle_*.json"))

        if not metadata_files:
            print(f"❌ No puzzle metadata found in {self.metadata_dir}")
            return False

        total_fixed = 0

        for metadata_file in metadata_files:
            puzzle_id = int(metadata_file.stem.split("_")[-1])

            # Load puzzle metadata
            with open(metadata_file, "r") as f:
                puzzle_data = json.load(f)

            initial_grid = puzzle_data.get("initial_grid", [])
            if not initial_grid:
                print(f"❌ No initial_grid data for puzzle {puzzle_id}")
                continue

            # Create properly rendered puzzle
            fixed_path, clues_drawn = self.create_proper_puzzle_image(
                initial_grid, puzzle_id
            )

            # Verify clue count
            expected_clues = puzzle_data.get("clue_count", 0)
            if clues_drawn == expected_clues:
                # Replace original with fixed version
                original_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"
                if original_path.exists():
                    # Backup original
                    backup_path = (
                        self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}_OLD.png"
                    )
                    shutil.move(str(original_path), str(backup_path))

                # Move fixed to original name
                shutil.move(str(fixed_path), str(original_path))
                print(f"✓ Replaced puzzle {puzzle_id} with properly rendered version")
                total_fixed += 1
            else:
                print(
                    f"❌ Puzzle {puzzle_id}: Clue count mismatch ({clues_drawn} vs {expected_clues})"
                )

        print(f"\n📊 Summary: Fixed {total_fixed} puzzles with proper clue rendering")
        print("\n🎯 Next steps:")
        print("1. Regenerate PDF with these new images")
        print("2. Run enhanced QA validation")
        print("3. Verify puzzles are now solvable")

        return total_fixed > 0

    def validate_rendering(self, puzzle_id):
        """Validate that a puzzle image has proper clue rendering"""
        # This would analyze the image to ensure:
        # 1. Clues are visually distinct (darker/bolder)
        # 2. Empty cells are clearly empty
        # 3. Grid lines are visible
        pass


def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_sudoku_clue_rendering.py <book_directory>")
        print(
            "Example: python fix_sudoku_clue_rendering.py books/active_production/Large_Print_Sudoku_Masters/volume_1"
        )
        sys.exit(1)

    book_dir = sys.argv[1]
    fixer = SudokuClueRenderingFixer(book_dir)

    if fixer.fix_all_puzzles():
        print("\n✅ Clue rendering fix complete!")
    else:
        print("\n❌ Fix failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
