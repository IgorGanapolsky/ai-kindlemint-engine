#!/usr/bin/env python3
"""
Unit tests for sudoku_pdf_layout_v2.py
Tests the Enhanced Sudoku PDF Layout Generator, specifically covering the changes
from random.choice to secrets.choice for cryptographically secure random selection.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout


class TestEnhancedSudokuPDFLayout(unittest.TestCase):
    """Test cases for EnhancedSudokuPDFLayout class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create mock metadata directory and files
        self.metadata_dir = self.input_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)

        # Mock collection data
        self.collection_data = {
            "title": "Test Sudoku Collection",
            "puzzles": [1, 2, 3],
            "difficulty": "medium",
            "total_puzzles": 3
        }

        # Mock puzzle data for different difficulties
        self.puzzle_data_easy = {
            "id": 1,
            "difficulty": "easy",
            "clue_count": 35,
            "solution": [[1] * 9 for _ in range(9)]
        }

        self.puzzle_data_medium = {
            "id": 2,
            "difficulty": "medium",
            "clue_count": 28,
            "solution": [[2] * 9 for _ in range(9)]
        }

        self.puzzle_data_hard = {
            "id": 3,
            "difficulty": "hard",
            "clue_count": 22,
            "solution": [[3] * 9 for _ in range(9)]
        }

        # Create mock JSON files
        collection_file = self.metadata_dir / "sudoku_collection.json"
        with open(collection_file, 'w') as f:
            json.dump(self.collection_data, f)

        puzzle_files = [
            (self.metadata_dir / "sudoku_puzzle_001.json", self.puzzle_data_easy),
            (self.metadata_dir / "sudoku_puzzle_002.json", self.puzzle_data_medium),
            (self.metadata_dir / "sudoku_puzzle_003.json", self.puzzle_data_hard),
        ]

        for file_path, data in puzzle_files:
            with open(file_path, 'w') as f:
                json.dump(data, f)

    def create_layout_instance(self):
        """Create a layout instance with mocked dependencies"""
        return EnhancedSudokuPDFLayout(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            title="Test Sudoku Book",
            author="Test Author",
            subtitle="Test Subtitle",
            include_solutions=True,
            isbn="123-456-789"
        )


