#!/usr/bin/env python3
"""
Professional Crossword Clue Generator
Generates high-quality, varied clues for crossword puzzles
"""

import random
import re
from typing import Dict, List, Optional


class CrosswordClueGenerator:
    def __init__(self):
        # Comprehensive clue database with multiple variations per word
        self.clue_database = {
            # 3-letter words
            "ACE": [
                "Playing card",
                "Tennis serve winner",
                "Expert pilot",
                "Top-notch",
                "Perfect serve",
            ],
            "ADD": [
                "Sum up",
                "Plus operation",
                "Combine numbers",
                "Tally",
                "Include in total",
            ],
            "AGE": [
                "Years lived",
                "Era",
                "Time period",
                "Get older",
                "Historical period",
            ],
            "AID": ["Help", "Assistance", "First ___", "Support", "Relief"],
            "AIM": ["Target", "Goal", "Point at", "Objective", "Purpose"],
            "AIR": [
                "Breathable gas",
                "Atmosphere",
                "Broadcast medium",
                "Melody",
                "Ventilate",
            ],
            "ALL": [
                "Everything",
                "Entire amount",
                "The whole thing",
                "100 percent",
                "Complete",
            ],
            "AND": ["Plus", "Also", "Conjunction", "In addition to", "With"],
            "ANT": [
                "Picnic pest",
                "Colony insect",
                "Small worker",
                "Hill dweller",
                "Industrious bug",
            ],
            "ANY": ["Whatever amount", "Some", "At all", "One or more", "Whichever"],
            "APE": ["Primate", "Gorilla cousin", "Mimic", "Copy", "Large primate"],
            "ARC": [
                "Curve",
                "Rainbow shape",
                "Part of circle",
                "Electrical spark",
                "Story progression",
            ],
            "ARE": [
                "Exist (plural)",
                "You ___ here",
                "Square measure",
                "Metric unit",
                "To be",
            ],
            "ARM": ["Limb", "Branch", "Weapon", "Supply with weapons", "Upper limb"],
            "ART": [
                "Creative work",
                "Gallery display",
                "Skill",
                "Paintings",
                "Museum piece",
            ],
            "ASK": ["Question", "Request", "Inquire", "Seek answer", "Query"],
            "ATE": ["Consumed", "Had dinner", "Devoured", "Past of eat", "Dined"],
            "BAD": ["Not good", "Naughty", "Poor quality", "Wicked", "Spoiled"],
            "BAG": ["Sack", "Container", "Purse", "Catch", "Shopping holder"],
            "BAR": ["Tavern", "Rod", "Prevent", "Legal profession", "Soap unit"],
            "BAT": [
                "Baseball stick",
                "Flying mammal",
                "Cricket club",
                "Vampire form",
                "Swing at",
            ],
            "BED": [
                "Sleep furniture",
                "Garden plot",
                "River bottom",
                "Place to rest",
                "Foundation",
            ],
            "BEE": [
                "Honey maker",
                "Spelling contest",
                "Buzzing insect",
                "Busy worker",
                "Pollinator",
            ],
            "BIG": ["Large", "Important", "Grown up", "Huge", "Major"],
            "BIT": [
                "Small piece",
                "Computer unit",
                "Horse restraint",
                "Slightly",
                "Fragment",
            ],
            "BOW": [
                "Ribbon shape",
                "Violin stick",
                "Bend forward",
                "Arrow launcher",
                "Ship front",
            ],
            "BOX": ["Container", "Fight", "Square", "Package", "Ring sport"],
            "BOY": ["Young male", "Lad", "Son", "Youth", "Male child"],
            "BUS": [
                "Public transport",
                "School vehicle",
                "Motor coach",
                "City transport",
                "Clear tables",
            ],
            "BUY": ["Purchase", "Acquire", "Shop for", "Obtain with money", "Believe"],
            "CAB": ["Taxi", "Truck front", "Wine type", "Yellow car", "Hired car"],
            "CAN": ["Tin", "Is able to", "Container", "Preserve", "Fire"],
            "CAP": ["Hat", "Lid", "Upper limit", "Baseball hat", "Crown"],
            "CAR": ["Auto", "Vehicle", "Sedan", "Railway wagon", "Automobile"],
            "CAT": ["Feline", "Pet", "Jazz fan", "Lion's cousin", "Meower"],
            "COW": ["Bovine", "Milk source", "Farm animal", "Intimidate", "Moo maker"],
            "CRY": ["Weep", "Shout", "Sob", "Shed tears", "Wail"],
            "CUP": ["Mug", "Trophy", "Measure", "Drinking vessel", "Bra part"],
            "CUT": ["Slice", "Reduce", "Wound", "Film edit", "Share"],
            "DAD": ["Father", "Pop", "Papa", "Male parent", "Daddy"],
            "DAY": ["24 hours", "Light time", "Date", "Epoch", "Not night"],
            "DEN": ["Animal home", "Study room", "Lair", "Hideout", "Fox's home"],
            "DEW": [
                "Morning moisture",
                "Grass drops",
                "Dawn wetness",
                "Condensation",
                "Mountain ___ soda",
            ],
            "DID": [
                "Performed",
                "Accomplished",
                "Past of do",
                "Executed",
                "Carried out",
            ],
            "DIE": [
                "Expire",
                "Gaming cube",
                "Perish",
                "Cease living",
                "Singular of dice",
            ],
            "DIG": [
                "Excavate",
                "Understand",
                "Archaeological work",
                "Shovel work",
                "Like",
            ],
            "DOC": [
                "Physician",
                "Document",
                "Medical pro",
                "Seven dwarfs member",
                "PhD",
            ],
            "DOG": ["Canine", "Pet", "Hound", "Pup", "Man's best friend"],
            "DOT": ["Point", "Period", "Spot", "Small mark", "Polka ___"],
            "DRY": ["Not wet", "Arid", "Boring", "Towel off", "Wine type"],
            "DUE": ["Owed", "Expected", "Payable", "Because of", "Proper"],
            "EAR": [
                "Hearing organ",
                "Corn unit",
                "Sound sensor",
                "Lobe location",
                "Audio receiver",
            ],
            "EAT": ["Consume", "Dine", "Have a meal", "Chow down", "Devour"],
            "EGG": [
                "Oval food",
                "Breakfast item",
                "Encourage",
                "Chicken product",
                "Easter decoration",
            ],
            "ELF": [
                "Santa helper",
                "Pixie",
                "Small being",
                "North Pole worker",
                "Fairy tale creature",
            ],
            "END": ["Finish", "Conclusion", "Terminate", "Goal", "Final part"],
            "ERA": ["Period", "Age", "Epoch", "Time span", "Historical time"],
            "EVE": ["Night before", "First woman", "Evening", "Brink", "Dec 31"],
            "EYE": [
                "Vision organ",
                "Look at",
                "Storm center",
                "Needle hole",
                "Observe",
            ],
            "FAN": [
                "Admirer",
                "Cooling device",
                "Enthusiast",
                "Spread out",
                "Sports supporter",
            ],
            "FAR": ["Distant", "Remote", "Long way", "Not near", "Way off"],
            "FAT": ["Obese", "Grease", "Plump", "Cooking oil", "Not thin"],
            "FAX": [
                "Document transmitter",
                "Send electronically",
                "Office machine",
                "Quick message",
                "Pre-email communication",
            ],
            "FEE": ["Charge", "Cost", "Payment", "Price", "Professional charge"],
            "FEW": ["Not many", "Some", "Small number", "Several", "Handful"],
            "FIG": [
                "Fruit",
                "Newton filling",
                "Tree fruit",
                "Dried fruit",
                "Mediterranean fruit",
            ],
            "FIN": ["Fish part", "End", "Five dollars", "Flipper", "Shark feature"],
            "FIT": ["Healthy", "Suitable", "Match", "In shape", "Proper size"],
            "FIX": ["Repair", "Mend", "Predicament", "Fasten", "Prepare"],
            "FLY": ["Insect", "Soar", "Travel by air", "Baseball hit", "Pilot"],
            "FOE": ["Enemy", "Opponent", "Adversary", "Rival", "Antagonist"],
            "FOG": ["Mist", "Haze", "Low cloud", "Obscure", "Weather condition"],
            "FOR": [
                "In favor of",
                "Because",
                "Purpose",
                "During",
                "Meant to be given to",
            ],
            "FOX": [
                "Sly animal",
                "News channel",
                "Cunning one",
                "Red animal",
                "Chicken thief",
            ],
            "FUN": ["Enjoyment", "Amusement", "Good time", "Entertainment", "Pleasure"],
            "FUR": ["Animal coat", "Pelt", "Soft hair", "Mink or sable", "Winter coat"],
            "GAP": ["Opening", "Space", "Interval", "Break", "Clothing store"],
            "GAS": ["Fuel", "Vapor", "Petrol", "Natural ___", "Step on it"],
            "GEL": [
                "Hair product",
                "Solidify",
                "Jelly",
                "Come together",
                "Styling aid",
            ],
            "GEM": [
                "Jewel",
                "Precious stone",
                "Diamond",
                "Treasure",
                "Outstanding person",
            ],
            "GET": ["Obtain", "Receive", "Acquire", "Understand", "Fetch"],
            "GOD": [
                "Deity",
                "Supreme being",
                "Creator",
                "Divine one",
                "Object of worship",
            ],
            "GOT": ["Obtained", "Received", "Understood", "Past of get", "Acquired"],
            "GUM": [
                "Chewing substance",
                "Tree sap",
                "Adhesive",
                "Pink mouth part",
                "Sticky stuff",
            ],
            "GUN": ["Weapon", "Firearm", "Pistol", "Accelerate", "Rifle"],
            "GUT": [
                "Stomach",
                "Intestine",
                "Instinct",
                "Inner feeling",
                "Remove insides",
            ],
            "GUY": ["Fellow", "Man", "Dude", "Cable", "November 5 effigy"],
            "GYM": [
                "Exercise place",
                "PE class",
                "Workout spot",
                "School auditorium",
                "Fitness center",
            ],
            "HAD": ["Possessed", "Owned", "Past of have", "Experienced", "Held"],
            "HAM": ["Pork", "Actor type", "Radio operator", "Overact", "Sandwich meat"],
            "HAS": ["Possesses", "Owns", "Contains", "Present of have", "Holds"],
            "HAT": [
                "Head covering",
                "Cap",
                "Fedora",
                "Millinery item",
                "Bowler or beret",
            ],
            "HAY": [
                "Dried grass",
                "Horse food",
                "Barn stack",
                "Make ___ while...",
                "Fever cause",
            ],
            "HER": [
                "That woman",
                "Belonging to she",
                "Female pronoun",
                "Not him",
                "She, objectively",
            ],
            "HEW": ["Chop", "Cut with axe", "Shape by cutting", "Carve", "Hack"],
            "HEX": ["Curse", "Six-sided", "Spell", "Bewitch", "Evil spell"],
            "HID": [
                "Concealed",
                "Past of hide",
                "Kept secret",
                "Stashed",
                "Put out of sight",
            ],
            "HIM": [
                "That man",
                "Male pronoun",
                "Not her",
                "He, objectively",
                "That guy",
            ],
            "HIP": ["Body joint", "Cool", "Trendy", "Rose fruit", "Pelvis part"],
            "HIS": [
                "Belonging to him",
                "That man's",
                "Male possessive",
                "Not hers",
                "Of him",
            ],
            "HIT": [
                "Strike",
                "Success",
                "Punch",
                "Popular song",
                "Baseball achievement",
            ],
            "HOG": ["Pig", "Road ___", "Monopolize", "Swine", "Greedy one"],
            "HOP": ["Jump", "Skip", "Beer ingredient", "Quick trip", "Rabbit move"],
            "HOT": ["Very warm", "Spicy", "Popular", "Angry", "Stolen"],
            "HOW": [
                "In what way",
                "Question word",
                "Method inquiry",
                "By what means",
                "___ come?",
            ],
            "HUB": [
                "Center",
                "Airport",
                "Wheel center",
                "Main location",
                "Activity center",
            ],
            "HUG": ["Embrace", "Squeeze", "Hold close", "Bear ___", "Show affection"],
            "HUM": ["Buzz", "Sing wordlessly", "Vibrate", "Be busy", "Engine sound"],
            "HUT": ["Shack", "Small dwelling", "Cabin", "Simple shelter", "Pizza ___"],
            "ICE": ["Frozen water", "Cool", "Diamonds", "Hockey surface", "Cube"],
            "ILL": ["Sick", "Unwell", "Bad", "Harmful", "Under the weather"],
            "INK": [
                "Pen fluid",
                "Tattoo material",
                "Squid defense",
                "Writing fluid",
                "Press material",
            ],
            "INN": ["Small hotel", "Tavern", "Lodge", "Roadside stop", "B&B"],
            "ION": [
                "Charged particle",
                "Atom type",
                "Saturn model",
                "Electrical particle",
                "Chemistry term",
            ],
            "IRE": ["Anger", "Wrath", "Fury", "Rage", "Indignation"],
            "ITS": [
                "Belonging to it",
                "That thing's",
                "Possessive of it",
                "Not it's",
                "Of it",
            ],
            "IVY": [
                "Climbing plant",
                "League plant",
                "Wall climber",
                "Poison ___",
                "College vine",
            ],
            # 4-letter words
            "ABLE": ["Capable", "Competent", "Having skill", "Can do", "Qualified"],
            "ACHE": ["Pain", "Hurt", "Throb", "Dull pain", "Yearn"],
            "ACID": [
                "Sour substance",
                "LSD",
                "Battery fluid",
                "pH below 7",
                "Corrosive",
            ],
            "ACRE": [
                "Land measure",
                "4,840 sq yards",
                "Farm unit",
                "Plot size",
                "Field measure",
            ],
            "AGED": ["Old", "Matured", "Elderly", "Like wine", "Senior"],
            "AJAR": [
                "Slightly open",
                "Not shut",
                "Door position",
                "Partly open",
                "Cracked",
            ],
            "ALSO": ["Too", "In addition", "As well", "Besides", "Furthermore"],
            "AMID": ["Among", "In the middle of", "Surrounded by", "During", "Within"],
            "ANTS": [
                "Picnic pests",
                "Colony insects",
                "Small workers",
                "Hill dwellers",
                "Six-leggers",
            ],
            "APEX": ["Top", "Peak", "Summit", "Highest point", "Pinnacle"],
            "ARCH": [
                "Curved structure",
                "Foot part",
                "Playfully sly",
                "Bridge type",
                "Eyebrow shape",
            ],
            "AREA": ["Region", "Zone", "Space", "District", "Section"],
            "ARMY": [
                "Military force",
                "Host",
                "Large group",
                "Soldiers",
                "Ground forces",
            ],
            "ARTS": [
                "Creative works",
                "Liberal ___",
                "Crafts partner",
                "Cultural studies",
                "Fine ___",
            ],
            "ATOM": [
                "Tiny particle",
                "Molecule part",
                "Nuclear item",
                "Basic unit",
                "Smallest bit",
            ],
            "AUTO": ["Car", "Self prefix", "Vehicle", "Automatic", "Automobile"],
            "AWAY": ["Gone", "Distant", "Not here", "On vacation", "Departed"],
            "BABY": ["Infant", "Newborn", "Tot", "Little one", "Pamper"],
            "BACK": ["Rear", "Return", "Support", "Spine area", "Ago"],
            "BAKE": [
                "Cook in oven",
                "Make bread",
                "Roast",
                "Heat thoroughly",
                "Make cookies",
            ],
            "BALL": ["Sphere", "Dance", "Round object", "Good time", "Sports item"],
            "BAND": ["Musical group", "Ring", "Strip", "Unite", "Frequency range"],
            "BANK": [
                "Financial institution",
                "River edge",
                "Rely on",
                "Tilt",
                "Money place",
            ],
            "BARE": ["Naked", "Empty", "Minimal", "Expose", "Plain"],
            "BARK": ["Dog sound", "Tree covering", "Yell", "Ship", "Rough call"],
            "BARN": [
                "Farm building",
                "Storage structure",
                "Hay holder",
                "Cow house",
                "Rural structure",
            ],
            "BASE": [
                "Foundation",
                "Bottom",
                "Military post",
                "Starting point",
                "Alkaline",
            ],
            "BATH": ["Wash", "Tub", "Soak", "Cleansing", "Spa city"],
            "BEAM": ["Ray", "Smile", "Support", "Light shaft", "Broadcast"],
            "BEAN": ["Legume", "Coffee seed", "Head", "Lima or navy", "Vegetable"],
            "BEAR": ["Animal", "Carry", "Endure", "Give birth", "Market pessimist"],
            "BEAT": ["Defeat", "Rhythm", "Strike", "Mix", "Tired"],
            "BEEN": ["Existed", "Past participle of be", "Went to", "Occurred", "Was"],
            "BEER": ["Brew", "Ale", "Lager", "Pub drink", "Hops beverage"],
            "BELL": [
                "Ringer",
                "Chime",
                "Alexander Graham",
                "Tower item",
                "Door signal",
            ],
            "BELT": [
                "Waist strap",
                "Region",
                "Hit hard",
                "Sing loudly",
                "Asteroid region",
            ],
            "BEND": ["Curve", "Flex", "Turn", "Bow", "River feature"],
            "BEST": ["Finest", "Top", "Defeat", "Most good", "Optimal"],
            "BIKE": ["Bicycle", "Two-wheeler", "Cycle", "Pedal vehicle", "Motorcycle"],
            "BILL": [
                "Invoice",
                "Duck part",
                "Paper money",
                "Proposed law",
                "Statement",
            ],
            "BIND": ["Tie", "Fasten", "Obligate", "Difficult situation", "Book edge"],
            "BIRD": [
                "Feathered creature",
                "Plane",
                "Shuttlecock",
                "Oriole or owl",
                "Flying animal",
            ],
            "BITE": ["Chew", "Sting", "Small meal", "Tooth grip", "Nibble"],
            "BLOW": ["Wind", "Strike", "Explode", "Breathe hard", "Disaster"],
            "BLUE": ["Color", "Sad", "Sky shade", "Ocean hue", "Jazz type"],
            "BLUR": ["Smudge", "Unclear image", "Make fuzzy", "Indistinct", "Speed by"],
            "BOAR": ["Wild pig", "Male pig", "Tusked animal", "Forest animal", "Swine"],
            "BOAT": ["Vessel", "Ship", "Watercraft", "Yacht", "Sailing craft"],
            "BODY": ["Physique", "Corpse", "Main part", "Group", "Torso"],
            "BOIL": ["Heat liquid", "Bubble", "Anger", "Skin infection", "Cook"],
            "BOLD": ["Brave", "Daring", "Font type", "Audacious", "Prominent"],
            "BOLT": ["Fastener", "Lightning", "Run away", "Lock part", "Fabric roll"],
            "BOMB": ["Explosive", "Fail badly", "Theatre flop", "Weapon", "Dud"],
            "BOND": ["Connection", "007", "Adhesive", "Financial instrument", "Unite"],
            "BONE": [
                "Skeleton part",
                "Fish hazard",
                "Study hard",
                "Ivory source",
                "Dog treat",
            ],
            "BOOK": ["Volume", "Reserve", "Novel", "Text", "Arrest"],
            "BOOM": [
                "Loud sound",
                "Prosper",
                "Crane arm",
                "Economic growth",
                "Thunder",
            ],
            "BOOT": ["Footwear", "Kick out", "Computer start", "Trunk", "Navy recruit"],
            "BORE": [
                "Drill",
                "Tedious person",
                "Make weary",
                "Gun barrel",
                "Tidal ___",
            ],
            "BORN": [
                "Brought into being",
                "Natural",
                "Delivered",
                "Native",
                "Originated",
            ],
            "BOSS": ["Manager", "Supervisor", "Excellent", "Stud", "Chief"],
            "BOTH": [
                "Two together",
                "Each of two",
                "Equally",
                "The pair",
                "One and the other",
            ],
            "BOWL": ["Dish", "Stadium", "Roll a ball", "Super ___", "Soup holder"],
            # 5-letter words
            "ABOUT": [
                "Concerning",
                "Approximately",
                "Around",
                "Near",
                "On the subject of",
            ],
            "ABOVE": ["Over", "Higher than", "Beyond", "More than", "Overhead"],
            "ABUSE": [
                "Mistreat",
                "Misuse",
                "Harmful treatment",
                "Insult",
                "Take advantage",
            ],
            "ACTOR": [
                "Performer",
                "Thespian",
                "Stage player",
                "Movie star",
                "One who acts",
            ],
            "ADAPT": ["Adjust", "Modify", "Change to fit", "Make suitable", "Evolve"],
            "ADMIT": ["Confess", "Allow in", "Acknowledge", "Let enter", "Own up"],
            "ADOPT": [
                "Take as one's own",
                "Choose",
                "Take in",
                "Embrace",
                "Accept formally",
            ],
            "ADULT": [
                "Grown-up",
                "Mature person",
                "Of age",
                "Not a child",
                "Full-grown",
            ],
            "AFTER": [
                "Following",
                "Later than",
                "Behind",
                "Subsequently",
                "In pursuit of",
            ],
            "AGAIN": [
                "Once more",
                "Anew",
                "Additionally",
                "Repeatedly",
                "Another time",
            ],
            "AGENT": ["Representative", "Spy", "Broker", "Factor", "007 for one"],
            "AGREE": ["Concur", "Consent", "Match", "Harmonize", "See eye to eye"],
            "AHEAD": ["In front", "Forward", "In advance", "Leading", "Before"],
            "ALARM": ["Warning device", "Alert", "Fear", "Clock feature", "Frighten"],
            "ALBUM": [
                "Photo book",
                "Record",
                "Collection",
                "Music release",
                "Scrapbook",
            ],
            "ALERT": ["Watchful", "Warning", "Quick", "Awake", "On guard"],
            "ALIEN": [
                "Foreign",
                "Extraterrestrial",
                "Strange",
                "Outsider",
                "From space",
            ],
            "ALIGN": ["Line up", "Adjust", "Straighten", "Side with", "Make parallel"],
            "ALIKE": ["Similar", "Comparable", "Equally", "In common", "Resembling"],
            "ALIVE": ["Living", "Animated", "Vibrant", "Not dead", "Breathing"],
            "ALLOW": ["Permit", "Let", "Enable", "Grant", "Give permission"],
            "ALONE": ["Solo", "Solitary", "By oneself", "Unaccompanied", "Single"],
            "ALONG": ["Beside", "Throughout", "With", "Forward", "Side by side"],
            "ALOUD": ["Audibly", "Out loud", "Vocally", "Not silently", "Spoken"],
            "ALPHA": [
                "First Greek letter",
                "Beginning",
                "Top dog",
                "Leader",
                "Primary",
            ],
            "ALTER": ["Change", "Modify", "Adjust", "Transform", "Revise"],
            "ANGEL": [
                "Heavenly being",
                "Good person",
                "Guardian spirit",
                "Investor",
                "Cherub",
            ],
            "ANGER": ["Rage", "Fury", "Wrath", "Ire", "Mad feeling"],
            "ANGLE": ["Corner", "Viewpoint", "Fish", "Slant", "Geometric figure"],
            "ANGRY": ["Mad", "Furious", "Irate", "Upset", "Wrathful"],
            "ANKLE": [
                "Foot joint",
                "Leg part",
                "Above the foot",
                "Sock top",
                "Sprain site",
            ],
            "ANNEX": [
                "Add on",
                "Extension",
                "Attach",
                "Building addition",
                "Take over",
            ],
            "ANNOY": ["Irritate", "Bother", "Pester", "Vex", "Get on nerves"],
            "ANTIC": ["Caper", "Prank", "Playful act", "Shenanigan", "Funny behavior"],
            "APART": ["Separate", "Away from", "In pieces", "Distant", "To one side"],
            "APPLE": [
                "Fruit",
                "Computer company",
                "NYC nickname",
                "Pie fruit",
                "Teacher's gift",
            ],
            "APPLY": ["Put on", "Request", "Use", "Be relevant", "Submit application"],
            "APRIL": [
                "Fourth month",
                "Spring month",
                "Shower month",
                "After March",
                "Easter month",
            ],
            "APRON": [
                "Kitchen wear",
                "Protective garment",
                "Chef's cover",
                "Airport area",
                "Stage front",
            ],
            "ARGUE": ["Debate", "Dispute", "Quarrel", "Make a case", "Disagree"],
            "ARISE": ["Get up", "Occur", "Stand up", "Come about", "Originate"],
            "ARMED": [
                "Carrying weapons",
                "Equipped",
                "Military",
                "With guns",
                "Prepared for war",
            ],
            "AROMA": ["Scent", "Fragrance", "Smell", "Perfume", "Pleasant odor"],
            "ARRAY": [
                "Display",
                "Arrangement",
                "Collection",
                "Line up",
                "Impressive group",
            ],
            "ARROW": [
                "Pointer",
                "Bow missile",
                "Direction indicator",
                "Cupid's weapon",
                "Sign",
            ],
            "ARSON": [
                "Fire crime",
                "Burning crime",
                "Deliberate fire",
                "Pyromania act",
                "Insurance fraud",
            ],
            "ASIDE": ["To one side", "Apart", "Digression", "Stage whisper", "Away"],
            "ASSET": ["Valuable item", "Resource", "Advantage", "Property", "Plus"],
            "ATLAS": [
                "Map book",
                "World holder",
                "Geography book",
                "Titan",
                "Reference book",
            ],
            "ATTIC": ["Top floor", "Storage space", "Garret", "Loft", "Upper room"],
            "AUDIO": ["Sound", "Hearing-related", "Not video", "Recording", "Sonic"],
            "AUDIT": [
                "Financial review",
                "Examine",
                "Verify accounts",
                "Check books",
                "Inspection",
            ],
            "AVOID": ["Evade", "Shun", "Stay away from", "Dodge", "Sidestep"],
            "AWAKE": ["Not asleep", "Alert", "Conscious", "Up", "Aware"],
            "AWARD": ["Prize", "Honor", "Give", "Trophy", "Recognition"],
            "AWARE": ["Conscious of", "Knowing", "Alert", "Informed", "Cognizant"],
            "AWFUL": ["Terrible", "Very bad", "Dreadful", "Horrible", "Inspiring awe"],
        }

        # Pattern-based clues for common endings
        self.pattern_clues = {
            "ING": [
                "Action word",
                "Present participle",
                "Verb form",
                "-ing word",
                "Continuous action",
            ],
            "ER": [
                "Person who",
                "More than",
                "Comparative ending",
                "One who does",
                "Agent suffix",
            ],
            "ED": [
                "Past tense",
                "Already done",
                "Completed action",
                "Verb ending",
                "Historical",
            ],
            "LY": [
                "Adverb ending",
                "In a way",
                "Manner of",
                "How it's done",
                "Descriptive ending",
            ],
            "EST": [
                "Most",
                "Superlative",
                "To the greatest degree",
                "Supreme",
                "Ultimate form",
            ],
            "TION": [
                "Action result",
                "Process",
                "State of being",
                "Noun ending",
                "Abstract concept",
            ],
            "NESS": [
                "Quality of being",
                "State of",
                "Condition",
                "Abstract quality",
                "Noun suffix",
            ],
            "MENT": [
                "Result of",
                "Action outcome",
                "Process result",
                "State",
                "Noun ending",
            ],
            "ABLE": [
                "Can be done",
                "Capable of being",
                "Possible to",
                "Worthy of",
                "Fit for",
            ],
            "LESS": ["Without", "Lacking", "Free from", "Absence of", "Not having"],
            "FUL": [
                "Full of",
                "Having quality of",
                "Characterized by",
                "Tending to",
                "Having",
            ],
            "ISH": [
                "Somewhat",
                "Like",
                "Approximately",
                "Having quality of",
                "Tending toward",
            ],
            "WARD": ["In direction of", "Toward", "Facing", "Moving to", "Oriented"],
            "WISE": [
                "In manner of",
                "With respect to",
                "Regarding",
                "In direction of",
                "Smart",
            ],
        }

        # Thematic clues for specific topics
        self.theme_clues = {
            "ANIMAL": [
                "Living creature",
                "Zoo resident",
                "Pet or wild",
                "Fauna member",
                "Non-plant organism",
            ],
            "COLOR": ["Hue", "Shade", "Tint", "Pigment", "Artist's choice"],
            "NUMBER": ["Digit", "Figure", "Count", "Quantity", "Math symbol"],
            "FOOD": ["Nourishment", "Meal item", "Edible", "Cuisine", "Sustenance"],
            "SPORT": [
                "Athletic activity",
                "Game",
                "Competition",
                "Physical contest",
                "Recreation",
            ],
            "MUSIC": [
                "Sound art",
                "Melody",
                "Rhythmic sounds",
                "Concert content",
                "Audio art",
            ],
            "WEATHER": [
                "Climate condition",
                "Atmospheric state",
                "Forecast subject",
                "Sky status",
                "Meteorology",
            ],
            "GEOGRAPHY": [
                "Earth study",
                "Location science",
                "Map subject",
                "Place study",
                "World features",
            ],
            "SCIENCE": [
                "Knowledge field",
                "Research area",
                "Natural study",
                "Lab work",
                "Discovery field",
            ],
            "HISTORY": [
                "Past events",
                "What happened",
                "Chronicle",
                "Former times",
                "Historical record",
            ],
        }

    def get_clue(
        self,
        word: str,
        difficulty: str = "medium",
        puzzle_num: int = 1,
        used_clues: Optional[set] = None,
    ) -> str:
        """
        Get a high-quality clue for a word

        Args:
            word: The word to create a clue for
            difficulty: easy, medium, or hard
            puzzle_num: Puzzle number for variation
            used_clues: Set of already used clues to avoid duplicates

        Returns:
            A crossword clue string
        """
        if used_clues is None:
            used_clues = set()

        word = word.upper()

        # Check if we have specific clues for this word
        if word in self.clue_database:
            clues = self.clue_database[word]

            # Select clue based on difficulty
            if difficulty.lower() == "easy":
                # Use first (simplest) clue
                idx = 0
            elif difficulty.lower() == "hard":
                # Use last (hardest) clue
                idx = len(clues) - 1
            else:
                # Medium: rotate through middle clues based on puzzle number
                idx = (puzzle_num % max(1, len(clues) - 2)) + 1

            # Ensure we have a valid index
            idx = min(idx, len(clues) - 1)
            clue = clues[idx]

            # If clue is already used, try to find another
            attempts = 0
            while clue in used_clues and attempts < len(clues):
                idx = (idx + 1) % len(clues)
                clue = clues[idx]
                attempts += 1

            used_clues.add(clue)
            return clue

        # If no specific clue, generate one based on patterns
        return self._generate_pattern_clue(word, difficulty, puzzle_num)

    def _generate_pattern_clue(
        self, word: str, difficulty: str, puzzle_num: int
    ) -> str:
        """Generate a clue based on word patterns and structure"""

        # Check for common endings
        for ending, clue_options in self.pattern_clues.items():
            if word.endswith(ending) and len(word) > len(ending):
                base = word[: -len(ending)]
                clue_idx = puzzle_num % len(clue_options)

                # Format based on ending type
                if ending == "ING":
                    return f"{clue_options[clue_idx]} ({base.lower()}ing)"
                elif ending == "ER":
                    if base in self.clue_database:
                        return f"One who {self.clue_database[base][0].lower()}s"
                    return f"{clue_options[clue_idx]} ({base.lower()}s)"
                elif ending == "ED":
                    if base in self.clue_database:
                        return f"Previously {self.clue_database[base][0].lower()}"
                    return f"{clue_options[clue_idx]} ({base.lower()})"
                elif ending == "LY":
                    return f"{clue_options[clue_idx]} ({base.lower()})"
                else:
                    return f"{base.title()} {clue_options[clue_idx].lower()}"

        # Check for compound words
        compound_parts = self._check_compound(word)
        if compound_parts:
            part1, part2 = compound_parts
            if part1 in self.clue_database and part2 in self.clue_database:
                return (
                    f"{self.clue_database[part1][0]} + {self.clue_database[part2][0]}"
                )

        # Check for theme-based clues
        theme_clue = self._get_theme_clue(word, difficulty)
        if theme_clue:
            return theme_clue

        # Generate contextual clue based on word properties
        return self._generate_contextual_clue(word, difficulty)

    def _check_compound(self, word: str) -> Optional[tuple]:
        """Check if word is a compound word"""
        # Common compound patterns
        for i in range(3, len(word) - 2):
            part1 = word[:i]
            part2 = word[i:]
            if part1 in self.clue_database and part2 in self.clue_database:
                return (part1, part2)
        return None

    def _get_theme_clue(self, word: str, difficulty: str) -> Optional[str]:
        """Get theme-based clue if word fits a category"""
        # Animal names
        animals = [
            "BEAR",
            "WOLF",
            "LION",
            "TIGER",
            "EAGLE",
            "HAWK",
            "DEER",
            "MOOSE",
            "OTTER",
            "SEAL",
        ]
        if word in animals:
            if difficulty == "easy":
                return f"Wild animal"
            elif difficulty == "hard":
                return (
                    f"Forest dweller"
                    if word in ["BEAR", "WOLF", "DEER", "MOOSE"]
                    else "Predator"
                )
            else:
                return f"{word.title()}'s habitat resident"

        # Colors
        colors = [
            "RED",
            "BLUE",
            "GREEN",
            "YELLOW",
            "ORANGE",
            "PURPLE",
            "BLACK",
            "WHITE",
            "BROWN",
            "PINK",
        ]
        if word in colors:
            return self._get_color_clue(word, difficulty)

        # Numbers
        if word in [
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
            "FIVE",
            "SIX",
            "SEVEN",
            "EIGHT",
            "NINE",
            "TEN",
        ]:
            return self._get_number_clue(word, difficulty)

        return None

    def _get_color_clue(self, color: str, difficulty: str) -> str:
        """Get color-specific clues"""
        color_associations = {
            "RED": ["Rose hue", "Stop sign color", "Ruby shade"],
            "BLUE": ["Sky color", "Ocean hue", "Sapphire shade"],
            "GREEN": ["Grass color", "Go signal", "Emerald hue"],
            "YELLOW": ["Sun color", "Banana hue", "Caution color"],
            "ORANGE": ["Citrus color", "Sunset hue", "Carrot shade"],
            "PURPLE": ["Royal color", "Violet hue", "Grape shade"],
            "BLACK": ["Night color", "Coal hue", "Darkest shade"],
            "WHITE": ["Snow color", "Pure hue", "Lightest shade"],
            "BROWN": ["Earth color", "Chocolate hue", "Wood shade"],
            "PINK": ["Blush color", "Rose tint", "Flamingo hue"],
        }

        if color in color_associations:
            clues = color_associations[color]
            if difficulty == "easy":
                return clues[0]
            elif difficulty == "hard":
                return clues[2] if len(clues) > 2 else clues[-1]
            else:
                return clues[1] if len(clues) > 1 else clues[0]

        return f"{color.title()} color"

    def _get_number_clue(self, number: str, difficulty: str) -> str:
        """Get number-specific clues"""
        number_map = {
            "ONE": ["Unity", "Single", "First number"],
            "TWO": ["Pair", "Couple", "Binary"],
            "THREE": ["Trio", "Triangle sides", "Crowd number"],
            "FOUR": ["Quartet", "Square sides", "Season count"],
            "FIVE": ["Hand digits", "Pentagon sides", "Basketball team"],
            "SIX": ["Half dozen", "Cube faces", "Insect legs"],
            "SEVEN": ["Lucky number", "Week days", "Deadly sins"],
            "EIGHT": ["Octet", "Spider legs", "Byte bits"],
            "NINE": ["Baseball team", "Cat lives", "Square of three"],
            "TEN": ["Decade", "Decimal base", "Perfect score"],
        }

        if number in number_map:
            clues = number_map[number]
            if difficulty == "easy":
                return clues[0]
            elif difficulty == "hard":
                return clues[2]
            else:
                return clues[1]

        return f"Number {number.lower()}"

    def _generate_contextual_clue(self, word: str, difficulty: str) -> str:
        """Generate contextual clue as last resort"""
        # Use word length and structure to create clue
        length = len(word)

        # Check for repeated letters
        letter_count = {}
        for letter in word:
            letter_count[letter] = letter_count.get(letter, 0) + 1

        repeated_letters = [l for l, c in letter_count.items() if c > 1]

        if repeated_letters:
            if difficulty == "easy":
                return f"{length}-letter word with double {repeated_letters[0]}"
            else:
                return f"Word with repeated {repeated_letters[0]}"

        # Check for vowel patterns
        vowels = sum(1 for letter in word if letter in "AEIOU")
        if vowels >= length // 2:
            return f"Vowel-rich {length}-letter word"
        elif vowels <= 1:
            return f"Consonant-heavy {length}-letter word"

        # Default contextual clues based on length
        if length <= 3:
            return f"Short {length}-letter word"
        elif length <= 5:
            return f"Common {length}-letter word"
        elif length <= 7:
            return f"Medium {length}-letter word"
        else:
            return f"Long {length}-letter word"

    def get_varied_clue(self, word: str, clue_number: int, total_clues: int) -> str:
        """Get a varied clue based on position in puzzle"""
        # Vary difficulty based on position
        if clue_number <= total_clues * 0.3:
            difficulty = "easy"
        elif clue_number >= total_clues * 0.7:
            difficulty = "hard"
        else:
            difficulty = "medium"

        return self.get_clue(word, difficulty, clue_number)


# Example usage and testing
if __name__ == "__main__":
    generator = CrosswordClueGenerator()

    # Test some words
    test_words = ["CAT", "COMPUTER", "RUNNING", "QUICKLY", "APPLE", "CROSSWORD"]

    print("Testing Crossword Clue Generator:\n")

    for word in test_words:
        print(f"Word: {word}")
        print(f"  Easy: {generator.get_clue(word, 'easy')}")
        print(f"  Medium: {generator.get_clue(word, 'medium')}")
        print(f"  Hard: {generator.get_clue(word, 'hard')}")
        print()
