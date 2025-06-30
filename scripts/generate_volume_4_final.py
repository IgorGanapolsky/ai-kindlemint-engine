#!/usr/bin/env python3
"""
Create crossword puzzles for Volume 4 with UNIQUE solutions for each puzzle
Building on Volume 4's success with enhanced word variety
"""

from volume_4_clue_generator import Volume4ClueGenerator
import json
import random
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

sys.path.append(str(Path(__file__).parent))

# 6×9 book dimensions (KDP Standard)
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


class Volume4CrosswordGenerator:
    def __init__(self):
        self.output_dir = Path(
            "books/active_production/Large_Print_Crossword_Masters/volume_4"
        )
        self.paperback_dir = self.output_dir / "paperback"
        self.hardcover_dir = self.output_dir / "hardcover"

        # Initialize the professional clue generator for Volume 4
        self.clue_generator = Volume4ClueGenerator()

        # Expanded word database for Volume 4 with fresh variety
        self.word_database = {
            "3": [
                "CAT",
                "DOG",
                "SUN",
                "RUN",
                "EAT",
                "RED",
                "YES",
                "TOP",
                "ARM",
                "LEG",
                "EYE",
                "EAR",
                "BIG",
                "OLD",
                "NEW",
                "HOT",
                "ICE",
                "FLY",
                "RAN",
                "SAT",
                "BED",
                "CUP",
                "HAT",
                "JAR",
                "KEY",
                "MAN",
                "NET",
                "OWL",
                "PEN",
                "RAT",
                "TEA",
                "SEA",
                "SKY",
                "BOX",
                "FOX",
                "TAX",
                "WAX",
                "MIX",
                "FIX",
                "SIX",
                "BAG",
                "TAG",
                "RAG",
                "JOG",
                "LOG",
                "FOG",
                "HOG",
                "COG",
                "BOG",
                "DIG",
                "PIG",
                "FIG",
                "WIG",
                "RIG",
                "BIT",
                "HIT",
                "SIT",
                "FIT",
                "KIT",
                "WIT",
                "BAT",
                "MAT",
                "PAT",
                "FAT",
                "VAT",
                "BET",
                "GET",
                "JET",
                "LET",
                "MET",
                "SET",
                "VET",
                "WET",
                "YET",
                "PET",
                "CUT",
                "GUT",
                "HUT",
                "JUT",
                "NUT",
                "PUT",
                "RUT",
                "BUT",
                "BUN",
                "FUN",
                "GUN",
                "PUN",
                "SUM",
                "RUM",
                "GUM",
            ],
            "4": [
                "LOVE",
                "LIFE",
                "HOME",
                "BOOK",
                "TIME",
                "YEAR",
                "HAND",
                "DOOR",
                "FOOD",
                "TREE",
                "BIRD",
                "FISH",
                "RAIN",
                "SNOW",
                "BLUE",
                "GOLD",
                "FAST",
                "SLOW",
                "HOPE",
                "CARE",
                "WIND",
                "STAR",
                "MOON",
                "LAKE",
                "HILL",
                "ROSE",
                "KING",
                "SHIP",
                "ROAD",
                "GIFT",
                "MIND",
                "SOUL",
                "SONG",
                "GAME",
                "PLAY",
                "WORK",
                "REST",
                "BEST",
                "WEST",
                "EAST",
                "DARK",
                "PARK",
                "MARK",
                "BARK",
                "FARM",
                "WARM",
                "HARM",
                "CALM",
                "PALM",
                "BALM",
                "WALK",
                "TALK",
                "FOLK",
                "BULK",
                "SILK",
                "MILK",
                "HELP",
                "KELP",
                "YELP",
                "BELT",
                "MELT",
                "FELT",
                "PELT",
                "SALT",
                "HALT",
                "BOLT",
                "JOLT",
                "VOLT",
                "COLD",
                "BOLD",
                "FOLD",
                "HOLD",
                "TOLD",
                "SOLD",
                "MILD",
                "WILD",
                "GILD",
                "PILL",
                "FILL",
                "MILL",
                "TILL",
                "WILL",
                "BILL",
                "KILL",
                "DILL",
                "HILL",
                "CALL",
                "FALL",
                "HALL",
                "MALL",
                "TALL",
                "WALL",
                "BALL",
                "DOLL",
                "POLL",
                "TOLL",
                "ROLL",
                "BOWL",
                "FOWL",
                "HOWL",
            ],
            "5": [
                "HOUSE",
                "MUSIC",
                "DANCE",
                "SMILE",
                "HEART",
                "LIGHT",
                "NIGHT",
                "WATER",
                "EARTH",
                "OCEAN",
                "HAPPY",
                "QUIET",
                "BRAVE",
                "SWEET",
                "FRESH",
                "CLEAN",
                "PEACE",
                "DREAM",
                "ANGEL",
                "MAGIC",
                "CLOUD",
                "FIELD",
                "RIVER",
                "BEACH",
                "PIANO",
                "CHAIR",
                "TABLE",
                "PHONE",
                "BREAD",
                "FRUIT",
                "MOUSE",
                "HORSE",
                "GOOSE",
                "MOOSE",
                "LOOSE",
                "NOOSE",
                "JUICE",
                "TRUCE",
                "BRUCE",
                "DEUCE",
                "VOICE",
                "NOISE",
                "POISE",
                "HOIST",
                "MOIST",
                "JOINT",
                "POINT",
                "FAINT",
                "PAINT",
                "SAINT",
                "QUINT",
                "PRINT",
                "FLINT",
                "GLINT",
                "STINT",
                "BRAIN",
                "GRAIN",
                "TRAIN",
                "DRAIN",
                "PLAIN",
                "CHAIN",
                "STAIN",
                "SPAIN",
                "SPRAIN",
                "CRANE",
                "PLANE",
                "FLAME",
                "FRAME",
                "BLAME",
                "SHAME",
                "GRAPE",
                "DRAPE",
                "SHAPE",
                "TAPE",
                "CAPE",
                "GAPE",
                "NAPE",
                "PLACE",
                "SPACE",
                "GRACE",
                "TRACE",
                "BRACE",
                "LACE",
                "PACE",
                "FACE",
                "RACE",
                "MACE",
                "SLICE",
                "PRICE",
                "SPICE",
                "TWICE",
                "THRICE",
                "SPLICE",
                "TRICK",
                "BRICK",
                "STICK",
                "CLICK",
                "THICK",
                "QUICK",
                "SLICK",
            ],
            "6": [
                "GARDEN",
                "WINDOW",
                "MEMORY",
                "FAMILY",
                "FRIEND",
                "SUMMER",
                "WINTER",
                "SPRING",
                "AUTUMN",
                "BEAUTY",
                "WISDOM",
                "COURAGE",
                "GENTLE",
                "SIMPLE",
                "NATURE",
                "FOREST",
                "FLOWER",
                "SUNSET",
                "BRIDGE",
                "CASTLE",
                "COFFEE",
                "DINNER",
                "PICNIC",
                "TRAVEL",
                "CAMERA",
                "LETTER",
                "PENCIL",
                "BASKET",
                "MIRROR",
                "CANDLE",
                "BOTTLE",
                "BATTLE",
                "CATTLE",
                "RATTLE",
                "SETTLE",
                "METTLE",
                "KETTLE",
                "NETTLE",
                "LITTLE",
                "MIDDLE",
                "FIDDLE",
                "RIDDLE",
                "CUDDLE",
                "HUDDLE",
                "MUDDLE",
                "PUDDLE",
                "BUBBLE",
                "RUBBLE",
                "TUMBLE",
                "HUMBLE",
                "FUMBLE",
                "RUMBLE",
                "JUMBLE",
                "MUMBLE",
                "STUMBLE",
                "CRUMBLE",
                "GRUMBLE",
                "SCRAMBLE",
                "BRAMBLE",
                "GAMBLE",
                "RAMBLE",
                "SAMPLE",
                "TEMPLE",
                "SIMPLE",
                "DIMPLE",
                "PIMPLE",
                "RIPPLE",
                "TIPPLE",
                "NIPPLE",
                "CRIPPLE",
                "TRIPLE",
                "PURPLE",
                "COUPLE",
                "SUPPLE",
                "TOPPLE",
                "TOGGLE",
                "BOGGLE",
                "GOGGLE",
                "JOGGLE",
                "WIGGLE",
                "GIGGLE",
                "JIGGLE",
                "NIGGLE",
                "WRIGGLE",
                "SNUGGLE",
                "SMUGGLE",
                "JUGGLE",
                "STRUGGLE",
                "PADDLE",
                "SADDLE",
                "WADDLE",
                "STRADDLE",
                "CUDDLE",
                "MUDDLE",
                "PUDDLE",
                "HUDDLE",
                "NEEDLE",
                "BEADLE",
                "WHEEDLE",
                "DOODLE",
            ],
            "7": [
                "MORNING",
                "EVENING",
                "JOURNEY",
                "FREEDOM",
                "RAINBOW",
                "SUNSHINE",
                "LAUGHTER",
                "HARMONY",
                "MYSTERY",
                "PICTURE",
                "HEALTHY",
                "PERFECT",
                "AMAZING",
                "CRYSTAL",
                "DIAMOND",
                "TREASURE",
                "COMFORT",
                "BLESSED",
                "PROMISE",
                "WELCOME",
                "KITCHEN",
                "BEDROOM",
                "LIBRARY",
                "HOLIDAY",
                "WEEKEND",
                "SUNRISE",
                "FEELING",
                "WEATHER",
                "PRESENT",
                "HISTORY",
                "CHICKEN",
                "THICKEN",
                "QUICKEN",
                "SLICKEN",
                "STRICKEN",
                "BRACKEN",
                "BLACKEN",
                "SLACKEN",
                "CRACKER",
                "TRACKER",
                "PACKER",
                "HACKER",
                "BACKER",
                "ATTACKER",
                "HIJACKER",
                "STACKER",
                "SMACKER",
                "WHACKER",
                "QUACKER",
                "SLACKER",
                "CLACKER",
                "SNACKER",
                "BLOCKER",
                "MOCKER",
                "DOCKER",
                "LOCKER",
                "ROCKER",
                "SHOCKER",
                "KNOCKER",
                "STOCKER",
                "CHECKER",
                "WRECKER",
                "PECKER",
                "DECKER",
                "NECKER",
                "TRUCKER",
                "PUCKER",
                "MUCKER",
                "SUCKER",
                "TUCKER",
                "CLICKER",
                "FLICKER",
                "SLICKER",
                "THICKER",
                "KICKER",
                "LICKER",
                "PICKER",
                "SICKER",
                "TICKER",
                "WICKER",
                "STICKER",
                "PRICKER",
                "SNICKER",
                "QUICKER",
                "TRICKER",
                "BRISKER",
                "WHISKER",
                "FRISKER",
                "DRINKER",
                "THINKER",
                "BLINKER",
                "CLINKER",
                "SLINKER",
                "TINKER",
                "WINKER",
                "SINKER",
                "LINKER",
                "PINKER",
                "FLANKER",
                "BLANKER",
            ],
        }

        # Initialize used words tracker for each puzzle
        self.used_words_by_puzzle = {}

    def get_clue_for_word(self, word, puzzle_num):
        """Get a unique clue for a word, varying by puzzle number"""
        # Use the professional clue generator to get varied clues
        clue = self.clue_generator.get_clue(
            word, difficulty="medium", puzzle_num=puzzle_num
        )
        if clue:
            return clue
        else:
            # Fallback to a generic clue only if absolutely necessary
            return f"Word meaning {word.lower()}"

    def create_filled_grid(self, puzzle_num):
        """Create a crossword grid with ACTUAL WORDS filled in - UNIQUE for each puzzle"""
        grid = [["#" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        solution = [["#" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Initialize used words for this puzzle if not exists
        if puzzle_num not in self.used_words_by_puzzle:
            self.used_words_by_puzzle[puzzle_num] = set()

        # Use puzzle number as seed for consistent but unique patterns
        puzzle_seed = puzzle_num * 1000 + hash(str(puzzle_num))
        random.seed(puzzle_seed)

        # Place horizontal words - create truly unique patterns
        placed_words = []

        # Generate unique pattern based on puzzle number
        # Use more variation in patterns
        base_patterns = [
            # Pattern 1: Dense top/bottom
            [
                (0, 0, 7),
                (0, 8, 6),
                (2, 1, 6),
                (2, 8, 5),
                (4, 0, 5),
                (4, 6, 4),
                (4, 11, 4),
                (6, 2, 7),
                (6, 10, 5),
                (8, 0, 6),
                (8, 7, 7),
                (10, 1, 5),
                (10, 7, 6),
                (12, 0, 7),
                (12, 8, 6),
                (14, 2, 5),
                (14, 8, 6),
            ],
            # Pattern 2: Centered design
            [
                (1, 1, 6),
                (1, 8, 5),
                (3, 0, 4),
                (3, 5, 5),
                (3, 11, 4),
                (5, 2, 7),
                (5, 10, 4),
                (7, 0, 6),
                (7, 7, 7),
                (9, 1, 4),
                (9, 6, 5),
                (9, 12, 3),
                (11, 0, 7),
                (11, 8, 6),
                (13, 2, 5),
                (13, 8, 5),
            ],
            # Pattern 3: Diagonal emphasis
            [
                (0, 2, 6),
                (0, 9, 5),
                (2, 0, 5),
                (2, 6, 7),
                (4, 1, 4),
                (4, 6, 3),
                (4, 10, 5),
                (6, 0, 7),
                (6, 8, 6),
                (8, 2, 5),
                (8, 8, 6),
                (10, 0, 6),
                (10, 7, 7),
                (12, 1, 5),
                (12, 7, 6),
                (14, 0, 4),
                (14, 5, 5),
                (14, 11, 4),
            ],
            # Pattern 4: Symmetric
            [
                (0, 0, 6),
                (0, 7, 3),
                (0, 11, 4),
                (2, 1, 7),
                (2, 9, 5),
                (4, 0, 5),
                (4, 6, 6),
                (6, 2, 4),
                (6, 7, 7),
                (8, 0, 7),
                (8, 8, 6),
                (10, 1, 6),
                (10, 8, 5),
                (12, 0, 4),
                (12, 5, 5),
                (12, 11, 4),
                (14, 2, 7),
                (14, 10, 5),
            ],
            # Pattern 5: Open center
            [
                (0, 1, 7),
                (0, 9, 5),
                (2, 0, 6),
                (2, 7, 7),
                (4, 2, 5),
                (4, 8, 6),
                (6, 0, 4),
                (6, 5, 5),
                (6, 11, 4),
                (8, 1, 6),
                (8, 8, 6),
                (10, 0, 7),
                (10, 8, 5),
                (12, 2, 6),
                (12, 9, 5),
                (14, 0, 5),
                (14, 6, 7),
            ],
        ]

        # Mix patterns based on puzzle number for more variety
        pattern_index = puzzle_num % len(base_patterns)
        horizontal_slots = base_patterns[pattern_index].copy()

        # Shuffle slots for this specific puzzle
        random.shuffle(horizontal_slots)

        # Place horizontal words with unique word selection
        for row, col, length in horizontal_slots:
            if (
                str(length) in self.word_database
                and row < GRID_SIZE
                and col + length <= GRID_SIZE
            ):
                available_words = [
                    w
                    for w in self.word_database[str(length)]
                    if w not in self.used_words_by_puzzle[puzzle_num]
                ]

                if not available_words:
                    # Reset if we've used all words of this length
                    available_words = self.word_database[str(length)].copy()

                # Shuffle with puzzle-specific seed
                random.shuffle(available_words)

                # Select word based on position and puzzle number
                word_index = (puzzle_num + row + col) % len(available_words)
                word = available_words[word_index]

                # Track used word
                self.used_words_by_puzzle[puzzle_num].add(word)

                # Place word in grid
                for i, letter in enumerate(word):
                    if col + i < GRID_SIZE:
                        grid[row][col + i] = "."
                        solution[row][col + i] = letter

                placed_words.append(
                    {
                        "word": word,
                        "row": row,
                        "col": col,
                        "direction": "across",
                        "clue": self.get_clue_for_word(word, puzzle_num),
                    }
                )

        # Add vertical words at intersections with unique selections
        vertical_patterns = [
            [
                (0, 0, 5),
                (0, 3, 7),
                (0, 6, 6),
                (0, 9, 5),
                (0, 12, 6),
                (2, 2, 5),
                (4, 5, 6),
                (6, 8, 5),
                (8, 11, 7),
            ],
            [
                (0, 1, 6),
                (0, 4, 5),
                (0, 7, 7),
                (0, 10, 5),
                (0, 13, 4),
                (1, 3, 6),
                (3, 6, 5),
                (5, 9, 6),
                (7, 12, 5),
            ],
            [
                (0, 2, 7),
                (0, 5, 6),
                (0, 8, 5),
                (0, 11, 6),
                (0, 14, 5),
                (2, 0, 5),
                (4, 4, 6),
                (6, 7, 7),
                (8, 10, 5),
            ],
            [
                (0, 0, 6),
                (0, 3, 5),
                (0, 6, 7),
                (0, 9, 6),
                (0, 12, 5),
                (1, 2, 5),
                (3, 5, 6),
                (5, 8, 5),
                (7, 11, 6),
            ],
            [
                (0, 1, 5),
                (0, 4, 7),
                (0, 7, 6),
                (0, 10, 5),
                (0, 13, 6),
                (2, 3, 5),
                (4, 6, 6),
                (6, 9, 7),
                (8, 12, 5),
            ],
        ]

        vertical_index = (puzzle_num + 7) % len(vertical_patterns)
        vertical_slots = vertical_patterns[vertical_index].copy()
        random.shuffle(vertical_slots)

        for row, col, length in vertical_slots:
            if (
                str(length) in self.word_database
                and col < GRID_SIZE
                and row + length <= GRID_SIZE
            ):
                # Find word that matches existing letters
                available_words = [
                    w
                    for w in self.word_database[str(length)]
                    if w not in self.used_words_by_puzzle[puzzle_num]
                ]

                if not available_words:
                    available_words = self.word_database[str(length)].copy()

                random.shuffle(available_words)

                for word in available_words:
                    valid = True
                    for i, letter in enumerate(word):
                        if row + i < GRID_SIZE:
                            if (
                                solution[row + i][col] != "#"
                                and solution[row + i][col] != letter
                            ):
                                valid = False
                                break

                    if valid:
                        # Track used word
                        self.used_words_by_puzzle[puzzle_num].add(word)

                        # Place word
                        for i, letter in enumerate(word):
                            if row + i < GRID_SIZE:
                                grid[row + i][col] = "."
                                solution[row + i][col] = letter

                        placed_words.append(
                            {
                                "word": word,
                                "row": row,
                                "col": col,
                                "direction": "down",
                                "clue": self.get_clue_for_word(word, puzzle_num),
                            }
                        )
                        break

        # Reset random seed
        random.seed()

        return grid, solution, placed_words

    def assign_numbers(self, grid, placed_words=None):
        """Assign numbers to cells that start words"""
        if placed_words is None:
            # Fallback to old method if no word list provided
            return self._assign_numbers_by_pattern(grid)

        # Collect all word start positions
        word_starts = set()
        for word_info in placed_words:
            word_starts.add((word_info["row"], word_info["col"]))

        # Sort positions by row, then column for consistent numbering
        sorted_positions = sorted(word_starts)

        # Assign numbers to each position
        numbers = {}
        for i, (row, col) in enumerate(sorted_positions):
            numbers[(row, col)] = i + 1

        return numbers

    def _assign_numbers_by_pattern(self, grid):
        """Original numbering method based on grid pattern detection"""
        numbers = {}
        current_num = 1

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if grid[row][col] != "#":
                    needs_number = False

                    # Check if starts an across word
                    if col == 0 or grid[row][col - 1] == "#":
                        if col < GRID_SIZE - 1 and grid[row][col + 1] != "#":
                            needs_number = True

                    # Check if starts a down word
                    if row == 0 or grid[row - 1][col] == "#":
                        if row < GRID_SIZE - 1 and grid[row + 1][col] != "#":
                            needs_number = True

                    if needs_number:
                        numbers[(row, col)] = current_num
                        current_num += 1

        return numbers

    def draw_grid(self, c, x_offset, y_offset, grid, numbers, solution=None):
        """Draw crossword grid - empty for puzzle, filled for answer key"""
        c.setLineWidth(1.5)

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = x_offset + (col * CELL_SIZE)
                y = y_offset + ((GRID_SIZE - 1 - row) * CELL_SIZE)

                if grid[row][col] == "#":
                    # Black square
                    c.setFillColor(colors.black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=0)
                else:
                    # White square
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=1)

                    # Add number if needed
                    cell_num = numbers.get((row, col))
                    if cell_num:
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica", 7)
                        c.drawString(x + 2, y + CELL_SIZE - 9, str(cell_num))

                    # Add solution letter if this is answer key
                    if solution and solution[row][col] != "#":
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica-Bold", 12)
                        c.drawCentredString(
                            x + CELL_SIZE / 2, y + CELL_SIZE / 2 - 4, solution[row][col]
                        )

    def create_complete_book(self):
        """Create the complete crossword book with UNIQUE puzzles for Volume 4"""
        print("🔧 Creating Volume 4 with UNIQUE solutions for each puzzle...")

        # Create for both paperback and hardcover
        for output_dir in [self.paperback_dir, self.hardcover_dir]:
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = (
                output_dir
                / "Large_Print_Crossword_Masters_-_Volume_4_interior_FINAL.pdf"
            )

            c = canvas.Canvas(str(pdf_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

            # Title page
            c.setFont("Helvetica-Bold", 32)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2 * inch, "LARGE PRINT")
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2.6 * inch, "CROSSWORD")
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3.2 * inch, "MASTERS")

            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 4.2 * inch, "VOLUME 3")

            c.setFont("Helvetica", 16)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - 5.2 * inch,
                "50 Challenging Crossword Puzzles",
            )
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 5.6 * inch, "for Seniors")

            c.setFont("Helvetica", 14)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT - 7 * inch, "Senior Puzzle Studio"
            )

            c.showPage()

            # Table of Contents
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch,
                "Table of Contents",
            )

            c.setFont("Helvetica", 12)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch
            c.drawString(
                GUTTER, y_pos, "Introduction.........................................3"
            )
            y_pos -= 0.3 * inch
            c.drawString(GUTTER, y_pos, "How to Solve Crosswords...................4")
            y_pos -= 0.3 * inch
            c.drawString(
                GUTTER, y_pos, "Puzzles 1-50................................5-104"
            )
            y_pos -= 0.3 * inch
            c.drawString(
                GUTTER, y_pos, "Answer Key...............................105-156"
            )

            c.showPage()

            # Introduction page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch, "Introduction"
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch
            intro_text = [
                "Welcome to Large Print Crossword Masters Volume 4!",
                "",
                "This collection features 50 challenging crossword puzzles",
                "specifically designed for seniors and puzzle enthusiasts.",
                "Each puzzle uses large, clear print that's easy on the eyes,",
                "with carefully crafted clues that stimulate your mind while",
                "remaining enjoyable to solve.",
                "",
                "Each puzzle in this volume is completely unique, with",
                "different word selections and patterns to keep you engaged.",
                "All answers use common English words, and complete",
                "solution grids are provided at the back of the book.",
                "",
                "Happy puzzling!",
            ]

            for line in intro_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch

            c.showPage()

            # How to Solve page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch,
                "How to Solve Crosswords",
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch
            howto_text = [
                "1. Start with the clues you know for certain.",
                "",
                "2. Fill in these answers lightly in pencil.",
                "",
                "3. Use the crossing letters to help solve",
                "   intersecting words.",
                "",
                "4. Look for common word patterns and endings",
                "   (-ING, -ED, -ER, etc.)",
                "",
                "5. If stuck, try a different section of the puzzle",
                "   and come back later.",
                "",
                "6. Check your answers with the solution key",
                "   at the back of the book.",
            ]

            for line in howto_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch

            c.showPage()

            # Store all puzzles for answer key
            all_puzzles = []

            # Generate 50 UNIQUE puzzles
            for puzzle_num in range(1, 51):
                print(f"  📝 Creating Unique Puzzle {puzzle_num}/50")

                # Create puzzle with actual words - UNIQUE for each puzzle
                grid, solution, placed_words = self.create_filled_grid(puzzle_num)
                numbers = self.assign_numbers(grid, placed_words)

                # Store for answer key
                all_puzzles.append(
                    {
                        "num": puzzle_num,
                        "grid": grid,
                        "solution": solution,
                        "numbers": numbers,
                        "words": placed_words,
                    }
                )

                # Puzzle page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Puzzle {puzzle_num}",
                )

                # Draw empty grid for solving
                grid_x = (PAGE_WIDTH - GRID_TOTAL_SIZE) / 2
                grid_y = (PAGE_HEIGHT - GRID_TOTAL_SIZE) / 2 - 0.5 * inch
                self.draw_grid(c, grid_x, grid_y, grid, numbers)

                c.showPage()

                # Clues page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Puzzle {puzzle_num} - Clues",
                )

                # Separate words by direction
                across_words = [w for w in placed_words if w["direction"] == "across"]
                down_words = [w for w in placed_words if w["direction"] == "down"]

                # Sort by position
                across_words.sort(key=lambda w: (w["row"], w["col"]))
                down_words.sort(key=lambda w: (w["col"], w["row"]))

                # Across clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "ACROSS")

                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch
                for word_info in across_words[:20]:
                    clue_num = numbers.get((word_info["row"], word_info["col"]), "?")
                    clue_text = f"{clue_num}. {word_info['clue']}"
                    if len(clue_text) > 45:
                        clue_text = clue_text[:42] + "..."
                    c.drawString(GUTTER, y_pos, clue_text)
                    y_pos -= 0.25 * inch

                # Down clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(
                    PAGE_WIDTH / 2 + 0.1 * inch,
                    PAGE_HEIGHT - TOP_MARGIN - 1 * inch,
                    "DOWN",
                )

                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch
                for word_info in down_words[:20]:
                    clue_num = numbers.get((word_info["row"], word_info["col"]), "?")
                    clue_text = f"{clue_num}. {word_info['clue']}"
                    if len(clue_text) > 45:
                        clue_text = clue_text[:42] + "..."
                    c.drawString(PAGE_WIDTH / 2 + 0.1 * inch, y_pos, clue_text)
                    y_pos -= 0.25 * inch

                c.showPage()

            # ANSWER KEY SECTION - UNIQUE SOLUTIONS FOR EACH PUZZLE
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "ANSWER KEY")
            c.setFont("Helvetica", 14)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT / 2 - 0.5 * inch,
                "Complete Solutions for All Puzzles",
            )
            c.showPage()

            # Solution pages - One puzzle per page with complete grid
            for puzzle_idx, puzzle in enumerate(all_puzzles):
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Solution for Puzzle {puzzle['num']}",
                )

                # Draw smaller solution grid
                small_cell = 0.22 * inch
                grid_total = GRID_SIZE * small_cell
                grid_x = (PAGE_WIDTH - grid_total) / 2
                grid_y = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch

                # Draw grid with solutions
                c.setLineWidth(1.0)
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        x = grid_x + (col * small_cell)
                        y = grid_y - ((GRID_SIZE - 1 - row) * small_cell)

                        if puzzle["solution"][row][col] == "#":
                            c.setFillColor(colors.black)
                            c.rect(x, y, small_cell, small_cell, fill=1, stroke=0)
                        else:
                            c.setFillColor(colors.white)
                            c.setStrokeColor(colors.black)
                            c.rect(x, y, small_cell, small_cell, fill=1, stroke=1)

                            # Add solution letter
                            c.setFillColor(colors.black)
                            c.setFont("Helvetica-Bold", 10)
                            # Center letter in cell - y coordinate needs adjustment for
                            # PDF coordinate system
                            text_y = y + (
                                small_cell * 0.35
                            )  # Position text in lower third of cell
                            c.drawCentredString(
                                x + small_cell / 2, text_y, puzzle["solution"][row][col]
                            )

                # Add word lists below grid
                y_pos = grid_y - (GRID_SIZE * small_cell) - 0.5 * inch

                # Get unique words from this puzzle
                across_words = sorted(
                    set(
                        [
                            w["word"]
                            for w in puzzle["words"]
                            if w["direction"] == "across"
                        ]
                    )
                )
                down_words = sorted(
                    set(
                        [w["word"] for w in puzzle["words"] if w["direction"] == "down"]
                    )
                )

                # Display words in two columns
                c.setFont("Helvetica-Bold", 10)
                c.drawString(GUTTER + 0.5 * inch, y_pos, "ACROSS ANSWERS:")
                c.drawString(PAGE_WIDTH / 2 + 0.1 * inch, y_pos, "DOWN ANSWERS:")

                y_pos -= 0.25 * inch
                c.setFont("Helvetica", 9)

                # List words for this puzzle - handle unequal lists properly
                max_words = max(len(across_words), len(down_words))

                for i in range(min(max_words, 10)):  # Show up to 10 words
                    # Draw across word if available
                    if i < len(across_words):
                        across = across_words[i]
                        # Find clue number for this word
                        word_info = next(
                            (
                                w
                                for w in puzzle["words"]
                                if w["word"] == across and w["direction"] == "across"
                            ),
                            None,
                        )
                        if word_info:
                            clue_num = puzzle["numbers"].get(
                                (word_info["row"], word_info["col"]), "?"
                            )
                            clue_text = (
                                word_info["clue"][:30] + "..."
                                if len(word_info["clue"]) > 30
                                else word_info["clue"]
                            )
                            c.drawString(
                                GUTTER + 0.5 * inch, y_pos, f"{clue_num}. {across}"
                            )

                    # Draw down word if available
                    if i < len(down_words):
                        down = down_words[i]
                        # Find clue number for this word
                        word_info = next(
                            (
                                w
                                for w in puzzle["words"]
                                if w["word"] == down and w["direction"] == "down"
                            ),
                            None,
                        )
                        if word_info:
                            clue_num = puzzle["numbers"].get(
                                (word_info["row"], word_info["col"]), "?"
                            )
                            clue_text = (
                                word_info["clue"][:30] + "..."
                                if len(word_info["clue"]) > 30
                                else word_info["clue"]
                            )
                            c.drawString(
                                PAGE_WIDTH / 2 + 0.1 * inch,
                                y_pos,
                                f"{clue_num}. {down}",
                            )

                    y_pos -= 0.2 * inch

                c.showPage()

            # About the Author page (page 156)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch,
                "About Senior Puzzle Studio",
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch
            about_text = [
                "Senior Puzzle Studio specializes in creating large print",
                "puzzle books designed specifically for older adults.",
                "Our mission is to provide engaging mental exercise",
                "through carefully crafted puzzles that are both",
                "challenging and accessible.",
                "",
                "All our puzzles feature:",
                "• Extra-large print for easy reading",
                "• Clear, unambiguous clues",
                "• Common vocabulary words",
                "• Complete answer keys",
                "• Progressive difficulty levels",
                "",
                "Volume 4 features 50 completely unique puzzles,",
                "each with different word selections and patterns",
                "to provide maximum variety and challenge.",
                "",
                "Visit us at www.seniorpuzzlestudio.com",
            ]

            for line in about_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch

            # Save PDF
            c.save()

            print(f"✅ Created Volume 4 with UNIQUE solutions: {pdf_path}")

            # Create metadata
            metadata = {
                "title": "Large Print Crossword Masters - Volume 4",
                "subtitle": "50 Challenging Puzzles for Word Enthusiasts",
                "author": "Crossword Masters Publishing",
                "pages": 156,
                "format": "6 x 9 inches",
                "quality": "Professional with unique solutions for each puzzle",
                "generated": str(datetime.now()),
                "unique_puzzles": 50,
                "solution_format": "One complete grid per puzzle",
            }

            metadata_path = output_dir / "metadata_volume4.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)


def main():
    print("🚀 Creating Volume 4 Crossword Book with UNIQUE solutions...")
    print("📋 Target: 156 pages with 50 unique puzzles")
    generator = Volume4CrosswordGenerator()
    generator.create_complete_book()
    print("\n✅ Volume 4 generated with unique solutions for each puzzle!")


if __name__ == "__main__":
    main()
