#!/usr/bin/env python3
"""
Generate 5 Free Brain-Boosting Sudoku Puzzles for Lead Magnet
Specifically designed for seniors 75+ with extra-large print
"""

import os
import sys
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import gray

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
        """Set font with fallback to Helvetica"""
        try:
            canvas.setFont(font_name, size)
        except:
            # Fallback to Helvetica family
            if 'Bold' in font_name:
                canvas.setFont('Helvetica-Bold', size)
            else:
                canvas.setFont('Helvetica', size)
        
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
        
        # Register fonts
        font_dir = "assets/fonts"
        if os.path.exists(os.path.join(font_dir, "DejaVuSans.ttf")):
            pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(font_dir, 'DejaVuSans.ttf')))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', os.path.join(font_dir, 'DejaVuSans-Bold.ttf')))
        
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
        self._set_font(c, 'DejaVuSans-Bold', 36)
        c.drawCentredString(width/2, height - 2*inch, "5 FREE")
        c.drawCentredString(width/2, height - 2.8*inch, "Brain-Boosting")
        c.drawCentredString(width/2, height - 3.6*inch, "Sudoku Puzzles")
        
        self._set_font(c, 'DejaVuSans', 24)
        c.drawCentredString(width/2, height - 5*inch, "Extra-Large Print")
        c.drawCentredString(width/2, height - 5.6*inch, "For Seniors")
        
        self._set_font(c, 'DejaVuSans', 16)
        c.drawCentredString(width/2, height - 7*inch, "From KindleMint Publishing")
        c.drawCentredString(width/2, height - 7.5*inch, "Your Trusted Source for Large Print Puzzles")
    
    def _draw_intro_page(self, c, width, height):
        """Draw the introduction page"""
        self._set_font(c, 'DejaVuSans-Bold', 28)
        c.drawCentredString(width/2, height - 1.5*inch, "Welcome!")
        
        self._set_font(c, 'DejaVuSans', 16)
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
    
    def _draw_puzzle_page(self, c, width, height, puzzle_data):
        """Draw a single puzzle page"""
        # Header
        self._set_font(c, 'DejaVuSans-Bold', 24)
        c.drawCentredString(width/2, height - 1*inch, 
                          f"Puzzle #{puzzle_data['number']} - {puzzle_data['difficulty'].title()}")
        
        # Grid settings - EXTRA LARGE
        grid_size = 6.5 * inch  # Even larger than normal
        cell_size = grid_size / 9
        start_x = (width - grid_size) / 2
        start_y = height - 2.5*inch - grid_size
        
        # Draw grid
        c.setLineWidth(2)
        for i in range(10):
            # Thicker lines for 3x3 boxes
            if i % 3 == 0:
                c.setLineWidth(3)
            else:
                c.setLineWidth(1)
            
            # Vertical lines
            x = start_x + i * cell_size
            c.line(x, start_y, x, start_y + grid_size)
            
            # Horizontal lines
            y = start_y + i * cell_size
            c.line(start_x, y, start_x + grid_size, y)
        
        # Fill in numbers - EXTRA LARGE FONT
        self._set_font(c, 'DejaVuSans', 28)  # Very large font
        puzzle = puzzle_data['puzzle']
        
        for row in range(9):
            for col in range(9):
                number = puzzle[row][col]
                if number != 0:
                    x = start_x + col * cell_size + cell_size / 2
                    y = start_y + (8 - row) * cell_size + cell_size / 2 - 10
                    c.drawCentredString(x, y, str(number))
        
        # Footer tip
        self._set_font(c, 'DejaVuSans', 14)
        c.drawCentredString(width/2, 1*inch, 
                          "Tip: Start with rows, columns, or boxes that have the most numbers!")
    
    def _draw_solutions_page(self, c, width, height, puzzles):
        """Draw all solutions on one page"""
        self._set_font(c, 'DejaVuSans-Bold', 28)
        c.drawCentredString(width/2, height - 1*inch, "Solutions")
        
        # Smaller grids for solutions
        grid_size = 2 * inch
        cell_size = grid_size / 9
        
        # Arrange in 2 columns, 3 rows
        positions = [
            (1.5*inch, height - 3*inch),
            (4.5*inch, height - 3*inch),
            (1.5*inch, height - 5.5*inch),
            (4.5*inch, height - 5.5*inch),
            (3*inch, height - 8*inch),  # Center the last one
        ]
        
        for idx, (puzzle_data, (x_pos, y_pos)) in enumerate(zip(puzzles, positions)):
            # Label
            self._set_font(c, 'DejaVuSans-Bold', 12)
            c.drawString(x_pos, y_pos + grid_size + 0.2*inch, 
                        f"Puzzle #{puzzle_data['number']}")
            
            # Draw mini grid
            c.setLineWidth(0.5)
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
            self._set_font(c, 'DejaVuSans', 8)
            solution = puzzle_data['solution']
            
            for row in range(9):
                for col in range(9):
                    number = solution[row][col]
                    x = x_pos + col * cell_size + cell_size / 2
                    y = y_pos + (8 - row) * cell_size + cell_size / 2 - 3
                    c.drawCentredString(x, y, str(number))
    
    def _draw_cta_page(self, c, width, height):
        """Draw the call-to-action page"""
        self._set_font(c, 'DejaVuSans-Bold', 28)
        c.drawCentredString(width/2, height - 2*inch, "Want More Puzzles?")
        
        self._set_font(c, 'DejaVuSans', 18)
        text_y = height - 3.5*inch
        
        cta_text = [
            "Join thousands of seniors who keep their",
            "minds sharp with our Large Print Sudoku series!",
            "",
            "✓ 100 puzzles per volume",
            "✓ Extra-large print throughout", 
            "✓ Progressive difficulty levels",
            "✓ Complete solutions included",
            "✓ Perfect binding - lays flat",
            "",
            "Get your copy on Amazon:",
            "Search for 'Large Print Sudoku Masters'",
            "by KindleMint Publishing",
            "",
            "Plus, as a subscriber, you'll receive:",
            "• Our weekly 'Puzzle of the Week'",
            "• Special discounts on new releases",
            "• Brain training tips and tricks",
        ]
        
        for line in cta_text:
            if line.startswith('✓'):
                c.drawString(2*inch, text_y, line)
            elif line.startswith('•'):
                c.drawString(2*inch, text_y, line)
            else:
                c.drawCentredString(width/2, text_y, line)
            text_y -= 0.35*inch
        
        # Website
        self._set_font(c, 'DejaVuSans-Bold', 20)
        c.setFillColor(gray)
        c.drawCentredString(width/2, 1.5*inch, "SudokuForSeniors.com")
    
    def generate(self):
        """Main generation process"""
        print("Generating lead magnet puzzles...")
        puzzles = self.generate_puzzles()
        
        print("Creating PDF...")
        self.create_pdf(puzzles)
        
        # Also save puzzle data as JSON for potential web use
        json_path = os.path.join(self.output_dir, "puzzle-data.json")
        with open(json_path, 'w') as f:
            json.dump(puzzles, f, indent=2)
        
        print("Lead magnet generation complete!")
        print(f"PDF: {self.pdf_path}")
        print(f"Data: {json_path}")


if __name__ == "__main__":
    generator = LeadMagnetGenerator()
    generator.generate()