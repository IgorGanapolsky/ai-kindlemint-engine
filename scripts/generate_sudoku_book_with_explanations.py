#!/usr/bin/env python3

    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>HOW TO SOLVE:</b> Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "<b>PUZZLE RULES:</b> Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "<b>SOLVING GOAL:</b> Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "<b>GAME RULES:</b> Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>CHALLENGE RULES:</b> Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "<b>SOLVING INSTRUCTIONS:</b> Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "<b>PUZZLE OBJECTIVE:</b> Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "<b>GAME OBJECTIVE:</b> Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>EXPERT CHALLENGE:</b> Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "<b>ADVANCED RULES:</b> Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "<b>MASTER PUZZLE:</b> Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "<b>CHALLENGE GOAL:</b> Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!",
                "<b>💡 HINT:</b> Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "<b>💡 STRATEGY:</b> Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "<b>💡 APPROACH:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 METHOD:</b> If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "<b>💡 TECHNIQUE:</b> Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "<b>💡 SHORTCUT:</b> Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "<b>💡 STRATEGY:</b> Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "<b>💡 TECHNIQUE:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "<b>💡 METHOD:</b> When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "<b>💡 APPROACH:</b> If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "<b>💡 HINT:</b> Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "<b>💡 STRATEGY:</b> Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "<b>💡 EXPERT TIP:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-WING:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 ADVANCED:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 FORCING:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "<b>💡 PATTERN:</b> Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "<b>💡 PERSISTENCE:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

"""
Enhanced Sudoku Book Generator with Solution Explanations
Generates Large Print Sudoku Masters with proper solving tips and explanations
"""

import json
import os
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
    )
except ImportError:
    print("Installing required packages...")
    os.system("pip install reportlab")
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
    )


class EnhancedSudokuBookGenerator:
    """Generate complete Sudoku book with solution explanations"""

    # Solving tips for different difficulty levels
    SOLVING_TIPS = {
        "easy": [
            "Look for rows, columns, or 3x3 boxes with only one empty cell",
            "Find numbers that appear 8 times on the grid - the 9th position is obvious",
            "Check each 3x3 box for missing numbers and see if they can only go in one cell",
        ],
        "medium": [
            "Use the 'pencil mark' technique - note possible numbers in empty cells",
            "Look for 'naked pairs' - two cells in a row/column/box that can only contain the same two numbers",
            "Apply the 'pointing pairs' technique - when a number in a box can only be in one row/column",
        ],
        "hard": [
            "Look for 'hidden singles' - numbers that can only go in one cell of a unit",
            "Use 'box-line reduction' - eliminate candidates based on box constraints",
            "Apply 'X-Wing' pattern recognition for advanced eliminations",
        ],
        "expert": [
            "Master the 'Swordfish' pattern - a complex elimination technique",
            "Use 'coloring' to track chains of related cells",
            "Apply 'forcing chains' - follow logical consequences to find contradictions",
        ],
    }

        """  Init  """
def __init__(self, volume_path: Path):
        self.volume_path = volume_path
        self.puzzles_dir = volume_path / "puzzles"
        self.output_dir = volume_path / "paperback"
        self.output_dir.mkdir(exist_ok=True)

        # Setup styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

        """Setup Custom Styles"""
def setup_custom_styles(self):
        """Setup custom paragraph styles for the book"""
        self.styles.add(
            ParagraphStyle(
                name="BookTitle",
                parent=self.styles["Title"],
                fontSize=28,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.black,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Copyright",
                parent=self.styles["Normal"],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_LEFT,
                leftIndent=0.5 * inch,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="PuzzleNumber",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.black,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SolutionExplanation",
                parent=self.styles["Normal"],
                fontSize=11,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                leftIndent=0.25 * inch,
                rightIndent=0.25 * inch,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SolvingTip",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_LEFT,
                leftIndent=0.5 * inch,
                textColor=colors.HexColor("#333333"),
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="FinalTeaser",
                parent=self.styles["Normal"],
                fontSize=12,
                spaceAfter=15,
                alignment=TA_CENTER,
                textColor=colors.black,
            )
        )

        """Create Title Page"""
