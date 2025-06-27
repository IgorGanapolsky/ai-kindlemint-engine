#!/usr/bin/env python3
"""
Sudoku PDF Layout Generator for KindleMint Engine
Creates professional PDF interiors for Large Print Sudoku books
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
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


class SudokuPDFLayout:
    """Generate professional PDF layouts for Sudoku puzzle books."""

    def __init__(
        self,
        input_dir,
        output_dir,
        title,
        author,
        subtitle=None,
        page_size="letter",
        include_solutions=True,
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.title = title
        self.author = author
        self.subtitle = subtitle
        self.include_solutions = include_solutions

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

    def create_title_page(self, story):
        """Create the title page."""
        story.append(Spacer(1, 2 * inch))

        # Title
        story.append(Paragraph(self.title, self.styles["BookTitle"]))

        # Subtitle
        if self.subtitle:
            story.append(Paragraph(self.subtitle, self.styles["BookSubtitle"]))

        # Author
        story.append(Paragraph(f"by {self.author}", self.styles["BookAuthor"]))

        # Publication info
        story.append(Spacer(1, 2 * inch))
        story.append(
            Paragraph(
                f"Published {datetime.now().strftime('%Y')}<br/>© {self.author}",
                self.styles["Normal"],
            )
        )

        story.append(PageBreak())

    def create_copyright_page(self, story):
        """Create the copyright page."""
        copyright_text = f"""
        © {datetime.now().year} {self.author}. All rights reserved.
        
        No part of this book may be reproduced in any form or by any electronic or mechanical means,
        including information storage and retrieval systems, without written permission from the author,
        except for the use of brief quotations in a book review.
        
        First Edition: {datetime.now().strftime('%B %Y')}
        
        ISBN: [To be assigned]
        
        Printed in the United States of America
        """

        story.append(Paragraph(copyright_text, self.styles["Normal"]))
        story.append(PageBreak())

    def create_instructions_page(self, story):
        """Create the instructions page."""
        story.append(Paragraph("How to Solve Sudoku", self.styles["Heading1"]))
        story.append(Spacer(1, 0.5 * inch))

        instructions = [
            "Sudoku is a logic-based number puzzle. The goal is to fill the 9×9 grid so that each column, each row, and each of the nine 3×3 boxes contains the digits 1 through 9.",
            "",
            "<b>Rules:</b>",
            "• Each row must contain the numbers 1-9 with no repetition",
            "• Each column must contain the numbers 1-9 with no repetition",
            "• Each 3×3 box must contain the numbers 1-9 with no repetition",
            "",
            "<b>Tips for Beginners:</b>",
            "• Start with the easiest puzzles and work your way up",
            "• Look for rows, columns, or boxes that already have many numbers filled in",
            "• Use pencil so you can erase mistakes",
            "• Take your time and enjoy the process!",
            "",
            "<b>This Large Print Edition:</b>",
            "All puzzles in this book are printed in extra-large format for comfortable solving. Each puzzle has only one unique solution.",
        ]

        for line in instructions:
            story.append(Paragraph(line, self.styles["Instructions"]))

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
        """Create the solutions section."""
        if not self.include_solutions:
            return

        story.append(Paragraph("Solutions", self.styles["Heading1"]))
        story.append(PageBreak())

        # Add solutions in a grid layout (4 per page)
        puzzles_per_page = 4
        current_page_puzzles = []

        for i, puzzle_data in enumerate(self.puzzles):
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
                # Create solution entry
                solution_table_data = [
                    [Paragraph(f"Puzzle {i+1}", self.styles["Normal"])],
                    [Image(str(solution_path), width=2.5 * inch, height=2.5 * inch)],
                ]
                current_page_puzzles.append(solution_table_data)

                # Create page when we have 4 solutions
                if len(current_page_puzzles) == puzzles_per_page:
                    self.add_solutions_page(story, current_page_puzzles)
                    current_page_puzzles = []

        # Add remaining solutions
        if current_page_puzzles:
            self.add_solutions_page(story, current_page_puzzles)

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

    def generate_pdf(self):
        """Generate the complete PDF book."""
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

        story = []

        # Front matter
        self.create_title_page(story)
        self.create_copyright_page(story)
        self.create_instructions_page(story)

        # Puzzles
        for i, puzzle_data in enumerate(self.puzzles):
            self.create_puzzle_page(story, puzzle_data, i + 1)

        # Solutions
        self.create_solutions_section(story)

        # Build PDF
        doc.build(story)

        print(f"✅ PDF generated: {output_file}")
        return output_file


def main():
    """Main entry point for Sudoku PDF layout generator."""
    parser = argparse.ArgumentParser(
        description="Generate PDF layout for Sudoku puzzle books"
    )
    parser.add_argument(
        "--input", required=True, help="Input directory with puzzle images"
    )
    parser.add_argument("--output", required=True, help="Output directory for PDF")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", required=True, help="Book author")
    parser.add_argument("--subtitle", help="Book subtitle")
    parser.add_argument(
        "--page-size", choices=["letter", "a4"], default="letter", help="Page size"
    )
    parser.add_argument(
        "--include-solutions", action="store_true", help="Include solutions section"
    )

    args = parser.parse_args()

    try:
        layout = SudokuPDFLayout(
            input_dir=args.input,
            output_dir=args.output,
            title=args.title,
            author=args.author,
            subtitle=args.subtitle,
            page_size=args.page_size,
            include_solutions=args.include_solutions,
        )

        pdf_file = layout.generate_pdf()
        print(f"📚 Sudoku PDF layout complete: {pdf_file}")
        return 0

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
