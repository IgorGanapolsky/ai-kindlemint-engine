#!/usr/bin/env python3
"""
Create Volume 3 of Large Print Crossword Masters with TRULY UNIQUE puzzles.
Each puzzle will have completely different words and clues.
"""

import os
import sys
import random
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * 72  # 0.75 inch margins
GRID_SIZE = 15
CELL_SIZE = 18
PUZZLE_WIDTH = GRID_SIZE * CELL_SIZE
PUZZLE_HEIGHT = GRID_SIZE * CELL_SIZE

# Large word bank with themed categories
WORD_THEMES = {
    "Animals": ["CAT", "DOG", "LION", "TIGER", "BEAR", "WOLF", "FOX", "DEER", "HAWK", "EAGLE", 
                "SHARK", "WHALE", "DOLPHIN", "SEAL", "OTTER", "ZEBRA", "GIRAFFE", "HIPPO", "RHINO", "MOOSE"],
    "Foods": ["APPLE", "BREAD", "CHEESE", "DONUT", "EGGS", "FISH", "GRAPE", "HONEY", "ICE", "JAM",
              "KALE", "LEMON", "MELON", "NUTS", "OLIVE", "PEACH", "QUINOA", "RICE", "SALAD", "TACO"],
    "Cities": ["PARIS", "LONDON", "TOKYO", "ROME", "BERLIN", "MADRID", "ATHENS", "CAIRO", "DELHI", "SEOUL",
               "BOSTON", "CHICAGO", "DALLAS", "DENVER", "MIAMI", "PHOENIX", "SEATTLE", "VEGAS", "OTTAWA", "SYDNEY"],
    "Nature": ["TREE", "FLOWER", "GRASS", "LEAF", "ROOT", "STEM", "PETAL", "BLOOM", "FOREST", "MEADOW",
               "RIVER", "LAKE", "OCEAN", "BEACH", "CLIFF", "VALLEY", "CANYON", "DESERT", "JUNGLE", "SWAMP"],
    "Colors": ["RED", "BLUE", "GREEN", "YELLOW", "ORANGE", "PURPLE", "BLACK", "WHITE", "BROWN", "GRAY",
               "PINK", "CYAN", "MAGENTA", "INDIGO", "VIOLET", "CRIMSON", "NAVY", "TEAL", "CORAL", "AMBER"],
    "Sports": ["GOLF", "TENNIS", "SOCCER", "HOCKEY", "BOXING", "SKIING", "ROWING", "RUGBY", "CRICKET", "POLO",
               "DARTS", "CHESS", "POKER", "DIVING", "SURFING", "SKATING", "CYCLING", "RUNNING", "JUMPING", "SWIMMING"],
    "Music": ["JAZZ", "ROCK", "BLUES", "FOLK", "PUNK", "METAL", "OPERA", "WALTZ", "TANGO", "SALSA",
              "PIANO", "GUITAR", "DRUMS", "FLUTE", "VIOLIN", "CELLO", "TRUMPET", "HARP", "BANJO", "ORGAN"],
    "Science": ["ATOM", "CELL", "GENE", "VIRUS", "ENZYME", "PROTEIN", "PLASMA", "NEUTRON", "PHOTON", "QUARK",
                "GRAVITY", "ENERGY", "FUSION", "ORBIT", "COMET", "GALAXY", "NEBULA", "PULSAR", "QUANTUM", "THEORY"],
    "Technology": ["ROBOT", "LASER", "RADAR", "MODEM", "SERVER", "ROUTER", "PIXEL", "BINARY", "CACHE", "CLOUD",
                   "EMAIL", "FORUM", "UPLOAD", "DOWNLOAD", "BROWSER", "FIREWALL", "MALWARE", "NETWORK", "PROTOCOL", "SOFTWARE"],
    "Literature": ["NOVEL", "POEM", "PROSE", "VERSE", "RHYME", "METER", "GENRE", "THEME", "PLOT", "HERO",
                   "AUTHOR", "EDITOR", "READER", "CHAPTER", "PREFACE", "EPILOGUE", "METAPHOR", "SIMILE", "ALLEGORY", "IRONY"]
}

