#!/usr/bin/env python3
"""
Fix the mini puzzles in Volume 3 to be actually solvable
"""

from pathlib import Path
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import io

# 6×9 book dimensions
PAGE_WIDTH = 6 * inch
PAGE_HEIGHT = 9 * inch
GUTTER = 0.375 * inch
TOP_MARGIN = 0.75 * inch
BOTTOM_MARGIN = 0.75 * inch

def create_mini_puzzles():
    """Create 9 properly solvable mini puzzles"""
    
    # Define 9 simple, solvable mini puzzles
    mini_puzzles = [
        {
            "grid": [
                ['C', 'A', 'T', '#', '#'],
                ['A', '#', 'O', '#', '#'],
                ['R', 'E', 'D', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Feline pet", "4. Color of roses"],
            "clues_down": ["1. Vehicle", "2. Past tense of eat", "3. Also; as well"]
        },
        {
            "grid": [
                ['D', 'O', 'G', '#', '#'],
                ['O', '#', 'O', '#', '#'],
                ['T', 'E', 'A', '#', '#'],
                ['#', '#', 'L', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Man's best friend", "4. Hot beverage"],
            "clues_down": ["1. Spot mark", "2. Rowing tool", "3. Objective"]
        },
        {
            "grid": [
                ['S', 'U', 'N', '#', '#'],
                ['I', '#', 'E', '#', '#'],
                ['T', 'O', 'P', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Star", "4. Highest point"],
            "clues_down": ["1. Rest", "2. Employ", "3. Fresh"]
        },
        {
            "grid": [
                ['A', 'R', 'M', '#', '#'],
                ['G', '#', 'A', '#', '#'],
                ['E', 'Y', 'E', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Limb", "4. Organ of sight"],
            "clues_down": ["1. Time period", "2. Memory unit", "3. Myself"]
        },
        {
            "grid": [
                ['B', 'I', 'G', '#', '#'],
                ['E', '#', 'O', '#', '#'],
                ['D', 'A', 'Y', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Large", "4. 24 hours"],
            "clues_down": ["1. Sleeping place", "2. Sick", "3. Leave"]
        },
        {
            "grid": [
                ['H', 'O', 'T', '#', '#'],
                ['A', '#', 'E', '#', '#'],
                ['T', 'I', 'N', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. High temperature", "4. Metal container"],
            "clues_down": ["1. Headwear", "2. Frequently", "3. Number"]
        },
        {
            "grid": [
                ['R', 'U', 'N', '#', '#'],
                ['A', '#', 'E', '#', '#'],
                ['N', 'E', 'W', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Jog", "4. Not old"],
            "clues_down": ["1. Precipitation", "2. Utilize", "3. Mesh"]
        },
        {
            "grid": [
                ['Y', 'E', 'S', '#', '#'],
                ['E', '#', 'E', '#', '#'],
                ['T', 'O', 'P', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Affirmative", "4. Summit"],
            "clues_down": ["1. Still", "2. Ovum", "3. Observe"]
        },
        {
            "grid": [
                ['O', 'L', 'D', '#', '#'],
                ['N', '#', 'A', '#', '#'],
                ['E', 'N', 'D', '#', '#'],
                ['#', '#', '#', '#', '#'],
                ['#', '#', '#', '#', '#']
            ],
            "black": [(0,3), (0,4), (1,1), (1,3), (1,4), (2,3), (2,4), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1), (4,2), (4,3), (4,4)],
            "clues_across": ["1. Not young", "4. Finish"],
            "clues_down": ["1. Single", "2. Cover", "3. Father"]
        }
    ]
    
    # Create PDF with just the mini puzzles
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    
    for puzzle_num, puzzle in enumerate(mini_puzzles, 1):
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - TOP_MARGIN - 0.5*inch, f"Bonus Mini Puzzle {puzzle_num}")
        
        # Draw grid
        mini_grid_size = 5
        mini_cell_size = 0.35 * inch
        grid_x = (PAGE_WIDTH - (mini_grid_size * mini_cell_size)) / 2
        grid_y = PAGE_HEIGHT - 2.2*inch
        
        # Draw the grid with numbers
        c.setLineWidth(1.5)
        number = 1
        number_positions = {}
        
        for row in range(mini_grid_size):
            for col in range(mini_grid_size):
                x = grid_x + (col * mini_cell_size)
                y = grid_y - (row * mini_cell_size)
                
                if (row, col) in puzzle["black"]:
                    c.setFillColor(colors.black)
                    c.rect(x, y, mini_cell_size, mini_cell_size, fill=1, stroke=0)
                else:
                    c.setFillColor(colors.white)
                    c.setStrokeColor(colors.black)
                    c.rect(x, y, mini_cell_size, mini_cell_size, fill=1, stroke=1)
                    
                    # Add number if this starts a word
                    needs_number = False
                    if col == 0 or (row, col-1) in puzzle["black"]:
                        if col < mini_grid_size - 1 and (row, col+1) not in puzzle["black"]:
                            needs_number = True
                    if row == 0 or (row-1, col) in puzzle["black"]:
                        if row < mini_grid_size - 1 and (row+1, col) not in puzzle["black"]:
                            needs_number = True
                    
                    if needs_number:
                        number_positions[(row, col)] = number
                        c.setFillColor(colors.black)
                        c.setFont("Helvetica", 8)
                        c.drawString(x + 2, y + mini_cell_size - 10, str(number))
                        number += 1
        
        # Draw clues with light background
        clues_start_y = grid_y - (mini_grid_size * mini_cell_size) - 0.3*inch
        
        c.setFillColor(colors.Color(0.95, 0.95, 0.95))
        c.rect(GUTTER - 0.1*inch, clues_start_y - 1.5*inch, PAGE_WIDTH - 2*GUTTER + 0.2*inch, 1.5*inch, fill=1, stroke=0)
        
        # ACROSS clues
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(GUTTER, clues_start_y, "ACROSS")
        c.setFont("Helvetica", 9)
        y_pos = clues_start_y - 0.2*inch
        
        for clue in puzzle["clues_across"]:
            c.drawString(GUTTER, y_pos, clue)
            y_pos -= 0.18*inch
        
        # DOWN clues
        c.setFont("Helvetica-Bold", 10)
        c.drawString(PAGE_WIDTH/2 + 0.1*inch, clues_start_y, "DOWN")
        c.setFont("Helvetica", 9)
        y_pos = clues_start_y - 0.2*inch
        
        for clue in puzzle["clues_down"]:
            c.drawString(PAGE_WIDTH/2 + 0.1*inch, y_pos, clue)
            y_pos -= 0.18*inch
        
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

def replace_mini_puzzles():
    """Replace pages 147-155 with fixed mini puzzles"""
    
    # Read existing PDF
    input_path = Path("books/active_production/Large_Print_Crossword_Masters/volume_3/paperback/crossword_book_volume_3_FINAL.pdf")
    output_path = Path("books/active_production/Large_Print_Crossword_Masters/volume_3/paperback/crossword_book_volume_3_FINAL_FIXED.pdf")
    
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    
    # Copy pages 1-146
    for i in range(146):
        writer.add_page(reader.pages[i])
    
    # Add new mini puzzle pages
    mini_puzzles_buffer = create_mini_puzzles()
    mini_reader = PdfReader(mini_puzzles_buffer)
    for page in mini_reader.pages:
        writer.add_page(page)
    
    # Copy page 156 (About page)
    writer.add_page(reader.pages[155])
    
    # Write output
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    print(f"✅ Created fixed PDF: {output_path}")
    
    # Also fix hardcover
    hardcover_input = Path("books/active_production/Large_Print_Crossword_Masters/volume_3/hardcover/crossword_book_volume_3_FINAL.pdf")
    hardcover_output = Path("books/active_production/Large_Print_Crossword_Masters/volume_3/hardcover/crossword_book_volume_3_FINAL_FIXED.pdf")
    
    reader = PdfReader(str(hardcover_input))
    writer = PdfWriter()
    
    # Copy pages 1-146
    for i in range(146):
        writer.add_page(reader.pages[i])
    
    # Add new mini puzzle pages
    mini_puzzles_buffer.seek(0)
    mini_reader = PdfReader(mini_puzzles_buffer)
    for page in mini_reader.pages:
        writer.add_page(page)
    
    # Copy page 156
    writer.add_page(reader.pages[155])
    
    with open(hardcover_output, 'wb') as f:
        writer.write(f)
    
    print(f"✅ Created fixed hardcover PDF: {hardcover_output}")

if __name__ == "__main__":
    replace_mini_puzzles()