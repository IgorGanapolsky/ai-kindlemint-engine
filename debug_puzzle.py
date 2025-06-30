#!/usr/bin/env python3
import json
from pathlib import Path

# Check what puzzle data looks like and if image exists
puzzle_file = Path('books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/metadata/sudoku_puzzle_001.json')
with open(puzzle_file) as f:
    data = json.load(f)

print('Puzzle data summary:')
print(f'Clue count: {data.get("clue_count", "missing")}')
print(f'Difficulty: {data.get("difficulty", "missing")}')

# Count actual clues in initial_grid
clues = 0
for row in data['initial_grid']:
    for cell in row:
        if cell != 0:
            clues += 1
print(f'Actual clues in grid: {clues}')

# Show first few rows to see the clue pattern
print('\nFirst 3 rows of initial_grid:')
for i, row in enumerate(data['initial_grid'][:3]):
    print(f'Row {i}: {row}')

# Check if corresponding image exists
image_path = Path('books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/puzzles/sudoku_puzzle_001.png')
print(f'\nImage exists: {image_path.exists()}')
print(f'Image path: {image_path}')

# Also check the path that PDF generator would use
pdf_puzzles_dir = Path('books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles') / "puzzles" / "puzzles"
if not pdf_puzzles_dir.exists():
    pdf_puzzles_dir = Path('books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles') / "puzzles"

pdf_image_path = pdf_puzzles_dir / f"sudoku_puzzle_{data['id']:03d}.png"
print(f'PDF would look for: {pdf_image_path}')
print(f'PDF path exists: {pdf_image_path.exists()}')