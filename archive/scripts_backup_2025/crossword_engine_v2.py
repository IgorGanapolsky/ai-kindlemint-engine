#!/usr/bin/env python3
"""
Crossword Engine v2 - Command Line Interface
Generates crossword puzzles for KindleMint Engine
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class CrosswordEngineV2:
    """Generate crossword puzzles with filled grids and black squares"""
    
    def __init__(self, output_dir, puzzle_count=50, difficulty="mixed", grid_size=15, 
                 word_count=None, max_word_length=15):
        """Initialize the crossword generator with configuration"""
        self.grid_size = grid_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.puzzle_count = puzzle_count
        self.difficulty_mode = difficulty
        self.word_count = word_count
        self.max_word_length = max_word_length
        
        # Create puzzles directory structure
        self.puzzles_dir = self.output_dir / "puzzles"
        self.puzzles_dir.mkdir(exist_ok=True)
        
        # Create metadata directory
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
    
    def create_symmetric_pattern(self):
        """Create symmetric black square pattern for crossword"""
        # More realistic crossword pattern
        pattern = []
        
        # Top section
        pattern.extend([(0, 3), (0, 11), (1, 3), (1, 11)])
        pattern.extend([(2, 5), (2, 9), (3, 0), (3, 7)])
        pattern.extend([(4, 1), (4, 13), (5, 2), (5, 12)])
        pattern.extend([(6, 4), (6, 10)])
        
        return pattern
    
    def generate_grid_with_content(self, puzzle_id):
        """Generate a filled 15x15 grid with words"""
        grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Apply black squares
        black_squares = self.create_symmetric_pattern()
        for r, c in black_squares:
            grid[r][c] = '#'
            # Symmetric position
            grid[self.grid_size-1-r][self.grid_size-1-c] = '#'
            
        # Leave white squares empty for users to fill in
        # Grid should only have '#' for black squares and ' ' for empty squares
                    
        return grid
    
    def generate_filled_solution_grid(self, grid, clues):
        """Generate a filled grid with all answers placed"""
        filled_grid = [row[:] for row in grid]  # Copy the grid
        
        # Place across words
        for num, clue_text, answer in clues.get("across", []):
            # Find position for this clue number
            placed = False
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if self._can_place_across(grid, row, col, len(answer)):
                        # Place the word
                        for i, letter in enumerate(answer):
                            filled_grid[row][col + i] = letter
                        placed = True
                        break
                if placed:
                    break
        
        # Place down words
        for num, clue_text, answer in clues.get("down", []):
            placed = False
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if self._can_place_down(grid, row, col, len(answer)):
                        # Check for conflicts with existing letters
                        conflict = False
                        for i, letter in enumerate(answer):
                            if filled_grid[row + i][col] != ' ' and filled_grid[row + i][col] != letter:
                                conflict = True
                                break
                        
                        if not conflict:
                            for i, letter in enumerate(answer):
                                filled_grid[row + i][col] = letter
                            placed = True
                            break
                if placed:
                    break
        
        return filled_grid
    
    def _can_place_across(self, grid, row, col, length):
        """Check if word can be placed horizontally"""
        if col + length > self.grid_size:
            return False
        for i in range(length):
            if grid[row][col + i] == '#':
                return False
        return True
    
    def _can_place_down(self, grid, row, col, length):
        """Check if word can be placed vertically"""
        if row + length > self.grid_size:
            return False
        for i in range(length):
            if grid[row + i][col] == '#':
                return False
        return True
    
    def create_grid_image(self, grid, puzzle_id, is_solution=False, filled_grid=None):
        """Create high-quality grid image"""
        cell_size = 60
        margin = 40
        img_size = self.grid_size * cell_size + 2 * margin
        
        # White background
        img = Image.new('RGB', (img_size, img_size), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()
            number_font = font
            
        # Draw grid
        number = 1
        clue_positions = {}
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = margin + col * cell_size
                y = margin + row * cell_size
                
                if grid[row][col] == '#':
                    # Black square
                    draw.rectangle([x, y, x + cell_size, y + cell_size], fill='black')
                else:
                    # White square with border
                    draw.rectangle([x, y, x + cell_size, y + cell_size], outline='black', width=2)
                    
                    # For solution grids, fill in the letters
                    if is_solution and filled_grid and filled_grid[row][col] != ' ':
                        text = filled_grid[row][col]
                        text_bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        text_x = x + (cell_size - text_width) // 2
                        text_y = y + (cell_size - text_height) // 2
                        draw.text((text_x, text_y), text, fill='black', font=font)
                    
                    # Add number if this starts a word
                    needs_number = False
                    
                    # Check across
                    if (col == 0 or grid[row][col-1] == '#') and col < self.grid_size-1 and grid[row][col+1] != '#':
                        needs_number = True
                        
                    # Check down
                    if (row == 0 or grid[row-1][col] == '#') and row < self.grid_size-1 and grid[row+1][col] != '#':
                        needs_number = True
                        
                    if needs_number and not is_solution:  # Don't add numbers to solution grids
                        draw.text((x + 5, y + 5), str(number), font=number_font, fill='black')
                        clue_positions[(row, col)] = number
                        number += 1
        
        # Save image with appropriate name
        if is_solution:
            img_path = self.puzzles_dir / f"solution_{puzzle_id:02d}.png"
        else:
            img_path = self.puzzles_dir / f"puzzle_{puzzle_id:02d}.png"
        img.save(img_path, 'PNG')
        
        return img_path, clue_positions
    
    def generate_clues(self, puzzle_id, theme, difficulty):
        """Generate appropriate clues based on difficulty"""
        clues = {
            "across": [],
            "down": []
        }
        
        # Sample clues by difficulty
        if difficulty == "EASY":
            sample_across = [
                (1, "Fuzzy fruit", "PEACH"),
                (5, "Morning beverage", "COFFEE"), 
                (8, "Cat's sound", "MEOW"),
                (12, "Bread spread", "BUTTER"),
                (15, "Ocean motion", "WAVE")
            ]
            sample_down = [
                (1, "Dog's foot", "PAW"),
                (2, "Sunshine state", "FLORIDA"),
                (3, "Red flower", "ROSE"),
                (4, "Kitchen appliance", "OVEN"),
                (6, "Sweet treat", "CAKE")
            ]
        elif difficulty == "MEDIUM":
            sample_across = [
                (1, "Shakespeare's theater", "GLOBE"),
                (5, "Italian currency, once", "LIRA"),
                (8, "Nautical greeting", "AHOY"),
                (12, "Greek letter", "OMEGA"),
                (15, "Desert haven", "OASIS")
            ]
            sample_down = [
                (1, "Gatsby's creator", "FITZGERALD"),
                (2, "Paris landmark", "EIFFEL"),
                (3, "Opera solo", "ARIA"),
                (4, "Chess piece", "ROOK"),
                (6, "Mountain chain", "RANGE")
            ]
        else:  # HARD
            sample_across = [
                (1, "Kafka protagonist", "SAMSA"),
                (5, "Quantum particle", "BOSON"),
                (8, "Byzantine art", "MOSAIC"),
                (12, "Philosophy branch", "ETHICS"),
                (15, "Rare earth element", "YTTRIUM")
            ]
            sample_down = [
                (1, "Sartre's philosophy", "EXISTENTIALISM"),
                (2, "Mathematical constant", "EULER"),
                (3, "Literary device", "METAPHOR"),
                (4, "Economic theory", "KEYNESIAN"),
                (6, "Ancient script", "CUNEIFORM")
            ]
            
        # Extend clues to fill puzzle
        for i in range(20):  # More clues per puzzle
            if i < len(sample_across):
                clues["across"].append(sample_across[i])
            if i < len(sample_down):
                clues["down"].append(sample_down[i])
                
        return clues
    
    def generate_puzzles(self):
        """Generate the specified number of crossword puzzles"""
        print(f"🔤 CROSSWORD ENGINE V2 - Generating {self.puzzle_count} puzzles")
        print(f"📁 Output directory: {self.puzzles_dir}")
        
        puzzles_data = []
        
        # Generate themes based on difficulty mode
        themes = self._generate_themes()
        
        for i in range(self.puzzle_count):
            puzzle_id = i + 1
            
            # Determine difficulty based on mode
            difficulty = self._get_difficulty_for_puzzle(puzzle_id)
            
            theme = themes[i % len(themes)]
            
            print(f"  Creating puzzle {puzzle_id}/{self.puzzle_count}: {theme} ({difficulty})")
            
            # Generate grid with actual content
            grid = self.generate_grid_with_content(puzzle_id)
            
            # Create grid image
            grid_path, clue_positions = self.create_grid_image(grid, puzzle_id)
            
            # Generate clues
            clues = self.generate_clues(puzzle_id, theme, difficulty)
            
            # Generate filled solution grid
            filled_grid = self.generate_filled_solution_grid(grid, clues)
            
            # Create solution image
            solution_path, _ = self.create_grid_image(grid, puzzle_id, is_solution=True, filled_grid=filled_grid)
            
            # Store puzzle data
            puzzle_data = {
                "id": puzzle_id,
                "theme": theme,
                "difficulty": difficulty,
                # Embed grid pattern for domain validation: '#' for black, ' ' for white
                "grid_pattern": grid,
                "grid_path": str(grid_path),
                "solution_path": str(solution_path),
                "solution_grid": filled_grid,  # Store the filled solution
                "clues": clues,
                "clue_positions": {f"{r},{c}": num for (r, c), num in clue_positions.items()},
                "word_count": {
                    "across": len(clues.get("across", [])),
                    "down": len(clues.get("down", [])),
                    "total": len(clues.get("across", [])) + len(clues.get("down", []))
                }
            }
            
            # Save individual puzzle metadata
            puzzle_meta_path = self.metadata_dir / f"puzzle_{puzzle_id:02d}.json"
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
        
        with open(self.metadata_dir / "collection.json", 'w') as f:
            json.dump(collection_meta, f, indent=2)
        
        print(f"✅ Generated {self.puzzle_count} crossword puzzles")
        print(f"📊 Metadata saved to {self.metadata_dir}")
        
        return puzzles_data
    
    def _generate_themes(self):
        """Generate themes based on difficulty mode"""
        themes = [
            # Easy themes
            "Garden Flowers", "Kitchen Tools", "Family Time", "Weather",
            "Colors", "Fruits", "Birds", "Pets", "Seasons", "Numbers",
            "Body Parts", "Clothing", "Breakfast", "Rooms", "Tools",
            "Trees", "Ocean", "Farm", "Music", "Sports",
            
            # Medium themes
            "Classic Movies", "Famous Authors", "World Capitals", "Cooking",
            "Card Games", "Dance", "Gems", "Desserts", "Travel", "Hobbies",
            "Classic Songs", "Wine", "Antiques", "Board Games", "Art",
            "Opera", "Cars", "Radio Shows", "History", "Architecture",
            
            # Hard themes
            "Literature", "Science", "Geography", "Classical Music",
            "Art History", "Cuisine", "Philosophy", "Astronomy",
            "Medicine", "Technology"
        ]
        
        # If we have fewer themes than puzzles, repeat themes
        if len(themes) < self.puzzle_count:
            themes = themes * (self.puzzle_count // len(themes) + 1)
        
        # Shuffle themes if mixed difficulty
        if self.difficulty_mode.lower() == "mixed":
            random.shuffle(themes)
        
        return themes[:self.puzzle_count]
    
    def _get_difficulty_for_puzzle(self, puzzle_id):
        """Determine difficulty for a puzzle based on mode and ID"""
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
    """Main entry point for crossword engine"""
    parser = argparse.ArgumentParser(description='Crossword Engine v2 - Generate crossword puzzles')
    parser.add_argument('--output', required=True, help='Output directory for puzzles')
    parser.add_argument('--count', type=int, default=50, help='Number of puzzles to generate')
    parser.add_argument('--difficulty', default='mixed', 
                        choices=['easy', 'medium', 'hard', 'mixed'],
                        help='Difficulty level for puzzles')
    parser.add_argument('--grid-size', type=int, default=15, help='Grid size (default: 15x15)')
    parser.add_argument('--word-count', type=int, help='Words per puzzle (optional)')
    parser.add_argument('--max-word-length', type=int, default=15, 
                        help='Maximum word length (default: 15)')
    
    args = parser.parse_args()
    
    try:
        engine = CrosswordEngineV2(
            output_dir=args.output,
            puzzle_count=args.count,
            difficulty=args.difficulty,
            grid_size=args.grid_size,
            word_count=args.word_count,
            max_word_length=args.max_word_length
        )
        
        puzzles = engine.generate_puzzles()
        
        print(f"\n🎯 CROSSWORD ENGINE V2 - SUCCESS")
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
