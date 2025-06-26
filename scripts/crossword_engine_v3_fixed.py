#!/usr/bin/env python3
"""
Crossword Engine v3 Fixed - Command Line Interface
Generates high-quality crossword puzzles for KindleMint Engine with proper word filling
"""

import os
import sys
import json
import random
import argparse
import string
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CrosswordEngine')

class CrosswordEngineV3:
    """Generate crossword puzzles with proper filled grids and real words"""
    
    def __init__(self, output_dir, puzzle_count=50, difficulty="mixed", grid_size=15, 
                 word_count=None, max_word_length=15, word_list_path=None):
        """Initialize the crossword generator with configuration"""
        self.grid_size = grid_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.puzzle_count = puzzle_count
        self.difficulty_mode = difficulty
        self.word_count = word_count
        self.max_word_length = max_word_length
        
        # Create puzzles directory structure
        self.puzzles_dir = self.output_dir / "puzzles"
        self.puzzles_dir.mkdir(exist_ok=True)
        
        # Create metadata directory
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Create solutions directory
        self.solutions_dir = self.output_dir / "solutions"
        self.solutions_dir.mkdir(exist_ok=True)
        
        # Load word dictionary
        self.word_dict = self._load_word_dictionary(word_list_path)
        logger.info(f"Loaded {len(self.word_dict)} words into dictionary")
        
        # Dictionary to store theme-specific words
        self.theme_words = self._generate_theme_words()
    
    def _load_word_dictionary(self, word_list_path=None):
        """Load word dictionary from file or use built-in common words"""
        word_dict = {}
        
        if word_list_path and Path(word_list_path).exists():
            # Load from provided file
            with open(word_list_path, 'r') as f:
                for line in f:
                    word = line.strip().upper()
                    if 3 <= len(word) <= self.max_word_length and word.isalpha():
                        word_dict[word] = True
        else:
            # Use built-in common English words (limited set)
            common_words = [
                # 3-letter words
                "ACE", "ACT", "ADD", "AGE", "AGO", "AID", "AIM", "AIR", "ALL", "AND", 
                "ANY", "ARM", "ART", "ASK", "BAD", "BAG", "BAR", "BAT", "BAY", "BED", 
                "BEE", "BIG", "BIT", "BOX", "BOY", "BUG", "BUS", "BUY", "CAB", "CAP", 
                "CAR", "CAT", "CUT", "DAD", "DAY", "DIE", "DIG", "DOG", "DOT", "DRY", 
                "DUE", "EAR", "EAT", "EGG", "END", "ERA", "EVE", "EYE", "FAN", "FAR", 
                "FEE", "FEW", "FIT", "FIX", "FLY", "FOG", "FOR", "FOX", "FUN", "GAP", 
                "GAS", "GET", "GOD", "GOT", "GUN", "GUY", "GYM", "HAD", "HAT", "HAS", 
                "HAY", "HER", "HID", "HIM", "HIP", "HIS", "HIT", "HOT", "HOW", "HUB", 
                "HUG", "ICE", "ILL", "INK", "INN", "JAM", "JAR", "JET", "JOB", "JOG", 
                "JOY", "KEY", "KID", "KIT", "LAB", "LAD", "LAG", "LAP", "LAW", "LAY", 
                "LEG", "LET", "LID", "LIE", "LIP", "LOG", "LOT", "LOW", "MAP", "MAT", 
                "MAX", "MAY", "MEN", "MET", "MIX", "MOB", "MOM", "MOP", "MUD", "MUG", 
                "NAP", "NET", "NEW", "NIL", "NOR", "NOT", "NOW", "NUT", "OAK", "ODD", 
                "OFF", "OIL", "OLD", "ONE", "OUR", "OUT", "OWL", "OWN", "PAD", "PAN", 
                "PAR", "PAT", "PAW", "PAY", "PEN", "PET", "PIE", "PIG", "PIN", "PIT", 
                "POT", "PRO", "PUT", "RAG", "RAT", "RAW", "RED", "RIB", "RID", "RIG", 
                "RIM", "RIP", "ROD", "ROW", "RUB", "RUG", "RUN", "SAD", "SAG", "SAT", 
                "SAW", "SAY", "SEA", "SEE", "SET", "SEW", "SHE", "SHY", "SIN", "SIP", 
                "SIR", "SIT", "SIX", "SKI", "SKY", "SLY", "SON", "SPA", "SPY", "SUM", 
                "SUN", "TAB", "TAG", "TAP", "TAX", "TEA", "TEN", "THE", "TIE", "TIN", 
                "TIP", "TOE", "TON", "TOP", "TOW", "TOY", "TRY", "TUB", "TWO", "USE", 
                "VAN", "VAT", "VET", "VIA", "WAR", "WAS", "WAX", "WAY", "WEB", "WET", 
                "WHO", "WHY", "WIN", "WON", "YES", "YET", "YOU", "ZOO",
                
                # 4-letter words
                "ABLE", "ACID", "AGED", "ALSO", "AREA", "ARMY", "AWAY", "BABY", "BACK", 
                "BALL", "BAND", "BANK", "BASE", "BATH", "BEAR", "BEAT", "BEEN", "BEER", 
                "BELL", "BELT", "BEST", "BILL", "BIRD", "BLOW", "BLUE", "BOAT", "BODY", 
                "BOMB", "BOND", "BONE", "BOOK", "BOOM", "BORN", "BOSS", "BOTH", "BOWL", 
                "BULK", "BURN", "BUSH", "BUSY", "CALL", "CALM", "CAME", "CAMP", "CARD", 
                "CARE", "CASE", "CASH", "CAST", "CELL", "CHAT", "CHIP", "CITY", "CLUB", 
                "COAL", "COAT", "CODE", "COLD", "COME", "COOK", "COOL", "COPE", "COPY", 
                "CORE", "COST", "CREW", "CROP", "DARK", "DATA", "DATE", "DAWN", "DAYS", 
                "DEAD", "DEAL", "DEAN", "DEAR", "DEBT", "DEEP", "DENY", "DESK", "DIAL", 
                "DIET", "DIRT", "DISC", "DISK", "DOES", "DONE", "DOOR", "DOSE", "DOWN", 
                "DRAW", "DROP", "DRUG", "DUAL", "DUKE", "DUST", "DUTY", "EACH", "EARN", 
                "EASE", "EAST", "EASY", "EDGE", "ELSE", "EVEN", "EVER", "EVIL", "EXIT", 
                "FACE", "FACT", "FAIL", "FAIR", "FALL", "FARM", "FAST", "FATE", "FEAR", 
                "FEED", "FEEL", "FEET", "FELL", "FELT", "FILE", "FILL", "FILM", "FIND", 
                "FINE", "FIRE", "FIRM", "FISH", "FIVE", "FLAT", "FLOW", "FOOD", "FOOT", 
                "FORD", "FORM", "FORT", "FOUR", "FREE", "FROM", "FUEL", "FULL", "FUND", 
                "GAIN", "GAME", "GATE", "GAVE", "GEAR", "GENE", "GIFT", "GIRL", "GIVE", 
                "GLAD", "GOAL", "GOES", "GOLD", "GOLF", "GONE", "GOOD", "GRAY", "GREW", 
                "GREY", "GROW", "GULF", "HAIR", "HALF", "HALL", "HAND", "HANG", "HARD", 
                "HARM", "HATE", "HAVE", "HEAD", "HEAR", "HEAT", "HELD", "HELL", "HELP", 
                "HERE", "HERO", "HIGH", "HILL", "HIRE", "HOLD", "HOLE", "HOLY", "HOME", 
                "HOPE", "HOST", "HOUR", "HUGE", "HUNG", "HUNT", "HURT", "IDEA", "INCH", 
                "INTO", "IRON", "ITEM", "JACK", "JANE", "JEAN", "JOHN", "JOIN", "JUMP", 
                "JURY", "JUST", "KEEN", "KEEP", "KENT", "KEPT", "KICK", "KILL", "KIND", 
                "KING", "KNEE", "KNEW", "KNOW", "LACK", "LADY", "LAID", "LAKE", "LAND", 
                "LANE", "LAST", "LATE", "LEAD", "LEFT", "LESS", "LIFE", "LIFT", "LIKE", 
                "LINE", "LINK", "LIST", "LIVE", "LOAD", "LOAN", "LOCK", "LOGO", "LONG", 
                "LOOK", "LORD", "LOSE", "LOSS", "LOST", "LOVE", "LUCK", "MADE", "MAIL", 
                "MAIN", "MAKE", "MALE", "MANY", "MARK", "MASS", "MATT", "MEAL", "MEAN", 
                "MEAT", "MEET", "MENU", "MERE", "MIKE", "MILE", "MILK", "MILL", "MIND", 
                "MINE", "MISS", "MODE", "MOOD", "MOON", "MORE", "MOST", "MOVE", "MUCH", 
                "MUST", "NAME", "NAVY", "NEAR", "NECK", "NEED", "NEWS", "NEXT", "NICE", 
                "NICK", "NINE", "NONE", "NOSE", "NOTE", "OKAY", "ONCE", "ONLY", "ONTO", 
                "OPEN", "ORAL", "OVER", "PACE", "PACK", "PAGE", "PAID", "PAIN", "PAIR", 
                "PALM", "PARK", "PART", "PASS", "PAST", "PATH", "PEAK", "PICK", "PINK", 
                "PIPE", "PLAN", "PLAY", "PLOT", "PLUG", "PLUS", "POLL", "POOL", "POOR", 
                "PORT", "POST", "PULL", "PURE", "PUSH", "RACE", "RAIL", "RAIN", "RANK", 
                "RARE", "RATE", "READ", "REAL", "REAR", "RELY", "RENT", "REST", "RICE", 
                "RICH", "RIDE", "RING", "RISE", "RISK", "ROAD", "ROCK", "ROLE", "ROLL", 
                "ROOF", "ROOM", "ROOT", "ROSE", "RULE", "RUSH", "RUTH", "SAFE", "SAID", 
                "SAKE", "SALE", "SALT", "SAME", "SAND", "SAVE", "SEAT", "SEED", "SEEK", 
                "SEEM", "SEEN", "SELF", "SELL", "SEND", "SENT", "SEPT", "SHIP", "SHOP", 
                "SHOT", "SHOW", "SHUT", "SICK", "SIDE", "SIGN", "SITE", "SIZE", "SKIN", 
                "SLIP", "SLOW", "SNOW", "SOFT", "SOIL", "SOLD", "SOLE", "SOME", "SONG", 
                "SOON", "SORT", "SOUL", "SPOT", "STAR", "STAY", "STEP", "STOP", "SUCH", 
                "SUIT", "SURE", "TAKE", "TALE", "TALK", "TALL", "TANK", "TAPE", "TASK", 
                "TEAM", "TECH", "TELL", "TEND", "TERM", "TEST", "TEXT", "THAN", "THAT", 
                "THEM", "THEN", "THEY", "THIN", "THIS", "THUS", "TILL", "TIME", "TINY", 
                "TOLD", "TOLL", "TONE", "TONY", "TOOK", "TOOL", "TOUR", "TOWN", "TREE", 
                "TRIP", "TRUE", "TUNE", "TURN", "TWIN", "TYPE", "UNIT", "UPON", "USED", 
                "USER", "VARY", "VAST", "VERY", "VIEW", "VOTE", "WAGE", "WAIT", "WAKE", 
                "WALK", "WALL", "WANT", "WARD", "WARM", "WASH", "WAVE", "WAYS", "WEAK", 
                "WEAR", "WEEK", "WELL", "WENT", "WERE", "WEST", "WHAT", "WHEN", "WHOM", 
                "WIDE", "WIFE", "WILD", "WILL", "WIND", "WINE", "WING", "WIRE", "WISE", 
                "WISH", "WITH", "WOOD", "WORD", "WORE", "WORK", "YARD", "YEAH", "YEAR", 
                "YOUR", "ZERO", "ZONE",
                
                # 5+ letter words (common ones)
                "ABOUT", "ABOVE", "ABUSE", "ACTOR", "ADAPT", "ADDED", "ADMIT", "ADOPT", 
                "AFTER", "AGAIN", "AGENT", "AGREE", "AHEAD", "ALARM", "ALBUM", "ALERT", 
                "ALIKE", "ALIVE", "ALLOW", "ALONE", "ALONG", "ALTER", "AMONG", "ANGER", 
                "ANGLE", "ANGRY", "APART", "APPLE", "APPLY", "ARENA", "ARGUE", "ARISE", 
                "ARRAY", "ASIDE", "ASSET", "AVOID", "AWARD", "AWARE", "BADLY", "BAKER", 
                "BASES", "BASIC", "BASIS", "BEACH", "BEGAN", "BEGIN", "BEGUN", "BEING", 
                "BELOW", "BENCH", "BILLY", "BIRTH", "BLACK", "BLAME", "BLANK", "BLAST", 
                "BLEND", "BLESS", "BLIND", "BLOCK", "BLOOD", "BOARD", "BOOST", "BOOTH", 
                "BOUND", "BRAIN", "BRAND", "BREAD", "BREAK", "BREED", "BRIEF", "BRING", 
                "BROAD", "BROKE", "BROWN", "BUILD", "BUILT", "BUNCH", "BURST", "CABLE", 
                "CALIF", "CARRY", "CATCH", "CAUSE", "CHAIN", "CHAIR", "CHART", "CHASE", 
                "CHEAP", "CHECK", "CHEST", "CHIEF", "CHILD", "CHINA", "CHOSE", "CIVIL", 
                "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLICK", "CLOCK", "CLOSE", "COACH", 
                "COAST", "COULD", "COUNT", "COURT", "COVER", "CRAFT", "CRASH", "CREAM", 
                "CRIME", "CROSS", "CROWD", "CROWN", "CURVE", "CYCLE", "DAILY", "DANCE", 
                "DATED", "DEALT", "DEATH", "DEBUT", "DELAY", "DEPTH", "DOING", "DOUBT", 
                "DOZEN", "DRAFT", "DRAMA", "DRAWN", "DREAM", "DRESS", "DRILL", "DRINK", 
                "DRIVE", "DROVE", "DYING", "EAGER", "EARLY", "EARTH", "EIGHT", "ELITE", 
                "EMPTY", "ENEMY", "ENJOY", "ENTER", "ENTRY", "EQUAL", "ERROR", "EVENT", 
                "EVERY", "EXACT", "EXIST", "EXTRA", "FAITH", "FALSE", "FAULT", "FAVOR", 
                "FENCE", "FIELD", "FIFTH", "FIFTY", "FIGHT", "FINAL", "FIRST", "FIXED", 
                "FLASH", "FLEET", "FLOOR", "FLUID", "FOCUS", "FORCE", "FORTH", "FORTY", 
                "FORUM", "FOUND", "FRAME", "FRANK", "FRAUD", "FRESH", "FRONT", "FRUIT", 
                "FULLY", "FUNNY", "GIANT", "GIVEN", "GLASS", "GLOBE", "GOING", "GRACE", 
                "GRADE", "GRAND", "GRANT", "GRASS", "GREAT", "GREEN", "GROSS", "GROUP", 
                "GROWN", "GUARD", "GUESS", "GUEST", "GUIDE", "HAPPY", "HARRY", "HEART", 
                "HEAVY", "HENCE", "HENRY", "HORSE", "HOTEL", "HOUSE", "HUMAN", "IDEAL", 
                "IMAGE", "INDEX", "INNER", "INPUT", "ISSUE", "JAPAN", "JIMMY", "JOINT", 
                "JONES", "JUDGE", "KNOWN", "LABEL", "LARGE", "LASER", "LATER", "LAUGH", 
                "LAYER", "LEARN", "LEASE", "LEAST", "LEAVE", "LEGAL", "LEVEL", "LEWIS", 
                "LIGHT", "LIMIT", "LINKS", "LIVES", "LOCAL", "LOGIC", "LOOSE", "LOWER", 
                "LUCKY", "LUNCH", "LYING", "MAGIC", "MAJOR", "MAKER", "MARCH", "MARIA", 
                "MATCH", "MAYBE", "MAYOR", "MEANT", "MEDIA", "METAL", "MIGHT", "MINOR", 
                "MINUS", "MIXED", "MODEL", "MONEY", "MONTH", "MORAL", "MOTOR", "MOUNT", 
                "MOUSE", "MOUTH", "MOVIE", "MUSIC", "NEEDS", "NEVER", "NEWLY", "NIGHT", 
                "NOISE", "NORTH", "NOTED", "NOVEL", "NURSE", "OCCUR", "OCEAN", "OFFER", 
                "OFTEN", "ORDER", "OTHER", "OUGHT", "PAINT", "PANEL", "PAPER", "PARTY", 
                "PEACE", "PETER", "PHASE", "PHONE", "PHOTO", "PIECE", "PILOT", "PITCH", 
                "PLACE", "PLAIN", "PLANE", "PLANT", "PLATE", "POINT", "POUND", "POWER", 
                "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIOR", "PRIZE", "PROOF", 
                "PROUD", "PROVE", "QUEEN", "QUICK", "QUIET", "QUITE", "RADIO", "RAISE", 
                "RANGE", "RAPID", "RATIO", "REACH", "READY", "REFER", "RIGHT", "RIVAL", 
                "RIVER", "ROBIN", "ROGER", "ROMAN", "ROUGH", "ROUND", "ROUTE", "ROYAL", 
                "RURAL", "SCALE", "SCENE", "SCOPE", "SCORE", "SENSE", "SERVE", "SEVEN", 
                "SHALL", "SHAPE", "SHARE", "SHARP", "SHEET", "SHELF", "SHELL", "SHIFT", 
                "SHIRT", "SHOCK", "SHOOT", "SHORT", "SHOWN", "SIGHT", "SINCE", "SIXTH", 
                "SIXTY", "SIZED", "SKILL", "SLEEP", "SLIDE", "SMALL", "SMART", "SMILE", 
                "SMITH", "SMOKE", "SOLID", "SOLVE", "SORRY", "SOUND", "SOUTH", "SPACE", 
                "SPARE", "SPEAK", "SPEED", "SPEND", "SPENT", "SPLIT", "SPOKE", "SPORT", 
                "STAFF", "STAGE", "STAKE", "STAND", "START", "STATE", "STEAM", "STEEL", 
                "STICK", "STILL", "STOCK", "STONE", "STOOD", "STORE", "STORM", "STORY", 
                "STRIP", "STUCK", "STUDY", "STUFF", "STYLE", "SUGAR", "SUITE", "SUPER", 
                "SWEET", "TABLE", "TAKEN", "TASTE", "TAXES", "TEACH", "TEETH", "TERRY", 
                "TEXAS", "THANK", "THEFT", "THEIR", "THEME", "THERE", "THESE", "THICK", 
                "THING", "THINK", "THIRD", "THOSE", "THREE", "THREW", "THROW", "TIGHT", 
                "TIMES", "TIRED", "TITLE", "TODAY", "TOPIC", "TOTAL", "TOUCH", "TOUGH", 
                "TOWER", "TRACK", "TRADE", "TRAIN", "TREAT", "TREND", "TRIAL", "TRIED", 
                "TRIES", "TRUCK", "TRULY", "TRUST", "TRUTH", "TWICE", "UNDER", "UNDUE", 
                "UNION", "UNITY", "UNTIL", "UPPER", "UPSET", "URBAN", "USAGE", "USUAL", 
                "VALID", "VALUE", "VIDEO", "VIRUS", "VISIT", "VITAL", "VOICE", "WASTE", 
                "WATCH", "WATER", "WHEEL", "WHERE", "WHICH", "WHILE", "WHITE", "WHOLE", 
                "WHOSE", "WOMAN", "WOMEN", "WORLD", "WORRY", "WORSE", "WORST", "WORTH", 
                "WOULD", "WOUND", "WRITE", "WRONG", "WROTE", "YIELD", "YOUNG", "YOUTH"
            ]
            
            # Add words to dictionary
            for word in common_words:
                word_dict[word] = True
                
            # Add some longer words for variety
            longer_words = [
                "PUZZLE", "CROSSWORD", "SOLUTION", "CHALLENGE", "DICTIONARY", 
                "KNOWLEDGE", "QUESTION", "ANSWER", "MYSTERY", "DISCOVERY",
                "LEARNING", "THINKING", "PROBLEM", "SOLVING", "EDUCATION",
                "EXPERIENCE", "ADVENTURE", "JOURNEY", "EXPLORATION", "WISDOM",
                "CREATIVITY", "IMAGINATION", "INNOVATION", "INSPIRATION", "MOTIVATION",
                "DETERMINATION", "PERSISTENCE", "PATIENCE", "DILIGENCE", "EXCELLENCE",
                "ACHIEVEMENT", "SUCCESS", "VICTORY", "TRIUMPH", "ACCOMPLISHMENT",
                "DEVELOPMENT", "PROGRESS", "GROWTH", "IMPROVEMENT", "ADVANCEMENT",
                "UNDERSTANDING", "COMPREHENSION", "PERCEPTION", "RECOGNITION", "AWARENESS",
                "INTELLIGENCE", "BRILLIANCE", "GENIUS", "MASTERY", "EXPERTISE"
            ]
            
            for word in longer_words:
                if len(word) <= self.max_word_length:
                    word_dict[word] = True
        
        return word_dict
    
    def _generate_theme_words(self):
        """Generate theme-specific word lists"""
        theme_words = {
            # Easy themes
            "Garden Flowers": ["ROSE", "DAISY", "TULIP", "LILY", "IRIS", "PANSY", "POPPY", "DAHLIA"],
            "Kitchen Tools": ["KNIFE", "SPOON", "FORK", "WHISK", "GRATER", "SPATULA", "LADLE", "POT", "PAN"],
            "Family Time": ["GAME", "MOVIE", "DINNER", "CHAT", "PLAY", "LAUGH", "SHARE", "LOVE", "HUG"],
            "Weather": ["RAIN", "SNOW", "WIND", "STORM", "SUN", "CLOUD", "HEAT", "COLD", "FOG"],
            "Colors": ["RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE", "PINK", "BROWN", "BLACK", "WHITE"],
            "Fruits": ["APPLE", "BANANA", "ORANGE", "GRAPE", "PEAR", "PEACH", "PLUM", "CHERRY", "LEMON", "LIME"],
            "Birds": ["ROBIN", "EAGLE", "HAWK", "OWL", "CROW", "DUCK", "SWAN", "GOOSE", "FINCH", "WREN"],
            
            # Medium themes
            "Classic Movies": ["CASABLANCA", "GODFATHER", "VERTIGO", "PSYCHO", "CITIZEN", "KANE", "JAWS"],
            "Famous Authors": ["DICKENS", "TOLKIEN", "AUSTEN", "TWAIN", "HEMINGWAY", "CHRISTIE", "KING"],
            "World Capitals": ["LONDON", "PARIS", "ROME", "TOKYO", "BERLIN", "MADRID", "MOSCOW", "CAIRO"],
            "Card Games": ["POKER", "BRIDGE", "HEARTS", "SPADES", "RUMMY", "CANASTA", "EUCHRE", "WHIST"],
            
            # Hard themes
            "Literature": ["METAPHOR", "ALLEGORY", "SONNET", "TRAGEDY", "COMEDY", "IRONY", "SATIRE"],
            "Science": ["QUANTUM", "ELECTRON", "MOLECULE", "CATALYST", "ENTROPY", "FUSION", "GRAVITY"],
            "Classical Music": ["SYMPHONY", "CONCERTO", "SONATA", "QUARTET", "ARIA", "OVERTURE", "FUGUE"]
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
        grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Apply black squares
        black_squares = self.create_symmetric_pattern(difficulty)
        for r, c in black_squares:
            grid[r][c] = '#'
            # Symmetric position
            grid[self.grid_size-1-r][self.grid_size-1-c] = '#'
        
        # Find all word slots (across and down)
        across_slots = []
        down_slots = []
        
        # Find across word slots
        for r in range(self.grid_size):
            c = 0
            while c < self.grid_size:
                if grid[r][c] == '#':
                    c += 1
                    continue
                
                # Found start of a potential word
                start_c = c
                while c < self.grid_size and grid[r][c] != '#':
                    c += 1
                
                # If length >= 3, it's a valid word slot
                if c - start_c >= 3:
                    across_slots.append((r, start_c, c - start_c))
                else:
                    c = start_c + 1
        
        # Find down word slots
        for c in range(self.grid_size):
            r = 0
            while r < self.grid_size:
                if grid[r][c] == '#':
                    r += 1
                    continue
                
                # Found start of a potential word
                start_r = r
                while r < self.grid_size and grid[r][c] != '#':
                    r += 1
                
                # If length >= 3, it's a valid word slot
                if r - start_r >= 3:
                    down_slots.append((start_r, c, r - start_r))
                else:
                    r = start_r + 1
        
        # Sort slots by decreasing length (fill longer words first)
        across_slots.sort(key=lambda x: -x[2])
        down_slots.sort(key=lambda x: -x[2])
        
        # Get theme-specific words if available
        theme_word_list = self.theme_words.get(theme, [])
        
        # Fill the grid using backtracking
        filled_grid = self._fill_grid(grid, across_slots, down_slots, theme_word_list)
        
        if not filled_grid:
            logger.warning(f"Failed to fill grid for puzzle {puzzle_id}. Retrying with simpler pattern.")
            # Retry with simpler pattern
            grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            black_squares = self.create_symmetric_pattern("EASY")
            for r, c in black_squares:
                grid[r][c] = '#'
                grid[self.grid_size-1-r][self.grid_size-1-c] = '#'
            
            # Recalculate word slots
            across_slots = []
            down_slots = []
            
            # Find across word slots
            for r in range(self.grid_size):
                c = 0
                while c < self.grid_size:
                    if grid[r][c] == '#':
                        c += 1
                        continue
                    
                    start_c = c
                    while c < self.grid_size and grid[r][c] != '#':
                        c += 1
                    
                    if c - start_c >= 3:
                        across_slots.append((r, start_c, c - start_c))
                    else:
                        c = start_c + 1
            
            # Find down word slots
            for c in range(self.grid_size):
                r = 0
                while r < self.grid_size:
                    if grid[r][c] == '#':
                        r += 1
                        continue
                    
                    start_r = r
                    while r < self.grid_size and grid[r][c] != '#':
                        r += 1
                    
                    if r - start_r >= 3:
                        down_slots.append((start_r, c, r - start_r))
                    else:
                        r = start_r + 1
            
            across_slots.sort(key=lambda x: -x[2])
            down_slots.sort(key=lambda x: -x[2])
            
            filled_grid = self._fill_grid(grid, across_slots, down_slots, theme_word_list)
        
        if not filled_grid:
            logger.error(f"Failed to generate valid grid for puzzle {puzzle_id} after retries.")
            # Fall back to a very simple grid with predefined words
            filled_grid = self._create_fallback_grid()
        
        return filled_grid
    
    def _fill_grid(self, grid, across_slots, down_slots, theme_words, max_attempts=3):
        """Fill the grid with valid words using backtracking"""
        # Make a copy of the grid
        grid_copy = [row[:] for row in grid]
        
        # Create a list of all slots
        all_slots = [(slot, 'across') for slot in across_slots] + [(slot, 'down') for slot in down_slots]
        
        # Sort by number of intersections (most constrained first)
        slot_intersections = {}
        for (slot, direction) in all_slots:
            intersections = 0
            if direction == 'across':
                r, c, length = slot
                for i in range(length):
                    for other_slot, other_dir in all_slots:
                        if other_dir == 'down':
                            other_r, other_c, other_len = other_slot
                            if other_c == c + i and other_r <= r < other_r + other_len:
                                intersections += 1
            else:  # down
                r, c, length = slot
                for i in range(length):
                    for other_slot, other_dir in all_slots:
                        if other_dir == 'across':
                            other_r, other_c, other_len = other_slot
                            if other_r == r + i and other_c <= c < other_c + other_len:
                                intersections += 1
            
            slot_intersections[(slot, direction)] = intersections
        
        all_slots.sort(key=lambda x: (-slot_intersections[x], -x[0][2]))
        
        # Try to fill the grid
        used_words = set()
        
        # First try to place theme words
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
        
        # Now fill the rest
        for attempt in range(max_attempts):
            success = self._backtrack_fill(grid_copy, all_slots, used_words)
            if success:
                return grid_copy
            
            # Reset for next attempt
            grid_copy = [row[:] for row in grid]
            used_words = set(word for word, _, _ in theme_words_used)
            
            # Re-place theme words
            for word, slot, direction in theme_words_used:
                self._place_word(grid_copy, slot, direction, word)
        
        return None
    
    def _backtrack_fill(self, grid, slots, used_words, index=0):
        """Recursively fill the grid using backtracking"""
        if index >= len(slots):
            return True
        
        slot, direction = slots[index]
        r, c, length = slot
        
        # Get current constraints
        constraints = self._get_constraints(grid, slot, direction)
        
        # Find valid words matching constraints
        valid_words = self._find_valid_words(constraints, length, used_words)
        
        # Try each valid word
        for word in valid_words:
            # Place the word
            self._place_word(grid, slot, direction, word)
            used_words.add(word)
            
            # Recursively fill the rest
            if self._backtrack_fill(grid, slots, used_words, index + 1):
                return True
            
            # Backtrack
            used_words.remove(word)
            self._remove_word(grid, slot, direction)
        
        return False
    
    def _get_constraints(self, grid, slot, direction):
        """Get constraints for a word slot"""
        constraints = {}
        r, c, length = slot
        
        if direction == 'across':
            for i in range(length):
                if grid[r][c + i] != ' ':
                    constraints[i] = grid[r][c + i]
        else:  # down
            for i in range(length):
                if grid[r + i][c] != ' ':
                    constraints[i] = grid[r + i][c]
        
        return constraints
    
    def _find_valid_words(self, constraints, length, used_words):
        """Find valid words matching constraints"""
        valid_words = []
        
        # Check all words in dictionary
        for word in self.word_dict:
            if len(word) == length and word not in used_words:
                # Check constraints
                matches = True
                for pos, letter in constraints.items():
                    if word[pos] != letter:
                        matches = False
                        break
                
                if matches:
                    valid_words.append(word)
        
        # Shuffle to avoid similar patterns
        random.shuffle(valid_words)
        
        return valid_words
    
    def _can_place_word(self, grid, slot, direction, word):
        """Check if a word can be placed at the given slot"""
        r, c, length = slot
        
        if len(word) != length:
            return False
        
        # Check constraints
        if direction == 'across':
            for i in range(length):
                if grid[r][c + i] != ' ' and grid[r][c + i] != word[i]:
                    return False
        else:  # down
            for i in range(length):
                if grid[r + i][c] != ' ' and grid[r + i][c] != word[i]:
                    return False
        
        return True
    
    def _place_word(self, grid, slot, direction, word):
        """Place a word on the grid"""
        r, c, length = slot
        
        if direction == 'across':
            for i in range(length):
                grid[r][c + i] = word[i]
        else:  # down
            for i in range(length):
                grid[r + i][c] = word[i]
    
    def _remove_word(self, grid, slot, direction):
        """Remove a word from the grid, preserving intersections"""
        r, c, length = slot
        
        # Create a temporary grid to track which cells to clear
        temp_grid = [[False for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        if direction == 'across':
            for i in range(length):
                temp_grid[r][c + i] = True
        else:  # down
            for i in range(length):
                temp_grid[r + i][c] = True
        
        # Clear cells, but only if they're not part of another word
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if temp_grid[i][j]:
                    # Check if this cell is part of another word
                    is_intersection = False
                    
                    if direction == 'across':
                        # Check if it's part of a down word
                        if i > 0 and grid[i-1][j] != ' ' and grid[i-1][j] != '#':
                            is_intersection = True
                        elif i < self.grid_size - 1 and grid[i+1][j] != ' ' and grid[i+1][j] != '#':
                            is_intersection = True
                    else:  # down
                        # Check if it's part of an across word
                        if j > 0 and grid[i][j-1] != ' ' and grid[i][j-1] != '#':
                            is_intersection = True
                        elif j < self.grid_size - 1 and grid[i][j+1] != ' ' and grid[i][j+1] != '#':
                            is_intersection = True
                    
                    if not is_intersection:
                        grid[i][j] = ' '
    
    def _create_fallback_grid(self):
        """Create a simple grid with predefined words as a last resort"""
        grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Create a simple pattern of black squares
        for i in range(0, self.grid_size, 4):
            for j in range(0, self.grid_size, 4):
                grid[i][j] = '#'
                grid[self.grid_size-1-i][self.grid_size-1-j] = '#'
        
        # Add some predefined words
        words_across = ["PUZZLE", "CROSS", "WORD", "GAME", "PLAY", "FUN", "SOLVE"]
        words_down = ["PENCIL", "CLUE", "GRID", "BOX", "WIN", "TRY", "MIND"]
        
        # Place across words
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
        
        # Place down words
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
        cell_size = 60
        margin = 40
        img_size = self.grid_size * cell_size + 2 * margin
        
        # Create empty grid image (for puzzle)
        empty_img = Image.new('RGB', (img_size, img_size), 'white')
        empty_draw = ImageDraw.Draw(empty_img)
        
        # Create filled grid image (for solution)
        filled_img = Image.new('RGB', (img_size, img_size), 'white')
        filled_draw = ImageDraw.Draw(filled_img)
        
        # Try to load font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            try:
                # Try common Linux font
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
                number_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                # Fall back to default
                font = ImageFont.load_default()
                number_font = font
        
        # Draw grid and add numbers
        number = 1
        clue_positions = {}
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = margin + col * cell_size
                y = margin + row * cell_size
                
                if grid[row][col] == '#':
                    # Black square (same for both grids)
                    empty_draw.rectangle([x, y, x + cell_size, y + cell_size], fill='black')
                    filled_draw.rectangle([x, y, x + cell_size, y + cell_size], fill='black')
                else:
                    # White square with border
                    empty_draw.rectangle([x, y, x + cell_size, y + cell_size], outline='black', width=2)
                    filled_draw.rectangle([x, y, x + cell_size, y + cell_size], outline='black', width=2)
                    
                    # Add letter to filled grid (solution)
                    letter = grid[row][col]
                    text_width, text_height = filled_draw.textsize(letter, font=font)
                    filled_draw.text(
                        (x + (cell_size - text_width) / 2, y + (cell_size - text_height) / 2),
                        letter, font=font, fill='black'
                    )
                    
                    # Add number if this starts a word
                    needs_number = False
                    
                    # Check across
                    if (col == 0 or grid[row][col-1] == '#') and col < self.grid_size-1 and grid[row][col+1] != '#':
                        needs_number = True
                    
                    # Check down
                    if (row == 0 or grid[row-1][col] == '#') and row < self.grid_size-1 and grid[row+1][col] != '#':
                        needs_number = True
                    
                    if needs_number:
                        empty_draw.text((x + 5, y + 5), str(number), font=number_font, fill='black')
                        filled_draw.text((x + 5, y + 5), str(number), font=number_font, fill='black')
                        clue_positions[(row, col)] = number
                        number += 1
        
        # Save images
        empty_img_path = self.puzzles_dir / f"puzzle_{puzzle_id:02d}.png"
        empty_img.save(empty_img_path, 'PNG')
        
        filled_img_path = self.solutions_dir / f"solution_{puzzle_id:02d}.png"
        filled_img.save(filled_img_path, 'PNG')
        
        return empty_img_path, filled_img_path, clue_positions
    
    def extract_words_from_grid(self, grid, clue_positions):
        """Extract words and their positions from the filled grid"""
        across_words = []
        down_words = []
        
        # Extract across words
        for row in range(self.grid_size):
            col = 0
            while col < self.grid_size:
                if grid[row][col] == '#':
                    col += 1
                    continue
                
                # Check if this is the start of a word
                if col == 0 or grid[row][col-1] == '#':
                    # Find the word
                    start_col = col
                    word = ""
                    while col < self.grid_size and grid[row][col] != '#':
                        word += grid[row][col]
                        col += 1
                    
                    # Only add if length >= 3
                    if len(word) >= 3:
                        # Find the clue number
                        number = clue_positions.get((row, start_col))
                        if number:
                            across_words.append((number, word, (row, start_col)))
                else:
                    col += 1
        
        # Extract down words
        for col in range(self.grid_size):
            row = 0
            while row < self.grid_size:
                if grid[row][col] == '#':
                    row += 1
                    continue
                
                # Check if this is the start of a word
                if row == 0 or grid[row-1][col] == '#':
                    # Find the word
                    start_row = row
                    word = ""
                    while row < self.grid_size and grid[row][col] != '#':
                        word += grid[row][col]
                        row += 1
                    
                    # Only add if length >= 3
                    if len(word) >= 3:
                        # Find the clue number
                        number = clue_positions.get((start_row, col))
                        if number:
                            down_words.append((number, word, (start_row, col)))
                else:
                    row += 1
        
        # Sort by clue number
        across_words.sort(key=lambda x: x[0])
        down_words.sort(key=lambda x: x[0])
        
        return across_words, down_words
    
    def generate_clues(self, puzzle_id, theme, difficulty, across_words, down_words):
        """Generate appropriate clues based on words and difficulty"""
        # Dictionary of common words and their clues
        common_clues = {
            # 3-letter words
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
            
            # 4-letter words
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
            
            # 5+ letter words
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
            "ORANGE": ["Citrus fruit", "Color between red and yellow", "Tangerine relative"],
            "PENCIL": ["Writing tool", "Drawing implement", "Graphite stick"],
            "PUZZLE": ["Brain teaser", "Jigsaw challenge", "Mental game"],
            "RIVER": ["Flowing water", "Stream", "Waterway"],
            "SCHOOL": ["Learning place", "Education building", "Student's destination"],
            "TABLE": ["Flat surface furniture", "Dining platform", "Desk"],
            "WINDOW": ["Glass opening", "View frame", "Wall aperture"],
            "WINTER": ["Cold season", "Snow time", "December to March"],
            
            # Theme-specific words
            "CROSSWORD": ["Word puzzle", "Grid challenge", "Intersecting words game"],
            "SOLUTION": ["Answer", "Resolution", "Puzzle completion"],
            "CHALLENGE": ["Difficult task", "Test of ability", "Contest"],
            "KNOWLEDGE": ["Information", "Learning", "Understanding"],
            "QUESTION": ["Inquiry", "Query", "Problem to solve"]
        }
        
        clues = {
            "across": [],
            "down": []
        }
        
        # Generate clues for across words
        for number, word, _ in across_words:
            if word in common_clues:
                # Use predefined clue
                clue_options = common_clues[word]
                # Select harder or easier clues based on difficulty
                clue_index = 0  # Easy
                if difficulty == "MEDIUM":
                    clue_index = min(1, len(clue_options) - 1)  # Medium
                elif difficulty == "HARD":
                    clue_index = min(2, len(clue_options) - 1)  # Hard
                
                clue = clue_options[clue_index]
            else:
                # Generate a simple clue based on word characteristics
                if word.endswith("ING"):
                    clue = f"Action of {word[:-3].lower()}"
                elif word.endswith("ER"):
                    clue = f"One who {word[:-2].lower()}s"
                elif word.endswith("LY"):
                    clue = f"In a {word[:-2].lower()} manner"
                else:
                    clue = f"Related to {word.lower()}"
            
            clues["across"].append((number, clue, word))
        
        # Generate clues for down words
        for number, word, _ in down_words:
            if word in common_clues:
                # Use predefined clue
                clue_options = common_clues[word]
                # Select harder or easier clues based on difficulty
                clue_index = 0  # Easy
                if difficulty == "MEDIUM":
                    clue_index = min(1, len(clue_options) - 1)  # Medium
                elif difficulty == "HARD":
                    clue_index = min(2, len(clue_options) - 1)  # Hard
                
                clue = clue_options[clue_index]
            else:
                # Generate a simple clue based on word characteristics
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
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check minimum word count
        if len(across_words) < 10 or len(down_words) < 10:
            validation["valid"] = False
            validation["issues"].append(f"Too few words: {len(across_words)} across, {len(down_words)} down")
        
        # Check word balance (should have roughly equal across and down)
        total_words = len(across_words) + len(down_words)
        if len(across_words) < total_words * 0.3 or len(down_words) < total_words * 0.3:
            validation["valid"] = False
            validation["issues"].append("Unbalanced word distribution")
        
        # Check for duplicate words
        all_words = [word for _, word, _ in across_words + down_words]
        word_counts = Counter(all_words)
        duplicates = [word for word, count in word_counts.items() if count > 1]
        if duplicates:
            validation["valid"] = False
            validation["issues"].append(f"Duplicate words: {', '.join(duplicates)}")
        
        # Check for very short words (should be minimal)
        short_words = [word for _, word, _ in across_words + down_words if len(word) <= 2]
        if len(short_words) > 3:
            validation["valid"] = False
            validation["issues"].append(f"Too many short words: {len(short_words)}")
        
        # Check for grid connectivity (no isolated sections)
        if not self._check_grid_connectivity(grid):
            validation["valid"] = False
            validation["issues"].append("Grid has isolated sections")
        
        # Check that all clues have corresponding words
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
        # Find a starting white square
        start_r, start_c = None, None
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if grid[r][c] != '#':
                    start_r, start_c = r, c
                    break
            if start_r is not None:
                break
        
        if start_r is None:
            return False  # No white squares
        
        # Do a flood fill to find all connected white squares
        visited = [[False for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self._flood_fill(grid, visited, start_r, start_c)
        
        # Check if all white squares are visited
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if grid[r][c] != '#' and not visited[r][c]:
                    return False  # Found an unvisited white square
        
        return True
    
    def _flood_fill(self, grid, visited, r, c):
        """Flood fill algorithm to mark connected squares"""
        if r < 0 or r >= self.grid_size or c < 0 or c >= self.grid_size:
            return
        if grid[r][c] == '#' or visited[r][c]:
            return
        
        visited[r][c] = True
        
        # Visit neighbors
        self._flood_fill(grid, visited, r+1, c)
        self._flood_fill(grid, visited, r-1, c)
        self._flood_fill(grid, visited, r, c+1)
        self._flood_fill(grid, visited, r, c-1)
    
    def generate_puzzles(self):
        """Generate the specified number of crossword puzzles"""
        print(f"🔤 CROSSWORD ENGINE V3 - Generating {self.puzzle_count} puzzles")
        print(f"📁 Output directory: {self.puzzles_dir}")
        
        puzzles_data = []
        
        # Generate themes based on difficulty mode
        themes = self._generate_themes()
        
        for i in range(self.puzzle_count):
            puzzle_id = i + 1
            
            # Determine difficulty based on mode
            difficulty = self._get_difficulty_for_puzzle(puzzle_id)
            
            theme = themes[i % len(themes)]
            
            print(f"  Creating puzzle {puzzle_id}/{self.puzzle_count}: {theme} ({difficulty})")
            
            # Generate grid with actual content
            grid = self.generate_grid_with_content(puzzle_id, theme, difficulty)
            
            # Create grid images (empty and filled)
            empty_grid_path, filled_grid_path, clue_positions = self.create_grid_images(grid, puzzle_id)
            
            # Extract words from grid
            across_words, down_words = self.extract_words_from_grid(grid, clue_positions)
            
            # Generate clues
            clues = self.generate_clues(puzzle_id, theme, difficulty, across_words, down_words)
            
            # Validate puzzle
            validation = self.validate_puzzle(grid, across_words, down_words, clues)
            
            if not validation["valid"]:
                print(f"    ⚠️ Puzzle {puzzle_id} has issues: {validation['issues']}")
                # Try to regenerate if invalid
                attempts = 0
                while not validation["valid"] and attempts < 3:
                    attempts += 1
                    print(f"    Regenerating puzzle {puzzle_id} (attempt {attempts})...")
                    
                    grid = self.generate_grid_with_content(puzzle_id, theme, difficulty)
                    empty_grid_path, filled_grid_path, clue_positions = self.create_grid_images(grid, puzzle_id)
                    across_words, down_words = self.extract_words_from_grid(grid, clue_positions)
                    clues = self.generate_clues(puzzle_id, theme, difficulty, across_words, down_words)
                    validation = self.validate_puzzle(grid, across_words, down_words, clues)
                
                if not validation["valid"]:
                    print(f"    ⚠️ Could not generate valid puzzle after {attempts} attempts. Using best effort.")
            
            # Store puzzle data
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
                    "total": len(across_words) + len(down_words)
                },
                "validation": {
                    "valid": validation["valid"],
                    "issues": validation["issues"] if not validation["valid"] else []
                },
                "clue_positions": {f"{r},{c}": num for (r, c), num in clue_positions.items()}
            }
            
            # Save individual puzzle metadata
            puzzle_meta_path = self.metadata_dir / f"puzzle_{puzzle_id:02d}.json"
            with open(puzzle_meta_path, 'w') as f:
                json.dump(puzzle_data, f, indent=2)
            
            puzzles_data.append(puzzle_data)
            
            # Add a small delay to prevent system overload
            time.sleep(0.1)
        
        # Save full puzzle collection metadata
        collection_meta = {
            "puzzle_count": self.puzzle_count,
            "difficulty_mode": self.difficulty_mode,
            "grid_size": self.grid_size,
            "generation_date": datetime.now().isoformat(),
            "puzzles": [p["id"] for p in puzzles_data],
            "validation_summary": {
                "valid_puzzles": sum(1 for p in puzzles_data if p["validation"]["valid"]),
                "invalid_puzzles": sum(1 for p in puzzles_data if not p["validation"]["valid"])
            }
        }
        
        with open(self.metadata_dir / "collection.json", 'w') as f:
            json.dump(collection_meta, f, indent=2)
        
        print(f"✅ Generated {self.puzzle_count} crossword puzzles")
        print(f"📊 Metadata saved to {self.metadata_dir}")
        print(f"🧩 Puzzles saved to {self.puzzles_dir}")
        print(f"🔍 Solutions saved to {self.solutions_dir}")
        
        # Print validation summary
        valid_count = sum(1 for p in puzzles_data if p["validation"]["valid"])
        print(f"✓ Valid puzzles: {valid_count}/{self.puzzle_count}")
        
        if valid_count < self.puzzle_count:
            print(f"⚠️ {self.puzzle_count - valid_count} puzzles have validation issues")
        
        return puzzles_data
    
    def _generate_themes(self):
        """Generate themes based on difficulty mode"""
        themes = [
            # Easy themes
            "Garden Flowers", "Kitchen Tools", "Family Time", "Weather",
            "Colors", "Fruits", "Birds", "Pets", "Seasons", "Numbers",
            "Body Parts", "Clothing", "Breakfast", "Rooms", "Tools",
            "Trees", "Ocean", "Farm", "Music", "Sports",
            
            # Medium themes
            "Classic Movies", "Famous Authors", "World Capitals", "Cooking",
            "Card Games", "Dance", "Gems", "Desserts", "Travel", "Hobbies",
            "Classic Songs", "Wine", "Antiques", "Board Games", "Art",
            "Opera", "Cars", "Radio Shows", "History", "Architecture",
            
            # Hard themes
            "Literature", "Science", "Geography", "Classical Music",
            "Art History", "Cuisine", "Philosophy", "Astronomy",
            "Medicine", "Technology"
        ]
        
        # If we have fewer themes than puzzles, repeat themes
        if len(themes) < self.puzzle_count:
            themes = themes * (self.puzzle_count // len(themes) + 1)
        
        # Shuffle themes if mixed difficulty
        if self.difficulty_mode.lower() == "mixed":
            random.shuffle(themes)
        
        return themes[:self.puzzle_count]
    
    def _get_difficulty_for_puzzle(self, puzzle_id):
        """Determine difficulty for a puzzle based on mode and ID"""
        mode = self.difficulty_mode.lower()
        
        if mode == "easy":
            return "EASY"
        elif mode == "medium":
            return "MEDIUM"
        elif mode == "hard":
            return "HARD"
        else:  # mixed or progressive
            # Progressive difficulty: 40% easy, 40% medium, 20% hard
            if puzzle_id <= int(self.puzzle_count * 0.4):
                return "EASY"
            elif puzzle_id <= int(self.puzzle_count * 0.8):
                return "MEDIUM"
            else:
                return "HARD"

def main():
    """Main entry point for crossword engine"""
    parser = argparse.ArgumentParser(description='Crossword Engine v3 Fixed - Generate high-quality crossword puzzles')
    parser.add_argument('--output', required=True, help='Output directory for puzzles')
    parser.add_argument('--count', type=int, default=50, help='Number of puzzles to generate')
    parser.add_argument('--difficulty', default='mixed', 
                        choices=['easy', 'medium', 'hard', 'mixed'],
                        help='Difficulty level for puzzles')
    parser.add_argument('--grid-size', type=int, default=15, help='Grid size (default: 15x15)')
    parser.add_argument('--word-count', type=int, help='Words per puzzle (optional)')
    parser.add_argument('--max-word-length', type=int, default=15, 
                        help='Maximum word length (default: 15)')
    parser.add_argument('--word-list', help='Path to custom word list file')
    parser.add_argument('--log-level', default='info', 
                        choices=['debug', 'info', 'warning', 'error'],
                        help='Logging level')
    
    args = parser.parse_args()
    
    # Set logging level
    log_level = getattr(logging, args.log_level.upper())
    logger.setLevel(log_level)
    
    try:
        start_time = time.time()
        
        engine = CrosswordEngineV3(
            output_dir=args.output,
            puzzle_count=args.count,
            difficulty=args.difficulty,
            grid_size=args.grid_size,
            word_count=args.word_count,
            max_word_length=args.max_word_length,
            word_list_path=args.word_list
        )
        
        puzzles = engine.generate_puzzles()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n🎯 CROSSWORD ENGINE V3 - SUCCESS")
        print(f"📊 Generated {len(puzzles)} puzzles")
        print(f"⏱️ Time taken: {elapsed_time:.2f} seconds")
        print(f"📁 Output directory: {args.output}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
