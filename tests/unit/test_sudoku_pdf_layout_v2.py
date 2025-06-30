#!/usr/bin/env python3
"""
Unit tests for EnhancedSudokuPDFLayout class
Tests the PDF layout generator with focus on the changes made to get_puzzle_insight method
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
        # Create temporary directories for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.temp_dir / "input"
        self.output_dir = self.temp_dir / "output"
        self.metadata_dir = self.input_dir / "metadata"
        
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        self.metadata_dir.mkdir(parents=True)
        
        # Create mock metadata files
        self.create_mock_metadata()
        
        # Initialize the layout generator
        self.layout = EnhancedSudokuPDFLayout(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            title="Test Sudoku Book Volume 1",
            author="Test Author",
            subtitle="Test Subtitle"
        )

    def create_mock_metadata(self):
        """Create mock metadata files for testing"""
        # Collection metadata
        collection_data = {
            "title": "Test Sudoku Collection",
            "total_puzzles": 3,
            "puzzles": [1, 2, 3]
        }
        
        collection_file = self.metadata_dir / "sudoku_collection.json"
        with open(collection_file, 'w') as f:
            json.dump(collection_data, f)
        
        # Individual puzzle metadata
        for i, difficulty in enumerate(["easy", "medium", "hard"], 1):
            puzzle_data = {
                "id": i,
                "difficulty": difficulty,
                "clue_count": 30 + i * 5,
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            puzzle_file = self.metadata_dir / f"sudoku_puzzle_{i:03d}.json"
            with open(puzzle_file, 'w') as f:
                json.dump(puzzle_data, f)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestGetPuzzleInsight(TestEnhancedSudokuPDFLayout):
    """Test cases specifically for the get_puzzle_insight method that was changed"""

    def test_get_puzzle_insight_easy_difficulty(self):
        """Test that get_puzzle_insight returns correct insights for easy puzzles"""
        puzzle_data = {"difficulty": "easy", "id": 1}
        
        # Mock secrets.choice to return a predictable result
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "Focus on the 3×3 boxes first - they often have the most clues to start with."
            
            insight = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called
            self.assertTrue(mock_choice.called)
            
            # Verify the returned insight
            self.assertEqual(insight, "Focus on the 3×3 boxes first - they often have the most clues to start with.")
            
            # Verify it was called with easy difficulty insights
            call_args = mock_choice.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertIn("Focus on the 3×3 boxes first - they often have the most clues to start with.", call_args)

    def test_get_puzzle_insight_medium_difficulty(self):
        """Test that get_puzzle_insight returns correct insights for medium puzzles"""
        puzzle_data = {"difficulty": "medium", "id": 2}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "This puzzle has a critical breakthrough in the middle rows - focus there first."
            
            insight = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called
            self.assertTrue(mock_choice.called)
            
            # Verify the returned insight
            self.assertEqual(insight, "This puzzle has a critical breakthrough in the middle rows - focus there first.")
            
            # Verify it was called with medium difficulty insights
            call_args = mock_choice.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertIn("This puzzle has a critical breakthrough in the middle rows - focus there first.", call_args)

    def test_get_puzzle_insight_hard_difficulty(self):
        """Test that get_puzzle_insight returns correct insights for hard puzzles"""
        puzzle_data = {"difficulty": "hard", "id": 3}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "This puzzle requires patience - the initial clues are sparse but well-placed."
            
            insight = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called
            self.assertTrue(mock_choice.called)
            
            # Verify the returned insight
            self.assertEqual(insight, "This puzzle requires patience - the initial clues are sparse but well-placed.")
            
            # Verify it was called with hard difficulty insights
            call_args = mock_choice.call_args[0][0]
            self.assertIsInstance(call_args, list)
            self.assertIn("This puzzle requires patience - the initial clues are sparse but well-placed.", call_args)

    def test_get_puzzle_insight_missing_difficulty_defaults_to_medium(self):
        """Test that missing difficulty defaults to medium insights"""
        puzzle_data = {"id": 1}  # No difficulty specified
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "This puzzle has a critical breakthrough in the middle rows - focus there first."
            
            insight = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called
            self.assertTrue(mock_choice.called)
            
            # Verify it was called with medium difficulty insights (default)
            call_args = mock_choice.call_args[0][0]
            self.assertIsInstance(call_args, list)
            # Check that it contains medium-specific insights
            medium_insights = [
                "This puzzle has a critical breakthrough in the middle rows - focus there first.",
                "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
                "The corner boxes have fewer clues but hold important constraints.",
                "Using pencil marks becomes essential for tracking multiple possibilities.",
            ]
            self.assertEqual(call_args, medium_insights)

    def test_get_puzzle_insight_invalid_difficulty_defaults_to_medium(self):
        """Test that invalid difficulty defaults to medium insights"""
        puzzle_data = {"difficulty": "invalid", "id": 1}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "This puzzle has a critical breakthrough in the middle rows - focus there first."
            
            insight = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called
            self.assertTrue(mock_choice.called)
            
            # Verify it was called with medium difficulty insights (default)
            call_args = mock_choice.call_args[0][0]
            self.assertIsInstance(call_args, list)
            # Check that it contains medium-specific insights
            medium_insights = [
                "This puzzle has a critical breakthrough in the middle rows - focus there first.",
                "Pay attention to the interaction between boxes 4, 5, and 6 for key deductions.",
                "The corner boxes have fewer clues but hold important constraints.",
                "Using pencil marks becomes essential for tracking multiple possibilities.",
            ]
            self.assertEqual(call_args, medium_insights)

    def test_get_puzzle_insight_uses_secrets_not_random(self):
        """Test that the method uses secrets.choice, not random.choice"""
        puzzle_data = {"difficulty": "easy", "id": 1}
        
        # Patch both secrets.choice and random.choice to verify which is called
        with patch('secrets.choice') as mock_secrets_choice, \
             patch('random.choice') as mock_random_choice:
            
            mock_secrets_choice.return_value = "Test insight"
            
            insight = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called
            self.assertTrue(mock_secrets_choice.called)
            
            # Verify random.choice was NOT called
            self.assertFalse(mock_random_choice.called)
            
            # Verify the result
            self.assertEqual(insight, "Test insight")

    def test_get_puzzle_insight_returns_string(self):
        """Test that get_puzzle_insight always returns a string"""
        test_cases = [
            {"difficulty": "easy", "id": 1},
            {"difficulty": "medium", "id": 2},
            {"difficulty": "hard", "id": 3},
            {"difficulty": "invalid", "id": 4},
            {"id": 5}  # No difficulty
        ]
        
        for puzzle_data in test_cases:
            with self.subTest(puzzle_data=puzzle_data):
                insight = self.layout.get_puzzle_insight(puzzle_data)
                self.assertIsInstance(insight, str)
                self.assertGreater(len(insight), 0)

    def test_get_puzzle_insight_all_insights_present(self):
        """Test that all expected insights are present in the insights dictionary"""
        puzzle_data = {"difficulty": "easy", "id": 1}
        
        # Get the actual insights from the method by examining what gets passed to secrets.choice
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "dummy"
            
            # Test each difficulty level
            for difficulty in ["easy", "medium", "hard"]:
                puzzle_data["difficulty"] = difficulty
                self.layout.get_puzzle_insight(puzzle_data)
                
                call_args = mock_choice.call_args[0][0]
                self.assertIsInstance(call_args, list)
                self.assertGreater(len(call_args), 0)
                
                # All insights should be non-empty strings
                for insight in call_args:
                    self.assertIsInstance(insight, str)
                    self.assertGreater(len(insight.strip()), 0)


if __name__ == "__main__":
    unittest.main()