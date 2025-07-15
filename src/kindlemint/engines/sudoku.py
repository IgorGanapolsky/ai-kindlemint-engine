#!/usr/bin/env python3
"""
Production-Ready Sudoku Generator - Command Line Interface
Generates valid Sudoku puzzles with guaranteed unique solutions for KindleMint Engine
"""

import argparse
import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont
import secrets


class SudokuGenerator:
    """Generate valid Sudoku puzzles with configurable difficulty."""

    def __init__(
        self, output_dir=None, puzzle_count=50, difficulty="mixed", grid_size=9
    ):
        """Initialize the Sudoku generator with configuration."""
        self.grid_size = grid_size
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.puzzles_dir = self.output_dir / "puzzles"
            self.puzzles_dir.mkdir(exist_ok=True)
            self.metadata_dir = self.output_dir / "metadata"
            self.metadata_dir.mkdir(exist_ok=True)

        self.puzzle_count = puzzle_count
        self.difficulty_mode = difficulty

        # Difficulty parameters with realistic ranges for production
        # These allow for variation while maintaining unique solutions
        self.difficulty_params = {
            "easy": {"min_clues": 32, "max_clues": 48, "target_clues": 40},
            "medium": {"min_clues": 25, "max_clues": 36, "target_clues": 30},
            "hard": {"min_clues": 20, "max_clues": 28, "target_clues": 24},
            "expert": {"min_clues": 17, "max_clues": 26, "target_clues": 20},
        }

    def _create_empty_grid(self) -> List[List[int]]:
        """Create an empty 9x9 grid."""
        return [[0 for __var in range(self.grid_size)] for __var in range(self.grid_size)]

    def _is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at grid[row][col] is valid."""
        # Check row
        for x in range(9):
            if grid[row][x] == num:
                return False

        # Check column
        for x in range(9):
            if grid[x][col] == num:
                return False

        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num:
                    return False

        return True

    def _generate_complete_grid(self) -> List[List[int]]:
        """Generate a complete valid Sudoku grid using backtracking with Las Vegas randomization."""
        grid = self._create_empty_grid()

        # Fill first row with shuffled numbers 1-9 for randomization
        first_row = list(range(1, 10))
        secrets.SystemRandom().shuffle(first_row)
        grid[0] = first_row

        # Fill the rest using backtracking
        self._fill_grid(grid, 0, 0)
        return grid

    def _fill_grid(self, grid: List[List[int]], row: int, col: int) -> bool:
        """Fill grid using backtracking algorithm."""
        # Find next empty cell
        while row < 9:
            if col >= 9:
                row += 1
                col = 0
                continue
            if row >= 9:
                return True
            if grid[row][col] == 0:
                break
            col += 1

        if row >= 9:
            return True

        # Try numbers in random order (Las Vegas element)
        numbers = list(range(1, 10))
        secrets.SystemRandom().shuffle(numbers)

        for num in numbers:
            if self._is_valid(grid, row, col, num):
                grid[row][col] = num

                if self._fill_grid(grid, row, col + 1):
                    return True

                grid[row][col] = 0  # Backtrack

        return False

    def _count_solutions(self, grid: List[List[int]], limit: int = 2) -> int:
        """Count number of solutions for a puzzle (stops at limit)."""
        solutions = [0]

        def solve(row: int, col: int):
            """Solve"""
            if solutions[0] >= limit:
                return

            # Find next empty cell
            while row < 9:
                if col >= 9:
                    row += 1
                    col = 0
                    continue
                if row >= 9:
                    solutions[0] += 1
                    return
                if grid[row][col] == 0:
                    break
                col += 1

            if row >= 9:
                solutions[0] += 1
                return

            # Try each number
            for num in range(1, 10):
                if self._is_valid(grid, row, col, num):
                    grid[row][col] = num
                    solve(row, col + 1)
                    grid[row][col] = 0

                    if solutions[0] >= limit:
                        return

        solve(0, 0)
        return solutions[0]

    def _solve_puzzle(self, grid: List[List[int]]) -> Optional[List[List[int]]]:
        """Solve a Sudoku puzzle and return the solution."""
        solution = copy.deepcopy(grid)
        if self._solve_grid(solution, 0, 0):
            return solution
        return None

    def _solve_grid(self, grid: List[List[int]], row: int, col: int) -> bool:
        """Solve grid using backtracking (for getting the solution)."""
        # Find next empty cell
        while row < 9:
            if col >= 9:
                row += 1
                col = 0
                continue
            if row >= 9:
                return True
            if grid[row][col] == 0:
                break
            col += 1

        if row >= 9:
            return True

        # Try numbers in order
        for num in range(1, 10):
            if self._is_valid(grid, row, col, num):
                grid[row][col] = num

                if self._solve_grid(grid, row, col + 1):
                    return True

                grid[row][col] = 0

        return False

    def _create_puzzle_from_solution(
        self, solution: List[List[int]], difficulty: str
    ) -> List[List[int]]:
        """Create a puzzle by removing cells from complete grid while maintaining unique solution."""
        puzzle = copy.deepcopy(solution)

        # Get target number of clues for difficulty
        params = self.difficulty_params.get(
            difficulty, self.difficulty_params["medium"]
        )
        target_clues = params["target_clues"]
        min_clues = params["min_clues"]
        max_clues = params["max_clues"]

        # Create list of all cell positions
        cells = [(r, c) for r in range(9) for c in range(9)]
        secrets.SystemRandom().shuffle(cells)

        # Remove cells while maintaining unique solution
        cells_removed = 0
        current_clues = 81

        for row, col in cells:
            # Stop if we've reached target clues
            if current_clues <= target_clues:
                break

            # Never go below minimum clues
            if current_clues <= min_clues:
                break

            # Try removing this cell
            temp = puzzle[row][col]
            puzzle[row][col] = 0

            # Check if puzzle still has unique solution
            solution_count = self._count_solutions(puzzle, limit=2)

            if solution_count == 1:
                cells_removed += 1
                current_clues -= 1
            else:
                # Restore cell if multiple solutions or no solution
                puzzle[row][col] = temp

        # Ensure we're within the expected range
        final_clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        if final_clue_count > max_clues:
            # Try harder to remove more clues for expert difficulty
            additional_attempts = 0
            for row, col in cells[cells_removed:]:
                if final_clue_count <= max_clues or additional_attempts > 20:
                    break

                if puzzle[row][col] != 0:
                    temp = puzzle[row][col]
                    puzzle[row][col] = 0

                    solution_count = self._count_solutions(puzzle, limit=2)
                    if solution_count == 1:
                        final_clue_count -= 1
                    else:
                        puzzle[row][col] = temp

                    additional_attempts += 1

        # Final check to ensure no empty rows or columns
        for i in range(9):
            if all(puzzle[i][j] == 0 for j in range(9)):
                # This row is empty, so we need to add a clue back.
                # Find a cell in this row that was removed and restore it.
                for row, col in reversed(cells):
                    if row == i:
                        puzzle[row][col] = solution[row][col]
                        break

            if all(puzzle[j][i] == 0 for j in range(9)):
                # This column is empty, so we need to add a clue back.
                for row, col in reversed(cells):
                    if col == i:
                        puzzle[row][col] = solution[row][col]
                        break

        return puzzle

    def generate_puzzle(self, difficulty: str = "medium") -> Dict:
        """
        Generate a single, structurally valid Sudoku puzzle with a unique solution.
        This method will loop until a valid puzzle is created.
        """
        while True:
            if difficulty not in self.difficulty_params:
                difficulty = "medium"

            solution = self._generate_complete_grid()
            puzzle = self._create_puzzle_from_solution(solution, difficulty)

            # Perform final, definitive validation
            clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
            if clue_count < 17:  # Absolute minimum for a unique solution
                continue

            has_empty_row = any(all(cell == 0 for cell in row) for row in puzzle)
            if has_empty_row:
                continue

            has_empty_col = any(
                all(puzzle[i][j] == 0 for i in range(9)) for j in range(9)
            )
            if has_empty_col:
                continue

            # If all checks pass, we have a valid puzzle
            break

        return {
            "grid": puzzle,
            "solution": solution,
            "difficulty": difficulty,
            "clue_count": clue_count,
        }

    def create_grid_image(
        self, grid: List[List[int]], puzzle_id: int, is_solution: bool = False
    ) -> Path:
        """Create high-quality Large Print Sudoku grid image with proper clue distinction."""
        cell_size = 60
        margin = 40
        img_size = self.grid_size * cell_size + 2 * margin

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        # Load fonts with proper fallback for visual distinction
        try:
            # Bold font for clues (given numbers) - CRITICAL for visual distinction
            clue_font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica-Bold.ttc", 42
            )
        except BaseException:
            try:
                clue_font = ImageFont.truetype(
                    "/System/Library/Fonts/Arial-BoldMT.ttc", 42
                )
            except BaseException:
                try:
                    clue_font = ImageFont.truetype(
                        "/System/Library/Fonts/AppleSDGothicNeo-Bold.ttc", 42
                    )
                except BaseException:
                    clue_font = ImageFont.load_default()

        try:
            # Regular font for solutions (when is_solution=True)
            regular_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except BaseException:
            regular_font = ImageFont.load_default()

        # Draw grid lines with proper thickness for large print
        for i in range(self.grid_size + 1):
            # Major lines (3x3 box boundaries) are thicker
            line_width = 3 if i % 3 == 0 else 1

            # Vertical lines
            draw.line(
                [
                    (margin + i * cell_size, margin),
                    (margin + i * cell_size, img_size - margin),
                ],
                fill="black",
                width=line_width,
            )

            # Horizontal lines
            draw.line(
                [
                    (margin, margin + i * cell_size),
                    (img_size - margin, margin + i * cell_size),
                ],
                fill="black",
                width=line_width,
            )

        # Draw numbers with proper visual distinction between clues and empty cells
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                # Calculate cell boundaries
                cell_x1 = margin + c * cell_size
                cell_y1 = margin + r * cell_size
                cell_x2 = cell_x1 + cell_size
                cell_y2 = cell_y1 + cell_size

                value = grid[r][c]
                if value != 0:
                    # This cell has a number
                    text = str(value)

                    # CRITICAL: Choose font based on puzzle type
                    if is_solution:
                        # Solution: use regular font
                        font = regular_font
                        fill_color = "black"
                    else:
                        # Puzzle: use BOLD font for clues (visual distinction)
                        font = clue_font
                        fill_color = "black"

                    # Get text dimensions for centering
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    x = margin + c * cell_size + (cell_size - text_width) // 2
                    y = margin + r * cell_size + (cell_size - text_height) // 2

                    draw.text((x, y), text, fill=fill_color, font=font)
                else:
                    # Empty cell: add subtle background for visual distinction
                    if not is_solution:  # Only for puzzles, not solutions
                        # Light gray background to clearly show empty cells
                        draw.rectangle(
                            [cell_x1 + 2, cell_y1 + 2, cell_x2 - 2, cell_y2 - 2],
                            fill="#FAFAFA",
                        )

        # Use appropriate filename based on whether it's a solution or puzzle
        filename = (
            f"sudoku_{'solution' if is_solution else 'puzzle'}_{puzzle_id:03d}.png"
        )
        img_path = self.puzzles_dir / filename
        img.save(img_path, "PNG", dpi=(300, 300))

        return img_path

    def generate_puzzles(self) -> List[Dict]:
        """Generate the specified number of Sudoku puzzles."""
        if not self.output_dir:
            raise ValueError("Output directory must be specified for batch generation")

        print(f"🔢 SUDOKU GENERATOR - Generating {self.puzzle_count} puzzles")
        print(f"📁 Output directory: {self.puzzles_dir}")

        puzzles_data = []

        for i in range(self.puzzle_count):
            puzzle_id = i + 1

            # Determine difficulty for this puzzle
            difficulty = self._get_difficulty_for_puzzle(puzzle_id)

            print(
                f"  Creating puzzle {puzzle_id}/{self.puzzle_count} ({difficulty})..."
            )

            # Generate puzzle
            puzzle_data = self.generate_puzzle(difficulty)

            # Create grid image (puzzle with blanks)
            grid_path = self.create_grid_image(
                puzzle_data["grid"], puzzle_id, is_solution=False
            )

            # Create solution image (complete grid)
            solution_path = self.create_grid_image(
                puzzle_data["solution"], puzzle_id, is_solution=True
            )

            # Store puzzle data
            full_puzzle_data = {
                "id": puzzle_id,
                "difficulty": difficulty,
                "grid_path": str(grid_path),
                "solution_path": str(solution_path),
                "initial_grid": puzzle_data["grid"],
                "solution_grid": puzzle_data["solution"],
                "clue_count": puzzle_data["clue_count"],
            }

            # Save individual puzzle metadata
            puzzle_meta_path = self.metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"
            with open(puzzle_meta_path, "w") as f:
                json.dump(full_puzzle_data, f, indent=2)

            puzzles_data.append(full_puzzle_data)

        # Save full puzzle collection metadata
        collection_meta = {
            "puzzle_count": self.puzzle_count,
            "difficulty_mode": self.difficulty_mode,
            "grid_size": self.grid_size,
            "generation_date": datetime.now().isoformat(),
            "puzzles": [p["id"] for p_var in puzzles_data],
        }

        with open(self.metadata_dir / "sudoku_collection.json", "w") as f:
            json.dump(collection_meta, f, indent=2)

        print(f"✅ Generated {self.puzzle_count} valid Sudoku puzzles")
        print(f"📊 Metadata saved to {self.metadata_dir}")

        return puzzles_data

    def _get_difficulty_for_puzzle(self, puzzle_id: int) -> str:
        """Determine difficulty for a puzzle based on mode and ID."""
        mode = self.difficulty_mode.lower()

        if mode in ["easy", "medium", "hard", "expert"]:
            return mode
        elif mode == "mixed" or mode == "progressive":
            # Progressive difficulty distribution
            # 40% easy, 40% medium, 20% hard for general audience
            if puzzle_id <= int(self.puzzle_count * 0.4):
                return "easy"
            elif puzzle_id <= int(self.puzzle_count * 0.8):
                return "medium"
            else:
                return "hard"
        else:
            return "medium"


# Export the main class
__all__ = ["SudokuGenerator"]


def main():
    """Main entry point for Sudoku generator."""
    parser = argparse.ArgumentParser(
        description="Sudoku Generator - Generate valid Sudoku puzzles"
    )
    parser.add_argument("--output", required=True, help="Output directory for puzzles")
    parser.add_argument(
        "--count", type=int, default=100, help="Number of puzzles to generate"
    )
    parser.add_argument(
        "--difficulty",
        default="mixed",
        choices=["easy", "medium", "hard", "expert", "mixed"],
        help="Difficulty level for puzzles",
    )
    parser.add_argument(
        "--grid-size", type=int, default=9, help="Grid size (default: 9x9)"
    )

    args = parser.parse_args()

    try:
        generator = SudokuGenerator(
            output_dir=args.output,
            puzzle_count=args.count,
            difficulty=args.difficulty,
            grid_size=args.grid_size,
        )

        puzzles = generator.generate_puzzles()

        print(f"\n🎯 SUDOKU GENERATOR - SUCCESS")
        print(f"📊 Generated {len(puzzles)} valid puzzles with unique solutions")
        print(f"📁 Output directory: {args.output}")

        # Print difficulty distribution
        difficulty_counts = {}
        for puzzle in puzzles:
            diff = puzzle["difficulty"]
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

        print("\n📈 Difficulty Distribution:")
        for diff, count in sorted(difficulty_counts.items()):
            print(f"  {diff.upper()}: {count} puzzles")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
