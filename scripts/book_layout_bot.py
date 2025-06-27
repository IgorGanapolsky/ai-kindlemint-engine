#!/usr/bin/env python3
"""
Book Layout Bot - PDF Interior Generator
Creates professional PDF interiors from puzzle data for KDP publishing
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph, Table, TableStyle
except ImportError:
    print("❌ Required dependencies missing. Run: pip install reportlab pillow")
    sys.exit(1)


class BookLayoutBot:
    """Creates professional PDF interiors for puzzle books"""

    def __init__(
        self,
        input_dir,
        output_dir,
        title,
        author,
        subtitle=None,
        page_size="letter",
        font_size=14,
        include_solutions=True,
    ):
        """Initialize the book layout generator"""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.title = title
        self.subtitle = subtitle or "50 Puzzles for Relaxation"
        self.author = author
        self.include_solutions = include_solutions

        # Set page size
        if page_size.lower() == "letter":
            self.page_size = letter
        elif page_size.lower() == "a4":
            self.page_size = A4
        else:
            print(f"⚠️ Unknown page size '{page_size}', defaulting to letter")
            self.page_size = letter

        self.page_width, self.page_height = self.page_size

        # Set font sizes
        self.title_font_size = int(font_size * 2.5)
        self.subtitle_font_size = int(font_size * 1.5)
        self.heading_font_size = int(font_size * 1.2)
        self.body_font_size = int(font_size)
        self.small_font_size = int(font_size * 0.8)

        # Initialize page counter
        self.current_page = 0

        # Load puzzle data
        self.puzzles_data = self._load_puzzle_data()

    def _load_puzzle_data(self):
        """Load puzzle data from input directory"""
        puzzles_data = []

        # Check for metadata directory first
        metadata_dir = self.input_dir / "metadata"
        if metadata_dir.exists() and metadata_dir.is_dir():
            # Load collection metadata if available
            collection_file = metadata_dir / "collection.json"
            if collection_file.exists():
                with open(collection_file, "r") as f:
                    collection = json.load(f)
                    print(
                        f"📊 Found collection metadata: {collection.get('puzzle_count', 0)} puzzles"
                    )

            # Load individual puzzle metadata
            puzzle_files = list(metadata_dir.glob("puzzle_*.json"))
            puzzle_files.sort(
                key=lambda p: int(re.search(r"puzzle_(\d+)", p.name).group(1))
            )

            for puzzle_file in puzzle_files:
                with open(puzzle_file, "r") as f:
                    puzzle_data = json.load(f)
                    puzzles_data.append(puzzle_data)

            print(f"📊 Loaded {len(puzzles_data)} puzzles from metadata")

        else:
            # Fallback: Look for puzzle images directly
            puzzle_images = list(self.input_dir.glob("puzzle_*.png"))
            puzzle_images.sort(
                key=lambda p: int(re.search(r"puzzle_(\d+)", p.name).group(1))
            )

            if not puzzle_images:
                # Try puzzles subdirectory
                puzzles_dir = self.input_dir / "puzzles"
                if puzzles_dir.exists():
                    puzzle_images = list(puzzles_dir.glob("puzzle_*.png"))
                    puzzle_images.sort(
                        key=lambda p: int(re.search(r"puzzle_(\d+)", p.name).group(1))
                    )

            if puzzle_images:
                print(f"🖼️ Found {len(puzzle_images)} puzzle images")

                # Create basic metadata for each puzzle
                for i, img_path in enumerate(puzzle_images):
                    puzzle_id = i + 1
                    difficulty = (
                        "EASY"
                        if puzzle_id <= 20
                        else "MEDIUM" if puzzle_id <= 40 else "HARD"
                    )
                    theme = f"Puzzle Theme {puzzle_id}"

                    puzzles_data.append(
                        {
                            "id": puzzle_id,
                            "theme": theme,
                            "difficulty": difficulty,
                            "grid_path": str(img_path),
                            "clues": {
                                "across": [(1, "Sample across clue", "ANSWER")],
                                "down": [(2, "Sample down clue", "ANSWER")],
                            },
                        }
                    )
            else:
                print("❌ No puzzle data found in input directory")
                sys.exit(1)

        return puzzles_data

    def create_pdf_interior(self):
        """Create the complete PDF interior"""
        print(f"📝 Creating PDF interior for '{self.title}'")

        # Determine output PDF path
        series_name = re.sub(r"[^\w\s-]", "", self.title).strip().replace(" ", "_")
        pdf_filename = f"{series_name}_interior_FINAL.pdf"
        pdf_path = self.output_dir / pdf_filename

        # Create PDF canvas
        c = canvas.Canvas(str(pdf_path), pagesize=self.page_size)

        # Generate front matter
        self._create_title_page(c)
        self._create_copyright_page(c)
        self._create_table_of_contents(c)

        # Generate puzzles
        self._create_puzzle_pages(c)

        # Generate solutions if requested
        if self.include_solutions:
            self._create_solutions_section(c)

        # Save the PDF
        c.save()

        print(f"✅ Created PDF interior: {pdf_path}")
        print(f"   File size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")

        # Create metadata files
        self._create_metadata_files(pdf_path)

        return pdf_path

    def _create_title_page(self, c):
        """Create the title page"""
        self.current_page += 1

        # Title
        c.setFont("Helvetica-Bold", self.title_font_size)
        title_parts = self.title.split()
        if len(title_parts) > 3:
            # Split long title into multiple lines
            mid_point = len(title_parts) // 2
            title_line1 = " ".join(title_parts[:mid_point])
            title_line2 = " ".join(title_parts[mid_point:])
            c.drawCentredString(
                self.page_width / 2, self.page_height - 3 * inch, title_line1
            )
            c.drawCentredString(
                self.page_width / 2, self.page_height - 4 * inch, title_line2
            )
        else:
            c.drawCentredString(
                self.page_width / 2, self.page_height - 3.5 * inch, self.title
            )

        # Subtitle
        c.setFont("Helvetica", self.subtitle_font_size)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 5 * inch, self.subtitle
        )

        # Author
        c.setFont("Helvetica", self.heading_font_size)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 6.5 * inch, f"By {self.author}"
        )

        # Page number (not visible on title page)
        c.showPage()

    def _create_copyright_page(self, c):
        """Create the copyright page"""
        self.current_page += 1

        c.setFont("Helvetica", self.body_font_size)
        year = datetime.now().year
        c.drawString(
            1 * inch, self.page_height - 2 * inch, f"Copyright © {year} {self.author}"
        )
        c.drawString(1 * inch, self.page_height - 2.3 * inch, "All rights reserved.")
        c.drawString(1 * inch, self.page_height - 3 * inch, "ISBN: [To be assigned]")
        c.drawString(1 * inch, self.page_height - 3.5 * inch, self.author)

        # Legal text
        legal_text = (
            "No part of this publication may be reproduced, distributed, or transmitted "
            "in any form or by any means, including photocopying, recording, or other "
            "electronic or mechanical methods, without the prior written permission of "
            "the publisher, except in the case of brief quotations embodied in critical "
            "reviews and certain other noncommercial uses permitted by copyright law."
        )

        text_obj = c.beginText(1 * inch, self.page_height - 5 * inch)
        text_obj.setFont("Helvetica", self.small_font_size)

        # Wrap text
        words = legal_text.split()
        line = ""
        for word in words:
            test_line = line + " " + word if line else word
            if c.stringWidth(test_line, "Helvetica", self.small_font_size) < 6 * inch:
                line = test_line
            else:
                text_obj.textLine(line)
                line = word
        if line:
            text_obj.textLine(line)

        c.drawText(text_obj)

        # Page number (not visible on copyright page)
        c.showPage()

    def _create_table_of_contents(self, c):
        """Create the table of contents"""
        self.current_page += 1

        c.setFont("Helvetica-Bold", self.heading_font_size * 1.2)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 1.5 * inch, "TABLE OF CONTENTS"
        )
        c.setFont("Helvetica", self.body_font_size)

        y_pos = self.page_height - 2.5 * inch
        items_per_page = 40

        # Add introduction entry
        c.drawString(1 * inch, y_pos, "Introduction")
        c.drawString(6 * inch, y_pos, str(self.current_page + 1))  # Next page
        y_pos -= 0.3 * inch

        # Add puzzles to TOC
        for i, puzzle in enumerate(self.puzzles_data):
            if i > 0 and i % items_per_page == 0:
                # Start a new page for long TOC
                c.showPage()
                self.current_page += 1
                y_pos = self.page_height - 1 * inch

            puzzle_id = puzzle.get("id", i + 1)
            theme = puzzle.get("theme", f"Puzzle {puzzle_id}")

            c.drawString(1 * inch, y_pos, f"Puzzle {puzzle_id}: {theme}")
            # Estimate page number (introduction + 2 pages per puzzle)
            puzzle_page = self.current_page + 1 + (i * 2)
            c.drawString(6 * inch, y_pos, str(puzzle_page))

            y_pos -= 0.3 * inch

        # Add solutions section to TOC
        if self.include_solutions:
            if y_pos < self.page_height - 9 * inch:
                # Start a new page if near bottom
                c.showPage()
                self.current_page += 1
                y_pos = self.page_height - 1 * inch

            c.drawString(1 * inch, y_pos, "Solutions")
            # Estimate solutions page (introduction + 2 pages per puzzle + 1)
            solutions_page = self.current_page + 1 + (len(self.puzzles_data) * 2) + 1
            c.drawString(6 * inch, y_pos, str(solutions_page))

        c.showPage()

    def _create_introduction_page(self, c):
        """Create the introduction page"""
        self.current_page += 1

        c.setFont("Helvetica-Bold", self.heading_font_size * 1.2)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 1.5 * inch, "INTRODUCTION"
        )

        intro_text = (
            f"Welcome to {self.title}!\n\n"
            "This collection features carefully crafted puzzles designed for your enjoyment. "
            "Each puzzle has been created to provide the perfect balance of challenge and fun.\n\n"
            "How to Use This Book:\n"
            "• Each puzzle has its own dedicated page with a grid and clues\n"
            "• Difficulty levels progress gradually throughout the book\n"
            "• Complete solutions are provided at the back of the book\n\n"
            "Whether you're a beginner or an experienced puzzle solver, we hope you enjoy the "
            "hours of entertainment these puzzles will provide.\n\n"
            "Happy puzzling!"
        )

        text_obj = c.beginText(1 * inch, self.page_height - 3 * inch)
        text_obj.setFont("Helvetica", self.body_font_size)

        # Split text into paragraphs and add to text object
        paragraphs = intro_text.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            if i > 0:
                text_obj.textLine("")  # Add blank line between paragraphs

            # Wrap text
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = line + " " + word if line else word
                if (
                    c.stringWidth(test_line, "Helvetica", self.body_font_size)
                    < 6 * inch
                ):
                    line = test_line
                else:
                    text_obj.textLine(line)
                    line = word
            if line:
                text_obj.textLine(line)

        c.drawText(text_obj)

        # Add page number
        c.setFont("Helvetica", self.small_font_size)
        c.drawCentredString(self.page_width / 2, 0.5 * inch, str(self.current_page))

        c.showPage()

    def _create_puzzle_pages(self, c):
        """Create pages for all puzzles"""
        # First create introduction
        self._create_introduction_page(c)

        # Then create puzzle pages
        for puzzle in self.puzzles_data:
            self._create_puzzle_page(c, puzzle)
            self._create_clues_page(c, puzzle)

    def _create_puzzle_page(self, c, puzzle):
        """Create a page with the puzzle grid"""
        self.current_page += 1

        puzzle_id = puzzle.get("id", 1)
        theme = puzzle.get("theme", f"Puzzle {puzzle_id}")
        difficulty = puzzle.get("difficulty", "MEDIUM")

        # Puzzle header
        c.setFont("Helvetica-Bold", self.heading_font_size)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 1 * inch, f"Puzzle {puzzle_id}"
        )
        c.setFont("Helvetica", self.body_font_size)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 1.3 * inch, f"Theme: {theme}"
        )
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 1.6 * inch,
            f"Difficulty: {difficulty}",
        )

        # Draw the grid image
        grid_path = puzzle.get("grid_path")
        if grid_path and Path(grid_path).exists():
            # Center the grid on page
            grid_size = 5 * inch  # Large print!
            x_pos = (self.page_width - grid_size) / 2
            y_pos = (self.page_height - grid_size) / 2 - 0.5 * inch
            c.drawImage(grid_path, x_pos, y_pos, width=grid_size, height=grid_size)
        else:
            # Draw placeholder if image not found
            c.setFont("Helvetica", self.body_font_size)
            c.drawCentredString(
                self.page_width / 2,
                self.page_height / 2,
                f"[Grid image not found: {grid_path}]",
            )

        # Add page number
        c.setFont("Helvetica", self.small_font_size)
        c.drawCentredString(self.page_width / 2, 0.5 * inch, str(self.current_page))

        c.showPage()

    def _create_clues_page(self, c, puzzle):
        """Create a page with the puzzle clues"""
        self.current_page += 1

        puzzle_id = puzzle.get("id", 1)

        # Clues header
        c.setFont("Helvetica-Bold", self.heading_font_size)
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 1 * inch,
            f"Puzzle {puzzle_id} - Clues",
        )

        # Get clues
        clues = puzzle.get("clues", {"across": [], "down": []})

        # Across clues
        c.setFont("Helvetica-Bold", self.heading_font_size * 0.9)
        c.drawString(1 * inch, self.page_height - 1.8 * inch, "ACROSS")
        c.setFont("Helvetica", self.body_font_size)

        y_pos = self.page_height - 2.2 * inch
        for clue_data in clues.get("across", []):
            if isinstance(clue_data, (list, tuple)) and len(clue_data) >= 2:
                num, clue = clue_data[0], clue_data[1]
                c.drawString(1 * inch, y_pos, f"{num}. {clue}")
                y_pos -= 0.3 * inch

                # Check if we need to continue to next column
                if y_pos < 1 * inch:
                    y_pos = self.page_height - 2.2 * inch

        # Down clues
        c.setFont("Helvetica-Bold", self.heading_font_size * 0.9)
        c.drawString(4 * inch, self.page_height - 1.8 * inch, "DOWN")
        c.setFont("Helvetica", self.body_font_size)

        y_pos = self.page_height - 2.2 * inch
        for clue_data in clues.get("down", []):
            if isinstance(clue_data, (list, tuple)) and len(clue_data) >= 2:
                num, clue = clue_data[0], clue_data[1]
                c.drawString(4 * inch, y_pos, f"{num}. {clue}")
                y_pos -= 0.3 * inch

                # Check if we need to continue to next column
                if y_pos < 1 * inch:
                    y_pos = self.page_height - 2.2 * inch

        # Add page number
        c.setFont("Helvetica", self.small_font_size)
        c.drawCentredString(self.page_width / 2, 0.5 * inch, str(self.current_page))

        c.showPage()

    def _create_solutions_section(self, c):
        """Create the solutions section"""
        # Solutions title page
        self.current_page += 1
        c.setFont("Helvetica-Bold", self.heading_font_size * 1.5)
        c.drawCentredString(
            self.page_width / 2, self.page_height - 3 * inch, "SOLUTIONS"
        )
        c.setFont("Helvetica", self.body_font_size)
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 4 * inch,
            "Complete answer key for all puzzles",
        )

        # Add page number
        c.setFont("Helvetica", self.small_font_size)
        c.drawCentredString(self.page_width / 2, 0.5 * inch, str(self.current_page))

        c.showPage()

        # Solutions pages
        for puzzle in self.puzzles_data:
            self._create_solution_page(c, puzzle)

    def _create_solution_page(self, c, puzzle):
        """Create a solution page for a puzzle"""
        self.current_page += 1

        puzzle_id = puzzle.get("id", 1)

        # Solution header
        c.setFont("Helvetica-Bold", self.heading_font_size)
        c.drawCentredString(
            self.page_width / 2,
            self.page_height - 1 * inch,
            f"Solution for Puzzle {puzzle_id}",
        )

        # Get clues with answers
        clues = puzzle.get("clues", {"across": [], "down": []})

        # Across answers
        c.setFont("Helvetica-Bold", self.heading_font_size * 0.9)
        c.drawString(1 * inch, self.page_height - 2 * inch, "ACROSS ANSWERS:")
        c.setFont("Helvetica", self.body_font_size)

        y_pos = self.page_height - 2.4 * inch
        for clue_data in clues.get("across", []):
            if isinstance(clue_data, (list, tuple)) and len(clue_data) >= 3:
                num, clue, answer = clue_data[0], clue_data[1], clue_data[2]
                c.drawString(1 * inch, y_pos, f"{num}. {answer} - {clue}")
                y_pos -= 0.3 * inch

                # Check if we need to continue to next column
                if y_pos < 1 * inch:
                    y_pos = self.page_height - 2.4 * inch

        # Down answers
        c.setFont("Helvetica-Bold", self.heading_font_size * 0.9)
        c.drawString(4 * inch, self.page_height - 2 * inch, "DOWN ANSWERS:")
        c.setFont("Helvetica", self.body_font_size)

        y_pos = self.page_height - 2.4 * inch
        for clue_data in clues.get("down", []):
            if isinstance(clue_data, (list, tuple)) and len(clue_data) >= 3:
                num, clue, answer = clue_data[0], clue_data[1], clue_data[2]
                c.drawString(4 * inch, y_pos, f"{num}. {answer} - {clue}")
                y_pos -= 0.3 * inch

                # Check if we need to continue to next column
                if y_pos < 1 * inch:
                    y_pos = self.page_height - 2.4 * inch

        # Add page number
        c.setFont("Helvetica", self.small_font_size)
        c.drawCentredString(self.page_width / 2, 0.5 * inch, str(self.current_page))

        c.showPage()

    def _create_metadata_files(self, pdf_path):
        """Create metadata files for KDP publishing"""
        # Create KDP metadata
        metadata = {
            "title": self.title,
            "subtitle": self.subtitle,
            "author": self.author,
            "description": f"A collection of {len(self.puzzles_data)} puzzles for relaxation and enjoyment.",
            "keywords": [
                "puzzle book",
                "crossword puzzles",
                "large print",
                "brain games",
                "puzzle collection",
            ],
            "categories": ["Games & Puzzles > Crossword Puzzles", "Activity Books"],
            "language": "English",
            "pages": self.current_page,
            "format": "Paperback",
            "dimensions": "8.5 x 11 inches",
            "price_range": "$9.99 - $14.99",
            "target_audience": "Adults, Seniors, Puzzle enthusiasts",
            "publication_date": datetime.now().strftime("%Y-%m-%d"),
        }

        metadata_file = self.output_dir / "amazon_kdp_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create Excel import template (placeholder)
        excel_file = self.output_dir / "kdp_import.xlsx"
        with open(excel_file, "w") as f:
            f.write("# KDP Import Template - Replace with actual Excel file")

        # Create publishing checklist
        checklist = f"""# KDP Publishing Checklist

