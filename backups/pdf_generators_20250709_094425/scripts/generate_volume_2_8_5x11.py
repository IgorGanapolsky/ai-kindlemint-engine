#!/usr/bin/env python3
"""
Generate Volume 2 PDF in proper 8.5x11 format for paperback
This is the CORRECT format for Large Print puzzle books
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter  # 8.5x11
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# CORRECT Page dimensions - 8.5x11 (letter size)
PAGE_WIDTH = 8.5 * inch
PAGE_HEIGHT = 11 * inch

# Margins for 8.5x11 - more generous for large print
TOP_MARGIN = 1 * inch
BOTTOM_MARGIN = 1 * inch
LEFT_MARGIN = 1 * inch
RIGHT_MARGIN = 1 * inch

# Puzzle grid size for 8.5x11 - MUCH larger
GRID_SIZE = 6 * inch  # Was 4.5 for 6x9

# Use standard fonts
BASE_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"


class Volume2_8_5x11_Generator:
    """Generate Volume 2 PDF in proper 8.5x11 format"""

    def __init__(self):
        self.base_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_2")
        self.metadata_dir = self.base_dir / "metadata"
        self.puzzles_dir = self.base_dir / "puzzles"
        self.output_dir = self.base_dir / "paperback"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(self):
        """Generate the complete Volume 2 PDF in 8.5x11"""
        print("📚 Generating Volume 2 PDF (8.5x11 FORMAT)")
        print("=" * 70)
        print("📏 Format: 8.5 × 11 inches (Letter size)")
        print("📐 Grid size: 6 inches (optimal for large print)")
        print("=" * 70)
        
        # Output file
        output_file = self.output_dir / "Large_Print_Sudoku_Masters_Volume_2_Interior_8_5x11.pdf"
        
        # Create canvas with letter size
        c = canvas.Canvas(str(output_file), pagesize=letter)
        
        # Add metadata
        c.setTitle("Large Print Sudoku Masters: Volume 2")
        c.setAuthor("KindleMint Publishing")
        c.setSubject("100 Large Print Sudoku Puzzles - 8.5x11 Format")
        
        # Generate pages
        self._add_title_page(c)
        self._add_copyright_page(c)
        self._add_introduction(c)
        self._add_puzzles(c)
        self._add_solutions(c)
        self._add_outro(c)
        
        # Save PDF
        c.save()
        
        print("\n✅ PDF generated successfully!")
        print(f"📄 Output: {output_file}")
        print("📏 Format: 8.5 × 11 inches")
        print(f"📏 Size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        return output_file

    def _add_title_page(self, c):
        """Add title page optimized for 8.5x11"""
        # Larger fonts for 8.5x11
        c.setFont(BOLD_FONT, 60)  # Was 48
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2.5 * inch, "LARGE PRINT")
        
        c.setFont(BOLD_FONT, 48)  # Was 36
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3.75 * inch, "SUDOKU")
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 4.75 * inch, "MASTERS")
        
        c.setFont(BASE_FONT, 30)  # Was 24
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 6.5 * inch, "Volume 2")
        
        c.setFont(BASE_FONT, 24)  # Was 18
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 7.5 * inch, "100 Puzzles")
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 8 * inch, "With Solutions")
        
        # Format indicator
        c.setFont(BASE_FONT, 16)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 9 * inch, "8.5 × 11 inch Large Print Edition")
        
        c.setFont(BASE_FONT, 18)  # Was 14
        c.drawCentredString(PAGE_WIDTH / 2, 1.5 * inch, "KindleMint Publishing")
        
        c.showPage()

    def _add_copyright_page(self, c):
        """Add copyright page"""
        c.setFont(BASE_FONT, 12)  # Slightly larger for 8.5x11
        y = PAGE_HEIGHT - TOP_MARGIN
        
        lines = [
            f"Copyright © {datetime.now().year} KindleMint Publishing",
            "All rights reserved.",
            "",
            "No part of this publication may be reproduced, distributed,",
            "or transmitted in any form or by any means, including",
            "photocopying, recording, or other electronic or mechanical",
            "methods, without the prior written permission of the publisher.",
            "",
            "ISBN: 979-8-12345-678-9",
            "",
            "First Edition",
            "8.5 × 11 inch Large Print Format",
            "Printed in the United States of America",
        ]
        
        for line in lines:
            c.drawCentredString(PAGE_WIDTH / 2, y, line)
            y -= 18
        
        c.showPage()

    def _add_introduction(self, c):
        """Add introduction page"""
        c.setFont(BOLD_FONT, 28)  # Larger for 8.5x11
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN, "How to Play Sudoku")
        
        c.setFont(BASE_FONT, 14)  # Was 12
        y = PAGE_HEIGHT - 2 * inch
        
        intro_text = [
            "Sudoku is a logic puzzle played on a 9×9 grid.",
            "",
            "The Rules:",
            "• Fill in the empty cells with numbers 1-9",
            "• Each row must contain all numbers 1-9",
            "• Each column must contain all numbers 1-9",
            "• Each 3×3 box must contain all numbers 1-9",
            "• No number can repeat in any row, column, or box",
            "",
            "Tips for Solving:",
            "• Start with rows, columns, or boxes that have many given numbers",
            "• Look for cells where only one number can fit",
            "• Use pencil marks to track possible numbers",
            "• Take your time and enjoy the challenge!",
            "",
            "This book contains 100 puzzles:",
            "• Puzzles 1-20: Easy (35-40 clues)",
            "• Puzzles 21-80: Medium (30-35 clues)",
            "• Puzzles 81-100: Hard (25-30 clues)",
            "",
            "This 8.5 × 11 inch format provides extra-large grids",
            "for comfortable solving and easy-to-read numbers.",
        ]
        
        for line in intro_text:
            if line.startswith("•"):
                c.drawString(LEFT_MARGIN + 30, y, line)
            else:
                c.drawString(LEFT_MARGIN, y, line)
            y -= 20
        
        c.showPage()

    def _add_puzzles(self, c):
        """Add all 100 puzzles optimized for 8.5x11"""
        print("\n📝 Adding puzzles (8.5x11 format)...")
        
        for puzzle_num in range(1, 101):
            self._add_single_puzzle(c, puzzle_num)
            
            if puzzle_num % 10 == 0:
                print(f"  ✓ Puzzles {puzzle_num-9}-{puzzle_num} added")

    def _add_single_puzzle(self, c, puzzle_num):
        """Add a single puzzle page for 8.5x11"""
        # Header - larger font
        c.setFont(BOLD_FONT, 24)  # Was 18
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN, f"Puzzle #{puzzle_num:02d}")
        
        # Difficulty indicator
        if puzzle_num <= 20:
            difficulty = "Easy"
        elif puzzle_num <= 80:
            difficulty = "Medium"
        else:
            difficulty = "Hard"
        
        c.setFont(BASE_FONT, 16)  # Was 12
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 35, f"Difficulty: {difficulty}")
        
        # Load and display puzzle image - MUCH larger for 8.5x11
        puzzle_image = self.puzzles_dir / f"sudoku_puzzle_{puzzle_num:03d}.png"
        
        if puzzle_image.exists():
            # 6 inch grid for 8.5x11 (was 4.5 for 6x9)
            img_size = GRID_SIZE
            x = (PAGE_WIDTH - img_size) / 2
            y = (PAGE_HEIGHT - img_size) / 2 - 0.75 * inch
            
            # Draw the puzzle image
            c.drawImage(str(puzzle_image), x, y, width=img_size, height=img_size)
            
            # Instructions
            c.setFont(BASE_FONT, 12)
            c.drawCentredString(PAGE_WIDTH / 2, y - 30, "Fill in the empty cells with numbers 1-9")
        else:
            # Error message
            c.setFont(BASE_FONT, 14)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "ERROR: Puzzle image not found!")
            print(f"  ⚠️  Missing puzzle image: {puzzle_image}")
        
        c.showPage()

    def _add_solutions(self, c):
        """Add solutions section for 8.5x11"""
        print("\n📝 Adding solutions (8.5x11 format)...")
        
        # Solutions header page
        c.setFont(BOLD_FONT, 48)  # Was 36
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "SOLUTIONS")
        c.showPage()
        
        # Two solutions per page for 8.5x11
        for puzzle_num in range(1, 101, 2):
            self._add_solution_page(c, puzzle_num)
            
            if puzzle_num % 20 == 19:
                print(f"  ✓ Solutions {puzzle_num-18}-{puzzle_num+1} added")

    def _add_solution_page(self, c, start_num):
        """Add two solutions on one page for 8.5x11"""
        # Solution 1 (top half)
        c.setFont(BOLD_FONT, 18)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN, f"Solutions #{start_num:02d} & #{start_num+1:02d}")
        
        # First solution
        solution_image1 = self.puzzles_dir / f"sudoku_solution_{start_num:03d}.png"
        if solution_image1.exists():
            img_size = 3.5 * inch  # Smaller for 2 per page
            x = (PAGE_WIDTH - img_size) / 2
            y = PAGE_HEIGHT - TOP_MARGIN - 1.5 * inch - img_size
            c.drawImage(str(solution_image1), x, y, width=img_size, height=img_size)
            
            # Label
            c.setFont(BASE_FONT, 12)
            c.drawCentredString(PAGE_WIDTH / 2, y + img_size + 10, f"Puzzle #{start_num}")
        
        # Second solution (if exists)
        if start_num + 1 <= 100:
            solution_image2 = self.puzzles_dir / f"sudoku_solution_{start_num+1:03d}.png"
            if solution_image2.exists():
                y2 = y - img_size - 1 * inch
                c.drawImage(str(solution_image2), x, y2, width=img_size, height=img_size)
                
                # Label
                c.drawCentredString(PAGE_WIDTH / 2, y2 + img_size + 10, f"Puzzle #{start_num+1}")
        
        c.showPage()

    def _add_outro(self, c):
        """Add outro/marketing page for 8.5x11"""
        c.setFont(BOLD_FONT, 32)  # Was 24
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - TOP_MARGIN - 1 * inch, "Thank You!")
        
        c.setFont(BASE_FONT, 16)  # Was 14
        y = PAGE_HEIGHT - 3 * inch
        
        outro_text = [
            "We hope you enjoyed these puzzles!",
            "",
            "If you loved this book:",
            "• Please leave a review on Amazon",
            "• Check out Volumes 1, 3, and 4 in 8.5×11 format",
            "• Visit www.kindlemint.com for more puzzle books",
            "",
            "Available in This Series:",
            "• Large Print Sudoku Masters (8.5×11)",
            "• Large Print Crossword Masters (8.5×11)",
            "• Large Print Word Search Champions (8.5×11)",
            "",
            "All books feature extra-large 8.5×11 format",
            "for maximum readability and solving comfort.",
            "",
            "Happy Puzzling!",
        ]
        
        for line in outro_text:
            if line.startswith("•"):
                c.drawString(LEFT_MARGIN + 30, y, line)
            else:
                c.drawCentredString(PAGE_WIDTH / 2, y, line)
            y -= 25
        
        c.showPage()


def main():
    """Generate Volume 2 in proper 8.5x11 format"""
    generator = Volume2_8_5x11_Generator()
    
    # Verify we have puzzle images
    puzzle_count = len(list(generator.puzzles_dir.glob("sudoku_puzzle_*.png")))
    solution_count = len(list(generator.puzzles_dir.glob("sudoku_solution_*.png")))
    
    print(f"Found {puzzle_count} puzzle images")
    print(f"Found {solution_count} solution images")
    
    if puzzle_count < 100:
        print("❌ Error: Not enough puzzle images!")
        return
    
    # Generate the PDF
    generator.generate_pdf()
    
    print("\n✅ Volume 2 is now properly formatted for 8.5×11!")
    print("📏 This is the CORRECT format for Large Print puzzle books")


if __name__ == "__main__":
    main()