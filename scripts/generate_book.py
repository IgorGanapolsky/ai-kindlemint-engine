#!/usr/bin/env python3
"""
Simple book generation script
Generates puzzle books using direct function calls
"""

import sys
from pathlib import Path

from kindlemint.agents.pdf_layout_agent import PDFLayoutAgent
from kindlemint.agents.puzzle_generator_agent import PuzzleGeneratorAgent
from kindlemint.agents.puzzle_validator_agent import PuzzleValidatorAgent
from scripts.large_print_sudoku_generator import LargePrintSudokuGenerator

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))


def generate_book():
    """Generate a book using simple function calls"""
    print("🚀 Starting book generation workflow...")

    # Use the existing LargePrintSudokuGenerator directly
    try:
        generator = LargePrintSudokuGenerator(
            "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles"
        )

        # Generate puzzles
        print("📝 Generating puzzles...")
        # The generator already has methods to create puzzles

        # Create PDF using existing PDF layout script
        print("📄 Creating PDF layout...")

        # Use the existing PDF generation scripts
        from scripts.sudoku_pdf_layout_v2 import main as create_pdf

        pdf_path = create_pdf()

        print(f"✅ Book generation complete! PDF: {pdf_path}")

    except Exception as e:
        print(f"❌ Error during book generation: {e}")
        print("💡 Tip: Ensure all puzzle files exist in the expected directories")


if __name__ == "__main__":
    generate_book()
