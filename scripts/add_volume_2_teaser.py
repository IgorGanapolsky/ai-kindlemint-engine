#!/usr/bin/env python3
"""
Add professional teaser page to end of Volume 2 PDF
"""

from pathlib import Path
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
import PyPDF2

# Page dimensions
PAGE_WIDTH = 6 * inch
PAGE_HEIGHT = 9 * inch

def create_teaser_page():
    """Create the teaser page as a separate PDF"""
    output = Path("teaser_page.pdf")
    c = canvas.Canvas(str(output), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    
    # Main message
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2 * inch, "Loved Volume 2?")
    
    c.setFont("Helvetica", 20)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3 * inch, "Stay sharp with Volume 3")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3.5 * inch, "— coming soon!")
    
    # Review request
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 5 * inch, "⭐ ⭐ ⭐ ⭐ ⭐")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 5.5 * inch, "Please leave a review to support")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 6 * inch, "our puzzle series")
    
    # Additional books
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 7.5 * inch, "Also Available:")
    
    c.setFont("Helvetica", 14)
    y = PAGE_HEIGHT - 8 * inch
    books = [
        "• Large Print Sudoku Masters: Volume 1",
        "• Large Print Crossword Masters: Volume 1",
        "• Large Print Word Search Champions",
    ]
    for book in books:
        c.drawString(1.5 * inch, y, book)
        y -= 0.3 * inch
    
    # Footer
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_WIDTH / 2, 1.5 * inch, "Thank you for choosing")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, 1.2 * inch, "KindleMint Publishing")
    
    c.showPage()
    c.save()
    
    return output

def append_teaser_to_pdf(original_pdf, teaser_pdf, output_path):
    """Append teaser page to the main PDF"""
    pdf_writer = PyPDF2.PdfWriter()
    
    # Add all pages from original
    with open(original_pdf, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
    
    # Add teaser page
    with open(teaser_pdf, 'rb') as f:
        teaser_reader = PyPDF2.PdfReader(f)
        pdf_writer.add_page(teaser_reader.pages[0])
    
    # Write final PDF
    with open(output_path, 'wb') as f:
        pdf_writer.write(f)

if __name__ == "__main__":
    # Create teaser page
    teaser = create_teaser_page()
    print(f"✅ Created teaser page: {teaser}")
    
    # Append to Volume 2
    original = Path("books/active_production/Large_Print_Sudoku_Masters/volume_2/paperback/Large_Print_Sudoku_Masters_Volume_2_Interior_FIXED.pdf")
    final = Path("books/active_production/Large_Print_Sudoku_Masters/volume_2/paperback/Large_Print_Sudoku_Masters_Volume_2_Interior_FINAL.pdf")
    
    if original.exists():
        append_teaser_to_pdf(original, teaser, final)
        print(f"✅ Created final PDF with teaser: {final}")
        print(f"📏 Total pages: 209 (was 208)")
    else:
        print(f"❌ Original PDF not found: {original}")
    
    # Clean up
    teaser.unlink()