#!/usr/bin/env python3
"""
Crossword Engine v3 Fixed - Command Line Interface
Generates high-quality crossword puzzles for KindleMint Engine with proper word filling
"""

import argparse
import json
import logging
import random
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Add project root to path to allow importing config_loader
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

try:
    from scripts.config_loader import config
except ImportError:
    print(
        "❌ ERROR: Could not import config_loader. Make sure it exists in the 'scripts' directory."
    )

    # Define a dummy config object to prevent crashing if the import fails
    class DummyConfig:
        def get(self, key, default=None):
            return default

        def get_path(self, key, default=None):
            return default

        def get_puzzle_setting(self, puzzle_type, key):
            return None

        def get_qa_threshold(self, key):
            return None

    config = DummyConfig()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CrosswordEngine")


class CrosswordEngineV3:
    """Generate crossword puzzles with proper filled grids and real words"""

    def __init__(
        self,
        output_dir,
        puzzle_count=None,
        difficulty=None,
        grid_size=None,
        word_count=None,
        max_word_length=None,
        min_word_length=None,
        word_list_path=None,
    ):
        """Initialize the crossword generator with configuration."""

        # --- Load settings from config, with overrides from arguments ---
        self.grid_size = (
            grid_size or config.get_puzzle_setting("crossword", "grid_size") or 15
        )
        self.puzzle_count = (
            puzzle_count or config.get("puzzle_generation.default_puzzle_count") or 50
        )
        self.difficulty_mode = difficulty or "mixed"
        self.max_word_length = (
            max_word_length
            or config.get_puzzle_setting("crossword", "max_word_length")
            or 15
        )
        self.min_word_length = (
            min_word_length
            or config.get_puzzle_setting("crossword", "min_word_length")
            or 3
        )
        self.word_list_path = word_list_path or config.get_path(
            "file_paths.word_list_path"
        )
        self.backtracking_max_attempts = (
            config.get_puzzle_setting("crossword", "backtracking_max_attempts") or 3
        )
        self.difficulty_distribution = config.get_puzzle_setting(
            "crossword", "difficulty_distribution"
        ) or {"easy_ratio": 0.4, "medium_ratio": 0.4}

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.word_count = word_count  # Not used by generator logic, but can be metadata

        # --- Create directory structure from config ---
        puzzles_subdir = config.get("file_paths.puzzles_subdir", "puzzles")
        metadata_subdir = config.get("file_paths.metadata_subdir", "metadata")
        solutions_subdir = config.get("file_paths.solutions_subdir", "solutions")

        self.puzzles_dir = self.output_dir / puzzles_subdir
        self.puzzles_dir.mkdir(exist_ok=True)

        self.metadata_dir = self.output_dir / metadata_subdir
        self.metadata_dir.mkdir(exist_ok=True)

        self.solutions_dir = self.output_dir / solutions_subdir
        self.solutions_dir.mkdir(exist_ok=True)

        # --- Load resources ---
        self.word_dict = self._load_word_dictionary()
        logger.info(f"Loaded {len(self.word_dict)} words into dictionary")

        self.theme_words = self._generate_theme_words()

    def _load_word_dictionary(self):
        """Load word dictionary from file or use built-in common words."""
        word_dict = {}

        if self.word_list_path and self.word_list_path.exists():
            with open(self.word_list_path, "r") as f:
                for line in f:
                    word = line.strip().upper()
                    if (
                        self.min_word_length <= len(word) <= self.max_word_length
                        and word.isalpha()
                    ):
                        word_dict[word] = True
        else:
            if self.word_list_path:
                logger.warning(
                    f"Word list not found at {self.word_list_path}. Falling back to built-in list."
                )
            # Use built-in common English words (limited set)
            common_words = [
                # 3-letter words
                "ACE",
                "ACT",
                "ADD",
                "AGE",
                "AGO",
                "AID",
                "AIM",
                "AIR",
                "ALL",
                "AND",
                "ANY",
                "ARM",
                "ART",
                "ASK",
                "BAD",
                "BAG",
                "BAR",
                "BAT",
                "BAY",
                "BED",
                "BEE",
                "BIG",
                "BIT",
                "BOX",
                "BOY",
                "BUG",
                "BUS",
                "BUY",
                "CAB",
                "CAP",
                "CAR",
                "CAT",
                "CUT",
                "DAD",
                "DAY",
                "DIE",
                "DIG",
                "DOG",
                "DOT",
                "DRY",
                "DUE",
                "EAR",
                "EAT",
                "EGG",
                "END",
                "ERA",
                "EVE",
                "EYE",
                "FAN",
                "FAR",
                "FEE",
                "FEW",
                "FIT",
                "FIX",
                "FLY",
                "FOG",
                "FOR",
                "FOX",
                "FUN",
                "GAP",
                "GAS",
                "GET",
                "GOD",
                "GOT",
                "GUN",
                "GUY",
                "GYM",
                "HAD",
                "HAT",
                "HAS",
                "HAY",
                "HER",
                "HID",
                "HIM",
                "HIP",
                "HIS",
                "HIT",
                "HOT",
                "HOW",
                "HUB",
                "HUG",
                "ICE",
                "ILL",
                "INK",
                "INN",
                "JAM",
                "JAR",
                "JET",
                "JOB",
                "JOG",
                "JOY",
                "KEY",
                "KID",
                "KIT",
                "LAB",
                "LAD",
                "LAG",
                "LAP",
                "LAW",
                "LAY",
                "LEG",
                "LET",
                "LID",
                "LIE",
                "LIP",
                "LOG",
                "LOT",
                "LOW",
                "MAP",
                "MAT",
                "MAX",
                "MAY",
                "MEN",
                "MET",
                "MIX",
                "MOB",
                "MOM",
                "MOP",
                "MUD",
                "MUG",
                "NAP",
                "NET",
                "NEW",
                "NIL",
                "NOR",
                "NOT",
                "NOW",
                "NUT",
                "OAK",
                "ODD",
                "OFF",
                "OIL",
                "OLD",
                "ONE",
                "OUR",
                "OUT",
                "OWL",
                "OWN",
                "PAD",
                "PAN",
                "PAR",
                "PAT",
                "PAW",
                "PAY",
                "PEN",
                "PET",
                "PIE",
                "PIG",
                "PIN",
                "PIT",
                "POT",
                "PRO",
                "PUT",
                "RAG",
                "RAT",
                "RAW",
                "RED",
                "RIB",
                "RID",
                "RIG",
                "RIM",
                "RIP",
                "ROD",
                "ROW",
                "RUB",
                "RUG",
                "RUN",
                "SAD",
                "SAG",
                "SAT",
                "SAW",
                "SAY",
                "SEA",
                "SEE",
                "SET",
                "SEW",
                "SHE",
                "SHY",
                "SIN",
                "SIP",
                "SIR",
                "SIT",
                "SIX",
                "SKI",
                "SKY",
                "SLY",
                "SON",
                "SPA",
                "SPY",
                "SUM",
                "SUN",
                "TAB",
                "TAG",
                "TAP",
                "TAX",
                "TEA",
                "TEN",
                "THE",
                "TIE",
                "TIN",
                "TIP",
                "TOE",
                "TON",
                "TOP",
                "TOW",
                "TOY",
                "TRY",
                "TUB",
                "TWO",
                "USE",
                "VAN",
                "VAT",
                "VET",
                "VIA",
                "WAR",
                "WAS",
                "WAX",
                "WAY",
                "WEB",
                "WET",
                "WHO",
                "WHY",
                "WIN",
                "WON",
                "YES",
                "YET",
                "YOU",
                "ZOO",
                # 4-letter words
                "ABLE",
                "ACID",
                "AGED",
                "ALSO",
                "AREA",
                "ARMY",
                "AWAY",
                "BABY",
                "BACK",
                "BALL",
                "BAND",
                "BANK",
                "BASE",
                "BATH",
                "BEAR",
                "BEAT",
                "BEEN",
                "BEER",
                "BELL",
                "BELT",
                "BEST",
                "BILL",
                "BIRD",
                "BLOW",
                "BLUE",
                "BOAT",
                "BODY",
                "BOMB",
                "BOND",
                "BONE",
                "BOOK",
                "BOOM",
                "BORN",
                "BOSS",
                "BOTH",
                "BOWL",
                "BULK",
                "BURN",
                "BUSH",
                "BUSY",
                "CALL",
                "CALM",
                "CAME",
                "CAMP",
                "CARD",
                "CARE",
                "CASE",
                "CASH",
                "CAST",
                "CELL",
                "CHAT",
                "CHIP",
                "CITY",
                "CLUB",
                "COAL",
                "COAT",
                "CODE",
                "COLD",
                "COME",
                "COOK",
                "COOL",
                "COPE",
                "COPY",
                "CORE",
                "COST",
                "CREW",
                "CROP",
                "DARK",
                "DATA",
                "DATE",
                "DAWN",
                "DAYS",
                "DEAD",
                "DEAL",
                "DEAN",
                "DEAR",
                "DEBT",
                "DEEP",
                "DENY",
                "DESK",
                "DIAL",
                "DIET",
                "DIRT",
                "DISC",
                "DISK",
                "DOES",
                "DONE",
                "DOOR",
                "DOSE",
                "DOWN",
                "DRAW",
                "DROP",
                "DRUG",
                "DUAL",
                "DUKE",
                "DUST",
                "DUTY",
                "EACH",
                "EARN",
                "EASE",
                "EAST",
                "EASY",
                "EDGE",
                "ELSE",
                "EVEN",
                "EVER",
                "EVIL",
                "EXIT",
                "FACE",
                "FACT",
                "FAIL",
                "FAIR",
                "FALL",
                "FARM",
                "FAST",
                "FATE",
                "FEAR",
                "FEED",
                "FEEL",
                "FEET",
                "FELL",
                "FELT",
                "FILE",
                "FILL",
                "FILM",
                "FIND",
                "FINE",
                "FIRE",
                "FIRM",
                "FISH",
                "FIVE",
                "FLAT",
                "FLOW",
                "FOOD",
                "FOOT",
                "FORD",
                "FORM",
                "FORT",
                "FOUR",
                "FREE",
                "FROM",
                "FUEL",
                "FULL",
                "FUND",
                "GAIN",
                "GAME",
                "GATE",
                "GAVE",
                "GEAR",
                "GENE",
                "GIFT",
                "GIRL",
                "GIVE",
                "GLAD",
                "GOAL",
                "GOES",
                "GOLD",
                "GOLF",
                "GONE",
                "GOOD",
                "GRAY",
                "GREW",
                "GREY",
                "GROW",
                "GULF",
                "HAIR",
                "HALF",
                "HALL",
                "HAND",
                "HANG",
                "HARD",
                "HARM",
                "HATE",
                "HAVE",
                "HEAD",
                "HEAR",
                "HEAT",
                "HELD",
                "HELL",
                "HELP",
                "HERE",
                "HERO",
                "HIGH",
                "HILL",
                "HIRE",
                "HOLD",
                "HOLE",
                "HOLY",
                "HOME",
                "HOPE",
                "HOST",
                "HOUR",
                "HUGE",
                "HUNG",
                "HUNT",
                "HURT",
                "IDEA",
                "INCH",
                "INTO",
                "IRON",
                "ITEM",
                "JACK",
                "JANE",
                "JEAN",
                "JOHN",
                "JOIN",
                "JUMP",
                "JURY",
                "JUST",
                "KEEN",
                "KEEP",
                "KENT",
                "KEPT",
                "KICK",
                "KILL",
                "KIND",
                "KING",
                "KNEE",
                "KNEW",
                "KNOW",
                "LACK",
                "LADY",
                "LAID",
                "LAKE",
                "LAND",
                "LANE",
                "LAST",
                "LATE",
                "LEAD",
                "LEFT",
                "LESS",
                "LIFE",
                "LIFT",
                "LIKE",
                "LINE",
                "LINK",
                "LIST",
                "LIVE",
                "LOAD",
                "LOAN",
                "LOCK",
                "LOGO",
                "LONG",
                "LOOK",
                "LORD",
                "LOSE",
                "LOSS",
                "LOST",
                "LOVE",
                "LUCK",
                "MADE",
                "MAIL",
                "MAIN",
                "MAKE",
                "MALE",
                "MANY",
                "MARK",
                "MASS",
                "MATT",
                "MEAL",
                "MEAN",
                "MEAT",
                "MEET",
                "MENU",
                "MERE",
                "MIKE",
                "MILE",
                "MILK",
                "MILL",
                "MIND",
                "MINE",
                "MISS",
                "MODE",
                "MOOD",
                "MOON",
                "MORE",
                "MOST",
                "MOVE",
                "MUCH",
                "MUST",
                "NAME",
                "NAVY",
                "NEAR",
                "NECK",
                "NEED",
                "NEWS",
                "NEXT",
                "NICE",
                "NICK",
                "NINE",
                "NONE",
                "NOSE",
                "NOTE",
                "OKAY",
                "ONCE",
                "ONLY",
                "ONTO",
                "OPEN",
                "ORAL",
                "OVER",
                "PACE",
                "PACK",
                "PAGE",
                "PAID",
                "PAIN",
                "PAIR",
                "PALM",
                "PARK",
                "PART",
                "PASS",
                "PAST",
                "PATH",
                "PEAK",
                "PICK",
                "PINK",
                "PIPE",
                "PLAN",
                "PLAY",
                "PLOT",
                "PLUG",
                "PLUS",
                "POLL",
                "POOL",
                "POOR",
                "PORT",
                "POST",
                "PULL",
                "PURE",
                "PUSH",
                "RACE",
                "RAIL",
                "RAIN",
                "RANK",
                "RARE",
                "RATE",
                "READ",
                "REAL",
                "REAR",
                "RELY",
                "RENT",
                "REST",
                "RICE",
                "RICH",
                "RIDE",
                "RING",
                "RISE",
                "RISK",
                "ROAD",
                "ROCK",
                "ROLE",
                "ROLL",
                "ROOF",
                "ROOM",
                "ROOT",
                "ROSE",
                "RULE",
                "RUSH",
                "RUTH",
                "SAFE",
                "SAID",
                "SAKE",
                "SALE",
                "SALT",
                "SAME",
                "SAND",
                "SAVE",
                "SEAT",
                "SEED",
                "SEEK",
                "SEEM",
                "SEEN",
                "SELF",
                "SELL",
                "SEND",
                "SENT",
                "SEPT",
                "SHIP",
                "SHOP",
                "SHOT",
                "SHOW",
                "SHUT",
                "SICK",
                "SIDE",
                "SIGN",
                "SITE",
                "SIZE",
                "SKIN",
                "SLIP",
                "SLOW",
                "SNOW",
                "SOFT",
                "SOIL",
                "SOLD",
                "SOLE",
                "SOME",
                "SONG",
                "SOON",
                "SORT",
                "SOUL",
                "SPOT",
                "STAR",
                "STAY",
                "STEP",
                "STOP",
                "SUCH",
                "SUIT",
                "SURE",
                "TAKE",
                "TALE",
                "TALK",
                "TALL",
                "TANK",
                "TAPE",
                "TASK",
                "TEAM",
                "TECH",
                "TELL",
                "TEND",
                "TERM",
                "TEST",
                "TEXT",
                "THAN",
                "THAT",
                "THEM",
                "THEN",
                "THEY",
                "THIN",
                "THIS",
                "THUS",
                "TILL",
                "TIME",
                "TINY",
                "TOLD",
                "TOLL",
                "TONE",
                "TONY",
                "TOOK",
                "TOOL",
                "TOUR",
                "TOWN",
                "TREE",
                "TRIP",
                "TRUE",
                "TUNE",
                "TURN",
                "TWIN",
                "TYPE",
                "UNIT",
                "UPON",
                "USED",
                "USER",
                "VARY",
                "VAST",
                "VERY",
                "VIEW",
                "VOTE",
                "WAGE",
                "WAIT",
                "WAKE",
                "WALK",
                "WALL",
                "WANT",
                "WARD",
                "WARM",
                "WASH",
                "WAVE",
                "WAYS",
                "WEAK",
                "WEAR",
                "WEEK",
                "WELL",
                "WENT",
                "WERE",
                "WEST",
                "WHAT",
                "WHEN",
                "WHOM",
                "WIDE",
                "WIFE",
                "WILD",
                "WILL",
                "WIND",
                "WINE",
                "WING",
                "WIRE",
                "WISE",
                "WISH",
                "WITH",
                "WOOD",
                "WORD",
                "WORE",
                "WORK",
                "YARD",
                "YEAH",
                "YEAR",
                "YOUR",
                "ZERO",
                "ZONE",
                # 5+ letter words (common ones)
                "ABOUT",
                "ABOVE",
                "ABUSE",
                "ACTOR",
                "ADAPT",
                "ADDED",
                "ADMIT",
                "ADOPT",
                "AFTER",
                "AGAIN",
                "AGENT",
                "AGREE",
                "AHEAD",
                "ALARM",
                "ALBUM",
                "ALERT",
                "ALIKE",
                "ALIVE",
                "ALLOW",
                "ALONE",
                "ALONG",
                "ALTER",
                "AMONG",
                "ANGER",
                "ANGLE",
                "ANGRY",
                "APART",
                "APPLE",
                "APPLY",
                "ARENA",
                "ARGUE",
                "ARISE",
                "ARRAY",
                "ASIDE",
                "ASSET",
                "AVOID",
                "AWARD",
                "AWARE",
                "BADLY",
                "BAKER",
                "BASES",
                "BASIC",
                "BASIS",
                "BEACH",
                "BEGAN",
                "BEGIN",
                "BEGUN",
                "BEING",
                "BELOW",
                "BENCH",
                "BILLY",
                "BIRTH",
                "BLACK",
                "BLAME",
                "BLANK",
                "BLAST",
                "BLEND",
                "BLESS",
                "BLIND",
                "BLOCK",
                "BLOOD",
                "BOARD",
                "BOOST",
                "BOOTH",
                "BOUND",
                "BRAIN",
                "BRAND",
                "BREAD",
                "BREAK",
                "BREED",
                "BRIEF",
                "BRING",
                "BROAD",
                "BROKE",
                "BROWN",
                "BUILD",
                "BUILT",
                "BUNCH",
                "BURST",
                "CABLE",
                "CALIF",
                "CARRY",
                "CATCH",
                "CAUSE",
                "CHAIN",
                "CHAIR",
                "CHART",
                "CHASE",
                "CHEAP",
                "CHECK",
                "CHEST",
                "CHIEF",
                "CHILD",
                "CHINA",
                "CHOSE",
                "CIVIL",
                "CLAIM",
                "CLASS",
                "CLEAN",
                "CLEAR",
                "CLICK",
                "CLOCK",
                "CLOSE",
                "COACH",
                "COAST",
                "COULD",
                "COUNT",
                "COURT",
                "COVER",
                "CRAFT",
                "CRASH",
                "CREAM",
                "CRIME",
                "CROSS",
                "CROWD",
                "CROWN",
                "CURVE",
                "CYCLE",
                "DAILY",
                "DANCE",
                "DATED",
                "DEALT",
                "DEATH",
                "DEBUT",
                "DELAY",
                "DEPTH",
                "DOING",
                "DOUBT",
                "DOZEN",
                "DRAFT",
                "DRAMA",
                "DRAWN",
                "DREAM",
                "DRESS",
                "DRILL",
                "DRINK",
                "DRIVE",
                "DROVE",
                "DYING",
                "EAGER",
                "EARLY",
                "EARTH",
                "EIGHT",
                "ELITE",
                "EMPTY",
                "ENEMY",
                "ENJOY",
                "ENTER",
                "ENTRY",
                "EQUAL",
                "ERROR",
                "EVENT",
                "EVERY",
                "EXACT",
                "EXIST",
                "EXTRA",
                "FAITH",
                "FALSE",
                "FAULT",
                "FAVOR",
                "FENCE",
                "FIELD",
                "FIFTH",
                "FIFTY",
                "FIGHT",
                "FINAL",
                "FIRST",
                "FIXED",
                "FLASH",
                "FLEET",
                "FLOOR",
                "FLUID",
                "FOCUS",
                "FORCE",
                "FORTH",
                "FORTY",
                "FORUM",
                "FOUND",
                "FRAME",
                "FRANK",
                "FRAUD",
                "FRESH",
                "FRONT",
                "FRUIT",
                "FULLY",
                "FUNNY",
                "GIANT",
                "GIVEN",
                "GLASS",
                "GLOBE",
                "GOING",
                "GRACE",
                "GRADE",
                "GRAND",
                "GRANT",
                "GRASS",
                "GREAT",
                "GREEN",
                "GROSS",
                "GROUP",
                "GROWN",
                "GUARD",
                "GUESS",
                "GUEST",
                "GUIDE",
                "HAPPY",
                "HARRY",
                "HEART",
                "HEAVY",
                "HENCE",
                "HENRY",
                "HORSE",
                "HOTEL",
                "HOUSE",
                "HUMAN",
                "IDEAL",
                "IMAGE",
                "INDEX",
                "INNER",
                "INPUT",
                "ISSUE",
                "JAPAN",
                "JIMMY",
                "JOINT",
                "JONES",
                "JUDGE",
                "KNOWN",
                "LABEL",
                "LARGE",
                "LASER",
                "LATER",
                "LAUGH",
                "LAYER",
                "LEARN",
                "LEASE",
                "LEAST",
                "LEAVE",
                "LEGAL",
                "LEVEL",
                "LEWIS",
                "LIGHT",
                "LIMIT",
                "LINKS",
                "LIVES",
                "LOCAL",
                "LOGIC",
                "LOOSE",
                "LOWER",
                "LUCKY",
                "LUNCH",
                "LYING",
                "MAGIC",
                "MAJOR",
                "MAKER",
                "MARCH",
                "MARIA",
                "MATCH",
                "MAYBE",
                "MAYOR",
                "MEANT",
                "MEDIA",
                "METAL",
                "MIGHT",
                "MINOR",
                "MINUS",
                "MIXED",
                "MODEL",
                "MONEY",
                "MONTH",
                "MORAL",
                "MOTOR",
                "MOUNT",
                "MOUSE",
                "MOUTH",
                "MOVIE",
                "MUSIC",
                "NEEDS",
                "NEVER",
                "NEWLY",
                "NIGHT",
                "NOISE",
                "NORTH",
                "NOTED",
                "NOVEL",
                "NURSE",
                "OCCUR",
                "OCEAN",
                "OFFER",
                "OFTEN",
                "ORDER",
                "OTHER",
                "OUGHT",
                "PAINT",
                "PANEL",
                "PAPER",
                "PARTY",
                "PEACE",
                "PETER",
                "PHASE",
                "PHONE",
                "PHOTO",
                "PIECE",
                "PILOT",
                "PITCH",
                "PLACE",
                "PLAIN",
                "PLANE",
                "PLANT",
                "PLATE",
                "POINT",
                "POUND",
                "POWER",
                "PRESS",
                "PRICE",
                "PRIDE",
                "PRIME",
                "PRINT",
                "PRIOR",
                "PRIZE",
                "PROOF",
                "PROUD",
                "PROVE",
                "QUEEN",
                "QUICK",
                "QUIET",
                "QUITE",
                "RADIO",
                "RAISE",
                "RANGE",
                "RAPID",
                "RATIO",
                "REACH",
                "READY",
                "REFER",
                "RIGHT",
                "RIVAL",
                "RIVER",
                "ROBIN",
                "ROGER",
                "ROMAN",
                "ROUGH",
                "ROUND",
                "ROUTE",
                "ROYAL",
                "RURAL",
                "SCALE",
                "SCENE",
                "SCOPE",
                "SCORE",
                "SENSE",
                "SERVE",
                "SEVEN",
                "SHALL",
                "SHAPE",
                "SHARE",
                "SHARP",
                "SHEET",
                "SHELF",
                "SHELL",
                "SHIFT",
                "SHIRT",
                "SHOCK",
                "SHOOT",
                "SHORT",
                "SHOWN",
                "SIGHT",
                "SINCE",
                "SIXTH",
                "SIXTY",
                "SIZED",
                "SKILL",
                "SLEEP",
                "SLIDE",
                "SMALL",
                "SMART",
                "SMILE",
                "SMITH",
                "SMOKE",
                "SOLID",
                "SOLVE",
                "SORRY",
                "SOUND",
                "SOUTH",
                "SPACE",
                "SPARE",
                "SPEAK",
                "SPEED",
                "SPEND",
                "SPENT",
                "SPLIT",
                "SPOKE",
                "SPORT",
                "STAFF",
                "STAGE",
                "STAKE",
                "STAND",
                "START",
                "STATE",
                "STEAM",
                "STEEL",
                "STICK",
                "STILL",
                "STOCK",
                "STONE",
                "STOOD",
                "STORE",
                "STORM",
                "STORY",
                "STRIP",
                "STUCK",
                "STUDY",
                "STUFF",
                "STYLE",
                "SUGAR",
                "SUITE",
                "SUPER",
                "SWEET",
                "TABLE",
                "TAKEN",
                "TASTE",
                "TAXES",
                "TEACH",
                "TEETH",
                "TERRY",
                "TEXAS",
                "THANK",
                "THEFT",
                "THEIR",
                "THEME",
                "THERE",
                "THESE",
                "THICK",
                "THING",
                "THINK",
                "THIRD",
                "THOSE",
                "THREE",
                "THREW",
                "THROW",
                "TIGHT",
                "TIMES",
                "TIRED",
                "TITLE",
                "TODAY",
                "TOPIC",
                "TOTAL",
                "TOUCH",
                "TOUGH",
                "TOWER",
                "TRACK",
                "TRADE",
                "TRAIN",
                "TREAT",
                "TREND",
                "TRIAL",
                "TRIED",
                "TRIES",
                "TRUCK",
                "TRULY",
                "TRUST",
                "TRUTH",
                "TWICE",
                "UNDER",
                "UNDUE",
                "UNION",
                "UNITY",
                "UNTIL",
                "UPPER",
                "UPSET",
                "URBAN",
                "USAGE",
                "USUAL",
                "VALID",
                "VALUE",
                "VIDEO",
                "VIRUS",
                "VISIT",
                "VITAL",
                "VOICE",
                "WASTE",
                "WATCH",
                "WATER",
                "WHEEL",
                "WHERE",
                "WHICH",
                "WHILE",
                "WHITE",
                "WHOLE",
                "WHOSE",
                "WOMAN",
                "WOMEN",
                "WORLD",
                "WORRY",
                "WORSE",
                "WORST",
                "WORTH",
                "WOULD",
                "WOUND",
                "WRITE",
                "WRONG",
                "WROTE",
                "YIELD",
                "YOUNG",
                "YOUTH",
            ]

            for word in common_words:
                if self.min_word_length <= len(word) <= self.max_word_length:
                    word_dict[word] = True

            longer_words = [
                "PUZZLE",
                "CROSSWORD",
                "SOLUTION",
                "CHALLENGE",
                "DICTIONARY",
                "KNOWLEDGE",
                "QUESTION",
                "ANSWER",
                "MYSTERY",
                "DISCOVERY",
                "LEARNING",
                "THINKING",
                "PROBLEM",
                "SOLVING",
                "EDUCATION",
                "EXPERIENCE",
                "ADVENTURE",
                "JOURNEY",
                "EXPLORATION",
                "WISDOM",
                "CREATIVITY",
                "IMAGINATION",
                "INNOVATION",
                "INSPIRATION",
                "MOTIVATION",
                "DETERMINATION",
                "PERSISTENCE",
                "PATIENCE",
                "DILIGENCE",
                "EXCELLENCE",
                "ACHIEVEMENT",
                "SUCCESS",
                "VICTORY",
                "TRIUMPH",
                "ACCOMPLISHMENT",
                "DEVELOPMENT",
                "PROGRESS",
                "GROWTH",
                "IMPROVEMENT",
                "ADVANCEMENT",
                "UNDERSTANDING",
                "COMPREHENSION",
                "PERCEPTION",
                "RECOGNITION",
                "AWARENESS",
                "INTELLIGENCE",
                "BRILLIANCE",
                "GENIUS",
                "MASTERY",
                "EXPERTISE",
            ]

            for word in longer_words:
                if self.min_word_length <= len(word) <= self.max_word_length:
                    word_dict[word] = True

        return word_dict

    def _generate_theme_words(self):
        """Generate theme-specific word lists"""
        theme_words = {
            # Easy themes
            "Garden Flowers": [
                "ROSE",
                "DAISY",
                "TULIP",
                "LILY",
                "IRIS",
                "PANSY",
                "POPPY",
                "DAHLIA",
            ],
            "Kitchen Tools": [
                "KNIFE",
                "SPOON",
                "FORK",
                "WHISK",
                "GRATER",
                "SPATULA",
                "LADLE",
                "POT",
                "PAN",
            ],
            "Family Time": [
                "GAME",
                "MOVIE",
                "DINNER",
                "CHAT",
                "PLAY",
                "LAUGH",
                "SHARE",
                "LOVE",
                "HUG",
            ],
            "Weather": [
                "RAIN",
                "SNOW",
                "WIND",
                "STORM",
                "SUN",
                "CLOUD",
                "HEAT",
                "COLD",
                "FOG",
            ],
            "Colors": [
                "RED",
                "BLUE",
                "GREEN",
                "YELLOW",
                "PURPLE",
                "ORANGE",
                "PINK",
                "BROWN",
                "BLACK",
                "WHITE",
            ],
            "Fruits": [
                "APPLE",
                "BANANA",
                "ORANGE",
                "GRAPE",
                "PEAR",
                "PEACH",
                "PLUM",
                "CHERRY",
                "LEMON",
                "LIME",
            ],
            "Birds": [
                "ROBIN",
                "EAGLE",
                "HAWK",
                "OWL",
                "CROW",
                "DUCK",
                "SWAN",
                "GOOSE",
                "FINCH",
                "WREN",
            ],
            # Medium themes
            "Classic Movies": [
                "CASABLANCA",
                "GODFATHER",
                "VERTIGO",
                "PSYCHO",
                "CITIZEN",
                "KANE",
                "JAWS",
            ],
            "Famous Authors": [
                "DICKENS",
                "TOLKIEN",
                "AUSTEN",
                "TWAIN",
                "HEMINGWAY",
                "CHRISTIE",
                "KING",
            ],
            "World Capitals": [
                "LONDON",
                "PARIS",
                "ROME",
                "TOKYO",
                "BERLIN",
                "MADRID",
                "MOSCOW",
                "CAIRO",
            ],
            "Card Games": [
                "POKER",
                "BRIDGE",
                "HEARTS",
                "SPADES",
                "RUMMY",
                "CANASTA",
                "EUCHRE",
                "WHIST",
            ],
            # Hard themes
            "Literature": [
                "METAPHOR",
                "ALLEGORY",
                "SONNET",
                "TRAGEDY",
                "COMEDY",
                "IRONY",
                "SATIRE",
            ],
            "Science": [
                "QUANTUM",
                "ELECTRON",
                "MOLECULE",
                "CATALYST",
                "ENTROPY",
                "FUSION",
                "GRAVITY",
            ],
            "Classical Music": [
                "SYMPHONY",
                "CONCERTO",
                "SONATA",
                "QUARTET",
                "ARIA",
                "OVERTURE",
                "FUGUE",
            ],
        }

        # Fill in any missing themes with generic words
        all_themes = self._generate_themes()
        for theme in all_themes:
            if theme not in theme_words:
                theme_words[theme] = []

        return theme_words

    def create_symmetric_pattern(self, difficulty="MEDIUM"):
        """Create symmetric black square pattern for crossword"""
        pattern = []

        if difficulty == "EASY":
            # Simpler pattern with fewer black squares
            pattern.extend([(0, 4), (0, 10), (4, 0), (4, 14)])
            pattern.extend([(10, 0), (10, 14), (14, 4), (14, 10)])
            pattern.extend([(2, 2), (2, 12), (12, 2), (12, 12)])
            pattern.extend([(5, 5), (5, 9), (9, 5), (9, 9)])
        elif difficulty == "HARD":
            # More complex pattern with more black squares
            pattern.extend([(0, 3), (0, 7), (0, 11), (3, 0), (3, 14)])
            pattern.extend([(7, 0), (7, 14), (11, 0), (11, 14)])
            pattern.extend([(14, 3), (14, 7), (14, 11)])
            pattern.extend([(2, 2), (2, 12), (12, 2), (12, 12)])
            pattern.extend([(4, 4), (4, 10), (10, 4), (10, 10)])
            pattern.extend([(6, 6), (6, 8), (8, 6), (8, 8)])
        else:  # MEDIUM (default)
            pattern.extend([(0, 3), (0, 11), (3, 0), (3, 14)])
            pattern.extend([(11, 0), (11, 14), (14, 3), (14, 11)])
            pattern.extend([(2, 2), (2, 12), (12, 2), (12, 12)])
            pattern.extend([(5, 5), (5, 9), (9, 5), (9, 9)])
            pattern.extend([(7, 7)])

        return pattern

    def generate_grid_with_content(self, puzzle_id, theme, difficulty):
        """Generate a filled 15x15 grid with actual words"""
        # Create empty grid
        grid = [[" " for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Apply black squares
        black_squares = self.create_symmetric_pattern(difficulty)
        for r, c in black_squares:
            grid[r][c] = "#"
            # Symmetric position
            grid[self.grid_size - 1 - r][self.grid_size - 1 - c] = "#"

        # Find all word slots (across and down)
        across_slots = []
        down_slots = []

        # Find across word slots
        for r in range(self.grid_size):
            c = 0
            while c < self.grid_size:
                if grid[r][c] == "#":
                    c += 1
                    continue

                start_c = c
                while c < self.grid_size and grid[r][c] != "#":
                    c += 1

                if c - start_c >= self.min_word_length:
                    across_slots.append((r, start_c, c - start_c))
                else:
                    c = start_c + 1

        # Find down word slots
        for c in range(self.grid_size):
            r = 0
            while r < self.grid_size:
                if grid[r][c] == "#":
                    r += 1
                    continue

                start_r = r
                while r < self.grid_size and grid[r][c] != "#":
                    r += 1

                if r - start_r >= self.min_word_length:
                    down_slots.append((start_r, c, r - start_r))
                else:
                    r = start_r + 1

        across_slots.sort(key=lambda x: -x[2])
        down_slots.sort(key=lambda x: -x[2])

        theme_word_list = self.theme_words.get(theme, [])

        filled_grid = self._fill_grid(grid, across_slots, down_slots, theme_word_list)

        if not filled_grid:
            logger.warning(
                f"Failed to fill grid for puzzle {puzzle_id}. Retrying with simpler pattern."
            )
            grid = [[" " for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            black_squares = self.create_symmetric_pattern("EASY")
            for r, c in black_squares:
                grid[r][c] = "#"
                grid[self.grid_size - 1 - r][self.grid_size - 1 - c] = "#"

            across_slots = []
            down_slots = []
            for r in range(self.grid_size):
                c = 0
                while c < self.grid_size:
                    if grid[r][c] == "#":
                        c += 1
                        continue
                    start_c = c
                    while c < self.grid_size and grid[r][c] != "#":
                        c += 1
                    if c - start_c >= self.min_word_length:
                        across_slots.append((r, start_c, c - start_c))
                    else:
                        c = start_c + 1
            for c in range(self.grid_size):
                r = 0
                while r < self.grid_size:
                    if grid[r][c] == "#":
                        r += 1
                        continue
                    start_r = r
                    while r < self.grid_size and grid[r][c] != "#":
                        r += 1
                    if r - start_r >= self.min_word_length:
                        down_slots.append((start_r, c, r - start_r))
                    else:
                        r = start_r + 1

            across_slots.sort(key=lambda x: -x[2])
            down_slots.sort(key=lambda x: -x[2])

            filled_grid = self._fill_grid(
                grid, across_slots, down_slots, theme_word_list
            )

        if not filled_grid:
            logger.error(
                f"Failed to generate valid grid for puzzle {puzzle_id} after retries."
            )
            filled_grid = self._create_fallback_grid()

        return filled_grid

    def _fill_grid(self, grid, across_slots, down_slots, theme_words):
        """Fill the grid with valid words using backtracking"""
        grid_copy = [row[:] for row in grid]
        all_slots = [(slot, "across") for slot in across_slots] + [
            (slot, "down") for slot in down_slots
        ]

        slot_intersections = {}
        for slot, direction in all_slots:
            intersections = 0
            if direction == "across":
                r, c, length = slot
                for i in range(length):
                    for other_slot, other_dir in all_slots:
                        if other_dir == "down":
                            other_r, other_c, other_len = other_slot
                            if other_c == c + i and other_r <= r < other_r + other_len:
                                intersections += 1
            else:
                r, c, length = slot
                for i in range(length):
                    for other_slot, other_dir in all_slots:
                        if other_dir == "across":
                            other_r, other_c, other_len = other_slot
                            if other_r == r + i and other_c <= c < other_c + other_len:
                                intersections += 1
            slot_intersections[(slot, direction)] = intersections

        all_slots.sort(key=lambda x: (-slot_intersections[x], -x[0][2]))

        used_words = set()
        theme_words_used = []
        for word in theme_words:
            if len(word) <= self.max_word_length and word in self.word_dict:
                for i, (slot, direction) in enumerate(all_slots):
                    if self._can_place_word(grid_copy, slot, direction, word):
                        self._place_word(grid_copy, slot, direction, word)
                        used_words.add(word)
                        theme_words_used.append((word, slot, direction))
                        all_slots.pop(i)
                        break

        for attempt in range(self.backtracking_max_attempts):
            success = self._backtrack_fill(grid_copy, all_slots, used_words)
            if success:
                return grid_copy

            grid_copy = [row[:] for row in grid]
            used_words = set(word for word, _, _ in theme_words_used)

            for word, slot, direction in theme_words_used:
                self._place_word(grid_copy, slot, direction, word)

        return None

    def _backtrack_fill(self, grid, slots, used_words, index=0):
        """Recursively fill the grid using backtracking"""
        if index >= len(slots):
            return True

        slot, direction = slots[index]
        r, c, length = slot

        constraints = self._get_constraints(grid, slot, direction)
        valid_words = self._find_valid_words(constraints, length, used_words)

        for word in valid_words:
            self._place_word(grid, slot, direction, word)
            used_words.add(word)

            if self._backtrack_fill(grid, slots, used_words, index + 1):
                return True

            used_words.remove(word)
            self._remove_word(grid, slot, direction)

        return False

    def _get_constraints(self, grid, slot, direction):
        """Get constraints for a word slot"""
        constraints = {}
        r, c, length = slot

        if direction == "across":
            for i in range(length):
                if grid[r][c + i] != " ":
                    constraints[i] = grid[r][c + i]
        else:
            for i in range(length):
                if grid[r + i][c] != " ":
                    constraints[i] = grid[r + i][c]

        return constraints

    def _find_valid_words(self, constraints, length, used_words):
        """Find valid words matching constraints"""
        valid_words = []

        for word in self.word_dict:
            if len(word) == length and word not in used_words:
                matches = True
                for pos, letter in constraints.items():
                    if word[pos] != letter:
                        matches = False
                        break
                if matches:
                    valid_words.append(word)

        random.shuffle(valid_words)
        return valid_words

    def _can_place_word(self, grid, slot, direction, word):
        """Check if a word can be placed at the given slot"""
        r, c, length = slot
        if len(word) != length:
            return False

        if direction == "across":
            for i in range(length):
                if grid[r][c + i] != " " and grid[r][c + i] != word[i]:
                    return False
        else:
            for i in range(length):
                if grid[r + i][c] != " " and grid[r + i][c] != word[i]:
                    return False

        return True

    def _place_word(self, grid, slot, direction, word):
        """Place a word on the grid"""
        r, c, length = slot
        if direction == "across":
            for i in range(length):
                grid[r][c + i] = word[i]
        else:
            for i in range(length):
                grid[r + i][c] = word[i]

    def _remove_word(self, grid, slot, direction):
        """Remove a word from the grid, preserving intersections"""
        r, c, length = slot
        temp_grid = [
            [False for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]

        if direction == "across":
            for i in range(length):
                temp_grid[r][c + i] = True
        else:
            for i in range(length):
                temp_grid[r + i][c] = True

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if temp_grid[i][j]:
                    is_intersection = False
                    if direction == "across":
                        if (i > 0 and grid[i - 1][j] not in (" ", "#")) or (
                            i < self.grid_size - 1 and grid[i + 1][j] not in (" ", "#")
                        ):
                            is_intersection = True
                    else:
                        if (j > 0 and grid[i][j - 1] not in (" ", "#")) or (
                            j < self.grid_size - 1 and grid[i][j + 1] not in (" ", "#")
                        ):
                            is_intersection = True

                    if not is_intersection:
                        grid[i][j] = " "

    def _create_fallback_grid(self):
        """Create a simple grid with predefined words as a last resort"""
        grid = [[" " for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for i in range(0, self.grid_size, 4):
            for j in range(0, self.grid_size, 4):
                grid[i][j] = "#"
                grid[self.grid_size - 1 - i][self.grid_size - 1 - j] = "#"

        words_across = ["PUZZLE", "CROSS", "WORD", "GAME", "PLAY", "FUN", "SOLVE"]
        words_down = ["PENCIL", "CLUE", "GRID", "BOX", "WIN", "TRY", "MIND"]

        row = 1
        for word in words_across:
            if row >= self.grid_size:
                break
            col = 1
            for c in word:
                if col >= self.grid_size:
                    break
                grid[row][col] = c
                col += 1
            row += 2

        col = 1
        for word in words_down:
            if col >= self.grid_size:
                break
            row = 1
            for c in word:
                if row >= self.grid_size:
                    break
                grid[row][col] = c
                row += 1
            col += 2

        return grid

    def create_grid_images(self, grid, puzzle_id):
        """Create high-quality grid images for puzzle and solution"""
        # Load style settings from config
        cell_size = config.get("style_settings.images.grid_cell_size_px", 60)
        margin = config.get("style_settings.images.grid_margin_px", 40)
        border_width = config.get("style_settings.images.grid_border_width_px", 2)
        grid_line_color = config.get("style_settings.colors.grid_line_color", "black")
        black_square_color = config.get(
            "style_settings.colors.black_square_color", "black"
        )
        text_color = config.get("style_settings.colors.text_color", "black")

        img_size = self.grid_size * cell_size + 2 * margin

        empty_img = Image.new("RGB", (img_size, img_size), "white")
        empty_draw = ImageDraw.Draw(empty_img)
        filled_img = Image.new("RGB", (img_size, img_size), "white")
        filled_draw = ImageDraw.Draw(filled_img)

        # Load fonts from config paths
        font_paths = config.get("style_settings.fonts.grid_font_paths", [])
        letter_font_size = config.get("style_settings.fonts.font_sizes.grid_letter", 36)
        number_font_size = config.get("style_settings.fonts.font_sizes.grid_number", 20)

        font, number_font = None, None
        for path in font_paths:
            try:
                if Path(path).exists():
                    font = ImageFont.truetype(path, letter_font_size)
                    number_font = ImageFont.truetype(path, number_font_size)
                    break
            except Exception:
                continue
        if not font:
            logger.warning("No valid font found in config paths. Using default font.")
            font = ImageFont.load_default()
            number_font = font

        number = 1
        clue_positions = {}

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = margin + col * cell_size
                y = margin + row * cell_size

                if grid[row][col] == "#":
                    empty_draw.rectangle(
                        [x, y, x + cell_size, y + cell_size], fill=black_square_color
                    )
                    filled_draw.rectangle(
                        [x, y, x + cell_size, y + cell_size], fill=black_square_color
                    )
                else:
                    empty_draw.rectangle(
                        [x, y, x + cell_size, y + cell_size],
                        outline=grid_line_color,
                        width=border_width,
                    )
                    filled_draw.rectangle(
                        [x, y, x + cell_size, y + cell_size],
                        outline=grid_line_color,
                        width=border_width,
                    )

                    letter = grid[row][col]
                    text_width, text_height = filled_draw.textsize(letter, font=font)
                    filled_draw.text(
                        (
                            x + (cell_size - text_width) / 2,
                            y + (cell_size - text_height) / 2,
                        ),
                        letter,
                        font=font,
                        fill=text_color,
                    )

                    needs_number = False
                    if (
                        (col == 0 or grid[row][col - 1] == "#")
                        and col < self.grid_size - 1
                        and grid[row][col + 1] != "#"
                    ):
                        needs_number = True
                    if (
                        (row == 0 or grid[row - 1][col] == "#")
                        and row < self.grid_size - 1
                        and grid[row + 1][col] != "#"
                    ):
                        needs_number = True

                    if needs_number:
                        empty_draw.text(
                            (x + 5, y + 5),
                            str(number),
                            font=number_font,
                            fill=text_color,
                        )
                        filled_draw.text(
                            (x + 5, y + 5),
                            str(number),
                            font=number_font,
                            fill=text_color,
                        )
                        clue_positions[(row, col)] = number
                        number += 1

        empty_img_path = self.puzzles_dir / f"puzzle_{puzzle_id:02d}.png"
        empty_img.save(empty_img_path, "PNG")

        filled_img_path = self.solutions_dir / f"solution_{puzzle_id:02d}.png"
        filled_img.save(filled_img_path, "PNG")

        return empty_img_path, filled_img_path, clue_positions

    def extract_words_from_grid(self, grid, clue_positions):
        """Extract words and their positions from the filled grid"""
        across_words = []
        down_words = []

        for row in range(self.grid_size):
            col = 0
            while col < self.grid_size:
                if grid[row][col] == "#":
                    col += 1
                    continue

                if col == 0 or grid[row][col - 1] == "#":
                    start_col = col
                    word = ""
                    while col < self.grid_size and grid[row][col] != "#":
                        word += grid[row][col]
                        col += 1

                    if len(word) >= self.min_word_length:
                        number = clue_positions.get((row, start_col))
                        if number:
                            across_words.append((number, word, (row, start_col)))
                else:
                    col += 1

        for col in range(self.grid_size):
            row = 0
            while row < self.grid_size:
                if grid[row][col] == "#":
                    row += 1
                    continue

                if row == 0 or grid[row - 1][col] == "#":
                    start_row = row
                    word = ""
                    while row < self.grid_size and grid[row][col] != "#":
                        word += grid[row][col]
                        row += 1

                    if len(word) >= self.min_word_length:
                        number = clue_positions.get((start_row, col))
                        if number:
                            down_words.append((number, word, (start_row, col)))
                else:
                    row += 1

        across_words.sort(key=lambda x: x[0])
        down_words.sort(key=lambda x: x[0])

        return across_words, down_words

    def generate_clues(self, puzzle_id, theme, difficulty, across_words, down_words):
        """Generate appropriate clues based on words and difficulty"""
        common_clues = {
            "ACE": ["High card", "Tennis winner", "Top pilot"],
            "AIR": ["What we breathe", "Radio broadcast", "Tune"],
            "ALL": ["Everything", "The whole amount", "Entirely"],
            "AND": ["Plus", "Also", "In addition"],
            "ART": ["Gallery display", "Creative work", "Painting or sculpture"],
            "BAG": ["Shopping carrier", "Sack", "Luggage piece"],
            "BOX": ["Container", "Square shape", "Package"],
            "CAR": ["Vehicle", "Automobile", "Driving machine"],
            "CAT": ["Feline pet", "Meowing animal", "Lion's cousin"],
            "DOG": ["Canine pet", "Barking animal", "Wolf's cousin"],
            "EAR": ["Hearing organ", "Side of the head", "What catches sound"],
            "EAT": ["Consume food", "Have a meal", "Dine"],
            "EGG": ["Breakfast staple", "Oval food", "Chicken product"],
            "EYE": ["Seeing organ", "Vision part", "Pupil's place"],
            "FAN": ["Cooling device", "Sports enthusiast", "Admirer"],
            "ABLE": ["Capable", "Having skill", "Competent"],
            "AREA": ["Region", "Space", "Section"],
            "BALL": ["Round toy", "Sports object", "Sphere"],
            "BLUE": ["Sky color", "Sad feeling", "Ocean hue"],
            "BOOK": ["Reading material", "Bound pages", "Literary work"],
            "CARD": ["Greeting paper", "Playing piece", "ID document"],
            "DOOR": ["Entry point", "Room divider", "Swinging barrier"],
            "FACE": ["Front of head", "Visage", "Expression"],
            "GAME": ["Play activity", "Sport contest", "Competition"],
            "HAND": ["End of arm", "Palm and fingers", "Clock pointer"],
            "APPLE": ["Red or green fruit", "iPhone maker", "Teacher's gift"],
            "BEACH": ["Sandy shore", "Ocean's edge", "Coastal area"],
            "CHAIR": ["Sitting furniture", "Desk companion", "Seat"],
            "DANCE": ["Rhythmic movement", "Ballroom activity", "Party activity"],
            "EARTH": ["Our planet", "Soil", "Ground"],
            "FLOWER": ["Bloom", "Garden plant", "Petal bearer"],
            "GARDEN": ["Plant area", "Growing space", "Flower bed"],
            "HOUSE": ["Home", "Dwelling", "Residence"],
            "ISLAND": ["Land surrounded by water", "Tropical getaway", "Isolated area"],
            "JACKET": ["Coat", "Outerwear", "Covering"],
            "KITCHEN": ["Cooking room", "Food preparation area", "Chef's domain"],
            "LETTER": ["Written message", "Alphabet unit", "Mail piece"],
            "MARKET": ["Shopping place", "Store", "Trading venue"],
            "NUMBER": ["Counting unit", "Digit", "Quantity"],
            "ORANGE": [
                "Citrus fruit",
                "Color between red and yellow",
                "Tangerine relative",
            ],
            "PENCIL": ["Writing tool", "Drawing implement", "Graphite stick"],
            "PUZZLE": ["Brain teaser", "Jigsaw challenge", "Mental game"],
            "RIVER": ["Flowing water", "Stream", "Waterway"],
            "SCHOOL": ["Learning place", "Education building", "Student's destination"],
            "TABLE": ["Flat surface furniture", "Dining platform", "Desk"],
            "WINDOW": ["Glass opening", "View frame", "Wall aperture"],
            "WINTER": ["Cold season", "Snow time", "December to March"],
            "CROSSWORD": ["Word puzzle", "Grid challenge", "Intersecting words game"],
            "SOLUTION": ["Answer", "Resolution", "Puzzle completion"],
            "CHALLENGE": ["Difficult task", "Test of ability", "Contest"],
            "KNOWLEDGE": ["Information", "Learning", "Understanding"],
            "QUESTION": ["Inquiry", "Query", "Problem to solve"],
        }

        clues = {"across": [], "down": []}

        for number, word, _ in across_words:
            if word in common_clues:
                clue_options = common_clues[word]
                clue_index = 0
                if difficulty == "MEDIUM":
                    clue_index = min(1, len(clue_options) - 1)
                elif difficulty == "HARD":
                    clue_index = min(2, len(clue_options) - 1)
                clue = clue_options[clue_index]
            else:
                if word.endswith("ING"):
                    clue = f"Action of {word[:-3].lower()}"
                elif word.endswith("ER"):
                    clue = f"One who {word[:-2].lower()}s"
                elif word.endswith("LY"):
                    clue = f"In a {word[:-2].lower()} manner"
                else:
                    clue = f"Related to {word.lower()}"
            clues["across"].append((number, clue, word))

        for number, word, _ in down_words:
            if word in common_clues:
                clue_options = common_clues[word]
                clue_index = 0
                if difficulty == "MEDIUM":
                    clue_index = min(1, len(clue_options) - 1)
                elif difficulty == "HARD":
                    clue_index = min(2, len(clue_options) - 1)
                clue = clue_options[clue_index]
            else:
                if word.endswith("ING"):
                    clue = f"Action of {word[:-3].lower()}"
                elif word.endswith("ER"):
                    clue = f"One who {word[:-2].lower()}s"
                elif word.endswith("LY"):
                    clue = f"In a {word[:-2].lower()} manner"
                else:
                    clue = f"Related to {word.lower()}"
            clues["down"].append((number, clue, word))

        return clues

    def validate_puzzle(self, grid, across_words, down_words, clues):
        """Validate that the puzzle meets quality standards"""
        validation = {"valid": True, "issues": []}
        min_word_count = config.get_qa_threshold("min_word_count_per_puzzle") or 20
        balance_ratio = config.get_qa_threshold("word_balance_ratio") or 0.3

        total_words = len(across_words) + len(down_words)
        if total_words < min_word_count:
            validation["valid"] = False
            validation["issues"].append(
                f"Too few words: {total_words} (min {min_word_count})"
            )

        if total_words > 0 and (
            len(across_words) < total_words * balance_ratio
            or len(down_words) < total_words * balance_ratio
        ):
            validation["valid"] = False
            validation["issues"].append("Unbalanced word distribution")

        all_words = [word for _, word, _ in across_words + down_words]
        duplicates = [word for word, count in Counter(all_words).items() if count > 1]
        if duplicates:
            validation["valid"] = False
            validation["issues"].append(f"Duplicate words: {', '.join(duplicates)}")

        short_words = [
            word
            for _, word, _ in across_words + down_words
            if len(word) < self.min_word_length
        ]
        if short_words:
            validation["valid"] = False
            validation["issues"].append(
                f"Found words shorter than min length {self.min_word_length}"
            )

        if not self._check_grid_connectivity(grid):
            validation["valid"] = False
            validation["issues"].append("Grid has isolated sections")

        for direction in ["across", "down"]:
            for number, clue, answer in clues[direction]:
                found = False
                word_list = across_words if direction == "across" else down_words
                for num, word, _ in word_list:
                    if num == number and word == answer:
                        found = True
                        break
                if not found:
                    validation["valid"] = False
                    validation["issues"].append(f"Clue mismatch: {direction} {number}")

        return validation

    def _check_grid_connectivity(self, grid):
        """Check that the grid has no isolated sections"""
        start_r, start_c = None, None
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if grid[r][c] != "#":
                    start_r, start_c = r, c
                    break
            if start_r is not None:
                break

        if start_r is None:
            return False

        visited = [
            [False for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]
        self._flood_fill(grid, visited, start_r, start_c)

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if grid[r][c] != "#" and not visited[r][c]:
                    return False

        return True

    def _flood_fill(self, grid, visited, r, c):
        """Flood fill algorithm to mark connected squares"""
        if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
            return
        if grid[r][c] == "#" or visited[r][c]:
            return

        visited[r][c] = True
        self._flood_fill(grid, visited, r + 1, c)
        self._flood_fill(grid, visited, r - 1, c)
        self._flood_fill(grid, visited, r, c + 1)
        self._flood_fill(grid, visited, r, c - 1)

    def generate_puzzles(self):
        """Generate the specified number of crossword puzzles"""
        print(f"🔤 CROSSWORD ENGINE V3 - Generating {self.puzzle_count} puzzles")
        print(f"📁 Output directory: {self.puzzles_dir}")

        puzzles_data = []
        themes = self._generate_themes()

        for i in range(self.puzzle_count):
            puzzle_id = i + 1
            difficulty = self._get_difficulty_for_puzzle(puzzle_id)
            theme = themes[i % len(themes)]

            print(
                f"  Creating puzzle {puzzle_id}/{self.puzzle_count}: {theme} ({difficulty})"
            )

            grid = self.generate_grid_with_content(puzzle_id, theme, difficulty)
            empty_grid_path, filled_grid_path, clue_positions = self.create_grid_images(
                grid, puzzle_id
            )
            across_words, down_words = self.extract_words_from_grid(
                grid, clue_positions
            )
            clues = self.generate_clues(
                puzzle_id, theme, difficulty, across_words, down_words
            )
            validation = self.validate_puzzle(grid, across_words, down_words, clues)

            if not validation["valid"]:
                logger.warning(
                    f"Puzzle {puzzle_id} has issues: {validation['issues']}. Trying to regenerate."
                )
                attempts = 0
                while (
                    not validation["valid"]
                    and attempts < self.backtracking_max_attempts
                ):
                    attempts += 1
                    grid = self.generate_grid_with_content(puzzle_id, theme, difficulty)
                    empty_grid_path, filled_grid_path, clue_positions = (
                        self.create_grid_images(grid, puzzle_id)
                    )
                    across_words, down_words = self.extract_words_from_grid(
                        grid, clue_positions
                    )
                    clues = self.generate_clues(
                        puzzle_id, theme, difficulty, across_words, down_words
                    )
                    validation = self.validate_puzzle(
                        grid, across_words, down_words, clues
                    )
                if not validation["valid"]:
                    logger.error(
                        f"Could not generate valid puzzle {puzzle_id} after {attempts} attempts."
                    )

            puzzle_data = {
                "id": puzzle_id,
                "theme": theme,
                "difficulty": difficulty,
                "grid_path": str(empty_grid_path),
                "solution_path": str(filled_grid_path),
                "clues": clues,
                "word_count": {
                    "across": len(across_words),
                    "down": len(down_words),
                    "total": len(across_words) + len(down_words),
                },
                "validation": {
                    "valid": validation["valid"],
                    "issues": validation["issues"] if not validation["valid"] else [],
                },
                "clue_positions": {
                    f"{r},{c}": num for (r, c), num in clue_positions.items()
                },
            }

            puzzle_meta_path = self.metadata_dir / f"puzzle_{puzzle_id:02d}.json"
            with open(puzzle_meta_path, "w") as f:
                json.dump(puzzle_data, f, indent=2)

            puzzles_data.append(puzzle_data)
            time.sleep(0.1)

        collection_meta = {
            "puzzle_count": self.puzzle_count,
            "difficulty_mode": self.difficulty_mode,
            "grid_size": self.grid_size,
            "generation_date": datetime.now().isoformat(),
            "puzzles": [p["id"] for p in puzzles_data],
            "validation_summary": {
                "valid_puzzles": sum(
                    1 for p in puzzles_data if p["validation"]["valid"]
                ),
                "invalid_puzzles": sum(
                    1 for p in puzzles_data if not p["validation"]["valid"]
                ),
            },
        }

        with open(self.metadata_dir / "collection.json", "w") as f:
            json.dump(collection_meta, f, indent=2)

        print(f"✅ Generated {self.puzzle_count} crossword puzzles")
        valid_count = collection_meta["validation_summary"]["valid_puzzles"]
        print(f"✓ Valid puzzles: {valid_count}/{self.puzzle_count}")
        if valid_count < self.puzzle_count:
            print(f"⚠️ {self.puzzle_count - valid_count} puzzles have validation issues")

        return puzzles_data

    def _generate_themes(self):
        """Generate themes based on difficulty mode"""
        themes = [
            "Garden Flowers",
            "Kitchen Tools",
            "Family Time",
            "Weather",
            "Colors",
            "Fruits",
            "Birds",
            "Pets",
            "Seasons",
            "Numbers",
            "Body Parts",
            "Clothing",
            "Breakfast",
            "Rooms",
            "Tools",
            "Trees",
            "Ocean",
            "Farm",
            "Music",
            "Sports",
            "Classic Movies",
            "Famous Authors",
            "World Capitals",
            "Cooking",
            "Card Games",
            "Dance",
            "Gems",
            "Desserts",
            "Travel",
            "Hobbies",
            "Classic Songs",
            "Wine",
            "Antiques",
            "Board Games",
            "Art",
            "Opera",
            "Cars",
            "Radio Shows",
            "History",
            "Architecture",
            "Literature",
            "Science",
            "Geography",
            "Classical Music",
            "Art History",
            "Cuisine",
            "Philosophy",
            "Astronomy",
            "Medicine",
            "Technology",
        ]
        if len(themes) < self.puzzle_count:
            themes = themes * (self.puzzle_count // len(themes) + 1)
        if self.difficulty_mode.lower() == "mixed":
            random.shuffle(themes)
        return themes[: self.puzzle_count]

    def _get_difficulty_for_puzzle(self, puzzle_id):
        """Determine difficulty for a puzzle based on mode and ID"""
        mode = self.difficulty_mode.lower()
        if mode in ["easy", "medium", "hard"]:
            return mode.upper()

        easy_ratio = self.difficulty_distribution.get("easy_ratio", 0.4)
        medium_ratio = self.difficulty_distribution.get("medium_ratio", 0.4)

        if puzzle_id <= int(self.puzzle_count * easy_ratio):
            return "EASY"
        elif puzzle_id <= int(self.puzzle_count * (easy_ratio + medium_ratio)):
            return "MEDIUM"
        else:
            return "HARD"


def main():
    """Main entry point for crossword engine"""
    parser = argparse.ArgumentParser(
        description="Crossword Engine v3 Fixed - Generate high-quality crossword puzzles"
    )
    parser.add_argument("--output", required=True, help="Output directory for puzzles")
    parser.add_argument(
        "--count",
        type=int,
        default=config.get("puzzle_generation.default_puzzle_count", 50),
        help="Number of puzzles to generate",
    )
    parser.add_argument(
        "--difficulty",
        default="mixed",
        choices=["easy", "medium", "hard", "mixed"],
        help="Difficulty level for puzzles",
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=config.get_puzzle_setting("crossword", "grid_size", 15),
        help="Grid size (default: 15x15)",
    )
    parser.add_argument(
        "--max-word-length",
        type=int,
        default=config.get_puzzle_setting("crossword", "max_word_length", 15),
        help="Maximum word length",
    )
    parser.add_argument(
        "--word-list",
        default=config.get_path("file_paths.word_list_path"),
        help="Path to custom word list file",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Logging level",
    )

    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level.upper()))

    try:
        start_time = time.time()
        engine = CrosswordEngineV3(
            output_dir=args.output,
            puzzle_count=args.count,
            difficulty=args.difficulty,
            grid_size=args.grid_size,
            max_word_length=args.max_word_length,
            word_list_path=args.word_list,
        )
        puzzles = engine.generate_puzzles()
        elapsed_time = time.time() - start_time

        print(f"\n🎯 CROSSWORD ENGINE V3 - SUCCESS")
        print(f"📊 Generated {len(puzzles)} puzzles")
        print(f"⏱️ Time taken: {elapsed_time:.2f} seconds")
        print(f"📁 Output directory: {args.output}")

        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
