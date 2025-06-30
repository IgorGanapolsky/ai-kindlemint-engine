#!/usr/bin/env python3
"""
Simple test to create a PDF with just puzzle 100 to verify the visual fix
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def create_test_pdf():
    """Create a simple test PDF with the fixed puzzle 100."""

    puzzle_image = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/sudoku_puzzle_100.png"
    )

    if not puzzle_image.exists():
        print(f"❌ Puzzle image not found: {puzzle_image}")
        return False

    # Create test PDF
    test_pdf_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback/TEST_PUZZLE_100.pdf"
    )

    print(f"🎨 Creating test PDF: {test_pdf_path}")

    c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
    width, height = letter

    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 1 * inch, "Puzzle 100 - VISUAL FIX TEST")

    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 1.5 * inch, "Difficulty: Hard")

    # Add the fixed puzzle image
    if puzzle_image.exists():
        # Center the image
        img_width = 5 * inch
        img_height = 5 * inch
        x = (width - img_width) / 2
        y = height / 2 - img_height / 2

        c.drawImage(str(puzzle_image), x, y, width=img_width, height=img_height)

        # Add note
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            width / 2,
            y - 0.5 * inch,
            "If fix worked: Clues should be BOLD, empty cells should have light background",
        )

    c.save()
    print(f"✅ Test PDF created: {test_pdf_path}")
    return True


if __name__ == "__main__":
    success = create_test_pdf()
    if success:
        print("\n🔍 Open the TEST_PUZZLE_100.pdf to verify visual distinction!")
    else:
        print("\n❌ Failed to create test PDF")
