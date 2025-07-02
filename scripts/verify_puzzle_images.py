#!/usr/bin/env python3
"""
Verify puzzle images have empty cells
"""

import numpy as np
from PIL import Image


def check_puzzle_image(image_path):
    """Check if puzzle image has empty cells"""
    img = Image.open(image_path)
    img_array = np.array(img)

    # Get image dimensions
    height, width = img_array.shape[:2]

    # Sample the center of each cell (9x9 grid)
    cell_size = width // 9
    border = 20  # Approximate border size

    empty_cells = 0
    filled_cells = 0

    for row in range(9):
        for col in range(9):
            # Sample center of cell
            x = border + col * cell_size + cell_size // 2
            y = border + row * cell_size + cell_size // 2

            # Check a small area around the center
            sample_area = img_array[y - 5: y + 5, x - 5: x + 5]

            # If mostly white (>250), it's empty
            avg_color = np.mean(sample_area)

            if avg_color > 250:
                empty_cells += 1
            else:
                filled_cells += 1

    return empty_cells, filled_cells


# Check first puzzle
puzzle_path = "books/active_production/Large_Print_Sudoku_Masters/volume_2/puzzles/sudoku_puzzle_001.png"
solution_path = "books/active_production/Large_Print_Sudoku_Masters/volume_2/puzzles/sudoku_solution_001.png"

print("Checking puzzle image...")
empty, filled = check_puzzle_image(puzzle_path)
print(f"Puzzle: {empty} empty cells, {filled} filled cells")

print("\nChecking solution image...")
empty, filled = check_puzzle_image(solution_path)
print(f"Solution: {empty} empty cells, {filled} filled cells")
