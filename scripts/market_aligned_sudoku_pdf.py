#!/usr/bin/env python3
"""
Market-Aligned Sudoku PDF Generator
Based on comprehensive market analysis of bestselling Sudoku books
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer


class MarketAlignedSudokuPDF:
    """Generate truly large print Sudoku PDFs based on market research"""

    def __init__(
        self,
        input_dir,
        output_dir,
        title,
        author,
        subtitle=None,
        page_size="letter",
        isbn=None,
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.title = title
        self.author = author
        self.subtitle = subtitle
        self.isbn = isbn or "978-0-00000-000-0"

        # Page setup for TRUE large print
        self.page_size = letter
        self.page_width = self.page_size[0]
        self.page_height = self.page_size[1]

        # Generous margins for senior-friendly layout
        self.left_margin = 1.25 * inch
        self.right_margin = 1.0 * inch
        self.top_margin = 1.25 * inch
        self.bottom_margin = 1.25 * inch

        # Load puzzles
        self.load_puzzle_metadata()
        self.setup_styles()

    def load_puzzle_metadata(self):
        """Load puzzle metadata"""
        metadata_dir = self.input_dir / "metadata"
        collection_file = metadata_dir / "sudoku_collection.json"

        if not collection_file.exists():
            raise FileNotFoundError(f"Collection metadata not found: {collection_file}")

        with open(collection_file) as f:
            self.collection_data = json.load(f)

        # Load individual puzzles
        self.puzzles = []
        for puzzle_id in self.collection_data.get("puzzles", []):
            puzzle_file = metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"
            if puzzle_file.exists():
                with open(puzzle_file) as f:
                    self.puzzles.append(json.load(f))

    def setup_styles(self):
        """Setup styles optimized for seniors and visual accessibility"""
        self.styles = getSampleStyleSheet()

        # Title page - extra large and clear
        self.styles.add(
            ParagraphStyle(
                name="BookTitle",
                parent=self.styles["Title"],
                fontSize=44,
                leading=52,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=36,
                fontName="Helvetica-Bold",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="BookSubtitle",
                parent=self.styles["Title"],
                fontSize=28,
                leading=34,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=24,
                fontName="Helvetica",
            )
        )

        # Section headers - clear and prominent
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=32,
                leading=38,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=24,
                spaceBefore=36,
                fontName="Helvetica-Bold",
            )
        )

        # Puzzle headers - large and clear
        self.styles.add(
            ParagraphStyle(
                name="PuzzleNumber",
                parent=self.styles["Heading1"],
                fontSize=28,
                leading=32,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=12,
                fontName="Helvetica-Bold",
            )
        )

        # Body text - optimized for readability
        self.styles.add(
            ParagraphStyle(
                name="LargeBody",
                parent=self.styles["Normal"],
                fontSize=16,
                leading=24,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=12,
                fontName="Helvetica",
            )
        )

        # Instructions - clear and easy to follow
        self.styles.add(
            ParagraphStyle(
                name="Instructions",
                parent=self.styles["Normal"],
                fontSize=18,
                leading=26,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=16,
                fontName="Helvetica",
            )
        )

    def generate_pdf(self):
        """Generate the complete PDF with market-aligned features"""
        filename = f"{self.title.replace(':', '').replace(' ', '_')}_Interior.pdf"
        pdf_path = self.output_dir / filename

        # Create document with proper page numbering
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=self.page_size,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title=self.title,
            author=self.author,
        )

        # Build content
        story = []

        # Front matter
        self.create_title_page(story)
        self.create_copyright_page(story)
        self.create_welcome_page(story)
        self.create_how_to_play_page(story)
        self.create_tips_and_strategies_page(story)
        self.create_cognitive_benefits_page(story)

        # Puzzles with solutions after each section
        self.create_puzzle_sections(story)

        # Back matter
        self.create_about_author_page(story)
        self.create_other_books_page(story)

        # Build PDF
        doc.build(story, canvasmaker=NumberedCanvas)

        print(f"✅ Market-aligned PDF generated: {pdf_path}")
        print(
            "📄 Features: True large print, solutions after puzzles, tips & tutorials"
        )

        return str(pdf_path)

    def create_title_page(self, story):
        """Create an appealing title page"""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(self.title, self.styles["BookTitle"]))

        if self.subtitle:
            story.append(Paragraph(self.subtitle, self.styles["BookSubtitle"]))

        story.append(Spacer(1, 1 * inch))

        # Add visual element
        story.append(Paragraph("◼ ◻ ◼ ◻ ◼ ◻ ◼ ◻ ◼", self.styles["BookTitle"]))

        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(f"by {self.author}", self.styles["BookSubtitle"]))

        story.append(PageBreak())

    def create_welcome_page(self, story):
        """Create a welcoming introduction"""
        story.append(
            Paragraph(
                "Welcome to Large Print Sudoku Masters!", self.styles["SectionHeader"]
            )
        )
        story.append(Spacer(1, 0.5 * inch))

        welcome_text = """
        Thank you for choosing Large Print Sudoku Masters! This book has been
        specially designed with your comfort and enjoyment in mind.

        <b>What Makes This Book Special:</b>

        • <b>True Large Print:</b> Every number is printed in extra-large size
        • <b>One Puzzle Per Page:</b> No cramped layouts or eye strain
        • <b>Solutions After Each Section:</b> Check your work easily
        • <b>Clear Grid Lines:</b> Easy to see and follow
        • <b>Premium Paper:</b> Designed for pencil use and erasing

        Whether you're new to Sudoku or a seasoned solver, these puzzles will
        provide hours of enjoyable brain training. Take your time, use a pencil,
        and most importantly - have fun!
        """

        for para in welcome_text.strip().split("\n\n"):
            story.append(Paragraph(para.strip(), self.styles["LargeBody"]))
            story.append(Spacer(1, 0.2 * inch))

        story.append(PageBreak())

    def create_how_to_play_page(self, story):
        """Create comprehensive how-to-play instructions"""
        story.append(Paragraph("How to Play Sudoku", self.styles["SectionHeader"]))
        story.append(Spacer(1, 0.3 * inch))

        instructions = [
            "<b>The Goal:</b> Fill every empty square so that each row, column, "
            "and 3×3 box contains the numbers 1 through 9.",
            "<b>The Rules:</b>",
            "1. Each row must contain the numbers 1-9 (no repeats)",
            "2. Each column must contain the numbers 1-9 (no repeats)",
            "3. Each 3×3 box must contain the numbers 1-9 (no repeats)",
            "<b>Getting Started:</b>",
            "• Look for rows, columns, or boxes with the most numbers filled in",
            "• Find where a specific number MUST go by elimination",
            "• Use pencil marks to note possible numbers in empty cells",
            "• Take breaks if you get stuck - fresh eyes help!",
            "<b>Remember:</b> Every puzzle has only one correct solution, and you "
            "can solve it through logic alone - no guessing required!",
        ]

        for instruction in instructions:
            story.append(Paragraph(instruction, self.styles["Instructions"]))
            story.append(Spacer(1, 0.3 * inch))

        story.append(PageBreak())

    def create_tips_and_strategies_page(self, story):
        """Create tips page based on market research"""
        story.append(Paragraph("Tips for Success", self.styles["SectionHeader"]))
        story.append(Spacer(1, 0.3 * inch))

        tips = [
            "<b>Scanning Method:</b> Look across rows and down columns to find "
            "where numbers must go. This is the most basic solving technique.",
            "<b>Single Candidates:</b> Find cells where only one number can fit "
            "based on what's already in that row, column, and box.",
            "<b>Pencil Marks:</b> Write small numbers in cells to track possibilities. "
            "Cross them out as you eliminate options.",
            "<b>Hidden Singles:</b> Sometimes a number can only go in one cell "
            "within a row, column, or box, even if other numbers could also fit there.",
            "<b>Take Your Time:</b> Sudoku is not a race. Enjoy the process of "
            "logical deduction and the satisfaction of finding each number's place.",
        ]

        for tip in tips:
            story.append(Paragraph(tip, self.styles["LargeBody"]))
            story.append(Spacer(1, 0.3 * inch))

        story.append(PageBreak())

    def create_cognitive_benefits_page(self, story):
        """Add cognitive benefits information as per market research"""
        story.append(Paragraph("Brain Training Benefits", self.styles["SectionHeader"]))
        story.append(Spacer(1, 0.3 * inch))

        benefits = [
            "Research shows that regular puzzle-solving can help maintain and "
            "improve cognitive function. Here's how Sudoku helps your brain:",
            "<b>• Memory Enhancement:</b> Remembering number placements and "
            "possibilities exercises your short-term memory.",
            "<b>• Logical Thinking:</b> Each puzzle requires systematic reasoning "
            "and deductive logic to solve.",
            "<b>• Concentration:</b> Focusing on puzzles helps improve attention "
            "span and concentration abilities.",
            "<b>• Pattern Recognition:</b> Spotting number patterns enhances your "
            "brain's pattern recognition skills.",
            "<b>• Stress Relief:</b> The focused nature of puzzle-solving can be "
            "meditative and reduce stress.",
            "Make Sudoku part of your daily routine - even 15 minutes a day can "
            "contribute to keeping your mind sharp and engaged!",
        ]

        for benefit in benefits:
            story.append(Paragraph(benefit, self.styles["LargeBody"]))
            story.append(Spacer(1, 0.25 * inch))

        story.append(PageBreak())

    def create_puzzle_sections(self, story):
        """Create puzzle sections with solutions after each group"""
        # Group puzzles by difficulty or in sections of 10
        section_size = 10
        total_sections = (len(self.puzzles) + section_size - 1) // section_size

        for section_num in range(total_sections):
            start_idx = section_num * section_size
            end_idx = min(start_idx + section_size, len(self.puzzles))
            section_puzzles = self.puzzles[start_idx:end_idx]

            # Section header
            story.append(
                Paragraph(
                    f"Puzzles {start_idx + 1} - {end_idx}", self.styles["SectionHeader"]
                )
            )
            story.append(PageBreak())

            # Add puzzles
            for i, puzzle in enumerate(section_puzzles):
                self.create_puzzle_page(story, puzzle, start_idx + i + 1)

            # Add solutions for this section
            story.append(
                Paragraph(
                    f"Solutions {start_idx + 1} - {end_idx}",
                    self.styles["SectionHeader"],
                )
            )
            story.append(PageBreak())

            for i, puzzle in enumerate(section_puzzles):
                self.create_solution_page(story, puzzle, start_idx + i + 1)

    def create_puzzle_page(self, story, puzzle_data, puzzle_number):
        """Create a single puzzle page with TRUE large print"""
        # Puzzle header
        story.append(Paragraph(f"Puzzle {puzzle_number}", self.styles["PuzzleNumber"]))
        difficulty = puzzle_data.get("difficulty", "medium").title()
        story.append(Paragraph(f"Difficulty: {difficulty}", self.styles["LargeBody"]))
        story.append(Spacer(1, 0.5 * inch))

        # Load and display puzzle image LARGE
        puzzles_dir = self.input_dir / "puzzles" / "puzzles"
        if not puzzles_dir.exists():
            puzzles_dir = self.input_dir / "puzzles"

        image_path = puzzles_dir / f"sudoku_puzzle_{puzzle_data['id']:03d}.png"

        if image_path.exists():
            # Make puzzle image TRULY large
            img = Image(str(image_path), width=6 * inch, height=6 * inch)
            img.hAlign = "CENTER"
            story.append(img)
        else:
            # Generate puzzle grid from data if image missing
            self.create_puzzle_grid(story, puzzle_data)

        story.append(PageBreak())

    def create_solution_page(self, story, puzzle_data, puzzle_number):
        """Create solution page right after puzzles as market research suggests"""
        story.append(
            Paragraph(f"Solution - Puzzle {puzzle_number}", self.styles["PuzzleNumber"])
        )
        story.append(Spacer(1, 0.3 * inch))

        # Solution image
        solutions_dir = self.input_dir / "puzzles" / "puzzles"
        if not solutions_dir.exists():
            solutions_dir = self.input_dir / "puzzles"

        solution_path = solutions_dir / f"sudoku_solution_{puzzle_data['id']:03d}.png"

        if solution_path.exists():
            img = Image(str(solution_path), width=4 * inch, height=4 * inch)
            img.hAlign = "CENTER"
            story.append(img)
        else:
            # Generate solution grid from data
            self.create_solution_grid(story, puzzle_data)

        story.append(PageBreak())

    def create_about_author_page(self, story):
        """Add author information"""
        story.append(Paragraph("About the Author", self.styles["SectionHeader"]))
        story.append(Spacer(1, 0.5 * inch))

        about_text = f"""
        {self.author} is dedicated to creating high-quality puzzle books that are
        both enjoyable and accessible. With a focus on large print formats and
        user-friendly designs, their books have helped thousands of puzzle
        enthusiasts enjoy their favorite pastime without eye strain.

        This Large Print Sudoku Masters series represents years of research into
        what makes the perfect puzzle book - from the size of the print to the
        quality of the puzzles themselves.
        """

        story.append(Paragraph(about_text.strip(), self.styles["LargeBody"]))
        story.append(PageBreak())

    def create_other_books_page(self, story):
        """Cross-promote other volumes"""
        story.append(
            Paragraph("More Large Print Sudoku Masters", self.styles["SectionHeader"])
        )
        story.append(Spacer(1, 0.5 * inch))

        other_books = """
        Continue your Sudoku journey with other volumes in this series:

        • <b>Volume 1:</b> Easy Puzzles - Perfect for Beginners
        • <b>Volume 2:</b> Easy to Medium - Building Confidence
        • <b>Volume 3:</b> Medium Puzzles - The Sweet Spot
        • <b>Volume 4:</b> Medium to Hard - Rising Challenge
        • <b>Volume 5:</b> Hard Puzzles - For Experienced Solvers
        • <b>Volume 6:</b> Mixed Collection - Something for Everyone

        Each volume contains 100-120 puzzles with the same large print format
        and user-friendly features you've come to expect.

        Available on Amazon in paperback and Kindle formats.
        """

        story.append(Paragraph(other_books.strip(), self.styles["LargeBody"]))

    def create_copyright_page(self, story):
        """Create copyright page"""
        copyright_text = f"""
        {self.title}

        Copyright © {datetime.now().year} by {self.author}

        All rights reserved. No part of this publication may be reproduced,
        distributed, or transmitted in any form or by any means, without
        prior written permission.

        ISBN: {self.isbn}

        First Edition: {datetime.now().strftime('%B %Y')}

        Printed in the United States of America
        """

        story.append(Paragraph(copyright_text.strip(), self.styles["Normal"]))
        story.append(PageBreak())


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds page numbers"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to all pages"""
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 6:  # Skip numbering front matter
                self.draw_page_number()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self):
        """Draw page number at bottom center"""
        self.setFont("Helvetica", 14)
        self.drawCentredString(
            self._pagesize[0] / 2,
            0.75 * inch,
            str(self._pageNumber - 6),  # Adjust for front matter
        )


def main():
    parser = argparse.ArgumentParser(
        description="Generate market-aligned Sudoku PDF with true large print"
    )
    parser.add_argument("--input", required=True, help="Input puzzles directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", required=True, help="Author name")
    parser.add_argument("--subtitle", help="Book subtitle")
    parser.add_argument("--isbn", help="ISBN number")

    args = parser.parse_args()

    try:
        generator = MarketAlignedSudokuPDF(
            input_dir=args.input,
            output_dir=args.output,
            title=args.title,
            author=args.author,
            subtitle=args.subtitle,
            isbn=args.isbn,
        )

        pdf_file = generator.generate_pdf()
        print(f"📚 Market-aligned PDF complete: {pdf_file}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    main()
