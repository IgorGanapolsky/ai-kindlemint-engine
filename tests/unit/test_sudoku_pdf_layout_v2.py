#!/usr/bin/env python3
"""
Unit tests for sudoku_pdf_layout_v2.py
Testing the EnhancedSudokuPDFLayout class and specifically the security changes
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from sudoku_pdf_layout_v2 import EnhancedSudokuPDFLayout


class TestEnhancedSudokuPDFLayout(unittest.TestCase):
    """Test cases for EnhancedSudokuPDFLayout class"""

    def setUp(self):
        """Set up test fixtures with proper mocking"""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.test_dir) / "input"
        self.output_dir = Path(self.test_dir) / "output"
        self.metadata_dir = self.input_dir / "metadata"
        
        # Create directory structure
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        self.metadata_dir.mkdir(parents=True)
        
        # Create test metadata files
        self.create_test_metadata()
        
        # Mock reportlab components to avoid dependency issues
        self.patcher = patch.multiple(
            'sudoku_pdf_layout_v2',
            SimpleDocTemplate=MagicMock(),
            Paragraph=MagicMock(),
            Spacer=MagicMock(),
            PageBreak=MagicMock(),
            Image=MagicMock(),
            Table=MagicMock(),
            TableStyle=MagicMock(),
            getSampleStyleSheet=MagicMock(return_value=self.mock_styles()),
            ParagraphStyle=MagicMock()
        )
        self.patcher.start()
        
    def tearDown(self):
        """Clean up test fixtures"""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.test_dir)
    
    def mock_styles(self):
        """Create mock styles dictionary"""
        mock_style = MagicMock()
        styles = {
            'Title': mock_style,
            'Normal': mock_style,
            'Heading1': mock_style
        }
        styles.add = MagicMock()
        return styles
        
    def create_test_metadata(self):
        """Create test metadata files"""
        # Collection metadata
        collection_data = {
            "title": "Test Sudoku Collection",
            "puzzles": [1, 2, 3]
        }
        
        with open(self.metadata_dir / "sudoku_collection.json", "w") as f:
            json.dump(collection_data, f)
        
        # Individual puzzle metadata
        for puzzle_id in [1, 2, 3]:
            puzzle_data = {
                "id": puzzle_id,
                "difficulty": "medium",
                "clue_count": 25,
                "solution_time": 15
            }
            
            with open(self.metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json", "w") as f:
                json.dump(puzzle_data, f)

    def test_initialization(self):
        """Test proper initialization of EnhancedSudokuPDFLayout"""
        layout = EnhancedSudokuPDFLayout(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            title="Test Sudoku Book",
            author="Test Author"
        )
        
        self.assertEqual(layout.title, "Test Sudoku Book")
        self.assertEqual(layout.author, "Test Author")
        self.assertEqual(layout.volume_number, "1")  # Default
        self.assertTrue(layout.include_solutions)
        self.assertEqual(layout.isbn, "[ISBN TO BE ASSIGNED]")
        
    def test_volume_number_extraction(self):
        """Test volume number extraction from title"""
        layout = EnhancedSudokuPDFLayout(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            title="Large Print Sudoku Masters - Volume 3",
            author="Test Author"
        )
        
        self.assertEqual(layout.volume_number, "3")
        
    def test_custom_isbn(self):
        """Test custom ISBN assignment"""
        isbn = "978-1234567890"
        layout = EnhancedSudokuPDFLayout(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            title="Test Book",
            author="Test Author",
            isbn=isbn
        )
        
        self.assertEqual(layout.isbn, isbn)


class TestGetPuzzleInsight(unittest.TestCase):
    """Test cases specifically for the get_puzzle_insight method and secrets usage"""
    
    def setUp(self):
        """Set up test fixtures for insight testing"""
        # Create minimal test environment
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.test_dir) / "input"
        self.output_dir = Path(self.test_dir) / "output"
        self.metadata_dir = self.input_dir / "metadata"
        
        # Create directory structure
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        self.metadata_dir.mkdir(parents=True)
        
        # Create minimal metadata
        collection_data = {"title": "Test", "puzzles": [1]}
        with open(self.metadata_dir / "sudoku_collection.json", "w") as f:
            json.dump(collection_data, f)
            
        puzzle_data = {"id": 1, "difficulty": "medium"}
        with open(self.metadata_dir / "sudoku_puzzle_001.json", "w") as f:
            json.dump(puzzle_data, f)
        
        # Mock reportlab
        self.patcher = patch.multiple(
            'sudoku_pdf_layout_v2',
            SimpleDocTemplate=MagicMock(),
            getSampleStyleSheet=MagicMock(return_value=self.mock_styles())
        )
        self.patcher.start()
        
        # Create layout instance
        self.layout = EnhancedSudokuPDFLayout(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            title="Test Book",
            author="Test Author"
        )
        
    def tearDown(self):
        """Clean up test fixtures"""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.test_dir)
        
    def mock_styles(self):
        """Create mock styles dictionary"""
        mock_style = MagicMock()
        styles = {'Title': mock_style, 'Normal': mock_style, 'Heading1': mock_style}
        styles.add = MagicMock()
        return styles
    
    @patch('secrets.choice')
    def test_get_puzzle_insight_uses_secrets_choice(self, mock_secrets_choice):
        """Test that get_puzzle_insight uses secrets.choice instead of random.choice"""
        # Arrange
        mock_secrets_choice.return_value = "Test insight from secrets"
        puzzle_data = {"difficulty": "medium"}
        
        # Act
        result = self.layout.get_puzzle_insight(puzzle_data)
        
        # Assert
        mock_secrets_choice.assert_called_once()
        self.assertEqual(result, "Test insight from secrets")
        
    def test_get_puzzle_insight_easy_difficulty(self):
        """Test get_puzzle_insight with easy difficulty"""
        puzzle_data = {"difficulty": "easy"}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "Easy insight"
            result = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called with easy insights
            call_args = mock_choice.call_args[0][0]
            self.assertIn("Focus on the 3×3 boxes first", call_args[0])
            self.assertEqual(result, "Easy insight")
    
    def test_get_puzzle_insight_medium_difficulty(self):
        """Test get_puzzle_insight with medium difficulty"""
        puzzle_data = {"difficulty": "medium"}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "Medium insight"
            result = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called with medium insights
            call_args = mock_choice.call_args[0][0]
            self.assertIn("critical breakthrough in the middle rows", call_args[0])
            self.assertEqual(result, "Medium insight")
    
    def test_get_puzzle_insight_hard_difficulty(self):
        """Test get_puzzle_insight with hard difficulty"""
        puzzle_data = {"difficulty": "hard"}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "Hard insight"
            result = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify secrets.choice was called with hard insights
            call_args = mock_choice.call_args[0][0]
            self.assertIn("requires patience", call_args[0])
            self.assertEqual(result, "Hard insight")
    
    def test_get_puzzle_insight_unknown_difficulty_defaults_to_medium(self):
        """Test get_puzzle_insight with unknown difficulty defaults to medium"""
        puzzle_data = {"difficulty": "unknown"}
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "Default insight"
            result = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify it defaults to medium insights
            call_args = mock_choice.call_args[0][0]
            self.assertIn("critical breakthrough in the middle rows", call_args[0])
            self.assertEqual(result, "Default insight")
    
    def test_get_puzzle_insight_missing_difficulty_defaults_to_medium(self):
        """Test get_puzzle_insight with missing difficulty key defaults to medium"""
        puzzle_data = {}  # No difficulty key
        
        with patch('secrets.choice') as mock_choice:
            mock_choice.return_value = "Default insight"
            result = self.layout.get_puzzle_insight(puzzle_data)
            
            # Verify it defaults to medium insights
            call_args = mock_choice.call_args[0][0]
            self.assertIn("critical breakthrough in the middle rows", call_args[0])
            self.assertEqual(result, "Default insight")


if __name__ == "__main__":
    unittest.main()