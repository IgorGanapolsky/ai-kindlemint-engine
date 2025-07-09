#!/usr/bin/env python3
"""
Generate 5 Free Brain-Boosting Sudoku Puzzles for Lead Magnet
Specifically designed for seniors 75+ with extra-large print
"""

import os
import sys
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, gray

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from kindlemint.engines.sudoku import SudokuGenerator


class LeadMagnetGenerator:
    def __init__(self):
        self.generator = SudokuGenerator()
        self.output_dir = "landing-pages/sudoku-for-seniors/public/downloads"
        self.pdf_path = os.path.join(self.output_dir, "5-free-sudoku-puzzles.pdf")
        
    def _set_font(self, canvas, font_name, size):
        """Set font - always use Helvetica for reliability"""
        # Always use Helvetica to avoid font issues
        if 'Bold' in font_name or 'bold' in font_name.lower():
            canvas.setFont('Helvetica-Bold', size)
        else:
            canvas.setFont('Helvetica', size)
    
    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "💡 TIP: Start with rows, columns, or boxes that have the most numbers already filled in!",
                "💡 HINT: Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "💡 STRATEGY: Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "💡 APPROACH: Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "💡 METHOD: If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "💡 TECHNIQUE: Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "💡 SHORTCUT: Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "💡 TIP: Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "💡 STRATEGY: Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "💡 TECHNIQUE: Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "💡 METHOD: When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "💡 APPROACH: If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "💡 HINT: Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "💡 STRATEGY: Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "💡 TIP: Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "💡 EXPERT TIP: Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "💡 X-WING: Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "💡 ADVANCED: Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "💡 FORCING: If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "💡 PATTERN: Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "💡 PERSISTENCE: Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]
        
    def generate_puzzles(self):
        """Generate 5 puzzles with progressive difficulty"""
        puzzles = []
        
        # 2 Easy, 2 Medium, 1 Hard
        difficulties = ['easy', 'easy', 'medium', 'medium', 'hard']
        
        for i, difficulty in enumerate(difficulties, 1):
            print(f"Generating puzzle {i} ({difficulty})...")
            puzzle_data = self.generator.generate_puzzle(difficulty)
            puzzles.append({
                'number': i,
                'difficulty': difficulty,
                'puzzle': puzzle_data['grid'],
                'solution': puzzle_data['solution']
            })
            
        return puzzles
    
    def create_pdf(self, puzzles):
        """Create the lead magnet PDF with extra-large print"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        c = canvas.Canvas(self.pdf_path, pagesize=letter)
        width, height = letter
        
        # Cover page
        self._draw_cover_page(c, width, height)
        
        # Introduction page
        c.showPage()
        self._draw_intro_page(c, width, height)
        
        # Puzzles (one per page)
        for puzzle in puzzles:
            c.showPage()
            self._draw_puzzle_page(c, width, height, puzzle)
        
        # Solutions page
        c.showPage()
        self._draw_solutions_page(c, width, height, puzzles)
        
        # Final page with CTA
        c.showPage()
        self._draw_cta_page(c, width, height)
        
        c.save()
        print(f"Lead magnet created: {self.pdf_path}")
    
    def _draw_cover_page(self, c, width, height):
        """Draw the cover page"""
        self._set_font(c, 'Helvetica-Bold', 36)
        c.drawCentredString(width/2, height - 2*inch, "5 FREE")
        c.drawCentredString(width/2, height - 2.8*inch, "Brain-Boosting")
        c.drawCentredString(width/2, height - 3.6*inch, "Sudoku Puzzles")
        
        self._set_font(c, 'Helvetica', 24)
        c.drawCentredString(width/2, height - 5*inch, "Extra-Large Print")
        c.drawCentredString(width/2, height - 5.6*inch, "For Seniors")
        
        self._set_font(c, 'Helvetica', 16)
        c.drawCentredString(width/2, height - 7*inch, "From Senior Puzzle Studio")
        c.drawCentredString(width/2, height - 7.5*inch, "Your Trusted Source for Large Print Puzzles")
    
    def _draw_intro_page(self, c, width, height):
        """Draw the introduction page"""
        self._set_font(c, 'Helvetica-Bold', 28)
        c.drawCentredString(width/2, height - 1.5*inch, "Welcome!")
        
        self._set_font(c, 'Helvetica', 16)
        text_y = height - 2.5*inch
        
        intro_text = [
            "Thank you for downloading these free Sudoku puzzles!",
            "",
            "These puzzles are specially designed for seniors:",
            "• Extra-large 20+ point fonts",
            "• High contrast for easy reading",
            "• Progressive difficulty levels",
            "• Complete solutions included",
            "",
            "How to Play Sudoku:",
            "Fill in the empty cells so that each row, column,",
            "and 3×3 box contains the numbers 1-9 exactly once.",
            "",
            "Start with Puzzle #1 (Easy) and work your way up!",
            "",
            "Enjoy your brain training!",
        ]
        
        for line in intro_text:
            c.drawString(1*inch, text_y, line)
            text_y -= 0.4*inch
        
        # Add Gumroad box on intro page
        text_y -= 0.5*inch
        self._set_font(c, 'Helvetica-Bold', 14)
        c.drawCentredString(width/2, text_y, "📘 Want 100 more puzzles after these 5?")
        text_y -= 0.3*inch
        self._set_font(c, 'Helvetica', 12)
        c.drawCentredString(width/2, text_y, "Get our complete book at: iganapolsky.gumroad.com/l/hjybj")
    
    def _draw_puzzle_page(self, c, width, height, puzzle_data):
        """Draw a single puzzle page"""
        # Header
        self._set_font(c, 'Helvetica-Bold', 24)
        c.drawCentredString(width/2, height - 1*inch, 
                          f"Puzzle #{puzzle_data['number']} - {puzzle_data['difficulty'].title()}")
        
        # Instructions - varied for each puzzle
        self._set_font(c, 'Helvetica', 12)
        instruction = self.get_varied_instructions(puzzle_data['difficulty'], puzzle_data['number'])
        # Wrap long instructions
        words = instruction.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 65:  # Approximate character limit per line
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        y_pos = height - 1.5*inch
        for line in lines:
            c.drawCentredString(width/2, y_pos, line)
            y_pos -= 0.3*inch
        
        # Grid settings - EXTRA LARGE
        grid_size = 6.5 * inch  # Even larger than normal
        cell_size = grid_size / 9
        start_x = (width - grid_size) / 2
        start_y = height - 2.5*inch - grid_size
        
        # Draw grid with proper line weights
        for i in range(10):
            # Thicker lines for 3x3 boxes
            if i % 3 == 0:
                c.setLineWidth(2.5)
            else:
                c.setLineWidth(0.75)
            
            # Vertical lines
            x = start_x + i * cell_size
            c.line(x, start_y, x, start_y + grid_size)
            
            # Horizontal lines
            y = start_y + i * cell_size
            c.line(start_x, y, start_x + grid_size, y)
        
        # Fill in numbers - EXTRA LARGE FONT
        self._set_font(c, 'Helvetica', 32)  # Very large font for better visibility
        puzzle = puzzle_data['puzzle']
        
        for row in range(9):
            for col in range(9):
                number = puzzle[row][col]
                if number != 0:
                    x = start_x + col * cell_size + cell_size / 2
                    y = start_y + (8 - row) * cell_size + cell_size / 2 - 10
                    c.drawCentredString(x, y, str(number))
        
        # Footer tip - varied for each puzzle
        self._set_font(c, 'Helvetica', 14)
        tip = self.get_varied_tips(puzzle_data['difficulty'], puzzle_data['number'])
        c.drawCentredString(width/2, 1.2*inch, tip)
        
        # Add Gumroad link footer
        self._set_font(c, 'Helvetica', 10)
        c.drawCentredString(width/2, 0.6*inch, "Love these puzzles? Get 100 more at: iganapolsky.gumroad.com/l/hjybj")
    
    def _draw_solutions_page(self, c, width, height, puzzles):
        """Draw all solutions on one page"""
        self._set_font(c, 'Helvetica-Bold', 28)
        c.drawCentredString(width/2, height - 1*inch, "Solutions")
        
        # Add description
        self._set_font(c, 'Helvetica', 12)
        c.drawCentredString(width/2, height - 1.5*inch, "Check your answers! Each completed grid shows all numbers 1-9 in every row, column, and 3×3 box.")
        
        # Smaller grids for solutions
        grid_size = 2 * inch
        cell_size = grid_size / 9
        
        # Arrange in 2 columns, 3 rows with proper spacing
        # Move down to avoid overlapping with description text
        positions = [
            (1.5*inch, height - 4.5*inch),    # Row 1, Col 1
            (4.5*inch, height - 4.5*inch),    # Row 1, Col 2
            (1.5*inch, height - 7.5*inch),    # Row 2, Col 1
            (4.5*inch, height - 7.5*inch),    # Row 2, Col 2
            (3*inch, height - 10.5*inch),     # Row 3, Centered
        ]
        
        for idx, (puzzle_data, (x_pos, y_pos)) in enumerate(zip(puzzles, positions)):
            # Label
            self._set_font(c, 'Helvetica-Bold', 12)
            c.drawString(x_pos, y_pos + grid_size + 0.2*inch, 
                        f"Puzzle #{puzzle_data['number']}")
            
            # Draw mini grid
            for i in range(10):
                if i % 3 == 0:
                    c.setLineWidth(1)
                else:
                    c.setLineWidth(0.5)
                
                # Vertical lines
                x = x_pos + i * cell_size
                c.line(x, y_pos, x, y_pos + grid_size)
                
                # Horizontal lines
                y = y_pos + i * cell_size
                c.line(x_pos, y, x_pos + grid_size, y)
            
            # Fill in solution numbers
            self._set_font(c, 'Helvetica', 8)
            solution = puzzle_data['solution']
            
            for row in range(9):
                for col in range(9):
                    number = solution[row][col]
                    x = x_pos + col * cell_size + cell_size / 2
                    y = y_pos + (8 - row) * cell_size + cell_size / 2 - 3
                    c.drawCentredString(x, y, str(number))
    
    def _draw_cta_page(self, c, width, height):
        """Draw the final call-to-action page"""
        self._set_font(c, 'Helvetica-Bold', 36)
        c.drawCentredString(width/2, height - 2*inch, "Ready for 100 More Puzzles?")
        
        self._set_font(c, 'Helvetica', 18)
        text_y = height - 3.5*inch
        
        cta_text = [
            "You've just completed 5 amazing puzzles!",
            "Now get our complete book with:",
            "",
            "✓ 100+ Large Print Sudoku Puzzles",
            "✓ Perfect 8.5×11 inch size",
            "✓ Crystal clear 32pt numbers",
            "✓ Progressive difficulty (Easy → Hard)",
            "✓ Complete solutions with tips",
            "✓ Professionally printed quality",
        ]
        
        for line in cta_text:
            c.drawCentredString(width/2, text_y, line)
            text_y -= 0.4*inch
        
        # Add big Gumroad button box
        text_y -= 0.3*inch
        box_height = 1.2*inch
        box_width = 5*inch
        box_x = (width - box_width) / 2
        
        # Draw box
        c.setFillColorRGB(0, 0.5, 0)  # Green
        c.rect(box_x, text_y - box_height, box_width, box_height, fill=1)
        
        # Add text in box
        c.setFillColorRGB(1, 1, 1)  # White
        self._set_font(c, 'Helvetica-Bold', 24)
        c.drawCentredString(width/2, text_y - 0.5*inch, "GET IT NOW - ONLY $9.99")
        self._set_font(c, 'Helvetica', 14)
        c.drawCentredString(width/2, text_y - 0.8*inch, "iganapolsky.gumroad.com/l/hjybj")
        
        # Reset color
        c.setFillColorRGB(0, 0, 0)  # Black
        text_y -= 1.5*inch
        
        self._set_font(c, 'Helvetica-Bold', 16)
        c.drawCentredString(width/2, text_y, "⭐ Join 4,000+ Happy Puzzle Solvers! ⭐")
        
        self._set_font(c, 'Helvetica', 14)
        c.drawCentredString(width/2, 1.5*inch, "© 2025 Senior Puzzle Studio")
        c.drawCentredString(width/2, 1*inch, "Dedicated to creating accessible puzzles for seniors everywhere")


def main():
    """Generate the lead magnet PDF"""
    print("Creating lead magnet PDF...")
    
    generator = LeadMagnetGenerator()
    
    # Generate puzzles
    puzzles = generator.generate_puzzles()
    
    # Create PDF
    generator.create_pdf(puzzles)
    
    # Also save puzzle data as JSON for the landing page
    json_path = os.path.join(generator.output_dir, "puzzle-data.json")
    with open(json_path, 'w') as f:
        json.dump({
            'puzzles': puzzles,
            'generated': datetime.now().isoformat(),
            'title': '5 Free Brain-Boosting Sudoku Puzzles'
        }, f, indent=2)
    
    print(f"Puzzle data saved: {json_path}")
    print("Done! Lead magnet PDF is ready for download.")


if __name__ == "__main__":
    main()