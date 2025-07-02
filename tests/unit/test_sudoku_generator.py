#!/usr/bin/env python3
"""
Unit tests for production-ready Sudoku puzzle generator
Tests puzzle validity, solvability, and difficulty levels
"""

import sys
import unittest
from pathlib import Path

from sudoku_generator import SudokuGenerator

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestSudokuGenerator(unittest.TestCase):
    """Test cases for Sudoku puzzle generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = SudokuGenerator()

    def test_generate_single_puzzle(self):
        """Test generation of a single puzzle"""
        puzzle = self.generator.generate_puzzle(difficulty="medium")

        self.assertIsNotNone(puzzle)
        self.assertIn("grid", puzzle)
        self.assertIn("solution", puzzle)
        self.assertIn("difficulty", puzzle)
        self.assertIn("clue_count", puzzle)
        self.assertEqual(puzzle["difficulty"], "medium")

    def test_puzzle_dimensions(self):
        """Test that puzzles have correct dimensions"""
        puzzle = self.generator.generate_puzzle()

        # Check grid is 9x9
        self.assertEqual(len(puzzle["grid"]), 9)
        for row in puzzle["grid"]:
            self.assertEqual(len(row), 9)

        # Check solution is 9x9
        self.assertEqual(len(puzzle["solution"]), 9)
        for row in puzzle["solution"]:
            self.assertEqual(len(row), 9)

        """Test Puzzle Validity"""


def test_puzzle_validity(self):
    """Test that generated puzzles are valid"""
    puzzle = self.generator.generate_puzzle()
    grid = puzzle["grid"]

    # Check all values are 0-9
    for row in grid:
        for cell in row:
            self.assertIn(cell, range(10))

    # Check that puzzle has empty cells
    empty_count = sum(1 for row in grid for cell in row if cell == 0)
    self.assertGreater(empty_count, 0)
    self.assertLess(empty_count, 81)  # Not completely empty

    """Test Solution Validity"""


def test_solution_validity(self):
    """Test that solutions are valid complete Sudoku grids"""
    puzzle = self.generator.generate_puzzle()
    solution = puzzle["solution"]

    # Check all values are 1-9
    for row in solution:
        for cell in row:
            self.assertIn(cell, range(1, 10))

    # Check rows have unique values
    for row in solution:
        self.assertEqual(len(set(row)), 9)

    # Check columns have unique values
    for col in range(9):
        column = [solution[row][col] for row in range(9)]
        self.assertEqual(len(set(column)), 9)

    # Check 3x3 boxes have unique values
    for box_row in range(3):
        for box_col in range(3):
            box_values = []
            for i in range(3):
                for j in range(3):
                    row = box_row * 3 + i
                    col = box_col * 3 + j
                    box_values.append(solution[row][col])
            self.assertEqual(len(set(box_values)), 9)

    """Test Puzzle Matches Solution"""


def test_puzzle_matches_solution(self):
    """Test that puzzle clues match the solution"""
    puzzle = self.generator.generate_puzzle()
    grid = puzzle["grid"]
    solution = puzzle["solution"]

    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                self.assertEqual(grid[i][j], solution[i][j])

    """Test Difficulty Levels"""


def test_difficulty_levels(self):
    """Test different difficulty levels"""
    difficulties = ["easy", "medium", "hard", "expert"]

    for difficulty in difficulties:
        puzzle = self.generator.generate_puzzle(difficulty=difficulty)
        self.assertEqual(puzzle["difficulty"], difficulty)

        # Check clue count matches expected ranges
        clue_count = puzzle["clue_count"]

        if difficulty == "easy":
            self.assertGreaterEqual(clue_count, 32)
            self.assertLessEqual(clue_count, 48)
        elif difficulty == "medium":
            self.assertGreaterEqual(clue_count, 25)
            self.assertLessEqual(clue_count, 36)
        elif difficulty == "hard":
            self.assertGreaterEqual(clue_count, 20)
            self.assertLessEqual(clue_count, 28)
        elif difficulty == "expert":
            self.assertGreaterEqual(clue_count, 17)
            self.assertLessEqual(clue_count, 26)

    """Test Unique Puzzles"""


def test_unique_puzzles(self):
    """Test that generator creates unique puzzles"""
    puzzles = []
    for __var in range(5):
        puzzle = self.generator.generate_puzzle()
        # Convert grid to tuple for comparison
        grid_tuple = tuple(tuple(row) for row in puzzle["grid"])
        self.assertNotIn(grid_tuple, puzzles)
        puzzles.append(grid_tuple)

    """Test Puzzle Has Unique Solution"""


def test_puzzle_has_unique_solution(self):
    """Test that puzzles have unique solutions"""
    for __var in range(3):  # Test multiple puzzles
        puzzle = self.generator.generate_puzzle()
        grid = puzzle["grid"]

        # Verify solution count is exactly 1
        solution_count = self.generator._count_solutions(grid, limit=2)
        self.assertEqual(solution_count, 1,
                         "Puzzle must have exactly one solution")

    """Test Minimum Clues"""


def test_minimum_clues(self):
    """Test that puzzles respect minimum clue requirement"""
    # Generate expert puzzle (hardest difficulty)
    puzzle = self.generator.generate_puzzle(difficulty="expert")
    clue_count = puzzle["clue_count"]

    # No valid Sudoku can have less than 17 clues
    self.assertGreaterEqual(clue_count, 17)

    """Test Invalid Difficulty Handling"""


def test_invalid_difficulty_handling(self):
    """Test handling of invalid difficulty parameter"""
    # Should default to medium
    puzzle = self.generator.generate_puzzle(difficulty="invalid")
    self.assertEqual(puzzle["difficulty"], "medium")

    """Test Puzzle Solvability"""


def test_puzzle_solvability(self):
    """Test that all generated puzzles are solvable"""
    difficulties = ["easy", "medium", "hard", "expert"]

    for difficulty in difficulties:
        puzzle = self.generator.generate_puzzle(difficulty=difficulty)
        grid = puzzle["grid"]
        expected_solution = puzzle["solution"]

        # Solve the puzzle
        solved = self.generator._solve_puzzle(grid)

        self.assertIsNotNone(
            solved, f"Puzzle should be solvable ({difficulty})")

        # Verify the solution matches
        for i in range(9):
            for j in range(9):
                self.assertEqual(solved[i][j], expected_solution[i][j])


class TestSudokuGeneratorHelpers(unittest.TestCase):
    """Test helper methods of SudokuGenerator"""

    """Setup"""


def setUp(self):
    """Set up test fixtures"""
    self.generator = SudokuGenerator()

    """Test Is Valid Placement"""


def test_is_valid_placement(self):
    """Test the validity checker for number placement"""
    # Create a partially filled grid
    grid = [[0] * 9 for __var in range(9)]
    grid[0][0] = 5

    # Test valid placements
    self.assertTrue(self.generator._is_valid(grid, 0, 1, 3))
    self.assertTrue(self.generator._is_valid(grid, 1, 0, 3))

    # Test invalid placements
    self.assertFalse(self.generator._is_valid(grid, 0, 1, 5))  # Same row
    self.assertFalse(self.generator._is_valid(grid, 1, 0, 5))  # Same column
    self.assertFalse(self.generator._is_valid(grid, 1, 1, 5))  # Same box

    """Test Grid Initialization"""


def test_grid_initialization(self):
    """Test grid initialization"""
    grid = self.generator._create_empty_grid()

    self.assertEqual(len(grid), 9)
    for row in grid:
        self.assertEqual(len(row), 9)
        self.assertEqual(set(row), {0})

    """Test Complete Grid Generation"""


def test_complete_grid_generation(self):
    """Test that complete grids are valid Sudoku solutions"""
    for __var in range(3):  # Test multiple times due to randomization
        grid = self.generator._generate_complete_grid()

        # Check all cells are filled
        for row in grid:
            for cell in row:
                self.assertIn(cell, range(1, 10))

        # Verify it's a valid Sudoku solution
        # Check rows
        for row in grid:
            self.assertEqual(len(set(row)), 9)

        # Check columns
        for col in range(9):
            column = [grid[row][col] for row in range(9)]
            self.assertEqual(len(set(column)), 9)

        # Check boxes
        for box_r in range(3):
            for box_c in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(grid[box_r * 3 + i][box_c * 3 + j])
                self.assertEqual(len(set(box)), 9)


class TestSudokuQualityAssurance(unittest.TestCase):
    """Quality assurance tests for production readiness"""

    """Setup"""


def setUp(self):
    """Set up test fixtures"""
    self.generator = SudokuGenerator()

    """Test Puzzle Quality"""


def test_puzzle_quality(self):
    """Test that puzzles meet quality standards"""
    puzzle = self.generator.generate_puzzle(difficulty="medium")
    grid = puzzle["grid"]

    # Check that puzzle has reasonable number of clues
    clue_count = sum(1 for row in grid for cell in row if cell != 0)
    self.assertGreaterEqual(
        clue_count, 17, "Puzzle must have at least 17 clues")
    self.assertLessEqual(
        clue_count, 81, "Puzzle must not be completely filled")

    # Check that puzzle has unique solution
    solution_count = self.generator._count_solutions(grid, limit=2)
    self.assertEqual(solution_count, 1,
                     "Puzzle must have exactly one solution")

    # Verify puzzle is solvable
    solution = self.generator._solve_puzzle(grid)
    self.assertIsNotNone(solution, "Puzzle must be solvable")

    """Test Performance"""


def test_performance(self):
    """Test that puzzle generation is reasonably fast"""
    import time

    start_time = time.time()
    puzzles = []

    # Generate 10 puzzles
    for __var in range(10):
        puzzle = self.generator.generate_puzzle()
        puzzles.append(puzzle)

    end_time = time.time()
    elapsed = end_time - start_time

    # Should generate 10 puzzles in under 5 seconds
    self.assertLess(
        elapsed, 5.0, f"Generation too slow: {elapsed:.2f}s for 10 puzzles")

    # All puzzles should be valid
    self.assertEqual(len(puzzles), 10)
    for puzzle in puzzles:
        self.assertIn("grid", puzzle)
        self.assertIn("solution", puzzle)

    """Test Difficulty Consistency"""


def test_difficulty_consistency(self):
    """Test that difficulty levels produce consistent clue counts"""
    difficulties = {
        "easy": {"min": 32, "max": 48},
        "medium": {"min": 25, "max": 36},
        "hard": {"min": 20, "max": 28},
        "expert": {"min": 17, "max": 26},
    }

    for difficulty, expected_range in difficulties.items():
        clue_counts = []

        # Generate 5 puzzles of each difficulty
        for __var in range(5):
            puzzle = self.generator.generate_puzzle(difficulty=difficulty)
            clue_counts.append(puzzle["clue_count"])

        # Check all are within expected range
        for count in clue_counts:
            self.assertGreaterEqual(
                count,
                expected_range["min"],
                f"{difficulty} puzzle has too few clues: {count}",
            )
            self.assertLessEqual(
                count,
                expected_range["max"],
                f"{difficulty} puzzle has too many clues: {count}",
            )


if __name__ == "__main__":
    unittest.main()
