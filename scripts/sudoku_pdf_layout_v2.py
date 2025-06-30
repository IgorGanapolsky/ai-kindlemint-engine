#!/usr/bin/env python3
"""
Enhanced Sudoku PDF Layout Generator for KindleMint Engine
Creates professional PDF interiors with all publishing standards
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds page numbers."""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.page_offset = 0  # Start numbering after front matter

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to all pages."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 3:  # Skip numbering title, copyright, instructions
                self.draw_page_number()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self):
        """Draw page number at bottom center."""
        self.setFont("Helvetica", 12)
        self.drawCentredString(
            self._pagesize[0] / 2,
            0.5 * inch,
            str(self._pageNumber - 3),  # Adjust for front matter
        )


class EnhancedSudokuPDFLayout:
    """Generate professional PDF layouts for Sudoku puzzle books with all elements."""

    def __init__(
        self,
        input_dir,
        output_dir,
        title,
        author,
        subtitle=None,
        page_size="letter",
        include_solutions=True,
        isbn=None,
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.title = title
        self.author = author
        self.subtitle = subtitle
        self.include_solutions = include_solutions
        self.isbn = isbn or "[ISBN TO BE ASSIGNED]"

        # Extract volume number from title
        self.volume_number = "1"  # Default
        if "Volume" in title:
            parts = title.split("Volume")
            if len(parts) > 1:
                self.volume_number = parts[1].strip().split()[0]

        # Page setup
        self.page_size = letter if page_size == "letter" else A4
        self.page_width = self.page_size[0]
        self.page_height = self.page_size[1]

        # Margins for large print books
        self.left_margin = 1.0 * inch
        self.right_margin = 0.75 * inch
        self.top_margin = 1.0 * inch
        self.bottom_margin = 1.0 * inch

        # Load puzzle metadata
        self.load_puzzle_metadata()

        # Setup styles
        self.setup_styles()

    def load_puzzle_metadata(self):
        """Load puzzle metadata from the input directory."""
        metadata_dir = self.input_dir / "metadata"
        if not metadata_dir.exists():
            metadata_dir = self.input_dir.parent / "metadata"

        collection_file = metadata_dir / "sudoku_collection.json"
        if not collection_file.exists():
            raise FileNotFoundError(f"Collection metadata not found: {collection_file}")

        with open(collection_file) as f:
            self.collection_data = json.load(f)

        # Load individual puzzle metadata
        self.puzzles = []
        for puzzle_id in self.collection_data["puzzles"]:
            puzzle_file = metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"
            if puzzle_file.exists():
                with open(puzzle_file) as f:
                    self.puzzles.append(json.load(f))

    def setup_styles(self):
        """Setup paragraph styles for the book."""
        self.styles = getSampleStyleSheet()

        # Title page styles
        self.styles.add(
            ParagraphStyle(
                name="BookTitle",
                parent=self.styles["Title"],
                fontSize=36,
                leading=42,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=30,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="BookSubtitle",
                parent=self.styles["Title"],
                fontSize=24,
                leading=28,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=20,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="BookAuthor",
                parent=self.styles["Normal"],
                fontSize=18,
                leading=22,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceBefore=40,
            )
        )

        # Section headers
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=28,
                leading=32,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=30,
                spaceBefore=30,
            )
        )

        # Puzzle page styles
        self.styles.add(
            ParagraphStyle(
                name="PuzzleNumber",
                parent=self.styles["Heading1"],
                fontSize=20,
                leading=24,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=10,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Difficulty",
                parent=self.styles["Normal"],
                fontSize=14,
                leading=18,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=20,
            )
        )

        # Instructions style
        self.styles.add(
            ParagraphStyle(
                name="Instructions",
                parent=self.styles["Normal"],
                fontSize=14,
                leading=20,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=12,
                spaceBefore=12,
            )
        )

        # Marketing style
        self.styles.add(
            ParagraphStyle(
                name="Marketing",
                parent=self.styles["Normal"],
                fontSize=16,
                leading=22,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=20,
                spaceBefore=20,
            )
        )

    def create_title_page(self, story):
        """Create the title page."""
        story.append(Spacer(1, 2 * inch))

        # Title
        story.append(Paragraph(self.title, self.styles["BookTitle"]))

        # Subtitle
        if self.subtitle:
            story.append(Paragraph(self.subtitle, self.styles["BookSubtitle"]))

        # Volume indicator
        story.append(
            Paragraph(f"Volume {self.volume_number}", self.styles["BookSubtitle"])
        )

        # Author
        story.append(Paragraph(f"by {self.author}", self.styles["BookAuthor"]))

        # Series branding
        story.append(Spacer(1, 1 * inch))
        story.append(
            Paragraph("Part of the Large Print Masters Series", self.styles["Normal"])
        )

        # Publication info
        story.append(Spacer(1, 1 * inch))
        story.append(
            Paragraph(
                f"Published {datetime.now().strftime('%Y')}<br/>© {self.author}",
                self.styles["Normal"],
            )
        )

        story.append(PageBreak())

    def create_copyright_page(self, story):
        """Create the enhanced copyright page with ISBN."""
        copyright_text = f"""
        <b>Large Print Sudoku Masters - Volume {self.volume_number}</b><br/>
        <br/>
        © {datetime.now().year} {self.author}. All rights reserved.<br/>
        <br/>
        ISBN: {self.isbn}<br/>
        <br/>
        No part of this book may be reproduced in any form or by any electronic or mechanical means,
        including information storage and retrieval systems, without written permission from the author,
        except for the use of brief quotations in a book review.<br/>
        <br/>
        <b>Publisher:</b> {self.author}<br/>
        <b>First Edition:</b> {datetime.now().strftime('%B %Y')}<br/>
        <br/>
        <b>Disclaimer:</b><br/>
        All puzzles in this book have been carefully created and tested to ensure they have
        unique solutions. The difficulty ratings are based on standard Sudoku solving techniques.<br/>
        <br/>
        <b>Large Print Edition:</b><br/>
        This book has been specially formatted with large print for comfortable reading.<br/>
        <br/>
        Printed in the United States of America
        """

        story.append(Paragraph(copyright_text, self.styles["Normal"]))
        story.append(PageBreak())

    def create_instructions_page(self, story):
        """Create the enhanced instructions page."""
        story.append(Paragraph("How to Play Sudoku", self.styles["SectionHeader"]))

        instructions = [
            "<b>Objective:</b><br/>Fill the 9×9 grid so that each column, each row, and each of the nine 3×3 boxes contains the digits 1 through 9.",
            "",
            "<b>The Rules:</b>",
            "• Each row must contain the numbers 1-9 with no repetition",
            "• Each column must contain the numbers 1-9 with no repetition",
            "• Each 3×3 box must contain the numbers 1-9 with no repetition",
            "• Use logic and deduction - no guessing required!",
            "",
            "<b>Tips for Success:</b>",
            "• Start by looking for rows, columns, or boxes with the most numbers already filled",
            "• Look for numbers that appear frequently across the grid",
            "• Use pencil marks to note possible numbers in empty cells",
            "• Take breaks if you get stuck - fresh eyes often spot new patterns",
            "",
            "<b>Difficulty Levels in This Book:</b>",
            f"This Volume {self.volume_number} contains <b>{self.puzzles[0]['difficulty'].title()}</b> level puzzles, perfect for "
            + (
                "beginners learning the basics."
                if self.puzzles[0]["difficulty"] == "easy"
                else "improving your skills."
            ),
            "",
            "<b>About This Large Print Edition:</b>",
            "• Extra-large grids for comfortable solving",
            "• Clear, bold numbers that are easy to read",
            "• One puzzle per page to avoid distractions",
            "• Complete solutions included at the back",
            "",
            "Ready to begin? Turn the page and enjoy your Sudoku journey!",
        ]

        for line in instructions:
            if line:
                story.append(Paragraph(line, self.styles["Instructions"]))
            else:
                story.append(Spacer(1, 0.2 * inch))

        story.append(PageBreak())

    def create_puzzle_page(self, story, puzzle_data, puzzle_number):
        """Create a page for a single puzzle."""
        # Puzzle header
        story.append(Paragraph(f"Puzzle {puzzle_number}", self.styles["PuzzleNumber"]))
        story.append(
            Paragraph(
                f"Difficulty: {puzzle_data['difficulty'].title()}",
                self.styles["Difficulty"],
            )
        )

        # Load puzzle image
        puzzles_dir = self.input_dir / "puzzles" / "puzzles"
        if not puzzles_dir.exists():
            puzzles_dir = self.input_dir / "puzzles"
            if not puzzles_dir.exists():
                puzzles_dir = self.input_dir.parent / "puzzles"

        image_path = puzzles_dir / f"sudoku_puzzle_{puzzle_data['id']:03d}.png"

        if image_path.exists():
            # Center the image
            img = Image(str(image_path), width=5 * inch, height=5 * inch)
            img.hAlign = "CENTER"
            story.append(img)
        else:
            story.append(
                Paragraph(
                    f"[Puzzle image not found: {image_path}]", self.styles["Normal"]
                )
            )

        story.append(PageBreak())

    def create_solutions_section(self, story):
        """Create the enhanced solutions section with answer explanations."""
        if not self.include_solutions:
            return

        # Add section header
        story.append(Paragraph("SOLUTIONS", self.styles["SectionHeader"]))
        story.append(
            Paragraph(
                "Complete solutions with solving strategies and explanations for each puzzle.",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.5 * inch))
        story.append(PageBreak())

        # Add each solution with explanation on its own page
        for i, puzzle_data in enumerate(self.puzzles):
            self.create_solution_page(story, puzzle_data, i + 1)

    def create_solution_page(self, story, puzzle_data, puzzle_number):
        """Create a solution page with image and detailed explanations."""
        # Solution header
        story.append(
            Paragraph(
                f"Solution for Puzzle {puzzle_number}", self.styles["PuzzleNumber"]
            )
        )
        story.append(
            Paragraph(
                f"Difficulty: {puzzle_data['difficulty'].title()}",
                self.styles["Difficulty"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # Load solution image
        solution_path = (
            self.input_dir
            / "puzzles"
            / "puzzles"
            / f"sudoku_solution_{puzzle_data['id']:03d}.png"
        )
        if not solution_path.exists():
            solution_path = (
                self.input_dir
                / "puzzles"
                / f"sudoku_solution_{puzzle_data['id']:03d}.png"
            )
            if not solution_path.exists():
                solution_path = (
                    self.input_dir.parent
                    / "puzzles"
                    / f"sudoku_solution_{puzzle_data['id']:03d}.png"
                )

        if solution_path.exists():
            # Center the solution image
            img = Image(str(solution_path), width=4 * inch, height=4 * inch)
            img.hAlign = "CENTER"
            story.append(img)
        else:
            story.append(
                Paragraph(
                    f"[Solution image not found: {solution_path}]",
                    self.styles["Normal"],
                )
            )

        story.append(Spacer(1, 0.5 * inch))

        # Add solving explanation based on difficulty
        story.append(Paragraph("<b>Solving Strategy:</b>", self.styles["Normal"]))

        if puzzle_data["difficulty"] == "easy":
            explanation = [
                "This puzzle can be solved using basic scanning techniques:",
                "• Look for rows, columns, or 3×3 boxes with only one empty cell",
                "• Find numbers that appear 8 times in the grid - the 9th position is obvious",
                "• Use the process of elimination in each row, column, and box",
                "• No advanced techniques required - just careful observation!",
            ]
        elif puzzle_data["difficulty"] == "medium":
            explanation = [
                "This puzzle requires intermediate solving techniques:",
                "• Start with basic scanning and singles",
                "• Look for hidden singles - numbers that can only go in one cell in a unit",
                "• Use pencil marks to track candidates in empty cells",
                "• Apply box/line reduction to eliminate possibilities",
                "• Watch for naked pairs and triples to narrow down options",
            ]
        else:  # hard
            explanation = [
                "This challenging puzzle requires advanced techniques:",
                "• Begin with all basic and intermediate strategies",
                "• Look for X-Wing patterns across rows and columns",
                "• Apply Swordfish technique for complex eliminations",
                "• Use forcing chains to test possibilities",
                "• Consider coloring or other advanced logical deductions",
                "• Patience and systematic approach are essential!",
            ]

        for line in explanation:
            story.append(Paragraph(line, self.styles["Instructions"]))

        story.append(Spacer(1, 0.3 * inch))

        # Add key insight
        story.append(Paragraph("<b>Key Insight:</b>", self.styles["Normal"]))
        key_insight = self.get_puzzle_insight(puzzle_data)
        story.append(Paragraph(key_insight, self.styles["Instructions"]))

        story.append(PageBreak())

    def get_puzzle_insight(self, puzzle_data):
        """Generate a specific insight for the puzzle based on its characteristics."""
        insights = {
            "easy": [
                "Focus on the 3×3 boxes first - they often have the most clues to start with.",
                "Look for rows or columns that are almost complete - filling these gives quick wins.",
                "Start with the number that appears most frequently in the given clues.",
                "The center box often provides good starting points in easier puzzles.",
            ],
            "medium": [
                "This puzzle has a critical breakthrough in the middle rows - focus there first.",
                "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
                "The corner boxes have fewer clues but hold important constraints.",
                "Using pencil marks becomes essential for tracking multiple possibilities.",
            ],
            "hard": [
                "This puzzle requires patience - the initial clues are sparse but well-placed.",
                "Look for the unique pattern in rows 3-5 that unlocks the middle section.",
                "The breakthrough often comes from finding a hidden pair in the corner boxes.",
                "Don't rush - systematic candidate elimination is more important than speed.",
            ],
        }

        difficulty = puzzle_data.get("difficulty", "medium")
        import random

        return random.choice(insights.get(difficulty, insights["medium"]))

    def add_solutions_page(self, story, puzzle_solutions):
        """Add a page with multiple solutions."""
        # Create 2x2 grid
        if len(puzzle_solutions) <= 2:
            table_data = [[puzzle_solutions[0]] if len(puzzle_solutions) >= 1 else []]
            if len(puzzle_solutions) >= 2:
                table_data[0].append(puzzle_solutions[1])
        else:
            table_data = [
                [
                    puzzle_solutions[0],
                    puzzle_solutions[1] if len(puzzle_solutions) > 1 else [],
                ],
                [
                    puzzle_solutions[2] if len(puzzle_solutions) > 2 else [],
                    puzzle_solutions[3] if len(puzzle_solutions) > 3 else [],
                ],
            ]

        # Convert nested structure to proper table format
        formatted_data = []
        for row in table_data:
            formatted_row = []
            for cell in row:
                if cell:
                    # Create a subtable for each puzzle solution
                    subtable = Table(cell, colWidths=[2.7 * inch])
                    subtable.setStyle(
                        TableStyle(
                            [
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]
                        )
                    )
                    formatted_row.append(subtable)
                else:
                    formatted_row.append("")
            formatted_data.append(formatted_row)

        table = Table(formatted_data, colWidths=[3.5 * inch, 3.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )

        story.append(table)
        story.append(PageBreak())

    def create_marketing_page(self, story):
        """Create the final marketing/call-to-action page."""
        story.append(Paragraph("Thank You!", self.styles["SectionHeader"]))

        story.append(Spacer(1, 0.5 * inch))

        # Thank you message
        story.append(
            Paragraph(
                "We hope you enjoyed solving these Sudoku puzzles!",
                self.styles["Marketing"],
            )
        )

        story.append(Spacer(1, 0.5 * inch))

        # Series promotion
        next_volume = int(self.volume_number) + 1
        marketing_text = f"""
        <b>Continue Your Sudoku Journey!</b><br/>
        <br/>
        ✓ <b>Large Print Sudoku Masters - Volume {next_volume}</b><br/>
        {'100 Medium Sudoku Puzzles for Improving Skills' if self.volume_number == '1' else '100 Challenging Sudoku Puzzles'}<br/>
        <br/>
        ✓ <b>Large Print Crossword Masters Series</b><br/>
        Classic crossword puzzles in the same senior-friendly format<br/>
        <br/>
        ✓ <b>Coming Soon: Large Print Word Search Masters</b><br/>
        Join our email list for launch announcements!
        """

        story.append(Paragraph(marketing_text, self.styles["Normal"]))

        story.append(Spacer(1, 0.5 * inch))

        # Email list CTA
        story.append(
            Paragraph("<b>Get FREE Bonus Puzzles!</b>", self.styles["Marketing"])
        )

        story.append(
            Paragraph(
                "Visit www.CrosswordMastersPublishing.com/bonus<br/>"
                + "Sign up for our newsletter and receive:<br/>"
                + "• 5 exclusive bonus Sudoku puzzles<br/>"
                + "• Early access to new releases<br/>"
                + "• Special discounts for loyal readers",
                self.styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.5 * inch))

        # Review request
        story.append(
            Paragraph(
                "<b>Love This Book?</b><br/>"
                + "Please leave a review on Amazon!<br/>"
                + "Your feedback helps other puzzle lovers find our books.",
                self.styles["Normal"],
            )
        )

        story.append(Spacer(1, 1 * inch))

        # Publisher info
        story.append(
            Paragraph(
                f"© {datetime.now().year} Crossword Masters Publishing<br/>"
                + "Part of the Large Print Masters Series",
                self.styles["Normal"],
            )
        )

    def generate_pdf(self):
        """Generate the complete PDF book with page numbers."""
        output_file = self.output_dir / f"{self.title.replace(' ', '_')}_Interior.pdf"

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=self.page_size,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title=self.title,
            author=self.author,
        )

        # Build with numbered canvas
        story = []

        # Front matter (not numbered)
        self.create_title_page(story)
        self.create_copyright_page(story)
        self.create_instructions_page(story)

        # Puzzles (numbered)
        for i, puzzle_data in enumerate(self.puzzles):
            self.create_puzzle_page(story, puzzle_data, i + 1)

        # Solutions (numbered)
        self.create_solutions_section(story)

        # Marketing (numbered)
        self.create_marketing_page(story)

        # Build PDF with custom canvas for page numbers
        doc.build(story, canvasmaker=NumberedCanvas)

        print(f"✅ Enhanced PDF generated: {output_file}")
        print(
            f"📄 Total pages: {len(self.puzzles) + 4}"
        )  # puzzles + front matter + solutions
        return output_file


def main():
    """Main entry point for enhanced Sudoku PDF layout generator."""
    parser = argparse.ArgumentParser(
        description="Generate professional PDF layout for Sudoku puzzle books"
    )
    parser.add_argument(
        "--input", required=True, help="Input directory with puzzle images"
    )
    parser.add_argument("--output", required=True, help="Output directory for PDF")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", required=True, help="Book author")
    parser.add_argument("--subtitle", help="Book subtitle")
    parser.add_argument("--isbn", help="ISBN number")
    parser.add_argument(
        "--page-size", choices=["letter", "a4"], default="letter", help="Page size"
    )
    parser.add_argument(
        "--include-solutions", action="store_true", help="Include solutions section"
    )

    args = parser.parse_args()

    try:
        layout = EnhancedSudokuPDFLayout(
            input_dir=args.input,
            output_dir=args.output,
            title=args.title,
            author=args.author,
            subtitle=args.subtitle,
            isbn=args.isbn,
            page_size=args.page_size,
            include_solutions=args.include_solutions,
        )

        pdf_file = layout.generate_pdf()
        print(f"📚 Enhanced Sudoku PDF layout complete: {pdf_file}")
        return 0

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
