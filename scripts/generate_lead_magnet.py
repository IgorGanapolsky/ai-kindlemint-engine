#!/usr/bin/env python3
"""
Lead Magnet Generator - Creates "5 FREE Brain-Boosting Puzzles" for email capture

This script generates the exact lead magnet promised on the landing page:
- 5 easy Sudoku puzzles
- Large print (20pt+ font)
- Professional PDF with branding
- Includes teaser for paid product
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.generators.sudoku_generator import SudokuGenerator
from src.kindlemint.generators.pdf_generator import PDFGenerator

def generate_lead_magnet():
    """Generate the 5 FREE Brain-Boosting Puzzles lead magnet"""
    print("🧩 Generating Lead Magnet: 5 FREE Brain-Boosting Puzzles")
    print("=" * 60)
    
    # Initialize generators
    sudoku_gen = SudokuGenerator()
    
    # Generate 5 easy puzzles optimized for seniors
    puzzles = []
    print("Generating puzzles...")
    for i in range(1, 6):
        puzzle_data = sudoku_gen.generate_puzzle(difficulty='easy')
        puzzle_data['title'] = f"Brain Booster #{i}"
        puzzle_data['instructions'] = "Fill in the empty cells so that each row, column, and 3x3 box contains the numbers 1-9."
        puzzles.append(puzzle_data)
        print(f"✓ Generated puzzle {i}/5")
    
    # Create metadata for the lead magnet
    metadata = {
        "title": "5 FREE Brain-Boosting Sudoku Puzzles",
        "subtitle": "Large Print Edition for Seniors",
        "author": "KindleMint Publishing",
        "isbn": None,  # Lead magnets don't need ISBN
        "language": "English",
        "publication_date": datetime.now().strftime("%Y-%m-%d"),
        "trim_size": "8.5x11",
        "page_count": 12,  # Cover + 5 puzzles + 5 solutions + CTA page
        "font_size": "20pt",
        "categories": ["Games & Activities", "Brain Training", "Senior Activities"],
        "description": "Start your day with mental exercise! These 5 carefully selected Sudoku puzzles are designed with seniors in mind - featuring extra-large print that's easy on the eyes.",
        "keywords": ["large print sudoku", "brain training", "senior puzzles", "mental exercise", "easy sudoku"],
        "series": "Brain-Boosting Puzzles",
        "volume": "Free Sample",
        "kdp_book_type": {
            "low_content_book": True,
            "large_print_book": True
        }
    }
    
    # Add marketing elements
    metadata['marketing'] = {
        "lead_capture": True,
        "cta_page": {
            "title": "Enjoyed These Puzzles?",
            "content": "Get 100 more brain-boosting puzzles in our Large Print Sudoku Masters Volume 1!",
            "offer": "Special offer for email subscribers: Save 20% with code BRAIN20",
            "link": "https://www.amazon.com/dp/YOUR_ASIN_HERE"
        },
        "email_sequence_tag": "sudoku_lead_magnet"
    }
    
    # Create the lead magnet structure
    lead_magnet = {
        "metadata": metadata,
        "puzzles": puzzles,
        "generation_info": {
            "generated_date": datetime.now().isoformat(),
            "generator_version": "1.0",
            "purpose": "email_lead_magnet",
            "target_audience": "seniors_65_plus"
        }
    }
    
    # Save the lead magnet data
    output_dir = Path("generated/lead_magnets")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_dir / f"brain_boosting_puzzles_lead_magnet_{timestamp}.json"
    
    with open(json_file, 'w') as f:
        json.dump(lead_magnet, f, indent=2)
    
    print(f"\n✅ Lead magnet data saved to: {json_file}")
    
    # Generate PDF
    print("\nGenerating PDF...")
    pdf_gen = PDFGenerator()
    pdf_file = output_dir / f"5_FREE_Brain_Boosting_Puzzles_{timestamp}.pdf"
    
    # Create PDF with special lead magnet formatting
    pdf_gen.generate_lead_magnet_pdf(lead_magnet, str(pdf_file))
    
    print(f"✅ PDF generated: {pdf_file}")
    print(f"\n📧 Ready for email delivery!")
    print(f"   File size: {pdf_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    return {
        "json_file": str(json_file),
        "pdf_file": str(pdf_file),
        "metadata": metadata
    }

if __name__ == "__main__":
    result = generate_lead_magnet()
    print("\n🎯 Lead Magnet Generation Complete!")
    print(f"   JSON: {result['json_file']}")
    print(f"   PDF: {result['pdf_file']}")