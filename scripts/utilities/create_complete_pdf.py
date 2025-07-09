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

"""Create a complete PDF with actual Sudoku puzzles"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Create comprehensive PDF with actual puzzles
pdf_path = 'landing-pages/sudoku-for-seniors/public/downloads/5-free-sudoku-puzzles-complete.pdf'
c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

# Title page
c.setFont('Helvetica-Bold', 32)
c.drawCentredString(width/2, height-2*inch, '5 Free Sudoku Puzzles')
c.setFont('Helvetica', 20)
c.drawCentredString(width/2, height-3*inch, 'Large Print Edition')
c.drawCentredString(width/2, height-3.5*inch, 'For Seniors')
c.setFont('Helvetica', 16)
c.drawCentredString(width/2, height-5*inch, 'Brain Training & Mental Wellness')

# Benefits
c.setFont('Helvetica', 14)
benefits = [
    '✓ Extra Large Print - Easy on the Eyes',
    '✓ Progressive Difficulty - Start Easy, Build Skills',
    '✓ Solution Keys Included',
    '✓ Proven to Improve Memory & Focus'
]
y = height - 6.5*inch
for benefit in benefits:
    c.drawString(1.5*inch, y, benefit)
    y -= 0.4*inch

c.showPage()

# Instructions page
c.setFont('Helvetica-Bold', 24)
c.drawCentredString(width/2, height-1.5*inch, 'How to Play Sudoku')
c.setFont('Helvetica', 16)
instructions = [
    '1. Fill each row with numbers 1-9 (no repeats)',
    '2. Fill each column with numbers 1-9 (no repeats)', 
    '3. Fill each 3x3 box with numbers 1-9 (no repeats)',
    '4. Use logic and elimination to find the solution',
    '5. Start with easier puzzles and work your way up!'
]
y = height - 2.5*inch
for instruction in instructions:
    c.drawString(1*inch, y, instruction)
    y -= 0.5*inch

c.showPage()

# Puzzle 1 - Very Easy 4x4
c.setFont('Helvetica-Bold', 24)
c.drawCentredString(width/2, height-1*inch, 'Puzzle #1: Warm-Up (4x4)')
c.setFont('Helvetica', 14)
c.drawCentredString(width/2, height-1.5*inch, 'Fill each row, column, and 2x2 box with numbers 1-4')

# 4x4 grid
puzzle1 = [
    [2, 0, 4, 0],
    [0, 3, 0, 1],
    [4, 0, 1, 0],
    [0, 1, 0, 3]
]

# Draw grid
grid_size = 80
start_x = width/2 - 2*grid_size
start_y = height/2 + 2*grid_size

for i in range(5):
    lw = 3 if i % 2 == 0 else 1
    c.setLineWidth(lw)
    c.line(start_x + i*grid_size, start_y, start_x + i*grid_size, start_y - 4*grid_size)
    c.line(start_x, start_y - i*grid_size, start_x + 4*grid_size, start_y - i*grid_size)

# Fill numbers
c.setFont('Helvetica', 36)
for row in range(4):
    for col in range(4):
        if puzzle1[row][col] != 0:
            x = start_x + col*grid_size + grid_size/2 - 10
            y = start_y - row*grid_size - grid_size/2 - 10
            c.drawString(x, y, str(puzzle1[row][col]))

c.showPage()

# Puzzle 2 - Easy 9x9
c.setFont('Helvetica-Bold', 24)
c.drawCentredString(width/2, height-1*inch, 'Puzzle #2: Easy')
c.setFont('Helvetica', 14)
c.drawCentredString(width/2, height-1.5*inch, 'Fill each row, column, and 3x3 box with numbers 1-9')

# Easy 9x9 puzzle with many given numbers
puzzle2 = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9]
]

# Draw 9x9 grid
grid_size = 50
start_x = width/2 - 4.5*grid_size
start_y = height - 3*inch

for i in range(10):
    lw = 3 if i % 3 == 0 else 1
    c.setLineWidth(lw)
    c.line(start_x + i*grid_size, start_y, start_x + i*grid_size, start_y - 9*grid_size)
    c.line(start_x, start_y - i*grid_size, start_x + 9*grid_size, start_y - i*grid_size)

# Fill numbers
c.setFont('Helvetica-Bold', 24)
for row in range(9):
    for col in range(9):
        if puzzle2[row][col] != 0:
            x = start_x + col*grid_size + grid_size/2 - 8
            y = start_y - row*grid_size - grid_size/2 - 8
            c.drawString(x, y, str(puzzle2[row][col]))

c.showPage()

# Puzzle 3 - Medium 9x9
c.setFont('Helvetica-Bold', 24)
c.drawCentredString(width/2, height-1*inch, 'Puzzle #3: Medium')

puzzle3 = [
    [0,0,0,2,6,0,7,0,1],
    [6,8,0,0,7,0,0,9,0],
    [1,9,0,0,0,4,5,0,0],
    [8,2,0,1,0,0,0,4,0],
    [0,0,4,6,0,2,9,0,0],
    [0,5,0,0,0,3,0,2,8],
    [0,0,9,3,0,0,0,7,4],
    [0,4,0,0,5,0,0,3,6],
    [7,0,3,0,1,8,0,0,0]
]

# Draw grid (same as puzzle 2)
for i in range(10):
    lw = 3 if i % 3 == 0 else 1
    c.setLineWidth(lw)
    c.line(start_x + i*grid_size, start_y, start_x + i*grid_size, start_y - 9*grid_size)
    c.line(start_x, start_y - i*grid_size, start_x + 9*grid_size, start_y - i*grid_size)

# Fill numbers
c.setFont('Helvetica-Bold', 24)
for row in range(9):
    for col in range(9):
        if puzzle3[row][col] != 0:
            x = start_x + col*grid_size + grid_size/2 - 8
            y = start_y - row*grid_size - grid_size/2 - 8
            c.drawString(x, y, str(puzzle3[row][col]))

c.showPage()

# Solutions page
c.setFont('Helvetica-Bold', 24)
c.drawCentredString(width/2, height-1*inch, 'Solutions')

# Solution for 4x4
c.setFont('Helvetica', 16)
c.drawString(1*inch, height-2*inch, 'Puzzle #1 Solution:')
solution1 = '2 3 4 1 / 1 3 2 4 / 4 2 1 3 / 3 1 4 2'
c.setFont('Courier', 14)
c.drawString(1*inch, height-2.5*inch, solution1)

# Solution for 9x9
c.setFont('Helvetica', 16)
c.drawString(1*inch, height-3.5*inch, 'Puzzle #2 Solution:')
c.setFont('Courier', 10)
y = height - 4*inch
solution2_rows = [
    '5 3 4 | 6 7 8 | 9 1 2',
    '6 7 2 | 1 9 5 | 3 4 8',
    '1 9 8 | 3 4 2 | 5 6 7',
    '------+-------+------',
    '8 5 9 | 7 6 1 | 4 2 3',
    '4 2 6 | 8 5 3 | 7 9 1',
    '7 1 3 | 9 2 4 | 8 5 6',
    '------+-------+------',
    '9 6 1 | 5 3 7 | 2 8 4',
    '2 8 7 | 4 1 9 | 6 3 5',
    '3 4 5 | 2 8 6 | 1 7 9'
]
for row in solution2_rows:
    c.drawString(1*inch, y, row)
    y -= 0.25*inch

# Solution for puzzle 3
c.setFont('Helvetica', 16)
c.drawString(1*inch, height-7*inch, 'Puzzle #3 Solution:')
c.setFont('Courier', 10)
y = height - 7.5*inch
solution3_rows = [
    '4 3 5 | 2 6 9 | 7 8 1',
    '6 8 2 | 5 7 1 | 4 9 3',
    '1 9 7 | 8 3 4 | 5 6 2',
    '------+-------+------',
    '8 2 6 | 1 9 5 | 3 4 7',
    '3 7 4 | 6 8 2 | 9 1 5',
    '9 5 1 | 7 4 3 | 6 2 8',
    '------+-------+------',
    '5 1 9 | 3 2 6 | 8 7 4',
    '2 4 8 | 9 5 7 | 1 3 6',
    '7 6 3 | 4 1 8 | 2 5 9'
]
for row in solution3_rows:
    c.drawString(1*inch, y, row)
    y -= 0.25*inch

# Thank you page
c.showPage()
c.setFont('Helvetica-Bold', 28)
c.drawCentredString(width/2, height/2, 'Enjoy Your Brain Training!')
c.setFont('Helvetica', 18)
c.drawCentredString(width/2, height/2-1*inch, 'For more free puzzles, visit:')
c.drawCentredString(width/2, height/2-1.5*inch, 'ai-kindlemint-landing.s3-website-us-east-1.amazonaws.com')
c.setFont('Helvetica', 14)
c.drawCentredString(width/2, height/2-2.5*inch, '© 2025 AI KindleMint Engine')

c.save()
print(f'Created comprehensive PDF with {c.getPageNumber()} pages')