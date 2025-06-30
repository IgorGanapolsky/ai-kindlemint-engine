#!/usr/bin/env python3
import json
from pathlib import Path

# Test if PDF generator can find the image properly
input_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles")

# Load first puzzle
puzzle_file = input_dir / "metadata" / "sudoku_puzzle_001.json"
with open(puzzle_file) as f:
    puzzle_data = json.load(f)

print(f"Input dir: {input_dir}")
print(f"Puzzle ID: {puzzle_data['id']}")

# Replicate the PDF generator's logic for finding images
puzzles_dir = input_dir / "puzzles" / "puzzles"
if not puzzles_dir.exists():
    puzzles_dir = input_dir / "puzzles"

image_path = puzzles_dir / f"sudoku_puzzle_{puzzle_data['id']:03d}.png"

print(f"PDF generator would look in: {puzzles_dir}")
print(f"PDF generator would try: {image_path}")
print(f"Directory exists: {puzzles_dir.exists()}")
print(f"Image exists: {image_path.exists()}")

if image_path.exists():
    print("✅ PDF generator SHOULD find the image")
else:
    print("❌ PDF generator will fall back to create_puzzle_grid")
    
# Check what's in the puzzles directory
print(f"\nContents of {puzzles_dir}:")
if puzzles_dir.exists():
    for item in sorted(puzzles_dir.iterdir())[:5]:  # Show first 5 files
        print(f"  {item.name}")