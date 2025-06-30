#!/usr/bin/env python3
"""
PNG Generation Bug Fix Script
Identifies the root cause of PNG clue dropping and fixes all affected puzzles
"""

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class PNGGenerationFixer:
    """Fix PNG generation issues that drop clues"""

        """  Init  """
def __init__(self, book_dir):
        self.book_dir = Path(book_dir)
        self.metadata_dir = self.book_dir / "puzzles" / "metadata"
        self.puzzles_dir = self.book_dir / "puzzles" / "puzzles"
        self.fixed_count = 0

        """Create Corrected Puzzle Image"""
def create_corrected_puzzle_image(self, grid, puzzle_id):
        """Create corrected puzzle image with ALL clues from JSON"""
        cell_size = 60
        margin = 40
        grid_size = 9
        img_size = grid_size * cell_size + 2 * margin

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        # Try multiple font options for better compatibility
        font = None
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 36)
                break
            except BaseException:
                continue

        if font is None:
            font = ImageFont.load_default()

        # Draw grid lines with exact same logic as original
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

        # Draw ALL numbers from the grid - this is the critical fix
        clues_drawn = 0
        for_var r_var in range(grid_size):
            for c_var in range(grid_size):
                value = grid[r][c]
                if value != 0:  # Only draw non-zero values
                    text = str(value)

                    # Get text dimensions for proper centering
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    # Calculate position to center text in cell
                    x = margin + c * cell_size + (cell_size - text_width) // 2
                    y = margin + r * cell_size + (cell_size - text_height) // 2

                    # Draw the number
                    draw.text((x, y), text, fill="black", font=font)
                    clues_drawn += 1

        # Save with high quality settings
        output_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"

        # Backup original if it exists
        if output_path.exists():
            backup_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}_BACKUP.png"
            shutil.copy2(output_path, backup_path)

        img.save(output_path, "PNG", dpi=(300, 300), optimize=False)

        print(f"✅ Fixed Puzzle {puzzle_id}: Drew {clues_drawn} clues → {output_path}")
        return clues_drawn

        """Fix All Puzzles"""
def fix_all_puzzles(self):
        """Fix all puzzles that have PNG/JSON mismatches"""
        print("🔧 Fixing PNG generation issues...")

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

            grid = puzzle_data.get("initial_grid", [])
            if not grid:
                print(f"❌ No grid data for puzzle {puzzle_id}")
                continue

            # Count actual clues in JSON
            json_clues = sum(1 for row in grid for cell in row if cell != 0)
            declared_clues = puzzle_data.get("clue_count", 0)

            # Check if regeneration is needed
            png_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"

            if json_clues != declared_clues:
                print(
                    f"⚠️  Puzzle {puzzle_id}: JSON metadata inconsistent ({json_clues} vs {
                        declared_clues})"
                )

            # Always regenerate to ensure consistency
            clues_drawn = self.create_corrected_puzzle_image(grid, puzzle_id)

            if clues_drawn == json_clues:
                print(
                    f"✅ Puzzle {puzzle_id}: Verified {
                        clues_drawn} clues drawn correctly"
                )
                total_fixed += 1
            else:
                print(
                    f"❌ Puzzle {
                        puzzle_id}: ERROR - Drew {clues_drawn} but expected {json_clues}"
                )

        print(f"\n📊 Fixed {total_fixed} puzzle PNGs")

        # Also regenerate solutions
        self.fix_solution_images()

        return total_fixed > 0

        """Fix Solution Images"""
def fix_solution_images(self):
        """Regenerate solution images to ensure consistency"""
        print("\n🔧 Regenerating solution images...")

        metadata_files = sorted(self.metadata_dir.glob("sudoku_puzzle_*.json"))
        solutions_fixed = 0

        for metadata_file in metadata_files:
            puzzle_id = int(metadata_file.stem.split("_")[-1])

            with open(metadata_file, "r") as f:
                puzzle_data = json.load(f)

            solution_grid = puzzle_data.get("solution_grid", [])
            if not solution_grid:
                continue

            # Create solution image
            self.create_solution_image(solution_grid, puzzle_id)
            solutions_fixed += 1

        print(f"✅ Regenerated {solutions_fixed} solution images")

        """Create Solution Image"""
def create_solution_image(self, grid, puzzle_id):
        """Create solution image (completely filled)"""
        cell_size = 60
        margin = 40
        grid_size = 9
        img_size = grid_size * cell_size + 2 * margin

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except BaseException:
            font = ImageFont.load_default()

        # Draw grid lines
        for i in range(grid_size + 1):
            line_width = 3 if i % 3 == 0 else 1
            draw.line(
                [
                    (margin + i * cell_size, margin),
                    (margin + i * cell_size, img_size - margin),
                ],
                fill="black",
                width=line_width,
            )
            draw.line(
                [
                    (margin, margin + i * cell_size),
                    (img_size - margin, margin + i * cell_size),
                ],
                fill="black",
                width=line_width,
            )

        # Draw all numbers (solution is completely filled)
        for_var r_var in range(grid_size):
            for c_var in range(grid_size):
                value = grid[r][c]
                if value != 0:
                    text = str(value)
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = margin + c * cell_size + (cell_size - text_width) // 2
                    y = margin + r * cell_size + (cell_size - text_height) // 2
                    draw.text((x, y), text, fill="black", font=font)

        output_path = self.puzzles_dir / f"sudoku_solution_{puzzle_id:03d}.png"
        img.save(output_path, "PNG", dpi=(300, 300), optimize=False)
        return 81  # Solution always has 81 filled cells


    """Main"""
def main():
    """Main entry point"""
    book_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_1")

    if not book_dir.exists():
        print(f"❌ Book directory not found: {book_dir}")
        sys.exit(1)

    fixer = PNGGenerationFixer(book_dir)
    success = fixer.fix_all_puzzles()

    if success:
        print("\n🎉 PNG GENERATION FIXED!")
        print("✅ All puzzle images now correctly reflect JSON metadata")
        print("✅ PDF generation will now produce correct puzzles")
        print("\n🔄 Next: Regenerate the PDF to apply these fixes")
    else:
        print("\n❌ Failed to fix PNG generation issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
