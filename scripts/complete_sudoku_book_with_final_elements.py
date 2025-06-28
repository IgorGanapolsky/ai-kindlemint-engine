#!/usr/bin/env python3
"""
Complete Sudoku Book Generator with Final Elements
Regenerates the Large Print Sudoku Masters Volume 1 with copyright page and final teaser
"""

import json
import os
from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib import colors
except ImportError:
    print("Installing required packages...")
    os.system("pip install reportlab")
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib import colors


class CompleteSudokuBookGenerator:
    """Generate complete Sudoku book with all required elements"""
    
    def __init__(self, volume_path: Path):
        self.volume_path = volume_path
        self.puzzles_dir = volume_path / "puzzles"
        self.output_dir = volume_path / "paperback"
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the book"""
        self.styles.add(ParagraphStyle(
            name='BookTitle',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='Copyright',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_LEFT,
            leftIndent=0.5*inch
        ))
        
        self.styles.add(ParagraphStyle(
            name='PuzzleNumber',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='FinalTeaser',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.black
        ))

    def create_title_page(self, story):
        """Create the title page"""
        story.append(Spacer(1, 2*inch))
        
        title = Paragraph("Large Print Sudoku Masters", self.styles['BookTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        subtitle = Paragraph("Volume 1", self.styles['Heading1'])
        story.append(subtitle)
        story.append(Spacer(1, 0.5*inch))
        
        tagline = Paragraph("100 Easy to Hard Puzzles for Hours of Brain Training", 
                          self.styles['Heading2'])
        story.append(tagline)
        story.append(Spacer(1, 2*inch))
        
        author = Paragraph("Igor Ganapolsky", self.styles['Heading1'])
        story.append(author)
        story.append(PageBreak())

    def create_copyright_page(self, story):
        """Create the copyright page (Page 2)"""
        story.append(Spacer(1, 1*inch))
        
        copyright_content = [
            "Large Print Sudoku Masters – Volume 1",
            "© 2025 Crossword Masters Publishing",
            "All rights reserved.",
            "",
            "No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means—electronic, mechanical, photocopy, recording, or otherwise—without prior written permission from the publisher.",
            "",
            "This book is intended for personal entertainment only.",
            "",
            "ISBN: 978-1-XXXXXXX-XX-X",
            "Published by Crossword Masters Publishing",
            "www.CrosswordMasters.com",
            "",
            "Printed in the USA"
        ]
        
        for line in copyright_content:
            if line:
                para = Paragraph(line, self.styles['Copyright'])
                story.append(para)
            else:
                story.append(Spacer(1, 12))
        
        story.append(PageBreak())

    def load_puzzle_data(self):
        """Load all puzzle data from JSON files"""
        puzzles = []
        metadata_dir = self.puzzles_dir / "metadata"
        
        for i in range(1, 101):  # Puzzles 1-100
            puzzle_file = metadata_dir / f"sudoku_puzzle_{i:03d}.json"
            if puzzle_file.exists():
                with open(puzzle_file, 'r') as f:
                    puzzle_data = json.load(f)
                    puzzles.append(puzzle_data)
        
        return sorted(puzzles, key=lambda x: x.get('id', 0))

    def add_puzzle_pages(self, story, puzzles):
        """Add all puzzle pages to the book"""
        for i, puzzle in enumerate(puzzles, 1):
            # Puzzle number header
            puzzle_header = Paragraph(f"Puzzle #{i}", self.styles['PuzzleNumber'])
            story.append(puzzle_header)
            story.append(Spacer(1, 20))
            
            # Add puzzle image if available
            puzzle_image_path = self.puzzles_dir / "puzzles" / f"sudoku_puzzle_{i:03d}.png"
            if puzzle_image_path.exists():
                try:
                    abs_path = puzzle_image_path.resolve()
                    print(f"Loading puzzle image: {abs_path}")
                    img = Image(str(abs_path), width=6*inch, height=6*inch)
                    story.append(img)
                    print(f"✅ Successfully loaded puzzle image {i}")
                except Exception as e:
                    print(f"❌ Could not load puzzle image {i}: {e}")
                    print(f"📄 Falling back to text representation")
                    # Fallback: create text representation
                    self.add_text_puzzle(story, puzzle)
            else:
                print(f"❌ Puzzle image not found: {puzzle_image_path}")
                self.add_text_puzzle(story, puzzle)
            
            story.append(PageBreak())

    def add_text_puzzle(self, story, puzzle):
        """Add a text-based puzzle representation"""
        if 'initial_grid' in puzzle:
            grid_text = ""
            for row in puzzle['initial_grid']:
                row_text = " ".join([str(cell) if cell != 0 else "." for cell in row])
                grid_text += f"<font name='Courier'>{row_text}</font><br/>"
            
            grid_para = Paragraph(grid_text, self.styles['Normal'])
            story.append(grid_para)
        else:
            placeholder = Paragraph("[ Sudoku Grid ]", self.styles['Normal'])
            story.append(placeholder)

    def add_text_solution(self, story, puzzle):
        """Add a text-based solution representation"""
        if 'solution_grid' in puzzle:
            solution_text = ""
            for row in puzzle['solution_grid']:
                row_text = " ".join([str(cell) for cell in row])
                solution_text += f"<font name='Courier'>{row_text}</font><br/>"
            
            solution_para = Paragraph(solution_text, self.styles['Normal'])
            story.append(solution_para)
        else:
            placeholder = Paragraph("[ Solution Grid ]", self.styles['Normal'])
            story.append(placeholder)

    def add_solutions_section(self, story, puzzles):
        """Add solutions section"""
        story.append(Spacer(1, 1*inch))
        
        solutions_title = Paragraph("Solutions", self.styles['BookTitle'])
        story.append(solutions_title)
        story.append(Spacer(1, 0.5*inch))
        story.append(PageBreak())
        
        for i, puzzle in enumerate(puzzles, 1):
            # Solution number header
            solution_header = Paragraph(f"Solution to Puzzle #{i}", self.styles['PuzzleNumber'])
            story.append(solution_header)
            story.append(Spacer(1, 20))
            
            # Add solution image if available
            solution_image_path = self.puzzles_dir / "puzzles" / f"sudoku_solution_{i:03d}.png"
            if solution_image_path.exists():
                try:
                    abs_path = solution_image_path.resolve()
                    print(f"Loading SOLUTION image: {abs_path}")
                    img = Image(str(abs_path), width=6*inch, height=6*inch)
                    story.append(img)
                    print(f"✅ Successfully loaded solution image {i}")
                except Exception as e:
                    print(f"❌ Could not load solution image {i}: {e}")
                    print(f"📄 Falling back to text representation")
                    # Fallback: create text representation
                    self.add_text_solution(story, puzzle)
            else:
                print(f"❌ Solution image not found: {solution_image_path}")
                self.add_text_solution(story, puzzle)
            
            story.append(PageBreak())

    def add_final_teaser_page(self, story):
        """Add the final teaser page (Page 104)"""
        story.append(Spacer(1, 2*inch))
        
        teaser_content = [
            "Enjoyed this puzzle book?",
            "",
            "📚 Get ready for more in the Sudoku Masters series!",
            "",
            "Volume 2 is coming soon with 50 all-new puzzles",
            "in the same easy-to-read large print format.",
            "",
            "🛒 Visit www.CrosswordMasters.com or check Amazon",
            "for our latest releases, including Crossword and Word Search books!",
            "",
            "💬 We'd love your feedback!",
            "Please leave a quick review on Amazon — it helps more puzzlers find us."
        ]
        
        for line in teaser_content:
            if line:
                para = Paragraph(line, self.styles['FinalTeaser'])
                story.append(para)
                story.append(Spacer(1, 10))
            else:
                story.append(Spacer(1, 15))

    def generate_complete_book(self):
        """Generate the complete book with all elements"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"Large_Print_Sudoku_Masters_V1_VERIFIED_{timestamp}.pdf"
        
        print(f"🚀 Generating complete Sudoku book...")
        print(f"📁 Output: {output_file}")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # 1. Title Page
        print("📄 Adding title page...")
        self.create_title_page(story)
        
        # 2. Copyright Page
        print("©️ Adding copyright page...")
        self.create_copyright_page(story)
        
        # 3. Load puzzle data
        print("🧩 Loading puzzle data...")
        puzzles = self.load_puzzle_data()
        print(f"✅ Loaded {len(puzzles)} puzzles")
        
        # 4. Puzzle Pages
        print("🔢 Adding puzzle pages...")
        self.add_puzzle_pages(story, puzzles)
        
        # 5. Solutions Section
        print("💡 Adding solutions section...")
        self.add_solutions_section(story, puzzles)
        
        # 6. Final Teaser Page
        print("📢 Adding final teaser page...")
        self.add_final_teaser_page(story)
        
        # Generate PDF
        print("📖 Building PDF...")
        doc.build(story)
        
        print(f"✅ SUCCESS! Complete book generated: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        return output_file


def main():
    """Main function to generate the complete book"""
    base_path = Path(__file__).parent.parent
    volume_path = base_path / "books" / "active_production" / "Large_Print_Sudoku_Masters" / "volume_1"
    
    if not volume_path.exists():
        print(f"❌ ERROR: Volume path not found: {volume_path}")
        return
    
    generator = CompleteSudokuBookGenerator(volume_path)
    output_file = generator.generate_complete_book()
    
    print(f"\n🎉 BOOK COMPLETE!")
    print(f"📁 Location: {output_file}")
    print(f"🚀 Ready for KDP upload!")


if __name__ == "__main__":
    main()