def create_title_page(self, story):
        """Create the title page"""
        story.append(Spacer(1, 2 * inch))

        title = Paragraph("Large Print Sudoku Masters", self.styles["BookTitle"])
        story.append(title)
        story.append(Spacer(1, 0.5 * inch))

        subtitle = Paragraph("Volume 1", self.styles["Heading1"])
        story.append(subtitle)
        story.append(Spacer(1, 0.5 * inch))

        tagline = Paragraph(
            "100 Easy to Hard Puzzles with Complete Solution Explanations",
            self.styles["Heading2"],
        )
        story.append(tagline)
        story.append(Spacer(1, 2 * inch))

        author = Paragraph("Igor Ganapolsky", self.styles["Heading1"])
        story.append(author)
        story.append(PageBreak())

        """Create Copyright Page"""
def create_copyright_page(self, story):
        """Create the copyright page"""
        story.append(Spacer(1, 1 * inch))

        copyright_content = [
            "Large Print Sudoku Masters – Volume 1",
            "© 2025 Crossword Masters Publishing",
            "All rights reserved.",
            "",
            "No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means—electronic, mechanical, photocopy, recording, or otherwise—without prior written permission from the publisher.",
            "",
            "This book is intended for personal entertainment only.",
            "",
            "ISBN: 978-1-XXXXXXX-XX-X",
            "Published by Crossword Masters Publishing",
            "www.CrosswordMasters.com",
            "",
            "Printed in the USA",
        ]

        for line in copyright_content:
            if line:
                para = Paragraph(line, self.styles["Copyright"])
                story.append(para)
            else:
                story.append(Spacer(1, 12))

        story.append(PageBreak())

        """Create How To Play Section"""
def create_how_to_play_section(self, story):
        """Create How to Play Sudoku section"""
        story.append(Spacer(1, 0.5 * inch))

        title = Paragraph("How to Play Sudoku", self.styles["Heading1"])
        story.append(title)
        story.append(Spacer(1, 0.5 * inch))

        instructions = [
            "<b>Objective:</b> Fill the 9×9 grid so that each row, column, and 3×3 box contains the digits 1-9 exactly once.",
            "",
            "<b>Rules:</b>",
            "• Each row must contain the numbers 1-9 with no repetition",
            "• Each column must contain the numbers 1-9 with no repetition",
            "• Each 3×3 box must contain the numbers 1-9 with no repetition",
            "• Some numbers are given as clues - these cannot be changed",
            "",
            "<b>Strategy Tips:</b>",
            "• Start with the easiest puzzles to build your skills",
            "• Look for rows, columns, or boxes with the most clues",
            "• Use pencil marks to note possible numbers in empty cells",
            "• Take breaks if you get stuck - fresh eyes often spot new patterns",
            "",
            "<b>Difficulty Levels:</b>",
            "• Easy (Puzzles 1-25): Great for beginners, 35-45 clues",
            "• Medium (Puzzles 26-50): Moderate challenge, 27-34 clues",
            "• Hard (Puzzles 51-75): Advanced techniques needed, 20-26 clues",
            "• Expert (Puzzles 76-100): Maximum challenge, 17-19 clues",
        ]

        for line in instructions:
            para = Paragraph(line, self.styles["Normal"])
            story.append(para)
            story.append(Spacer(1, 8))

        story.append(PageBreak())

        """Load Puzzle Data"""
def load_puzzle_data(self):
        """Load all puzzle data from JSON files"""
        puzzles = []
        metadata_dir = self.puzzles_dir / "metadata"

        for i in range(1, 101):
            puzzle_file = metadata_dir / f"sudoku_puzzle_{i:03d}.json"
            if puzzle_file.exists():
                with open(puzzle_file, "r") as f:
                    puzzle_data = json.load(f)
                    puzzles.append(puzzle_data)

        return sorted(puzzles, key=lambda x: x.get("id", 0))

        """Add Puzzle Pages"""
def add_puzzle_pages(self, story, puzzles):
        """Add all puzzle pages to the book"""
        for i, puzzle in enumerate(puzzles, 1):
            # Puzzle number header
            puzzle_header = Paragraph(f"Puzzle #{i}", self.styles["PuzzleNumber"])
            story.append(puzzle_header)

            # Add difficulty indicator
            difficulty = puzzle.get("difficulty", "medium").title()
            diff_para = Paragraph(f"Difficulty: {difficulty}", self.styles["Normal"])
            story.append(diff_para)
            story.append(Spacer(1, 20))

            # Add puzzle image if available
            puzzle_image_path = (
                self.puzzles_dir / "puzzles" / f"sudoku_puzzle_{i:03d}.png"
            )
            if puzzle_image_path.exists():
                try:
                    img = Image(str(puzzle_image_path), width=6 * inch, height=6 * inch)
                    story.append(img)
                except Exception as e:
                    print(f"Could not load puzzle image {i}: {e}")
                    self.add_text_puzzle(story, puzzle)
            else:
                self.add_text_puzzle(story, puzzle)

            story.append(PageBreak())

        """Add Text Puzzle"""
