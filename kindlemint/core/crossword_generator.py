"""
Crossword Puzzle Generator Module
Creates actual crossword grids and clues for KDP publishing.
"""
import random
import string
from typing import Dict, List, Tuple, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class CrosswordGrid:
    """Represents a crossword puzzle grid."""
    
    def __init__(self, width: int = 15, height: int = 15):
        self.width = width
        self.height = height
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        self.numbers = [[0 for _ in range(width)] for _ in range(height)]
        self.words = []
        self.across_clues = {}
        self.down_clues = {}
        self.current_number = 1
    
    def place_word(self, word: str, row: int, col: int, direction: str, clue: str) -> bool:
        """Place a word in the grid."""
        word = word.upper().replace(' ', '')
        
        if direction == 'across':
            if col + len(word) > self.width:
                return False
            # Check if we can place the word
            for i, letter in enumerate(word):
                if self.grid[row][col + i] != '.' and self.grid[row][col + i] != letter:
                    return False
            
            # Place the word
            for i, letter in enumerate(word):
                self.grid[row][col + i] = letter
            
            # Add number if this is a new word start
            if self.numbers[row][col] == 0:
                self.numbers[row][col] = self.current_number
                self.across_clues[self.current_number] = clue
                self.current_number += 1
            
        elif direction == 'down':
            if row + len(word) > self.height:
                return False
            # Check if we can place the word
            for i, letter in enumerate(word):
                if self.grid[row + i][col] != '.' and self.grid[row + i][col] != letter:
                    return False
            
            # Place the word
            for i, letter in enumerate(word):
                self.grid[row + i][col] = letter
            
            # Add number if this is a new word start
            if self.numbers[row][col] == 0:
                self.numbers[row][col] = self.current_number
                self.down_clues[self.current_number] = clue
                self.current_number += 1
        
        self.words.append({
            'word': word,
            'row': row,
            'col': col,
            'direction': direction,
            'clue': clue
        })
        return True
    
    def to_large_print_string(self) -> str:
        """Convert grid to large print format suitable for seniors."""
        result = []
        
        # Add title
        result.append("┌" + "─" * (self.width * 4 + 1) + "┐")
        
        # Add grid with large spacing
        for row in range(self.height):
            line = "│ "
            for col in range(self.width):
                if self.grid[row][col] == '.':
                    if self.numbers[row][col] > 0:
                        line += f"{self.numbers[row][col]:2d} "
                    else:
                        line += "■■ "
                else:
                    if self.numbers[row][col] > 0:
                        line += f"{self.numbers[row][col]:2d} "
                    else:
                        line += "   "
                line += " "
            line += "│"
            result.append(line)
        
        result.append("└" + "─" * (self.width * 4 + 1) + "┘")
        return "\n".join(result)
    
    def to_solution_string(self) -> str:
        """Convert grid to solution format."""
        result = []
        result.append("SOLUTION:")
        result.append("┌" + "─" * (self.width * 2 + 1) + "┐")
        
        for row in range(self.height):
            line = "│"
            for col in range(self.width):
                if self.grid[row][col] == '.':
                    line += "■"
                else:
                    line += self.grid[row][col]
                line += " "
            line += "│"
            result.append(line)
        
        result.append("└" + "─" * (self.width * 2 + 1) + "┘")
        return "\n".join(result)

