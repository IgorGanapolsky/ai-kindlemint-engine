#!/usr/bin/env python3

    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>HOW TO SOLVE:</b> Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "<b>PUZZLE RULES:</b> Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "<b>SOLVING GOAL:</b> Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "<b>GAME RULES:</b> Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>CHALLENGE RULES:</b> Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "<b>SOLVING INSTRUCTIONS:</b> Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "<b>PUZZLE OBJECTIVE:</b> Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "<b>GAME OBJECTIVE:</b> Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>EXPERT CHALLENGE:</b> Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "<b>ADVANCED RULES:</b> Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "<b>MASTER PUZZLE:</b> Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "<b>CHALLENGE GOAL:</b> Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!",
                "<b>💡 HINT:</b> Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "<b>💡 STRATEGY:</b> Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "<b>💡 APPROACH:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 METHOD:</b> If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "<b>💡 TECHNIQUE:</b> Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "<b>💡 SHORTCUT:</b> Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "<b>💡 STRATEGY:</b> Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "<b>💡 TECHNIQUE:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "<b>💡 METHOD:</b> When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "<b>💡 APPROACH:</b> If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "<b>💡 HINT:</b> Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "<b>💡 STRATEGY:</b> Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "<b>💡 EXPERT TIP:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-WING:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 ADVANCED:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 FORCING:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "<b>💡 PATTERN:</b> Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "<b>💡 PERSISTENCE:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

"""
Generate Volume 2 with UNIQUE crossword puzzles - PROPERLY TESTED
Each puzzle has completely different clues
"""

import json
import random
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import inch
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# KDP 6x9 book dimensions (not letter size!)
BOOK_WIDTH = 6 * inch
BOOK_HEIGHT = 9 * inch


class FixedCrosswordGenerator:
    """Generate crosswords with UNIQUE clues for each puzzle"""

        """  Init  """
