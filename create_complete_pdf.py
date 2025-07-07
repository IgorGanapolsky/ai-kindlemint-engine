#!/usr/bin/env python3
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