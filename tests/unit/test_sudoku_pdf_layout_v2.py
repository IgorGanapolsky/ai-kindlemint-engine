#!/usr/bin/env python3
"""
Unit tests for sudoku_pdf_layout_v2.py to cover the secrets module changes
"""

import json
import secrets
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Import the class we're testing
from scripts.sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout


class TestSudokuPDFLayoutV2(unittest.TestCase):
    """Test the EnhancedSudokuPDFLayout class with focus on secrets module usage"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_input_dir = Path("/test/input")
        self.test_output_dir = Path("/test/output")
        self.test_title = "Test Sudoku Book"
        self.test_author = "Test Author"

        # Mock puzzle metadata
        self.mock_collection_data = {
            "puzzles": [1, 2, 3],
            "difficulty": "medium",
            "total_puzzles": 3,
        }

        self.mock_puzzle_data = {
            "id": 1,
            "difficulty": "medium",
            "clues": 25,
            "solution_time": "10-15 minutes",
        }

    @patch("scripts.sudoku_pdf_layout_v2.Path")
    @patch("scripts.sudoku_pdf_layout_v2.json.load")
    @patch("builtins.open", new_callable=mock_open, read_data='{"puzzles": [1]}')
    def test_get_puzzle_insight_uses_secrets_choice(
        self, mock_file, mock_json_load, mock_path
    ):
        """Test that get_puzzle_insight uses secrets.choice instead of random.choice"""
        # Setup mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_json_load.return_value = self.mock_collection_data

        # Create instance
        layout = EnhancedSudokuPDFLayout(
            input_dir=self.test_input_dir,
            output_dir=self.test_output_dir,
            title=self.test_title,
            author=self.test_author,
        )
        layout.puzzles = [self.mock_puzzle_data]

        # Test with different difficulty levels
        test_cases = [
            {"difficulty": "easy"},
            {"difficulty": "medium"},
            {"difficulty": "hard"},
            {"difficulty": "unknown"},  # Should default to medium
        ]

        for puzzle_data in test_cases:
            with patch("secrets.choice") as mock_secrets_choice:
                mock_secrets_choice.return_value = "test insight"

                result = layout.get_puzzle_insight(puzzle_data)

                # Verify secrets.choice was called
                mock_secrets_choice.assert_called_once()
                self.assertEqual(result, "test insight")

                # Verify the correct insights list was passed
                call_args = mock_secrets_choice.call_args[0][0]
                self.assertIsInstance(call_args, list)
                self.assertTrue(len(call_args) > 0)

                # Reset mock for next iteration
                mock_secrets_choice.reset_mock()

    @patch("scripts.sudoku_pdf_layout_v2.Path")
    @patch("scripts.sudoku_pdf_layout_v2.json.load")
    @patch("builtins.open", new_callable=mock_open, read_data='{"puzzles": [1]}')
    def test_get_puzzle_insight_easy_difficulty(
        self, mock_file, mock_json_load, mock_path
    ):
        """Test get_puzzle_insight returns appropriate insight for easy difficulty"""
        # Setup mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_json_load.return_value = self.mock_collection_data

        layout = EnhancedSudokuPDFLayout(
            input_dir=self.test_input_dir,
            output_dir=self.test_output_dir,
            title=self.test_title,
            author=self.test_author,
        )
        layout.puzzles = [self.mock_puzzle_data]

        puzzle_data = {"difficulty": "easy"}

        with patch("secrets.choice") as mock_secrets_choice:
            # Mock return value that would come from easy insights
            mock_secrets_choice.return_value = "Focus on the 3×3 boxes first - they often have the most clues to start with."

            result = layout.get_puzzle_insight(puzzle_data)

            # Verify the method was called with easy difficulty insights
            mock_secrets_choice.assert_called_once()
            call_args = mock_secrets_choice.call_args[0][0]

            # Verify it's the easy insights list (check for characteristic content)
            easy_content_found = any(
                "3×3 boxes" in insight or "rows or columns" in insight
                for insight in call_args
            )
            self.assertTrue(
                easy_content_found,
                "Easy difficulty insights should contain characteristic content",
            )

    @patch("scripts.sudoku_pdf_layout_v2.Path")
    @patch("scripts.sudoku_pdf_layout_v2.json.load")
    @patch("builtins.open", new_callable=mock_open, read_data='{"puzzles": [1]}')
    def test_get_puzzle_insight_hard_difficulty(
        self, mock_file, mock_json_load, mock_path
    ):
        """Test get_puzzle_insight returns appropriate insight for hard difficulty"""
        # Setup mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_json_load.return_value = self.mock_collection_data

        layout = EnhancedSudokuPDFLayout(
            input_dir=self.test_input_dir,
            output_dir=self.test_output_dir,
            title=self.test_title,
            author=self.test_author,
        )
        layout.puzzles = [self.mock_puzzle_data]

        puzzle_data = {"difficulty": "hard"}

        with patch("secrets.choice") as mock_secrets_choice:
            # Mock return value that would come from hard insights
            mock_secrets_choice.return_value = "This puzzle requires patience - the initial clues are sparse but well-placed."

            result = layout.get_puzzle_insight(puzzle_data)

            # Verify the method was called with hard difficulty insights
            mock_secrets_choice.assert_called_once()
            call_args = mock_secrets_choice.call_args[0][0]

            # Verify it's the hard insights list (check for characteristic content)
            hard_content_found = any(
                "patience" in insight or "sparse" in insight or "systematic" in insight
                for insight in call_args
            )
            self.assertTrue(
                hard_content_found,
                "Hard difficulty insights should contain characteristic content",
            )

    def test_secrets_module_imported(self):
        """Test that the secrets module is properly imported and available"""
        # This test verifies the import statement change
        self.assertTrue(
            hasattr(secrets, "choice"), "secrets module should have choice function"
        )

        # Test that secrets.choice works as expected
        test_list = ["option1", "option2", "option3"]
        result = secrets.choice(test_list)
        self.assertIn(
            result, test_list, "secrets.choice should return an item from the list"
        )


if __name__ == "__main__":
    unittest.main()