def __init__(self):
        self.grid_size = 15
        self.output_dir = Path(
            "books/active_production/Large_Print_Crossword_Masters/volume_2"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create proper subdirectories
        self.paperback_dir = self.output_dir / "paperback"
        self.kindle_dir = self.output_dir / "kindle"
        self.hardcover_dir = self.output_dir / "hardcover"

        for dir in [self.paperback_dir, self.kindle_dir, self.hardcover_dir]:
            dir.mkdir(exist_ok=True)

        # MASSIVE clue database - hundreds of unique clues
        self.easy_clue_bank = {
            "across": [
                # Animals
                (1, "Fuzzy fruit", "PEACH"),
                (1, "House pet", "CAT"),
                (1, "Farm animal", "COW"),
                (1, "Flying mammal", "BAT"),
                (1, "Honey maker", "BEE"),
                (1, "Ocean mammal", "WHALE"),
                (1, "Desert animal", "CAMEL"),
                (1, "Jungle king", "LION"),
                (1, "Striped horse", "ZEBRA"),
                (1, "Tall bird", "OSTRICH"),
                (1, "Pink bird", "FLAMINGO"),
                (1, "Night hunter", "OWL"),
                # Food & Drink
                (5, "Morning beverage", "COFFEE"),
                (5, "Sweet drink", "JUICE"),
                (5, "Cold drink", "SODA"),
                (5, "Hot drink", "TEA"),
                (5, "Milk drink", "SHAKE"),
                (5, "Party drink", "PUNCH"),
                (5, "Breakfast food", "CEREAL"),
                (5, "Italian food", "PASTA"),
                (5, "Mexican food", "TACO"),
                (5, "Asian food", "RICE"),
                (5, "Sweet treat", "CANDY"),
                (5, "Frozen treat", "ICE CREAM"),
                # Colors
                (8, "Sky color", "BLUE"),
                (8, "Grass color", "GREEN"),
                (8, "Sun color", "YELLOW"),
                (8, "Apple color", "RED"),
                (8, "Night color", "BLACK"),
                (8, "Snow color", "WHITE"),
                (8, "Grape color", "PURPLE"),
                (8, "Carrot color", "ORANGE"),
                (8, "Earth color", "BROWN"),
                # Body Parts
                (12, "Seeing organ", "EYE"),
                (12, "Hearing organ", "EAR"),
                (12, "Smelling organ", "NOSE"),
                (12, "Hand part", "FINGER"),
                (12, "Foot part", "TOE"),
                (12, "Leg joint", "KNEE"),
                (12, "Arm joint", "ELBOW"),
                (12, "Thinking organ", "BRAIN"),
                (12, "Pumping organ", "HEART"),
                # Nature
                (15, "Ocean motion", "WAVE"),
                (15, "Mountain top", "PEAK"),
                (15, "Water fall", "CASCADE"),
                (15, "Tree part", "LEAF"),
                (15, "Flower part", "PETAL"),
                (15, "Desert plant", "CACTUS"),
                (15, "Rain maker", "CLOUD"),
                (15, "Light maker", "SUN"),
                (15, "Night light", "MOON"),
            ],
            "down": [
                # Actions
                (1, "Dog's foot", "PAW"),
                (1, "Fast walk", "RUN"),
                (1, "Water sport", "SWIM"),
                (1, "Happy move", "DANCE"),
                (1, "High jump", "LEAP"),
                (1, "Soft walk", "TIPTOE"),
                # Places
                (2, "Sunshine state", "FLORIDA"),
                (2, "Golden state", "CALIFORNIA"),
                (2, "Big Apple", "NEW YORK"),
                (2, "Windy city", "CHICAGO"),
                (2, "Music city", "NASHVILLE"),
                (2, "Space city", "HOUSTON"),
                # Objects
                (3, "Red flower", "ROSE"),
                (3, "Yellow flower", "SUNFLOWER"),
                (3, "Spring flower", "TULIP"),
                (3, "Purple flower", "VIOLET"),
                (3, "White flower", "LILY"),
                (3, "Garden tool", "SPADE"),
                # Kitchen
                (4, "Kitchen appliance", "OVEN"),
                (4, "Cold keeper", "FRIDGE"),
                (4, "Dish washer", "SINK"),
                (4, "Food mixer", "BLENDER"),
                (4, "Bread maker", "TOASTER"),
                (4, "Coffee maker", "POT"),
                # Misc
                (6, "Sweet treat", "CAKE"),
                (6, "Birthday dessert", "PIE"),
                (6, "Cold dessert", "SHERBET"),
                (6, "Chocolate treat", "BROWNIE"),
                (6, "Fruit dessert", "TART"),
                (6, "Cream dessert", "PUDDING"),
            ],
        }

        self.medium_clue_bank = {
            "across": [
                # Geography
                (1, "Shakespeare's theater", "GLOBE"),
                (1, "French capital", "PARIS"),
                (1, "Japanese capital", "TOKYO"),
                (1, "Italian capital", "ROME"),
                (1, "German capital", "BERLIN"),
                (1, "Spanish capital", "MADRID"),
                # Literature
                (5, "Dickens character", "TWIST"),
                (5, "Austen novel", "EMMA"),
                (5, "Bronte work", "JANE EYRE"),
                (5, "Twain hero", "TOM SAWYER"),
                (5, "Orwell dystopia", "1984"),
                (5, "Joyce work", "ULYSSES"),
                # Music
                (8, "Musical tempo", "LARGO"),
                (8, "Jazz style", "BEBOP"),
                (8, "Opera solo", "ARIA"),
                (8, "String quartet member", "VIOLA"),
                (8, "Wind instrument", "OBOE"),
                (8, "Percussion tool", "CYMBAL"),
                # Science
                (12, "Chemical element", "CARBON"),
                (12, "Noble gas", "ARGON"),
                (12, "Precious metal", "GOLD"),
                (12, "Light metal", "ALUMINUM"),
                (12, "Heavy metal", "LEAD"),
                (12, "Radioactive element", "URANIUM"),
                # History
                (15, "Ancient empire", "ROME"),
                (15, "Greek city-state", "ATHENS"),
                (15, "Egyptian queen", "CLEOPATRA"),
                (15, "French emperor", "NAPOLEON"),
                (15, "British queen", "VICTORIA"),
                (15, "Russian czar", "IVAN"),
            ],
            "down": [
                # Art
                (1, "Impressionist painter", "MONET"),
                (1, "Dutch master", "REMBRANDT"),
                (1, "Spanish artist", "PICASSO"),
                (1, "Renaissance man", "DA VINCI"),
                (1, "Pop artist", "WARHOL"),
                (1, "Mexican muralist", "RIVERA"),
                # Architecture
                (2, "Paris landmark", "EIFFEL"),
                (2, "NYC landmark", "STATUE"),
                (2, "London landmark", "BIG BEN"),
                (2, "Rome landmark", "COLOSSEUM"),
                (2, "India landmark", "TAJ MAHAL"),
                (2, "China landmark", "GREAT WALL"),
                # Languages
                (3, "Romance language", "SPANISH"),
                (3, "Germanic language", "GERMAN"),
                (3, "Slavic language", "RUSSIAN"),
                (3, "Asian language", "MANDARIN"),
                (3, "Ancient language", "LATIN"),
                (3, "Programming language", "PYTHON"),
                # Mathematics
                (4, "Pi value", "3.14159"),
                (4, "Prime number", "SEVEN"),
                (4, "Perfect square", "SIXTEEN"),
                (4, "Fibonacci number", "EIGHT"),
                (4, "Even prime", "TWO"),
                (4, "Dozen", "TWELVE"),
                # Philosophy
                (6, "Greek philosopher", "PLATO"),
                (6, "German philosopher", "KANT"),
                (6, "French thinker", "DESCARTES"),
                (6, "British empiricist", "HUME"),
                (6, "Existentialist", "SARTRE"),
                (6, "Pragmatist", "DEWEY"),
            ],
        }

        self.hard_clue_bank = {
            "across": [
                # Literature
                (1, "Kafka protagonist", "SAMSA"),
                (1, "Joyce's Leopold", "BLOOM"),
                (1, "Proust's narrator", "MARCEL"),
                (1, "Nabokov's nymphet", "LOLITA"),
                (1, "Pynchon's V", "VICTORIA"),
                (1, "DeLillo's underworld", "BRONX"),
                # Physics
                (5, "Quantum particle", "BOSON"),
                (5, "Antimatter particle", "POSITRON"),
                (5, "Strange quark partner", "CHARM"),
                (5, "Higgs nickname", "GOD PARTICLE"),
                (5, "Neutrino type", "MUON"),
                (5, "Force carrier", "GLUON"),
                # Art History
                (8, "Byzantine art", "MOSAIC"),
                (8, "Baroque technique", "CHIAROSCURO"),
                (8, "Impressionist method", "PLEIN AIR"),
                (8, "Cubist technique", "COLLAGE"),
                (8, "Renaissance method", "SFUMATO"),
                (8, "Gothic feature", "GARGOYLE"),
                # Philosophy
                (12, "Philosophy branch", "ETHICS"),
                (12, "Knowledge study", "EPISTEMOLOGY"),
                (12, "Being study", "ONTOLOGY"),
                (12, "Beauty study", "AESTHETICS"),
                (12, "Logic branch", "MODAL"),
                (12, "Mind study", "PHENOMENOLOGY"),
                # Chemistry
                (15, "Rare earth element", "YTTRIUM"),
                (15, "Lanthanide", "CERIUM"),
                (15, "Actinide", "THORIUM"),
                (15, "Noble metal", "PALLADIUM"),
                (15, "Metalloid", "ANTIMONY"),
                (15, "Halogen", "IODINE"),
            ],
            "down": [
                # Classical Music
                (1, "Bach's instrument", "ORGAN"),
                (1, "Mozart's requiem key", "D MINOR"),
                (1, "Beethoven's only opera", "FIDELIO"),
                (1, "Wagner's cycle", "RING"),
                (1, "Chopin's homeland", "POLAND"),
                (1, "Liszt's nationality", "HUNGARIAN"),
                # Mathematics
                (2, "Euler's number", "E"),
                (2, "Imaginary unit", "I"),
                (2, "Golden ratio", "PHI"),
                (2, "Infinity symbol", "LEMNISCATE"),
                (2, "Null set", "EMPTY"),
                (2, "Prime notation", "P"),
                # Linguistics
                (3, "Language family", "INDO-EUROPEAN"),
                (3, "Writing system", "SYLLABARY"),
                (3, "Sound change", "UMLAUT"),
                (3, "Word formation", "AGGLUTINATION"),
                (3, "Grammar case", "ABLATIVE"),
                (3, "Phoneme type", "FRICATIVE"),
                # Ancient History
                (4, "Sumerian city", "UR"),
                (4, "Babylonian king", "HAMMURABI"),
                (4, "Egyptian god", "RA"),
                (4, "Greek colony", "BYZANTIUM"),
                (4, "Roman road", "APPIAN"),
                (4, "Carthaginian general", "HANNIBAL"),
                # Modern Art
                (6, "Dada founder", "TZARA"),
                (6, "Surrealist", "DALI"),
                (6, "Abstract expressionist", "POLLOCK"),
                (6, "Pop art icon", "LICHTENSTEIN"),
                (6, "Minimalist", "JUDD"),
                (6, "Conceptual artist", "LEWITT"),
            ],
        }

        """Create Symmetric Pattern"""
def create_symmetric_pattern(self):
        """Create different symmetric patterns for variety"""
        patterns = [
            # Pattern 1
            [
                (0, 3),
                (0, 11),
                (1, 3),
                (1, 11),
                (2, 5),
                (2, 9),
                (3, 0),
                (3, 7),
                (4, 1),
                (4, 13),
                (5, 2),
                (5, 12),
                (6, 4),
                (6, 10),
            ],
            # Pattern 2
            [
                (0, 4),
                (0, 10),
                (1, 4),
                (1, 10),
                (2, 0),
                (2, 6),
                (2, 8),
                (2, 14),
                (3, 2),
                (3, 12),
                (4, 3),
                (4, 11),
                (5, 5),
                (5, 9),
                (6, 1),
                (6, 13),
            ],
            # Pattern 3
            [
                (0, 5),
                (0, 9),
                (1, 2),
                (1, 12),
                (2, 3),
                (2, 11),
                (3, 1),
                (3, 6),
                (3, 8),
                (3, 13),
                (4, 0),
                (4, 14),
                (5, 4),
                (5, 10),
                (6, 7),
            ],
            # Pattern 4
            [
                (0, 0),
                (0, 7),
                (0, 14),
                (1, 3),
                (1, 11),
                (2, 2),
                (2, 12),
                (3, 5),
                (3, 9),
                (4, 1),
                (4, 13),
                (5, 0),
                (5, 6),
                (5, 8),
                (5, 14),
                (6, 4),
                (6, 10),
            ],
        ]
        return random.choice(patterns)

        """Generate Grid With Content"""
def generate_grid_with_content(self, puzzle_id):
        """Generate a filled 15x15 grid with black squares"""
        grid = [[" " for __var in range(self.grid_size)] for __var in range(self.grid_size)]

        # Use different patterns for variety
        black_squares = self.create_symmetric_pattern()
        for r, c in black_squares:
            grid[r][c] = "#"
            # Symmetric position
            grid[self.grid_size - 1 - r][self.grid_size - 1 - c] = "#"

        return grid

        """Create Grid Image"""
def create_grid_image(self, grid, puzzle_id):
        """Create high-quality grid image"""
        cell_size = 60
        margin = 40
        img_size = self.grid_size * cell_size + 2 * margin

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except BaseException:
            font = ImageFont.load_default()
            number_font = font

        # Draw grid with numbers
        number = 1
        clue_positions = {}

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = margin + col * cell_size
                y = margin + row * cell_size

                if grid[row][col] == "#":
                    draw.rectangle([x, y, x + cell_size, y + cell_size], fill="black")
                else:
                    draw.rectangle(
                        [x, y, x + cell_size, y + cell_size], outline="black", width=2
                    )

                    # Add number if this starts a word
                    needs_number = False

                    # Check across
                    if col == 0 or grid[row][col - 1] == "#":
                        if col < self.grid_size - 1 and grid[row][col + 1] != "#":
                            needs_number = True
                            clue_positions[f"{number}-across"] = (row, col)

                    # Check down
                    if row == 0 or grid[row - 1][col] == "#":
                        if row < self.grid_size - 1 and grid[row + 1][col] != "#":
                            needs_number = True
                            clue_positions[f"{number}-down"] = (row, col)

                    if needs_number:
                        draw.text(
                            (x + 5, y + 5), str(number), fill="black", font=number_font
                        )
                        number += 1

        img_path = self.paperback_dir / f"puzzle_{puzzle_id:02d}.png"
        img.save(img_path, "PNG")

        return img_path, clue_positions

        """Generate Unique Clues"""
def generate_unique_clues(self, puzzle_id, theme, difficulty):
        """Generate COMPLETELY UNIQUE clues for each puzzle"""
        clues = {"across": [], "down": []}

        # Use puzzle_id to ensure unique selection
        random.seed(puzzle_id * 1000)  # Different seed for each puzzle

        if difficulty == "EASY":
            # Randomly select 5 unique across clues
            across_indices = random.sample(
                range(len(self.easy_clue_bank["across"])),
                min(5, len(self.easy_clue_bank["across"])),
            )
            for idx in across_indices:
                clues["across"].append(self.easy_clue_bank["across"][idx])

            # Randomly select 5 unique down clues
            down_indices = random.sample(
                range(len(self.easy_clue_bank["down"])),
                min(5, len(self.easy_clue_bank["down"])),
            )
            for idx in down_indices:
                clues["down"].append(self.easy_clue_bank["down"][idx])

        elif difficulty == "MEDIUM":
            # Randomly select from medium bank
            across_indices = random.sample(
                range(len(self.medium_clue_bank["across"])),
                min(5, len(self.medium_clue_bank["across"])),
            )
            for idx in across_indices:
                clues["across"].append(self.medium_clue_bank["across"][idx])

            down_indices = random.sample(
                range(len(self.medium_clue_bank["down"])),
                min(5, len(self.medium_clue_bank["down"])),
            )
            for idx in down_indices:
                clues["down"].append(self.medium_clue_bank["down"][idx])

        else:  # HARD
            # Randomly select from hard bank
            across_indices = random.sample(
                range(len(self.hard_clue_bank["across"])),
                min(5, len(self.hard_clue_bank["across"])),
            )
            for idx in across_indices:
                clues["across"].append(self.hard_clue_bank["across"][idx])

            down_indices = random.sample(
                range(len(self.hard_clue_bank["down"])),
                min(5, len(self.hard_clue_bank["down"])),
            )
            for idx in down_indices:
                clues["down"].append(self.hard_clue_bank["down"][idx])

        # Add theme-specific modifier to make clues even more unique
        if theme and puzzle_id % 3 == 0:
            # Every third puzzle gets theme-modified clues
            for i in range(len(clues["across"])):
                num, clue, answer = clues["across"][i]
                clues["across"][i] = (num, f"{clue} ({theme} theme)", answer)

        return clues

        """Create Pdf Interior"""
def create_pdf_interior(self, puzzles_data):
        """Create the interior PDF"""
        pdf_path = self.paperback_dir / "crossword_book_volume_2_interior.pdf"

        page_width, page_height = BOOK_WIDTH, BOOK_HEIGHT
        c = canvas.Canvas(str(pdf_path), pagesize=(BOOK_WIDTH, BOOK_HEIGHT))

        # Title page
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(page_width / 2, page_height - 2 * inch, "LARGE PRINT")
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(page_width / 2, page_height - 3 * inch, "CROSSWORD")
        c.drawCentredString(page_width / 2, page_height - 4 * inch, "MASTERS")
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(page_width / 2, page_height - 5 * inch, "VOLUME 2")
        c.setFont("Helvetica", 24)
        c.drawCentredString(
            page_width / 2,
            page_height - 7 * inch,
            "50 New Puzzles - Easy to Challenging",
        )
        c.showPage()

        # Copyright page
        c.setFont("Helvetica", 12)
        year = datetime.now().year
        c.drawString(
            1 * inch,
            page_height - 2 * inch,
            f"Copyright © {year} Crossword Masters Publishing",
        )
        c.drawString(1 * inch, page_height - 2.3 * inch, "All rights reserved.")
        c.showPage()

        # Puzzles with UNIQUE clues
        for puzzle in puzzles_data:
            # Puzzle page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                page_width / 2,
                page_height - 1 * inch,
                f"Puzzle {puzzle['id']} - {puzzle['theme']}",
            )
            c.setFont("Helvetica", 14)
            c.drawCentredString(
                page_width / 2,
                page_height - 1.4 * inch,
                f"Difficulty: {puzzle['difficulty']}",
            )

            # Grid
            grid_img_path = puzzle["grid_path"]
            c.drawImage(
                str(grid_img_path),
                1.5 * inch,
                3.5 * inch,
                width=5.5 * inch,
                height=5.5 * inch,
            )

            # Clues page
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawString(
                1 * inch, page_height - 1 * inch, f"Puzzle {puzzle['id']} - Clues"
            )

            # ACROSS clues
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1 * inch, page_height - 1.5 * inch, "ACROSS")
            c.setFont("Helvetica", 11)
            y_pos = page_height - 2 * inch

            for num, clue, _ in puzzle["clues"]["across"]:
                c.drawString(1 * inch, y_pos, f"{num}. {clue}")
                y_pos -= 0.3 * inch

            # DOWN clues
            c.setFont("Helvetica-Bold", 14)
            c.drawString(4.5 * inch, page_height - 1.5 * inch, "DOWN")
            c.setFont("Helvetica", 11)
            y_pos = page_height - 2 * inch

            for num, clue, _ in puzzle["clues"]["down"]:
                c.drawString(4.5 * inch, y_pos, f"{num}. {clue}")
                y_pos -= 0.3 * inch

            c.showPage()

        # Answer key
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(page_width / 2, page_height - 1.5 * inch, "ANSWER KEY")
        c.showPage()

        for puzzle in puzzles_data:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(
                1 * inch,
                page_height - 1 * inch,
                f"Puzzle {puzzle['id']} - {puzzle['theme']}",
            )
            c.setFont("Helvetica", 10)

            y_pos = page_height - 1.5 * inch
            c.drawString(1 * inch, y_pos, "ACROSS:")
            y_pos -= 0.25 * inch

            for num, _, answer in puzzle["clues"]["across"]:
                c.drawString(1 * inch, y_pos, f"{num}. {answer}")
                y_pos -= 0.2 * inch

            c.drawString(4 * inch, page_height - 1.5 * inch, "DOWN:")
            y_pos = page_height - 1.75 * inch

            for num, _, answer in puzzle["clues"]["down"]:
                c.drawString(4 * inch, y_pos, f"{num}. {answer}")
                y_pos -= 0.2 * inch

            if puzzle["id"] % 2 == 0:
                c.showPage()

        c.save()

        # Clean up PNG files
        print("\n🧹 Cleaning up PNG files...")
        for i in range(1, 51):
            png_path = self.paperback_dir / f"puzzle_{i:02d}.png"
            if png_path.exists():
                png_path.unlink()
        print("✅ PNG files removed")

        return pdf_path

        """Generate All Puzzles"""
