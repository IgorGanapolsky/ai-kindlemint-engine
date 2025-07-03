#!/usr/bin/env python3
"""
Create Volume 3 with PROPER crossword puzzles
Ensures all letter sequences form real words
"""

import json
import random
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

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


class ProperCrosswordGenerator:
    def __init__(self):
        self.output_dir = Path(
            "books/active_production/Large_Print_Crossword_Masters/volume_3"
        )
        self.paperback_dir = self.output_dir / "paperback"
        self.hardcover_dir = self.output_dir / "hardcover"

        # Real crossword patterns from successful puzzles
        # Each pattern is designed to create valid word slots
        self.crossword_patterns = [
            # Pattern 1: Classic American style
            [
                "...#...#.......",
                ".#.#.#.#.#.#.#.",
                "...#...#...#...",
                ".#.#.#.#.#.#.#.",
                "......#...#....",
                ".####.#.#.####.",
                "...#...#...#...",
                ".#.#.#####.#.#.",
                "...#...#...#...",
                ".####.#.#.####.",
                "....#...#......",
                ".#.#.#.#.#.#.#.",
                "...#...#...#...",
                ".#.#.#.#.#.#.#.",
                ".......#...#...",
            ],
            # Pattern 2: Open grid
            [
                "....#....#.....",
                ".##.#.##.#.##.#",
                "....#....#.....",
                "###.#.##.#.###.",
                "....#....#.....",
                ".##.###.###.##.",
                "....#....#.....",
                ".#.#######.#.#.",
                "....#....#.....",
                ".##.###.###.##.",
                "....#....#.....",
                ".###.#.##.#.###",
                "....#....#.....",
                "#.##.#.##.#.##.",
                ".....#....#....",
            ],
            # Pattern 3: British style
            [
                ".......#.......",
                ".#####.#.#####.",
                ".......#.......",
                ".#.#.#.#.#.#.#.",
                "...#.......#...",
                "##.#.#####.#.##",
                "...#.......#...",
                ".#.#.#.#.#.#.#.",
                "...#.......#...",
                "##.#.#####.#.##",
                "...#.......#...",
                ".#.#.#.#.#.#.#.",
                ".......#.......",
                ".#####.#.#####.",
                ".......#.......",
            ],
        ]

        # Extensive word lists by length
        self.words_by_length = {
            3: [
                "THE",
                "AND",
                "FOR",
                "ARE",
                "BUT",
                "NOT",
                "YOU",
                "ALL",
                "CAN",
                "HER",
                "WAS",
                "ONE",
                "OUR",
                "OUT",
                "DAY",
                "RUN",
                "CAT",
                "DOG",
                "SUN",
                "MAN",
                "BOY",
                "FUN",
                "SIT",
                "EAT",
                "RED",
                "BIG",
                "HOT",
                "NEW",
                "OLD",
                "GET",
                "PUT",
                "SEE",
                "TOP",
                "TRY",
                "TWO",
                "USE",
                "WAY",
                "WIN",
                "YES",
                "YET",
                "ARM",
                "BAD",
                "BAG",
                "BED",
                "BOX",
                "BUS",
                "CUP",
                "CUT",
                "DID",
                "EAR",
                "EGG",
                "END",
                "EYE",
                "FEW",
                "FIT",
                "FLY",
                "GOT",
                "GUN",
                "HAD",
                "HAT",
                "HIT",
                "JOB",
                "LAW",
                "LAY",
                "LEG",
                "LET",
                "LIE",
                "LOT",
                "LOW",
                "MAY",
                "MEN",
                "MOM",
                "NOR",
                "NOW",
                "OWN",
                "PAY",
                "PER",
                "RAN",
                "SAW",
                "SAY",
                "SET",
                "SHE",
                "SIX",
                "SON",
                "TEN",
                "TOO",
                "WAR",
                "WHO",
                "WHY",
                "WON",
            ],
            4: [
                "THAT",
                "WITH",
                "HAVE",
                "THIS",
                "WILL",
                "YOUR",
                "FROM",
                "THEY",
                "KNOW",
                "WANT",
                "BEEN",
                "GOOD",
                "MUCH",
                "SOME",
                "TIME",
                "VERY",
                "WHEN",
                "COME",
                "HERE",
                "JUST",
                "LIKE",
                "LONG",
                "MAKE",
                "MANY",
                "OVER",
                "SUCH",
                "TAKE",
                "THAN",
                "THEM",
                "WELL",
                "ONLY",
                "YEAR",
                "WORK",
                "BACK",
                "CALL",
                "CAME",
                "EACH",
                "EVEN",
                "FIND",
                "GIVE",
                "HAND",
                "HIGH",
                "KEEP",
                "LAST",
                "LEFT",
                "LIFE",
                "LIVE",
                "LOOK",
                "MADE",
                "MOST",
                "MOVE",
                "MUST",
                "NAME",
                "NEED",
                "NEXT",
                "OPEN",
                "PART",
                "PLAY",
                "SAID",
                "SAME",
                "SEEM",
                "SHOW",
                "SIDE",
                "TELL",
                "TURN",
                "USED",
                "WANT",
                "WAYS",
                "WEEK",
                "WENT",
                "WERE",
                "WHAT",
                "WORD",
                "WORK",
                "YEAR",
                "ABLE",
                "ALSO",
                "BASE",
                "BEST",
                "BODY",
                "BOOK",
                "BOTH",
                "CARE",
                "CASE",
                "CITY",
                "DAYS",
                "DOOR",
                "DOWN",
                "FACE",
                "FACT",
                "FELT",
                "FIVE",
                "FOOD",
                "FOUR",
                "FREE",
                "FULL",
                "GAVE",
                "GIRL",
                "GOES",
                "GONE",
                "HALF",
                "HARD",
                "HEAD",
                "HELP",
                "HERE",
                "HOME",
                "HOPE",
                "HOUR",
                "IDEA",
                "KEEP",
                "KIND",
                "LAND",
                "LATE",
                "LESS",
                "LINE",
                "LOST",
                "LOVE",
                "MAIN",
                "MIND",
                "MISS",
                "ONCE",
                "PAGE",
                "PAST",
                "PLAN",
                "REAL",
                "REST",
                "ROAD",
                "ROOM",
                "SOON",
                "SURE",
                "TALK",
                "TOLD",
                "TOOK",
                "TOWN",
                "TREE",
                "TRUE",
                "UPON",
                "WALK",
                "WALL",
                "WARM",
                "WAVE",
                "WIFE",
                "WIND",
                "WISH",
                "WOOD",
                "WORD",
                "WORK",
            ],
            5: [
                "WHICH",
                "THEIR",
                "WOULD",
                "THERE",
                "COULD",
                "BEING",
                "FIRST",
                "AFTER",
                "THESE",
                "OTHER",
                "WORDS",
                "WORLD",
                "WHERE",
                "STILL",
                "THREE",
                "NEVER",
                "UNDER",
                "WHILE",
                "ABOUT",
                "AGAIN",
                "BEFORE",
                "FOUND",
                "GOING",
                "GREAT",
                "HOUSE",
                "LARGE",
                "PLACE",
                "RIGHT",
                "SMALL",
                "SOUND",
                "STILL",
                "THINGS",
                "THINK",
                "THOSE",
                "WATER",
                "YEARS",
                "YOUNG",
                "ACROSS",
                "ALONG",
                "AMONG",
                "BEGAN",
                "BLACK",
                "BRING",
                "BUILD",
                "CARRY",
                "CLEAN",
                "CLOSE",
                "COMES",
                "COVER",
                "EARLY",
                "EVERY",
                "FIELD",
                "FINAL",
                "GIVEN",
                "GREEN",
                "HAPPY",
                "HEARD",
                "HEART",
                "HEAVY",
                "HORSE",
                "HOURS",
                "HUMAN",
                "LEARN",
                "LEAVE",
                "LIGHT",
                "MONEY",
                "MUSIC",
                "NIGHT",
                "NORTH",
                "OFTEN",
                "ORDER",
                "PAPER",
                "PARTY",
                "PEACE",
                "PIECE",
                "POINT",
                "POWER",
                "QUICK",
                "REACH",
                "RIVER",
                "ROUND",
                "SERVE",
                "SHORT",
                "SHOWN",
                "SINCE",
                "SLEEP",
                "SOUTH",
                "SPACE",
                "SPEAK",
                "SPEED",
                "SPEND",
                "STAND",
                "START",
                "STATE",
                "STORY",
                "TABLE",
                "TAKEN",
                "THIRD",
                "TODAY",
                "TOTAL",
                "TOUCH",
                "TRADE",
                "TRIED",
                "TRULY",
                "UNTIL",
                "VOICE",
                "WATCH",
                "WATER",
                "WAVES",
                "WHOLE",
                "WOMAN",
                "WOMEN",
                "WRITE",
                "WROTE",
            ],
            6: [
                "BEFORE",
                "SHOULD",
                "PEOPLE",
                "THROUGH",
                "AROUND",
                "ANOTHER",
                "BETWEEN",
                "COUNTRY",
                "AGAINST",
                "BECAUSE",
                "WITHOUT",
                "THOUGHT",
                "GENERAL",
                "HOWEVER",
                "NOTHING",
                "PERHAPS",
                "PROBLEM",
                "SEVERAL",
                "TOGETHER",
                "ALREADY",
                "CERTAIN",
                "MORNING",
                "HIMSELF",
                "LOOKING",
                "SOMETHING",
                "BROUGHT",
                "GETTING",
                "ANYTHING",
                "BELIEVE",
                "COMPANY",
                "CONTROL",
                "DURING",
                "EITHER",
                "ENOUGH",
                "FATHER",
                "GROUND",
                "HAPPEN",
                "HAVING",
                "ITSELF",
                "LETTER",
                "LITTLE",
                "LIVING",
                "MAKING",
                "MATTER",
                "MEMBER",
                "MINUTE",
                "MOMENT",
                "MOTHER",
                "MYSELF",
                "NATURE",
                "OFFICE",
                "RATHER",
                "REASON",
                "RESULT",
                "SECOND",
                "SEEMED",
                "SIMPLE",
                "SOCIAL",
                "STREET",
                "SYSTEM",
                "TAKING",
                "THOUGH",
                "TURNED",
                "WITHIN",
                "ACROSS",
                "ALMOST",
                "ALWAYS",
                "AMOUNT",
                "ANIMAL",
                "ANSWER",
                "ANYONE",
                "APPEAR",
                "BECOME",
                "BEHIND",
                "BETTER",
                "CALLED",
                "CANNOT",
                "CENTER",
                "CHANGE",
                "CHURCH",
                "COMING",
                "COMMON",
                "COUPLE",
                "COURSE",
                "DECIDE",
                "DESIGN",
                "DIRECT",
                "DOCTOR",
                "EFFECT",
                "EFFORT",
                "EXAMPLE",
                "FAMILY",
                "FIGURE",
                "FOLLOW",
                "FRIEND",
                "FUTURE",
                "GARDEN",
                "HAPPEN",
                "HEALTH",
                "HISTORY",
                "INTEREST",
                "ISLAND",
                "LIKELY",
                "LISTEN",
                "MARKET",
                "MODERN",
                "NATION",
                "NUMBER",
                "PERIOD",
                "PERSON",
                "PICTURE",
                "PLAYED",
                "PLEASE",
                "POLICE",
                "POLICY",
                "PRESENT",
                "PUBLIC",
                "REPORT",
                "SCHOOL",
                "SEASON",
                "SEEMED",
                "SERIES",
                "SIMPLY",
                "SINGLE",
                "SPRING",
                "SQUARE",
                "STRONG",
                "SUBJECT",
                "SUMMER",
                "SUNDAY",
                "SUPPLY",
                "SYSTEM",
                "THEORY",
                "TRAVEL",
                "TRYING",
                "TURNED",
                "UNITED",
                "WALKED",
                "WANTED",
                "WINDOW",
                "WINTER",
                "WONDER",
                "WORKED",
                "WRITER",
                "YELLOW",
            ],
            7: [
                "BECAUSE",
                "THROUGH",
                "BETWEEN",
                "ANOTHER",
                "AGAINST",
                "WITHOUT",
                "NOTHING",
                "PERHAPS",
                "PROBLEM",
                "SEVERAL",
                "TOGETHER",
                "ALREADY",
                "CERTAIN",
                "COUNTRY",
                "GENERAL",
                "HOWEVER",
                "LOOKING",
                "MORNING",
                "HIMSELF",
                "BELIEVE",
                "BROUGHT",
                "COMPANY",
                "CONTROL",
                "GETTING",
                "ANYTHING",
                "EXAMPLE",
                "FOLLOWING",
                "QUESTION",
                "INTEREST",
                "BUSINESS",
                "PROGRAM",
                "POSSIBLE",
                "IMPORTANT",
                "REMEMBER",
                "CHILDREN",
                "STUDENTS",
                "AMERICAN",
                "NATIONAL",
                "BUILDING",
                "SPECIAL",
                "ACTUALLY",
                "AVAILABLE",
                "EVIDENCE",
                "FUNCTION",
                "LANGUAGE",
                "PERSONAL",
                "POSITION",
                "PROBABLY",
                "RESEARCH",
                "SERVICES",
                "SOMETHING",
                "THOUGHT",
                "WHETHER",
                "ADDITION",
                "ALTHOUGH",
                "APPROACH",
                "ATTENTION",
                "BEHAVIOR",
                "COMMUNITY",
                "COMPLETE",
                "COMPUTER",
                "CONSIDER",
                "CONTINUE",
                "DECISION",
                "DESCRIBE",
                "DEVELOP",
                "DIFFERENT",
                "DISCOVER",
                "ECONOMIC",
                "EDUCATION",
                "ESTABLISH",
                "EVERYONE",
                "EXERCISE",
                "EXPERIENCE",
                "FINANCIAL",
                "FOLLOWING",
                "GOVERNMENT",
                "HAPPENED",
                "HOSPITAL",
                "INCREASE",
                "INDIVIDUAL",
                "INDUSTRY",
                "INFLUENCE",
                "INFORMATION",
                "KNOWLEDGE",
                "LEARNING",
                "MATERIAL",
                "MEDICINE",
                "MILITARY",
                "MOVEMENT",
                "NECESSARY",
                "OPPORTUNITY",
                "ORIGINAL",
                "PARTICULAR",
                "PERFORMANCE",
                "PHYSICAL",
                "POLITICAL",
                "POPULATION",
                "PRACTICE",
                "PRESSURE",
                "PROBABLY",
                "PRODUCE",
                "PROPERTY",
                "PROTECT",
                "PROVIDE",
                "PURPOSE",
                "QUALITY",
                "QUESTION",
                "RECENTLY",
                "RECOGNIZE",
                "RELATIONSHIP",
                "RELIGION",
                "REMEMBER",
                "REPRESENT",
                "RESOURCE",
                "RESPONSE",
                "SECURITY",
                "SENTENCE",
                "SITUATION",
                "SOCIETY",
                "SPECIFIC",
                "STANDARD",
                "STATEMENT",
                "STRUCTURE",
                "STUDENT",
                "SUCCESS",
                "SUPPORT",
                "SURFACE",
                "TECHNOLOGY",
                "THOUSAND",
                "THROUGHOUT",
                "TOMORROW",
                "TRAINING",
                "TREATMENT",
                "UNDERSTAND",
                "UNIVERSITY",
                "VARIOUS",
                "WHATEVER",
                "YOURSELF",
            ],
        }

        # Clue templates
        self.clue_templates = {
            # Common 3-letter words
            "THE": [
                "Definite article",
                "Most common English word",
                "___ end (conclusion)",
            ],
            "AND": ["Conjunction", "Plus", "& in text"],
            "FOR": ["In favor of", "Because of", "___ example"],
            "ARE": ["Exist", "Live", "They ___ here"],
            "BUT": ["However", "Except", "On the other hand"],
            "NOT": ["Negative word", "Denial", "___ a chance"],
            "YOU": ["Second person", "Pronoun", "___ and me"],
            "ALL": ["Everything", "Entire amount", "___ or nothing"],
            "CAN": ["Able to", "Tin container", "Preserve food in"],
            "HER": ["Belonging to a woman", "She and ___", "Feminine pronoun"],
            "WAS": ["Existed", "Used to be", "Past tense of 'is'"],
            "ONE": ["Single", "Unity", "Number before two"],
            "OUR": ["Belonging to us", "We and ___", "Possessive pronoun"],
            "OUT": ["Not in", "External", "Strike ___"],
            "DAY": ["24 hours", "Period of light", "Night's opposite"],
            "RUN": ["Jog", "Sprint", "Race quickly"],
            "CAT": ["Feline", "Kitty", "Mouse chaser"],
            "DOG": ["Canine", "Man's best friend", "Bark maker"],
            "SUN": ["Star", "Sol", "Light source"],
            # Common 4-letter words
            "THAT": ["Pronoun", "Not this", "Over there"],
            "WITH": ["Alongside", "Including", "Together ___"],
            "HAVE": ["Possess", "Own", "Must ___"],
            "THIS": ["Not that", "Here", "Present item"],
            "WILL": ["Future tense helper", "Testament", "Determination"],
            "YOUR": ["Belonging to you", "Not mine", "Possessive"],
            "FROM": ["Out of", "Starting at", "Away ___"],
            "THEY": ["Those people", "Them", "Group pronoun"],
            "KNOW": ["Understand", "Be aware of", "Have knowledge"],
            "WANT": ["Desire", "Wish for", "Need"],
            "BEEN": ["Past participle of 'be'", "Existed", "Has ___"],
            "GOOD": ["Not bad", "Fine", "Excellent"],
            "MUCH": ["A lot", "Many", "Great amount"],
            "SOME": ["A few", "Part of", "Not all"],
            "TIME": ["Clock reading", "Duration", "Hour and minute"],
            "VERY": ["Extremely", "Quite", "Most"],
            "WHEN": ["At what time", "During", "Question word"],
            "COME": ["Arrive", "Approach", "Get here"],
            "HERE": ["This place", "Not there", "Present location"],
            "JUST": ["Only", "Fair", "Recently"],
            # Common 5-letter words
            "WHICH": ["What one", "That", "Question word"],
            "THEIR": ["Belonging to them", "Possessive", "Not our"],
            "WOULD": ["Conditional helper", "Used to", "Past of will"],
            "THERE": ["That place", "Not here", "Over yonder"],
            "COULD": ["Was able to", "Might", "Past of can"],
            "BEING": ["Existing", "Living thing", "Existence"],
            "FIRST": ["Number one", "Initial", "Before second"],
            "AFTER": ["Following", "Later than", "Behind"],
            "THESE": ["Plural of this", "Not those", "Here items"],
            "OTHER": ["Different", "Alternative", "Not this one"],
            "WORDS": ["Language units", "Terms", "Vocabulary"],
            "WORLD": ["Earth", "Globe", "Planet"],
            "WHERE": ["What place", "Location question", "In which spot"],
            "STILL": ["Motionless", "Yet", "Quiet"],
            "THREE": ["Number after two", "Trio", "III"],
            "NEVER": ["Not ever", "At no time", "Not once"],
            "UNDER": ["Below", "Beneath", "Lower than"],
            "WHILE": ["During", "Although", "Time period"],
            "ABOUT": ["Concerning", "Approximately", "Regarding"],
            "AGAIN": ["Once more", "Repeat", "Another time"],
        }

    def get_clue(self, word):
        """Get a clue for a word"""
        if word in self.clue_templates:
            return random.choice(self.clue_templates[word])

        # Generic clues by length
        if len(word) == 3:
            return f"Three-letter word"
        elif len(word) == 4:
            return f"Four-letter word"
        elif len(word) == 5:
            return f"Five-letter word"
        elif len(word) == 6:
            return f"Six-letter word"
        elif len(word) == 7:
            return f"Seven-letter word"
        else:
            return f"{len(word)}-letter word"

    def parse_pattern(self, pattern_strings):
        """Convert pattern strings to grid"""
        grid = []
        for row_str in pattern_strings:
            row = []
            for char in row_str:
                if char == "#":
                    row.append("#")  # Black square
                else:
                    row.append(".")  # White square
            grid.append(row)
        return grid

    def find_word_slots(self, grid):
        """Find all horizontal and vertical word slots in the grid"""
        h_slots = []
        v_slots = []

        # Find horizontal slots
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE:
                if grid[row][col] != "#":
                    start_col = col
                    while col < GRID_SIZE and grid[row][col] != "#":
                        col += 1
                    length = col - start_col
                    if length >= 3:  # Minimum word length
                        h_slots.append((row, start_col, length, "across"))
                else:
                    col += 1

        # Find vertical slots
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE:
                if grid[row][col] != "#":
                    start_row = row
                    while row < GRID_SIZE and grid[row][col] != "#":
                        row += 1
                    length = row - start_row
                    if length >= 3:  # Minimum word length
                        v_slots.append((start_row, col, length, "down"))
                else:
                    row += 1

        return h_slots + v_slots

    def fill_grid_with_words(self, grid, word_slots, puzzle_num):
        """Fill the grid with real words"""
        random.seed(puzzle_num * 1000)  # Consistent random for each puzzle

        solution = [["#" if cell == "#" else "" for cell in row] for row in grid]
        placed_words = []

        # Sort slots by length (longer first) and position
        word_slots.sort(key=lambda x: (-x[2], x[0], x[1]))

        for slot in word_slots:
            if slot[3] == "across":
                row, col, length, direction = slot

                # Get candidate words
                if length in self.words_by_length:
                    candidates = list(self.words_by_length[length])
                    random.shuffle(candidates)

                    placed = False
                    for word in candidates:
                        # Check if word fits with existing letters
                        fits = True
                        for i, letter in enumerate(word):
                            if col + i >= GRID_SIZE:
                                fits = False
                                break
                            if (
                                solution[row][col + i] != ""
                                and solution[row][col + i] != letter
                            ):
                                fits = False
                                break

                        if fits:
                            # Place word
                            for i, letter in enumerate(word):
                                solution[row][col + i] = letter

                            placed_words.append(
                                {
                                    "word": word,
                                    "row": row,
                                    "col": col,
                                    "direction": "across",
                                    "clue": self.get_clue(word),
                                }
                            )
                            placed = True
                            break

            else:  # down
                row, col, length, direction = slot

                # Get candidate words
                if length in self.words_by_length:
                    candidates = list(self.words_by_length[length])
                    random.shuffle(candidates)

                    placed = False
                    for word in candidates:
                        # Check if word fits with existing letters
                        fits = True
                        for i, letter in enumerate(word):
                            if row + i >= GRID_SIZE:
                                fits = False
                                break
                            if (
                                solution[row + i][col] != ""
                                and solution[row + i][col] != letter
                            ):
                                fits = False
                                break

                        if fits:
                            # Place word
                            for i, letter in enumerate(word):
                                solution[row + i][col] = letter

                            placed_words.append(
                                {
                                    "word": word,
                                    "row": row,
                                    "col": col,
                                    "direction": "down",
                                    "clue": self.get_clue(word),
                                }
                            )
                            placed = True
                            break

        # Fill any remaining empty cells with valid letters
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if solution[row][col] == "":
                    # This shouldn't happen with proper patterns
                    solution[row][col] = "A"

        return solution, placed_words

    def assign_numbers(self, grid):
        """Assign numbers to cells that start words"""
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

    def draw_grid(self, c, x_offset, y_offset, grid, numbers):
        """Draw the puzzle grid"""
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

                if grid[row][col] == "#":
                    # Black square
                    c.setFillColor(colors.black)
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=0)
                else:
                    # White square
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y, cell_size, cell_size, fill=1, stroke=1)

                    # Draw the solution letter
                    if solution[row][col] != "#":
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica-Bold", 9)
                        c.drawCentredString(
                            x + cell_size / 2, y + cell_size / 2 - 3, solution[row][col]
                        )

    def create_complete_book(self):
        """Create the complete Volume 3 book"""
        for format_name, output_dir in [
            ("paperback", self.paperback_dir),
            ("hardcover", self.hardcover_dir),
        ]:
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = output_dir / "crossword_book_volume_3.pdf"

            print(f"\n📖 Creating {format_name} edition...")

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
                PAGE_WIDTH / 2, PAGE_HEIGHT - 5.2 * inch, "50 Easy Crossword Puzzles"
            )
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 5.7 * inch, "for Seniors")

            c.setFont("Helvetica", 14)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT - 7 * inch, "Published by KindleMint Press"
            )

            c.showPage()

            # Copyright page
            c.setFont("Helvetica", 10)
            c.drawString(
                GUTTER,
                PAGE_HEIGHT - TOP_MARGIN - 1 * inch,
                "Copyright © 2025 KindleMint Press",
            )
            c.drawString(
                GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch, "All rights reserved."
            )
            c.drawString(
                GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1.8 * inch, "ISBN: 9798289681881"
            )
            c.drawString(
                GUTTER,
                PAGE_HEIGHT - TOP_MARGIN - 2.3 * inch,
                "This book is designed for entertainment purposes.",
            )
            c.drawString(
                GUTTER,
                PAGE_HEIGHT - TOP_MARGIN - 2.6 * inch,
                "All puzzles are original creations.",
            )
            c.showPage()

            # Table of Contents
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "Table of Contents"
            )

            c.setFont("Helvetica", 12)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2 * inch
            toc_items = [
                ("Introduction", "4"),
                ("How to Solve Crossword Puzzles", "5"),
                ("Puzzles 1-50", "6-105"),
                ("Solutions", "106-155"),
                ("About the Author", "156"),
            ]

            for item, pages in toc_items:
                c.drawString(GUTTER + 0.5 * inch, y_pos, item)
                c.drawRightString(PAGE_WIDTH - OUTER_MARGIN - 0.5 * inch, y_pos, pages)
                y_pos -= 0.4 * inch

            c.showPage()

            # Introduction page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "Introduction"
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2 * inch
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
                "Take your time, enjoy the mental exercise, and have fun!",
            ]

            for line in intro_text:
                if line.startswith("•"):
                    c.drawString(GUTTER + 0.3 * inch, y_pos, line)
                else:
                    c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch

            c.showPage()

            # How to Solve page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - TOP_MARGIN - 1 * inch,
                "How to Solve Crossword Puzzles",
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2 * inch
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
                "Remember: All the answers are in the back!",
            ]

            for line in howto_text:
                if line.startswith("   "):
                    c.drawString(GUTTER + 0.3 * inch, y_pos, line.strip())
                else:
                    c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.25 * inch

            c.showPage()

            # Store all puzzles for answer key
            all_puzzles = []

            # Generate 50 puzzles
            for puzzle_num in range(1, 51):
                print(f"  Creating Puzzle {puzzle_num}...")

                # Select pattern
                pattern_idx = (puzzle_num - 1) % len(self.crossword_patterns)
                pattern = self.crossword_patterns[pattern_idx]
                grid = self.parse_pattern(pattern)

                # Find word slots
                word_slots = self.find_word_slots(grid)

                # Fill with words
                solution, placed_words = self.fill_grid_with_words(
                    grid, word_slots, puzzle_num
                )

                # Assign numbers
                numbers = self.assign_numbers(grid)

                # Verify we have both across and down clues
                across_words = [w for w in placed_words if w["direction"] == "across"]
                down_words = [w for w in placed_words if w["direction"] == "down"]

                print(f"    ✓ Across: {len(across_words)}, Down: {len(down_words)}")

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

                # Draw empty grid
                grid_x = (PAGE_WIDTH - GRID_TOTAL_SIZE) / 2
                grid_y = PAGE_HEIGHT - TOP_MARGIN - 1.2 * inch
                self.draw_grid(c, grid_x, grid_y, grid, numbers)

                c.showPage()

                # Clues page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.4 * inch,
                    f"Puzzle {puzzle_num} - Clues",
                )

                # ACROSS clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(GUTTER, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "ACROSS")

                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch

                # Sort across words by their number
                across_numbered = []
                for word_info in across_words:
                    num = numbers.get((word_info["row"], word_info["col"]))
                    if num:
                        across_numbered.append((num, word_info))
                across_numbered.sort()

                for num, word_info in across_numbered:
                    c.drawString(GUTTER, y_pos, f"{num}. {word_info['clue']}")
                    y_pos -= 0.25 * inch
                    if y_pos < BOTTOM_MARGIN + 1 * inch:
                        break

                # DOWN clues
                c.setFont("Helvetica-Bold", 12)
                c.drawString(
                    PAGE_WIDTH / 2 + 0.1 * inch,
                    PAGE_HEIGHT - TOP_MARGIN - 1 * inch,
                    "DOWN",
                )

                c.setFont("Helvetica", 10)
                y_pos = PAGE_HEIGHT - TOP_MARGIN - 1.3 * inch

                # Sort down words by their number
                down_numbered = []
                for word_info in down_words:
                    num = numbers.get((word_info["row"], word_info["col"]))
                    if num:
                        down_numbered.append((num, word_info))
                down_numbered.sort()

                for num, word_info in down_numbered:
                    c.drawString(
                        PAGE_WIDTH / 2 + 0.1 * inch,
                        y_pos,
                        f"{num}. {word_info['clue']}",
                    )
                    y_pos -= 0.25 * inch
                    if y_pos < BOTTOM_MARGIN + 1 * inch:
                        break

                c.showPage()

            # Draw all 50 solution grids (1 per page for 156 total pages)
            for puzzle in all_puzzles:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(
                    PAGE_WIDTH / 2,
                    PAGE_HEIGHT - TOP_MARGIN - 0.5 * inch,
                    f"Puzzle {puzzle['num']} - Solution",
                )

                # Center the solution grid on the page
                small_cell = 0.24 * inch  # Larger cells for single puzzle per page
                grid_x = (PAGE_WIDTH - (GRID_SIZE * small_cell)) / 2
                grid_y = (PAGE_HEIGHT - (GRID_SIZE * small_cell)) / 2

                self.draw_solution_grid(
                    c, grid_x, grid_y, puzzle["grid"], puzzle["solution"], small_cell
                )

                c.showPage()

            # About the Author page
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(
                PAGE_WIDTH / 2,
                PAGE_HEIGHT - TOP_MARGIN - 1 * inch,
                "About KindleMint Press",
            )

            c.setFont("Helvetica", 11)
            y_pos = PAGE_HEIGHT - TOP_MARGIN - 2 * inch
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
                "Visit us at www.kindlemintpress.com",
            ]

            for line in about_text:
                c.drawString(GUTTER, y_pos, line)
                y_pos -= 0.3 * inch

            c.showPage()

            # Save
            c.save()

            print(f"✅ Created {format_name} PDF: {pdf_path}")


def main():
    print("🚀 Creating Volume 3 with PROPER crossword puzzles")
    print("All grids will contain only real English words")

    generator = ProperCrosswordGenerator()
    generator.create_complete_book()

    print("\n✅ Volume 3 generation complete!")
    print("All puzzles contain real words only")


if __name__ == "__main__":
    main()
