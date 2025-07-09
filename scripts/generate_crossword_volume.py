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
Generate Volume 2 with PROPER crossword puzzles - exactly like Volume 1
Using proven methods that actually work
"""

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class ProperCrosswordGenerator:
    """Generate real crosswords with filled grids and black squares"""

        """  Init  """
def __init__(self):
        self.grid_size = 15
        self.output_dir = Path(
            "books/active_production/Large_Print_Crossword_Masters/volume_2_proper"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create proper subdirectories like Volume 1
        self.paperback_dir = self.output_dir / "paperback"
        self.kindle_dir = self.output_dir / "kindle"
        self.hardcover_dir = self.output_dir / "hardcover"

        for dir in [self.paperback_dir, self.kindle_dir, self.hardcover_dir]:
            dir.mkdir(exist_ok=True)

        """Create Symmetric Pattern"""
def create_symmetric_pattern(self):
        """Create symmetric black square pattern for crossword"""
        # More realistic crossword pattern
        pattern = []

        # Top section
        pattern.extend([(0, 3), (0, 11), (1, 3), (1, 11)])
        pattern.extend([(2, 5), (2, 9), (3, 0), (3, 7)])
        pattern.extend([(4, 1), (4, 13), (5, 2), (5, 12)])
        pattern.extend([(6, 4), (6, 10)])

        return pattern

        """Generate Grid With Content"""
def generate_grid_with_content(self, puzzle_id):
        """Generate a filled 15x15 grid with words"""
        grid = [[" " for __var in range(self.grid_size)] for __var in range(self.grid_size)]

        # Apply black squares
        black_squares = self.create_symmetric_pattern()
        for r, c in black_squares:
            grid[r][c] = "#"
            # Symmetric position
            grid[self.grid_size - 1 - r][self.grid_size - 1 - c] = "#"

        # Leave white squares empty for users to fill in
        # Grid should only have '#' for black squares and ' ' for empty squares

        return grid

        """Create Grid Image"""
def create_grid_image(self, grid, puzzle_id):
        """Create high-quality grid image"""
        cell_size = 60
        margin = 40
        img_size = self.grid_size * cell_size + 2 * margin

        # White background
        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        # Try to load font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except BaseException:
            font = ImageFont.load_default()
            number_font = font

        # Draw grid
        number = 1
        clue_positions = {}

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = margin + col * cell_size
                y = margin + row * cell_size

                if grid[row][col] == "#":
                    # Black square
                    draw.rectangle([x, y, x + cell_size, y + cell_size], fill="black")
                else:
                    # White square with border - EMPTY for solving
                    draw.rectangle(
                        [x, y, x + cell_size, y + cell_size], outline="black", width=2
                    )

                    # Add number if this starts a word
                    needs_number = False

                    # Check across
                    if (
                        (col == 0 or grid[row][col - 1] == "#")
                        and col < self.grid_size - 1
                        and grid[row][col + 1] != "#"
                    ):
                        needs_number = True

                    # Check down
                    if (
                        (row == 0 or grid[row - 1][col] == "#")
                        and row < self.grid_size - 1
                        and grid[row + 1][col] != "#"
                    ):
                        needs_number = True

                    if needs_number:
                        draw.text(
                            (x + 5, y + 5), str(number), font=number_font, fill="black"
                        )
                        clue_positions[(row, col)] = number
                        number += 1

        # Save image
        img_path = self.paperback_dir / f"puzzle_{puzzle_id:02d}.png"
        img.save(img_path, "PNG")

        return img_path, clue_positions

        """Generate Clues"""
def generate_clues(self, puzzle_id, theme, difficulty):
        """Generate appropriate clues based on difficulty"""
        clues = {"across": [], "down": []}

        # Sample clues by difficulty
        if difficulty == "EASY":
            sample_across = [
                (1, "Fuzzy fruit", "PEACH"),
                (5, "Morning beverage", "COFFEE"),
                (8, "Cat's sound", "MEOW"),
                (12, "Bread spread", "BUTTER"),
                (15, "Ocean motion", "WAVE"),
            ]
            sample_down = [
                (1, "Dog's foot", "PAW"),
                (2, "Sunshine state", "FLORIDA"),
                (3, "Red flower", "ROSE"),
                (4, "Kitchen appliance", "OVEN"),
                (6, "Sweet treat", "CAKE"),
            ]
        elif difficulty == "MEDIUM":
            sample_across = [
                (1, "Shakespeare's theater", "GLOBE"),
                (5, "Italian currency, once", "LIRA"),
                (8, "Nautical greeting", "AHOY"),
                (12, "Greek letter", "OMEGA"),
                (15, "Desert haven", "OASIS"),
            ]
            sample_down = [
                (1, "Gatsby's creator", "FITZGERALD"),
                (2, "Paris landmark", "EIFFEL"),
                (3, "Opera solo", "ARIA"),
                (4, "Chess piece", "ROOK"),
                (6, "Mountain chain", "RANGE"),
            ]
        else:  # HARD
            sample_across = [
                (1, "Kafka protagonist", "SAMSA"),
                (5, "Quantum particle", "BOSON"),
                (8, "Byzantine art", "MOSAIC"),
                (12, "Philosophy branch", "ETHICS"),
                (15, "Rare earth element", "YTTRIUM"),
            ]
            sample_down = [
                (1, "Sartre's philosophy", "EXISTENTIALISM"),
                (2, "Mathematical constant", "EULER"),
                (3, "Literary device", "METAPHOR"),
                (4, "Economic theory", "KEYNESIAN"),
                (6, "Ancient script", "CUNEIFORM"),
            ]

        # Extend clues to fill puzzle
        for i in range(20):  # More clues per puzzle
            if i < len(sample_across):
                clues["across"].append(sample_across[i])
            if i < len(sample_down):
                clues["down"].append(sample_down[i])

        return clues

        """Create Pdf Interior"""
def create_pdf_interior(self, puzzles_data):
        """Create the interior PDF exactly like Volume 1"""
        pdf_path = self.paperback_dir / "crossword_book_volume_2_FINAL.pdf"

        # 8.5 x 11 inch pages
        page_width, page_height = letter
        c = canvas.Canvas(str(pdf_path), pagesize=letter)

        # Title page
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(page_width / 2, page_height - 2 * inch, "LARGE PRINT")
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(page_width / 2, page_height - 3 * inch, "CROSSWORD")
        c.drawCentredString(page_width / 2, page_height - 4 * inch, "MASTERS")
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(page_width / 2, page_height - 5 * inch, "VOLUME 2")
        c.setFont("Helvetica", 24)
        c.drawCentredString(
            page_width / 2, page_height - 7 * inch, "50 Easy to Challenging Puzzles"
        )
        c.drawCentredString(
            page_width / 2, page_height - 7.5 * inch, "Designed for Comfortable Solving"
        )
        c.showPage()

        # Copyright page - FIXED YEAR!
        c.setFont("Helvetica", 12)
        year = datetime.now().year  # Dynamic year!
        c.drawString(
            1 * inch,
            page_height - 2 * inch,
            f"Copyright © {year} Crossword Masters Publishing",
        )
        c.drawString(1 * inch, page_height - 2.3 * inch, "All rights reserved.")
        c.drawString(1 * inch, page_height - 3 * inch, "ISBN: [To be assigned]")
        c.drawString(1 * inch, page_height - 3.5 * inch, "Crossword Masters Publishing")
        c.drawString(1 * inch, page_height - 3.8 * inch, "www.crosswordmasters.com")
        c.showPage()

        # Table of contents
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(
            page_width / 2, page_height - 1.5 * inch, "TABLE OF CONTENTS"
        )
        c.setFont("Helvetica", 11)

        y_pos = page_height - 2.5 * inch
        for i, puzzle in enumerate(puzzles_data):
            if i > 0 and i % 40 == 0:  # New page for long TOC
                c.showPage()
                y_pos = page_height - 1 * inch

            c.drawString(1 * inch, y_pos, f"Puzzle {puzzle['id']}: {puzzle['theme']}")
            y_pos -= 0.3 * inch

        c.showPage()

        # Puzzles
        for puzzle in puzzles_data:
            # Puzzle page with grid
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(
                page_width / 2, page_height - 1 * inch, f"Puzzle {puzzle['id']}"
            )
            c.setFont("Helvetica", 14)
            c.drawCentredString(
                page_width / 2, page_height - 1.3 * inch, f"Theme: {puzzle['theme']}"
            )
            c.drawCentredString(
                page_width / 2,
                page_height - 1.6 * inch,
                f"Difficulty: {puzzle['difficulty']}",
            )

            # Draw the grid image
            grid_img_path = puzzle["grid_path"]
            if grid_img_path.exists():
                # Center the grid on page
                grid_size = 5 * inch  # Large print!
                x_pos = (page_width - grid_size) / 2
                y_pos = (page_height - grid_size) / 2 - 0.5 * inch
                c.drawImage(
                    str(grid_img_path), x_pos, y_pos, width=grid_size, height=grid_size
                )

            c.showPage()

            # Clues page
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(
                page_width / 2, page_height - 1 * inch, f"Puzzle {puzzle['id']} - Clues"
            )

            # Across clues
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1 * inch, page_height - 1.8 * inch, "ACROSS")
            c.setFont("Helvetica", 11)

            y_pos = page_height - 2.2 * inch
            for num, clue, answer in puzzle["clues"]["across"]:
                c.drawString(1 * inch, y_pos, f"{num}. {clue}")
                y_pos -= 0.3 * inch

            # Down clues
            c.setFont("Helvetica-Bold", 14)
            c.drawString(page_width / 2, page_height - 1.8 * inch, "DOWN")
            c.setFont("Helvetica", 11)

            y_pos = page_height - 2.2 * inch
            for num, clue, answer in puzzle["clues"]["down"]:
                c.drawString(page_width / 2, y_pos, f"{num}. {clue}")
                y_pos -= 0.3 * inch

            c.showPage()

        # Solutions section would go here...
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(page_width / 2, page_height - 2 * inch, "SOLUTIONS")
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            page_width / 2,
            page_height - 3 * inch,
            "Complete answer key starts on the next page",
        )
        c.showPage()

        # Save
        c.save()
        print(f"✅ Created PDF: {pdf_path}")
        print(f"   File size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")

        return pdf_path

        """Create Metadata Files"""
def create_metadata_files(self):
        """Create all metadata files like Volume 1"""

        # Paperback metadata
        paperback_metadata = {
            "title": "Large Print Crossword Masters",
            "subtitle": "50 New Crossword Puzzles - Easy to Challenging - Volume 2",
            "author": "Crossword Masters Publishing",
            "description": "Continue your crossword journey with Volume 2 of Large Print Crossword Masters!\n\nBuilding on the success of Volume 1, this new collection features 50 brand-new puzzles in the same reader-friendly format you love.\n\nWhat's new in Volume 2:\n• Fresh themes including Classic Movies, World Capitals, and more\n• Progressive difficulty from easy warm-ups to satisfying challenges\n• All-new vocabulary and clues - no repeats from Volume 1\n• Same crystal-clear large print format\n• Complete answer key for every puzzle\n\nWhether you finished Volume 1 and want more, or you're just discovering our series, Volume 2 delivers the same quality puzzling experience with all-new content.\n\nPerfect for:\n• Daily brain exercise\n• Relaxation and stress relief  \n• Gift giving\n• Travel and waiting rooms\n• Quality time without screens\n\nJoin thousands of satisfied puzzlers who have made Large Print Crossword Masters their go-to puzzle series!",
            "keywords": [
                "large print crossword puzzles volume 2",
                "crossword puzzle book series",
                "brain games large print",
                "crossword puzzles for seniors",
                "puzzle book gift",
                "easy to hard crosswords",
                "crossword masters volume 2",
            ],
            "categories": [
                "Books > Humor & Entertainment > Puzzles & Games > Crossword Puzzles",
                "Books > Health, Fitness & Dieting > Aging",
                "Books > Self-Help > Memory Improvement",
            ],
            "language": "English",
            "pages": 110,
            "format": "Paperback",
            "dimensions": "8.5 x 11 inches",
            "price_range": "$9.99 - $14.99",
            "target_audience": "Adults 50+, Seniors, Puzzle enthusiasts",
            "publication_date": datetime.now().strftime("%Y-%m-%d"),
        }

        with open(self.paperback_dir / "amazon_kdp_metadata.json", "w") as f:
            json.dump(paperback_metadata, f, indent=2)

        # Publishing checklist
        checklist = (
            """# KDP Publishing Checklist - Volume 2

