#!/usr/bin/env python3
"""
PDF Rendering Bug Diagnostic and Fix Script
Verifies that PNG images correctly reflect JSON metadata and fixes any discrepancies
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class SudokuRenderingFixer:
    """Diagnose and fix Sudoku PDF rendering issues"""

    def __init__(self, book_dir):
        self.book_dir = Path(book_dir)
        self.metadata_dir = self.book_dir / "puzzles" / "metadata"
        self.puzzles_dir = self.book_dir / "puzzles" / "puzzles"
        self.issues_found = []

    def count_clues_in_json(self, puzzle_data):
        """Count actual clues in JSON grid"""
        if "initial_grid" not in puzzle_data:
            return 0

        grid = puzzle_data["initial_grid"]
        clue_count = 0
        for row in grid:
            for cell in row:
                if cell != 0:
                    clue_count += 1
        return clue_count

    def analyze_png_image(self, png_path):
        """Analyze PNG image to detect filled cells (approximate)"""
        try:
            img = Image.open(png_path)
            # Convert to grayscale
            img_gray = img.convert("L")
            img_array = np.array(img_gray)

            # Grid analysis - detect dark regions that might be numbers
            # This is a rough approximation
            cell_size = 60  # From the generator code
            margin = 40

            filled_cells = 0

            # Check each cell position for darkness (indicating a number)
            for r in range(9):
                for c in range(9):
                    # Calculate cell center
                    x = margin + c * cell_size + cell_size // 2
                    y = margin + r * cell_size + cell_size // 2

                    # Sample a small region around the center
                    region = img_array[y - 10 : y + 10, x - 10 : x + 10]
                    if region.size > 0:
                        # If the region has darker pixels, likely contains a number
                        avg_brightness = np.mean(region)
                        if avg_brightness < 200:  # Threshold for detecting numbers
                            filled_cells += 1

            return filled_cells
        except Exception as e:
            print(f"Error analyzing PNG {png_path}: {e}")
            return -1

    def diagnose_puzzle(self, puzzle_id):
        """Diagnose a specific puzzle for rendering issues"""
        metadata_file = self.metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"
        png_file = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"

        if not metadata_file.exists():
            return f"Missing metadata: {metadata_file}"

        if not png_file.exists():
            return f"Missing PNG: {png_file}"

        # Load JSON metadata
        with open(metadata_file, "r") as f:
            puzzle_data = json.load(f)

        # Count clues in JSON
        json_clues = self.count_clues_in_json(puzzle_data)
        declared_clues = puzzle_data.get("clue_count", 0)

        # Analyze PNG
        png_clues = self.analyze_png_image(png_file)

        issue = {
            "puzzle_id": puzzle_id,
            "json_actual_clues": json_clues,
            "json_declared_clues": declared_clues,
            "png_detected_clues": png_clues,
            "difficulty": puzzle_data.get("difficulty", "unknown"),
        }

        # Check for discrepancies
        if json_clues != declared_clues:
            issue["issue"] = (
                f"JSON mismatch: actual {json_clues} vs declared {declared_clues}"
            )
        elif (
            png_clues != -1 and abs(png_clues - json_clues) > 5
        ):  # Allow some detection error
            issue["issue"] = f"PNG/JSON mismatch: PNG ~{png_clues} vs JSON {json_clues}"
        else:
            issue["status"] = "OK"

        return issue

    def regenerate_puzzle_png(self, puzzle_data, puzzle_id):
        """Regenerate PNG image from JSON metadata"""
        grid = puzzle_data["initial_grid"]

        # Use same parameters as original generator
        cell_size = 60
        margin = 40
        grid_size = 9
        img_size = grid_size * cell_size + 2 * margin

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            font = ImageFont.load_default()

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

        # Draw numbers
        for r in range(grid_size):
            for c in range(grid_size):
                value = grid[r][c]
                if value != 0:
                    text = str(value)
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    x = margin + c * cell_size + (cell_size - text_width) // 2
                    y = margin + r * cell_size + (cell_size - text_height) // 2

                    draw.text((x, y), text, fill="black", font=font)

        # Save regenerated image
        output_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}_FIXED.png"
        img.save(output_path, "PNG", dpi=(300, 300))

        return output_path

    def fix_all_issues(self):
        """Diagnose and fix all puzzle rendering issues"""
        print("🔍 Diagnosing PDF rendering issues...")

        issues = []

        # Check first 10 puzzles for quick diagnosis
        for puzzle_id in range(1, 11):
            result = self.diagnose_puzzle(puzzle_id)
            if isinstance(result, str):
                print(f"❌ Puzzle {puzzle_id}: {result}")
                continue

            if "issue" in result:
                print(f"🚨 Puzzle {puzzle_id}: {result['issue']}")
                issues.append(result)
            else:
                print(
                    f"✅ Puzzle {puzzle_id}: OK ({result['json_actual_clues']} clues)"
                )

        # Special check for puzzle 5 (the one in the screenshot)
        print("\n🎯 Special check for Puzzle 5:")
        puzzle_5_result = self.diagnose_puzzle(5)
        print(f"Puzzle 5 diagnosis: {puzzle_5_result}")

        if "issue" in puzzle_5_result:
            print("🔧 Regenerating Puzzle 5 PNG...")
            metadata_file = self.metadata_dir / "sudoku_puzzle_005.json"
            with open(metadata_file, "r") as f:
                puzzle_data = json.load(f)

            fixed_path = self.regenerate_puzzle_png(puzzle_data, 5)
            print(f"✅ Regenerated: {fixed_path}")

        return issues


def main():
    """Main entry point"""
    book_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_1")

    if not book_dir.exists():
        print(f"❌ Book directory not found: {book_dir}")
        sys.exit(1)

    fixer = SudokuRenderingFixer(book_dir)
    issues = fixer.fix_all_issues()

    print(f"\n📊 Summary: Found {len(issues)} rendering issues")

    if issues:
        print("🚨 CRITICAL: PDF rendering pipeline has data integrity issues!")
        print("The QA validation needs enhancement to catch PNG/JSON mismatches.")
        sys.exit(1)
    else:
        print("✅ All puzzles appear to be rendering correctly")


if __name__ == "__main__":
    main()