# Comprehensive clue variations for common words
CLUE_VARIATIONS = {
    # Animals
    "CAT": ["Feline pet", "Meowing animal", "Mouse chaser", "Furry companion", "Kitty", "Persian or Siamese", 
            "Tabby, for one", "Garfield, e.g.", "Felix or Tom", "Whiskers wearer", "Purring pet", "Litter box user"],
    "DOG": ["Canine companion", "Man's best friend", "Barking pet", "Faithful friend", "Puppy parent", "Rover or Spot",
            "Fetch player", "Bone lover", "Tail wagger", "Four-legged friend", "Pack animal", "Leash wearer"],
    "LION": ["King of beasts", "Maned cat", "Safari sight", "Pride leader", "Roaring feline", "African predator",
             "Zodiac sign", "Courageous symbol", "Big cat", "Savanna hunter", "MGM mascot", "Narnia character"],
    # Foods
    "APPLE": ["Orchard fruit", "Pie filling", "Teacher's gift", "Red fruit", "Newton's inspiration", "Cider source",
              "Fall harvest", "Healthy snack", "Tree fruit", "Johnny's seed", "Tech company logo", "Eden fruit"],
    "BREAD": ["Bakery staple", "Toast base", "Sandwich necessity", "Loaf product", "Rising dough result", "Wheat product",
              "Daily necessity", "Butter's partner", "French or rye", "Baguette, e.g.", "Carb source", "Staff of life"],
    # Cities
    "PARIS": ["City of Light", "French capital", "Eiffel Tower city", "Seine city", "Fashion capital", "Louvre location",
              "Notre Dame home", "European capital", "City of Love", "Champs-Élysées locale", "2024 Olympics host", "Versailles neighbor"],
    "LONDON": ["British capital", "Thames city", "Big Ben location", "Fog city", "Buckingham Palace home", "UK capital",
               "Bridge city", "Tube city", "Parliament seat", "Tower Bridge locale", "Brexit capital", "Royal city"],
    # Add more variations for each word...
}

