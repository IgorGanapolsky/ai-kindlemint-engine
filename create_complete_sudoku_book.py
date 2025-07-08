#!/usr/bin/env python3
"""
Create a complete Large Print Sudoku book with introduction and proper formatting
"""

import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_sudoku_grid():
    """Generate a valid 9x9 Sudoku puzzle with clues"""
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
    
    # Create puzzle by removing numbers (more removed = harder)
    puzzle = [row[:] for row in base]
    cells_to_remove = 45  # Medium difficulty
    
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
        "DIFFICULTY LEVEL:",
        "This book contains MEDIUM difficulty puzzles, perfect for",
        "daily brain training. Each puzzle has exactly one solution.",
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
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(x_offset + 4.25*inch, y_offset + 4.8*inch, f"Puzzle #{puzzle_num}")
    
    # Grid settings
    cell_size = 0.5*inch
    grid_size = cell_size * 9
    start_x = x_offset + (8.5*inch - grid_size) / 2
    start_y = y_offset + 0.5*inch
    
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
    c.drawCentredString(width/2, height - 5*inch, "100 Medium Difficulty Puzzles")
    c.drawCentredString(width/2, height - 5.5*inch, "Perfect for Daily Brain Training")
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 7*inch, "Large Print Edition")
    c.drawCentredString(width/2, height - 7.5*inch, "Easy on the Eyes")
    c.showPage()
    
    # Introduction page
    draw_introduction_page(c, width, height)
    c.showPage()
    
    # Generate 100 puzzles
    puzzles = []
    for i in range(100):
        puzzle, solution = create_sudoku_grid()
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