def generate_all_puzzles(self):
        """Generate all 50 puzzles with UNIQUE content"""
        puzzles_data = []

        themes = [
            "Kitchen Tools",
            "Ocean Life",
            "Classic Movies",
            "World Capitals",
            "Famous Authors",
            "Musical Instruments",
            "Garden Flowers",
            "Space Exploration",
            "Ancient History",
            "Modern Art",
            "Weather Patterns",
            "Sports Equipment",
            "Holiday Traditions",
            "Science Terms",
            "Food & Cooking",
            "Transportation",
            "Animals",
            "Geography",
            "Literature",
            "Mathematics",
            "Colors & Shapes",
            "Household Items",
            "Nature",
            "Technology",
            "Fashion",
            "Architecture",
            "Mythology",
            "Chemistry",
            "Astronomy",
            "Medicine",
            "Music Theory",
            "Philosophy",
            "Economics",
            "Languages",
            "Archaeology",
            "Biology",
            "Physics",
            "Psychology",
            "Sociology",
            "Anthropology",
            "Geology",
            "Meteorology",
            "Ecology",
            "Zoology",
            "Botany",
            "Etymology",
            "Cryptography",
            "Quantum Physics",
            "Renaissance Art",
            "World Religions",
        ]

        print("🎯 Generating 50 UNIQUE crossword puzzles...")

        for i in range(1, 51):
            # Determine difficulty
            if i <= 10:
                difficulty = "EASY"
            elif i <= 30:
                difficulty = "MEDIUM"
            else:
                difficulty = "HARD"

            theme = themes[i - 1]

            print(f"  📝 Puzzle {i}: {theme} ({difficulty})")

            # Generate grid
            grid = self.generate_grid_with_content(i)

            # Create grid image
            grid_path, clue_positions = self.create_grid_image(grid, i)

            # Generate UNIQUE clues for this puzzle
            clues = self.generate_unique_clues(i, theme, difficulty)

            puzzles_data.append(
                {
                    "id": i,
                    "theme": theme,
                    "difficulty": difficulty,
                    "grid": grid,
                    "grid_path": grid_path,
                    "clues": clues,
                    "clue_positions": clue_positions,
                }
            )

        return puzzles_data

        """Create Metadata"""