def add_text_puzzle(self, story, puzzle):
        """Add a text-based puzzle representation"""
        if "initial_grid" in puzzle:
            grid_data = []
            for row in puzzle["initial_grid"]:
                row_data = []
                for cell in row:
                    if cell == 0:
                        row_data.append("")
                    else:
                        row_data.append(str(cell))
                grid_data.append(row_data)

            # Create table for the grid
            table = Table(
                grid_data, colWidths=[0.6 * inch] * 9, rowHeights=[0.6 * inch] * 9
            )
            table.setStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 16),
                    # Add thicker lines for 3x3 boxes
                    ("LINEBELOW", (0, 2), (-1, 2), 2, colors.black),
                    ("LINEBELOW", (0, 5), (-1, 5), 2, colors.black),
                    ("LINEAFTER", (2, 0), (2, -1), 2, colors.black),
                    ("LINEAFTER", (5, 0), (5, -1), 2, colors.black),
                ]
            )
            story.append(table)

        """Generate Solution Explanation"""
def generate_solution_explanation(self, puzzle):
        """Generate explanation for how to solve a specific puzzle"""
        difficulty = puzzle.get("difficulty", "medium").lower()
        puzzle_id = puzzle.get("id", 0)

        # Get relevant tips for this difficulty
        tips = self.SOLVING_TIPS.get(difficulty, self.SOLVING_TIPS["medium"])

        # Generate puzzle-specific observations
        explanations = []

        # Add general approach
        explanations.append(f"<b>Solving Approach for Puzzle #{puzzle_id}:</b>")
        explanations.append("")

        # Add difficulty-specific strategy
        if difficulty == "easy":
            explanations.append(
                "This easy puzzle can be solved using basic scanning techniques:"
            )
        elif difficulty == "medium":
            explanations.append("This medium puzzle requires intermediate techniques:")
        elif difficulty == "hard":
            explanations.append(
                "This challenging puzzle needs advanced solving strategies:"
            )
        else:
            explanations.append(
                "This expert puzzle requires mastery of complex techniques:"
            )

        explanations.append("")

        # Add specific tips
        explanations.append("<b>Key Solving Steps:</b>")
        for i, tip in enumerate(tips, 1):
            explanations.append(f"{i}. {tip}")

        explanations.append("")
        explanations.append("<b>Starting Points:</b>")

        # Analyze the grid for good starting points
        if "initial_grid" in puzzle:
            grid = puzzle["initial_grid"]

            # Find rows/columns/boxes with most clues
            row_counts = [sum(1 for cell in row if cell != 0) for row in grid]
            max_row = row_counts.index(max(row_counts)) + 1

            col_counts = [sum(1 for i in range(9) if grid[i][j] != 0) for j in range(9)]
            max_col = col_counts.index(max(col_counts)) + 1

            explanations.append(
                f"• Row {max_row} has {max(row_counts)} clues - good place to start"
            )
            explanations.append(
                f"• Column {max_col} has {
                    max(col_counts)} clues - check for singles here"
            )
            explanations.append("• Look for 3×3 boxes with 6 or more clues filled")

        return explanations

        """Add Solutions Section"""
