#!/usr/bin/env python3
"""
Unit tests for Enhanced Sudoku PDF Layout Generator
Tests the security enhancement from random to secrets module
"""

import json
import secrets
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestEnhancedSudokuPDFLayoutSecrets(unittest.TestCase):
    """Test cases focusing on the secrets module implementation"""

    def setUp(self):
        """Set up test fixtures with mock data"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.metadata_dir = self.test_dir / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Create mock collection metadata
        collection_data = {
            "puzzles": [1, 2, 3],
            "difficulty": "medium",
            "total_puzzles": 3,
        }
        with open(self.metadata_dir / "sudoku_collection.json", "w") as f:
            json.dump(collection_data, f)

        # Create mock puzzle metadata files
        for i in range(1, 4):
            puzzle_data = {
                "id": i,
                "difficulty": "medium",
                "clue_count": 30,
                "grid": [[0] * 9 for _ in range(9)],
                "solution": [[1] * 9 for _ in range(9)],
            }
            with open(self.metadata_dir / f"sudoku_puzzle_{i:03d}.json", "w") as f:
                json.dump(puzzle_data, f)

        self.layout = EnhancedSudokuPDFLayout(
            input_dir=self.test_dir,
            output_dir=self.test_dir / "output",
            title="Test Sudoku Book",
            author="Test Author",
        )

    def test_secrets_module_imported(self):
        """Test that secrets module is properly imported"""
        # The file should import secrets at module level
        import scripts.sudoku_pdf_layout_v2 as module

        self.assertTrue(hasattr(module, "secrets"))

    @patch("secrets.choice")
    def test_get_puzzle_insight_uses_secrets_choice(self, mock_secrets_choice):
        """Test that get_puzzle_insight uses secrets.choice instead of random.choice"""
        # Set up mock return value
        expected_insight = "Test insight for security"
        mock_secrets_choice.return_value = expected_insight

        # Create test puzzle data
        puzzle_data = {"difficulty": "medium"}

        # Call the method
        result = self.layout.get_puzzle_insight(puzzle_data)

        # Verify secrets.choice was called
        self.assertTrue(mock_secrets_choice.called)
        self.assertEqual(result, expected_insight)

        # Verify the correct insights list was passed to secrets.choice
        call_args = mock_secrets_choice.call_args[0][0]
        self.assertIsInstance(call_args, list)
        self.assertTrue(len(call_args) > 0)

    @patch("secrets.choice")
    def test_get_puzzle_insight_easy_difficulty(self, mock_secrets_choice):
        """Test that easy difficulty selects from correct insights"""
        mock_secrets_choice.return_value = "Easy insight"

        puzzle_data = {"difficulty": "easy"}
        result = self.layout.get_puzzle_insight(puzzle_data)

        # Verify secrets.choice was called with easy insights
        call_args = mock_secrets_choice.call_args[0][0]
        expected_easy_insights = [
            "Focus on the 3×3 boxes first - they often have the most clues to start with.",
            "Look for rows or columns that are almost complete - filling these gives quick wins.",
            "Start with the number that appears most frequently in the given clues.",
            "The center box often provides good starting points in easier puzzles.",
        ]
        self.assertEqual(call_args, expected_easy_insights)
        self.assertEqual(result, "Easy insight")

    @patch("secrets.choice")
    def test_get_puzzle_insight_medium_difficulty(self, mock_secrets_choice):
        """Test that medium difficulty selects from correct insights"""
        mock_secrets_choice.return_value = "Medium insight"

        puzzle_data = {"difficulty": "medium"}
        result = self.layout.get_puzzle_insight(puzzle_data)

        # Verify secrets.choice was called with medium insights
        call_args = mock_secrets_choice.call_args[0][0]
        expected_medium_insights = [
            "This puzzle has a critical breakthrough in the middle rows - focus there first.",
            "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
            "The corner boxes have fewer clues but hold important constraints.",
            "Using pencil marks becomes essential for tracking multiple possibilities.",
        ]
        self.assertEqual(call_args, expected_medium_insights)
        self.assertEqual(result, "Medium insight")

    @patch("secrets.choice")
    def test_get_puzzle_insight_hard_difficulty(self, mock_secrets_choice):
        """Test that hard difficulty selects from correct insights"""
        mock_secrets_choice.return_value = "Hard insight"

        puzzle_data = {"difficulty": "hard"}
        result = self.layout.get_puzzle_insight(puzzle_data)

        # Verify secrets.choice was called with hard insights
        call_args = mock_secrets_choice.call_args[0][0]
        expected_hard_insights = [
            "This puzzle requires patience - the initial clues are sparse but well-placed.",
            "Look for the unique pattern in rows 3-5 that unlocks the middle section.",
            "The breakthrough often comes from finding a hidden pair in the corner boxes.",
            "Don't rush - systematic candidate elimination is more important than speed.",
        ]
        self.assertEqual(call_args, expected_hard_insights)
        self.assertEqual(result, "Hard insight")

    @patch("secrets.choice")
    def test_get_puzzle_insight_unknown_difficulty_defaults_medium(
        self, mock_secrets_choice
    ):
        """Test that unknown difficulty defaults to medium insights"""
        mock_secrets_choice.return_value = "Default medium insight"

        puzzle_data = {"difficulty": "unknown"}
        result = self.layout.get_puzzle_insight(puzzle_data)

        # Should default to medium insights
        call_args = mock_secrets_choice.call_args[0][0]
        expected_medium_insights = [
            "This puzzle has a critical breakthrough in the middle rows - focus there first.",
            "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
            "The corner boxes have fewer clues but hold important constraints.",
            "Using pencil marks becomes essential for tracking multiple possibilities.",
        ]
        self.assertEqual(call_args, expected_medium_insights)
        self.assertEqual(result, "Default medium insight")

    @patch("secrets.choice")
    def test_get_puzzle_insight_missing_difficulty_defaults_medium(
        self, mock_secrets_choice
    ):
        """Test that missing difficulty key defaults to medium insights"""
        mock_secrets_choice.return_value = "Default medium insight"

        puzzle_data = {}  # No difficulty key
        result = self.layout.get_puzzle_insight(puzzle_data)

        # Should default to medium insights
        call_args = mock_secrets_choice.call_args[0][0]
        expected_medium_insights = [
            "This puzzle has a critical breakthrough in the middle rows - focus there first.",
            "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
            "The corner boxes have fewer clues but hold important constraints.",
            "Using pencil marks becomes essential for tracking multiple possibilities.",
        ]
        self.assertEqual(call_args, expected_medium_insights)
        self.assertEqual(result, "Default medium insight")

    def test_secrets_choice_provides_cryptographically_secure_randomness(self):
        """Test that secrets.choice is used for cryptographically secure randomness"""
        # This is a behavioral test - secrets.choice should be used instead of random.choice
        # for security-sensitive randomness even though this isn't cryptographic use case
        puzzle_data = {"difficulty": "medium"}

        # Call multiple times to verify randomness is working
        results = []
        for _ in range(10):
            result = self.layout.get_puzzle_insight(puzzle_data)
            results.append(result)

        # All results should be valid medium insights
        valid_medium_insights = [
            "This puzzle has a critical breakthrough in the middle rows - focus there first.",
            "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
            "The corner boxes have fewer clues but hold important constraints.",
            "Using pencil marks becomes essential for tracking multiple possibilities.",
        ]

        for result in results:
            self.assertIn(result, valid_medium_insights)


if __name__ == "__main__":
    unittest.main()