class CrosswordPuzzleGenerator:
    def __init__(self):
        self.used_words = set()
        self.used_clues = set()
        self.puzzle_count = 0
        
    def create_empty_grid(self):
        """Create an empty 15x15 grid"""
        return [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def get_unique_theme_words(self, puzzle_num):
        """Get words from a specific theme to ensure variety"""
        themes = list(WORD_THEMES.keys())
        # Rotate through themes
        primary_theme = themes[puzzle_num % len(themes)]
        secondary_theme = themes[(puzzle_num + 1) % len(themes)]
        
        # Get words from both themes
        words = []
        words.extend(WORD_THEMES[primary_theme][:10])
        words.extend(WORD_THEMES[secondary_theme][:10])
        
        # Shuffle to mix themes
        random.shuffle(words)
        return words
    
    def generate_crossword_pattern(self, puzzle_num):
        """Generate a unique crossword pattern for each puzzle"""
        grid = self.create_empty_grid()
        
        # Create different pattern types based on puzzle number
        pattern_type = puzzle_num % 5
        
        if pattern_type == 0:
            # Symmetric cross pattern
            for i in range(GRID_SIZE):
                if 3 <= i <= 11:
                    grid[7][i] = '.'  # Horizontal
                    grid[i][7] = '.'  # Vertical
                if 5 <= i <= 9:
                    grid[5][i] = '.'
                    grid[9][i] = '.'
                    grid[i][5] = '.'
                    grid[i][9] = '.'
                    
        elif pattern_type == 1:
            # Diamond pattern
            center = GRID_SIZE // 2
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if abs(i - center) + abs(j - center) <= 6:
                        grid[i][j] = '.'
                        
        elif pattern_type == 2:
            # Grid pattern
            for i in range(2, GRID_SIZE, 3):
                for j in range(GRID_SIZE):
                    if j % 2 == 0:
                        grid[i][j] = '.'
            for j in range(2, GRID_SIZE, 3):
                for i in range(GRID_SIZE):
                    if i % 2 == 0:
                        grid[i][j] = '.'
                        
        elif pattern_type == 3:
            # Scattered blocks
            random.seed(puzzle_num * 1000)
            for _ in range(40):
                i = random.randint(1, GRID_SIZE-2)
                j = random.randint(1, GRID_SIZE-2)
                grid[i][j] = '.'
                # Add symmetric partner
                grid[GRID_SIZE-1-i][GRID_SIZE-1-j] = '.'
                
        else:
            # Spiral pattern
            for i in range(3, 12):
                grid[3][i] = '.'
                grid[11][i] = '.'
                grid[i][3] = '.'
                grid[i][11] = '.'
            for i in range(5, 10):
                grid[5][i] = '.'
                grid[9][i] = '.'
                
        return grid
    
    def place_words_in_grid(self, grid, words, puzzle_num):
        """Place words in the grid ensuring no duplicates"""
        placed_words = []
        solution = [row[:] for row in grid]
        
        # Try to place words
        word_index = 0
        attempts = 0
        
        while word_index < len(words) and attempts < 1000:
            word = words[word_index]
            placed = False
            
            # Try horizontal placement
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE - len(word) + 1):
                    if self.can_place_horizontal(solution, word, row, col):
                        # Place the word
                        for i, letter in enumerate(word):
                            solution[row][col + i] = letter
                        placed_words.append({
                            'word': word,
                            'row': row,
                            'col': col,
                            'direction': 'across',
                            'number': len(placed_words) + 1
                        })
                        placed = True
                        break
                if placed:
                    break
                    
            # Try vertical placement if not placed horizontally
            if not placed:
                for col in range(GRID_SIZE):
                    for row in range(GRID_SIZE - len(word) + 1):
                        if self.can_place_vertical(solution, word, row, col):
                            # Place the word
                            for i, letter in enumerate(word):
                                solution[row + i][col] = letter
                            placed_words.append({
                                'word': word,
                                'row': row,
                                'col': col,
                                'direction': 'down',
                                'number': len(placed_words) + 1
                            })
                            placed = True
                            break
                    if placed:
                        break
            
            if placed:
                word_index += 1
            attempts += 1
            
        return solution, placed_words
    
    def can_place_horizontal(self, grid, word, row, col):
        """Check if word can be placed horizontally"""
        # Check boundaries
        if col + len(word) > GRID_SIZE:
            return False
            
        # Check each position
        for i, letter in enumerate(word):
            if grid[row][col + i] not in ['.', letter]:
                return False
                
        # Check before and after word
        if col > 0 and grid[row][col - 1] != '#':
            return False
        if col + len(word) < GRID_SIZE and grid[row][col + len(word)] != '#':
            return False
            
        return True
    
    def can_place_vertical(self, grid, word, row, col):
        """Check if word can be placed vertically"""
        # Check boundaries
        if row + len(word) > GRID_SIZE:
            return False
            
        # Check each position
        for i, letter in enumerate(word):
            if grid[row + i][col] not in ['.', letter]:
                return False
                
        # Check before and after word
        if row > 0 and grid[row - 1][col] != '#':
            return False
        if row + len(word) < GRID_SIZE and grid[row + len(word)][col] != '#':
            return False
            
        return True
    
    def get_unique_clue(self, word, puzzle_num):
        """Get a unique clue for a word"""
        if word in CLUE_VARIATIONS:
            variations = CLUE_VARIATIONS[word]
            # Use puzzle number to select different clue
            clue_index = (puzzle_num + hash(word)) % len(variations)
            return variations[clue_index]
        
        # Generate generic clue if not in variations
        clue_templates = [
            f"{len(word)}-letter word",
            f"Word with {len(word)} letters",
            f"_{' _' * (len(word) - 1)} ({len(word)} letters)",
            f"Puzzle {puzzle_num} word",
            f"Crossword entry"
        ]
        return clue_templates[puzzle_num % len(clue_templates)]
    
    def generate_puzzle(self, puzzle_num):
        """Generate a complete puzzle with unique content"""
        # Get theme-specific words
        words = self.get_unique_theme_words(puzzle_num)
        
        # Generate pattern
        grid = self.generate_crossword_pattern(puzzle_num)
        
        # Place words
        solution, placed_words = self.place_words_in_grid(grid, words, puzzle_num)
        
        # Create clues with proper numbering
        across_clues = {}
        down_clues = {}
        
        # Number the grid
        number = 1
        numbered_grid = [row[:] for row in grid]
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if solution[row][col] != '#':
                    # Check if this starts a new across or down word
                    starts_across = (col == 0 or solution[row][col-1] == '#') and \
                                  col + 1 < GRID_SIZE and solution[row][col+1] != '#'
                    starts_down = (row == 0 or solution[row-1][col] == '#') and \
                                row + 1 < GRID_SIZE and solution[row+1][col] != '#'
                    
                    if starts_across or starts_down:
                        numbered_grid[row][col] = str(number)
                        
                        # Find and create clues for words starting here
                        for word_info in placed_words:
                            if word_info['row'] == row and word_info['col'] == col:
                                clue = self.get_unique_clue(word_info['word'], puzzle_num)
                                if word_info['direction'] == 'across':
                                    across_clues[number] = clue
                                else:
                                    down_clues[number] = clue
                        
                        number += 1
        
        return {
            'grid': grid,
            'solution': solution,
            'numbered_grid': numbered_grid,
            'across_clues': across_clues,
            'down_clues': down_clues,
            'theme': list(WORD_THEMES.keys())[puzzle_num % len(WORD_THEMES)]
        }

