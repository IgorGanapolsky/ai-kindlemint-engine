#!/usr/bin/env python3

    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>HOW TO SOLVE:</b> Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "<b>PUZZLE RULES:</b> Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "<b>SOLVING GOAL:</b> Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "<b>GAME RULES:</b> Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>CHALLENGE RULES:</b> Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "<b>SOLVING INSTRUCTIONS:</b> Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "<b>PUZZLE OBJECTIVE:</b> Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "<b>GAME OBJECTIVE:</b> Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>EXPERT CHALLENGE:</b> Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "<b>ADVANCED RULES:</b> Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "<b>MASTER PUZZLE:</b> Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "<b>CHALLENGE GOAL:</b> Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!",
                "<b>💡 HINT:</b> Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "<b>💡 STRATEGY:</b> Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "<b>💡 APPROACH:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 METHOD:</b> If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "<b>💡 TECHNIQUE:</b> Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "<b>💡 SHORTCUT:</b> Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "<b>💡 STRATEGY:</b> Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "<b>💡 TECHNIQUE:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "<b>💡 METHOD:</b> When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "<b>💡 APPROACH:</b> If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "<b>💡 HINT:</b> Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "<b>💡 STRATEGY:</b> Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "<b>💡 EXPERT TIP:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-WING:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 ADVANCED:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 FORCING:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "<b>💡 PATTERN:</b> Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "<b>💡 PERSISTENCE:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

"""
Create a complete Large Print Sudoku book with introduction and proper formatting
"""

import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_sudoku_grid(difficulty_level="medium"):
    """Generate a valid 9x9 Sudoku puzzle with clues based on difficulty"""
    # Base valid completed grid
    base = [
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9]
    ]
    
    # Shuffle rows within groups
    for group in range(3):
        rows = list(range(group*3, (group+1)*3))
        random.shuffle(rows)
        for i, row in enumerate(rows):
            if i != row % 3:
                base[group*3 + i], base[row] = base[row], base[group*3 + i]
    
    # Shuffle columns within groups  
    for group in range(3):
        cols = list(range(group*3, (group+1)*3))
        random.shuffle(cols)
        for i, col in enumerate(cols):
            if i != col % 3:
                for row in range(9):
                    base[row][group*3 + i], base[row][col] = base[row][col], base[row][group*3 + i]
    
    # Create puzzle by removing numbers based on difficulty
    puzzle = [row[:] for row in base]
    
    # Adjust number of clues based on difficulty
    if difficulty_level == "easy":
        cells_to_remove = 30  # 51 clues (very easy)
    elif difficulty_level == "medium":
        cells_to_remove = 40  # 41 clues (medium)
    else:  # hard
        cells_to_remove = 50  # 31 clues (harder)
    
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    
    for i in range(cells_to_remove):
        row, col = cells[i]
        puzzle[row][col] = 0
    
    return puzzle, base

def draw_introduction_page(c, width, height):
    """Draw the introduction page with how to play instructions"""
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 1.5*inch, "How to Play Sudoku")
    
    c.setFont("Helvetica", 14)  # Smaller font to fit better
    y = height - 2.5*inch
    left_margin = 1*inch
    right_margin = 1*inch
    max_width = width - left_margin - right_margin
    
    instructions = [
        "Sudoku is a logic-based number puzzle that's perfect for",
        "keeping your mind sharp!",
        "",
        "THE RULES:",
        "• Fill in the empty squares with numbers 1-9",
        "• Each row must contain the numbers 1-9 (no repeats)",
        "• Each column must contain the numbers 1-9 (no repeats)",
        "• Each 3x3 box must contain the numbers 1-9 (no repeats)",
        "",
        "TIPS FOR SUCCESS:",
        "• Start with rows, columns, or boxes that have the most",
        "  numbers filled in",
        "• Look for numbers that can only go in one place",
        "• Use pencil so you can erase if needed",
        "• Take your time - there's no time limit!",
        "",
        "PROGRESSIVE DIFFICULTY:",
        "• Puzzles 1-25: EASY (50+ clues) - Perfect for warming up",
        "• Puzzles 26-75: MEDIUM (40+ clues) - Build your skills",
        "• Puzzles 76-100: HARD (30+ clues) - Challenge yourself!",
        "",
        "Ready? Turn the page and let's begin!"
    ]
    
    for line in instructions:
        if line.startswith("THE RULES:") or line.startswith("TIPS FOR SUCCESS:") or line.startswith("DIFFICULTY LEVEL:"):
            c.setFont("Helvetica-Bold", 14)
        else:
            c.setFont("Helvetica", 14)
        
        if line:
            c.drawString(left_margin, y, line)
        y -= 0.3*inch

