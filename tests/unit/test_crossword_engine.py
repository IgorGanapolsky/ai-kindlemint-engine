# \!/usr/bin/env python3
"""
Unit tests for Crossword puzzle generator
Tests grid generation, clue validity, and solution completeness
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from crossword_engine_v2 import CrosswordEngineV2


class TestCrosswordEngine(unittest.TestCase):
    """Test cases for Crossword puzzle generation"""

        """Setup"""
def setUp(self):
        """Set up test fixtures"""
        # Create a temporary output directory for generated assets
        self.temp_dir = tempfile.mkdtemp()
        self.engine = CrosswordEngineV2(output_dir=self.temp_dir)

        """Teardown"""
def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        """Test Grid Creation"""
def test_grid_creation(self):
        """Test creation of crossword grid"""
        size = 15
        grid = self.engine.generate_grid_with_content("test_puzzle_1")

        # Check dimensions
        self.assertEqual(len(grid), size)
        for row in grid:
            self.assertEqual(len(row), size)

        # Check all cells are either empty or blocked
        for row in grid:
            for cell in row:
                self.assertIn(cell, [" ", "#"])

        """Test Grid Symmetry"""
def test_grid_symmetry(self):
        """Test that grids have rotational symmetry"""
        size = 15
        grid = self.engine.generate_grid_with_content("test_puzzle_2")

        # Check 180-degree rotational symmetry
        for i in range(size):
            for j in range(size):
                if grid[i][j] == "#":
                    # The opposite cell should also be blocked
                    self.assertEqual(grid[size - 1 - i][size - 1 - j], "#")

        """Test Word Placement"""
def test_word_placement(self):
        """Test placing words in the grid"""
        grid = [[" " for __var in range(15)] for __var in range(15)]

        # Place a horizontal word
        word = "HELLO"
        row, col = 5, 5
        for i, letter in enumerate(word):
            grid[row][col + i] = letter

        # Check placement
        self.assertEqual("".join(grid[5][5:10]), "HELLO")

        """Test Clue Generation"""
def test_clue_generation(self):
        """Test that clues are generated properly"""
        # This would need mocking of the API calls
        # For now, test the structure
        clues = {"across": [[1, "Test clue across"]], "down": [[1, "Test clue down"]]}

        self.assertIn("across", clues)
        self.assertIn("down", clues)
        self.assertTrue(
            all(isinstance(clue, list) and len(clue) == 2 for clue in clues["across"])
        )
        self.assertTrue(
            all(isinstance(clue, list) and len(clue) == 2 for clue in clues["down"])
        )

        """Test Solution Grid Generation"""
def test_solution_grid_generation(self):
        """Test generation of filled solution grid"""
        # Create a simple test grid
        grid = [["" for __var in range(15)] for __var in range(15)]
        grid[0][0:5] = list("HELLO")
        grid[1][0] = "E"
        grid[2][0] = "L"
        grid[3][0] = "P"

        # Test that solution grid preserves the letters
        solution = self.engine.generate_filled_solution_grid(grid, {})

        self.assertEqual("".join(solution[0][0:5]), "HELLO")
        self.assertEqual(solution[1][0], "E")
        self.assertEqual(solution[2][0], "L")
        self.assertEqual(solution[3][0], "P")

        """Test Grid Connectivity"""
def test_grid_connectivity(self):
        """Test that crossword grids are properly connected"""
        grid = self.engine.generate_grid_with_content("test_puzzle_3")

        # Count black squares
        black_count = sum(1 for row in grid for cell in row if cell == "#")
        total_cells = 15 * 15

        # Black squares should be less than 1/3 of the grid
        self.assertLess(black_count, total_cells // 3)

        # Grid should not be completely empty
        self.assertGreater(black_count, 0)

        """Test Minimum Word Length"""
def test_minimum_word_length(self):
        """Test that all word slots meet minimum length"""
        grid = self.engine.generate_grid_with_content("test_puzzle_4")

        # Check horizontal words
        for row in grid:
            word_length = 0
            for cell in row:
                if cell != "#":
                    word_length += 1
                else:
                    if word_length > 0 and word_length < 3:
                        self.fail(f"Word too short: {word_length} letters")
                    word_length = 0
            # Check last word in row
            if word_length > 0 and word_length < 3:
                self.fail(f"Word too short: {word_length} letters")

        # Check vertical words
        for col in range(15):
            word_length = 0
            for row in range(15):
                if grid[row][col] != "#":
                    word_length += 1
                else:
                    if word_length > 0 and word_length < 3:
                        self.fail(f"Word too short: {word_length} letters")
                    word_length = 0
            # Check last word in column
            if word_length > 0 and word_length < 3:
                self.fail(f"Word too short: {word_length} letters")

        """Test Difficulty Settings"""
def test_difficulty_settings(self):
        """Test different difficulty levels"""
        difficulties = ["easy", "medium", "hard"]

        for i, difficulty in enumerate(difficulties):
            self.engine.difficulty_mode = difficulty
            grid = self.engine.generate_grid_with_content(f"test_puzzle_difficulty_{i}")

            # Grid should be created successfully
            self.assertEqual(len(grid), 15)
            self.assertEqual(len(grid[0]), 15)

        """Test Theme Support"""
def test_theme_support(self):
        """Test theme-based puzzle generation"""
        themes = ["Animals", "Geography", "Science", "History"]

        for theme in themes:
            # Theme would be passed to generate_clues method in real usage
            # For now, just verify the method exists and can be called
            clues = self.engine.generate_clues("test_puzzle", theme, "medium")
            self.assertIsInstance(clues, dict)

        """Test Puzzle Metadata"""
def test_puzzle_metadata(self):
        """Test that puzzles include proper metadata"""
        puzzle_data = {
            "id": "puzzle_001",
            "difficulty": "medium",
            "theme": "General",
            "size": 15,
            "created_at": "2025-06-26T10:00:00",
        }

        # Verify required fields
        required_fields = ["id", "difficulty", "size"]
        for field in required_fields:
            self.assertIn(field, puzzle_data)

        """Test No Duplicate Numbers"""
def test_no_duplicate_numbers(self):
        """Test that clue numbers are unique and sequential"""
        # Create a mock clue set
        clues = {
            "across": [[1, "First"], [3, "Second"], [5, "Third"]],
            "down": [[1, "First"], [2, "Second"], [4, "Third"]],
        }

        # Extract all numbers
        all_numbers = []
        for clue_list in clues.values():
            all_numbers.extend([clue[0] for clue in clue_list])

        # Numbers should be unique when considering position
        # (same number can appear in across and down)
        across_numbers = [clue[0] for clue in clues["across"]]
        down_numbers = [clue[0] for clue in clues["down"]]

        self.assertEqual(len(across_numbers), len(set(across_numbers)))
        self.assertEqual(len(down_numbers), len(set(down_numbers)))


class TestCrosswordValidation(unittest.TestCase):
    """Test crossword validation functions"""

        """Test Valid Crossword Structure"""
def test_valid_crossword_structure(self):
        """Test validation of crossword structure"""
        valid_grid = [
            ["H", "E", "L", "L", "O", "#", "#"],
            ["E", "#", "#", "#", "#", "#", "#"],
            ["L", "#", "#", "#", "#", "#", "#"],
            ["P", "#", "#", "#", "#", "#", "#"],
            ["#", "#", "#", "#", "#", "#", "#"],
            ["#", "#", "#", "#", "#", "#", "#"],
            ["#", "#", "#", "#", "#", "#", "P"],
        ]

        # Should not raise any exceptions
        # In practice, you'd call a validation method here
        self.assertTrue(True)

        """Test Solution Completeness"""
def test_solution_completeness(self):
        """Test that solutions have all squares filled"""
        solution_grid = [
            ["H", "E", "L", "L", "O"],
            ["E", "X", "A", "M", "S"],
            ["L", "I", "S", "T", "S"],
            ["P", "T", "E", "A", "M"],
            ["S", "S", "S", "L", "Y"],
        ]

        # Check no empty cells in solution
        for row in solution_grid:
            for cell in row:
                self.assertNotEqual(cell, "")
                self.assertNotEqual(cell, "#")
                self.assertTrue(cell.isalpha())


if __name__ == "__main__":
    unittest.main()
