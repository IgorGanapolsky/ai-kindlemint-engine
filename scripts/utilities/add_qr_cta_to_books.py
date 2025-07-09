#!/usr/bin/env python3
"""
Add QR codes and CTAs to puzzle books for lead generation
Embeds email capture mechanisms directly into generated PDFs
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io
from pathlib import Path

class BookLeadMagnetGenerator:
    """Adds lead capture elements to puzzle books"""
    
    def __init__(self):
        self.qr_size = 100
        self.landing_page_base = "https://kindlemint-puzzles.com/bonus"
    
    def generate_qr_code(self, book_title: str, book_id: str = None) -> Image.Image:
        """Generate QR code for bonus content"""
        if not book_id:
            book_id = book_title.lower().replace(" ", "_").replace(",", "")
        
        # URL that tracks which book the lead came from
        bonus_url = f"{self.landing_page_base}?book={book_id}&ref=qr"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(bonus_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return qr_img, bonus_url
    
    def create_cta_page(self, book_title: str, output_path: str) -> str:
        """Create a dedicated CTA page with QR code"""
        qr_img, bonus_url = self.generate_qr_code(book_title)
        
        # Create PDF page
        pdf_path = output_path.replace('.pdf', '_with_cta.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredText(width/2, height - 100, "🎁 FREE BONUS PUZZLES!")
        
        # Add description
        c.setFont("Helvetica", 16)
        description_lines = [
            "Enjoyed these puzzles? Get 10 MORE puzzles FREE!",
            "",
            "Scan the QR code below with your phone camera",
            "or visit the link to download your bonus content."
        ]
        
        y_pos = height - 150
        for line in description_lines:
            c.drawCentredText(width/2, y_pos, line)
            y_pos -= 25
        
        # Add QR code
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_x = (width - 150) / 2
        qr_y = y_pos - 200
        c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=150, height=150)
        
        # Add URL text
        c.setFont("Helvetica", 12)
        c.drawCentredText(width/2, qr_y - 30, bonus_url)
        
        # Add footer
        c.setFont("Helvetica", 10)
        footer_lines = [
            "• Get notified when new puzzle books are released",
            "• Join thousands of puzzle enthusiasts", 
            "• No spam, unsubscribe anytime"
        ]
        
        y_footer = qr_y - 80
        for line in footer_lines:
            c.drawCentredText(width/2, y_footer, line)
            y_footer -= 15
        
        c.save()
        return pdf_path
    
    def add_inline_cta_to_book(self, original_pdf_path: str, book_title: str) -> str:
        """Add CTA elements throughout an existing puzzle book"""
        from PyPDF2 import PdfReader, PdfWriter
        import tempfile
        
        # Read original PDF
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()
        
        # Add first few pages normally
        for i in range(min(3, len(reader.pages))):
            writer.add_page(reader.pages[i])
        
        # Add CTA page after page 3
        cta_pdf_path = self.create_cta_page(book_title, original_pdf_path)
        cta_reader = PdfReader(cta_pdf_path)
        writer.add_page(cta_reader.pages[0])
        
        # Add remaining pages
        for i in range(3, len(reader.pages)):
            writer.add_page(reader.pages[i])
            
            # Add mini CTA every 20 pages
            if (i - 3) % 20 == 0:
                mini_cta = self.create_mini_cta_page(book_title)
                mini_reader = PdfReader(mini_cta)
                writer.add_page(mini_reader.pages[0])
        
        # Save enhanced PDF
        enhanced_path = original_pdf_path.replace('.pdf', '_enhanced.pdf')
        with open(enhanced_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Clean up temp files
        Path(cta_pdf_path).unlink()
        
        return enhanced_path
    
    def create_mini_cta_page(self, book_title: str) -> str:
        """Create a small CTA that can be inserted between puzzles"""
        qr_img, bonus_url = self.generate_qr_code(book_title)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            c = canvas.Canvas(tmp.name, pagesize=letter)
            width, height = letter
            
            # Simple mini CTA
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredText(width/2, height/2 + 50, "Want More Puzzles?")
            
            c.setFont("Helvetica", 12)
            c.drawCentredText(width/2, height/2 + 20, "Scan for 10 FREE bonus puzzles!")
            
            # Small QR code
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            qr_size = 80
            qr_x = (width - qr_size) / 2
            qr_y = height/2 - 40
            c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
            
            c.save()
            return tmp.name
    
    def create_landing_page_html(self, book_title: str) -> str:
        """Generate HTML for the landing page"""
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Free Bonus Puzzles - {book_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; color: #2c3e50; }}
        .form {{ background: #f8f9fa; padding: 30px; border-radius: 10px; margin: 20px 0; }}
        .btn {{ background: #27ae60; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎁 Your Free Bonus Puzzles Are Ready!</h1>
        <p>Thank you for purchasing {book_title}!</p>
    </div>
    
    <div class="form">
        <h2>Get Your 10 FREE Bonus Puzzles</h2>
        <p>Enter your email below and we'll send your bonus puzzles immediately:</p>
        
        <form action="/submit-email" method="post">
            <input type="hidden" name="book_source" value="{book_title.replace(' ', '_')}">
            <input type="email" name="email" placeholder="your@email.com" required 
                   style="width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
            <button type="submit" class="btn">Download My Free Puzzles 🧩</button>
        </form>
        
        <p style="font-size: 12px; color: #666; margin-top: 20px;">
            ✅ Instant download<br>
            ✅ No spam, ever<br>
            ✅ Unsubscribe anytime
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 30px;">
        <p>Questions? Email us at support@kindlemint-puzzles.com</p>
    </div>
</body>
</html>
        """
        
        # Save to file
        html_file = Path(f"data/landing_pages/{book_title.replace(' ', '_')}.html")
        html_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(html_file, 'w') as f:
            f.write(html_template)
        
        return str(html_file)

def enhance_book_with_lead_capture(book_pdf_path: str, book_title: str) -> dict:
    """Main function to enhance a book with lead capture"""
    generator = BookLeadMagnetGenerator()
    
    # Enhance the PDF
    enhanced_pdf = generator.add_inline_cta_to_book(book_pdf_path, book_title)
    
    # Generate landing page
    landing_page = generator.create_landing_page_html(book_title)
    
    # Generate QR info
    _, bonus_url = generator.generate_qr_code(book_title)
    
    return {
        "original_pdf": book_pdf_path,
        "enhanced_pdf": enhanced_pdf,
        "landing_page": landing_page,
        "bonus_url": bonus_url,
        "lead_capture_ready": True
    }

if __name__ == "__main__":
    # Test with a sample book
    sample_book = "books/sample/test_sudoku_book.pdf"
    result = enhance_book_with_lead_capture(sample_book, "Sample Sudoku Book")
    print(f"✅ Enhanced book ready: {result}")