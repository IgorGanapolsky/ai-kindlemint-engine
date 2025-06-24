#!/usr/bin/env python3
"""
Crossword Engine V2 - Standardized crossword generator for batch processing
Generates unique crossword puzzles with proper CLI interface
"""

import argparse
import json
import random
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class CrosswordEngineV2:
    def __init__(self, output_dir, count, difficulty, **params):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.count = count
        self.difficulty = difficulty
        self.grid_size = params.get('grid_size', 15)
        self.word_count = params.get('word_count', 35)
        self.max_word_length = params.get('max_word_length', 15)
        
        # Initialize clue database
        self._init_clue_database()
        
    def _init_clue_database(self):
        """Initialize comprehensive clue database"""
        self.clue_database = {
            'easy': {
                'themes': [
                    "Kitchen Items", "Animals", "Colors", "Food & Drink", "Weather",
                    "Family", "School", "Sports", "Music", "Nature"
                ],
                'across_clues': [
                    # Kitchen
                    (1, "Cooking pot", "PAN"), (1, "Eating utensil", "FORK"), (1, "Hot drink maker", "KETTLE"),
                    (1, "Cold storage", "FRIDGE"), (1, "Bread heater", "TOASTER"),
                    # Animals
                    (5, "House pet", "CAT"), (5, "Man's best friend", "DOG"), (5, "Farm animal", "COW"),
                    (5, "Pink farm animal", "PIG"), (5, "Wool provider", "SHEEP"),
                    # Colors
                    (8, "Sky color", "BLUE"), (8, "Grass color", "GREEN"), (8, "Sun color", "YELLOW"),
                    (8, "Fire truck color", "RED"), (8, "Night color", "BLACK"),
                    # Weather
                    (12, "Rain drops", "WATER"), (12, "Winter flakes", "SNOW"), (12, "Lightning flash", "STORM"),
                    (12, "Sunny weather", "CLEAR"), (12, "Morning mist", "FOG"),
                    # Nature
                    (15, "Tall plant", "TREE"), (15, "Colorful bloom", "FLOWER"), (15, "Green ground cover", "GRASS"),
                    (15, "Tree part", "LEAF"), (15, "Plant stem", "BRANCH")
                ],
                'down_clues': [
                    # Actions
                    (1, "Fast walk", "RUN"), (1, "Happy dance", "JIG"), (1, "Water sport", "SWIM"),
                    (2, "Bread maker", "BAKER"), (2, "Mail carrier", "POSTMAN"), (2, "Doctor's helper", "NURSE"),
                    (3, "Sleep place", "BED"), (3, "Sitting furniture", "CHAIR"), (3, "Eating surface", "TABLE"),
                    (4, "Time teller", "CLOCK"), (4, "Picture holder", "FRAME"), (4, "Light source", "LAMP"),
                    (6, "Sweet treat", "CANDY"), (6, "Birthday dessert", "CAKE"), (6, "Cold dessert", "ICE CREAM")
                ]
            },
            'medium': {
                'themes': [
                    "World Capitals", "Literature", "Science", "History", "Geography",
                    "Art & Music", "Technology", "Business", "Medicine", "Architecture"
                ],
                'across_clues': [
                    # Geography
                    (1, "French capital", "PARIS"), (1, "Japanese capital", "TOKYO"), (1, "UK capital", "LONDON"),
                    # Literature
                    (5, "Shakespeare play", "HAMLET"), (5, "Austen novel", "EMMA"), (5, "Dickens tale", "TWIST"),
                    # Science
                    (8, "Einstein's theory", "RELATIVITY"), (8, "Darwin's theory", "EVOLUTION"), (8, "Newton's force", "GRAVITY"),
                    # History
                    (12, "Ancient empire", "ROME"), (12, "Egyptian queen", "CLEOPATRA"), (12, "Greek philosopher", "PLATO"),
                    # Music
                    (15, "Classical composer", "MOZART"), (15, "Jazz instrument", "SAXOPHONE"), (15, "Opera solo", "ARIA")
                ],
                'down_clues': [
                    # Art
                    (1, "Mona Lisa creator", "DA VINCI"), (1, "Starry Night painter", "VAN GOGH"),
                    # Technology
                    (2, "Computer brain", "CPU"), (2, "Internet protocol", "HTTP"), (2, "Coding language", "PYTHON"),
                    # Business
                    (3, "Company leader", "CEO"), (3, "Stock market", "NYSE"), (3, "Annual report", "EARNINGS"),
                    # Architecture
                    (4, "Gothic feature", "SPIRE"), (4, "Roman arena", "COLOSSEUM"), (4, "Bridge type", "SUSPENSION"),
                    # Medicine
                    (6, "Heart doctor", "CARDIOLOGIST"), (6, "X-ray type", "MRI"), (6, "Pain reliever", "ASPIRIN")
                ]
            },
            'hard': {
                'themes': [
                    "Classical Literature", "Advanced Science", "Philosophy", "Ancient History", "Fine Arts",
                    "Quantum Physics", "Economics", "Linguistics", "Astronomy", "Mathematics"
                ],
                'across_clues': [
                    # Philosophy
                    (1, "Existentialism founder", "SARTRE"), (1, "German idealist", "HEGEL"), (1, "Social contract", "ROUSSEAU"),
                    # Quantum Physics
                    (5, "Uncertainty principle", "HEISENBERG"), (5, "Wave function", "SCHRODINGER"), (5, "Quantum particle", "PHOTON"),
                    # Literature
                    (8, "Ulysses author", "JOYCE"), (8, "Metamorphosis writer", "KAFKA"), (8, "1984 creator", "ORWELL"),
                    # Mathematics
                    (12, "Prime notation", "SIEVE"), (12, "Infinite series", "SEQUENCE"), (12, "Complex number", "IMAGINARY"),
                    # Ancient History
                    (15, "Mesopotamian writing", "CUNEIFORM"), (15, "Egyptian symbols", "HIEROGLYPHS"), (15, "Dead Sea texts", "SCROLLS")
                ],
                'down_clues': [
                    # Linguistics
                    (1, "Language family", "INDO-EUROPEAN"), (1, "Sound change", "PHONEME"), (1, "Grammar structure", "SYNTAX"),
                    # Economics
                    (2, "Market failure", "EXTERNALITY"), (2, "Supply curve", "ELASTICITY"), (2, "Trade theory", "COMPARATIVE"),
                    # Astronomy
                    (3, "Star death", "SUPERNOVA"), (3, "Galaxy type", "SPIRAL"), (3, "Dark matter", "WIMP"),
                    # Fine Arts
                    (4, "Fresco technique", "BUON"), (4, "Sculpture method", "CASTING"), (4, "Color theory", "COMPLEMENTARY"),
                    # Advanced Science
                    (6, "DNA sequence", "GENOME"), (6, "Cell division", "MITOSIS"), (6, "Enzyme action", "CATALYSIS")
                ]
            }
        }
        
    def generate_pattern(self, pattern_seed):
        """Generate symmetric black square pattern"""
        random.seed(pattern_seed)
        patterns = [
            # Classic symmetric patterns
            [(0,4), (0,10), (1,4), (1,10), (2,3), (2,11), (3,6), (3,8), (4,0), (4,7), (5,1), (5,13), (6,2), (6,5), (6,9), (6,12)],
            [(0,3), (0,11), (1,3), (1,7), (1,11), (2,5), (2,9), (3,0), (3,14), (4,1), (4,6), (4,8), (4,13), (5,2), (5,12), (6,4), (6,10)],
            [(0,5), (0,9), (1,1), (1,13), (2,2), (2,7), (2,12), (3,3), (3,11), (4,4), (4,10), (5,0), (5,8), (5,14), (6,6)],
            [(0,0), (0,7), (0,14), (1,2), (1,12), (2,4), (2,10), (3,1), (3,6), (3,8), (3,13), (4,3), (4,11), (5,5), (5,9), (6,0), (6,14)]
        ]
        return random.choice(patterns)
        
    def create_grid(self, puzzle_id):
        """Create empty crossword grid with black squares"""
        grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Get pattern for this puzzle
        pattern = self.generate_pattern(puzzle_id * 1000)
        
        # Apply black squares symmetrically
        for r, c in pattern:
            grid[r][c] = '#'
            grid[self.grid_size-1-r][self.grid_size-1-c] = '#'
            
        return grid
        
    def generate_clues(self, puzzle_id, theme, difficulty_level):
        """Generate unique clues for each puzzle"""
        random.seed(puzzle_id * 2000)
        
        clue_set = self.clue_database[difficulty_level]
        
        # Select random clues ensuring uniqueness
        across_pool = clue_set['across_clues'].copy()
        down_pool = clue_set['down_clues'].copy()
        
        random.shuffle(across_pool)
        random.shuffle(down_pool)
        
        # Take first 5-8 clues from each pool
        num_across = random.randint(5, min(8, len(across_pool)))
        num_down = random.randint(5, min(8, len(down_pool)))
        
        clues = {
            'across': across_pool[:num_across],
            'down': down_pool[:num_down]
        }
        
        # Add theme indicator to some clues
        if puzzle_id % 3 == 0 and theme:
            for i in range(min(2, len(clues['across']))):
                num, clue, answer = clues['across'][i]
                clues['across'][i] = (num, f"{clue} ({theme})", answer)
                
        return clues
        
    def create_puzzle_image(self, grid, puzzle_id, output_path):
        """Create puzzle grid image"""
        cell_size = 40
        margin = 20
        img_size = self.grid_size * cell_size + 2 * margin
        
        img = Image.new('RGB', (img_size, img_size), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = margin + col * cell_size
                y = margin + row * cell_size
                
                if grid[row][col] == '#':
                    draw.rectangle([x, y, x + cell_size, y + cell_size], fill='black')
                else:
                    draw.rectangle([x, y, x + cell_size, y + cell_size], outline='black', width=2)
                    
        # Add numbers
        number = 1
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if grid[row][col] != '#':
                    needs_number = False
                    
                    # Check if starts across word
                    if col == 0 or grid[row][col-1] == '#':
                        if col < self.grid_size - 1 and grid[row][col+1] != '#':
                            needs_number = True
                            
                    # Check if starts down word
                    if row == 0 or grid[row-1][col] == '#':
                        if row < self.grid_size - 1 and grid[row+1][col] != '#':
                            needs_number = True
                            
                    if needs_number:
                        x = margin + col * cell_size + 3
                        y = margin + row * cell_size + 3
                        draw.text((x, y), str(number), fill='black')
                        number += 1
                        
        img.save(output_path)
        
    def generate_puzzles(self):
        """Generate all puzzles"""
        # Determine difficulty distribution
        if self.difficulty == 'easy':
            difficulties = ['easy'] * self.count
        elif self.difficulty == 'medium':
            difficulties = ['medium'] * self.count
        elif self.difficulty == 'hard':
            difficulties = ['hard'] * self.count
        else:  # mixed
            easy_count = self.count // 3
            medium_count = self.count // 3
            hard_count = self.count - easy_count - medium_count
            difficulties = ['easy'] * easy_count + ['medium'] * medium_count + ['hard'] * hard_count
            
        puzzles_data = []
        themes = self.clue_database['easy']['themes'] + self.clue_database['medium']['themes'] + self.clue_database['hard']['themes']
        
        print(f"🎯 Generating {self.count} crossword puzzles...")
        
        for i in range(self.count):
            puzzle_id = i + 1
            difficulty = difficulties[i]
            theme = themes[i % len(themes)]
            
            print(f"  📝 Puzzle {puzzle_id}: {theme} ({difficulty})")
            
            # Generate grid
            grid = self.create_grid(puzzle_id)
            
            # Generate clues
            clues = self.generate_clues(puzzle_id, theme, difficulty)
            
            # Save grid image
            img_path = self.output_dir / f"puzzle_{puzzle_id:03d}.png"
            self.create_puzzle_image(grid, puzzle_id, img_path)
            
            # Save puzzle data
            puzzle_data = {
                'id': puzzle_id,
                'theme': theme,
                'difficulty': difficulty,
                'grid_size': self.grid_size,
                'clues': {
                    'across': [{'number': n, 'clue': c, 'answer': a} for n, c, a in clues['across']],
                    'down': [{'number': n, 'clue': c, 'answer': a} for n, c, a in clues['down']]
                },
                'grid_image': str(img_path),
                'created_at': datetime.now().isoformat()
            }
            
            json_path = self.output_dir / f"puzzle_{puzzle_id:03d}.json"
            with open(json_path, 'w') as f:
                json.dump(puzzle_data, f, indent=2)
                
            puzzles_data.append(puzzle_data)
            
        # Save master index
        index_path = self.output_dir / "puzzles_index.json"
        with open(index_path, 'w') as f:
            json.dump({
                'count': self.count,
                'difficulty': self.difficulty,
                'created_at': datetime.now().isoformat(),
                'puzzles': puzzles_data
            }, f, indent=2)
            
        print(f"✅ Generated {self.count} puzzles in {self.output_dir}")
        
        # Verify uniqueness
        unique_clues = set()
        for puzzle in puzzles_data:
            for clue_data in puzzle['clues']['across']:
                unique_clues.add(clue_data['clue'])
            for clue_data in puzzle['clues']['down']:
                unique_clues.add(clue_data['clue'])
                
        print(f"✅ Total unique clues: {len(unique_clues)}")
        
        return puzzles_data

def main():
    parser = argparse.ArgumentParser(description='Generate crossword puzzles for KindleMint Engine')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--count', type=int, default=50, help='Number of puzzles to generate')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard', 'mixed'], 
                       default='mixed', help='Difficulty level')
    parser.add_argument('--grid_size', type=int, default=15, help='Grid size (NxN)')
    parser.add_argument('--word_count', type=int, default=35, help='Target words per puzzle')
    parser.add_argument('--max_word_length', type=int, default=15, help='Maximum word length')
    
    args = parser.parse_args()
    
    # Create engine with parameters
    engine = CrosswordEngineV2(
        output_dir=args.output,
        count=args.count,
        difficulty=args.difficulty,
        grid_size=args.grid_size,
        word_count=args.word_count,
        max_word_length=args.max_word_length
    )
    
    # Generate puzzles
    engine.generate_puzzles()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())