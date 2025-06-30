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

        """  Init  """
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

        """Load Puzzle Metadata"""
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

        """Setup Styles"""
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

        """Generate Pdf"""
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

        """Create Title Page"""
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

        """Create Welcome Page"""
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

        """Create How To Play Page"""
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

        """Create Tips And Strategies Page"""
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

        """Create Cognitive Benefits Page"""
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

        """Create Puzzle Sections"""
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

        """Create Puzzle Page"""
def create_puzzle_page(self, story, puzzle_data, puzzle_number):
        """Create a single puzzle page with TRUE large print"""
        # Puzzle header
        story.append(Paragraph(f"Puzzle {puzzle_number}", self.styles["PuzzleNumber"]))
        difficulty = puzzle_data.get("difficulty", "medium").title()
        story.append(Paragraph(f"Difficulty: {difficulty}", self.styles["LargeBody"]))
        story.append(Spacer(1, 0.2 * inch))

        # Add clear instructions for customers - CRITICAL for usability
        instructions = """
        <b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column,
        and each 3×3 box contains all numbers from 1 to 9. Each number can appear
        only once in each row, column, and 3×3 box.
        """
        story.append(Paragraph(instructions.strip(), self.styles["Instructions"]))

        # Add solving tip based on difficulty
        if difficulty.lower() == "easy":
            tip = "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!"
        elif difficulty.lower() == "medium":
            tip = "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints."
        else:
            tip = "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically."

        story.append(Paragraph(tip, self.styles["LargeBody"]))
        story.append(Spacer(1, 0.3 * inch))

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

        """Create Puzzle Grid"""
