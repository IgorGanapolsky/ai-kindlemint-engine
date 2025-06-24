#!/usr/bin/env python3
"""
Book Layout Bot - Automated PDF interior generation for KindleMint Engine
Creates print-ready PDF interiors from puzzle data
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

class BookLayoutBot:
    def __init__(self, book_config, puzzle_dir, output_dir):
        self.config = book_config
        self.puzzle_dir = Path(puzzle_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Page setup
        self.page_width, self.page_height = letter  # 8.5 x 11 inches
        self.margin = 1 * inch
        
    def load_puzzles(self):
        """Load puzzle data from JSON files"""
        index_file = self.puzzle_dir / "puzzles_index.json"
        if not index_file.exists():
            raise FileNotFoundError(f"Puzzles index not found: {index_file}")
            
        with open(index_file, 'r') as f:
            index_data = json.load(f)
            
        return index_data['puzzles']
        
    def create_title_page(self, c):
        """Create book title page"""
        # Title
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(self.page_width/2, self.page_height - 2*inch, "LARGE PRINT")
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(self.page_width/2, self.page_height - 3*inch, "CROSSWORD")
        c.drawCentredString(self.page_width/2, self.page_height - 4*inch, "MASTERS")
        
        # Volume
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(self.page_width/2, self.page_height - 5.5*inch, f"VOLUME {self.config['volume']}")
        
        # Subtitle
        c.setFont("Helvetica", 20)
        c.drawCentredString(self.page_width/2, self.page_height - 7*inch, self.config['subtitle'])
        
        # Publisher
        c.setFont("Helvetica", 16)
        c.drawCentredString(self.page_width/2, 2*inch, self.config['publisher'])
        
        c.showPage()
        
    def create_copyright_page(self, c):
        """Create copyright page"""
        c.setFont("Helvetica", 12)
        year = datetime.now().year
        
        y_pos = self.page_height - 2*inch
        c.drawString(self.margin, y_pos, f"Copyright © {year} {self.config['publisher']}")
        
        y_pos -= 0.3*inch
        c.drawString(self.margin, y_pos, "All rights reserved.")
        
        y_pos -= 0.5*inch
        c.drawString(self.margin, y_pos, f"Volume {self.config['volume']}")
        
        y_pos -= 0.3*inch
        c.drawString(self.margin, y_pos, "First Edition")
        
        y_pos -= 0.5*inch
        c.drawString(self.margin, y_pos, "No part of this publication may be reproduced, distributed, or transmitted")
        y_pos -= 0.2*inch
        c.drawString(self.margin, y_pos, "in any form or by any means without prior written permission.")
        
        y_pos -= 0.5*inch
        c.drawString(self.margin, y_pos, f"Published by: {self.config['publisher']}")
        
        y_pos -= 0.5*inch
        c.drawString(self.margin, y_pos, "Printed in the United States of America")
        
        c.showPage()
        
    def create_toc(self, c, puzzles):
        """Create table of contents"""
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.page_width/2, self.page_height - 1.5*inch, "TABLE OF CONTENTS")
        
        c.setFont("Helvetica", 12)
        y_pos = self.page_height - 2.5*inch
        
        # Intro sections
        c.drawString(self.margin, y_pos, "Introduction")
        c.drawRightString(self.page_width - self.margin, y_pos, "5")
        y_pos -= 0.3*inch
        
        c.drawString(self.margin, y_pos, "How to Solve")
        c.drawRightString(self.page_width - self.margin, y_pos, "6")
        y_pos -= 0.3*inch
        
        # Puzzles section
        y_pos -= 0.2*inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_pos, "PUZZLES")
        c.setFont("Helvetica", 12)
        y_pos -= 0.3*inch
        
        for i, puzzle in enumerate(puzzles):
            if y_pos < 2*inch:  # New page if needed
                c.showPage()
                y_pos = self.page_height - 1*inch
                
            # Calculate page number (rough estimate)
            page_num = 7 + (i * 2)  # Each puzzle takes ~2 pages
            
            c.drawString(self.margin + 0.2*inch, y_pos, f"Puzzle {puzzle['id']}: {puzzle['theme']}")
            c.drawRightString(self.page_width - self.margin, y_pos, str(page_num))
            y_pos -= 0.25*inch
            
        # Answer key
        y_pos -= 0.2*inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_pos, "ANSWER KEY")
        answer_page = 7 + (len(puzzles) * 2) + 1
        c.drawRightString(self.page_width - self.margin, y_pos, str(answer_page))
        
        c.showPage()
        
    def create_introduction(self, c):
        """Create introduction page"""
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.page_width/2, self.page_height - 1.5*inch, "INTRODUCTION")
        
        c.setFont("Helvetica", 12)
        text = [
            f"Welcome to Volume {self.config['volume']} of Large Print Crossword Masters!",
            "",
            "This collection has been specially designed with you in mind. Every puzzle",
            "features extra-large print that's easy on your eyes, allowing you to enjoy",
            "the mental stimulation of crosswords without the strain.",
            "",
            "In this volume, you'll find a carefully curated selection of puzzles that",
            "progress in difficulty. Whether you're warming up with easier puzzles or",
            "challenging yourself with the harder ones, each crossword is crafted to",
            "provide satisfaction and mental exercise.",
            "",
            "Take your time, enjoy the journey, and remember - every puzzle solved is",
            "a victory for your mind!",
            "",
            "Happy solving!",
            "",
            "The Crossword Masters Team"
        ]
        
        y_pos = self.page_height - 2.5*inch
        for line in text:
            c.drawString(self.margin, y_pos, line)
            y_pos -= 0.3*inch
            
        c.showPage()
        
    def create_how_to_solve(self, c):
        """Create how-to-solve page"""
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.page_width/2, self.page_height - 1.5*inch, "HOW TO SOLVE")
        
        c.setFont("Helvetica", 12)
        y_pos = self.page_height - 2.5*inch
        
        sections = [
            ("Getting Started:", [
                "• Read through all the clues first",
                "• Start with the clues you're confident about",
                "• Fill in the letters you know for certain"
            ]),
            ("", []),
            ("Tips for Success:", [
                "• Look for common letter patterns",
                "• Check crossing words to verify your answers",
                "• Don't be afraid to erase and try again",
                "• Take breaks if you get stuck"
            ]),
            ("", []),
            ("Clue Types:", [
                "• Direct definitions: 'Feline pet' = CAT",
                "• Fill-in-the-blank: 'Ready, ___, go!' = SET",
                "• Wordplay: 'Sound of contentment' = PURR",
                "• Abbreviations marked: 'Doctor (abbr.)' = MD"
            ])
        ]
        
        for title, items in sections:
            if title:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(self.margin, y_pos, title)
                y_pos -= 0.3*inch
                c.setFont("Helvetica", 12)
                
            for item in items:
                c.drawString(self.margin, y_pos, item)
                y_pos -= 0.25*inch
                
        c.showPage()
        
    def create_puzzle_pages(self, c, puzzles):
        """Create puzzle pages"""
        for puzzle in puzzles:
            # Puzzle header page
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(self.page_width/2, self.page_height - 1.5*inch, f"PUZZLE {puzzle['id']}")
            
            c.setFont("Helvetica", 18)
            c.drawCentredString(self.page_width/2, self.page_height - 2*inch, f"Theme: {puzzle['theme']}")
            c.drawCentredString(self.page_width/2, self.page_height - 2.5*inch, f"Difficulty: {puzzle['difficulty'].upper()}")
            
            # Grid image
            img_path = Path(puzzle['grid_image'])
            if img_path.exists():
                # Center the grid on the page
                grid_size = 5.5 * inch
                x_pos = (self.page_width - grid_size) / 2
                y_pos = 2.5 * inch
                
                c.drawImage(str(img_path), x_pos, y_pos, width=grid_size, height=grid_size)
            
            c.showPage()
            
            # Clues page
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(self.page_width/2, self.page_height - 1*inch, f"Puzzle {puzzle['id']} - Clues")
            
            # Across clues
            c.setFont("Helvetica-Bold", 14)
            c.drawString(self.margin, self.page_height - 1.5*inch, "ACROSS")
            
            c.setFont("Helvetica", 11)
            y_pos = self.page_height - 2*inch
            
            for clue_data in puzzle['clues']['across']:
                c.drawString(self.margin, y_pos, f"{clue_data['number']}. {clue_data['clue']}")
                y_pos -= 0.3*inch
                
            # Down clues
            c.setFont("Helvetica-Bold", 14)
            c.drawString(self.page_width/2, self.page_height - 1.5*inch, "DOWN")
            
            c.setFont("Helvetica", 11)
            y_pos = self.page_height - 2*inch
            
            for clue_data in puzzle['clues']['down']:
                c.drawString(self.page_width/2, y_pos, f"{clue_data['number']}. {clue_data['clue']}")
                y_pos -= 0.3*inch
                
            c.showPage()
            
    def create_answer_key(self, c, puzzles):
        """Create answer key section"""
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.page_width/2, self.page_height - 1.5*inch, "ANSWER KEY")
        c.showPage()
        
        # Group puzzles by page
        puzzles_per_page = 3
        
        for i in range(0, len(puzzles), puzzles_per_page):
            page_puzzles = puzzles[i:i+puzzles_per_page]
            y_start = self.page_height - 1.5*inch
            
            for j, puzzle in enumerate(page_puzzles):
                y_offset = j * 3*inch
                
                # Puzzle header
                c.setFont("Helvetica-Bold", 14)
                c.drawString(self.margin, y_start - y_offset, f"Puzzle {puzzle['id']} - {puzzle['theme']}")
                
                # Answers in two columns
                c.setFont("Helvetica", 10)
                y_pos = y_start - y_offset - 0.3*inch
                
                # Across
                c.drawString(self.margin, y_pos, "ACROSS:")
                y_pos -= 0.2*inch
                
                for clue_data in puzzle['clues']['across']:
                    c.drawString(self.margin + 0.2*inch, y_pos, 
                                f"{clue_data['number']}. {clue_data['answer']}")
                    y_pos -= 0.2*inch
                    
                # Down  
                y_pos = y_start - y_offset - 0.3*inch
                c.drawString(self.page_width/2, y_pos, "DOWN:")
                y_pos -= 0.2*inch
                
                for clue_data in puzzle['clues']['down']:
                    c.drawString(self.page_width/2 + 0.2*inch, y_pos, 
                                f"{clue_data['number']}. {clue_data['answer']}")
                    y_pos -= 0.2*inch
                    
            c.showPage()
            
    def create_back_matter(self, c):
        """Create back matter pages"""
        # About the publisher
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.page_width/2, self.page_height - 1.5*inch, "ABOUT THE PUBLISHER")
        
        c.setFont("Helvetica", 12)
        y_pos = self.page_height - 2.5*inch
        
        text = [
            "Crossword Masters Publishing is dedicated to creating high-quality",
            "puzzle books that combine mental stimulation with accessibility.",
            "",
            "Our Large Print series is specially designed for puzzle enthusiasts",
            "who appreciate clear, readable formats without compromising on",
            "challenge or entertainment value.",
            "",
            "Look for other volumes in the Large Print Crossword Masters series!"
        ]
        
        for line in text:
            c.drawString(self.margin, y_pos, line)
            y_pos -= 0.3*inch
            
        c.showPage()
        
    def generate_pdf(self):
        """Generate complete PDF interior"""
        # Load puzzles
        puzzles = self.load_puzzles()
        
        # Create PDF
        pdf_path = self.output_dir / f"{self.config['series_name']}_volume_{self.config['volume']}_interior.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Set document info
        c.setTitle(f"{self.config['title']} - Volume {self.config['volume']}")
        c.setAuthor(self.config['author'])
        c.setSubject(self.config['subtitle'])
        
        print(f"📖 Creating PDF interior for Volume {self.config['volume']}...")
        
        # Create pages
        self.create_title_page(c)
        self.create_copyright_page(c)
        self.create_toc(c, puzzles)
        self.create_introduction(c)
        self.create_how_to_solve(c)
        self.create_puzzle_pages(c, puzzles)
        self.create_answer_key(c, puzzles)
        self.create_back_matter(c)
        
        # Save PDF
        c.save()
        
        print(f"✅ PDF created: {pdf_path}")
        return pdf_path

def main():
    parser = argparse.ArgumentParser(description='Generate PDF book interior')
    parser.add_argument('--book-config', required=True, help='Path to book configuration JSON')
    parser.add_argument('--puzzle-dir', required=True, help='Directory containing puzzle data')
    parser.add_argument('--output-dir', required=True, help='Output directory for PDF')
    parser.add_argument('--page_size', default='letter', help='Page size')
    parser.add_argument('--font_size', type=int, default=12, help='Base font size')
    parser.add_argument('--include_solutions', type=bool, default=True, help='Include answer key')
    parser.add_argument('--title_page', type=bool, default=True, help='Include title page')
    parser.add_argument('--toc', type=bool, default=True, help='Include table of contents')
    parser.add_argument('--answer_key', type=bool, default=True, help='Include answer key')
    
    args = parser.parse_args()
    
    # Load book config
    with open(args.book_config, 'r') as f:
        book_config = json.load(f)
        
    # Create layout bot
    bot = BookLayoutBot(
        book_config=book_config,
        puzzle_dir=args.puzzle_dir,
        output_dir=args.output_dir
    )
    
    # Generate PDF
    bot.generate_pdf()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())