#!/usr/bin/env python3
"""Analyze puzzle 86 to show clue details"""

import json
from pathlib import Path

# Check puzzle 86
puzzle_file = Path('books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/metadata/sudoku_puzzle_086.json')
with open(puzzle_file) as f:
    data = json.load(f)

grid = data['initial_grid']
clue_count = sum(1 for row in grid for cell in row if cell != 0)

print(f'Puzzle #86 Analysis:')
print(f'Stated clue count: {data["clue_count"]}')
print(f'Actual clue count: {clue_count}')
print(f'Difficulty: {data["difficulty"]}')

# Check for empty rows/columns
empty_rows = [i+1 for i, row in enumerate(grid) if all(cell == 0 for cell in row)]
empty_cols = [j+1 for j in range(9) if all(grid[i][j] == 0 for i in range(9))]

print(f'Empty rows: {empty_rows if empty_rows else "None"}')
print(f'Empty columns: {empty_cols if empty_cols else "None"}')

# Show the grid with clues marked
print('\nPuzzle Grid (0 = empty):')
for i, row in enumerate(grid):
    print(f'Row {i+1}: {" ".join(str(cell) for cell in row)}')

# Count clues in each row/column
print('\nClues per row:')
for i, row in enumerate(grid):
    count = sum(1 for cell in row if cell != 0)
    print(f'  Row {i+1}: {count} clues')

print('\nClues per column:')
for j in range(9):
    count = sum(1 for i in range(9) if grid[i][j] != 0)
    print(f'  Column {j+1}: {count} clues')