def draw_sudoku_puzzle(c, puzzle, puzzle_num, x_offset, y_offset):
    """Draw a single Sudoku puzzle on the canvas"""
    # Title - MOVED HIGHER TO AVOID OVERLAP
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(x_offset + 4.25*inch, y_offset + 6.5*inch, f"Puzzle #{puzzle_num}")
    
    # Add difficulty indicator instead of repetitive instructions
    if puzzle_num <= 25:
        difficulty = "EASY"
    elif puzzle_num <= 75:
        difficulty = "MEDIUM"
    else:
        difficulty = "HARD"
    
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(x_offset + 4.25*inch, y_offset + 5.8*inch, f"Difficulty: {difficulty}")
    
    # Grid settings
    cell_size = 0.5*inch
    grid_size = cell_size * 9
    start_x = x_offset + (8.5*inch - grid_size) / 2
    start_y = y_offset + 0.5*inch  # Proper position for grid
    
    # Draw the grid
    c.setLineWidth(1)
    
    # Draw cells
    for row in range(10):
        y = start_y + row * cell_size
        c.line(start_x, y, start_x + grid_size, y)
    
    for col in range(10):
        x = start_x + col * cell_size
        c.line(x, start_y, x, start_y + grid_size)
    
    # Draw thick lines for 3x3 boxes
    c.setLineWidth(3)
    for i in range(4):
        # Horizontal thick lines
        y = start_y + i * 3 * cell_size
        c.line(start_x, y, start_x + grid_size, y)
        # Vertical thick lines
        x = start_x + i * 3 * cell_size
        c.line(x, start_y, x, start_y + grid_size)
    
    # Fill in the numbers
    c.setFont("Helvetica", 24)
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] != 0:
                x = start_x + col * cell_size + cell_size/2
                y = start_y + (8-row) * cell_size + cell_size/2 - 8
                c.drawCentredString(x, y, str(puzzle[row][col]))

def create_sudoku_book(filename):
    """Create a complete Sudoku book with 100 puzzles"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title page
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(width/2, height - 3*inch, "Large Print Sudoku")
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height - 4*inch, "Volume 1")
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2, height - 5*inch, "100 Progressive Puzzles")
    c.drawCentredString(width/2, height - 5.5*inch, "25 Easy • 50 Medium • 25 Hard")
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 7*inch, "Large Print Edition")
    c.drawCentredString(width/2, height - 7.5*inch, "Easy on the Eyes")
    c.showPage()
    
    # Introduction page
    draw_introduction_page(c, width, height)
    c.showPage()
    
    # Generate 100 puzzles with varying difficulty
    puzzles = []
    for i in range(100):
        if i < 25:
            difficulty = "easy"
        elif i < 75:
            difficulty = "medium"
        else:
            difficulty = "hard"
        
        puzzle, solution = create_sudoku_grid(difficulty)
        puzzles.append((puzzle, solution))
    
    # Draw puzzles (1 per page for large print)
    for i, (puzzle, solution) in enumerate(puzzles):
        draw_sudoku_puzzle(c, puzzle, i+1, 0, 0)
        c.showPage()
    
    # Solutions section
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height/2, "SOLUTIONS")
    c.showPage()
    
    # Draw solutions (4 per page, smaller)
    for i in range(0, 100, 4):
        for j in range(4):
            if i + j < 100:
                puzzle_num = i + j + 1
                _, solution = puzzles[i + j]
                
                # Position for 4 grids per page
                x_offset = (j % 2) * 4.25*inch
                y_offset = (1 - j // 2) * 5.5*inch
                
                # Draw smaller solution grid
                c.setFont("Helvetica-Bold", 14)
                c.drawString(x_offset + 1*inch, y_offset + 5*inch, f"Puzzle #{puzzle_num}")
                
                # Grid settings for solutions (smaller)
                cell_size = 0.35*inch
                grid_size = cell_size * 9
                start_x = x_offset + 1*inch
                start_y = y_offset + 1.5*inch
                
                # Draw the solution grid
                c.setLineWidth(0.5)
                for row in range(10):
                    y = start_y + row * cell_size
                    c.line(start_x, y, start_x + grid_size, y)
                
                for col in range(10):
                    x = start_x + col * cell_size
                    c.line(x, start_y, x, start_y + grid_size)
                
                # Draw thick lines for 3x3 boxes
                c.setLineWidth(2)
                for k in range(4):
                    y = start_y + k * 3 * cell_size
                    c.line(start_x, y, start_x + grid_size, y)
                    x = start_x + k * 3 * cell_size
                    c.line(x, start_y, x, start_y + grid_size)
                
                # Fill in the solution numbers
                c.setFont("Helvetica", 12)
                for row in range(9):
                    for col in range(9):
                        x = start_x + col * cell_size + cell_size/2
                        y = start_y + (8-row) * cell_size + cell_size/2 - 4
                        c.drawCentredString(x, y, str(solution[row][col]))
        
        c.showPage()
    
    # Back cover
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height/2 + 1*inch, "Congratulations on completing")
    c.drawCentredString(width/2, height/2 + 0.5*inch, "Large Print Sudoku Volume 1!")
    c.drawCentredString(width/2, height/2 - 0.5*inch, "Keep your mind sharp with daily puzzles.")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height/2 - 2*inch, "Look for Volume 2 coming soon!")
    
    c.save()
    print(f"Created {filename} with 100 puzzles, introduction, and solutions!")

if __name__ == "__main__":
    create_sudoku_book("Large_Print_Sudoku_Complete.pdf")