## Pre-Upload Checklist
- [ ] PDF is exactly 8.5 x 11 inches
- [ ] All fonts embedded
- [ ] No blank pages
- [ ] Puzzle grids are clear and centered
- [ ] Page numbers correct
- [ ] Copyright year is {datetime.now().year}

## KDP Upload Steps
1. [ ] Log into KDP Dashboard
2. [ ] Click "Create Paperback"
3. [ ] Enter title: {self.title}
4. [ ] Enter subtitle: {self.subtitle}
5. [ ] Select "This is not a public domain work"
6. [ ] Enter author: {self.author}
7. [ ] Upload interior PDF: {pdf_path.name}
8. [ ] Upload cover: [Use cover generator]
9. [ ] Select categories (3 maximum)
10. [ ] Set price: $9.99
11. [ ] Submit for review

## Post-Upload
- [ ] Order author proof copy
- [ ] Review printed version
- [ ] Make any necessary corrections
- [ ] Approve for publication
"""

        checklist_file = self.output_dir / "kdp_publishing_checklist.md"
        with open(checklist_file, "w") as f:
            f.write(checklist)

        print(f"📄 Created metadata files in {self.output_dir}")


def main():
    """Main entry point for book layout bot"""
    parser = argparse.ArgumentParser(
        description="Book Layout Bot - PDF Interior Generator"
    )
    parser.add_argument(
        "--input", required=True, help="Input directory with puzzle data"
    )
    parser.add_argument(
        "--output", required=True, help="Output directory for PDF and metadata"
    )
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", required=True, help="Author name")
    parser.add_argument("--subtitle", help="Book subtitle")
    parser.add_argument(
        "--page-size",
        default="letter",
        choices=["letter", "a4"],
        help="Page size (letter or a4)",
    )
    parser.add_argument("--font-size", type=int, default=14, help="Base font size")
    parser.add_argument(
        "--no-solutions",
        action="store_false",
        dest="include_solutions",
        default=True,
        help="Exclude solutions section (solutions included by default)",
    )

    args = parser.parse_args()

    try:
        print("📚 BOOK LAYOUT BOT - PDF INTERIOR GENERATOR")
        print("=" * 60)
        print(f"📁 Input: {args.input}")
        print(f"📁 Output: {args.output}")
        print(f"📖 Title: {args.title}")
        print(f"✍️  Author: {args.author}")
        print("=" * 60)

        layout_bot = BookLayoutBot(
            input_dir=args.input,
            output_dir=args.output,
            title=args.title,
            author=args.author,
            subtitle=args.subtitle,
            page_size=args.page_size,
            font_size=args.font_size,
            include_solutions=args.include_solutions,
        )

        pdf_path = layout_bot.create_pdf_interior()

        print("\n🎉 BOOK LAYOUT COMPLETE")
        print(f"📄 PDF Interior: {pdf_path}")
        print(f"📊 Pages: {layout_bot.current_page}")
        print(f"📁 Metadata: {args.output}/amazon_kdp_metadata.json")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
