#!/usr/bin/env python3
"""
FIXED: Generate Volume 2 PDF with proper puzzle images (not solutions!)
Ensures puzzles are playable with empty cells
"""

import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import inch
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Page setup - 6x9 inch book
PAGE_WIDTH = 6 * inch
PAGE_HEIGHT = 9 * inch
MARGIN = 0.75 * inch

# Use standard fonts
BASE_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"


class Volume2PDFGenerator:
    """Generate Volume 2 PDF with FIXED puzzle display"""

    def __init__(self):
        self.base_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_2")
        self.metadata_dir = self.base_dir / "metadata"
        self.puzzles_dir = self.base_dir / "puzzles"  # FIXED: Correct path
        self.output_dir = self.base_dir / "paperback"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(self):
        """Generate the complete Volume 2 PDF"""
        print("📚 Generating Volume 2 PDF (FIXED VERSION)")
        print("=" * 70)
        
        # Output file
        output_file = self.output_dir / "Large_Print_Sudoku_Masters_Volume_2_Interior_FIXED.pdf"
        
        # Create canvas
        c = canvas.Canvas(str(output_file), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
        
        # Add metadata
        c.setTitle("Large Print Sudoku Masters: Volume 2")
        c.setAuthor("KindleMint Publishing")
        c.setSubject("100 Large Print Sudoku Puzzles")
        
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
        print(f"📏 Size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Validate the PDF
        print("\n🔍 Running validation...")
        self._validate_pdf(output_file)
        
        return output_file

    def _add_title_page(self, c):
        """Add title page"""
        c.setFont(BOLD_FONT, 48)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2 * inch, "LARGE PRINT")
        
        c.setFont(BOLD_FONT, 36)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3 * inch, "SUDOKU")
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3.75 * inch, "MASTERS")
        
        c.setFont(BASE_FONT, 24)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 5 * inch, "Volume 2")
        
        c.setFont(BASE_FONT, 18)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 6 * inch, "100 Puzzles")
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 6.5 * inch, "With Solutions")
        
        c.setFont(BASE_FONT, 14)
        c.drawCentredString(PAGE_WIDTH / 2, 1.5 * inch, "KindleMint Publishing")
        
        c.showPage()

    def _add_copyright_page(self, c):
        """Add copyright page"""
        c.setFont(BASE_FONT, 10)
        y = PAGE_HEIGHT - MARGIN
        
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
            "Printed in the United States of America",
        ]
        
        for line in lines:
            c.drawCentredString(PAGE_WIDTH / 2, y, line)
            y -= 14
        
        c.showPage()

    def _add_introduction(self, c):
        """Add introduction page"""
        c.setFont(BOLD_FONT, 24)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN, "How to Play Sudoku")
        
        c.setFont(BASE_FONT, 12)
        y = PAGE_HEIGHT - 1.5 * inch
        
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
        ]
        
        for line in intro_text:
            if line.startswith("•"):
                c.drawString(MARGIN + 20, y, line)
            else:
                c.drawString(MARGIN, y, line)
            y -= 16
        
        c.showPage()

    def _add_puzzles(self, c):
        """Add all 100 puzzles"""
        print("\n📝 Adding puzzles...")
        
        for puzzle_num in range(1, 101):
            self._add_single_puzzle(c, puzzle_num)
            
            if puzzle_num % 10 == 0:
                print(f"  ✓ Puzzles {puzzle_num-9}-{puzzle_num} added")

    def _add_single_puzzle(self, c, puzzle_num):
        """Add a single puzzle page"""
        # Header
        c.setFont(BOLD_FONT, 18)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN, f"Puzzle #{puzzle_num:02d}")
        
        # Difficulty indicator
        if puzzle_num <= 20:
            difficulty = "Easy"
        elif puzzle_num <= 80:
            difficulty = "Medium"
        else:
            difficulty = "Hard"
        
        c.setFont(BASE_FONT, 12)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN - 25, f"Difficulty: {difficulty}")
        
        # CRITICAL: Load and display the PUZZLE image (not solution!)
        puzzle_image = self.puzzles_dir / f"sudoku_puzzle_{puzzle_num:03d}.png"
        
        if puzzle_image.exists():
            # Calculate position to center the image
            img_size = 4.5 * inch  # Large print size
            x = (PAGE_WIDTH - img_size) / 2
            y = (PAGE_HEIGHT - img_size) / 2 - 0.5 * inch
            
            # Draw the puzzle image
            c.drawImage(str(puzzle_image), x, y, width=img_size, height=img_size)
            
            # Add visual confirmation this is a puzzle
            c.setFont(BASE_FONT, 10)
            c.drawCentredString(PAGE_WIDTH / 2, y - 20, "Fill in the empty cells")
        else:
            # Fallback error message
            c.setFont(BASE_FONT, 14)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "ERROR: Puzzle image not found!")
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 20, f"Looking for: {puzzle_image.name}")
            print(f"  ⚠️  Missing puzzle image: {puzzle_image}")
        
        c.showPage()

    def _add_solutions(self, c):
        """Add solutions section"""
        print("\n📝 Adding solutions...")
        
        # Solutions section header
        c.setFont(BOLD_FONT, 36)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "SOLUTIONS")
        c.showPage()
        
        # Add each solution
        for puzzle_num in range(1, 101):
            self._add_single_solution(c, puzzle_num)
            
            if puzzle_num % 10 == 0:
                print(f"  ✓ Solutions {puzzle_num-9}-{puzzle_num} added")

    def _add_single_solution(self, c, puzzle_num):
        """Add a single solution page"""
        # Header
        c.setFont(BOLD_FONT, 16)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN, f"Solution to Puzzle #{puzzle_num:02d}")
        
        # Solution image
        solution_image = self.puzzles_dir / f"sudoku_solution_{puzzle_num:03d}.png"
        
        if solution_image.exists():
            # Smaller size for solutions
            img_size = 3.5 * inch
            x = (PAGE_WIDTH - img_size) / 2
            y = (PAGE_HEIGHT - img_size) / 2
            
            c.drawImage(str(solution_image), x, y, width=img_size, height=img_size)
        else:
            # Fallback
            c.setFont(BASE_FONT, 14)
            c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2, "Solution image not found")
            print(f"  ⚠️  Missing solution image: {solution_image}")
        
        c.showPage()

    def _add_outro(self, c):
        """Add outro/marketing page"""
        c.setFont(BOLD_FONT, 24)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN, "Thank You!")
        
        c.setFont(BASE_FONT, 14)
        y = PAGE_HEIGHT - 2 * inch
        
        outro_text = [
            "We hope you enjoyed these puzzles!",
            "",
            "If you loved this book:",
            "• Please leave a review on Amazon",
            "• Check out Volumes 1, 3, and 4",
            "• Visit www.kindlemint.com for more puzzle books",
            "",
            "Coming Soon:",
            "• Large Print Crossword Masters",
            "• Large Print Word Search Champions",
            "• Large Print Logic Puzzles",
            "",
            "Happy Puzzling!",
        ]
        
        for line in outro_text:
            if line.startswith("•"):
                c.drawString(MARGIN + 20, y, line)
            else:
                c.drawCentredString(PAGE_WIDTH / 2, y, line)
            y -= 20
        
        c.showPage()

    def _validate_pdf(self, pdf_path):
        """Quick validation of the generated PDF"""
        # Check file size
        size_mb = pdf_path.stat().st_size / 1024 / 1024
        if size_mb < 1:
            print("  ⚠️  Warning: PDF seems too small")
        elif size_mb > 50:
            print("  ⚠️  Warning: PDF seems too large")
        else:
            print(f"  ✓ File size OK: {size_mb:.1f} MB")
        
        # Count pages (roughly)
        expected_pages = 1 + 1 + 1 + 100 + 1 + 100 + 1  # title + copyright + intro + puzzles + solutions header + solutions + outro
        print(f"  ✓ Expected pages: ~{expected_pages}")
        
        # Verify critical images exist
        missing_puzzles = []
        missing_solutions = []
        
        for i in range(1, 101):
            if not (self.puzzles_dir / f"sudoku_puzzle_{i:03d}.png").exists():
                missing_puzzles.append(i)
            if not (self.puzzles_dir / f"sudoku_solution_{i:03d}.png").exists():
                missing_solutions.append(i)
        
        if missing_puzzles:
            print(f"  ❌ Missing {len(missing_puzzles)} puzzle images: {missing_puzzles[:5]}...")
        else:
            print("  ✓ All puzzle images found")
        
        if missing_solutions:
            print(f"  ❌ Missing {len(missing_solutions)} solution images: {missing_solutions[:5]}...")
        else:
            print("  ✓ All solution images found")


def main():
    """Generate Volume 2 PDF with proper puzzles"""
    generator = Volume2PDFGenerator()
    
    # First, verify we have puzzle images
    puzzle_count = len(list(generator.puzzles_dir.glob("sudoku_puzzle_*.png")))
    solution_count = len(list(generator.puzzles_dir.glob("sudoku_solution_*.png")))
    
    print(f"Found {puzzle_count} puzzle images")
    print(f"Found {solution_count} solution images")
    
    if puzzle_count < 100:
        print("❌ Error: Not enough puzzle images! Need to generate them first.")
        return
    
    # Generate the PDF
    pdf_file = generator.generate_pdf()
    
    # Run the validator
    print("\n🔍 Running full validation...")
    import subprocess
    result = subprocess.run([
        sys.executable, 
        "scripts/validate_sudoku_pdf.py", 
        str(pdf_file)
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print("❌ Validation failed!")
        print(result.stderr)
    else:
        print("✅ Volume 2 PDF is ready for publishing!")


if __name__ == "__main__":
    main()