def create_puzzle_grid(self, story, puzzle_data):
        """Generate puzzle grid from data when image is missing - CRITICAL FALLBACK"""
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        # Get the initial grid with clues
        initial_grid = puzzle_data.get("initial_grid", [[0] * 9] * 9)

        # Convert grid to table data - show clues as numbers, empty cells as blank
        table_data = []
        for row in initial_grid:
            table_row = []
            for cell in row:
                if cell == 0:
                    table_row.append("")  # Empty cell
                else:
                    table_row.append(str(cell))  # Clue number
            table_data.append(table_row)

        # Create table with large cells for accessibility
        table = Table(
            table_data, colWidths=[0.6 * inch] * 9, rowHeights=[0.6 * inch] * 9
        )

        # Style the table to look like a proper Sudoku grid
        table.setStyle(
            TableStyle(
                [
                    # Grid lines
                    ("GRID", (0, 0), (-1, -1), 2, colors.black),
                    ("LINEABOVE", (0, 0), (-1, -1), 2, colors.black),
                    ("LINEBELOW", (0, 0), (-1, -1), 2, colors.black),
                    ("LINEBEFORE", (0, 0), (-1, -1), 2, colors.black),
                    ("LINEAFTER", (0, 0), (-1, -1), 2, colors.black),
                    # Thick lines for 3x3 boxes
                    ("LINEABOVE", (0, 3), (-1, 3), 4, colors.black),
                    ("LINEABOVE", (0, 6), (-1, 6), 4, colors.black),
                    ("LINEBEFORE", (3, 0), (3, -1), 4, colors.black),
                    ("LINEBEFORE", (6, 0), (6, -1), 4, colors.black),
                    # Text formatting - large bold font for clues
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 24),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        # Center the table
        table.hAlign = "CENTER"
        story.append(table)

        """Create Solution Page"""
def create_solution_page(self, story, puzzle_data, puzzle_number):
        """Create solution page with step-by-step explanations as market research suggests"""
        story.append(
            Paragraph(f"Solution - Puzzle {puzzle_number}", self.styles["PuzzleNumber"])
        )
        story.append(Spacer(1, 0.3 * inch))

        # Add solving explanation based on difficulty
        difficulty = puzzle_data.get("difficulty", "medium").lower()
        solving_explanation = self.get_solving_explanation(difficulty, puzzle_number)
        story.append(Paragraph(solving_explanation, self.styles["LargeBody"]))
        story.append(Spacer(1, 0.3 * inch))

        # Solution image
        solutions_dir = self.input_dir / "puzzles" / "puzzles"
        if not solutions_dir.exists():
            solutions_dir = self.input_dir / "puzzles"

        solution_path = solutions_dir / f"sudoku_solution_{puzzle_data['id']:03d}.png"

        if solution_path.exists():
            img = Image(str(solution_path), width=4.5 * inch, height=4.5 * inch)
            img.hAlign = "CENTER"
            story.append(img)
        else:
            # Generate solution grid from data
            self.create_solution_grid(story, puzzle_data)

        # Add solving tips specific to difficulty level
        story.append(Spacer(1, 0.2 * inch))
        solving_tips = self.get_solving_tips(difficulty, puzzle_number)
        story.append(Paragraph(solving_tips, self.styles["Instructions"]))

        story.append(PageBreak())

        """Create Solution Grid"""
def create_solution_grid(self, story, puzzle_data):
        """Generate solution grid from data when image is missing - CRITICAL FALLBACK"""
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        # Get the complete solution grid
        solution_grid = puzzle_data.get("solution_grid", [[0] * 9] * 9)
        initial_grid = puzzle_data.get("initial_grid", [[0] * 9] * 9)

        # Convert grid to table data - show all numbers
        table_data = []
        for row_idx, row in enumerate(solution_grid):
            table_row = []
            for col_idx, cell in enumerate(row):
                table_row.append(str(cell) if cell != 0 else "")
            table_data.append(table_row)

        # Create table with large cells for accessibility
        table = Table(
            table_data, colWidths=[0.5 * inch] * 9, rowHeights=[0.5 * inch] * 9
        )

        # Style the table to look like a proper Sudoku solution
        table_style = [
            # Grid lines
            ("GRID", (0, 0), (-1, -1), 2, colors.black),
            ("LINEABOVE", (0, 0), (-1, -1), 2, colors.black),
            ("LINEBELOW", (0, 0), (-1, -1), 2, colors.black),
            ("LINEBEFORE", (0, 0), (-1, -1), 2, colors.black),
            ("LINEAFTER", (0, 0), (-1, -1), 2, colors.black),
            # Thick lines for 3x3 boxes
            ("LINEABOVE", (0, 3), (-1, 3), 4, colors.black),
            ("LINEABOVE", (0, 6), (-1, 6), 4, colors.black),
            ("LINEBEFORE", (3, 0), (3, -1), 4, colors.black),
            ("LINEBEFORE", (6, 0), (6, -1), 4, colors.black),
            # Text formatting - differentiate clues from solution
            ("FONTSIZE", (0, 0), (-1, -1), 20),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]

        # Make original clues bold, solution numbers lighter
        for row_idx in range(9):
            for col_idx in range(9):
                if initial_grid[row_idx][col_idx] != 0:
                    # Original clue - bold
                    table_style.append(
                        (
                            "FONTNAME",
                            (col_idx, row_idx),
                            (col_idx, row_idx),
                            "Helvetica-Bold",
                        )
                    )
                else:
                    # Solution number - regular weight, gray
                    table_style.append(
                        (
                            "FONTNAME",
                            (col_idx, row_idx),
                            (col_idx, row_idx),
                            "Helvetica",
                        )
                    )
                    table_style.append(
                        (
                            "TEXTCOLOR",
                            (col_idx, row_idx),
                            (col_idx, row_idx),
                            colors.grey,
                        )
                    )

        table.setStyle(TableStyle(table_style))

        # Center the table
        table.hAlign = "CENTER"
        story.append(table)

        """Get Solving Explanation"""
def get_solving_explanation(self, difficulty, puzzle_number):
        """Generate solving explanation based on difficulty level with much more variety"""
        explanations = {
            "easy": [
                "<b>Solving Strategy:</b> This easy puzzle can be solved using basic techniques. Start by looking for cells where only one number can fit. Scan each row, column, and 3×3 box to find obvious placements.",
                "<b>Step-by-Step Approach:</b> Begin with the most filled rows, columns, and boxes. Look for cells where 8 out of 9 numbers are already placed. Use the elimination method - if a row already has numbers 1-8, the empty cell must be 9.",
                "<b>Key Technique:</b> Focus on 'hidden singles' - cells where only one number can logically fit based on what's already in that row, column, and box. This puzzle uses fundamental Sudoku logic without requiring advanced techniques.",
                "<b>Scanning Method:</b> Look systematically through each number 1-9. For each number, check where it can legally be placed in each 3×3 box. Often you'll find only one possible location.",
                "<b>Region Analysis:</b> Start with the most constrained regions - areas with the most numbers already filled in. These provide the quickest solving opportunities and momentum.",
                "<b>Single Candidate:</b> Find cells where all but one number are eliminated by existing numbers in the same row, column, or box. These 'forced' moves are your primary solving tool.",
                "<b>Elimination Process:</b> For each empty cell, write down what numbers CAN'T go there based on the row, column, and box constraints. When only one option remains, you've found your answer.",
                "<b>Box-First Strategy:</b> Focus on completing individual 3×3 boxes before worrying about entire rows or columns. Completed boxes provide more constraints for adjacent areas.",
            ],
            "medium": [
                "<b>Solving Strategy:</b> This medium puzzle requires a combination of basic techniques and some logical deduction. You'll need to use pencil marks (candidate numbers) to track possibilities in empty cells.",
                "<b>Advanced Techniques:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers. Also use 'pointing pairs' - when a number in a box can only go in one row or column within that box.",
                "<b>Systematic Approach:</b> After filling obvious cells, make pencil marks showing all possible numbers for each empty cell. Then eliminate candidates systematically using logical rules. This builds pattern recognition skills.",
                "<b>Candidate Analysis:</b> Write small numbers in cell corners to track possibilities. When you fill a cell, immediately erase that number from all candidates in the same row, column, and box.",
                "<b>Intersection Technique:</b> When a candidate in a box is restricted to one row or column, eliminate it from the rest of that row/column outside the box. This 'pointing' technique is crucial for medium puzzles.",
                "<b>Hidden Pairs:</b> Look for two numbers that can only appear in two cells within a unit, even if those cells have other candidates. This eliminates the other candidates from those cells.",
                "<b>Multiple Constraint:</b> Focus on cells that are constrained by multiple factors - cells at intersections of nearly-complete rows, columns, and boxes often yield breakthrough moves.",
                "<b>Pattern Building:</b> As you solve, patterns emerge. Numbers often appear in diagonal lines or symmetric arrangements that can guide your next moves.",
            ],
            "hard": [
                "<b>Solving Strategy:</b> This challenging puzzle requires advanced techniques beyond basic elimination. You'll need to use multiple solving strategies in combination and think several steps ahead.",
                "<b>Expert Techniques:</b> Use 'X-Wing' patterns - when a number appears in only two rows and two columns, forming a rectangle. Also try 'Swordfish' patterns and 'coloring' techniques to track chains of logical deductions.",
                "<b>Pattern Recognition:</b> Look for complex interdependencies between cells. This puzzle may require 'what-if' analysis - temporarily assuming a number goes in a cell and following the logical chain to see if it leads to a contradiction.",
                "<b>Chain Logic:</b> Advanced puzzles often require following logical chains: if A is true, then B must be true, which forces C, etc. Track these chains carefully to avoid contradictions.",
                "<b>Forcing Networks:</b> When a cell has only two candidates, explore what happens if each is true. If one assumption leads to a contradiction or forces the same result elsewhere, you've found your answer.",
                "<b>Advanced Patterns:</b> Look for 'Swordfish' (three rows/columns with a number restricted to three positions) and 'XY-Wing' patterns that create elimination opportunities through complex logic.",
                "<b>Constraint Propagation:</b> Each move in hard puzzles creates ripple effects. Fill one cell and immediately trace all the implications before making your next move.",
                "<b>Systematic Elimination:</b> Use 'coloring' - mark candidates of the same number in different colors to spot when they form contradictory patterns that eliminate possibilities.",
            ],
        }

        explanation_list = explanations.get(difficulty, explanations["medium"])
        # Rotate explanations to provide variety
        explanation_index = (puzzle_number - 1) % len(explanation_list)
        return explanation_list[explanation_index]

        """Get Solving Tips"""
def get_solving_tips(self, difficulty, puzzle_number):
        """Generate solving tips with variety based on difficulty level and puzzle number"""
        tips = {
            "easy": [
                "<b>💡 Helpful Tip:</b> When stuck, focus on the most constrained areas first. Look for rows, columns, or boxes that are nearly complete.",
                "<b>💡 Scanning Tip:</b> Start with the number that appears most frequently in the grid. Look for where it can go in empty regions.",
                "<b>💡 Logic Tip:</b> If a row needs only 2 numbers and you have 2 empty cells, check which numbers are blocked by columns and boxes.",
                "<b>💡 Focus Tip:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 Patience Tip:</b> Easy puzzles should flow naturally. If you're stuck for more than a minute, you might have made an error - double-check your work.",
            ],
            "medium": [
                "<b>💡 Pro Tip:</b> Use pencil marks liberally! Write small numbers in corners of cells to track possibilities.",
                "<b>💡 Elimination Tip:</b> Look for 'naked pairs' - two cells in the same unit that can only contain the same two numbers.",
                "<b>💡 Pattern Tip:</b> When a number can only go in one row or column within a 3×3 box, it eliminates that number from the rest of that row/column.",
                "<b>💡 Strategy Tip:</b> If you find a cell where only one number fits, fill it in immediately and scan for new opportunities this creates.",
                "<b>💡 Progress Tip:</b> Medium puzzles require patience. Make a few moves, then re-scan the entire grid for new possibilities.",
            ],
            "hard": [
                "<b>💡 Expert Tip:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-Wing Tip:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 Advanced Tip:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 Forcing Tip:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain.",
                "<b>💡 Persistence Tip:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }

        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

        """Create About Author Page"""
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

        """Create Other Books Page"""
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

        """Create Copyright Page"""
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

        """  Init  """
def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

        """Showpage"""
def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

        """Save"""
def save(self):
        """Add page numbers to all pages"""
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 6:  # Skip numbering front matter
                self.draw_page_number()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

        """Draw Page Number"""
def draw_page_number(self):
        """Draw page number at bottom center"""
        self.setFont("Helvetica", 14)
        self.drawCentredString(
            self._pagesize[0] / 2,
            0.75 * inch,
            str(self._pageNumber - 6),  # Adjust for front matter
        )


    """Main"""
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
