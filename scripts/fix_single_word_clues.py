#!/usr/bin/env python3
"""Fix single-word clues by adding descriptive context"""


def fix_single_word_clue(clue: str) -> str:
    """Convert single-word clues to multi-word clues"""

    # Common patterns for different types of clues
    conversions = {
        # Emotions/feelings
        "Happy": "Feel happy",
        "Sad": "Feel sad",
        "Angry": "Feel angry",
        "Hurt": "Feel pain",
        "Pain": "Physical hurt",
        "Ache": "Dull pain",
        "Yearn": "Long for",
        # Actions
        "Run": "Move quickly",
        "Walk": "Go slowly",
        "Jump": "Leap up",
        "Fly": "Travel airborne",
        "Swim": "Move underwater",
        "Dance": "Move rhythmically",
        "Sing": "Vocalize melodically",
        "Operate": "Make function",
        "Function": "Work properly",
        "Support": "Hold up",
        "Help": "Give aid",
        "Aid": "Provide help",
        "Assist": "Give support",
        # Descriptors
        "Large": "Big size",
        "Small": "Little size",
        "Huge": "Very large",
        "Tiny": "Very small",
        "Hot": "High temperature",
        "Cold": "Low temperature",
        "Fast": "High speed",
        "Slow": "Low speed",
        "New": "Not old",
        "Old": "Not new",
        "Good": "Not bad",
        "Bad": "Not good",
        "Right": "Not wrong",
        "Wrong": "Not right",
        "True": "Not false",
        "False": "Not true",
        # Nouns
        "Person": "Human being",
        "Place": "Specific location",
        "Thing": "Physical object",
        "Animal": "Living creature",
        "Plant": "Growing organism",
        "Food": "Edible item",
        "Water": "Clear liquid",
        "Fire": "Hot flames",
        "Earth": "Our planet",
        "Air": "Breathable gas",
        # Relationships
        "Parent": "Mom or dad",
        "Child": "Young person",
        "Friend": "Close companion",
        "Enemy": "Hostile person",
        "Partner": "Close associate",
        "Spouse": "Marriage partner",
        # Time
        "Today": "This day",
        "Tomorrow": "Next day",
        "Yesterday": "Previous day",
        "Now": "This moment",
        "Then": "That time",
        "Always": "Every time",
        "Never": "No time",
        # Directions/positions
        "Up": "Toward sky",
        "Down": "Toward ground",
        "Left": "Port side",
        "Right": "Starboard side",
        "In": "Inside location",
        "Out": "Outside location",
        "On": "Surface position",
        "Off": "Away from",
        "Over": "Above position",
        "Under": "Below position",
        "Above": "Higher than",
        "Below": "Lower than",
        "Near": "Close by",
        "Far": "Distant from",
        # Common adjectives
        "Beautiful": "Very pretty",
        "Ugly": "Not attractive",
        "Strong": "Having strength",
        "Weak": "Lacking strength",
        "Rich": "Having wealth",
        "Poor": "Lacking money",
        "Full": "Completely filled",
        "Empty": "Nothing inside",
        "Clean": "Not dirty",
        "Dirty": "Not clean",
        "Wet": "Contains water",
        "Dry": "No moisture",
        # Common verbs
        "Go": "Move away",
        "Come": "Move toward",
        "Get": "Obtain something",
        "Give": "Provide something",
        "Take": "Remove something",
        "Make": "Create something",
        "Do": "Perform action",
        "Say": "Speak words",
        "See": "Use eyes",
        "Hear": "Use ears",
        "Think": "Use brain",
        "Know": "Have knowledge",
        "Want": "Desire something",
        "Need": "Require something",
        "Have": "Possess something",
        "Like": "Enjoy something",
        "Love": "Adore deeply",
        "Hate": "Dislike strongly",
        # Abstract concepts
        "Truth": "Accurate fact",
        "Lie": "False statement",
        "Hope": "Positive expectation",
        "Fear": "Negative emotion",
        "Dream": "Sleep vision",
        "Reality": "Actual existence",
        "Life": "Living existence",
        "Death": "Life's end",
        "Peace": "No conflict",
        "War": "Armed conflict",
        # Common single-word answers
        "Yes": "Positive response",
        "No": "Negative response",
        "Maybe": "Uncertain response",
        "Okay": "Agreement word",
        "Sure": "Certain agreement",
        "Fine": "Acceptable state",
        # Job/role descriptors
        "Doctor": "Medical professional",
        "Teacher": "Education provider",
        "Student": "Person learning",
        "Worker": "Employee person",
        "Boss": "Company leader",
        "Leader": "Group head",
        # Quality descriptors
        "Capable": "Having ability",
        "Competent": "Well qualified",
        "Qualified": "Meeting requirements",
        "Expert": "Highly skilled",
        "Amateur": "Not professional",
        "Professional": "Paid expert",
        # Quantity
        "All": "Every one",
        "None": "Not any",
        "Some": "Partial amount",
        "Many": "Large number",
        "Few": "Small number",
        "More": "Greater amount",
        "Less": "Smaller amount",
        # States of being
        "Alive": "Not dead",
        "Dead": "Not alive",
        "Awake": "Not sleeping",
        "Asleep": "Not awake",
        "Open": "Not closed",
        "Closed": "Not open",
        "Broken": "Not working",
        "Fixed": "Working properly",
        # Colors (if not already multi-word)
        "Red": "Rose color",
        "Blue": "Sky color",
        "Green": "Grass color",
        "Yellow": "Sun color",
        "Black": "Night color",
        "White": "Snow color",
        "Brown": "Earth color",
        "Orange": "Citrus color",
        "Purple": "Royal color",
        "Pink": "Light red",
        # Materials
        "Wood": "Tree material",
        "Metal": "Hard material",
        "Glass": "Clear material",
        "Plastic": "Synthetic material",
        "Stone": "Rock material",
        "Paper": "Writing material",
        # Weather
        "Rain": "Water drops",
        "Snow": "Frozen precipitation",
        "Wind": "Moving air",
        "Storm": "Bad weather",
        "Cloud": "Sky formation",
        "Sun": "Day star",
        # Basic needs
        "Eat": "Consume food",
        "Drink": "Consume liquid",
        "Sleep": "Rest state",
        "Breathe": "Take air",
        # Common adverbs that might appear
        "Quickly": "With speed",
        "Slowly": "Without haste",
        "Carefully": "With caution",
        "Roughly": "Without care",
        "Quietly": "Without noise",
        "Loudly": "With noise",
        # Geography
        "Mountain": "Tall landform",
        "Valley": "Low area",
        "River": "Water flow",
        "Ocean": "Large sea",
        "Desert": "Dry area",
        "Forest": "Tree area",
        "City": "Urban area",
        "Country": "Rural area",
        # Body parts
        "Head": "Top part",
        "Hand": "Arm end",
        "Foot": "Leg end",
        "Eye": "Seeing organ",
        "Ear": "Hearing organ",
        "Mouth": "Eating organ",
        "Nose": "Smelling organ",
        # Time periods
        "Day": "24 hours",
        "Night": "Dark hours",
        "Week": "Seven days",
        "Month": "Four weeks",
        "Year": "Twelve months",
        "Hour": "Sixty minutes",
        "Minute": "Sixty seconds",
        # Common prepositions that might need fixing
        "With": "Along with",
        "Without": "Lacking something",
        "Before": "Prior to",
        "After": "Following something",
        "During": "While happening",
        "Through": "Pass via",
        "Between": "In middle",
        "Among": "Within group",
        "Around": "Near about",
        "Across": "Other side",
        "Along": "Beside something",
        "Against": "In opposition",
        "Behind": "At back",
        "Beside": "Next to",
        "Beyond": "Past something",
        "Inside": "Within something",
        "Outside": "Not within",
        "Toward": "In direction",
        # Abstract/miscellaneous
        "Freedom": "Being free",
        "Justice": "Fair treatment",
        "Beauty": "Aesthetic quality",
        "Wisdom": "Deep knowledge",
        "Courage": "Being brave",
        "Strength": "Being strong",
        "Weakness": "Lacking strength",
        "Victory": "Winning result",
        "Defeat": "Losing result",
        "Success": "Good outcome",
        "Failure": "Bad outcome",
        # Common problem words from crosswords
        "Level": "Flat surface",
        "Plane": "Flat surface",
        "Circa": "About when",
        "Approximately": "About roughly",
        "Concerning": "About something",
        "Overhead": "Above position",
        "Corrosive": "Acid-like substance",
        "LSD": "Psychedelic drug",
        "Mistreat": "Treat badly",
        "Misuse": "Use wrongly",
        "Insult": "Verbal attack",
        "Top-notch": "First rate",
        "Throb": "Beat rhythmically",
    }

    # If we have a specific conversion, use it
    if clue in conversions:
        return conversions[clue]

    # Generic patterns for common endings
    if clue.endswith("ly"):
        return f"In {clue.lower()[:-2]} manner"

    if clue.endswith("ing"):
        return f"Act of {clue.lower()}"

    if clue.endswith("ed"):
        return f"Past tense action"

    if clue.endswith("er"):
        return f"One who {clue.lower()[:-2]}s"

    if clue.endswith("est"):
        return f"Most {clue.lower()[:-3]}"

    if clue.endswith("ness"):
        return f"State of being"

    # Default fallback - add context
    first_letter = clue[0].lower()
    if first_letter in "aeiou":
        return f"An {clue.lower()}"
    else:
        return f"A {clue.lower()}"


if __name__ == "__main__":
    # Test some examples
    test_clues = [
        "Happy",
        "Run",
        "Beautiful",
        "Quickly",
        "Level",
        "Function",
        "Support",
        "Approximately",
    ]
    for clue in test_clues:
        print(f"{clue} -> {fix_single_word_clue(clue)}")
