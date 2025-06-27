#!/usr/bin/env python3
"""
Enhanced QA Validator v2 - Content-First Validation
Validates the logical and content integrity of generated puzzle books
by analyzing the source JSON metadata.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('EnhancedQAValidator')

class EnhancedQAValidatorV2:
    """
    Performs deep validation of puzzle content based on JSON metadata,
    ensuring logical consistency, word quality, and structural integrity.
    """
    
    def __init__(self, book_dir, output_dir=None, word_list_path=None):
        """Initialize the validator"""
        self.book_dir = Path(book_dir)
        self.metadata_dir = self.book_dir / "metadata"
        
        if not self.metadata_dir.exists():
            raise FileNotFoundError(f"Metadata directory not found: {self.metadata_dir}")
            
        self.output_dir = Path(output_dir) if output_dir else self.book_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "book_directory": str(self.book_dir),
            "overall_status": "PENDING",
            "summary": {
                "total_puzzles": 0,
                "puzzles_passed": 0,
                "puzzles_with_warnings": 0,
                "puzzles_with_critical_issues": 0,
                "critical_issues_count": 0,
                "warnings_count": 0,
                "passed_checks_count": 0,
            },
            "puzzles": {},
            "global_issues": []
        }
        
        self.word_dict = self._load_word_dictionary(word_list_path)
        logger.info(f"Loaded {len(self.word_dict)} words for validation.")

    def _load_word_dictionary(self, word_list_path=None):
        """Load word dictionary from file or use a built-in set."""
        word_dict = set()
        if word_list_path and Path(word_list_path).exists():
            with open(word_list_path, 'r') as f:
                for line in f:
                    word = line.strip().upper()
                    if word.isalpha():
                        word_dict.add(word)
        else:
            # Use a built-in list if no file is provided
            # This list should be reasonably comprehensive for common crosswords
            common_words = [
                "ACE", "ACT", "ADD", "AGE", "AGO", "AID", "AIM", "AIR", "ALL", "AND", "ANY", "ARM", "ART", "ASK", "BAD", "BAG", "BAR", "BAT", "BAY", "BED", "BEE", "BIG", "BIT", "BOX", "BOY", "BUG", "BUS", "BUY", "CAB", "CAP", "CAR", "CAT", "CUT", "DAD", "DAY", "DIE", "DIG", "DOG", "DOT", "DRY", "DUE", "EAR", "EAT", "EGG", "END", "ERA", "EVE", "EYE", "FAN", "FAR", "FEE", "FEW", "FIT", "FIX", "FLY", "FOG", "FOR", "FOX", "FUN", "GAP", "GAS", "GET", "GOD", "GOT", "GUN", "GUY", "GYM", "HAD", "HAT", "HAS", "HAY", "HER", "HID", "HIM", "HIP", "HIS", "HIT", "HOT", "HOW", "HUB", "HUG", "ICE", "ILL", "INK", "INN", "JAM", "JAR", "JET", "JOB", "JOG", "JOY", "KEY", "KID", "KIT", "LAB", "LAD", "LAG", "LAP", "LAW", "LAY", "LEG", "LET", "LID", "LIE", "LIP", "LOG", "LOT", "LOW", "MAP", "MAT", "MAX", "MAY", "MEN", "MET", "MIX", "MOB", "MOM", "MOP", "MUD", "MUG", "NAP", "NET", "NEW", "NIL", "NOR", "NOT", "NOW", "NUT", "OAK", "ODD", "OFF", "OIL", "OLD", "ONE", "OUR", "OUT", "OWL", "OWN", "PAD", "PAN", "PAR", "PAT", "PAW", "PAY", "PEN", "PET", "PIE", "PIG", "PIN", "PIT", "POT", "PRO", "PUT", "RAG", "RAT", "RAW", "RED", "RIB", "RID", "RIG", "RIM", "RIP", "ROD", "ROW", "RUB", "RUG", "RUN", "SAD", "SAG", "SAT", "SAW", "SAY", "SEA", "SEE", "SET", "SEW", "SHE", "SHY", "SIN", "SIP", "SIR", "SIT", "SIX", "SKI", "SKY", "SLY", "SON", "SPA", "SPY", "SUM", "SUN", "TAB", "TAG", "TAP", "TAX", "TEA", "TEN", "THE", "TIE", "TIN", "TIP", "TOE", "TON", "TOP", "TOW", "TOY", "TRY", "TUB", "TWO", "USE", "VAN", "VAT", "VET", "VIA", "WAR", "WAS", "WAX", "WAY", "WEB", "WET", "WHO", "WHY", "WIN", "WON", "YES", "YET", "YOU", "ZOO",
                "ABLE", "ACID", "AGED", "ALSO", "AREA", "ARMY", "AWAY", "BABY", "BACK", "BALL", "BAND", "BANK", "BASE", "BATH", "BEAR", "BEAT", "BEEN", "BEER", "BELL", "BELT", "BEST", "BILL", "BIRD", "BLOW", "BLUE", "BOAT", "BODY", "BOMB", "BOND", "BONE", "BOOK", "BOOM", "BORN", "BOSS", "BOTH", "BOWL", "BULK", "BURN", "BUSH", "BUSY", "CALL", "CALM", "CAME", "CAMP", "CARD", "CARE", "CASE", "CASH", "CAST", "CELL", "CHAT", "CHIP", "CITY", "CLUB", "COAL", "COAT", "CODE", "COLD", "COME", "COOK", "COOL", "COPE", "COPY", "CORE", "COST", "CREW", "CROP", "DARK", "DATA", "DATE", "DAWN", "DAYS", "DEAD", "DEAL", "DEAN", "DEAR", "DEBT", "DEEP", "DENY", "DESK", "DIAL", "DIET", "DIRT", "DISC", "DISK", "DOES", "DONE", "DOOR", "DOSE", "DOWN", "DRAW", "DROP", "DRUG", "DUAL", "DUKE", "DUST", "DUTY", "EACH", "EARN", "EASE", "EAST", "EASY", "EDGE", "ELSE", "EVEN", "EVER", "EVIL", "EXIT", "FACE", "FACT", "FAIL", "FAIR", "FALL", "FARM", "FAST", "FATE", "FEAR", "FEED", "FEEL", "FEET", "FELL", "FELT", "FILE", "FILL", "FILM", "FIND", "FINE", "FIRE", "FIRM", "FISH", "FIVE", "FLAT", "FLOW", "FOOD", "FOOT", "FORD", "FORM", "FORT", "FOUR", "FREE", "FROM", "FUEL", "FULL", "FUND", "GAIN", "GAME", "GATE", "GAVE", "GEAR", "GENE", "GIFT", "GIRL", "GIVE", "GLAD", "GOAL", "GOES", "GOLD", "GOLF", "GONE", "GOOD", "GRAY", "GREW", "GREY", "GROW", "GULF", "HAIR", "HALF", "HALL", "HAND", "HANG", "HARD", "HARM", "HATE", "HAVE", "HEAD", "HEAR", "HEAT", "HELD", "HELL", "HELP", "HERE", "HERO", "HIGH", "HILL", "HIRE", "HOLD", "HOLE", "HOLY", "HOME", "HOPE", "HOST", "HOUR", "HUGE", "HUNG", "HUNT", "HURT", "IDEA", "INCH", "INTO", "IRON", "ITEM", "JACK", "JANE", "JEAN", "JOHN", "JOIN", "JUMP", "JURY", "JUST", "KEEN", "KEEP", "KENT", "KEPT", "KICK", "KILL", "KIND", "KING", "KNEE", "KNEW", "KNOW", "LACK", "LADY", "LAID", "LAKE", "LAND", "LANE", "LAST", "LATE", "LEAD", "LEFT", "LESS", "LIFE", "LIFT", "LIKE", "LINE", "LINK", "LIST", "LIVE", "LOAD", "LOAN", "LOCK", "LOGO", "LONG", "LOOK", "LORD", "LOSE", "LOSS", "LOST", "LOVE", "LUCK", "MADE", "MAIL", "MAIN", "MAKE", "MALE", "MANY", "MARK", "MASS", "MATT", "MEAL", "MEAN", "MEAT", "MEET", "MENU", "MERE", "MIKE", "MILE", "MILK", "MILL", "MIND", "MINE", "MISS", "MODE", "MOOD", "MOON", "MORE", "MOST", "MOVE", "MUCH", "MUST", "NAME", "NAVY", "NEAR", "NECK", "NEED", "NEWS", "NEXT", "NICE", "NICK", "NINE", "NONE", "NOSE", "NOTE", "OKAY", "ONCE", "ONLY", "ONTO", "OPEN", "ORAL", "OVER", "PACE", "PACK", "PAGE", "PAID", "PAIN", "PAIR", "PALM", "PARK", "PART", "PASS", "PAST", "PATH", "PEAK", "PICK", "PINK", "PIPE", "PLAN", "PLAY", "PLOT", "PLUG", "PLUS", "POLL", "POOL", "POOR", "PORT", "POST", "PULL", "PURE", "PUSH", "RACE", "RAIL", "RAIN", "RANK", "RARE", "RATE", "READ", "REAL", "REAR", "RELY", "RENT", "REST", "RICE", "RICH", "RIDE", "RING", "RISE", "RISK", "ROAD", "ROCK", "ROLE", "ROLL", "ROOF", "ROOM", "ROOT", "ROSE", "RULE", "RUSH", "RUTH", "SAFE", "SAID", "SAKE", "SALE", "SALT", "SAME", "SAND", "SAVE", "SEAT", "SEED", "SEEK", "SEEM", "SEEN", "SELF", "SELL", "SEND", "SENT", "SEPT", "SHIP", "SHOP", "SHOT", "SHOW", "SHUT", "SICK", "SIDE", "SIGN", "SITE", "SIZE", "SKIN", "SLIP", "SLOW", "SNOW", "SOFT", "SOIL", "SOLD", "SOLE", "SOME", "SONG", "SOON", "SORT", "SOUL", "SPOT", "STAR", "STAY", "STEP", "STOP", "SUCH", "SUIT", "SURE", "TAKE", "TALE", "TALK", "TALL", "TANK", "TAPE", "TASK", "TEAM", "TECH", "TELL", "TEND", "TERM", "TEST", "TEXT", "THAN", "THAT", "THEM", "THEN", "THEY", "THIN", "THIS", "THUS", "TILL", "TIME", "TINY", "TOLD", "TOLL", "TONE", "TONY", "TOOK", "TOOL", "TOUR", "TOWN", "TREE", "TRIP", "TRUE", "TUNE", "TURN", "TWIN", "TYPE", "UNIT", "UPON", "USED", "USER", "VARY", "VAST", "VERY", "VIEW", "VOTE", "WAGE", "WAIT", "WAKE", "WALK", "WALL", "WANT", "WARD", "WARM", "WASH", "WAVE", "WAYS", "WEAK", "WEAR", "WEEK", "WELL", "WENT", "WERE", "WEST", "WHAT", "WHEN", "WHOM", "WIDE", "WIFE", "WILD", "WILL", "WIND", "WINE", "WING", "WIRE", "WISE", "WISH", "WITH", "WOOD", "WORD", "WORE", "WORK", "YARD", "YEAH", "YEAR", "YOUR", "ZERO", "ZONE",
                "ABOUT", "ABOVE", "ACTOR", "ADMIT", "ADOPT", "AFTER", "AGAIN", "AGENT", "AGREE", "AHEAD", "ALARM", "ALBUM", "ALERT", "ALLOW", "ALONE", "ALONG", "AMONG", "ANGER", "ANGLE", "APPLE", "APPLY", "ARGUE", "ARISE", "ASIDE", "AVOID", "AWARD", "AWARE", "BASIC", "BEACH", "BEGIN", "BELOW", "BLACK", "BLAME", "BLANK", "BLIND", "BLOCK", "BLOOD", "BOARD", "BRAIN", "BREAD", "BREAK", "BRING", "BROWN", "BUILD", "CARRY", "CATCH", "CAUSE", "CHAIN", "CHAIR", "CHART", "CHECK", "CHIEF", "CHILD", "CIVIL", "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLOCK", "COACH", "COAST", "COURT", "COVER", "CREAM", "CRIME", "CROSS", "CROWD", "CYCLE", "DAILY", "DANCE", "DEATH", "DELAY", "DEPTH", "DOUBT", "DRAFT", "DRAMA", "DREAM", "DRESS", "DRINK", "DRIVE", "EARLY", "EARTH", "ENJOY", "ENTER", "EQUAL", "ERROR", "EVENT", "EVERY", "EXACT", "EXIST", "EXTRA", "FAITH", "FAULT", "FIELD", "FIGHT", "FINAL", "FIRST", "FLOOR", "FOCUS", "FORCE", "FORTH", "FOUND", "FRAME", "FRESH", "FRONT", "FRUIT", "FUNNY", "GIANT", "GIVEN", "GLASS", "GLOBE", "GOING", "GRACE", "GRADE", "GRAND", "GRANT", "GRASS", "GREAT", "GREEN", "GROUP", "GUARD", "GUESS", "GUEST", "GUIDE", "HEART", "HEAVY", "HORSE", "HOTEL", "HOUSE", "HUMAN", "IMAGE", "INDEX", "INPUT", "ISSUE", "JOINT", "JUDGE", "KNOWN", "LARGE", "LATER", "LAUGH", "LAYER", "LEARN", "LEAST", "LEAVE", "LEGAL", "LEVEL", "LIGHT", "LIMIT", "LOCAL", "LOGIC", "LUCKY", "LUNCH", "MAJOR", "MAKER", "MATCH", "MAYBE", "MEDIA", "METAL", "MIGHT", "MINOR", "MODEL", "MONEY", "MONTH", "MOTOR", "MOUSE", "MOUTH", "MOVIE", "MUSIC", "NEVER", "NIGHT", "NOISE", "NORTH", "NOVEL", "NURSE", "OCCUR", "OCEAN", "OFFER", "ORDER", "OTHER", "PAINT", "PANEL", "PAPER", "PARTY", "PEACE", "PHONE", "PHOTO", "PIECE", "PLACE", "PLAIN", "PLANE", "PLANT", "PLATE", "POINT", "POUND", "POWER", "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIOR", "PROOF", "PROUD", "PROVE", "QUEEN", "QUICK", "QUIET", "QUITE", "RADIO", "RAISE", "RANGE", "RATIO", "REACH", "READY", "RIGHT", "RIVAL", "RIVER", "ROUGH", "ROUND", "ROUTE", "RURAL", "SCALE", "SCENE", "SCOPE", "SCORE", "SENSE", "SERVE", "SEVEN", "SHALL", "SHAPE", "SHARE", "SHARP", "SHEET", "SHELF", "SHIFT", "SHIRT", "SHOCK", "SHOOT", "SHORT", "SIGHT", "SINCE", "SKILL", "SLEEP", "SMALL", "SMART", "SMILE", "SOLID", "SOLVE", "SORRY", "SOUND", "SOUTH", "SPACE", "SPEAK", "SPEED", "SPEND", "SPORT", "STAFF", "STAGE", "STAND", "START", "STATE", "STEAM", "STEEL", "STICK", "STILL", "STOCK", "STONE", "STORE", "STORY", "STUDY", "STYLE", "SUGAR", "TABLE", "TASTE", "TEACH", "THANK", "THEME", "THERE", "THESE", "THING", "THINK", "THIRD", "THREE", "TIGHT", "TODAY", "TOTAL", "TOUCH", "TOUGH", "TOWER", "TRACK", "TRADE", "TRAIN", "TREAT", "TREND", "TRIAL", "TRUCK", "TRULY", "TRUST", "TRUTH", "TWICE", "UNDER", "UNION", "UNTIL", "UPPER", "URBAN", "USAGE", "USUAL", "VALUE", "VIDEO", "VISIT", "VITAL", "VOICE", "WASTE", "WATCH", "WATER", "WHEEL", "WHERE", "WHICH", "WHILE", "WHITE", "WHOLE", "WOMAN", "WORLD", "WORRY", "WORSE", "WORTH", "WOULD", "WRITE", "WRONG", "YIELD", "YOUNG",
                "PUZZLE", "CROSSWORD", "SOLUTION", "CHALLENGE", "DICTIONARY", "KNOWLEDGE", "QUESTION", "ANSWER"
            ]
            word_dict.update(common_words)
        return word_dict

    def _add_result(self, puzzle_id, level, message):
        """Helper to add a result to the report."""
        if puzzle_id not in self.report["puzzles"]:
            self.report["puzzles"][puzzle_id] = {
                "status": "PASS",
                "critical_issues": [],
                "warnings": [],
                "passed_checks": []
            }
        
        if level == "critical":
            self.report["puzzles"][puzzle_id]["critical_issues"].append(message)
            self.report["puzzles"][puzzle_id]["status"] = "FAIL"
            self.report["summary"]["critical_issues_count"] += 1
        elif level == "warning":
            self.report["puzzles"][puzzle_id]["warnings"].append(message)
            if self.report["puzzles"][puzzle_id]["status"] != "FAIL":
                self.report["puzzles"][puzzle_id]["status"] = "WARN"
            self.report["summary"]["warnings_count"] += 1
        elif level == "pass":
            self.report["puzzles"][puzzle_id]["passed_checks"].append(message)
            self.report["summary"]["passed_checks_count"] += 1

    def validate_book(self):
        """Main method to run all validation checks for the entire book."""
        logger.info(f"Starting validation for book at: {self.book_dir}")
        
        collection_file = self.metadata_dir / "collection.json"
        if not collection_file.exists():
            self.report["global_issues"].append("CRITICAL: collection.json not found.")
            self.finalize_report()
            return self.report

        with open(collection_file, 'r') as f:
            collection_data = json.load(f)
        
        puzzle_ids = collection_data.get("puzzles", [])
        self.report["summary"]["total_puzzles"] = len(puzzle_ids)
        
        if not puzzle_ids:
            self.report["global_issues"].append("CRITICAL: No puzzles listed in collection.json.")
            self.finalize_report()
            return self.report

        for puzzle_id in puzzle_ids:
            self.validate_puzzle(puzzle_id)
            
        self.finalize_report()
        self.save_report()
        return self.report

    def validate_puzzle(self, puzzle_id):
        """Run all validation checks for a single puzzle."""
        puzzle_file = self.metadata_dir / f"puzzle_{puzzle_id:02d}.json"
        if not puzzle_file.exists():
            self._add_result(puzzle_id, "critical", f"Puzzle metadata file not found: {puzzle_file.name}")
            return

        with open(puzzle_file, 'r') as f:
            try:
                puzzle_data = json.load(f)
            except json.JSONDecodeError:
                self._add_result(puzzle_id, "critical", "Invalid JSON in metadata file.")
                return

        # Run checks
        self._validate_metadata_completeness(puzzle_id, puzzle_data)
        self._validate_word_content(puzzle_id, puzzle_data)
        self._validate_word_balance_and_count(puzzle_id, puzzle_data)
        self._validate_for_duplicate_words(puzzle_id, puzzle_data)
        
        # Intersection and connectivity checks are dependent on a valid grid reconstruction
        grid, reconstruction_ok = self._validate_intersections_and_reconstruct_grid(puzzle_id, puzzle_data)
        if reconstruction_ok:
            self._validate_grid_connectivity(puzzle_id, grid)
        else:
            self._add_result(puzzle_id, "critical", "Skipping connectivity check due to grid reconstruction failure.")

    def _validate_metadata_completeness(self, puzzle_id, data):
        """Check if all required metadata fields are present."""
        required_keys = ["id", "theme", "difficulty", "clues", "grid_path", "solution_path", "clue_positions", "word_count"]
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            self._add_result(puzzle_id, "critical", f"Missing required metadata keys: {', '.join(missing_keys)}")
        else:
            self._add_result(puzzle_id, "pass", "All required metadata keys are present.")

    def _validate_word_content(self, puzzle_id, data):
        """Validate that all words in the puzzle are in the dictionary."""
        clues = data.get("clues", {})
        all_words = clues.get("across", []) + clues.get("down", [])
        
        invalid_words = []
        for clue_data in all_words:
            if len(clue_data) < 3:
                self._add_result(puzzle_id, "critical", f"Malformed clue data: {clue_data}")
                continue
            word = clue_data[2]
            if word not in self.word_dict:
                invalid_words.append(word)
        
        if invalid_words:
            self._add_result(puzzle_id, "critical", f"Contains invalid/unknown words: {', '.join(invalid_words)}")
        else:
            self._add_result(puzzle_id, "pass", "All words are valid.")

    def _validate_word_balance_and_count(self, puzzle_id, data):
        """Check for a reasonable balance between across and down words."""
        word_count = data.get("word_count", {})
        across_count = word_count.get("across", 0)
        down_count = word_count.get("down", 0)
        total_count = word_count.get("total", 0)

        if total_count < 20:
            self._add_result(puzzle_id, "critical", f"Too few words in puzzle: {total_count} (min 20)")
        else:
            self._add_result(puzzle_id, "pass", f"Sufficient word count: {total_count}")

        if total_count > 0:
            across_ratio = across_count / total_count
            down_ratio = down_count / total_count
            if across_ratio < 0.3 or down_ratio < 0.3:
                self._add_result(puzzle_id, "warning", f"Poor word balance: {across_count} across, {down_count} down")
            else:
                self._add_result(puzzle_id, "pass", "Good word balance.")

    def _validate_for_duplicate_words(self, puzzle_id, data):
        """Check for any duplicate words within the same puzzle."""
        clues = data.get("clues", {})
        all_words = [item[2] for item in clues.get("across", []) + clues.get("down", []) if len(item) > 2]
        
        counts = Counter(all_words)
        duplicates = [word for word, count in counts.items() if count > 1]
        
        if duplicates:
            self._add_result(puzzle_id, "critical", f"Duplicate words found: {', '.join(duplicates)}")
        else:
            self._add_result(puzzle_id, "pass", "No duplicate words.")

    def _validate_intersections_and_reconstruct_grid(self, puzzle_id, data):
        """Reconstruct the grid and validate all word intersections."""
        clues = data.get("clues", {})
        clue_positions = data.get("clue_positions", {})
        if not clues or not clue_positions:
            self._add_result(puzzle_id, "critical", "Missing clues or clue_positions for intersection check.")
            return None, False

        grid_size = 15 # Assuming fixed size for now
        grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Invert clue_positions for easier lookup
        pos_to_num = {v: k for k, v in clue_positions.items()}

        all_clues = [("across", item) for item in clues.get("across", [])] + \
                    [("down", item) for item in clues.get("down", [])]

        intersection_errors = []

        for direction, (num, _, word) in all_clues:
            pos_str = pos_to_num.get(num)
            if not pos_str:
                intersection_errors.append(f"No position found for clue {direction} {num}")
                continue
            
            r_start, c_start = map(int, pos_str.split(','))

            for i, letter in enumerate(word):
                if direction == "across":
                    r, c = r_start, c_start + i
                else: # down
                    r, c = r_start + i, c_start

                if r >= grid_size or c >= grid_size:
                    intersection_errors.append(f"Word '{word}' ({direction} {num}) goes out of bounds.")
                    break
                
                if grid[r][c] == '':
                    grid[r][c] = letter
                elif grid[r][c] != letter:
                    error_msg = (f"Intersection conflict at ({r},{c}) for word '{word}' ({direction} {num}). "
                                 f"Grid has '{grid[r][c]}', word has '{letter}'.")
                    intersection_errors.append(error_msg)
        
        if intersection_errors:
            for error in intersection_errors:
                self._add_result(puzzle_id, "critical", error)
            return grid, False
        else:
            self._add_result(puzzle_id, "pass", "All word intersections are valid.")
            return grid, True

    def _validate_grid_connectivity(self, puzzle_id, grid):
        """Check if all white squares in the grid are connected."""
        if not grid:
            return

        grid_size = len(grid)
        white_squares = set()
        for r in range(grid_size):
            for c in range(grid_size):
                if grid[r][c]:
                    white_squares.add((r, c))

        if not white_squares:
            self._add_result(puzzle_id, "warning", "Grid appears to be empty or all black squares.")
            return
            
        q = [next(iter(white_squares))]
        visited = {q[0]}

        while q:
            r, c = q.pop(0)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in white_squares and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        
        if len(visited) != len(white_squares):
            unreachable_count = len(white_squares) - len(visited)
            self._add_result(puzzle_id, "critical", f"Grid has {unreachable_count} unreachable/isolated squares.")
        else:
            self._add_result(puzzle_id, "pass", "Grid is fully connected.")

    def finalize_report(self):
        """Calculate final summary stats for the report."""
        for puzzle_id, results in self.report["puzzles"].items():
            if results["status"] == "FAIL":
                self.report["summary"]["puzzles_with_critical_issues"] += 1
            elif results["status"] == "WARN":
                self.report["summary"]["puzzles_with_warnings"] += 1
            else:
                self.report["summary"]["puzzles_passed"] += 1
        
        if self.report["summary"]["critical_issues_count"] > 0 or self.report["global_issues"]:
            self.report["overall_status"] = "FAIL"
        elif self.report["summary"]["warnings_count"] > 0:
            self.report["overall_status"] = "WARN"
        else:
            self.report["overall_status"] = "PASS"

    def save_report(self):
        """Save the final validation report to a JSON file."""
        report_filename = f"ENHANCED_QA_REPORT_{self.book_dir.name}.json"
        report_path = self.output_dir / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        logger.info(f"✅ Enhanced QA report saved to: {report_path}")

def main():
    """Main entry point for the enhanced QA validator."""
    parser = argparse.ArgumentParser(description='Enhanced QA Validator v2 - Content-First Puzzle Validation')
    parser.add_argument('book_dir', help='Path to the book directory containing the metadata folder.')
    parser.add_argument('--output-dir', help='Directory to save the QA report (defaults to book_dir).')
    parser.add_argument('--word-list', help='Path to a custom word list file for validation.')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'], help='Set the logging level.')
    
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level.upper()))
    
    try:
        validator = EnhancedQAValidatorV2(
            book_dir=args.book_dir,
            output_dir=args.output_dir,
            word_list_path=args.word_list
        )
        report = validator.validate_book()
        
        print("\n--- Enhanced QA Validation Summary ---")
        print(f"Overall Status: {report['overall_status']}")
        print(f"  - Total Puzzles: {report['summary']['total_puzzles']}")
        print(f"  - Passed: {report['summary']['puzzles_passed']}")
        print(f"  - Warnings: {report['summary']['puzzles_with_warnings']}")
        print(f"  - Critical Issues: {report['summary']['puzzles_with_critical_issues']}")
        print("-" * 36)
        
        if report['overall_status'] != "PASS":
            print("Review the generated JSON report for detailed issues.")
            return 1
        else:
            print("All puzzles passed validation successfully.")
            return 0
            
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