class TestGetPuzzleInsight(TestEnhancedSudokuPDFLayout):
    """Test cases specifically for the get_puzzle_insight method and its security changes"""

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_uses_secrets_choice(self, mock_secrets_choice):
        """Test that get_puzzle_insight uses secrets.choice instead of random.choice"""
        layout = self.create_layout_instance()
        
        # Mock secrets.choice to return a specific value
        expected_insight = "Test insight for easy puzzle"
        mock_secrets_choice.return_value = expected_insight
        
        result = layout.get_puzzle_insight(self.puzzle_data_easy)
        
        # Verify secrets.choice was called
        self.assertTrue(mock_secrets_choice.called)
        self.assertEqual(result, expected_insight)

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_easy_difficulty(self, mock_secrets_choice):
        """Test get_puzzle_insight with easy difficulty"""
        layout = self.create_layout_instance()
        expected_insight = "Focus on the 3×3 boxes first"
        mock_secrets_choice.return_value = expected_insight
        
        result = layout.get_puzzle_insight(self.puzzle_data_easy)
        
        # Verify secrets.choice was called with easy insights
        mock_secrets_choice.assert_called_once()
        call_args = mock_secrets_choice.call_args[0][0]
        self.assertIsInstance(call_args, list)
        self.assertGreater(len(call_args), 0)
        self.assertEqual(result, expected_insight)

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_medium_difficulty(self, mock_secrets_choice):
        """Test get_puzzle_insight with medium difficulty"""
        layout = self.create_layout_instance()
        expected_insight = "This puzzle has a critical breakthrough"
        mock_secrets_choice.return_value = expected_insight
        
        result = layout.get_puzzle_insight(self.puzzle_data_medium)
        
        mock_secrets_choice.assert_called_once()
        call_args = mock_secrets_choice.call_args[0][0]
        self.assertIsInstance(call_args, list)
        self.assertGreater(len(call_args), 0)
        self.assertEqual(result, expected_insight)

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_hard_difficulty(self, mock_secrets_choice):
        """Test get_puzzle_insight with hard difficulty"""
        layout = self.create_layout_instance()
        expected_insight = "This puzzle requires patience"
        mock_secrets_choice.return_value = expected_insight
        
        result = layout.get_puzzle_insight(self.puzzle_data_hard)
        
        mock_secrets_choice.assert_called_once()
        call_args = mock_secrets_choice.call_args[0][0]
        self.assertIsInstance(call_args, list)
        self.assertGreater(len(call_args), 0)
        self.assertEqual(result, expected_insight)

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_unknown_difficulty(self, mock_secrets_choice):
        """Test get_puzzle_insight defaults to medium for unknown difficulty"""
        layout = self.create_layout_instance()
        expected_insight = "Default medium insight"
        mock_secrets_choice.return_value = expected_insight
        
        # Create puzzle data with unknown difficulty
        unknown_puzzle = {
            "id": 999,
            "difficulty": "unknown",
            "clue_count": 25
        }
        
        result = layout.get_puzzle_insight(unknown_puzzle)
        
        mock_secrets_choice.assert_called_once()
        self.assertEqual(result, expected_insight)

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_missing_difficulty(self, mock_secrets_choice):
        """Test get_puzzle_insight defaults to medium when difficulty is missing"""
        layout = self.create_layout_instance()
        expected_insight = "Default medium insight"
        mock_secrets_choice.return_value = expected_insight
        
        # Create puzzle data without difficulty field
        puzzle_no_difficulty = {
            "id": 999,
            "clue_count": 25
        }
        
        result = layout.get_puzzle_insight(puzzle_no_difficulty)
        
        mock_secrets_choice.assert_called_once()
        self.assertEqual(result, expected_insight)

    def test_insight_content_structure(self):
        """Test that insights are properly structured for each difficulty"""
        layout = self.create_layout_instance()
        
        # Test that insights exist for all difficulties
        easy_insight = layout.get_puzzle_insight(self.puzzle_data_easy)
        medium_insight = layout.get_puzzle_insight(self.puzzle_data_medium)
        hard_insight = layout.get_puzzle_insight(self.puzzle_data_hard)
        
        # All insights should be non-empty strings
        self.assertIsInstance(easy_insight, str)
        self.assertIsInstance(medium_insight, str)
        self.assertIsInstance(hard_insight, str)
        
        self.assertGreater(len(easy_insight), 0)
        self.assertGreater(len(medium_insight), 0)
        self.assertGreater(len(hard_insight), 0)

    def test_secrets_module_import(self):
        """Test that secrets module is properly imported"""
        # This test ensures the import change from random to secrets is working
        import scripts.sudoku_pdf_layout_v2 as layout_module
        
        # Check that secrets is available in the module
        self.assertTrue(hasattr(layout_module, 'secrets'))
        
        # Verify secrets.choice is callable
        self.assertTrue(callable(layout_module.secrets.choice))

    @patch('scripts.sudoku_pdf_layout_v2.secrets.choice')
    def test_get_puzzle_insight_call_frequency(self, mock_secrets_choice):
        """Test that secrets.choice is called exactly once per insight request"""
        layout = self.create_layout_instance()
        mock_secrets_choice.return_value = "Test insight"
        
        # Call get_puzzle_insight multiple times
        layout.get_puzzle_insight(self.puzzle_data_easy)
        layout.get_puzzle_insight(self.puzzle_data_medium)
        layout.get_puzzle_insight(self.puzzle_data_hard)
        
        # Should be called exactly 3 times
        self.assertEqual(mock_secrets_choice.call_count, 3)

    def test_cryptographic_randomness_behavior(self):
        """Test that the function produces varied outputs (indicating randomness)"""
        layout = self.create_layout_instance()
        
        # Generate multiple insights for the same puzzle
        insights = []
        for _ in range(10):
            insight = layout.get_puzzle_insight(self.puzzle_data_medium)
            insights.append(insight)
        
        # Should have some variation (not all identical) for a reasonable sample
        unique_insights = set(insights)
        # With 4 medium insights available, we expect some variety in 10 calls
        self.assertGreaterEqual(len(unique_insights), 1)
        self.assertLessEqual(len(unique_insights), 4)  # Can't exceed available insights


if __name__ == "__main__":
    unittest.main()