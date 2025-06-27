#!/usr/bin/env python3
"""
Simple unit tests for Crossword puzzle generator
Basic tests that work with the current implementation
"""

import sys
import unittest
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from scripts.crossword_engine_v2 import CrosswordEngineV2


class TestCrosswordEngineSimple(unittest.TestCase):
    """Simple test cases for Crossword puzzle generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_crossword_engine_creation(self):
        """Test that CrosswordEngineV2 can be instantiated"""
        engine = CrosswordEngineV2(
            output_dir=self.temp_dir,
            puzzle_count=1,
            difficulty="EASY"
        )
        self.assertIsNotNone(engine)
        self.assertEqual(engine.puzzle_count, 1)
        self.assertEqual(engine.difficulty_mode, "EASY")
    
    def test_symmetric_pattern_creation(self):
        """Test creation of symmetric crossword pattern"""
        engine = CrosswordEngineV2(
            output_dir=self.temp_dir,
            puzzle_count=1
        )
        # Use generate_grid_with_content which applies the symmetric pattern
        grid = engine.generate_grid_with_content(1)
        
        # Check grid is 15x15
        self.assertEqual(len(grid), 15)
        self.assertEqual(len(grid[0]), 15)
        
        # Check symmetry
        for i in range(15):
            for j in range(15):
                self.assertEqual(
                    grid[i][j], 
                    grid[14-i][14-j],
                    f"Grid not symmetric at ({i},{j}) vs ({14-i},{14-j})"
                )
    
    def test_difficulty_assignment(self):
        """Test difficulty assignment for puzzles"""
        engine = CrosswordEngineV2(
            output_dir=self.temp_dir,
            puzzle_count=10,
            difficulty="mixed"
        )
        
        # Test difficulty distribution
        difficulties = []
        for i in range(1, 11):
            diff = engine._get_difficulty_for_puzzle(i)
            difficulties.append(diff)
        
        # Should have mix of difficulties
        self.assertIn("EASY", difficulties)
        self.assertIn("MEDIUM", difficulties)
        self.assertIn("HARD", difficulties)


if __name__ == "__main__":
    unittest.main()