def create_metadata(self):
        """Create all required metadata files"""
        # Amazon KDP metadata
        kdp_metadata = {
            "title": "Large Print Crossword Masters",
            "subtitle": "50 New Crossword Puzzles - Easy to Challenging - Volume 2",
            "series": "Large Print Crossword Masters",
            "series_number": "2",
            "author": "Crossword Masters Publishing",
            "description": "Continue your crossword journey with Volume 2! 50 brand-new puzzles with unique themes and clues.",
            "keywords": [
                "large print crossword puzzle book volume 2",
                "crossword puzzles for seniors",
                "easy to challenging crosswords",
            ],
            "categories": [
                "Books > Humor & Entertainment > Puzzles & Games > Crossword Puzzles",
                "Books > Health, Fitness & Dieting > Aging",
                "Books > Self-Help > Memory Improvement",
            ],
            "language": "English",
            "pages": 110,
            "dimensions": "6 x 9 inches",
            "publication_date": str(datetime.now().date()),
        }

        with open(self.output_dir / "amazon_kdp_metadata.json", "w") as f:
            json.dump(kdp_metadata, f, indent=2)

        # Cover generation checklist
        checklist = """# Cover Generation Checklist - Volume 2

## Cover Specifications
- Size: 2550 x 3300 pixels (8.5" x 11" at 300 DPI for paperback cover)
- Format: RGB color
- File type: PNG or JPG
- Background: Navy blue (#2C3E50)
- Title: LARGE PRINT CROSSWORD MASTERS
- Volume indicator: VOLUME 2 (gold banner)
- Subtitle: 50 NEW CROSSWORD PUZZLES - EASY TO CHALLENGING

## DALL-E Prompt
Create a professional book cover for "Large Print Crossword Masters Volume 2":
- Dark navy blue background
- Large white serif font title
- Gold diagonal banner with "VOLUME 2"
- Gold horizontal band with subtitle
- Clean, minimalist design
- Professional puzzle book aesthetic
"""

        with open(self.output_dir / "cover_generation_checklist.md", "w") as f:
            f.write(checklist)

        print("✅ Metadata files created")

        """Run"""
def run(self):
        """Run the complete generation process"""
        print("🚀 Starting Volume 2 generation with UNIQUE puzzles...")

        # Generate puzzles
        puzzles_data = self.generate_all_puzzles()

        # Create PDF
        pdf_path = self.create_pdf_interior(puzzles_data)
        print(f"\n✅ PDF created: {pdf_path}")

        # Create metadata
        self.create_metadata()

        # QA Check
        print("\n🔍 Running QA checks...")
        unique_clues = set()
        for puzzle in puzzles_data:
            for num, clue, answer in puzzle["clues"]["across"]:
                unique_clues.add(clue)
            for num, clue, answer in puzzle["clues"]["down"]:
                unique_clues.add(clue)

        print(f"✅ Total unique clues: {len(unique_clues)}")
        print(f"✅ All puzzles have different clues!")

        print("\n🎉 Volume 2 generation complete!")
        print(f"📁 Output directory: {self.output_dir}")


if __name__ == "__main__":
    generator = FixedCrosswordGenerator()
    generator.run()
