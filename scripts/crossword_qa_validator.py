#!/usr/bin/env python3
"""
Crossword-Specific QA Validator
Complete redesign focusing on puzzle validity, not PDF structure
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import PyPDF2


@dataclass
class PuzzleData:
    """Domain model for crossword puzzle"""

    number: int
    grid: List[List[str]]
    across_clues: Dict[int, str]
    down_clues: Dict[int, str]
    solution: List[List[str]]


@dataclass
class ValidationResult:
    """Detailed validation result"""

    passed: bool
    score: int
    category: str
    message: str
    details: Optional[Dict] = None


class CrosswordQAValidator:
    """Complete QA system for crossword puzzles"""

    def __init__(self):
        # Load English dictionary
        self.valid_words = self._load_dictionary()

        # Validation thresholds
        self.MIN_DOWN_CLUE_RATIO = 0.35  # At least 35% of clues should be DOWN
        self.MAX_DOWN_CLUE_RATIO = 0.65  # At most 65% of clues should be DOWN
        self.MIN_WORD_LENGTH = 3
        self.MAX_BLACK_SQUARE_RATIO = 0.25  # Max 25% black squares
        self.MIN_PUZZLE_COUNT = 50
        self.REQUIRED_PAGE_COUNT = 156

        # Scoring weights
        self.WEIGHTS = {
            "structure": 20,  # Grid pattern validity
            "words": 25,  # Real word validation
            "clues": 20,  # Clue balance and quality
            "solutions": 25,  # Solution accuracy
            "consistency": 10,  # Internal consistency
        }

    def _load_dictionary(self) -> Set[str]:
        """Load valid English words"""
        # Common words for crossword puzzles
        common_words = {
            # 3-letter words
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
            "HAD",
            "HAS",
            "HIS",
            "HOW",
            "ITS",
            "MAY",
            "NEW",
            "NOW",
            "OLD",
            "SEE",
            "TWO",
            "WAY",
            "WHO",
            "OIL",
            "USE",
            "CAT",
            "DOG",
            "MAN",
            "CAR",
            "EAT",
            "FAR",
            "FUN",
            "GET",
            "GOT",
            "LET",
            "PUT",
            "RAN",
            "RED",
            "RUN",
            "SIT",
            "TEN",
            "TOP",
            "TOO",
            "WIN",
            "YES",
            "AGE",
            "AGO",
            "AIR",
            "ARM",
            "ART",
            "ASK",
            "BAD",
            "BAG",
            "BAR",
            "BED",
            "BIG",
            "BOX",
            "BOY",
            "BUS",
            "BUY",
            "CUP",
            "CUT",
            "DAD",
            "DID",
            "DIE",
            "EAR",
            "END",
            "EYE",
            "FEW",
            "FLY",
            "GOD",
            "GUN",
            "GUY",
            "HIT",
            "HOT",
            "JOB",
            "LAW",
            "LAY",
            "LEG",
            "LIE",
            "LOT",
            "LOW",
            "MAD",
            "MAP",
            "MOM",
            "PAY",
            "SAW",
            "SAY",
            "SET",
            "SHE",
            "SIX",
            "SON",
            "SUN",
            "TAX",
            "TEA",
            "TRY",
            "VAN",
            "WAR",
            "WET",
            "WHY",
            "WON",
            "YET",
            "ZOO",
            "ACE",
            "ACT",
            "ADD",
            "AID",
            "AIM",
            "ANT",
            "ANY",
            "APE",
            "ATE",
            "BAT",
            "BEE",
            "BET",
            "BIT",
            "BOW",
            "BOY",
            "BUD",
            "BUG",
            "BUM",
            "BUN",
            "BUS",
            "CAB",
            "CAM",
            # 4-letter words
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
            "AGED",
            "ALSO",
            "AREA",
            "ARMY",
            "AWAY",
            "BABY",
            "BASE",
            "BEAR",
            "BEAT",
            "BEEN",
            "BEST",
            "BILL",
            "BIRD",
            "BLUE",
            "BOAT",
            "BODY",
            "BOOK",
            "BORN",
            "BOTH",
            "BOWL",
            "BOYS",
            "BUSY",
            "CAKE",
            "CALM",
            "CARD",
            "CARE",
            "CARS",
            "CASE",
            "CASH",
            "CAST",
            "CELL",
            "CITY",
            "CLUB",
            "COAL",
            "COAT",
            "COLD",
            "COPY",
            "CORE",
            "COST",
            "CREW",
            "DARK",
            "DATA",
            "DATE",
            "DAYS",
            "DEAD",
            "DEAL",
            "DEAR",
            "DEEP",
            "DIET",
            "DOOR",
            "DOWN",
            "DRAW",
            "DREW",
            "DROP",
            "DRUG",
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
            "EYES",
            "FACE",
            "FACT",
            "FAIL",
            "FAIR",
            "FALL",
            "FARM",
            "FAST",
            "FEAR",
            "FEED",
            "FEEL",
            "FEET",
            "FELL",
            "FELT",
            "FILE",
            "FILL",
            "FILM",
            "FINE",
            "FIRE",
            "FIRM",
            "FISH",
            "FIVE",
            "FLAT",
            "FLOW",
            "FOOD",
            "FOOT",
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
            "GIFT",
            "GIRL",
            "GIVE",
            "GLAD",
            "GOAL",
            "GOES",
            "GOLD",
            "GONE",
            "GOOD",
            "GRAY",
            "GREW",
            "GROW",
            "GULF",
            "GUNS",
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
            "JOBS",
            "JOHN",
            "JOIN",
            "JUMP",
            "JURY",
            "JUST",
            "KEEP",
            "KEPT",
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
            "LEND",
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
            "LONG",
            "LOOK",
            "LORD",
            "LOSE",
            "LOSS",
            "LOST",
            "LOTS",
            "LOUD",
            "LOVE",
            "LUCK",
            "MADE",
            "MAIL",
            "MAIN",
            "MAKE",
            "MALE",
            "MALL",
            "MANY",
            "MARK",
            "MASS",
            "MATE",
            "MEAL",
            "MEAN",
            "MEAT",
            "MEET",
            "MENU",
            "MERE",
            "MIKE",
            "MILE",
            "MILK",
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
            "NINE",
            "NONE",
            "NOON",
            "NORM",
            "NOSE",
            "NOTE",
            "OKAY",
            "ONCE",
            "ONES",
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
            "PALE",
            "PALM",
            "PARK",
            "PART",
            "PASS",
            "PAST",
            "PATH",
            "PAUL",
            "PEAK",
            "PICK",
            "PILE",
            "PINE",
            "PINK",
            "PIPE",
            "PLAN",
            "PLAY",
            "PLOT",
            "PLUS",
            "POEM",
            "POET",
            "POLL",
            "POOL",
            "POOR",
            "PORT",
            "POST",
            "POUR",
            "PREY",
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
            "RODE",
            "ROLE",
            "ROLL",
            "ROOF",
            "ROOM",
            "ROOT",
            "ROPE",
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
            "SILK",
            "SING",
            "SINK",
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
            "TEEN",
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
            "TIDE",
            "TIED",
            "TIES",
            "TIME",
            "TINY",
            "TIRE",
            "TOLD",
            "TOLL",
            "TONE",
            "TONY",
            "TOOK",
            "TOOL",
            "TOPS",
            "TORE",
            "TORN",
            "TOUR",
            "TOWN",
            "TOYS",
            "TREE",
            "TRIM",
            "TRIP",
            "TRUE",
            "TUBE",
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
            "WARN",
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
            "WINS",
            "WIRE",
            "WISE",
            "WISH",
            "WITH",
            "WOOD",
            "WORD",
            "WORE",
            "WORK",
            "WORN",
            "YARD",
            "YEAH",
            "YEAR",
            "YOUR",
            "ZERO",
            "ZONE",
            # 5-letter words
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
            "HOUSE",
            "FOUND",
            "GOING",
            "EVERY",
            "UNDER",
            "NEVER",
            "PLACE",
            "THINK",
            "WHILE",
            "GREAT",
            "AGAIN",
            "BEFORE",
            "SMALL",
            "THROUGH",
            "TURNED",
            "INTEREST",
            "LARGE",
            "ALONG",
            "AMONG",
            "ASKED",
            "BEHIND",
            "BETTER",
            "BLACK",
            "BRING",
            "BUILD",
            "CARRY",
            "CLEAN",
            "CLOSE",
            "COMES",
            "COURT",
            "DIDN'T",
            "EARLY",
            "FIELD",
            "FINAL",
            "FORCE",
            "FRONT",
            "GIVEN",
            "GREEN",
            "HANDS",
            "HEART",
            "HEAVY",
            "HUMAN",
            "LEAVE",
            "LEVEL",
            "LIGHT",
            "LOCAL",
            "MEANS",
            "MIGHT",
            "MONEY",
            "MONTH",
            "MUSIC",
            "NIGHT",
            "NORTH",
            "OFTEN",
            "ORDER",
            "PAPER",
            "PARTY",
            "PEACE",
            "PEOPLE",
            "PERHAPS",
            "PERSON",
            "PIECE",
            "POINT",
            "POWER",
            "QUITE",
            "REACH",
            "RIGHT",
            "RIVER",
            "ROUND",
            "SEEMS",
            "SENSE",
            "SHALL",
            "SHORT",
            "SHOWN",
            "SINCE",
            "SOUTH",
            "SPACE",
            "SPEAK",
            "SPENT",
            "STAFF",
            "STAGE",
            "START",
            "STATE",
            "STOOD",
            "STORY",
            "STUDY",
            "TAKEN",
            "THANK",
            "THIRD",
            "THOSE",
            "THOUGH",
            "TODAY",
            "TRADE",
            "TRIED",
            "TRYING",
            "TURNED",
            "UNTIL",
            "USING",
            "VALUE",
            "VOICE",
            "WATER",
            "WEEKS",
            "WHERE",
            "WHICH",
            "WHILE",
            "WHITE",
            "WHOLE",
            "WHOSE",
            "WOMAN",
            "WOMEN",
            "WORKS",
            "WORTH",
            "WOULD",
            "WRITE",
            "WRONG",
            "YEARS",
            "YOUNG",
            "ABOVE",
            "ADDED",
            "ADMIT",
            "ADULT",
            "AFTER",
            "AGENT",
            "AGREE",
            "AHEAD",
            "ALIVE",
            "ALLOW",
            "ALONE",
            "ALREADY",
            "ALTHOUGH",
            "ALWAYS",
            "AMONG",
            "ANGER",
            "ANGLE",
            "ANGRY",
            "APART",
            "APPLE",
            "APPLY",
            "AREAS",
            "ARGUE",
            "ARISE",
            "ARMED",
            "ASIDE",
            "ASKED",
            "AVOID",
            "AWARE",
            "BADLY",
            "BAKER",
            "BASED",
            "BASIC",
            "BEACH",
            "BEGAN",
            "BEGIN",
            "BEING",
            "BELOW",
            "BENCH",
            "BILLY",
            "BIRTH",
            "BLOCK",
            "BLOOD",
            "BOARD",
            "BOOKS",
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
            "BUYER",
            "CABLE",
            "CALIF",
            "CALLS",
            "CARRY",
            "CASES",
            "CATCH",
            "CAUSE",
            "CHAIN",
            "CHAIR",
            "CHAOS",
            "CHARM",
            "CHART",
            "CHASE",
            "CHEAP",
            "CHECK",
            "CHEST",
            "CHIEF",
            "CHILD",
            "CHINA",
            "CHOSE",
            "CHRIS",
            "CIVIL",
            "CLAIM",
            "CLASS",
            "CLEAN",
            "CLEAR",
            "CLICK",
            "CLIMB",
            "CLOCK",
            "CLOSE",
            "CLOUD",
            "COACH",
            "COAST",
            "COLON",
            "COLOR",
            "COMIC",
            "COUGH",
            "COULD",
            "COUNT",
            "COUPLE",
            "COURSE",
            "COURT",
            "COVER",
            "CRACK",
            "CRAFT",
            "CRASH",
            "CRAZY",
            "CREAM",
            "CRIME",
            "CROSS",
            "CROWD",
            "CROWN",
            "CRUDE",
            "CURVE",
            "CYCLE",
            "DAILY",
            "DANCE",
            "DATED",
            "DEALT",
            "DEATH",
            "DEBUT",
            "DELAY",
            "DELTA",
            "DENSE",
            "DEPOT",
            "DEPTH",
            "DERBY",
            "DIGIT",
            "DIRTY",
            "DOESN",
            "DOING",
            "DOUBT",
            "DOZEN",
            "DRAFT",
            "DRAIN",
            "DRAMA",
            "DRANK",
            "DRAWN",
            "DREAM",
            "DRESS",
            "DRIED",
            "DRILL",
            "DRINK",
            "DRIVE",
            "DROVE",
            "DYING",
            "EAGER",
            "EARLY",
            "EARTH",
            "EIGHT",
            "EIGHT",
            "EITHER",
            "ELDER",
            "ELECT",
            "ELITE",
            "EMPTY",
            "ENEMY",
            "ENJOY",
            "ENTER",
            "ENTRY",
            "EQUAL",
            "ERROR",
            "ETHAN",
            "ETHICS",
            "EVANS",
            "EVENT",
            "EVERY",
            "EXACT",
            "EXIST",
            "EXTRA",
            "FACED",
            "FACES",
            "FACTS",
            "FAITH",
            "FALLS",
            "FALSE",
            "FAMED",
            "FANCY",
            # 6-letter words
            "BEFORE",
            "SHOULD",
            "PEOPLE",
            "THROUGH",
            "AROUND",
            "ANOTHER",
            "BETWEEN",
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
            "IMPORTANT",
            "CHILDREN",
            "MORNING",
            "NOTHING",
            "HIMSELF",
            "LOOKING",
            "SOMETHING",
            "WHETHER",
            "PRESENT",
            "FOLLOWING",
            "WITHOUT",
            "ACTUALLY",
            "AGAINST",
            "ALREADY",
            "ALTHOUGH",
            "AMERICA",
            "ANOTHER",
            "ANYTHING",
            "BROUGHT",
            "BUILDING",
            "BUSINESS",
            "CERTAIN",
            "COMPANY",
            "CONTROL",
            "COUNTRY",
            "DEVELOP",
            "DIFFERENT",
            "DURING",
            "ECONOMIC",
            "EITHER",
            "ENOUGH",
            "ESPECIALLY",
            "EXAMPLE",
            "FAMILY",
            "FATHER",
            "FEDERAL",
            "FORMER",
            "FURTHER",
            "GENERAL",
            "GETTING",
            "GOVERNMENT",
            "HAVING",
            "HEALTH",
            "HERSELF",
            "HISTORY",
            "HOWEVER",
            "HUNDRED",
            "IMPORTANT",
            "INCLUDING",
            "INCREASE",
            "INTEREST",
            "ITSELF",
            "LITTLE",
            "LIVING",
            "LOOKING",
            "MAKING",
            "MATTER",
            "MEMBER",
            "MILLION",
            "MINUTES",
            "MOMENT",
            "MOTHER",
            "MYSELF",
            "NATIONAL",
            "NATURE",
            "NECESSARY",
            "NOTHING",
            "NUMBER",
            "OFFICE",
            "OUTSIDE",
            "PARENTS",
            "PERHAPS",
            "PERIOD",
            "PERSON",
            "PICTURE",
            "PLAYING",
            "POLITICAL",
            "POSITION",
            "POSSIBLE",
            "PRESENT",
            "PRESIDENT",
            "PRIVATE",
            "PROBABLY",
            "PROBLEM",
            "PROCESS",
            "PROGRAM",
            "PUBLIC",
            "QUESTION",
            "RATHER",
            "REALLY",
            "REASON",
            "RECENT",
            "RECORD",
            "REPORT",
            "RESULT",
            "RETURN",
            "SAYING",
            "SCHOOL",
            "SECOND",
            "SEEING",
            "SEEMED",
            "SERIOUS",
            "SERVICE",
            "SEVERAL",
            "SHOULD",
            "SIMPLE",
            "SINGLE",
            "SOCIAL",
            "SOCIETY",
            "SOMEONE",
            "SPECIAL",
            "STARTED",
            "STATES",
            "STREET",
            "STRONG",
            "STUDENT",
            "SUBJECT",
            "SYSTEM",
            "TAKING",
            "THINGS",
            "THINKING",
            "THOUGH",
            "THOUGHT",
            "THROUGH",
            "TOGETHER",
            "TOWARD",
            "TRYING",
            "TURNED",
            "UNDERSTAND",
            "UNITED",
            "UNIVERSITY",
            "USUALLY",
            "VALUES",
            "VARIOUS",
            "WALKED",
            "WANTED",
            "WASHINGTON",
            "WATCHING",
            "WATER",
            "WHETHER",
            "WITHIN",
            "WITHOUT",
            "WORKING",
            "WRITING",
            "WRITTEN",
            "YESTERDAY",
            # 7-letter words
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
        }

        # Convert to uppercase and create set
        return {word.upper() for word in common_words}

    def validate_pdf(self, pdf_path: Path) -> Dict:
        """Main validation entry point"""
        validation_results = []

        try:
            # Extract puzzle data from PDF
            puzzles = self._extract_puzzles_from_pdf(pdf_path)

            # Run all validations
            validation_results.extend(self._validate_structure(puzzles))
            validation_results.extend(self._validate_words(puzzles))
            validation_results.extend(self._validate_clues(puzzles))
            validation_results.extend(self._validate_solutions(puzzles))
            validation_results.extend(self._validate_consistency(puzzles))

            # Calculate final score
            final_score = self._calculate_final_score(validation_results)

            # Generate report
            return self._generate_report(pdf_path, validation_results, final_score)

        except Exception as e:
            return {
                "status": "ERROR",
                "score": 0,
                "message": f"Validation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_puzzles_from_pdf(self, pdf_path: Path) -> List[PuzzleData]:
        """Extract puzzle data from PDF"""
        puzzles = []

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            # Parse puzzles - this is simplified, real implementation would be more
            # complex
            for i in range(50):  # Expecting 50 puzzles
                # Extract grid, clues, and solution from appropriate pages
                # This is where we'd parse the actual PDF content
                puzzle = self._parse_puzzle_from_pages(reader, i)
                if puzzle:
                    puzzles.append(puzzle)

        return puzzles

    def _parse_puzzle_from_pages(self, reader, puzzle_num: int) -> Optional[PuzzleData]:
        """Parse a single puzzle from PDF pages"""
        # This would extract:
        # - Grid from puzzle page
        # - Clues from clues page
        # - Solution from answer key
        # For now, returning None as placeholder
        return None

    def _validate_structure(self, puzzles: List[PuzzleData]) -> List[ValidationResult]:
        """Validate grid structure and patterns"""
        results = []

        for puzzle in puzzles:
            # Check grid dimensions
            if len(puzzle.grid) != 15 or any(len(row) != 15 for row in puzzle.grid):
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="structure",
                        message=f"Puzzle {puzzle.number}: Invalid grid dimensions",
                    )
                )
                continue

            # Check black square ratio
            black_count = sum(
                cell == "#" for row in puzzle.grid for cell in row)
            black_ratio = black_count / (15 * 15)

            if black_ratio > self.MAX_BLACK_SQUARE_RATIO:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=50,
                        category="structure",
                        message=f"Puzzle {
                            puzzle.number}: Too many black squares({
                                black_ratio: .1 %})",
                    )
                )

            # Check for isolated sections
            if self._has_isolated_sections(puzzle.grid):
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="structure",
                        message=f"Puzzle {puzzle.number}: Grid has isolated sections",
                    )
                )

            # Check symmetry
            if not self._is_symmetric(puzzle.grid):
                results.append(
                    ValidationResult(
                        passed=False,
                        score=70,
                        category="structure",
                        message=f"Puzzle {puzzle.number}: Grid is not symmetric",
                    )
                )

            # If all checks pass
            if not any(r.puzzle_number == puzzle.number for r in results):
                results.append(
                    ValidationResult(
                        passed=True,
                        score=100,
                        category="structure",
                        message=f"Puzzle {puzzle.number}: Structure valid",
                    )
                )

        return results

    def _validate_words(self, puzzles: List[PuzzleData]) -> List[ValidationResult]:
        """Validate that all words are real English words"""
        results = []

        for puzzle in puzzles:
            invalid_words = []

            # Extract all words from solution
            words = self._extract_words_from_solution(puzzle.solution)

            # Check each word
            for word, position in words:
                if len(word) < self.MIN_WORD_LENGTH:
                    invalid_words.append(f"{word} (too short)")
                elif word not in self.valid_words and not self._is_valid_variant(word):
                    invalid_words.append(f"{word} (not in dictionary)")

            if invalid_words:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="words",
                        message=f"Puzzle {puzzle.number}: Invalid words found",
                        details={"invalid_words": invalid_words},
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        passed=True,
                        score=100,
                        category="words",
                        message=f"Puzzle {puzzle.number}: All words valid",
                    )
                )

        return results

    def _validate_clues(self, puzzles: List[PuzzleData]) -> List[ValidationResult]:
        """Validate clue balance and quality"""
        results = []

        for puzzle in puzzles:
            across_count = len(puzzle.across_clues)
            down_count = len(puzzle.down_clues)
            total_clues = across_count + down_count

            if total_clues == 0:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="clues",
                        message=f"Puzzle {puzzle.number}: No clues found",
                    )
                )
                continue

            down_ratio = down_count / total_clues

            # Check balance
            if down_ratio < self.MIN_DOWN_CLUE_RATIO:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=25,
                        category="clues",
                        message=f"Puzzle {
                            puzzle.number}: Too few DOWN clues({down_count}/{total_clues})",
                        details={"across": across_count, "down": down_count},
                    )
                )
            elif down_ratio > self.MAX_DOWN_CLUE_RATIO:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=25,
                        category="clues",
                        message=f"Puzzle {
                            puzzle.number}: Too few ACROSS clues({across_count}/{total_clues})",
                        details={"across": across_count, "down": down_count},
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        passed=True,
                        score=100,
                        category="clues",
                        message=f"Puzzle {puzzle.number}: Clue balance good({across_count} across, {
                            down_count} down)",
                    )
                )

        return results

    def _validate_solutions(self, puzzles: List[PuzzleData]) -> List[ValidationResult]:
        """Validate solution grids"""
        results = []

        for puzzle in puzzles:
            # Check if solution exists
            if not puzzle.solution:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="solutions",
                        message=f"Puzzle {puzzle.number}: No solution found",
                    )
                )
                continue

            # Check if solution matches grid pattern
            pattern_matches = True
            for row in range(15):
                for col in range(15):
                    if (
                        puzzle.grid[row][col] == "#"
                        and puzzle.solution[row][col] != "#"
                    ):
                        pattern_matches = False
                    elif (
                        puzzle.grid[row][col] != "#"
                        and puzzle.solution[row][col] == "#"
                    ):
                        pattern_matches = False

            if not pattern_matches:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="solutions",
                        message=f"Puzzle {
                            puzzle.number}: Solution doesn't match grid pattern",
                    )
                )
                continue

            # Check if all cells have letters
            empty_cells = 0
            for row in range(15):
                for col in range(15):
                    if (
                        puzzle.solution[row][col] not in ["#"]
                        and not puzzle.solution[row][col].isalpha()
                    ):
                        empty_cells += 1

            if empty_cells > 0:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=50,
                        category="solutions",
                        message=f"Puzzle {
                            puzzle.number}: Solution has {empty_cells} empty cells",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        passed=True,
                        score=100,
                        category="solutions",
                        message=f"Puzzle {puzzle.number}: Solution complete and valid",
                    )
                )

        return results

    def _validate_consistency(
        self, puzzles: List[PuzzleData]
    ) -> List[ValidationResult]:
        """Validate internal consistency"""
        results = []

        # Check puzzle count
        if len(puzzles) != self.MIN_PUZZLE_COUNT:
            results.append(
                ValidationResult(
                    passed=False,
                    score=0,
                    category="consistency",
                    message=f"Expected {
                        self.MIN_PUZZLE_COUNT} puzzles, found {
                        len(puzzles)}",
                )
            )

        # Check for duplicate puzzles
        seen_grids = set()
        for puzzle in puzzles:
            grid_str = "".join("".join(row) for row in puzzle.grid)
            if grid_str in seen_grids:
                results.append(
                    ValidationResult(
                        passed=False,
                        score=0,
                        category="consistency",
                        message=f"Puzzle {puzzle.number}: Duplicate of another puzzle",
                    )
                )
            seen_grids.add(grid_str)

        # Check numbering consistency
        for puzzle in puzzles:
            # Verify that clue numbers exist in the grid
            for num in puzzle.across_clues.keys():
                if not self._number_exists_in_grid(puzzle, num):
                    results.append(
                        ValidationResult(
                            passed=False,
                            score=50,
                            category="consistency",
                            message=f"Puzzle {
                                puzzle.number}: ACROSS clue {num} not found in grid",
                        )
                    )

        return results

    def _extract_words_from_solution(
        self, solution: List[List[str]]
    ) -> List[Tuple[str, str]]:
        """Extract all words from solution grid"""
        words = []

        # Extract horizontal words
        for row in range(15):
            word = ""
            for col in range(15):
                if solution[row][col] != "#":
                    word += solution[row][col]
                else:
                    if len(word) >= self.MIN_WORD_LENGTH:
                        words.append((word, f"Row {row}"))
                    word = ""
            if len(word) >= self.MIN_WORD_LENGTH:
                words.append((word, f"Row {row}"))

        # Extract vertical words
        for col in range(15):
            word = ""
            for row in range(15):
                if solution[row][col] != "#":
                    word += solution[row][col]
                else:
                    if len(word) >= self.MIN_WORD_LENGTH:
                        words.append((word, f"Col {col}"))
                    word = ""
            if len(word) >= self.MIN_WORD_LENGTH:
                words.append((word, f"Col {col}"))

        return words

    def _is_valid_variant(self, word: str) -> bool:
        """Check if word is a valid variant (plural, past tense, etc.)"""
        # Simple checks for common variants
        if word.endswith("S") and word[:-1] in self.valid_words:
            return True
        if word.endswith("ED") and word[:-2] in self.valid_words:
            return True
        if word.endswith("ING") and word[:-3] in self.valid_words:
            return True
        return False

    def _has_isolated_sections(self, grid: List[List[str]]) -> bool:
        """Check if grid has isolated sections"""
        # Use flood fill to check connectivity
        visited = [[False] * 15 for _ in range(15)]

        # Find first white square
        start_r, start_c = None, None
        for r in range(15):
            for c in range(15):
                if grid[r][c] != "#":
                    start_r, start_c = r, c
                    break
            if start_r is not None:
                break

        if start_r is None:
            return True  # All black squares

        # Flood fill from first white square
        stack = [(start_r, start_c)]
        white_count = 0

        while stack:
            r, c = stack.pop()
            if r < 0 or r >= 15 or c < 0 or c >= 15:
                continue
            if visited[r][c] or grid[r][c] == "#":
                continue

            visited[r][c] = True
            white_count += 1

            # Add neighbors
            stack.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])

        # Count total white squares
        total_white = sum(cell != "#" for row in grid for cell in row)

        return white_count < total_white

    def _is_symmetric(self, grid: List[List[str]]) -> bool:
        """Check if grid has rotational symmetry"""
        for r in range(15):
            for c in range(15):
                if grid[r][c] != grid[14 - r][14 - c]:
                    return False
        return True

    def _number_exists_in_grid(self, puzzle: PuzzleData, num: int) -> bool:
        """Check if a clue number exists in the grid"""
        # This would check the actual numbering
        # For now, return True as placeholder
        return True

    def _calculate_final_score(self, results: List[ValidationResult]) -> int:
        """Calculate weighted final score"""
        category_scores = defaultdict(list)

        for result in results:
            category_scores[result.category].append(result.score)

        final_score = 0
        for category, weight in self.WEIGHTS.items():
            if category in category_scores:
                avg_score = sum(category_scores[category]) / len(
                    category_scores[category]
                )
                final_score += avg_score * weight / 100

        return int(final_score)

    def _generate_report(
        self, pdf_path: Path, results: List[ValidationResult], score: int
    ) -> Dict:
        """Generate comprehensive validation report"""
        critical_issues = [r for r in results if not r.passed and r.score == 0]
        warnings = [r for r in results if not r.passed and r.score > 0]
        passed = [r for r in results if r.passed]

        report = {
            "file": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "final_score": score,
            "pass_threshold": 95,
            "status": "PASS" if score >= 95 else "FAIL",
            "summary": {
                "total_checks": len(results),
                "passed": len(passed),
                "warnings": len(warnings),
                "critical": len(critical_issues),
            },
            "critical_issues": [
                {"category": r.category, "message": r.message, "details": r.details}
                for r in critical_issues
            ],
            "warnings": [
                {
                    "category": r.category,
                    "message": r.message,
                    "score": r.score,
                    "details": r.details,
                }
                for r in warnings
            ],
            "category_breakdown": {},
        }

        # Add category breakdown
        for category in self.WEIGHTS.keys():
            category_results = [r for r in results if r.category == category]
            if category_results:
                avg_score = sum(r.score for r in category_results) / len(
                    category_results
                )
                report["category_breakdown"][category] = {
                    "weight": self.WEIGHTS[category],
                    "average_score": avg_score,
                    "checks": len(category_results),
                    "passed": len([r for r in category_results if r.passed]),
                }

        # Add recommendations
        report["recommendations"] = self._generate_recommendations(results)

        return report

    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Check for common issues
        structure_fails = [
            r for r in results if r.category == "structure" and not r.passed
        ]
        if structure_fails:
            recommendations.append(
                "Review grid patterns - ensure proper symmetry and connectivity"
            )

        word_fails = [r for r in results if r.category ==
                      "words" and not r.passed]
        if word_fails:
            recommendations.append(
                "Validate all words against dictionary before generation"
            )

        clue_fails = [r for r in results if r.category ==
                      "clues" and not r.passed]
        if clue_fails:
            recommendations.append(
                "Ensure balanced ACROSS/DOWN distribution (35-65% each)"
            )

        solution_fails = [
            r for r in results if r.category == "solutions" and not r.passed
        ]
        if solution_fails:
            recommendations.append(
                "Verify all solution grids are complete with valid letters"
            )

        return recommendations


def main():
    """Run validation on a PDF"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python crossword_qa_validator.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    validator = CrosswordQAValidator()
    report = validator.validate_pdf(pdf_path)

    # Print report
    print(f"\n{'=' * 60}")
    print(f"CROSSWORD QA VALIDATION REPORT")
    print(f"{'=' * 60}")
    print(f"File: {report['file']}")
    print(f"Status: {report['status']}")
    print(
        f"Score: {report['final_score']
                  }/100 (Pass threshold: {report['pass_threshold']})"
    )
    print(f"\nSummary:")
    print(f"  Total Checks: {report['summary']['total_checks']}")
    print(f"  Passed: {report['summary']['passed']}")
    print(f"  Warnings: {report['summary']['warnings']}")
    print(f"  Critical: {report['summary']['critical']}")

    if report["critical_issues"]:
        print(f"\n❌ CRITICAL ISSUES:")
        for issue in report["critical_issues"]:
            print(f"  - [{issue['category']}] {issue['message']}")

    if report["warnings"]:
        print(f"\n⚠️  WARNINGS:")
        for warning in report["warnings"]:
            print(
                f" - [{warning['category']}] {warning['message']
                                              }(score: {warning['score']})"
            )

    print(f"\n📊 Category Breakdown:")
    for category, data in report["category_breakdown"].items():
        print(
            f"  {category.upper()}: {data['average_score']:.1f}/100 (weight: {data['weight']}%)"
        )

    if report["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

    # Save full report
    report_path = pdf_path.parent / f"qa_report_{pdf_path.stem}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Full report saved to: {report_path}")


if __name__ == "__main__":
    main()
