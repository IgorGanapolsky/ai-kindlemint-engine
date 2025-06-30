#!/usr/bin/env python3
"""
Large Print Sudoku Generator - Market Aligned
Creates truly large print puzzle images based on bestseller analysis
"""

import json
import random
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class LargePrintSudokuGenerator:
    """Generate market-aligned large print Sudoku puzzles"""

    def __init__(self, output_dir, grid_size=9):
        self.output_dir = Path(output_dir)
        self.puzzles_dir = self.output_dir / "puzzles"
        self.metadata_dir = self.output_dir / "metadata"

        # Create directories
        self.puzzles_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        self.grid_size = grid_size

        # TRUE large print settings based on market research
        self.cell_size = 120  # Much larger cells
        self.line_width = 4  # Thicker lines for visibility
        self.font_size = 72  # TRULY large print numbers
        self.margin = 60  # Generous margins

        # Image size for one puzzle per page
        self.image_size = (
            self.grid_size * self.cell_size + 2 * self.margin,
            self.grid_size * self.cell_size + 2 * self.margin,
        )

    def generate_puzzle_image(self, puzzle_data, puzzle_id):
        """Create a truly large print puzzle image"""
        # Create white background
        img = Image.new("RGB", self.image_size, "white")
        draw = ImageDraw.Draw(img)

        # Try to use a clear, bold font
        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc", self.font_size
            )
        except OSError:
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except OSError:
                font = ImageFont.load_default()

        # Draw the grid with thick, clear lines
        self._draw_grid(draw)

        # Add numbers with true large print - make clues BOLD and prominent
        initial_grid = puzzle_data.get("initial_grid", [[0] * 9] * 9)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = initial_grid[row][col]
                if value != 0:
                    # Make clues bold and highly visible with dark black color
                    self._draw_number(
                        draw, row, col, str(value), font, color="#000000", bold=True
                    )

        # Save puzzle image
        puzzle_path = self.puzzles_dir / f"sudoku_puzzle_{puzzle_id:03d}.png"
        img.save(puzzle_path, "PNG", quality=95)

        return puzzle_path

    def generate_solution_image(self, puzzle_data, puzzle_id):
        """Create solution image with complete grid"""
        # Create white background
        img = Image.new("RGB", self.image_size, "white")
        draw = ImageDraw.Draw(img)

        # Font for solutions (slightly smaller but still large)
        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc", int(self.font_size * 0.8)
            )
        except OSError:
            try:
                font = ImageFont.truetype("arial.ttf", int(self.font_size * 0.8))
            except OSError:
                font = ImageFont.load_default()

        # Draw grid
        self._draw_grid(draw)

        # Add all numbers with clear distinction between clues and solutions
        solution_grid = puzzle_data.get("solution_grid", [[0] * 9] * 9)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = solution_grid[row][col]
                if value != 0:
                    # Show initial clues in bold black, solved numbers in lighter gray
                    initial_value = puzzle_data["initial_grid"][row][col]
                    if initial_value != 0:
                        # Original clues - bold and black
                        self._draw_number(
                            draw, row, col, str(value), font, color="#000000", bold=True
                        )
                    else:
                        # Solution numbers - lighter and regular weight
                        self._draw_number(
                            draw,
                            row,
                            col,
                            str(value),
                            font,
                            color="#888888",
                            bold=False,
                        )

        # Save solution image
        solution_path = self.puzzles_dir / f"sudoku_solution_{puzzle_id:03d}.png"
        img.save(solution_path, "PNG", quality=95)

        return solution_path

    def _draw_grid(self, draw):
        """Draw the Sudoku grid with clear, thick lines"""
        # Outer border - extra thick
        draw.rectangle(
            [
                self.margin,
                self.margin,
                self.image_size[0] - self.margin,
                self.image_size[1] - self.margin,
            ],
            outline="black",
            width=self.line_width * 2,
        )

        # Draw grid lines
        for i in range(1, self.grid_size):
            # Determine line thickness (thicker for 3x3 box borders)
            width = self.line_width * 2 if i % 3 == 0 else self.line_width

            # Vertical lines
            x = self.margin + i * self.cell_size
            draw.line(
                [(x, self.margin), (x, self.image_size[1] - self.margin)],
                fill="black",
                width=width,
            )

            # Horizontal lines
            y = self.margin + i * self.cell_size
            draw.line(
                [(self.margin, y), (self.image_size[0] - self.margin, y)],
                fill="black",
                width=width,
            )

    def _draw_number(self, draw, row, col, number, font, color="black", bold=False):
        """Draw a number in a cell with perfect centering and optional bold effect"""
        # Calculate cell center
        x = self.margin + col * self.cell_size + self.cell_size // 2
        y = self.margin + row * self.cell_size + self.cell_size // 2

        # Get text bounds for perfect centering
        bbox = draw.textbbox((0, 0), number, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate text position
        text_x = x - text_width // 2
        text_y = y - text_height // 2

        if bold:
            # Create bold effect by drawing text multiple times with slight offsets
            # This makes clues much more prominent and visible
            offsets = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]
            for dx, dy in offsets:
                draw.text((text_x + dx, text_y + dy), number, fill=color, font=font)

        # Draw the main number
        draw.text((text_x, text_y), number, fill=color, font=font)

    def generate_sudoku_puzzle(self, difficulty="medium"):
        """Generate a Sudoku puzzle with the specified difficulty"""
        # Generate a complete valid Sudoku grid
        solution = self._generate_complete_grid()

        # Remove numbers based on difficulty - optimized for customer satisfaction
        clue_counts = {
            "easy": random.randint(42, 46),  # Much more accessible for seniors
            "medium": random.randint(32, 38),  # Balanced challenge
            "hard": random.randint(26, 31),  # Still challenging but solvable
        }

        clue_count = clue_counts.get(difficulty, 32)
        initial_grid = self._remove_numbers(solution, clue_count)

        return {
            "initial_grid": initial_grid,
            "solution_grid": solution,
            "difficulty": difficulty,
            "clue_count": clue_count,
        }

    def _generate_complete_grid(self):
        """Generate a complete valid Sudoku grid"""
        # Start with a base valid grid and shuffle it
        base = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8],
        ]

        # Shuffle rows within each band
        for band in range(3):
            rows = list(range(band * 3, band * 3 + 3))
            random.shuffle(rows)
            for i, row in enumerate(rows):
                if i != row % 3:
                    base[band * 3 + i], base[row] = base[row], base[band * 3 + i]

        # Shuffle columns within each stack
        base = list(zip(*base))  # Transpose
        for stack in range(3):
            cols = list(range(stack * 3, stack * 3 + 3))
            random.shuffle(cols)
            for i, col in enumerate(cols):
                if i != col % 3:
                    base[stack * 3 + i], base[col] = base[col], base[stack * 3 + i]
        base = list(zip(*base))  # Transpose back

        # Convert back to list of lists
        return [list(row) for row in base]

    def _remove_numbers(self, solution, clue_count):
        """Remove numbers from solution to create puzzle"""
        puzzle = [row[:] for row in solution]
        cells_to_remove = 81 - clue_count

        # Get all cell positions
        positions = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(positions)

        # Remove numbers
        for i in range(cells_to_remove):
            row, col = positions[i]
            puzzle[row][col] = 0

        return puzzle

    def generate_batch(self, count, difficulty="medium"):
        """Generate a batch of puzzles with metadata"""
        puzzles_metadata = []

        print(f"🔢 Generating {count} large print Sudoku puzzles...")

        for i in range(count):
            puzzle_id = i + 1
            print(f"  Creating puzzle {puzzle_id}/{count} ({difficulty})...")

            # Generate puzzle data
            puzzle_data = self.generate_sudoku_puzzle(difficulty)
            puzzle_data["id"] = puzzle_id
            puzzle_data["generated_at"] = datetime.now().isoformat()

            # Generate images
            self.generate_puzzle_image(puzzle_data, puzzle_id)
            self.generate_solution_image(puzzle_data, puzzle_id)

            # Save metadata
            metadata_file = self.metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"
            with open(metadata_file, "w") as f:
                json.dump(puzzle_data, f, indent=2)

            puzzles_metadata.append(puzzle_id)

        # Save collection metadata
        collection_data = {
            "puzzle_count": count,
            "difficulty_mode": difficulty,
            "grid_size": self.grid_size,
            "generation_date": datetime.now().isoformat(),
            "puzzles": puzzles_metadata,
            "features": {
                "true_large_print": True,
                "cell_size": self.cell_size,
                "font_size": self.font_size,
                "one_per_page": True,
            },
        }

        collection_file = self.metadata_dir / "sudoku_collection.json"
        with open(collection_file, "w") as f:
            json.dump(collection_data, f, indent=2)

        print(f"✅ Generated {count} TRUE large print Sudoku puzzles")
        print(f"📁 Output directory: {self.output_dir}")

        return puzzles_metadata


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate truly large print Sudoku puzzles"
    )
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--count", type=int, default=100, help="Number of puzzles")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Puzzle difficulty",
    )

    args = parser.parse_args()

    generator = LargePrintSudokuGenerator(args.output)
    generator.generate_batch(args.count, args.difficulty)


if __name__ == "__main__":
    main()
