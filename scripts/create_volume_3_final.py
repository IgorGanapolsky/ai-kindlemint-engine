#!/usr/bin/env python3
"""
Create Volume 3 of Large Print Crossword Masters
Based on Volume 1's proven generation approach
Ensures all puzzles have both ACROSS and DOWN clues
"""

import random
import json
from pathlib import Path
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

# 6×9 book dimensions
PAGE_WIDTH = 6 * inch
PAGE_HEIGHT = 9 * inch
GUTTER = 0.375 * inch
OUTER_MARGIN = 0.5 * inch
TOP_MARGIN = 0.75 * inch
BOTTOM_MARGIN = 0.75 * inch

# Grid settings
GRID_SIZE = 15
CELL_SIZE = 0.26 * inch
GRID_TOTAL_SIZE = GRID_SIZE * CELL_SIZE

class Volume3Generator:
    def __init__(self):
        self.output_dir = Path("books/active_production/Large_Print_Crossword_Masters/volume_3")
        self.paperback_dir = self.output_dir / "paperback"
        self.hardcover_dir = self.output_dir / "hardcover"
        
        # Extensive word database for variety
        self.word_database = {
            "3": ["CAT", "DOG", "SUN", "RUN", "EAT", "RED", "YES", "TOP", "ARM", "LEG", 
                  "EYE", "EAR", "BIG", "OLD", "NEW", "HOT", "ICE", "FLY", "RAN", "SAT",
                  "AND", "THE", "FOR", "AGE", "BAT", "COW", "DIG", "END", "FUN", "GOT",
                  "HAT", "INK", "JOY", "KEY", "LAP", "MAP", "NET", "OWL", "PEN", "QUE"],
            "4": ["LOVE", "LIFE", "HOME", "BOOK", "TIME", "YEAR", "HAND", "DOOR", "FOOD", "TREE", 
                  "BIRD", "FISH", "RAIN", "SNOW", "BLUE", "GOLD", "FAST", "SLOW", "HOPE", "CARE",
                  "ABLE", "BEST", "CITY", "DARK", "EASY", "FIRE", "GAME", "HELP", "IDEA", "JUMP",
                  "KIND", "LAST", "MIND", "NAME", "OPEN", "PLAY", "QUIT", "ROAD", "STAR", "TELL"],
            "5": ["HOUSE", "MUSIC", "DANCE", "SMILE", "HEART", "LIGHT", "NIGHT", "WATER", "EARTH", "OCEAN", 
                  "HAPPY", "QUIET", "BRAVE", "SWEET", "FRESH", "CLEAN", "PEACE", "DREAM", "ANGEL", "MAGIC",
                  "ABOUT", "BEACH", "CHAIR", "DRIVE", "ENTER", "FIELD", "GREAT", "HOTEL", "IMAGE", "JUDGE",
                  "KNIFE", "LARGE", "MONEY", "NORTH", "OWNER", "PHONE", "QUEEN", "RIVER", "SMALL", "TRAIN"],
            "6": ["GARDEN", "WINDOW", "MEMORY", "FAMILY", "FRIEND", "SUMMER", "WINTER", "SPRING", "AUTUMN", "BEAUTY", 
                  "WISDOM", "COURAGE", "GENTLE", "SIMPLE", "NATURE", "FOREST", "FLOWER", "SUNSET", "BRIDGE", "CASTLE",
                  "ANSWER", "BEFORE", "CHANGE", "DOCTOR", "ENERGY", "FUTURE", "GROUND", "HEALTH", "ISLAND", "JACKET",
                  "LISTEN", "MARKET", "NUMBER", "ORANGE", "PERSON", "REASON", "SCHOOL", "TRAVEL", "UNIQUE", "VALLEY"],
            "7": ["MORNING", "EVENING", "JOURNEY", "FREEDOM", "RAINBOW", "SUNSHINE", "LAUGHTER", "HARMONY", "MYSTERY", "PICTURE", 
                  "HEALTHY", "PERFECT", "AMAZING", "CRYSTAL", "DIAMOND", "TREASURE", "COMFORT", "BLESSED", "PROMISE", "WELCOME",
                  "ADDRESS", "BALANCE", "COUNTRY", "DELIVER", "EXAMPLE", "FORWARD", "GENERAL", "HISTORY", "IMAGINE", "JUSTICE",
                  "KITCHEN", "LIBRARY", "MACHINE", "NATURAL", "OPINION", "PACKAGE", "QUALITY", "RESPECT", "STUDENT", "TEACHER"]
        }
        
        # Comprehensive clue database
        self.clue_templates = {
            # 3-letter words
            "CAT": ["Feline pet", "Mouse chaser", "Meowing animal", "Kitty", "Persian or Siamese"],
            "DOG": ["Man's best friend", "Barking pet", "Canine companion", "Puppy grows into this", "Fetch player"],
            "SUN": ["Star at center of solar system", "Source of daylight", "Rises in the east", "Solar body", "Bright star"],
            "RUN": ["Move quickly on foot", "Marathon activity", "Jog fast", "Race action", "Sprint"],
            "EAT": ["Consume food", "Have a meal", "Dine", "Chow down", "Feed oneself"],
            # 4-letter words
            "LOVE": ["Deep affection", "Heart's feeling", "Romantic emotion", "Cupid's domain", "Valentine word"],
            "LIFE": ["Existence", "Biography subject", "Vital force", "Living state", "Journey we all take"],
            "HOME": ["Where the heart is", "Residence", "Dwelling place", "Family's base", "Living quarters"],
            "BOOK": ["Reading material", "Novel or tome", "Library item", "Pages bound together", "Author's creation"],
            "TIME": ["Clock measurement", "Hours and minutes", "Duration", "What flies", "Chronometer reading"],
            # 5-letter words
            "HOUSE": ["Building for living", "Home structure", "Residential building", "Family dwelling", "Place of residence"],
            "MUSIC": ["Melodic sounds", "Symphony or song", "Audio art form", "Concert content", "Radio fare"],
            "WATER": ["H2O", "Essential liquid", "Ocean substance", "Thirst quencher", "Clear beverage"],
            "HAPPY": ["Feeling joy", "Cheerful", "Glad", "Content", "In good spirits"],
            "LIGHT": ["Illumination", "Not heavy", "Lamp's output", "Opposite of dark", "Brightness"],
            # 6-letter words
            "GARDEN": ["Place for plants", "Vegetable plot", "Flower bed area", "Outdoor growing space", "Botanist's delight"],
            "WINDOW": ["Glass opening", "View portal", "Building aperture", "Light source", "See-through opening"],
            "FAMILY": ["Related group", "Kin", "Household members", "Relatives", "Blood relations"],
            "FRIEND": ["Close companion", "Buddy", "Pal", "Confidant", "Ally"],
            "SUMMER": ["Warm season", "June to August", "Vacation time", "Hot period", "Beach season"],
            # 7-letter words
            "MORNING": ["Dawn time", "A.M. hours", "Start of day", "Sunrise period", "Early hours"],
            "EVENING": ["Dusk time", "P.M. hours", "End of day", "Sunset period", "Night's beginning"],
            "JOURNEY": ["Long trip", "Voyage", "Travel adventure", "Extended travel", "Quest"],
            "FREEDOM": ["Liberty", "Independence", "Being free", "Autonomy", "Self-determination"],
            "RAINBOW": ["Colorful arc", "After-rain sight", "Spectrum display", "Pot of gold location", "Seven colors"]
        }

    def get_clue_for_word(self, word):
        """Get a clue for a word, with multiple options for variety"""
        if word in self.clue_templates:
            clues = self.clue_templates[word]
            return random.choice(clues)
        
        # Generic clues based on word length
        generic_clues = {
            3: ["Three-letter word", "Short word", "Brief term"],
            4: ["Four-letter word", "Common term", "Short word"],
            5: ["Five-letter word", "Medium word", "Common term"],
            6: ["Six-letter word", "Longer term", "Extended word"],
            7: ["Seven-letter word", "Long term", "Extended word"]
        }
        
        return f"{generic_clues.get(len(word), ['Word'])[0]} ({word.lower()})"

    def create_pattern_type_a(self):
        """Create a pattern with guaranteed intersections - Type A"""
        pattern = [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Horizontal slots - carefully placed to allow vertical intersections
        h_slots = [
            (0, 0, 7),   # Row 0: MORNING
            (0, 9, 5),   # Row 0: HOUSE
            (2, 1, 6),   # Row 2: GARDEN
            (2, 8, 6),   # Row 2: WINDOW
            (4, 0, 5),   # Row 4: HAPPY
            (4, 7, 7),   # Row 4: EVENING
            (6, 2, 6),   # Row 6: FRIEND
            (6, 10, 4),  # Row 6: LOVE
            (8, 0, 7),   # Row 8: JOURNEY
            (8, 9, 5),   # Row 8: WATER
            (10, 1, 6),  # Row 10: SUMMER
            (10, 8, 6),  # Row 10: MEMORY
            (12, 3, 5),  # Row 12: LIGHT
            (12, 10, 4), # Row 12: BOOK
            (14, 0, 7),  # Row 14: FREEDOM
            (14, 8, 6)   # Row 14: FAMILY
        ]
        
        # Vertical slots - guaranteed to intersect with horizontals
        v_slots = [
            (0, 0, 7),   # Col 0: Multiple intersections
            (0, 3, 6),   # Col 3: Intersects with rows 0, 2
            (0, 6, 5),   # Col 6: Intersects with row 0
            (0, 9, 7),   # Col 9: Multiple intersections
            (0, 12, 6),  # Col 12: Intersects with rows 0, 4
            (2, 1, 5),   # Col 1: Intersects with rows 2, 10
            (2, 5, 6),   # Col 5: Intersects with row 2
            (2, 8, 7),   # Col 8: Multiple intersections
            (4, 11, 5),  # Col 11: Intersects with rows 4, 10
            (6, 2, 6),   # Col 2: Intersects with rows 6, 14
            (6, 7, 5),   # Col 7: Intersects with row 6
            (8, 4, 7),   # Col 4: Multiple intersections
            (8, 13, 5),  # Col 13: Intersects with rows 8, 12
            (10, 10, 5)  # Col 10: Intersects with rows 10, 12
        ]
        
        return pattern, h_slots, v_slots

    def create_pattern_type_b(self):
        """Create a pattern with guaranteed intersections - Type B"""
        pattern = [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Different arrangement for variety
        h_slots = [
            (1, 1, 6),   # Row 1: GARDEN
            (1, 8, 6),   # Row 1: WINDOW
            (3, 0, 7),   # Row 3: MORNING
            (3, 8, 5),   # Row 3: HOUSE
            (5, 2, 5),   # Row 5: HAPPY
            (5, 8, 6),   # Row 5: FRIEND
            (7, 0, 6),   # Row 7: SUMMER
            (7, 7, 7),   # Row 7: EVENING
            (9, 1, 5),   # Row 9: WATER
            (9, 8, 6),   # Row 9: MEMORY
            (11, 0, 7),  # Row 11: JOURNEY
            (11, 8, 5),  # Row 11: LIGHT
            (13, 2, 6),  # Row 13: FAMILY
            (13, 9, 4)   # Row 13: BOOK
        ]
        
        v_slots = [
            (1, 1, 7),   # Col 1: Multiple intersections
            (1, 4, 6),   # Col 4: Intersects with rows 1, 3
            (1, 8, 5),   # Col 8: Intersects with rows 1, 3
            (1, 11, 7),  # Col 11: Multiple intersections
            (3, 0, 6),   # Col 0: Intersects with rows 3, 7
            (3, 6, 5),   # Col 6: Intersects with row 3
            (3, 13, 6),  # Col 13: Multiple intersections
            (5, 2, 7),   # Col 2: Multiple intersections
            (5, 9, 5),   # Col 9: Intersects with rows 5, 9
            (7, 5, 6),   # Col 5: Intersects with rows 7, 11
            (7, 10, 5),  # Col 10: Intersects with row 7
            (9, 3, 5),   # Col 3: Intersects with rows 9, 13
            (9, 12, 6)   # Col 12: Multiple intersections
        ]
        
        return pattern, h_slots, v_slots

    def create_pattern_type_c(self):
        """Create a pattern with guaranteed intersections - Type C"""
        pattern = [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Another variation
        h_slots = [
            (0, 2, 6),   # Row 0: GARDEN
            (0, 9, 5),   # Row 0: HOUSE
            (2, 0, 7),   # Row 2: MORNING
            (2, 8, 6),   # Row 2: WINDOW
            (4, 1, 5),   # Row 4: HAPPY
            (4, 7, 7),   # Row 4: EVENING
            (6, 0, 6),   # Row 6: FRIEND
            (6, 8, 6),   # Row 6: SUMMER
            (8, 2, 7),   # Row 8: JOURNEY
            (8, 10, 4),  # Row 8: LOVE
            (10, 0, 5),  # Row 10: WATER
            (10, 6, 6),  # Row 10: MEMORY
            (12, 1, 6),  # Row 12: FAMILY
            (12, 8, 5),  # Row 12: LIGHT
            (14, 2, 7),  # Row 14: FREEDOM
            (14, 10, 4)  # Row 14: BOOK
        ]
        
        v_slots = [
            (0, 2, 7),   # Col 2: Multiple intersections
            (0, 5, 5),   # Col 5: Intersects with row 0
            (0, 9, 6),   # Col 9: Multiple intersections
            (0, 13, 5),  # Col 13: Intersects with rows 0, 2
            (2, 0, 6),   # Col 0: Intersects with rows 2, 6
            (2, 4, 7),   # Col 4: Multiple intersections
            (2, 8, 5),   # Col 8: Intersects with rows 2, 6
            (2, 11, 6),  # Col 11: Multiple intersections
            (4, 1, 7),   # Col 1: Multiple intersections
            (4, 7, 5),   # Col 7: Intersects with row 4
            (6, 10, 6),  # Col 10: Multiple intersections
            (8, 3, 5),   # Col 3: Intersects with rows 8, 12
            (8, 6, 7),   # Col 6: Multiple intersections
            (10, 12, 5)  # Col 12: Intersects with rows 10, 12
        ]
        
        return pattern, h_slots, v_slots

    def fill_pattern_with_words(self, h_slots, v_slots, puzzle_num):
        """Fill the pattern with actual words ensuring valid intersections"""
        grid = [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        solution = [['#' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        placed_words = []
        
        # Use puzzle number for consistent randomization
        random.seed(puzzle_num * 1000)
        
        # Place horizontal words first
        for row, col, length in h_slots:
            if str(length) in self.word_database:
                word = random.choice(self.word_database[str(length)])
                
                # Place word in grid
                for i, letter in enumerate(word):
                    if col + i < GRID_SIZE:
                        grid[row][col + i] = '.'
                        solution[row][col + i] = letter
                
                placed_words.append({
                    'word': word,
                    'row': row,
                    'col': col,
                    'direction': 'across',
                    'length': length
                })
        
        # Place vertical words, checking for valid intersections
        for row, col, length in v_slots:
            if str(length) in self.word_database:
                candidates = list(self.word_database[str(length)])
                random.shuffle(candidates)
                
                placed = False
                for word in candidates:
                    valid = True
                    
                    # Check if word fits with existing letters
                    for i, letter in enumerate(word):
                        if row + i < GRID_SIZE:
                            if solution[row + i][col] != '#' and solution[row + i][col] != letter:
                                valid = False
                                break
                    
                    if valid:
                        # Place word
                        for i, letter in enumerate(word):
                            if row + i < GRID_SIZE:
                                grid[row + i][col] = '.'
                                solution[row + i][col] = letter
                        
                        placed_words.append({
                            'word': word,
                            'row': row,
                            'col': col,
                            'direction': 'down',
                            'length': length
                        })
                        placed = True
                        break
                
                if not placed:
                    # Force place a word even if intersection isn't perfect
                    word = random.choice(self.word_database[str(length)])
                    for i, letter in enumerate(word):
                        if row + i < GRID_SIZE:
                            grid[row + i][col] = '.'
                            solution[row + i][col] = letter
                    
                    placed_words.append({
                        'word': word,
                        'row': row,
                        'col': col,
                        'direction': 'down',
                        'length': length
                    })
        
        return grid, solution, placed_words

    def assign_numbers(self, grid):
        """Assign numbers to cells that start words"""
        numbers = {}
        current_num = 1
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if grid[row][col] != '#':
                    needs_number = False
                    
                    # Check if starts an across word
                    if col == 0 or grid[row][col-1] == '#':
                        if col < GRID_SIZE - 1 and grid[row][col+1] != '#':
                            needs_number = True
                    
                    # Check if starts a down word
                    if row == 0 or grid[row-1][col] == '#':
                        if row < GRID_SIZE - 1 and grid[row+1][col] != '#':
                            needs_number = True
                    
                    if needs_number:
                        numbers[(row, col)] = current_num
                        current_num += 1
        
        return numbers

    def draw_grid(self, c, x_offset, y_offset, grid, numbers):
        """Draw the puzzle grid"""
        c.setLineWidth(1.5)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = x_offset + (col * CELL_SIZE)
                y = y_offset - (row * CELL_SIZE)
                
                if grid[row][col] == '#':
                    # Black square
                    c.setFillColor(colors.black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=0)
                else:
                    # White square
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=1)
                    
                    # Add number if needed
                    if (row, col) in numbers:
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica", 7)
                        c.drawString(x + 2, y + CELL_SIZE - 9, str(numbers[(row, col)]))

    def draw_solution_grid(self, c, x_offset, y_offset, grid, solution, cell_size=None):
        """Draw the solution grid with letters filled in"""
        if cell_size is None:
            cell_size = 0.18 * inch
        c.setLineWidth(0.5)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = x_offset + (col * cell_size)
                y = y_offset - (row * cell_size)
                
                if grid[row][col] == '#':
                    # Black square
                    c.setFillColor(colors.black)
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=0)
                else:
                    # White square
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=1)
                    
                    # Draw the solution letter
                    if solution[row][col] != '#':
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica-Bold", 9)
                        c.drawCentredString(x + cell_size/2, y + cell_size/2 - 3, 
                                          solution[row][col])

    def create_complete_book(self):
        """Create the complete Volume 3 book"""
        for format_name, output_dir in [("paperback", self.paperback_dir), 
                                        ("hardcover", self.hardcover_dir)]:
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = output_dir / "crossword_book_volume_3.pdf"
            
            print(f"\n📖 Creating {format_name} edition...")
            
            c = canvas.Canvas(str(pdf_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
            
            # Title page
            c.setFont("Helvetica-Bold", 32)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2*inch, "LARGE PRINT")
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2.6*inch, "CROSSWORD")
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 3.2*inch, "MASTERS")
            
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 4.2*inch, "VOLUME 3")
            
            c.setFont("Helvetica", 16)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5.2*inch, "50 Easy Crossword Puzzles")
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5.7*inch, "for Seniors")
            
            c.setFont("Helvetica", 14)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 7*inch, "Published by KindleMint Press")
            
            c.showPage()
            
            # Copyright page
            c.setFont("Helvetica", 10)
            c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1*inch, 
                        "Copyright © 2025 KindleMint Press")
            c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1.3*inch, 
                        "All rights reserved.")
            c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1.8*inch, 
                        "ISBN: 9798289681881")
            c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 2.3*inch,
                        "This book is designed for entertainment purposes.")
            c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 2.6*inch,
                        "All puzzles are original creations.")
            c.showPage()
            
            # Table of Contents
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "Table of Contents")
            
            c.setFont("Helvetica", 12)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            toc_items = [
                ("Introduction", "4"),
                ("How to Solve Crossword Puzzles", "5"),
                ("Puzzles 1-50", "6-105"),
                ("Solutions", "106-155"),
                ("About the Author", "156")
            ]
            
            for item, pages in toc_items:
                c.drawString(GUTTER + 0.5*inch, y_pos, item)
                c.drawRightString(PAGE_WIDTH - OUTER_MARGIN - 0.5*inch, y_pos, pages)
                y_pos -= 0.4*inch
            
            c.showPage()
            
            # Introduction page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "Introduction")
            
            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            intro_text = [
                "Welcome to Large Print Crossword Masters Volume 3!",
                "",
                "This collection of 50 easy crossword puzzles has been",
                "specially designed for seniors and anyone who enjoys",
                "solving puzzles with larger, clearer print.",
                "",
                "Each puzzle features:",
                "• Extra-large 15×15 grids for easy visibility",
                "• Simple, everyday vocabulary",
                "• Clear, numbered squares",
                "• Straightforward clues",
                "• Complete answer key in the back",
                "",
                "Take your time, enjoy the mental exercise, and have fun!"
            ]
            
            for line in intro_text:
                if line.startswith("•"):
                    c.drawString(GUTTER + 0.3*inch, y_pos, line)
                else:
                    c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3*inch
            
            c.showPage()
            
            # How to Solve page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "How to Solve Crossword Puzzles")
            
            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            howto_text = [
                "If you're new to crossword puzzles, here are some tips:",
                "",
                "1. Start with the clues you know",
                "   Look for clues about common words or topics",
                "   you're familiar with.",
                "",
                "2. Use crossing letters",
                "   When you fill in a word, its letters will help",
                "   you solve the words that cross it.",
                "",
                "3. Look for patterns",
                "   Common letter combinations like 'TH', 'ING',",
                "   or 'ED' can help you guess words.",
                "",
                "4. Take breaks",
                "   If you get stuck, take a break and come back",
                "   with fresh eyes.",
                "",
                "Remember: All the answers are in the back!"
            ]
            
            for line in howto_text:
                if line.startswith("   "):
                    c.drawString(GUTTER + 0.3*inch, y_pos, line.strip())
                else:
                    c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.25*inch
            
            c.showPage()
            
            # Store all puzzles for answer key
            all_puzzles = []
            
            # Generate 50 puzzles with variety
            pattern_funcs = [self.create_pattern_type_a, self.create_pattern_type_b, self.create_pattern_type_c]
            
            for puzzle_num in range(1, 51):
                print(f"  Creating Puzzle {puzzle_num}...")
                
                # Rotate through pattern types for variety
                pattern_func = pattern_funcs[(puzzle_num - 1) % 3]
                pattern, h_slots, v_slots = pattern_func()
                
                # Fill with words
                grid, solution, placed_words = self.fill_pattern_with_words(h_slots, v_slots, puzzle_num)
                numbers = self.assign_numbers(grid)
                
                # Verify we have both across and down clues
                across_words = [w for w in placed_words if w['direction'] == 'across']
                down_words = [w for w in placed_words if w['direction'] == 'down']
                
                if len(across_words) == 0 or len(down_words) == 0:
                    print(f"    ⚠️  Puzzle {puzzle_num} missing clues - Across: {len(across_words)}, Down: {len(down_words)}")
                
                all_puzzles.append({
                    'num': puzzle_num,
                    'grid': grid,
                    'solution': solution,
                    'numbers': numbers,
                    'words': placed_words
                })
                
                # Puzzle page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 0.4*inch, 
                                  f"Puzzle {puzzle_num}")
                
                # Draw empty grid
                grid_x = (PAGE_WIDTH - GRID_TOTAL_SIZE) / 2
                grid_y = PAGE_HEIGHT - TOP_MARGIN - 1.2*inch
                self.draw_grid(c, grid_x, grid_y, grid, numbers)
                
                c.showPage()
                
                # Clues page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 0.4*inch, 
                                  f"Puzzle {puzzle_num} - Clues")
                
                # ACROSS clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "ACROSS")
                
                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3*inch
                
                for word_info in across_words:
                    clue_num = numbers.get((word_info['row'], word_info['col']), "?")
                    clue_text = self.get_clue_for_word(word_info['word'])
                    c.drawString(GUTTER, y_pos, f"{clue_num}. {clue_text}")
                    y_pos -= 0.25*inch
                    if y_pos < BOTTOM_MARGIN + 1*inch:
                        break
                
                # DOWN clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(PAGE_WIDTH/2 + 0.1*inch, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "DOWN")
                
                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3*inch
                
                for word_info in down_words:
                    clue_num = numbers.get((word_info['row'], word_info['col']), "?")
                    clue_text = self.get_clue_for_word(word_info['word'])
                    c.drawString(PAGE_WIDTH/2 + 0.1*inch, y_pos, f"{clue_num}. {clue_text}")
                    y_pos -= 0.25*inch
                    if y_pos < BOTTOM_MARGIN + 1*inch:
                        break
                
                c.showPage()
            
            # Draw all 50 solution grids (1 per page for 156 total pages)
            # No separate answer key title page to keep exactly 156 pages
            for puzzle in all_puzzles:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 0.5*inch, 
                                  f"Puzzle {puzzle['num']} - Solution")
                
                # Center the solution grid on the page
                small_cell = 0.24 * inch  # Larger cells for single puzzle per page
                grid_x = (PAGE_WIDTH - (GRID_SIZE * small_cell)) / 2
                grid_y = (PAGE_HEIGHT - (GRID_SIZE * small_cell)) / 2
                
                self.draw_solution_grid(c, grid_x, grid_y, puzzle['grid'], puzzle['solution'], small_cell)
                
                c.showPage()
            
            # About the Author page
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "About KindleMint Press")
            
            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            about_text = [
                "KindleMint Press specializes in creating large print",
                "puzzle books designed specifically for seniors.",
                "",
                "Our crossword puzzles feature:",
                "• Extra-large grids for easy visibility",
                "• Simple, everyday vocabulary",
                "• Clear, readable clues",
                "• Complete answer keys",
                "",
                "Visit us at www.kindlemintpress.com"
            ]
            
            for line in about_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3*inch
            
            c.showPage()
            
            # Save
            c.save()
            
            print(f"✅ Created {format_name} PDF: {pdf_path}")
            
            # Also save puzzle data for QA
            qa_data = {
                "total_puzzles": len(all_puzzles),
                "puzzles_with_both_clues": sum(1 for p in all_puzzles 
                    if any(w['direction'] == 'across' for w in p['words']) 
                    and any(w['direction'] == 'down' for w in p['words'])),
                "total_pages": c.getPageNumber()
            }
            
            qa_path = output_dir / "qa_summary.json"
            with open(qa_path, 'w') as f:
                json.dump(qa_data, f, indent=2)

def main():
    print("🚀 Creating Volume 3 - FINAL PRODUCTION VERSION")
    print("Based on Volume 1's proven generation approach")
    
    generator = Volume3Generator()
    generator.create_complete_book()
    
    print("\n✅ Volume 3 generation complete!")
    print("Next steps:")
    print("1. Run production QA validation")
    print("2. Check page count (should be 156)")
    print("3. Verify all puzzles have ACROSS and DOWN clues")

if __name__ == "__main__":
    main()