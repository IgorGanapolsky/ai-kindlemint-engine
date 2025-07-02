#!/usr/bin/env python3
"""
Unit tests for WordSearch puzzle generator engine
Tests grid generation with secrets module for cryptographically secure randomness
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.kindlemint.engines.wordsearch import WordSearchGenerator


class TestWordSearchGenerator(unittest.TestCase):
    """Test cases for WordSearch puzzle generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = WordSearchGenerator(
            output_dir=str(self.temp_dir),
            puzzle_count=1,
            grid_size=5,  # Small grid for testing
            words_file=None,
        )

    def tearDown(self):
        """Clean up temporary directory"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_grid_dimensions(self):
        """Test that _generate_grid produces correct dimensions"""
        grid = self.generator._generate_grid()

        # Check grid dimensions
        self.assertEqual(len(grid), self.generator.grid_size)
        for row in grid:
            self.assertEqual(len(row), self.generator.grid_size)

    def test_generate_grid_valid_letters(self):
        """Test that _generate_grid produces valid uppercase letters"""
        grid = self.generator._generate_grid()
        valid_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        # Check all cells contain valid letters
        for row in grid:
            for cell in row:
                self.assertIn(cell, valid_letters)

    def test_generate_grid_uses_secrets_choice(self):
        """Test that _generate_grid uses secrets.choice instead of random.choice"""
        with patch(
            "src.kindlemint.engines.wordsearch.secrets.choice"
        ) as mock_secrets_choice:
            # Set up mock to return predictable values
            mock_secrets_choice.return_value = "A"

            grid = self.generator._generate_grid()

            # Verify secrets.choice was called
            self.assertTrue(mock_secrets_choice.called)

            # Verify all cells are 'A' (our mocked return value)
            for row in grid:
                for cell in row:
                    self.assertEqual(cell, "A")

    def test_generate_grid_randomness(self):
        """Test that _generate_grid produces different grids on multiple calls"""
        grid1 = self.generator._generate_grid()
        grid2 = self.generator._generate_grid()

        # Convert grids to comparable format
        grid1_flat = [cell for row in grid1 for cell in row]
        grid2_flat = [cell for row in grid2 for cell in row]

        # Grids should be different (very unlikely to be identical with random generation)
        self.assertNotEqual(grid1_flat, grid2_flat)

    def test_generate_grid_different_sizes(self):
        """Test that _generate_grid works with different grid sizes"""
        test_sizes = [3, 10, 15, 20]

        for size in test_sizes:
            generator = WordSearchGenerator(
                output_dir=str(self.temp_dir), puzzle_count=1, grid_size=size
            )
            grid = generator._generate_grid()

            # Check dimensions
            self.assertEqual(len(grid), size)
            for row in grid:
                self.assertEqual(len(row), size)

    @patch("src.kindlemint.engines.wordsearch.secrets")
    def test_secrets_module_imported(self, mock_secrets):
        """Test that secrets module is imported and used"""
        # Mock secrets.choice to return 'X'
        mock_secrets.choice.return_value = "X"

        grid = self.generator._generate_grid()

        # Verify secrets.choice was called with correct alphabet
        mock_secrets.choice.assert_called_with("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        # Verify grid contains expected values
        for row in grid:
            for cell in row:
                self.assertEqual(cell, "X")

    def test_grid_contains_only_letters(self):
        """Test that grid contains only alphabetic characters"""
        grid = self.generator._generate_grid()

        for row in grid:
            for cell in row:
                self.assertTrue(cell.isalpha())
                self.assertTrue(cell.isupper())


if __name__ == "__main__":
    unittest.main()
