#!/usr/bin/env python3
"""
Simple test to create ONE puzzle and verify rendering
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Create a simple test PDF with one puzzle
c = canvas.Canvas("test_sudoku.pdf", pagesize=letter)

# Title
c.setFont("Helvetica-Bold", 24)
c.drawCentredString(4.25 * inch, 10 * inch, "Test Puzzle")

# Grid position
grid_x = 1.5 * inch
grid_y = 3 * inch
cell_size = 0.6 * inch

# Draw grid
c.setStrokeColorRGB(0, 0, 0)
for i in range(10):
    if i % 3 == 0:
        c.setLineWidth(3)
    else:
        c.setLineWidth(1)

    # Vertical
    c.line(
        grid_x + i * cell_size, grid_y, grid_x + i * cell_size, grid_y + 9 * cell_size
    )
    # Horizontal
    c.line(
        grid_x, grid_y + i * cell_size, grid_x + 9 * cell_size, grid_y + i * cell_size
    )

# Test grid with known clues
test_grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

# Count and draw clues
clue_count = 0
c.setFont("Helvetica-Bold", 28)
c.setFillColorRGB(0, 0, 0)  # Pure black

for row in range(9):
    for col in range(9):
        if test_grid[row][col] != 0:
            clue_count += 1
            x = grid_x + col * cell_size + cell_size / 2
            y = grid_y + (8 - row) * cell_size + cell_size / 2 - 8
            c.drawCentredString(x, y, str(test_grid[row][col]))

# Add clue count info
c.setFont("Helvetica", 14)
c.drawString(
    grid_x,
    grid_y - 0.5 * inch,
    f"This puzzle has {clue_count} clues (should be visible in BOLD)",
)
c.drawString(grid_x, grid_y - 0.8 * inch, "Empty cells should be completely blank")

c.save()
print(f"✅ Test PDF created with {clue_count} clues")
print("Please visually inspect test_sudoku.pdf")
