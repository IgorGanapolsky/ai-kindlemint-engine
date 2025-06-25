#!/usr/bin/env python3
"""
Sudoku Generator - Command Line Interface
Generates Sudoku puzzles for KindleMint Engine
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class SudokuGenerator:
    """Generate Sudoku puzzles with configurable difficulty."""
    
    def __init__(self, output_dir, puzzle_count=50, difficulty="mixed", grid_size=9):
        """Initialize the Sudoku generator with configuration."""
        self.grid_size = grid_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.puzzle_count = puzzle_count
        self.difficulty_mode = difficulty
        
        # Create puzzles directory structure
        self.puzzles_dir = self.output_dir / "puzzles"
        self.puzzles_dir.mkdir(exist_ok=True)
        
        # Create metadata directory
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
    
    def _generate_empty_grid(self):
        """Generates an empty 9x9 Sudoku grid."""
        return [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def _fill_grid_with_difficulty(self, grid, difficulty):
        """
        Fills a Sudoku grid with a certain number of pre-filled cells
        based on difficulty. (Placeholder for actual Sudoku generation logic)
        """
        # Simple placeholder: fill a certain number of cells randomly
        # A real Sudoku generator would ensure solvability and unique solutions.
        num_prefilled = 0
        if difficulty == "easy":
            num_prefilled = random.randint(35, 45)
        elif difficulty == "medium":
            num_prefilled = random.randint(25, 34)
        elif difficulty == "hard":
            num_prefilled = random.randint(17, 24)
        else: # mixed
            num_prefilled = random.randint(20, 40)

        filled_cells = 0
        while filled_cells < num_prefilled:
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)
            if grid[row][col] == 0:
                grid[row][col] = random.randint(1, 9) # Placeholder value
                filled_cells += 1
        return grid

    def create_grid_image(self, grid, puzzle_id):
        """Create high-quality Sudoku grid image."""
        cell_size = 60
        margin = 40
        img_size = self.grid_size * cell_size + 2 * margin
        
        img = Image.new('RGB', (img_size, img_size), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            font = ImageFont.load_default()
            
        # Draw grid lines
        for i in range(self.grid_size + 1):
            line_width = 3 if i % 3 == 0 else 1
            draw.line([(margin + i * cell_size, margin), (margin + i * cell_size, img_size - margin)], fill='black', width=line_width)
            draw.line([(margin, margin + i * cell_size), (img_size - margin, margin + i * cell_size)], fill='black', width=line_width)
            
        # Draw numbers
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                value = grid[r][c]
                if value != 0:
                    text = str(value)
                    text_width, text_height = draw.textsize(text, font=font)
                    x = margin + c * cell_size + (cell_size - text_width) / 2
                    y = margin + r * cell_size + (cell_size - text_height) / 2
                    draw.text((x, y), text, fill='black', font=font)
        
        img_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:02d}.png"
        img.save(img_path, 'PNG')
        
        return img_path
        
    def generate_puzzles(self):
        """Generate the specified number of Sudoku puzzles."""
        print(f"🔢 SUDOKU GENERATOR - Generating {self.puzzle_count} puzzles")
        print(f"📁 Output directory: {self.puzzles_dir}")
        
        puzzles_data = []
        
        for i in range(self.puzzle_count):
            puzzle_id = i + 1
            
            # Determine difficulty for this puzzle
            difficulty = self._get_difficulty_for_puzzle(puzzle_id)
            
            print(f"  Creating puzzle {puzzle_id}/{self.puzzle_count} ({difficulty})")
            
            grid = self._generate_empty_grid()
            grid = self._fill_grid_with_difficulty(grid, difficulty)
            
            grid_path = self.create_grid_image(grid, puzzle_id)
            
            # Store puzzle data
            puzzle_data = {
                "id": puzzle_id,
                "difficulty": difficulty,
                "grid_path": str(grid_path),
                "initial_grid": grid, # Store the initial grid state
                "solution_grid": grid # Placeholder for actual solution
            }
            
            # Save individual puzzle metadata
            puzzle_meta_path = self.metadata_dir / f"sudoku_puzzle_{puzzle_id:02d}.json"
            with open(puzzle_meta_path, 'w') as f:
                json.dump(puzzle_data, f, indent=2)
            
            puzzles_data.append(puzzle_data)
        
        # Save full puzzle collection metadata
        collection_meta = {
            "puzzle_count": self.puzzle_count,
            "difficulty_mode": self.difficulty_mode,
            "grid_size": self.grid_size,
            "generation_date": datetime.now().isoformat(),
            "puzzles": [p["id"] for p in puzzles_data]
        }
        
        with open(self.metadata_dir / "sudoku_collection.json", 'w') as f:
            json.dump(collection_meta, f, indent=2)
        
        print(f"✅ Generated {self.puzzle_count} Sudoku puzzles")
        print(f"📊 Metadata saved to {self.metadata_dir}")
        
        return puzzles_data
    
    def _get_difficulty_for_puzzle(self, puzzle_id):
        """Determine difficulty for a puzzle based on mode and ID."""
        mode = self.difficulty_mode.lower()
        
        if mode == "easy":
            return "EASY"
        elif mode == "medium":
            return "MEDIUM"
        elif mode == "hard":
            return "HARD"
        else:  # mixed or progressive
            # Progressive difficulty: 40% easy, 40% medium, 20% hard
            if puzzle_id <= int(self.puzzle_count * 0.4):
                return "EASY"
            elif puzzle_id <= int(self.puzzle_count * 0.8):
                return "MEDIUM"
            else:
                return "HARD"

def main():
    """Main entry point for Sudoku generator."""
    parser = argparse.ArgumentParser(description='Sudoku Generator - Generate Sudoku puzzles')
    parser.add_argument('--output', required=True, help='Output directory for puzzles')
    parser.add_argument('--count', type=int, default=50, help='Number of puzzles to generate')
    parser.add_argument('--difficulty', default='mixed', 
                        choices=['easy', 'medium', 'hard', 'mixed'],
                        help='Difficulty level for puzzles')
    parser.add_argument('--grid-size', type=int, default=9, help='Grid size (default: 9x9)')
    
    args = parser.parse_args()
    
    try:
        generator = SudokuGenerator(
            output_dir=args.output,
            puzzle_count=args.count,
            difficulty=args.difficulty,
            grid_size=args.grid_size
        )
        
        puzzles = generator.generate_puzzles()
        
        print(f"\n🎯 SUDOKU GENERATOR - SUCCESS")
        print(f"📊 Generated {len(puzzles)} puzzles")
        print(f"📁 Output directory: {args.output}")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
