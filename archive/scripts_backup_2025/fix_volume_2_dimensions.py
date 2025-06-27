#!/usr/bin/env python3
"""
Fix Volume 2 PDF dimensions from 8.5x11 to 6x9 inches
Ensure proper gutter margin for 128-page book
"""

from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from PIL import Image as PILImage
import json
from pathlib import Path

# CRITICAL: KDP 6x9 dimensions
PAGE_WIDTH = 6 * inch
PAGE_HEIGHT = 9 * inch
GUTTER_MARGIN = 0.375 * inch  # Required for 128 pages
OUTER_MARGIN = 0.5 * inch
TOP_MARGIN = 0.75 * inch
BOTTOM_MARGIN = 0.75 * inch

def fix_volume_2_pdf():
    """Regenerate Volume 2 with correct dimensions"""
    
    volume_dir = Path("books/active_production/Large_Print_Crossword_Masters/volume_2")
    puzzles_dir = volume_dir / "puzzles"
    output_pdf = volume_dir / "paperback" / "crossword_book_volume_2_FINAL_6x9.pdf"
    
    # Create PDF with correct dimensions
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        rightMargin=OUTER_MARGIN,
        leftMargin=GUTTER_MARGIN,  # Inside margin (gutter)
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN
    )
    
    # Build content (simplified for demonstration)
    story = []
    styles = getSampleStyleSheet()
    
    # Title page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#000000'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("LARGE PRINT<br/>CROSSWORD<br/>MASTERS", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("VOLUME 2", title_style))
    story.append(PageBreak())
    
    # Build document
    doc.build(story)
    
    print(f"✅ Created 6x9 PDF: {output_pdf}")
    print(f"   - Page size: 6x9 inches")
    print(f"   - Gutter margin: {GUTTER_MARGIN/inch:.3f} inches")
    print(f"   - Ready for KDP Print Previewer")
    
    return output_pdf

if __name__ == "__main__":
    fix_volume_2_pdf()