class CrosswordGenerator:
    """Generates crossword puzzles with clues."""
    
    def __init__(self):
        """Initialize the crossword generator."""
        self.word_lists = self._load_word_lists()
    
    def _load_word_lists(self) -> Dict[str, List[Dict[str, str]]]:
        """Load word lists organized by theme."""
        return {
            'kitchen': [
                {'word': 'OVEN', 'clue': 'Appliance for baking'},
                {'word': 'SPOON', 'clue': 'Stirring utensil'},
                {'word': 'PLATE', 'clue': 'Dish for food'},
                {'word': 'CUP', 'clue': 'Drinking vessel'},
                {'word': 'SALT', 'clue': 'White seasoning'},
                {'word': 'BREAD', 'clue': 'Baked loaf'},
                {'word': 'MILK', 'clue': 'White dairy drink'},
                {'word': 'EGG', 'clue': 'Oval breakfast food'},
                {'word': 'RICE', 'clue': 'White grain'},
                {'word': 'SOUP', 'clue': 'Hot liquid meal'}
            ],
            'flowers': [
                {'word': 'ROSE', 'clue': 'Red flower with thorns'},
                {'word': 'DAISY', 'clue': 'White petaled flower'},
                {'word': 'TULIP', 'clue': 'Spring bulb flower'},
                {'word': 'LILY', 'clue': 'Easter flower'},
                {'word': 'IRIS', 'clue': 'Purple garden flower'},
                {'word': 'POPPY', 'clue': 'Red memorial flower'},
                {'word': 'PANSY', 'clue': 'Face-like flower'},
                {'word': 'PEONY', 'clue': 'Large pink flower'},
                {'word': 'SAGE', 'clue': 'Purple herb flower'},
                {'word': 'MINT', 'clue': 'Green herb plant'}
            ],
            'animals': [
                {'word': 'CAT', 'clue': 'Meowing pet'},
                {'word': 'DOG', 'clue': 'Barking companion'},
                {'word': 'BIRD', 'clue': 'Flying animal'},
                {'word': 'FISH', 'clue': 'Swimming pet'},
                {'word': 'HORSE', 'clue': 'Riding animal'},
                {'word': 'COW', 'clue': 'Milk-giving animal'},
                {'word': 'PIG', 'clue': 'Pink farm animal'},
                {'word': 'DUCK', 'clue': 'Pond bird'},
                {'word': 'GOAT', 'clue': 'Climbing farm animal'},
                {'word': 'DEER', 'clue': 'Forest animal with antlers'}
            ],
            'easy_general': [
                {'word': 'SUN', 'clue': 'Bright star'},
                {'word': 'MOON', 'clue': 'Night light'},
                {'word': 'TREE', 'clue': 'Tall plant'},
                {'word': 'BOOK', 'clue': 'Reading material'},
                {'word': 'CHAIR', 'clue': 'Sitting furniture'},
                {'word': 'TABLE', 'clue': 'Dining furniture'},
                {'word': 'PHONE', 'clue': 'Calling device'},
                {'word': 'WATER', 'clue': 'Clear liquid'},
                {'word': 'PAPER', 'clue': 'Writing material'},
                {'word': 'PENCIL', 'clue': 'Writing tool'}
            ],
            'family': [
                {'word': 'MOM', 'clue': 'Mother'},
                {'word': 'DAD', 'clue': 'Father'},
                {'word': 'SON', 'clue': 'Male child'},
                {'word': 'AUNT', 'clue': 'Parent\'s sister'},
                {'word': 'UNCLE', 'clue': 'Parent\'s brother'},
                {'word': 'SISTER', 'clue': 'Female sibling'},
                {'word': 'BROTHER', 'clue': 'Male sibling'},
                {'word': 'COUSIN', 'clue': 'Aunt\'s child'},
                {'word': 'BABY', 'clue': 'Newborn'},
                {'word': 'CHILD', 'clue': 'Young person'}
            ]
        }
    
    def generate_puzzle(self, theme: str = 'easy_general', grid_size: int = 13) -> CrosswordGrid:
        """Generate a crossword puzzle with the given theme."""
        grid = CrosswordGrid(grid_size, grid_size)
        
        # Get words for the theme
        if theme not in self.word_lists:
            theme = 'easy_general'
        
        words = self.word_lists[theme].copy()
        random.shuffle(words)
        
        # Place first word in the center
        if words:
            first_word = words.pop(0)
            start_row = grid_size // 2
            start_col = (grid_size - len(first_word['word'])) // 2
            grid.place_word(first_word['word'], start_row, start_col, 'across', first_word['clue'])
        
        # Try to place remaining words
        placed_count = 1
        max_attempts = 50
        
        for attempt in range(max_attempts):
            if len(words) == 0 or placed_count >= 8:
                break
                
            word_index = random.randint(0, len(words) - 1)
            word_data = words[word_index]
            word = word_data['word']
            clue = word_data['clue']
            
            placed = False
            
            # Try to find intersections with existing words
            for existing_word in grid.words:
                if placed:
                    break
                
                existing = existing_word['word']
                
                # Find common letters
                for i, letter in enumerate(word):
                    if letter in existing:
                        for j, existing_letter in enumerate(existing):
                            if letter == existing_letter:
                                # Calculate placement position
                                if existing_word['direction'] == 'across':
                                    new_row = existing_word['row'] - i
                                    new_col = existing_word['col'] + j
                                    new_direction = 'down'
                                else:
                                    new_row = existing_word['row'] + j
                                    new_col = existing_word['col'] - i
                                    new_direction = 'across'
                                
                                # Check bounds
                                if (new_row >= 0 and new_col >= 0 and
                                    ((new_direction == 'across' and new_col + len(word) <= grid_size) or
                                     (new_direction == 'down' and new_row + len(word) <= grid_size))):
                                    
                                    if grid.place_word(word, new_row, new_col, new_direction, clue):
                                        placed = True
                                        placed_count += 1
                                        break
            
            if not placed:
                # Try random placement
                for _ in range(5):
                    row = random.randint(0, grid_size - 1)
                    col = random.randint(0, grid_size - 1)
                    direction = random.choice(['across', 'down'])
                    
                    if grid.place_word(word, row, col, direction, clue):
                        placed = True
                        placed_count += 1
                        break
            
            # Remove the word whether placed or not to avoid infinite loops
            words.pop(word_index)
        
        return grid
    
    def generate_clue_list(self, grid: CrosswordGrid) -> str:
        """Generate formatted clue list for the puzzle."""
        result = []
        
        if grid.across_clues:
            result.append("ACROSS:")
            for number in sorted(grid.across_clues.keys()):
                result.append(f"  {number}. {grid.across_clues[number]}")
        
        if grid.down_clues:
            result.append("\nDOWN:")
            for number in sorted(grid.down_clues.keys()):
                result.append(f"  {number}. {grid.down_clues[number]}")
        
        return "\n".join(result)