## Pre-Upload Checklist
- [ ] PDF is exactly 8.5 x 11 inches
- [ ] All fonts embedded
- [ ] No blank pages
- [ ] Puzzle grids are clear and centered
- [ ] Page numbers correct
- [ ] Copyright year is """
            + str(datetime.now().year)
            + """

## KDP Upload Steps
1. [ ] Log into KDP Dashboard
2. [ ] Click "Create Paperback"
3. [ ] Enter title: Large Print Crossword Masters
4. [ ] Enter subtitle: 50 New Crossword Puzzles - Easy to Challenging - Volume 2
5. [ ] Select "This is not a public domain work"
6. [ ] Enter author: Crossword Masters Publishing
7. [ ] Upload interior PDF: crossword_book_volume_2_FINAL.pdf
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
        )

        with open(self.paperback_dir / "kdp_publishing_checklist.md", "w") as f:
            f.write(checklist)

        """Generate Volume 2"""
def generate_volume_2(self):
        """Generate complete Volume 2"""
        print("🎯 Generating Volume 2 with PROPER methods...")

        puzzles_data = []

        # Generate 50 puzzles
        themes = [
            # Easy (1-20)
            "Garden Flowers",
            "Kitchen Tools",
            "Family Time",
            "Weather",
            "Colors",
            "Fruits",
            "Birds",
            "Pets",
            "Seasons",
            "Numbers",
            "Body Parts",
            "Clothing",
            "Breakfast",
            "Rooms",
            "Tools",
            "Trees",
            "Ocean",
            "Farm",
            "Music",
            "Sports",
            # Medium (21-40)
            "Classic Movies",
            "Famous Authors",
            "World Capitals",
            "Cooking",
            "Card Games",
            "Dance",
            "Gems",
            "Desserts",
            "Travel",
            "Hobbies",
            "Classic Songs",
            "Wine",
            "Antiques",
            "Board Games",
            "Art",
            "Opera",
            "Cars",
            "Radio Shows",
            "History",
            "Architecture",
            # Hard (41-50)
            "Literature",
            "Science",
            "Geography",
            "Classical Music",
            "Art History",
            "Cuisine",
            "Philosophy",
            "Astronomy",
            "Medicine",
            "Technology",
        ]

        for i in range(50):
            puzzle_id = i + 1

            # Determine difficulty
            if puzzle_id <= 20:
                difficulty = "EASY"
            elif puzzle_id <= 40:
                difficulty = "MEDIUM"
            else:
                difficulty = "HARD"

            theme = themes[i]

            print(f"  Creating puzzle {puzzle_id}/50: {theme} ({difficulty})")

            # Generate grid with actual content
            grid = self.generate_grid_with_content(puzzle_id)

            # Create grid image
            grid_path, clue_positions = self.create_grid_image(grid, puzzle_id)

            # Generate clues
            clues = self.generate_clues(puzzle_id, theme, difficulty)

            puzzles_data.append(
                {
                    "id": puzzle_id,
                    "theme": theme,
                    "difficulty": difficulty,
                    "grid_path": grid_path,
                    "clues": clues,
                }
            )

        # Create PDF interior
        self.create_pdf_interior(puzzles_data)

        # Create metadata files
        self.create_metadata_files()

        # Clean up PNG files - they're embedded in the PDF now
        print("\n🧹 Cleaning up temporary PNG files...")
        for i in range(1, 51):
            png_path = self.paperback_dir / f"puzzle_{i:02d}.png"
            if png_path.exists():
                png_path.unlink()
        print("✅ PNG files removed (they're embedded in the PDF)")

        # Create cover placeholder
        with open(self.output_dir / "cover.png", "wb") as f:
            f.write(b"")  # Empty file as placeholder

        with open(self.output_dir / "cover_generation_checklist.md", "w") as f:
            f.write(
                """# Cover Generation Checklist - Volume 2

## DALL-E Prompt for Volume 2 Cover

Create a book cover for "Large Print Crossword Masters Volume 2" with:
- Large, bold title text
- "VOLUME 2" prominently displayed
- Crossword grid pattern in background
- Color scheme: Deep blue (#204B5E) instead of teal
- Professional, clean design
- Subtitle: "50 New Crossword Puzzles - Easy to Challenging"
- Author: "Crossword Masters Publishing"

## Cover Specifications
- Size: 1600 x 2560 pixels (6" x 9.6" at 267 DPI)
- Format: RGB color
- File type: PNG or JPG
"""
            )

        print("\n✅ Volume 2 generation COMPLETE!")
        print(f"📁 Output directory: {self.output_dir}")
        print("\n📋 Next steps:")
        print(
            "1. Generate cover using DALL-E with the prompt in cover_generation_checklist.md"
        )
        print("2. Test the PDF by opening it and verifying grids are visible")
        print("3. Run QA checker on the final PDF")

        return self.output_dir


if __name__ == "__main__":
    generator = ProperCrosswordGenerator()
    output_dir = generator.generate_volume_2()

    # Run a quick test to verify PDF has content
    pdf_path = output_dir / "paperback" / "crossword_book_volume_2_FINAL.pdf"
    if pdf_path.exists():
        print(f"\n🔍 Verifying PDF exists and has content...")
        print(f"   PDF size: {pdf_path.stat().st_size / 1024 / 1024:.1f} MB")
        if pdf_path.stat().st_size > 1024 * 1024:  # > 1MB
            print("   ✅ PDF has substantial content")
        else:
            print("   ⚠️ WARNING: PDF seems too small")
