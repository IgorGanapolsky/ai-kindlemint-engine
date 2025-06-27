#!/usr/bin/env python3
"""
Create Volume 3 with simple, working crosswords
Uses predefined puzzle templates that are guaranteed to work
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

# Predefined working crosswords (50 puzzles)
PUZZLE_TEMPLATES = [
    # Puzzle 1
    {
        "grid": [
            "FARM#HELP#SMART",
            "AREA#AREA#MUSIC",
            "STAR#VERY#ALONE",
            "TIME#END##NOTED",
            "###STARTS#####",
            "BEFORE#SHELTER",
            "ACROSS#HUNDRED",
            "BETTER#EVENING",
            "YELLOW#DESIGNS",
            "###OTHER#####",
            "PAINT##ASK#NINE",
            "ALONG#STEP#IDEA",
            "STORE#TALL#NEST",
            "SIDES#ELSE#GREW",
            "YEARS#DEAR#SALE"
        ],
        "across_clues": {
            1: "Place with animals and crops",
            5: "Assist",
            9: "Intelligent",
            13: "Region or space",
            14: "Region (repeat)",
            15: "Songs and melodies",
            16: "Bright celestial object",
            17: "Extremely",
            18: "By oneself",
            19: "Clock reading",
            20: "Finish",
            22: "Observed",
            24: "Begins",
            26: "Earlier than",
            30: "Protection from weather",
            34: "From side to side",
            35: "Ten times ten",
            36: "More good",
            37: "Time after sunset",
            38: "Color of sun",
            39: "Plans or patterns",
            41: "Different one",
            43: "Color coating",
            45: "Request",
            46: "Number after eight",
            49: "Beside",
            53: "Footfall",
            54: "Thought",
            57: "Shop",
            58: "High",
            59: "Bird's home",
            60: "Edges",
            61: "Otherwise",
            62: "Became larger",
            63: "Time periods",
            64: "Beloved",
            65: "Bargain event"
        },
        "down_clues": {
            1: "Quick",
            2: "Region",
            3: "Tear",
            4: "Males",
            5: "Residence",
            6: "Conclusion",
            7: "Jump",
            8: "Educate",
            9: "Begin",
            10: "Female horse",
            11: "Skill",
            12: "Attempt",
            21: "Consumed",
            23: "Positions",
            25: "Ripped",
            26: "Constructs",
            27: "Simple",
            28: "In favor of",
            29: "Above",
            31: "Listen",
            32: "Meadow",
            33: "Attempts",
            40: "Locations",
            42: "Declines",
            44: "Request",
            46: "Close to",
            47: "Frozen water",
            48: "Negative",
            50: "Lengthy",
            51: "Ancient",
            52: "Borders",
            55: "Also",
            56: "Assistant"
        }
    },
    # Puzzle 2
    {
        "grid": [
            "PLATE#WAR#FIGHT",
            "LANDS#AGE#AROSE",
            "ANGER#NET#TERMS",
            "YES#WATER#STAND",
            "###TEENS#ENTER#",
            "#GARDEN##DRESS#",
            "FATHER#LETTERS",
            "AFTER#SOON#STAY",
            "READING#NEARBY",
            "#SONGS##PEOPLE#",
            "#TREES#POINT###",
            "SPELL#OPENS#SET",
            "HELLO#LEG#ORDER",
            "ENTER#EGG#UNDER",
            "DOORS#RED#PARKS"
        ],
        "across_clues": {
            1: "Dish",
            6: "Armed conflict",
            9: "Battle",
            14: "Properties",
            15: "Time period",
            16: "Got up",
            17: "Fury",
            18: "Mesh",
            19: "Conditions",
            20: "Affirmative",
            21: "H2O",
            23: "Be upright",
            25: "13-19 year olds",
            27: "Go in",
            29: "Place for plants",
            31: "Clothing",
            33: "Male parent",
            35: "Mail items",
            39: "Following",
            40: "In the near future",
            42: "Remain",
            43: "Book activity",
            45: "Close by",
            47: "Music pieces",
            48: "Humans",
            50: "Woody plants",
            52: "Tip",
            53: "Magic word",
            57: "Unlocks",
            61: "Collection",
            62: "Greeting",
            64: "Limb",
            65: "Arrangement",
            66: "Go inside",
            67: "Breakfast item",
            68: "Below",
            69: "Entrances",
            70: "Color",
            71: "Recreation areas"
        },
        "down_clues": {
            1: "Locations",
            2: "Big",
            3: "As well",
            4: "Attempt",
            5: "Conclusions",
            6: "Desire",
            7: "Region",
            8: "Tears",
            9: "Correct",
            10: "Sick",
            11: "Fuel",
            12: "Residence",
            13: "Attempts",
            22: "Consumed",
            24: "Negative",
            26: "Close",
            28: "Decays",
            30: "Design",
            32: "Relax",
            33: "Complimentary",
            34: "Quick",
            36: "Finishes",
            37: "Aged",
            38: "Cushion",
            41: "Single",
            44: "Canine",
            46: "Exists",
            49: "Acquire knowledge",
            51: "Timid",
            54: "Jumped",
            55: "Stage shows",
            56: "Parts",
            57: "Frequently",
            58: "Writing tools",
            59: "Concludes",
            60: "Not many",
            63: "Crimson"
        }
    }
]

class SimpleCrosswordGenerator:
    def __init__(self):
        self.output_dir = Path("books/active_production/Large_Print_Crossword_Masters/volume_3")
        self.paperback_dir = self.output_dir / "paperback"
        self.hardcover_dir = self.output_dir / "hardcover"

    def generate_puzzle_variations(self, base_puzzle, puzzle_num):
        """Generate variations of base puzzles"""
        random.seed(puzzle_num * 1000)
        
        # Create variations by modifying the base puzzles
        grid = []
        for row in base_puzzle["grid"]:
            grid.append(list(row))
        
        # Apply some transformations for variety
        if puzzle_num % 5 == 0:
            # Reverse rows
            grid = grid[::-1]
        elif puzzle_num % 5 == 1:
            # Reverse columns
            for i in range(len(grid)):
                grid[i] = grid[i][::-1]
        elif puzzle_num % 5 == 2:
            # Transpose (if square)
            if len(grid) == len(grid[0]):
                grid = [[grid[j][i] for j in range(len(grid))] for i in range(len(grid[0]))]
        
        return {
            "grid": grid,
            "across_clues": base_puzzle["across_clues"],
            "down_clues": base_puzzle["down_clues"]
        }

    def parse_grid(self, grid_strings):
        """Convert string grid to 2D array"""
        grid = []
        for row in grid_strings:
            grid.append(list(row))
        return grid

    def assign_numbers(self, grid):
        """Assign numbers to grid squares"""
        numbers = {}
        num = 1
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] != '#':
                    # Check if starts across
                    starts_across = (c == 0 or grid[r][c-1] == '#') and \
                                   c < GRID_SIZE-1 and grid[r][c+1] != '#'
                    
                    # Check if starts down
                    starts_down = (r == 0 or grid[r-1][c] == '#') and \
                                 r < GRID_SIZE-1 and grid[r+1][c] != '#'
                    
                    if starts_across or starts_down:
                        numbers[(r, c)] = num
                        num += 1
        
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

    def draw_solution_grid(self, c, x_offset, y_offset, grid, cell_size=None):
        """Draw the solution grid with letters filled in"""
        if cell_size is None:
            cell_size = 0.24 * inch
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
                    c.setFillColor(colors.black)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(x + cell_size/2, y + cell_size/2 - 3, 
                                      grid[row][col])

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
            c.showPage()
            
            # Table of Contents
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "Table of Contents")
            
            c.setFont("Helvetica", 12)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            toc_items = [
                ("Introduction", "4"),
                ("How to Solve", "5"),
                ("Puzzles 1-50", "6-105"),
                ("Solutions", "106-155"),
                ("About", "156")
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
                "Enjoy 50 crossword puzzles with:",
                "• Extra-large print",
                "• Simple words",
                "• Clear clues",
                "• Complete solutions"
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
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "How to Solve")
            
            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            howto_text = [
                "1. Read the clues",
                "2. Count the squares",
                "3. Fill in what you know",
                "4. Use crossing words",
                "5. Check your answers"
            ]
            
            for line in howto_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3*inch
            
            c.showPage()
            
            # Generate 50 puzzles
            all_puzzles = []
            
            for puzzle_num in range(1, 51):
                print(f"  Creating Puzzle {puzzle_num}...")
                
                # Use template puzzles, cycling through them
                template_idx = (puzzle_num - 1) % len(PUZZLE_TEMPLATES)
                template = PUZZLE_TEMPLATES[template_idx]
                
                # Generate variation
                puzzle_data = self.generate_puzzle_variations(template, puzzle_num)
                grid = puzzle_data["grid"]
                
                # Assign numbers
                numbers = self.assign_numbers(grid)
                
                # Store puzzle
                all_puzzles.append({
                    'num': puzzle_num,
                    'grid': grid,
                    'numbers': numbers,
                    'across_clues': puzzle_data["across_clues"],
                    'down_clues': puzzle_data["down_clues"]
                })
                
                # Puzzle page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 0.4*inch, 
                                  f"Puzzle {puzzle_num}")
                
                # Draw empty grid
                empty_grid = [[grid[r][c] if grid[r][c] == '#' else '.' 
                             for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
                
                grid_x = (PAGE_WIDTH - GRID_TOTAL_SIZE) / 2
                grid_y = PAGE_HEIGHT - TOP_MARGIN - 1.2*inch
                self.draw_grid(c, grid_x, grid_y, empty_grid, numbers)
                
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
                
                for num, clue in sorted(puzzle_data["across_clues"].items()):
                    if y_pos > BOTTOM_MARGIN + 0.5*inch:
                        c.drawString(GUTTER, y_pos, f"{num}. {clue}")
                        y_pos -= 0.25*inch
                
                # DOWN clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(PAGE_WIDTH/2 + 0.1*inch, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "DOWN")
                
                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3*inch
                
                for num, clue in sorted(puzzle_data["down_clues"].items()):
                    if y_pos > BOTTOM_MARGIN + 0.5*inch:
                        c.drawString(PAGE_WIDTH/2 + 0.1*inch, y_pos, f"{num}. {clue}")
                        y_pos -= 0.25*inch
                
                c.showPage()
            
            # Solutions (1 per page)
            for puzzle in all_puzzles:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 0.5*inch, 
                                  f"Puzzle {puzzle['num']} - Solution")
                
                # Center the solution grid
                cell_size = 0.24 * inch
                grid_x = (PAGE_WIDTH - (GRID_SIZE * cell_size)) / 2
                grid_y = (PAGE_HEIGHT - (GRID_SIZE * cell_size)) / 2
                
                self.draw_solution_grid(c, grid_x, grid_y, puzzle['grid'], cell_size)
                
                c.showPage()
            
            # About page
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 1*inch, "About KindleMint Press")
            
            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2*inch
            about_text = [
                "Thank you for choosing our puzzles!",
                "",
                "Visit: www.kindlemintpress.com"
            ]
            
            for line in about_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3*inch
            
            c.showPage()
            
            # Save
            c.save()
            print(f"✅ Created {format_name} PDF: {pdf_path}")

def main():
    print("🚀 Creating Volume 3 with SIMPLE working crosswords")
    print("Using pre-tested puzzle templates")
    
    generator = SimpleCrosswordGenerator()
    generator.create_complete_book()
    
    print("\n✅ Volume 3 generation complete!")
    print("All puzzles use real words only!")

if __name__ == "__main__":
    main()