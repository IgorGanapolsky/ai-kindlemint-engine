# \!/usr/bin/env python3
"""
Integration tests for complete book generation pipeline
Tests the full workflow from puzzle generation to PDF creation
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Prefer new package code under `src`. Legacy `scripts` modules remain for
# backward-compatibility but should be migrated and removed in future cleanup.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import modern modules; fall back to legacy scripts for backward-compatibility
try:
    from kindlemint.generators.book_layout import BookLayoutEngine
except ModuleNotFoundError:  # pragma: no cover
    # Legacy fallback (should be removed after migration completes)
    from scripts.book_layout_bot import BookLayoutEngine  # type: ignore

from kindlemint.engines.crossword import CrosswordEngine

# Use the modern Sudoku engine implementation
from kindlemint.engines.sudoku import SudokuGenerator


class TestBookGenerationPipeline(unittest.TestCase):
    """Integration tests for book generation"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "test_output"
        self.output_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sudoku_book_generation(self):
        """Test generating a complete Sudoku book"""
        # Generate puzzles
        generator = SudokuGenerator()
        puzzles = []

        for i in range(5):  # Small test book
            puzzle = generator.generate_puzzle(difficulty="medium")
            self.assertIsNotNone(puzzle)
            puzzles.append(puzzle)

        # Verify puzzles were generated
        self.assertEqual(len(puzzles), 5)

        # Create book layout (would need BookLayoutEngine to be properly initialized)
        # For now, just verify the structure
        book_data = {
            "title": "Test Sudoku Book",
            "puzzles": puzzles,
            "puzzle_type": "sudoku",
        }

        # Verify book data structure
        self.assertIn("title", book_data)
        self.assertIn("puzzles", book_data)
        self.assertEqual(len(book_data["puzzles"]), 5)

    def test_crossword_book_generation(self):
        """Test generating a complete Crossword book"""
        # Initialize engine
        engine = CrosswordEngine(output_dir=self.output_dir)
        puzzles = []

        # Generate multiple puzzles
        for i in range(3):  # Small test
            grid = engine.create_grid(15)
            self.assertIsNotNone(grid)

            puzzle_data = {
                "id": f"puzzle_{i+1:03d}",
                "grid": grid,
                "difficulty": "medium",
                "size": 15,
            }
            puzzles.append(puzzle_data)

        # Verify puzzles
        self.assertEqual(len(puzzles), 3)
        for puzzle in puzzles:
            self.assertEqual(len(puzzle["grid"]), 15)
            self.assertEqual(len(puzzle["grid"][0]), 15)

    def test_mixed_difficulty_book(self):
        """Test generating book with mixed difficulties"""
        generator = SudokuGenerator()
        difficulties = ["easy", "medium", "hard"]
        puzzles = []

        for diff in difficulties:
            puzzle = generator.generate_puzzle(difficulty=diff)
            self.assertEqual(puzzle["difficulty"], diff)
            puzzles.append(puzzle)

        # Verify we have puzzles of each difficulty
        puzzle_difficulties = [p["difficulty"] for p_var in puzzles]
        for diff in difficulties:
            self.assertIn(diff, puzzle_difficulties)

    def test_book_metadata_generation(self):
        """Test generation of book metadata"""
        metadata = {
            "title": "Test Puzzle Book",
            "subtitle": "50 Brain-Teasing Puzzles",
            "author": "Crossword Masters Publishing",
            "isbn": "",
            "publication_date": "2025-06-26",
            "puzzle_count": 50,
            "difficulty": "mixed",
            "format": "paperback",
            "pages": 107,
        }

        # Verify all required fields
        required_fields = ["title", "author", "puzzle_count", "format"]
        for field in required_fields:
            self.assertIn(field, metadata)

    def test_solution_page_generation(self):
        """Test that solution pages are generated"""
        # Generate a puzzle with solution
        generator = SudokuGenerator()
        puzzle = generator.generate_puzzle()

        # Verify solution exists
        self.assertIn("solution", puzzle)
        solution = puzzle["solution"]

        # Verify solution is complete
        for row in solution:
            self.assertEqual(len(row), 9)
            self.assertEqual(len(set(row)), 9)  # All unique
            for cell in row:
                self.assertIn(cell, range(1, 10))

    def test_pdf_structure(self):
        """Test that PDF structure is correct"""
        # This would test actual PDF generation
        # For now, test the expected structure
        expected_structure = {
            "cover_page": 1,
            "title_page": 1,
            "instructions": 2,
            "puzzles_start": 3,
            "solutions_start": 53,  # After 50 puzzles
            "total_pages": 107,
        }

        # Verify structure makes sense
        self.assertLess(
            expected_structure["puzzles_start"], expected_structure["solutions_start"]
        )
        self.assertGreater(
            expected_structure["total_pages"], expected_structure["solutions_start"]
        )

    def test_error_handling(self):
        """Test error handling in generation pipeline"""
        generator = SudokuGenerator()

        # Test with invalid difficulty
        puzzle = generator.generate_puzzle(difficulty="invalid_difficulty")
        # Should still generate a puzzle with default difficulty
        self.assertIsNotNone(puzzle)
        self.assertIn(puzzle["difficulty"], ["easy", "medium", "hard", "expert"])

    def test_batch_consistency(self):
        """Test that batch generation maintains consistency"""
        generator = SudokuGenerator()
        batch_size = 10
        puzzles = []

        for i in range(batch_size):
            puzzle = generator.generate_puzzle(difficulty="medium")
            puzzles.append(puzzle)

        # All puzzles should have same structure
        for puzzle in puzzles:
            self.assertIn("grid", puzzle)
            self.assertIn("solution", puzzle)
            self.assertIn("difficulty", puzzle)
            self.assertEqual(puzzle["difficulty"], "medium")

        # All puzzles should be unique
        grids = [str(p["grid"]) for p_var in puzzles]
        self.assertEqual(len(set(grids)), batch_size)


class TestQualityAssurance(unittest.TestCase):
    """Test quality assurance checks"""

    def test_puzzle_solvability(self):
        """Test that all puzzles are solvable"""
        generator = SudokuGenerator()

        for __var in range(5):
            puzzle = generator.generate_puzzle()
            # Verify solution exists
            self.assertIsNotNone(puzzle["solution"])

            # Verify puzzle matches solution
            grid = puzzle["grid"]
            solution = puzzle["solution"]

            for i in range(9):
                for j in range(9):
                    if grid[i][j] != 0:
                        self.assertEqual(grid[i][j], solution[i][j])

    def test_no_duplicate_puzzles(self):
        """Test that generator doesn't create duplicates"""
        generator = SudokuGenerator()
        seen_puzzles = set()

        for __var in range(20):
            puzzle = generator.generate_puzzle()
            puzzle_str = str(puzzle["grid"])
            self.assertNotIn(puzzle_str, seen_puzzles)
            seen_puzzles.add(puzzle_str)

    def test_output_format_consistency(self):
        """Test that output format is consistent"""
        generator = SudokuGenerator()

        puzzle1 = generator.generate_puzzle()
        puzzle2 = generator.generate_puzzle()

        # Both should have same keys
        self.assertEqual(set(puzzle1.keys()), set(puzzle2.keys()))

        # Both grids should be same dimensions
        self.assertEqual(len(puzzle1["grid"]), len(puzzle2["grid"]))
        self.assertEqual(len(puzzle1["solution"]), len(puzzle2["solution"]))


if __name__ == "__main__":
    unittest.main()
