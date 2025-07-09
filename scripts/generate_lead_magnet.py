#!/usr/bin/env python3

    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>HOW TO SOLVE:</b> Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "<b>PUZZLE RULES:</b> Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "<b>SOLVING GOAL:</b> Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "<b>GAME RULES:</b> Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>CHALLENGE RULES:</b> Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "<b>SOLVING INSTRUCTIONS:</b> Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "<b>PUZZLE OBJECTIVE:</b> Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "<b>GAME OBJECTIVE:</b> Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>EXPERT CHALLENGE:</b> Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "<b>ADVANCED RULES:</b> Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "<b>MASTER PUZZLE:</b> Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "<b>CHALLENGE GOAL:</b> Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!",
                "<b>💡 HINT:</b> Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "<b>💡 STRATEGY:</b> Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "<b>💡 APPROACH:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 METHOD:</b> If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "<b>💡 TECHNIQUE:</b> Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "<b>💡 SHORTCUT:</b> Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "<b>💡 STRATEGY:</b> Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "<b>💡 TECHNIQUE:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "<b>💡 METHOD:</b> When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "<b>💡 APPROACH:</b> If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "<b>💡 HINT:</b> Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "<b>💡 STRATEGY:</b> Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "<b>💡 EXPERT TIP:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-WING:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 ADVANCED:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 FORCING:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "<b>💡 PATTERN:</b> Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "<b>💡 PERSISTENCE:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

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