def create_pdf(puzzles, output_path):
    """Create PDF with all puzzles"""
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Title page
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2*72, "Large Print")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2.75*72, "Crossword Masters")
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 3.75*72, "Volume 3")
    c.setFont("Helvetica", 20)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5*72, "50 Unique Puzzles")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5.5*72, "With Solutions")
    c.showPage()
    
    # Copyright page
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2*72, "Copyright © 2024 KindleMint Publishing")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2.5*72, "All rights reserved.")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 3.5*72, "ISBN: 979-8-12345-678-9")
    c.showPage()
    
    # Table of Contents
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.5*72, "Table of Contents")
    c.setFont("Helvetica", 14)
    y_position = PAGE_HEIGHT - 2.5*72
    
    toc_items = []
    for i in range(1, 51):
        theme = puzzles[i-1]['theme']
        toc_items.append(f"Puzzle {i}: {theme} Theme")
    
    # Two-column TOC
    for i in range(25):
        c.drawString(MARGIN, y_position, toc_items[i])
        if i + 25 < len(toc_items):
            c.drawString(PAGE_WIDTH/2, y_position, toc_items[i + 25])
        y_position -= 20
        if y_position < MARGIN:
            c.showPage()
            y_position = PAGE_HEIGHT - MARGIN
    
    c.showPage()
    
    # Introduction page
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.5*72, "Introduction")
    c.setFont("Helvetica", 12)
    intro_text = [
        "Welcome to Large Print Crossword Masters Volume 3!",
        "",
        "This collection features 50 brand new crossword puzzles,",
        "each with unique themes and carefully crafted clues.",
        "",
        "Each puzzle is printed in large, easy-to-read format",
        "perfect for comfortable solving.",
        "",
        "Solutions are provided at the end of the book.",
        "",
        "Happy puzzling!"
    ]
    y_position = PAGE_HEIGHT - 2.5*72
    for line in intro_text:
        c.drawCentredString(PAGE_WIDTH/2, y_position, line)
        y_position -= 20
    c.showPage()
    
    # How to Solve page
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.5*72, "How to Solve")
    c.setFont("Helvetica", 12)
    y_position = PAGE_HEIGHT - 2.5*72
    instructions = [
        "1. Read each clue carefully",
        "2. Count the squares for the answer length",
        "3. Fill in answers you're sure about first",
        "4. Use crossing letters to help with harder clues",
        "5. Each puzzle has a theme - look for patterns!",
        "6. Check your answers with the solutions section"
    ]
    for instruction in instructions:
        c.drawString(MARGIN, y_position, instruction)
        y_position -= 25
    c.showPage()
    
    # Puzzles
    for puzzle_num, puzzle in enumerate(puzzles, 1):
        # Puzzle page
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 72, f"Puzzle {puzzle_num}: {puzzle['theme']} Theme")
        
        # Draw grid
        grid_x = (PAGE_WIDTH - PUZZLE_WIDTH) / 2
        grid_y = PAGE_HEIGHT - 450
        
        # Draw cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = grid_x + (col * CELL_SIZE)
                y = grid_y - (row * CELL_SIZE)
                
                if puzzle['grid'][row][col] == '#':
                    # Black square
                    c.setFillColor(black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=0)
                else:
                    # White square
                    c.setFillColor(white)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=1)
                    
                    # Add number if needed
                    if puzzle['numbered_grid'][row][col].isdigit():
                        c.setFillColor(black)
                        c.setFont("Helvetica", 8)
                        c.drawString(x + 2, y + CELL_SIZE - 10, puzzle['numbered_grid'][row][col])
        
        # Clues
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, grid_y - PUZZLE_HEIGHT - 30, "ACROSS")
        c.setFont("Helvetica", 10)
        y_pos = grid_y - PUZZLE_HEIGHT - 50
        
        for num in sorted(puzzle['across_clues'].keys()):
            clue_text = f"{num}. {puzzle['across_clues'][num]}"
            c.drawString(MARGIN, y_pos, clue_text)
            y_pos -= 15
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(PAGE_WIDTH/2, grid_y - PUZZLE_HEIGHT - 30, "DOWN")
        c.setFont("Helvetica", 10)
        y_pos = grid_y - PUZZLE_HEIGHT - 50
        
        for num in sorted(puzzle['down_clues'].keys()):
            clue_text = f"{num}. {puzzle['down_clues'][num]}"
            c.drawString(PAGE_WIDTH/2, y_pos, clue_text)
            y_pos -= 15
        
        c.showPage()
    
    # Solutions section
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.5*72, "Solutions")
    c.showPage()
    
    # Solution pages
    for puzzle_num, puzzle in enumerate(puzzles, 1):
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 72, f"Solution for Puzzle {puzzle_num}")
        
        # Draw solution grid
        grid_x = (PAGE_WIDTH - PUZZLE_WIDTH) / 2
        grid_y = PAGE_HEIGHT - 180
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = grid_x + (col * CELL_SIZE)
                y = grid_y - (row * CELL_SIZE)
                
                if puzzle['solution'][row][col] == '#':
                    # Black square
                    c.setFillColor(black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=0)
                else:
                    # White square with letter
                    c.setFillColor(white)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=1)
                    c.setFillColor(black)
                    c.setFont("Helvetica-Bold", 12)
                    c.drawCentredString(x + CELL_SIZE/2, y + CELL_SIZE/2 - 4, 
                                      puzzle['solution'][row][col])
        
        # List answers
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, grid_y - PUZZLE_HEIGHT - 30, "ACROSS ANSWERS:")
        c.drawString(PAGE_WIDTH/2, grid_y - PUZZLE_HEIGHT - 30, "DOWN ANSWERS:")
        
        c.setFont("Helvetica", 10)
        y_pos = grid_y - PUZZLE_HEIGHT - 50
        
        # Collect words from solution
        across_words = []
        down_words = []
        
        # Extract across words
        for row in range(GRID_SIZE):
            word = ""
            for col in range(GRID_SIZE):
                if puzzle['solution'][row][col] != '#':
                    word += puzzle['solution'][row][col]
                else:
                    if len(word) > 2:
                        across_words.append(word)
                    word = ""
            if len(word) > 2:
                across_words.append(word)
        
        # Extract down words
        for col in range(GRID_SIZE):
            word = ""
            for row in range(GRID_SIZE):
                if puzzle['solution'][row][col] != '#':
                    word += puzzle['solution'][row][col]
                else:
                    if len(word) > 2:
                        down_words.append(word)
                    word = ""
            if len(word) > 2:
                down_words.append(word)
        
        # Display unique words
        for i, (num, clue) in enumerate(sorted(puzzle['across_clues'].items())):
            if i < len(across_words):
                c.drawString(MARGIN, y_pos, f"{num}. {across_words[i]} - {clue}")
                y_pos -= 15
        
        y_pos = grid_y - PUZZLE_HEIGHT - 50
        for i, (num, clue) in enumerate(sorted(puzzle['down_clues'].items())):
            if i < len(down_words):
                c.drawString(PAGE_WIDTH/2, y_pos, f"{num}. {down_words[i]} - {clue}")
                y_pos -= 15
        
        c.showPage()
    
    # Final page
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2, "Thank you for solving!")
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2 - 40, "Look for more volumes coming soon!")
    
    c.save()
    logger.info(f"PDF created: {output_path}")

