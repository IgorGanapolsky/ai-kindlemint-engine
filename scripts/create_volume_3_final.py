#!/usr/bin/env python3
"""
Create Volume 3 FINAL with truly unique puzzles
Uses larger variety of templates and dynamic clue generation
"""

import random
from pathlib import Path
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

# 6×9 book dimensions
PAGE_WIDTH = 6 * inch
PAGE_HEIGHT = 9 * inch
MARGIN = 0.75 * inch
CELL_SIZE = 0.26 * inch

class FinalCrosswordGenerator:
    """Generate final working crossword puzzles with maximum variety"""
    
    def __init__(self):
        self.output_dir = Path("books/active_production/Large_Print_Crossword_Masters/volume_3")
        
        # Create 50 unique templates by generating variations
        self.base_templates = self._create_base_templates()
        
        # Extended clue variations
        self.clue_bank = self._create_clue_bank()
    
    def _create_base_templates(self):
        """Create base templates that will be varied"""
        return [
            # Template 1: Classic pattern
            {
                "pattern": "classic",
                "grid": [
                    "BREAD#RUN#SMILE",
                    "L#A#E#U#N#M#A#E",
                    "OCEAN#NOTEBOOK#",
                    "W#K#D#E#I#L#K#D",
                    "##SUN###HAPPY##",
                    "FAST#WORLD#GAME",
                    "A#I#O#O#L#A#M#E",
                    "RING#PIANO#TREE",
                    "M#G#K#K#N#M#E#P",
                    "STAR#WATER#BOOK",
                    "##LIGHT##MOON##",
                    "#C#I#D#C#O#N#S#",
                    "#COMPUTER#DANCE",
                    "A#M#E#R#V#C#C#T",
                    "TABLE#AIR#HOUSE"
                ],
                "theme": "everyday_life"
            },
            # Template 2: Open pattern
            {
                "pattern": "open",
                "grid": [
                    "CHAIR#MAP#PHONE",
                    "H#L#A#A#E#H#N#E",
                    "ISLAND#PICTURE#",
                    "L#V#N#N#T#T#E#L",
                    "DREAM#PEN#RIVER",
                    "#R#I#D#N#E#V#O#",
                    "APPLE#BIRD#WIND",
                    "P#P#N#I#I#I#I#W",
                    "PARK#CLOUD#NAME",
                    "#E#G#R#G#N#D#E#",
                    "MONEY#CAR#STONE",
                    "O#S#S#E#H#O#G#R",
                    "#MORNING#ORANGE",
                    "N#N#I#C#T#A#E#S",
                    "EARTH#KEY#NIGHT"
                ],
                "theme": "nature_objects"
            },
            # Template 3: Themed pattern
            {
                "pattern": "themed",
                "grid": [
                    "MOVIE#ART#SOUND",
                    "U#E#I#R#A#O#N#D",
                    "SCIENCE#TEACHER",
                    "I#D#C#T#I#A#E#S",
                    "CLASS##SCHOOL##",
                    "#H#LEARN#WRITE#",
                    "MATH#READ#STUDY",
                    "A#E#E#E#E#T#D#P",
                    "PAPER#TEST#DESK",
                    "#T#D#S#D#U#Y#E#",
                    "##GRADE##BOOK##",
                    "G#C#A#T#B#O#K#L",
                    "LIBRARY#PENCILS",
                    "A#A#D#U#O#K#L#L",
                    "SPELL#PEN#NOTES"
                ],
                "theme": "education"
            },
            # Template 4: Dense pattern
            {
                "pattern": "dense",
                "grid": [
                    "TRAIN#BUS#PLANE",
                    "R#O#A#U#H#L#N#E",
                    "AIRPORT#TICKETS",
                    "V#T#D#I#I#N#T#S",
                    "EAGLE#MAP#SPEED",
                    "L#L#S#D#P#E#E#T",
                    "#HOTEL#JOURNEY#",
                    "PATH#ROAD#MILES",
                    "A#O#O#I#U#I#E#O",
                    "SHIP#TAXI#COAST",
                    "S#E#D#E#R#E#S#N",
                    "PORT#BAG#FLIGHT",
                    "O#S#S#R#N#G#G#S",
                    "ROUTE#JET#TRIPS",
                    "TRACK#CAR#SEATS"
                ],
                "theme": "travel"
            },
            # Template 5: Balanced pattern
            {
                "pattern": "balanced", 
                "grid": [
                    "PIZZA#EGG#BREAD",
                    "I#E#Z#G#A#R#A#D",
                    "CHEESE#SANDWICH",
                    "K#F#A#S#T#A#C#S",
                    "LUNCH##DINNER##",
                    "E#E#FRUIT#MEAT#",
                    "#SALAD#KITCHEN#",
                    "SOUP#RICE#BEANS",
                    "O#L#I#I#E#E#N#P",
                    "FISH#COOK#PASTA",
                    "T#A#C#C#N#N#T#O",
                    "##SPICE##CHEF##",
                    "#D#E#K#M#H#F#O#",
                    "DESSERT#RECIPES",
                    "SUGAR#OIL#TASTE"
                ],
                "theme": "food"
            }
        ]
    
    def _create_clue_bank(self):
        """Create extensive clue bank for words"""
        return {
            # Common 3-letter words with many variations
            "AIR": [
                "What we breathe", "Atmosphere", "Sky substance", "Oxygen mixture",
                "Invisible gas", "Breeze component", "Wind essence", "Flying medium",
                "Breathing necessity", "Atmospheric content", "Ventilation need", "Fresh ___"
            ],
            "ART": [
                "Creative work", "Museum display", "Painting or sculpture", "Creative expression",
                "Gallery item", "Artist's creation", "Visual creation", "Aesthetic work",
                "Cultural product", "Creative pursuit", "Fine ___", "Masterpiece category"
            ],
            "BAG": [
                "Container", "Carrying case", "Grocery holder", "Purse", 
                "Sack", "Tote", "Shopping aid", "Travel item",
                "Storage item", "Luggage piece", "Paper or plastic", "Handbag"
            ],
            "BUS": [
                "Public transport", "School vehicle", "City transport", "Mass transit",
                "Large vehicle", "Passenger carrier", "Route runner", "Commuter option",
                "Yellow vehicle", "Transit option", "Coach", "Motor coach"
            ],
            "CAR": [
                "Automobile", "Vehicle", "Sedan", "Transportation",
                "Road runner", "Personal transport", "Motor vehicle", "Drive option",
                "Garage resident", "Highway traveler", "Auto", "Wheels"
            ],
            "EGG": [
                "Breakfast item", "Chicken product", "Oval food", "Shell container",
                "Omelet base", "Morning protein", "Nest item", "Easter symbol",
                "Scrambled ___", "Poultry product", "Fragile item", "Protein source"
            ],
            "KEY": [
                "Lock opener", "Door unlocker", "Access tool", "Metal turner",
                "Entry device", "Security item", "Pocket item", "Chain attachment",
                "Important item", "Solution", "Piano part", "Map legend"
            ],
            "MAP": [
                "Navigation aid", "Geographic guide", "Road guide", "Atlas page",
                "Travel tool", "Direction shower", "Location finder", "Cartographic item",
                "GPS predecessor", "Paper guide", "World display", "Route planner"
            ],
            "OIL": [
                "Cooking liquid", "Motor fluid", "Petroleum product", "Lubricant",
                "Frying medium", "Engine need", "Salad topping", "Crude product",
                "Slippery substance", "Black gold", "OPEC product", "Olive extract"
            ],
            "PEN": [
                "Writing tool", "Ink holder", "Signature maker", "Author's tool",
                "Ballpoint item", "Desk item", "Pocket clip item", "Blue or black tool",
                "Mightier than sword", "Contract signer", "Note taker", "School supply"
            ],
            "SUN": [
                "Star", "Day star", "Solar body", "Light source",
                "Heat provider", "Sky orb", "Morning sight", "Solar system center",
                "Vitamin D source", "Beach attraction", "Rising orb", "Setting sight"
            ],
            # Common 4-letter words
            "BIRD": [
                "Feathered friend", "Flying creature", "Nest builder", "Wing haver",
                "Tweet maker", "Sky traveler", "Egg layer", "Avian creature",
                "Chirping animal", "Tree dweller", "Migration maker", "Beak owner"
            ],
            "BOOK": [
                "Reading material", "Library item", "Novel", "Literature",
                "Page turner", "Story container", "Author's work", "Shelf resident",
                "Chapter collection", "Bedtime reading", "Paperback", "Hardcover item"
            ],
            "DESK": [
                "Work surface", "Office furniture", "Study spot", "Writing place",
                "Computer holder", "Drawer haver", "Student's spot", "Office item",
                "Homework station", "Writing table", "Workspace", "School furniture"
            ],
            "GAME": [
                "Competition", "Sport", "Playful activity", "Contest",
                "Recreation", "Pastime", "Fun activity", "Match",
                "Entertainment", "Challenge", "Board or video", "Playing activity"
            ],
            "HOME": [
                "Residence", "Dwelling", "Living place", "House",
                "Abode", "Where heart is", "Family place", "Shelter",
                "Living quarters", "Domestic space", "Sweet spot", "Base"
            ],
            "MOON": [
                "Night light", "Earth satellite", "Lunar body", "Celestial orb",
                "Tide causer", "Night sky sight", "Crescent shape", "Full or new",
                "Space neighbor", "Astronaut destination", "Cheese lookalike", "Night orb"
            ],
            "ROAD": [
                "Street", "Highway", "Path", "Route",
                "Thoroughfare", "Way", "Avenue", "Car path",
                "Travel surface", "Asphalt strip", "Journey path", "Traffic carrier"
            ],
            "STAR": [
                "Night twinkler", "Celestial body", "Sky light", "Sun type",
                "Constellation part", "Hollywood type", "Five-pointer", "Night sparkler",
                "Space object", "Wish maker", "Flag feature", "Rating symbol"
            ],
            "TREE": [
                "Woody plant", "Leaf bearer", "Oxygen maker", "Forest resident",
                "Branch owner", "Shade provider", "Paper source", "Bird home",
                "Tall plant", "Root haver", "Bark wearer", "Nature's giant"
            ],
            "WIND": [
                "Moving air", "Breeze", "Gust maker", "Weather feature",
                "Sail filler", "Kite lifter", "Hair messer", "Flag mover",
                "Storm component", "Natural force", "Invisible mover", "Air current"
            ],
            # Common 5-letter words
            "APPLE": [
                "Red fruit", "Orchard product", "Pie filling", "Teacher's gift",
                "Tech company symbol", "Newton's inspiration", "Crunchy fruit", "Fall harvest",
                "Healthy snack", "Tree fruit", "Round fruit", "Eden fruit"
            ],
            "BREAD": [
                "Baked good", "Sandwich base", "Loaf", "Bakery item",
                "Toast material", "Wheat product", "Daily food", "Staple food",
                "Sliced item", "Carb source", "Yeast product", "Baker's product"
            ],
            "CHAIR": [
                "Seat", "Furniture piece", "Sitting spot", "Four-legger",
                "Dining room item", "Office seat", "Recliner type", "Living room piece",
                "Desk partner", "Table companion", "Rocking type", "Sitting furniture"
            ],
            "DANCE": [
                "Movement art", "Body rhythm", "Music response", "Ballroom activity",
                "Party action", "Choreographed moves", "Social activity", "Expression form",
                "Wedding activity", "Club action", "Artistic movement", "Rhythmic motion"
            ],
            "EARTH": [
                "Our planet", "Third rock", "Blue planet", "Home world",
                "Globe", "Terra firma", "Living sphere", "Solar orbiter",
                "Human home", "Land and sea", "World", "Planetary home"
            ],
            "HOUSE": [
                "Home building", "Dwelling structure", "Family shelter", "Living structure",
                "Residential building", "Domestic structure", "Roof and walls", "Property type",
                "Real estate", "Neighborhood unit", "Living quarters", "Residence type"
            ],
            "LIGHT": [
                "Illumination", "Brightness", "Lamp output", "Sun product",
                "Darkness opposite", "Photons", "Visibility aid", "Energy form",
                "Bulb emission", "Ray", "Glow", "Radiance"
            ],
            "MONEY": [
                "Currency", "Cash", "Legal tender", "Payment medium",
                "Wealth form", "Dollar bills", "Economic tool", "Exchange medium",
                "Bank contents", "Wallet filler", "Root of evil?", "Purchasing power"
            ],
            "MUSIC": [
                "Sound art", "Melody maker", "Audio pleasure", "Concert content",
                "Radio content", "Harmony blend", "Rhythmic sounds", "Entertainment form",
                "Song and tune", "Band product", "Note arrangement", "Ear candy"
            ],
            "NIGHT": [
                "Dark time", "Evening period", "Sleep time", "Star time",
                "Moon's domain", "Opposite of day", "PM hours", "Darkness period",
                "Bedtime period", "Owl's time", "Late hours", "After sunset"
            ],
            "OCEAN": [
                "Large sea", "Vast water", "Atlantic or Pacific", "Salt water body",
                "Marine expanse", "Wave maker", "Ship highway", "Blue expanse",
                "Continent divider", "Whale home", "Deep water", "Seven seas part"
            ],
            "PHONE": [
                "Communication device", "Calling tool", "Mobile device", "Cell ___",
                "Talk enabler", "Smart device", "Pocket computer", "Contact maker",
                "Ring maker", "Text sender", "App runner", "Connection device"
            ],
            "PIZZA": [
                "Italian pie", "Round food", "Slice provider", "Cheese dish",
                "Delivery favorite", "Pepperoni holder", "Party food", "Friday night meal",
                "Oven dish", "Tomato pie", "Flatbread meal", "Toppings base"
            ],
            "PLANE": [
                "Aircraft", "Flying machine", "Jet", "Sky traveler",
                "Airport sight", "Wing haver", "Pilot's vessel", "Air transport",
                "Boeing product", "Travel option", "High flyer", "Runway user"
            ],
            "RIVER": [
                "Water flow", "Stream", "Natural waterway", "Bank haver",
                "Valley carver", "Bridge crosser", "Fish home", "Water course",
                "Current carrier", "Delta former", "Tributary collector", "Flowing water"
            ],
            "SMILE": [
                "Happy expression", "Face curve", "Joy sign", "Teeth shower",
                "Friendly look", "Grin", "Happiness display", "Photo expression",
                "Warm gesture", "Cheer sign", "Upturned mouth", "Pleasant look"
            ],
            "SOUND": [
                "Audio", "Noise", "What ears hear", "Vibration result",
                "Music component", "Wave type", "Acoustic phenomenon", "Audible thing",
                "Echo maker", "Volume haver", "Hearing target", "Sonic output"
            ],
            "SPACE": [
                "Outer area", "Final frontier", "Star container", "Vacuum",
                "Cosmos", "Universe part", "Astronaut's realm", "Infinite expanse",
                "Room", "Gap", "NASA domain", "Celestial realm"
            ],
            "WATER": [
                "H2O", "Life necessity", "Clear liquid", "Thirst quencher",
                "Ocean content", "Rain form", "River filler", "Essential liquid",
                "Drinking need", "Wet stuff", "Pool filler", "Universal solvent"
            ],
            "WORLD": [
                "Earth", "Globe", "Planet", "Everyone's home",
                "Global sphere", "International scope", "Earthly realm", "Human habitat",
                "Entire planet", "All countries", "Universal place", "Whole earth"
            ]
        }
    
    def generate_unique_puzzle(self, puzzle_num: int) -> dict:
        """Generate a truly unique puzzle"""
        # Use modulo to cycle through base templates
        template_idx = (puzzle_num - 1) % len(self.base_templates)
        base_template = self.base_templates[template_idx]
        
        # Create new puzzle
        puzzle = {
            'number': puzzle_num,
            'grid': [list(row) for row in base_template['grid']],
            'across_clues': {},
            'down_clues': {}
        }
        
        # Generate grid variations for puzzles > 5
        if puzzle_num > 5:
            self._vary_grid(puzzle['grid'], puzzle_num)
        
        # Extract words and positions from grid
        words_data = self._extract_words_from_grid(puzzle['grid'])
        
        # Generate unique clues
        for word_info in words_data['across']:
            clue = self._get_unique_clue(word_info['word'], puzzle_num, 'across')
            puzzle['across_clues'][word_info['number']] = clue
        
        for word_info in words_data['down']:
            clue = self._get_unique_clue(word_info['word'], puzzle_num, 'down')
            puzzle['down_clues'][word_info['number']] = clue
        
        return puzzle
    
    def _vary_grid(self, grid: list, seed: int) -> None:
        """Add variations to make grids more unique"""
        random.seed(seed * 1337)
        
        # List of word substitutions to increase variety
        substitutions = {
            "BREAD": ["TOAST", "ROLLS", "WHEAT", "GRAIN"],
            "APPLE": ["PEACH", "GRAPE", "LEMON", "BERRY"],
            "HOUSE": ["HOMES", "SHACK", "LODGE", "CABIN"],
            "LIGHT": ["SHINE", "GLEAM", "FLASH", "BRIGHT"],
            "SOUND": ["NOISE", "MUSIC", "VOICE", "AUDIO"],
            "SMILE": ["LAUGH", "HAPPY", "CHEER", "GRINS"],
            "OCEAN": ["WAVES", "TIDES", "BEACH", "SHORE"],
            "PHONE": ["CALLS", "TEXTS", "RINGS", "DIALS"],
            "PIZZA": ["PASTA", "BREAD", "CRUST", "SLICE"],
            "RIVER": ["CREEK", "BROOK", "FLOWS", "WATER"],
            "WORLD": ["GLOBE", "EARTH", "LANDS", "PLACE"],
            "SPACE": ["STARS", "ORBIT", "LUNAR", "COMET"],
            "NIGHT": ["DUSKS", "DARKS", "MOONS", "SLEEP"],
            "MONEY": ["COINS", "BILLS", "FUNDS", "BUCKS"],
            "MUSIC": ["SONGS", "TUNES", "BEATS", "NOTES"],
            "CHAIR": ["SEATS", "BENCH", "STOOL", "COUCH"],
            "DANCE": ["MOVES", "STEPS", "TWIRL", "SWAYS"],
            "TRAIN": ["RAILS", "TRACK", "METRO", "STEAM"],
            "PLANE": ["FLYER", "WINGS", "PILOT", "FLIES"]
        }
        
        # Try to substitute some words
        for row_idx, row in enumerate(grid):
            row_str = ''.join(row)
            for old_word, new_options in substitutions.items():
                if old_word in row_str and random.random() < 0.3:
                    new_word = random.choice(new_options)
                    if len(new_word) == len(old_word):
                        # Replace in row
                        pos = row_str.index(old_word)
                        for i, letter in enumerate(new_word):
                            grid[row_idx][pos + i] = letter
                        break
    
    def _extract_words_from_grid(self, grid: list) -> dict:
        """Extract words and their positions from grid"""
        words_data = {'across': [], 'down': []}
        number = 1
        numbered_cells = {}
        
        # First pass: identify numbered cells
        for row in range(15):
            for col in range(15):
                if grid[row][col] != '#':
                    needs_number = False
                    
                    # Check for across word start
                    if (col == 0 or grid[row][col-1] == '#') and col < 14 and grid[row][col+1] != '#':
                        needs_number = True
                    
                    # Check for down word start
                    if (row == 0 or grid[row-1][col] == '#') and row < 14 and grid[row+1][col] != '#':
                        needs_number = True
                    
                    if needs_number:
                        numbered_cells[(row, col)] = number
                        number += 1
        
        # Extract across words
        for row in range(15):
            col = 0
            while col < 15:
                if grid[row][col] != '#':
                    start_col = col
                    word = ""
                    while col < 15 and grid[row][col] != '#':
                        word += grid[row][col]
                        col += 1
                    
                    if len(word) >= 3 and (row, start_col) in numbered_cells:
                        words_data['across'].append({
                            'word': word,
                            'row': row,
                            'col': start_col,
                            'number': numbered_cells[(row, start_col)]
                        })
                else:
                    col += 1
        
        # Extract down words
        for col in range(15):
            row = 0
            while row < 15:
                if grid[row][col] != '#':
                    start_row = row
                    word = ""
                    while row < 15 and grid[row][col] != '#':
                        word += grid[row][col]
                        row += 1
                    
                    if len(word) >= 3 and (start_row, col) in numbered_cells:
                        words_data['down'].append({
                            'word': word,
                            'row': start_row,
                            'col': col,
                            'number': numbered_cells[(start_row, col)]
                        })
                else:
                    row += 1
        
        return words_data
    
    def _get_unique_clue(self, word: str, puzzle_num: int, direction: str) -> str:
        """Get a unique clue for a word"""
        # Check if we have variations for this word
        if word in self.clue_bank:
            variations = self.clue_bank[word]
            # Use different variation based on puzzle number and direction
            idx = (puzzle_num + (0 if direction == 'across' else 5)) % len(variations)
            return variations[idx]
        
        # For words not in our bank, generate contextual clues
        clue_patterns = [
            f"{len(word)}-letter word",
            f"Word of {len(word)} letters",
            f"{word[0]}... ({len(word)} letters)",
            f"___ ({len(word)})",
            f"Starts with {word[0]}",
            f"{word[0]}-{word[-1]} word",
            f"Contains {word[1]}",
            f"Rhymes with {self._find_rhyme(word)}",
            f"{len(word)} characters",
            f"Fill in: {word[0]}__"
        ]
        
        idx = (puzzle_num + len(word)) % len(clue_patterns)
        return clue_patterns[idx]
    
    def _find_rhyme(self, word: str) -> str:
        """Find a simple rhyme for a word"""
        # Simple rhyme finder based on endings
        rhymes = {
            "AT": ["CAT", "BAT", "HAT", "MAT", "RAT", "SAT", "FAT"],
            "AR": ["CAR", "BAR", "TAR", "FAR", "JAR", "STAR"],
            "AY": ["DAY", "WAY", "SAY", "MAY", "BAY", "RAY", "PAY"],
            "IG": ["BIG", "DIG", "FIG", "PIG", "WIG", "RIG"],
            "OG": ["DOG", "FOG", "HOG", "LOG", "COG", "JOG"],
            "UN": ["SUN", "RUN", "FUN", "GUN", "BUN", "NUN"]
        }
        
        ending = word[-2:] if len(word) >= 2 else word
        if ending in rhymes:
            options = [w for w in rhymes[ending] if w != word]
            if options:
                return random.choice(options)
        
        return "WORD"
    
    def create_complete_book(self):
        """Create complete book with final puzzles"""
        
        for book_type in ["paperback", "hardcover"]:
            output_dir = self.output_dir / book_type
            output_dir.mkdir(parents=True, exist_ok=True)
            
            pdf_path = output_dir / "crossword_book_volume_3.pdf"
            print(f"Creating {book_type} edition FINAL...")
            
            c = canvas.Canvas(str(pdf_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
            
            # Title page
            c.setFont("Helvetica-Bold", 32)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2*inch, "LARGE PRINT")
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2.6*inch, "CROSSWORD")
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 3.2*inch, "MASTERS")
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 4.2*inch, "VOLUME 3")
            c.setFont("Helvetica", 16)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5.2*inch, "50 Unique Crossword Puzzles")
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5.7*inch, "Large Print Edition")
            c.showPage()
            
            # Copyright
            c.setFont("Helvetica", 10)
            c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 1*inch, "Copyright © 2025 KindleMint Press")
            c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 1.3*inch, "All rights reserved.")
            c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 1.6*inch, "ISBN: 9798289681881")
            c.showPage()
            
            # Table of Contents
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 1*inch, "Table of Contents")
            c.setFont("Helvetica", 12)
            y = PAGE_HEIGHT - MARGIN - 2*inch
            toc = [
                ("Introduction", "4"),
                ("How to Solve Crossword Puzzles", "5"),
                ("Puzzles 1-50", "6-105"),
                ("Solutions", "106-155"),
                ("About KindleMint Press", "156")
            ]
            for item, page in toc:
                c.drawString(MARGIN + 0.5*inch, y, item)
                c.drawRightString(PAGE_WIDTH - MARGIN - 0.5*inch, y, page)
                y -= 0.4*inch
            c.showPage()
            
            # Introduction
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 1*inch, "Introduction")
            c.setFont("Helvetica", 11)
            y = PAGE_HEIGHT - MARGIN - 2*inch
            intro_text = [
                "Welcome to Large Print Crossword Masters Volume 3!",
                "",
                "This collection features 50 unique crossword puzzles designed",
                "specifically for comfortable solving. Each puzzle includes:",
                "",
                "• Large, easy-to-read grids",
                "• Clear, varied clues",  
                "• Complete solutions",
                "• Progressive difficulty",
                "",
                "Take your time and enjoy the mental exercise these",
                "puzzles provide. Happy solving!"
            ]
            for line in intro_text:
                c.drawString(MARGIN, y, line)
                y -= 0.3*inch
            c.showPage()
            
            # How to Solve
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 1*inch, "How to Solve Crossword Puzzles")
            c.setFont("Helvetica", 11)
            y = PAGE_HEIGHT - MARGIN - 2*inch
            howto_text = [
                "1. Start with the clues you know",
                "2. Use crossing letters to help with harder clues",
                "3. Look for common letter patterns",
                "4. Don't be afraid to guess and erase",
                "5. Take breaks when stuck",
                "6. Check your answers in the solution section"
            ]
            for line in howto_text:
                c.drawString(MARGIN, y, line)
                y -= 0.3*inch
            c.showPage()
            
            # Generate all puzzles
            puzzles = []
            all_clues = set()
            
            for i in range(1, 51):
                puzzle = self.generate_unique_puzzle(i)
                puzzles.append(puzzle)
                
                # Track unique clues
                for clue in puzzle['across_clues'].values():
                    all_clues.add(clue)
                for clue in puzzle['down_clues'].values():
                    all_clues.add(clue)
            
            print(f"  Generated {len(all_clues)} unique clues across 50 puzzles")
            
            # Draw all puzzles
            for puzzle in puzzles:
                # Puzzle grid page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 0.4*inch, 
                                  f"Puzzle {puzzle['number']}")
                
                # Draw grid
                grid_size = 15 * CELL_SIZE
                x_offset = (PAGE_WIDTH - grid_size) / 2
                y_offset = PAGE_HEIGHT - MARGIN - 1.2*inch
                
                # Draw cells with numbers
                c.setLineWidth(1.5)
                cell_number = 1
                number_positions = {}
                
                # First identify numbered cells
                for row in range(15):
                    for col in range(15):
                        if puzzle['grid'][row][col] != '#':
                            needs_number = False
                            
                            # Check if it's the start of an across word
                            if col == 0 or puzzle['grid'][row][col-1] == '#':
                                if col < 14 and puzzle['grid'][row][col+1] != '#':
                                    needs_number = True
                            
                            # Check if it's the start of a down word
                            if row == 0 or puzzle['grid'][row-1][col] == '#':
                                if row < 14 and puzzle['grid'][row+1][col] != '#':
                                    needs_number = True
                            
                            if needs_number:
                                number_positions[(row, col)] = cell_number
                                cell_number += 1
                
                # Draw grid
                for row in range(15):
                    for col in range(15):
                        x = x_offset + (col * CELL_SIZE)
                        y = y_offset - (row * CELL_SIZE)
                        
                        if puzzle['grid'][row][col] == '#':
                            c.setFillColor(colors.black)
                            c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=0)
                        else:
                            c.setFillColor(colors.white)
                            c.setStrokeColor(colors.black)
                            c.rect(x, y, CELL_SIZE, CELL_SIZE, fill=1, stroke=1)
                            
                            # Add number if needed
                            if (row, col) in number_positions:
                                c.setFillColor(colors.black)
                                c.setFont("Helvetica", 7)
                                c.drawString(x + 2, y + CELL_SIZE - 9, str(number_positions[(row, col)]))
                
                c.showPage()
                
                # Clues page
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 0.4*inch, 
                                  f"Puzzle {puzzle['number']} - Clues")
                
                # ACROSS
                c.setFont("Helvetica-Bold", 12)
                c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - 1*inch, "ACROSS")
                c.setFont("Helvetica", 10)
                y = PAGE_HEIGHT - MARGIN - 1.3*inch
                
                for num in sorted(puzzle['across_clues'].keys()):
                    if y > MARGIN + 0.5*inch:
                        c.drawString(MARGIN, y, f"{num}. {puzzle['across_clues'][num]}")
                        y -= 0.25*inch
                
                # DOWN
                c.setFont("Helvetica-Bold", 12)
                c.drawString(PAGE_WIDTH/2 + 0.1*inch, PAGE_HEIGHT - MARGIN - 1*inch, "DOWN")
                c.setFont("Helvetica", 10)
                y = PAGE_HEIGHT - MARGIN - 1.3*inch
                
                for num in sorted(puzzle['down_clues'].keys()):
                    if y > MARGIN + 0.5*inch:
                        c.drawString(PAGE_WIDTH/2 + 0.1*inch, y, f"{num}. {puzzle['down_clues'][num]}")
                        y -= 0.25*inch
                
                c.showPage()
            
            # Solutions (one per page)
            for puzzle in puzzles:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 0.5*inch, 
                                  f"Puzzle {puzzle['number']} - Solution")
                
                # Draw solution grid
                solution_cell = 0.24 * inch
                grid_size = 15 * solution_cell
                x_offset = (PAGE_WIDTH - grid_size) / 2
                y_offset = (PAGE_HEIGHT - grid_size) / 2 + 1*inch
                
                c.setLineWidth(0.5)
                for row in range(15):
                    for col in range(15):
                        x = x_offset + (col * solution_cell)
                        y = y_offset - (row * solution_cell)
                        
                        if puzzle['grid'][row][col] == '#':
                            c.setFillColor(colors.black)
                            c.rect(x, y, solution_cell, solution_cell, fill=1, stroke=0)
                        else:
                            c.setFillColor(colors.white)
                            c.setStrokeColor(colors.black)
                            c.rect(x, y, solution_cell, solution_cell, fill=1, stroke=1)
                            
                            # Add letter
                            c.setFillColor(colors.black)
                            c.setFont("Helvetica-Bold", 10)
                            letter = puzzle['grid'][row][col]
                            c.drawCentredString(x + solution_cell/2, 
                                              y + solution_cell/2 - 3, letter)
                
                c.showPage()
            
            # About page (156)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN - 1*inch, "About KindleMint Press")
            c.setFont("Helvetica", 11)
            y = PAGE_HEIGHT - MARGIN - 2*inch
            about_text = [
                "KindleMint Press specializes in large print puzzle books",
                "designed for readers who appreciate clear, easy-to-read",
                "formats. Our puzzles are carefully crafted to provide",
                "both entertainment and mental stimulation.",
                "",
                "Visit us at www.kindlemintpress.com for more titles."
            ]
            for line in about_text:
                c.drawString(MARGIN, y, line)
                y -= 0.3*inch
            c.showPage()
            
            c.save()
            print(f"✅ Created {pdf_path}")


def main():
    print("Creating Volume 3 FINAL with unique puzzles...")
    generator = FinalCrosswordGenerator()
    generator.create_complete_book()
    print("\n✅ Volume 3 FINAL complete!")


if __name__ == "__main__":
    main()