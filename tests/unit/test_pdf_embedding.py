#!/usr/bin/env python3
"""
Test if PDF embedding is causing the visual distinction loss
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer


def test_direct_embedding():
    """Test direct embedding of a puzzle image in PDF."""

    # Test with puzzle 98 (one the user showed)
    png_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/sudoku_puzzle_098.png"
    )

    if not png_path.exists():
        print(f"❌ PNG not found: {png_path}")
        return False

    # Create test PDF with EXACT same embedding method
    test_pdf_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback/TEST_EMBEDDING_98.pdf"
    )

    print(f"🎨 Creating embedding test PDF: {test_pdf_path}")

    doc = SimpleDocTemplate(str(test_pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Add title
    story.append(Paragraph("EMBEDDING TEST - Puzzle 98", styles["Title"]))
    story.append(Spacer(1, 0.5 * inch))

    # Add the image using EXACT same method as sudoku_pdf_layout_v2.py
    img = Image(str(png_path), width=5 * inch, height=5 * inch)
    img.hAlign = "CENTER"
    story.append(img)

    story.append(Spacer(1, 0.5 * inch))
    story.append(
        Paragraph(
            "If fix worked: Should see light gray empty cells and bold black clues",
            styles["Normal"],
        )
    )

    doc.build(story)

    print(f"✅ Test PDF created: {test_pdf_path}")
    return True


def test_canvas_embedding():
    """Test canvas-based embedding (alternative method)."""

    png_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/sudoku_puzzle_100.png"
    )

    if not png_path.exists():
        print(f"❌ PNG not found: {png_path}")
        return False

    test_pdf_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback/TEST_CANVAS_100.pdf"
    )

    print(f"🎨 Creating canvas test PDF: {test_pdf_path}")

    c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
    width, height = letter

    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(
        width / 2, height - 1 * inch, "CANVAS EMBEDDING TEST - Puzzle 100"
    )

    # Add image using canvas method with NO compression
    img_width = 5 * inch
    img_height = 5 * inch
    x = (width - img_width) / 2
    y = height / 2 - img_height / 2

    # Draw image without any compression or quality loss
    c.drawImage(
        str(png_path),
        x,
        y,
        width=img_width,
        height=img_height,
        preserveAspectRatio=True,
    )

    # Add note
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2, y - 0.5 * inch, "Canvas method - should preserve exact PNG quality"
    )

    c.save()
    print(f"✅ Canvas test PDF created: {test_pdf_path}")
    return True


if __name__ == "__main__":
    print("🧪 TESTING PDF EMBEDDING METHODS")
    print("=" * 50)

    # Test both methods
    print("\n📄 Testing Platypus embedding (same as main PDF)...")
    test_direct_embedding()

    print("\n🎨 Testing Canvas embedding (alternative method)...")
    test_canvas_embedding()

    print("\n" + "=" * 50)
    print("🔍 Now test these PDFs to see which method preserves visual distinction!")
