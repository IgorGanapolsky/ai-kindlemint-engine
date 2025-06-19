"""
PDF Generator for KDP Publishing
Converts crossword manuscripts to professional PDF format
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import logging

logger = logging.getLogger(__name__)

class CrosswordPDFGenerator:
    """Generates professional PDF from crossword manuscript."""
    
    def __init__(self, page_size=letter):
        """Initialize PDF generator with specified page size."""
        self.page_size = page_size
        self.width, self.height = page_size
        self.margin = 0.75 * inch
        self.styles = self._create_styles()
        
        # Try to register custom fonts for better readability
        self._register_fonts()
    
    def _register_fonts(self):
        """Register custom fonts for better senior readability."""
        try:
            # Check if Montserrat fonts exist in project
            font_dir = Path(__file__).parent.parent.parent / "fonts"
            
            if (font_dir / "Montserrat-Regular.ttf").exists():
                pdfmetrics.registerFont(TTFont('Montserrat', str(font_dir / "Montserrat-Regular.ttf")))
                logger.info("✅ Registered Montserrat Regular font")
            
            if (font_dir / "Montserrat-Bold.ttf").exists():
                pdfmetrics.registerFont(TTFont('Montserrat-Bold', str(font_dir / "Montserrat-Bold.ttf")))
                logger.info("✅ Registered Montserrat Bold font")
                
        except Exception as e:
            logger.warning(f"Could not register custom fonts: {e}")
    
    def _create_styles(self):
        """Create typography styles optimized for seniors."""
        styles = getSampleStyleSheet()
        
        # Large print title style
        styles.add(ParagraphStyle(
            name='LargePrintTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C5F6B'),
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='LargePrintSubtitle',
            parent=styles['Normal'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4A8A94'),
            fontName='Helvetica'
        ))
        
        # Author style
        styles.add(ParagraphStyle(
            name='Author',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=40,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Large print heading
        styles.add(ParagraphStyle(
            name='LargePrintHeading',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            spaceBefore=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C5F6B'),
            fontName='Helvetica-Bold'
        ))
        
        # Large print body text
        styles.add(ParagraphStyle(
            name='LargePrintBody',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=18
        ))
        
        # Puzzle title
        styles.add(ParagraphStyle(
            name='PuzzleTitle',
            parent=styles['Normal'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2C5F6B')
        ))
        
        # Clue text
        styles.add(ParagraphStyle(
            name='ClueText',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=16
        ))
        
        # Grid text (monospace for alignment)
        styles.add(ParagraphStyle(
            name='GridText',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Courier',
            leading=12
        ))
        
        return styles
    
    def generate_pdf(self, manuscript_path: str, output_path: str, metadata: dict = None) -> bool:
        """
        Generate PDF from crossword manuscript.
        
        Args:
            manuscript_path: Path to the text manuscript
            output_path: Path for the output PDF
            metadata: Book metadata (title, author, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📄 Generating PDF: {output_path}")
            
            # Read manuscript content
            with open(manuscript_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build PDF content
            story = []
            self._parse_and_build_story(content, story, metadata)
            
            # Generate PDF
            doc.build(story)
            
            logger.info(f"✅ PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _parse_and_build_story(self, content: str, story: list, metadata: dict = None):
        """Parse manuscript content and build PDF story."""
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Title page
            if line.startswith('LARGE PRINT CROSSWORD MASTERS'):
                story.append(Paragraph(line, self.styles['LargePrintTitle']))
                i += 1
                
                # Subtitle
                if i < len(lines) and lines[i].strip():
                    story.append(Paragraph(lines[i].strip(), self.styles['LargePrintSubtitle']))
                    i += 1
                
                # Author
                if i < len(lines) and lines[i].strip().startswith('By'):
                    story.append(Paragraph(lines[i].strip(), self.styles['Author']))
                    i += 1
                
                story.append(PageBreak())
            
            # Section headers
            elif line.startswith('=') and len(line) > 10:
                i += 1
                continue
            elif line.upper() in ['INTRODUCTION', 'HOW TO SOLVE CROSSWORDS', 'ANSWER KEY']:
                story.append(Paragraph(line, self.styles['LargePrintHeading']))
                i += 1
            
            # Puzzle titles
            elif line.startswith('PUZZLE '):
                story.append(Paragraph(line, self.styles['PuzzleTitle']))
                i += 1
                
                # Parse puzzle content
                i = self._parse_puzzle(lines, i, story)
            
            # Solution titles
            elif line.endswith('SOLUTION:'):
                story.append(Paragraph(line, self.styles['PuzzleTitle']))
                i += 1
                
                # Parse solution grid
                i = self._parse_solution_grid(lines, i, story)
            
            # Regular content
            else:
                # Check if it's a benefits list
                if line.startswith('✓'):
                    story.append(Paragraph(line, self.styles['LargePrintBody']))
                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                    story.append(Paragraph(line, self.styles['LargePrintBody']))
                else:
                    story.append(Paragraph(line, self.styles['LargePrintBody']))
                i += 1
    
    def _parse_puzzle(self, lines: list, start_idx: int, story: list) -> int:
        """Parse a puzzle section including grid and clues."""
        i = start_idx
        
        # Look for grid start
        while i < len(lines) and not lines[i].strip().startswith('┌'):
            if lines[i].strip():
                story.append(Spacer(1, 6))
            i += 1
        
        if i < len(lines):
            # Parse grid
            grid_lines = []
            while i < len(lines) and (lines[i].strip().startswith(('┌', '│', '└')) or not lines[i].strip()):
                if lines[i].strip():
                    grid_lines.append(lines[i])
                i += 1
            
            # Add grid as table for better formatting
            if grid_lines:
                self._add_crossword_grid(story, grid_lines)
        
        # Parse clues
        story.append(Spacer(1, 12))
        while i < len(lines) and not lines[i].strip().startswith('-'):
            line = lines[i].strip()
            if line:
                if line in ['ACROSS:', 'DOWN:']:
                    story.append(Paragraph(f"<b>{line}</b>", self.styles['ClueText']))
                elif line.startswith(('  1.', '  2.', '  3.', '  4.', '  5.', '  6.', '  7.', '  8.', '  9.')):
                    story.append(Paragraph(line, self.styles['ClueText']))
                else:
                    story.append(Paragraph(line, self.styles['LargePrintBody']))
            i += 1
        
        # Skip separator line
        if i < len(lines) and lines[i].strip().startswith('-'):
            i += 1
        
        story.append(PageBreak())
        return i
    
    def _parse_solution_grid(self, lines: list, start_idx: int, story: list) -> int:
        """Parse a solution grid."""
        i = start_idx
        
        # Look for grid start
        while i < len(lines) and not lines[i].strip().startswith('┌'):
            i += 1
        
        if i < len(lines):
            # Parse solution grid
            grid_lines = []
            while i < len(lines) and (lines[i].strip().startswith(('┌', '│', '└')) or not lines[i].strip()):
                if lines[i].strip():
                    grid_lines.append(lines[i])
                i += 1
            
            # Add solution grid
            if grid_lines:
                self._add_solution_grid(story, grid_lines)
        
        story.append(Spacer(1, 20))
        return i
    
    def _add_crossword_grid(self, story: list, grid_lines: list):
        """Add a crossword grid to the story."""
        # Convert grid to monospace text for now
        # In a production version, you'd create a proper table
        grid_text = '\n'.join(grid_lines)
        story.append(Paragraph(f'<font name="Courier" size="8">{grid_text}</font>', self.styles['GridText']))
        story.append(Spacer(1, 12))
    
    def _add_solution_grid(self, story: list, grid_lines: list):
        """Add a solution grid to the story."""
        grid_text = '\n'.join(grid_lines)
        story.append(Paragraph(f'<font name="Courier" size="8">{grid_text}</font>', self.styles['GridText']))
    
    def generate_kdp_ready_pdf(self, book_folder: str) -> str:
        """
        Generate a KDP-ready PDF from a book folder.
        
        Args:
            book_folder: Path to book folder containing manuscript.txt
            
        Returns:
            Path to generated PDF file
        """
        try:
            book_path = Path(book_folder)
            manuscript_path = book_path / "manuscript.txt"
            metadata_path = book_path / "metadata.json"
            
            if not manuscript_path.exists():
                raise FileNotFoundError(f"Manuscript not found: {manuscript_path}")
            
            # Load metadata if available
            metadata = {}
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            # Generate PDF filename
            pdf_filename = f"{book_path.name}_KDP_READY.pdf"
            pdf_path = book_path / pdf_filename
            
            # Generate PDF
            success = self.generate_pdf(str(manuscript_path), str(pdf_path), metadata)
            
            if success:
                logger.info(f"🎉 KDP-ready PDF generated: {pdf_path}")
                return str(pdf_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ KDP PDF generation failed: {e}")
            return None

def generate_all_volume_pdfs(base_dir: str = "output/generated_books") -> list:
    """Generate PDFs for all book volumes."""
    try:
        base_path = Path(base_dir)
        if not base_path.exists():
            logger.error(f"Base directory not found: {base_dir}")
            return []
        
        generator = CrosswordPDFGenerator()
        generated_pdfs = []
        
        # Find all book folders
        for book_folder in base_path.iterdir():
            if book_folder.is_dir() and "crossword_masters" in book_folder.name:
                logger.info(f"📚 Processing: {book_folder.name}")
                
                pdf_path = generator.generate_kdp_ready_pdf(str(book_folder))
                if pdf_path:
                    generated_pdfs.append(pdf_path)
                    logger.info(f"✅ Generated: {pdf_path}")
                else:
                    logger.error(f"❌ Failed to generate PDF for: {book_folder.name}")
        
        logger.info(f"🎉 Generated {len(generated_pdfs)} PDFs total")
        return generated_pdfs
        
    except Exception as e:
        logger.error(f"❌ Batch PDF generation failed: {e}")
        return []

if __name__ == "__main__":
    # Test the PDF generator
    generator = CrosswordPDFGenerator()
    
    # Test with Volume 1
    test_folder = "output/generated_books/large_print_crossword_masters_vol_1_final"
    pdf_path = generator.generate_kdp_ready_pdf(test_folder)
    
    if pdf_path:
        print(f"✅ Test PDF generated: {pdf_path}")
    else:
        print("❌ Test PDF generation failed")