#!/usr/bin/env python3
"""
STEALTH MODE: Quick Book Generator
Generate sellable puzzle books FAST - No BS, just revenue
"""

import json
import random
from datetime import datetime
from pathlib import Path

def generate_sudoku_puzzle():
    """Generate a simple valid sudoku puzzle"""
    # Start with a complete valid grid
    base = [
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9]
    ]
    
    # Shuffle rows and columns within bands
    def shuffle_band(grid):
        bands = [0, 3, 6]
        random.shuffle(bands)
        new_grid = []
        for band in bands:
            rows = list(range(band, band + 3))
            random.shuffle(rows)
            for row in rows:
                new_grid.append(grid[row])
        return new_grid
    
    # Create puzzle by removing numbers
    puzzle = shuffle_band(base)
    solution = [row[:] for row in puzzle]
    
    # Remove numbers to create puzzle (40-50 clues for medium)
    cells_to_remove = random.randint(31, 41)
    positions = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(positions)
    
    for i in range(cells_to_remove):
        row, col = positions[i]
        puzzle[row][col] = 0
    
    return puzzle, solution

def generate_book_json(num_puzzles=50):
    """Generate book data in JSON format"""
    puzzles = []
    
    for i in range(num_puzzles):
        puzzle, solution = generate_sudoku_puzzle()
        puzzles.append({
            "id": f"puzzle_{i+1}",
            "difficulty": random.choice(["easy", "medium", "hard"]),
            "puzzle": puzzle,
            "solution": solution
        })
    
    book_data = {
        "title": "Sudoku Masters: Volume 1",
        "subtitle": "50 Brain-Boosting Puzzles for Mental Fitness",
        "author": "KindleMint Publishing",
        "generated_date": datetime.now().isoformat(),
        "puzzles": puzzles
    }
    
    return book_data

def main():
    print("🥷 STEALTH MODE: Generating Revenue-Ready Sudoku Book...")
    
    # Generate book data
    book_data = generate_book_json(50)
    
    # Save to file
    output_dir = Path("../generated/stealth_books")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"sudoku_masters_vol1_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(book_data, f, indent=2)
    
    print(f"✅ Book generated: {filename}")
    print(f"📚 Contains {len(book_data['puzzles'])} puzzles")
    print("\n💰 NEXT STEPS:")
    print("1. Convert to PDF with book_layout_bot.py")
    print("2. Upload to KDP")
    print("3. Start selling!")

if __name__ == "__main__":
    main()