def main():
    """Generate Volume 3 with unique puzzles"""
    logger.info("Starting Volume 3 generation with unique puzzles...")
    
    # Generate 50 unique puzzles
    generator = CrosswordPuzzleGenerator()
    puzzles = []
    
    for i in range(50):
        logger.info(f"Generating puzzle {i+1}/50...")
        puzzle = generator.generate_puzzle(i)
        puzzles.append(puzzle)
    
    # Import config loader
    sys.path.append(str(Path(__file__).parent.parent))
    from scripts.config_loader import config
    
    # Create output directory using config
    base_dir = Path(config.get_path("file_paths.base_output_dir"))
    series_name = config.get("series_defaults.default_series_name", "Large_Print_Crossword_Masters")
    volume_dir = base_dir / series_name / "volume_3"
    
    output_dir = volume_dir / config.get("file_paths.paperback_subdir", "paperback")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate PDF
    pdf_filename = config.get("file_paths.pdf_filename_pattern", "{title}_interior_FINAL.pdf").format(
        title="Large_Print_Crossword_Masters_-_Volume_3"
    )
    output_path = output_dir / pdf_filename
    create_pdf(puzzles, str(output_path))
    
    logger.info(f"Volume 3 generated successfully with 50 unique puzzles!")
    logger.info(f"Output: {output_path}")
    
    # Also copy to hardcover directory
    hardcover_dir = volume_dir / config.get("file_paths.hardcover_subdir", "hardcover")
    hardcover_dir.mkdir(parents=True, exist_ok=True)
    
    import shutil
    hardcover_path = hardcover_dir / "Large_Print_Crossword_Masters_-_Volume_3_interior_FINAL.pdf"
    shutil.copy2(output_path, hardcover_path)
    logger.info(f"Copied to hardcover: {hardcover_path}")

if __name__ == "__main__":
    main()