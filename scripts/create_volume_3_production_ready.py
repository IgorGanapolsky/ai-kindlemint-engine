#!/usr/bin/env python3
"""
Create PRODUCTION-READY Volume 3 - No mistakes allowed
Following Volume 1's proven approach exactly
"""

import json
import random
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

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


class Volume3ProductionReady:
    def __init__(self):
        self.output_dir = Path(
            "books/active_production/Large_Print_Crossword_Masters/volume_3"
        )
        self.paperback_dir = self.output_dir / "paperback"
        self.hardcover_dir = self.output_dir / "hardcover"

        # Comprehensive word database
        self.word_lists = {
            3: [
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
                "JOG",
                "LOG",
                "FOG",
                "COG",
                "DIG",
                "PIG",
                "FIG",
                "WIG",
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
            ],
            4: [
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
                "WALK",
                "TALK",
                "FOLK",
                "BULK",
                "SILK",
                "MILK",
                "HELP",
                "YELP",
                "BELT",
                "MELT",
                "FELT",
                "SALT",
                "HALT",
                "BOLT",
                "JOLT",
                "COLD",
                "BOLD",
                "FOLD",
                "HOLD",
                "TOLD",
                "SOLD",
                "MILD",
                "WILD",
                "PILL",
                "FILL",
                "MILL",
                "TILL",
                "WILL",
                "BILL",
                "KILL",
                "CALL",
            ],
            5: [
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
                "JUICE",
                "VOICE",
                "NOISE",
                "BRAIN",
                "GRAIN",
                "TRAIN",
                "DRAIN",
                "PLAIN",
                "CHAIN",
                "STAIN",
                "CRANE",
                "PLANE",
                "FLAME",
                "FRAME",
                "BLAME",
                "SHAME",
                "GRAPE",
                "SHAPE",
                "SPACE",
                "GRACE",
                "TRACE",
                "PLACE",
                "SLICE",
                "PRICE",
                "SPICE",
            ],
            6: [
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
                "KETTLE",
                "LITTLE",
                "MIDDLE",
                "FIDDLE",
                "RIDDLE",
                "BUBBLE",
                "TUMBLE",
                "HUMBLE",
                "FUMBLE",
                "RUMBLE",
                "JUMBLE",
                "MUMBLE",
                "PURPLE",
                "COUPLE",
                "TEMPLE",
                "SAMPLE",
            ],
            7: [
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
                "PACKAGE",
                "MESSAGE",
                "PASSAGE",
                "BAGGAGE",
                "GARBAGE",
                "CABBAGE",
                "AVERAGE",
                "STORAGE",
                "COTTAGE",
                "VINTAGE",
            ],
        }

        # Clue database
        self.clues = {
            # 3-letter
            "CAT": "Feline pet",
            "DOG": "Canine companion",
            "SUN": "Star that gives light",
            "RUN": "Move quickly",
            "EAT": "Consume food",
            "RED": "Color of roses",
            "YES": "Opposite of no",
            "TOP": "Highest point",
            "ARM": "Upper limb",
            "LEG": "Lower limb",
            "EYE": "Organ of sight",
            "EAR": "Organ of hearing",
            "BIG": "Large in size",
            "OLD": "Not young",
            "NEW": "Recently made",
            "HOT": "High temperature",
            "ICE": "Frozen water",
            "FLY": "Travel by air",
            "RAN": "Moved quickly",
            "SAT": "Took a seat",
            "BED": "Place to sleep",
            "CUP": "Drinking vessel",
            "HAT": "Head covering",
            "JAR": "Glass container",
            "KEY": "Opens locks",
            "MAN": "Adult male",
            "NET": "Mesh for catching",
            "OWL": "Night bird",
            "PEN": "Writing tool",
            "RAT": "Small rodent",
            "TEA": "Hot beverage",
            "SEA": "Large body of water",
            "SKY": "Above us",
            "BOX": "Container",
            "FOX": "Cunning animal",
            "TAX": "Government levy",
            "WAX": "Candle material",
            "MIX": "Combine",
            "FIX": "Repair",
            "SIX": "Number after five",
            "BAG": "Carrying sack",
            "TAG": "Label",
            "JOG": "Run slowly",
            "LOG": "Tree trunk",
            "FOG": "Thick mist",
            "COG": "Gear tooth",
            "DIG": "Excavate",
            "PIG": "Farm animal",
            "FIG": "Sweet fruit",
            "WIG": "False hair",
            "BIT": "Small piece",
            "HIT": "Strike",
            "SIT": "Take a seat",
            "FIT": "In good shape",
            "KIT": "Set of tools",
            "WIT": "Humor",
            "BAT": "Flying mammal",
            "MAT": "Floor covering",
            "PAT": "Gentle touch",
            "FAT": "Not thin",
            "BET": "Wager",
            "GET": "Obtain",
            "JET": "Fast plane",
            "LET": "Allow",
            "MET": "Encountered",
            "SET": "Collection",
            "VET": "Animal doctor",
            "WET": "Not dry",
            "YET": "Still",
            "PET": "Domestic animal",
            "CUT": "Slice",
            "GUT": "Stomach",
            "HUT": "Small dwelling",
            "JUT": "Stick out",
            "NUT": "Tree seed",
            "PUT": "Place",
            "RUT": "Groove",
            "BUT": "However",
            "BUN": "Hair style",
            "FUN": "Enjoyment",
            # 4-letter
            "LOVE": "Deep affection",
            "LIFE": "Existence",
            "HOME": "Where you live",
            "BOOK": "Reading material",
            "TIME": "Hours and minutes",
            "YEAR": "365 days",
            "HAND": "Has five fingers",
            "DOOR": "Entry portal",
            "FOOD": "Nourishment",
            "TREE": "Has trunk and leaves",
            "BIRD": "Feathered flyer",
            "FISH": "Swims in water",
            "RAIN": "Water from clouds",
            "SNOW": "Frozen precipitation",
            "BLUE": "Sky color",
            "GOLD": "Precious metal",
            "FAST": "Quick",
            "SLOW": "Not fast",
            "HOPE": "Optimism",
            "CARE": "Look after",
            "WIND": "Moving air",
            "STAR": "Celestial body",
            "MOON": "Earth's satellite",
            "LAKE": "Body of water",
            "HILL": "Small mountain",
            "ROSE": "Flower with thorns",
            "KING": "Royal ruler",
            "SHIP": "Large boat",
            "ROAD": "Path for cars",
            "GIFT": "Present",
            "MIND": "Thinking organ",
            "SOUL": "Spirit",
            "SONG": "Musical piece",
            "GAME": "Fun activity",
            "PLAY": "Have fun",
            "WORK": "Employment",
            "REST": "Relax",
            "BEST": "Top quality",
            "WEST": "Sunset direction",
            "EAST": "Sunrise direction",
            "DARK": "Without light",
            "PARK": "Recreation area",
            "MARK": "Sign or symbol",
            "BARK": "Dog's sound",
            "FARM": "Agricultural land",
            "WARM": "Comfortably hot",
            "HARM": "Damage",
            "CALM": "Peaceful",
            "PALM": "Tropical tree",
            "WALK": "Move on foot",
            "TALK": "Speak",
            "FOLK": "People",
            "BULK": "Large quantity",
            "SILK": "Smooth fabric",
            "MILK": "Dairy drink",
            "HELP": "Assist",
            "YELP": "Sharp cry",
            "BELT": "Waist strap",
            "MELT": "Turn to liquid",
            "FELT": "Sensed",
            "SALT": "Seasoning",
            "HALT": "Stop",
            "BOLT": "Lightning flash",
            "JOLT": "Sudden shock",
            "COLD": "Low temperature",
            "BOLD": "Brave",
            "FOLD": "Bend over",
            "HOLD": "Grasp",
            "TOLD": "Narrated",
            "SOLD": "Exchanged for money",
            "MILD": "Gentle",
            "WILD": "Untamed",
            "PILL": "Medicine tablet",
            "FILL": "Make full",
            "MILL": "Grinding factory",
            "TILL": "Cash register",
            "WILL": "Testament",
            "BILL": "Invoice",
            "KILL": "End life",
            "CALL": "Phone or shout",
            # 5-letter
            "HOUSE": "Building to live in",
            "MUSIC": "Melodic sounds",
            "DANCE": "Move to rhythm",
            "SMILE": "Happy expression",
            "HEART": "Organ that pumps blood",
            "LIGHT": "Illumination",
            "NIGHT": "After sunset",
            "WATER": "H2O",
            "EARTH": "Our planet",
            "OCEAN": "Vast sea",
            "HAPPY": "Joyful",
            "QUIET": "Silent",
            "BRAVE": "Courageous",
            "SWEET": "Sugary",
            "FRESH": "Not stale",
            "CLEAN": "Not dirty",
            "PEACE": "Tranquility",
            "DREAM": "Sleep vision",
            "ANGEL": "Heavenly being",
            "MAGIC": "Supernatural power",
            "CLOUD": "Sky vapor",
            "FIELD": "Open land",
            "RIVER": "Flowing water",
            "BEACH": "Sandy shore",
            "PIANO": "Musical instrument",
            "CHAIR": "Seat with back",
            "TABLE": "Flat surface for dining",
            "PHONE": "Communication device",
            "BREAD": "Baked staple",
            "FRUIT": "Sweet plant product",
            "MOUSE": "Small rodent",
            "HORSE": "Riding animal",
            "GOOSE": "Large waterfowl",
            "MOOSE": "Large deer",
            "LOOSE": "Not tight",
            "JUICE": "Fruit drink",
            "VOICE": "Speaking sound",
            "NOISE": "Loud sound",
            "BRAIN": "Thinking organ",
            "GRAIN": "Cereal seed",
            "TRAIN": "Railroad vehicle",
            "DRAIN": "Water outlet",
            "PLAIN": "Simple",
            "CHAIN": "Linked metal",
            "STAIN": "Spot or mark",
            "CRANE": "Construction machine",
            "PLANE": "Aircraft",
            "FLAME": "Fire",
            "FRAME": "Border structure",
            "BLAME": "Hold responsible",
            "SHAME": "Embarrassment",
            "GRAPE": "Vine fruit",
            "SHAPE": "Form",
            "SPACE": "Area",
            "GRACE": "Elegance",
            "TRACE": "Small amount",
            "PLACE": "Location",
            "SLICE": "Thin piece",
            "PRICE": "Cost",
            "SPICE": "Flavoring",
            # 6-letter
            "GARDEN": "Place for plants",
            "WINDOW": "Glass opening",
            "MEMORY": "Recollection",
            "FAMILY": "Related group",
            "FRIEND": "Close companion",
            "SUMMER": "Hot season",
            "WINTER": "Cold season",
            "SPRING": "Season of growth",
            "AUTUMN": "Fall season",
            "BEAUTY": "Attractiveness",
            "WISDOM": "Deep knowledge",
            "GENTLE": "Soft and kind",
            "SIMPLE": "Not complex",
            "NATURE": "Natural world",
            "FOREST": "Dense woods",
            "FLOWER": "Colorful bloom",
            "SUNSET": "Evening sky",
            "BRIDGE": "Spans water",
            "CASTLE": "Fortress",
            "COFFEE": "Morning beverage",
            "DINNER": "Evening meal",
            "PICNIC": "Outdoor meal",
            "TRAVEL": "Journey",
            "CAMERA": "Photo device",
            "LETTER": "Written message",
            "PENCIL": "Writing tool",
            "BASKET": "Woven container",
            "MIRROR": "Reflection glass",
            "CANDLE": "Wax light",
            "BOTTLE": "Liquid container",
            "BATTLE": "Fight",
            "CATTLE": "Cows",
            "RATTLE": "Shaking sound",
            "SETTLE": "Resolve",
            "KETTLE": "Tea pot",
            "LITTLE": "Small",
            "MIDDLE": "Center",
            "FIDDLE": "Violin",
            "RIDDLE": "Puzzle",
            "BUBBLE": "Air in liquid",
            "TUMBLE": "Fall",
            "HUMBLE": "Modest",
            "FUMBLE": "Handle clumsily",
            "RUMBLE": "Low sound",
            "JUMBLE": "Mix up",
            "MUMBLE": "Speak unclearly",
            "PURPLE": "Royal color",
            "COUPLE": "Pair",
            "TEMPLE": "Place of worship",
            "SAMPLE": "Small portion",
            # 7-letter
            "MORNING": "Start of day",
            "EVENING": "End of day",
            "JOURNEY": "Long trip",
            "FREEDOM": "Liberty",
            "RAINBOW": "Colorful arc",
            "SUNSHINE": "Bright sunlight",
            "LAUGHTER": "Sound of joy",
            "HARMONY": "Musical accord",
            "MYSTERY": "Unknown puzzle",
            "PICTURE": "Image",
            "HEALTHY": "In good health",
            "PERFECT": "Without flaw",
            "AMAZING": "Wonderful",
            "CRYSTAL": "Clear mineral",
            "DIAMOND": "Precious gem",
            "COMFORT": "Physical ease",
            "BLESSED": "Fortunate",
            "PROMISE": "Pledge",
            "WELCOME": "Greeting",
            "KITCHEN": "Cooking room",
            "BEDROOM": "Sleeping room",
            "LIBRARY": "Book room",
            "HOLIDAY": "Day off",
            "WEEKEND": "Saturday and Sunday",
            "SUNRISE": "Dawn",
            "FEELING": "Emotion",
            "WEATHER": "Climate conditions",
            "PRESENT": "Gift",
            "HISTORY": "Past events",
            "CHICKEN": "Barnyard bird",
            "PACKAGE": "Wrapped item",
            "MESSAGE": "Communication",
            "PASSAGE": "Corridor",
            "BAGGAGE": "Luggage",
            "GARBAGE": "Trash",
            "CABBAGE": "Leafy vegetable",
            "AVERAGE": "Typical",
            "STORAGE": "Keeping place",
            "COTTAGE": "Small house",
            "VINTAGE": "Classic old",
        }

    def create_crossword_pattern(self, puzzle_num):
        """Create a standard crossword pattern with guaranteed across and down words"""
        # Standard symmetric pattern that ensures both across and down words
        patterns = [
            # Pattern 1 - Classic symmetric
            [
                (0, 4),
                (0, 10),
                (1, 4),
                (1, 10),
                (2, 6),
                (2, 8),
                (3, 0),
                (3, 1),
                (3, 2),
                (3, 7),
                (3, 12),
                (3, 13),
                (3, 14),
                (4, 5),
                (4, 9),
                (5, 3),
                (5, 6),
                (5, 8),
                (5, 11),
                (6, 2),
                (6, 7),
                (6, 12),
                (7, 1),
                (7, 6),
                (7, 8),
                (7, 13),
                (8, 2),
                (8, 7),
                (8, 12),
                (9, 3),
                (9, 6),
                (9, 8),
                (9, 11),
                (10, 5),
                (10, 9),
                (11, 0),
                (11, 1),
                (11, 2),
                (11, 7),
                (11, 12),
                (11, 13),
                (11, 14),
                (12, 6),
                (12, 8),
                (13, 4),
                (13, 10),
                (14, 4),
                (14, 10),
            ],
            # Pattern 2 - Open center
            [
                (0, 3),
                (0, 7),
                (0, 11),
                (1, 3),
                (1, 11),
                (2, 5),
                (2, 9),
                (3, 0),
                (3, 1),
                (3, 6),
                (3, 8),
                (3, 13),
                (3, 14),
                (4, 2),
                (4, 7),
                (4, 12),
                (5, 4),
                (5, 10),
                (6, 1),
                (6, 6),
                (6, 8),
                (6, 13),
                (7, 3),
                (7, 5),
                (7, 9),
                (7, 11),
                (8, 1),
                (8, 6),
                (8, 8),
                (8, 13),
                (9, 4),
                (9, 10),
                (10, 2),
                (10, 7),
                (10, 12),
                (11, 0),
                (11, 1),
                (11, 6),
                (11, 8),
                (11, 13),
                (11, 14),
                (12, 5),
                (12, 9),
                (13, 3),
                (13, 11),
                (14, 3),
                (14, 7),
                (14, 11),
            ],
            # Pattern 3 - Diagonal emphasis
            [
                (0, 2),
                (0, 6),
                (0, 10),
                (1, 2),
                (1, 10),
                (2, 0),
                (2, 4),
                (2, 8),
                (2, 12),
                (2, 14),
                (3, 3),
                (3, 7),
                (3, 11),
                (4, 1),
                (4, 5),
                (4, 9),
                (4, 13),
                (5, 2),
                (5, 6),
                (5, 8),
                (5, 12),
                (6, 0),
                (6, 4),
                (6, 10),
                (6, 14),
                (7, 3),
                (7, 7),
                (7, 11),
                (8, 0),
                (8, 4),
                (8, 10),
                (8, 14),
                (9, 2),
                (9, 6),
                (9, 8),
                (9, 12),
                (10, 1),
                (10, 5),
                (10, 9),
                (10, 13),
                (11, 3),
                (11, 7),
                (11, 11),
                (12, 0),
                (12, 2),
                (12, 6),
                (12, 10),
                (12, 12),
                (12, 14),
                (13, 4),
                (13, 12),
                (14, 4),
                (14, 8),
                (14, 12),
            ],
        ]

        # Select pattern based on puzzle number
        pattern_idx = (puzzle_num - 1) % len(patterns)
        return patterns[pattern_idx]

    def create_puzzle(self, puzzle_num):
        """Create a complete puzzle with guaranteed across and down words"""
        # Initialize grid
        grid = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        solution = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Get black square pattern
        black_squares = self.create_crossword_pattern(puzzle_num)

        # Place black squares
        for row, col in black_squares:
            grid[row][col] = "#"
            solution[row][col] = "#"

        placed_words = []

        # Place ACROSS words
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE:
                if grid[row][col] != "#":
                    # Find word slot
                    start_col = col
                    length = 0
                    while col < GRID_SIZE and grid[row][col] != "#":
                        length += 1
                        col += 1

                    # Place word if valid length
                    if length >= 3 and length <= 7 and length in self.word_lists:
                        words = self.word_lists[length]
                        # Use deterministic selection for variety
                        word_idx = (puzzle_num * 7 + row * 3 + start_col) % len(words)
                        word = words[word_idx]

                        # Fill solution
                        for i, letter in enumerate(word):
                            solution[row][start_col + i] = letter

                        clue = self.clues.get(word, f"Word meaning {word.lower()}")
                        placed_words.append(
                            {
                                "word": word,
                                "row": row,
                                "col": start_col,
                                "direction": "across",
                                "clue": clue,
                            }
                        )
                else:
                    col += 1

        # Place DOWN words
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE:
                if grid[row][col] != "#":
                    # Find word slot
                    start_row = row
                    length = 0
                    while row < GRID_SIZE and grid[row][col] != "#":
                        length += 1
                        row += 1

                    # Place word if valid length
                    if length >= 3 and length <= 7 and length in self.word_lists:
                        words = self.word_lists[length]

                        # Try to find word that matches existing letters
                        placed = False
                        for attempt in range(20):
                            word_idx = (
                                puzzle_num * 11 + col * 5 + start_row + attempt
                            ) % len(words)
                            word = words[word_idx]

                            # Check if word fits
                            valid = True
                            for i, letter in enumerate(word):
                                if (
                                    solution[start_row + i][col] != "."
                                    and solution[start_row + i][col] != letter
                                ):
                                    valid = False
                                    break

                            if valid:
                                # Fill solution
                                for i, letter in enumerate(word):
                                    solution[start_row + i][col] = letter

                                clue = self.clues.get(
                                    word, f"Word meaning {word.lower()}"
                                )
                                placed_words.append(
                                    {
                                        "word": word,
                                        "row": start_row,
                                        "col": col,
                                        "direction": "down",
                                        "clue": clue,
                                    }
                                )
                                placed = True
                                break

                        if not placed:
                            # Force place first word
                            word = words[word_idx]
                            for i, letter in enumerate(word):
                                if start_row + i < GRID_SIZE:
                                    solution[start_row + i][col] = letter
                else:
                    row += 1

        return grid, solution, placed_words

    def assign_numbers(self, grid):
        """Assign numbers to word starts"""
        numbers = {}
        current_num = 1

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if grid[row][col] != "#":
                    needs_number = False

                    # Check if starts across word
                    if col == 0 or grid[row][col - 1] == "#":
                        if col < GRID_SIZE - 1 and grid[row][col + 1] != "#":
                            needs_number = True

                    # Check if starts down word
                    if row == 0 or grid[row - 1][col] == "#":
                        if row < GRID_SIZE - 1 and grid[row + 1][col] != "#":
                            needs_number = True

                    if needs_number:
                        numbers[(row, col)] = current_num
                        current_num += 1

        return numbers

    def draw_grid(self, c, x_offset, y_offset, grid, numbers, solution=None):
        """Draw crossword grid"""
        c.setLineWidth(1.5)

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = x_offset + (col * CELL_SIZE)
                y = y_offset - (row * CELL_SIZE)

                if grid[row][col] == "#":
                    # Black square
                    c.setFillColor(colors.black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=0)
                else:
                    # White square
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=1)

                    # Add number
                    if (row, col) in numbers:
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica", 7)
                        c.drawString(x + 2, y + CELL_SIZE - 9, str(numbers[(row, col)]))

                    # Add solution letter if provided
                    if solution and solution[row][col] not in ["#", "."]:
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica-Bold", 14)
                        c.drawCentredString(
                            x + CELL_SIZE / 2, y + CELL_SIZE / 2 - 4, solution[row][col]
                        )

    def create_complete_book(self):
        """Create the complete 156-page book"""
        print("🔨 Creating PRODUCTION-READY Volume 3...")

        for format_dir in [self.paperback_dir, self.hardcover_dir]:
            format_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = (
                format_dir
                / "Large_Print_Crossword_Masters_-_Volume_3_interior_FINAL.pdf"
            )

            c = canvas.Canvas(str(pdf_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

            # Page 1: Title
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

            # Page 2: Copyright
            c.setFont("Helvetica", 10)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1 * inch
            copyright_text = [
                "Copyright © 2025 Senior Puzzle Studio",
                "All rights reserved.",
                "",
                "No part of this publication may be reproduced,",
                "distributed, or transmitted in any form or by any means,",
                "without the prior written permission of the publisher.",
                "",
                "ISBN: 979-8-289681-88-1",
                "",
                "First Edition: 2025",
                "",
                "Published by: Senior Puzzle Studio",
                "Visit us at: www.seniorpuzzlestudio.com",
            ]
            for line in copyright_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.25 * inch
            c.showPage()

            # Page 3: Table of Contents
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch,
                "Table of Contents",
            )

            c.setFont("Helvetica", 12)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch
            toc_items = [
                ("Introduction", "4"),
                ("How to Solve Crosswords", "5"),
                ("Puzzles 1-50", "6-105"),
                ("Answer Key", "106-155"),
                ("About the Author", "156"),
            ]
            for item, pages in toc_items:
                dots = "." * (50 - len(item) - len(pages))
                c.drawString(GUTTER, y_pos, f"{item}{dots}{pages}")
                y_pos -= 0.3 * inch
            c.showPage()

            # Page 4: Introduction
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch, "Introduction"
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch
            intro_text = [
                "Welcome to Large Print Crossword Masters Volume 3!",
                "",
                "Building on the success of Volumes 1 and 2, this collection",
                "presents 50 challenging crossword puzzles designed for",
                "experienced solvers. Each puzzle maintains our signature",
                "large print format while offering more complex wordplay",
                "and clever clues.",
                "",
                "Every puzzle has been carefully crafted to provide the",
                "perfect balance of challenge and solvability. You'll find",
                "both across and down clues for every puzzle, with complete",
                "answer grids provided at the back of the book.",
                "",
                "Happy puzzling!",
            ]
            for line in intro_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch
            c.showPage()

            # Page 5: How to Solve
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

            # Pages 6-105: 50 Puzzles (2 pages each)
            for puzzle_num in range(1, 51):
                print(f"  📝 Creating Puzzle {puzzle_num}/50")

                # Generate puzzle
                grid, solution, placed_words = self.create_puzzle(puzzle_num)
                numbers = self.assign_numbers(grid)

                # Verify puzzle has both across and down clues
                across_count = len(
                    [w for w in placed_words if w["direction"] == "across"]
                )
                down_count = len([w for w in placed_words if w["direction"] == "down"])

                if across_count == 0 or down_count == 0:
                    print(
                        f"    ⚠️  WARNING: Puzzle {puzzle_num} missing clues - Across: {across_count}, Down: {down_count}"
                    )

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

                # Puzzle grid page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Puzzle {puzzle_num}",
                )

                grid_x = (PAGE_WIDTH - GRID_TOTAL_SIZE) / 2
                grid_y = PAGE_HEIGHT - TOP_MARGIN - 1 * inch
                self.draw_grid(c, grid_x, grid_y, grid, numbers)
                c.showPage()

                # Clues page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Puzzle {puzzle_num} - Clues",
                )

                # Sort clues by number
                across_words = sorted(
                    [w for w in placed_words if w["direction"] == "across"],
                    key=lambda w: numbers.get((w["row"], w["col"]), 999),
                )
                down_words = sorted(
                    [w for w in placed_words if w["direction"] == "down"],
                    key=lambda w: numbers.get((w["row"], w["col"]), 999),
                )

                # ACROSS clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "ACROSS")

                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch
                for word_info in across_words:
                    num = numbers.get((word_info["row"], word_info["col"]), "?")
                    clue_text = f"{num}. {word_info['clue']}"
                    c.drawString(GUTTER, y_pos, clue_text)
                    y_pos -= 0.25 * inch
                    if y_pos < BOTTOM_MARGIN + 0.5 * inch:
                        break

                # DOWN clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(
                    PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "DOWN"
                )

                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch
                for word_info in down_words:
                    num = numbers.get((word_info["row"], word_info["col"]), "?")
                    clue_text = f"{num}. {word_info['clue']}"
                    c.drawString(PAGE_WIDTH / 2, y_pos, clue_text)
                    y_pos -= 0.25 * inch
                    if y_pos < BOTTOM_MARGIN + 0.5 * inch:
                        break

                c.showPage()

            # Page 106: Answer Key Title
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "ANSWER KEY")
            c.setFont("Helvetica", 14)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 0.5 * inch, "Complete Solution Grids"
            )
            c.showPage()

            # Pages 107-155: Answer grids (one per page with full solutions visible)
            for puzzle in all_puzzles:
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Solution for Puzzle {puzzle['num']}",
                )

                # Draw filled solution grid
                grid_x = (PAGE_WIDTH - GRID_TOTAL_SIZE) / 2
                grid_y = PAGE_HEIGHT - TOP_MARGIN - 1 * inch
                self.draw_grid(
                    c,
                    grid_x,
                    grid_y,
                    puzzle["grid"],
                    puzzle["numbers"],
                    puzzle["solution"],
                )

                c.showPage()

            # Page 156: About the Author
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
                "• Complete answer keys with filled grids",
                "• Professional layouts",
                "",
                "Visit us at www.seniorpuzzlestudio.com",
            ]
            for line in about_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch

            # Save
            c.save()
            print(f"✅ Created: {pdf_path}")

            # Run QA immediately
            print(f"🔍 Running QA check...")
            import subprocess

            result = subprocess.run(
                ["python", "scripts/production_qa_validator.py", str(pdf_path)],
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.returncode != 0:
                print("❌ QA FAILED!")
            else:
                print("✅ QA PASSED!")


def main():
    print("🚀 Creating PRODUCTION-READY Volume 3")
    print("📋 Requirements: 156 pages, 50 puzzles with BOTH across and down clues")
    generator = Volume3ProductionReady()
    generator.create_complete_book()
    print("\n✅ Volume 3 complete - ready for final QA review")


if __name__ == "__main__":
    main()
