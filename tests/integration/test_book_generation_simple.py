#!/usr/bin/env python3
"""
Simple integration tests for book generation
Basic tests that verify the components work together
"""

import sys
import unittest
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from scripts.sudoku_generator import SudokuGenerator


class TestBookGenerationSimple(unittest.TestCase):
    """Simple integration tests for book generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_sudoku_generation_pipeline(self):
        """Test basic sudoku generation works"""
        generator = SudokuGenerator()
        
        # Test single puzzle generation
        puzzle_data = generator.generate_puzzle("easy")
        
        self.assertIn("grid", puzzle_data)
        self.assertIn("solution", puzzle_data)
        self.assertIn("difficulty", puzzle_data)
        self.assertIn("clue_count", puzzle_data)
        
        # Verify grid and solution are 9x9
        self.assertEqual(len(puzzle_data["grid"]), 9)
        self.assertEqual(len(puzzle_data["solution"]), 9)
        self.assertEqual(len(puzzle_data["grid"][0]), 9)
        self.assertEqual(len(puzzle_data["solution"][0]), 9)
    
    def test_puzzle_uniqueness(self):
        """Test that multiple puzzles are unique"""
        generator = SudokuGenerator()
        
        puzzles = []
        for _ in range(3):
            puzzle = generator.generate_puzzle("medium")
            puzzles.append(puzzle["grid"])
        
        # Check that all puzzles are different
        for i in range(len(puzzles)):
            for j in range(i + 1, len(puzzles)):
                self.assertNotEqual(
                    puzzles[i], 
                    puzzles[j],
                    "Generated duplicate puzzles"
                )
    
    def test_difficulty_levels(self):
        """Test generation at different difficulty levels"""
        generator = SudokuGenerator()
        
        difficulties = ["easy", "medium", "hard", "expert"]
        
        for difficulty in difficulties:
            puzzle = generator.generate_puzzle(difficulty)
            self.assertEqual(puzzle["difficulty"], difficulty)
            
            # Count clues
            clue_count = sum(
                1 for row in puzzle["grid"] 
                for cell in row if cell != 0
            )
            
            # Basic check that harder puzzles have fewer clues
            if difficulty == "easy":
                self.assertGreater(clue_count, 30)
            elif difficulty == "expert":
                self.assertLess(clue_count, 30)


if __name__ == "__main__":
    unittest.main()