def add_solutions_section(self, story, puzzles):
        """Add solutions section with explanations"""
        story.append(Spacer(1, 1 * inch))

        solutions_title = Paragraph(
            "Solutions with Solving Tips", self.styles["BookTitle"]
        )
        story.append(solutions_title)
        story.append(Spacer(1, 0.5 * inch))

        intro = Paragraph(
            "This section provides not just the answers, but also solving strategies and tips for each puzzle. "
            "Use these explanations to improve your Sudoku skills!",
            self.styles["Normal"],
        )
        story.append(intro)
        story.append(PageBreak())

        for i, puzzle in enumerate(puzzles, 1):
            # Solution header
            solution_header = Paragraph(
                f"Solution to Puzzle #{i}", self.styles["PuzzleNumber"]
            )
            story.append(solution_header)
            story.append(Spacer(1, 15))

            # Add solving explanation
            explanations = self.generate_solution_explanation(puzzle)
            for explanation in explanations:
                if explanation:
                    para = Paragraph(explanation, self.styles["SolutionExplanation"])
                    story.append(para)
                else:
                    story.append(Spacer(1, 6))

            story.append(Spacer(1, 15))

            # Add solution grid
            if "solution_grid" in puzzle:
                solution_header = Paragraph(
                    "<b>Complete Solution:</b>", self.styles["Normal"]
                )
                story.append(solution_header)
                story.append(Spacer(1, 10))

                # Create solution table
                solution_data = [
                    [str(cell) for cell in row] for row in puzzle["solution_grid"]
                ]

                table = Table(
                    solution_data,
                    colWidths=[0.5 * inch] * 9,
                    rowHeights=[0.5 * inch] * 9,
                )
                table.setStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTSIZE", (0, 0), (-1, -1), 12),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f0f0")),
                        # Add thicker lines for 3x3 boxes
                        ("LINEBELOW", (0, 2), (-1, 2), 2, colors.black),
                        ("LINEBELOW", (0, 5), (-1, 5), 2, colors.black),
                        ("LINEAFTER", (2, 0), (2, -1), 2, colors.black),
                        ("LINEAFTER", (5, 0), (5, -1), 2, colors.black),
                    ]
                )
                story.append(table)

            story.append(PageBreak())

        """Add Final Teaser Page"""
def add_final_teaser_page(self, story):
        """Add the final teaser page"""
        story.append(Spacer(1, 2 * inch))

        teaser_content = [
            "Enjoyed this puzzle book?",
            "",
            "📚 Get ready for more in the Sudoku Masters series!",
            "",
            "Volume 2 is coming soon with 100 all-new puzzles",
            "in the same easy-to-read large print format.",
            "",
            "🛒 Visit www.CrosswordMasters.com or check Amazon",
            "for our latest releases, including Crossword and Word Search books!",
            "",
            "💬 We'd love your feedback!",
            "Please leave a quick review on Amazon — it helps more puzzlers find us.",
        ]

        for line in teaser_content:
            if line:
                para = Paragraph(line, self.styles["FinalTeaser"])
                story.append(para)
                story.append(Spacer(1, 10))
            else:
                story.append(Spacer(1, 15))

        """Generate Complete Book"""
def generate_complete_book(self):
        """Generate the complete book with all elements"""
        output_file = self.output_dir / "Large_Print_Sudoku_Masters_V1_ENHANCED.pdf"

        print(f"🚀 Generating enhanced Sudoku book with explanations...")
        print(f"📁 Output: {output_file}")

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        story = []

        # 1. Title Page
        print("📄 Adding title page...")
        self.create_title_page(story)

        # 2. Copyright Page
        print("©️ Adding copyright page...")
        self.create_copyright_page(story)

        # 3. How to Play Section
        print("📖 Adding how to play section...")
        self.create_how_to_play_section(story)

        # 4. Load puzzle data
        print("🧩 Loading puzzle data...")
        puzzles = self.load_puzzle_data()
        print(f"✅ Loaded {len(puzzles)} puzzles")

        # 5. Puzzle Pages
        print("🔢 Adding puzzle pages...")
        self.add_puzzle_pages(story, puzzles)

        # 6. Solutions Section with Explanations
        print("💡 Adding solutions with explanations...")
        self.add_solutions_section(story, puzzles)

        # 7. Final Teaser Page
        print("📢 Adding final teaser page...")
        self.add_final_teaser_page(story)

        # Generate PDF
        print("📖 Building PDF...")
        doc.build(story)

        print(f"✅ SUCCESS! Enhanced book generated: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

        return output_file


    """Main"""
def main():
    """Main function to generate the enhanced book"""
    base_path = Path(__file__).parent.parent
    volume_path = (
        base_path
        / "books"
        / "active_production"
        / "Large_Print_Sudoku_Masters"
        / "volume_1"
    )

    if not volume_path.exists():
        print(f"❌ ERROR: Volume path not found: {volume_path}")
        return

    generator = EnhancedSudokuBookGenerator(volume_path)
    output_file = generator.generate_complete_book()

    print(f"\n🎉 ENHANCED BOOK COMPLETE!")
    print(f"📁 Location: {output_file}")
    print(f"✨ Now includes solving tips and explanations for every puzzle!")
    print(f"🚀 Ready for KDP upload after fixing puzzle issues!")


if __name__ == "__main__":
    main()