def generate_complete_crossword_content(puzzle_count: int = 25) -> str:
    """Generate complete crossword content for a book."""
    generator = CrosswordGenerator()
    themes = list(generator.word_lists.keys())
    
    content = []
    generated_grids = []  # Store grids for answer key
    
    # Title and introduction
    content.append("LARGE PRINT CROSSWORD MASTERS: VOLUME 1")
    content.append("Easy Large Print Crosswords for Seniors")
    content.append("By Senior Puzzle Studio")
    content.append("\n" + "="*50 + "\n")
    
    # Introduction
    content.append("INTRODUCTION")
    content.append(f"\nWelcome to Large Print Crossword Masters! This book contains {puzzle_count} carefully crafted crossword puzzles designed specifically for seniors who appreciate larger, easier-to-read text.")
    content.append("\nBenefits of Large Print Crosswords:")
    content.append("✓ LARGE, CLEAR FONTS - Easy on the eyes, no squinting required")
    content.append("✓ SENIOR-FRIENDLY DESIGN - Perfect difficulty level for relaxing fun")
    content.append("✓ HIGH-QUALITY PUZZLES - Engaging themes and satisfying solutions")
    content.append("✓ SPACIOUS GRIDS - Plenty of room to write your answers")
    content.append("✓ BRAIN TRAINING - Keep your mind sharp and active")
    content.append("\n" + "="*50 + "\n")
    
    # Instructions
    content.append("HOW TO SOLVE CROSSWORDS")
    content.append("\n1. Read the clues carefully")
    content.append("2. Start with clues you know for certain") 
    content.append("3. Use crossing letters to help solve difficult clues")
    content.append("4. Don't be afraid to guess and erase")
    content.append("5. Take breaks when needed")
    content.append("6. Have fun and enjoy the process!")
    content.append("\n" + "="*50 + "\n")
    
    # Generate puzzles
    for i in range(puzzle_count):
        theme = themes[i % len(themes)]
        theme_name = theme.replace('_', ' ').title()
        
        content.append(f"PUZZLE {i+1}: {theme_name}")
        content.append("\n")
        
        # Generate the crossword
        grid = generator.generate_puzzle(theme)
        generated_grids.append(grid)  # Store for answer key
        
        # Add the grid
        content.append(grid.to_large_print_string())
        content.append("\n")
        
        # Add the clues
        clues = generator.generate_clue_list(grid)
        content.append(clues)
        content.append("\n" + "-"*40 + "\n")
    
    # Answer key section
    content.append("\n" + "="*50)
    content.append("ANSWER KEY")
    content.append("="*50 + "\n")
    
    for i, grid in enumerate(generated_grids):
        content.append(f"PUZZLE {i+1} SOLUTION:")
        content.append(grid.to_solution_string())
        content.append("\n")
    
    # Back matter
    content.append("="*50)
    content.append("Thank you for choosing Large Print Crossword Masters!")
    content.append("\nVisit https://senior-puzzle-studio.carrd.co for more puzzles!")
    content.append("© 2025 Senior Puzzle Studio | All Rights Reserved")
    
    return "\n".join(content)

if __name__ == "__main__":
    # Test the generator
    generator = CrosswordGenerator()
    grid = generator.generate_puzzle('kitchen')
    print(grid.to_large_print_string())
    print("\n")
    print(generator.generate_clue_list(grid))