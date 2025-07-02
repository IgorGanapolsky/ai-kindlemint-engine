#!/usr/bin/env python3
"""Emergency check - what images are actually in the PDF"""

import sys

from sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout

sys.path.append(".")


# Load the layout
layout = EnhancedSudokuPDFLayout(
    input_dir="../books/active_production/Large_Print_Sudoku_Masters/volume_2",
    output_dir="test_output",
    title="Test",
    author="Test",
)

# Check what the PDF generator is actually looking for
print("Checking puzzle image paths...")

for i, puzzle_data in enumerate(layout.puzzles[:3]):
    puzzle_num = i + 1

    # Check puzzle path resolution
    puzzles_dir = layout.input_dir
    if not (puzzles_dir / f"sudoku_puzzle_{puzzle_data['id']:03d}.png").exists():
        puzzles_dir = layout.input_dir / "puzzles"
        if not (puzzles_dir / f"sudoku_puzzle_{puzzle_data['id']:03d}.png").exists():
            puzzles_dir = layout.input_dir.parent / "puzzles"

    image_path = puzzles_dir / f"sudoku_puzzle_{puzzle_data['id']:03d}.png"

    print(f"\nPuzzle {puzzle_num}:")
    print(f"  Looking for: {image_path}")
    print(f"  Exists: {image_path.exists()}")
    print(f"  Puzzle ID: {puzzle_data['id']}")
    print(f"  Expected empty cells: {81 - puzzle_data['clue_count']}")
