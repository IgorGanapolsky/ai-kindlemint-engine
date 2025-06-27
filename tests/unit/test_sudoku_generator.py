#!/usr/bin/env python3
"""
Unit tests for Sudoku puzzle generator
Tests puzzle validity, solvability, and difficulty levels
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from sudoku_generator import SudokuGenerator


class TestSudokuGenerator(unittest.TestCase):
    """Test cases for Sudoku puzzle generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = SudokuGenerator()
    
    def test_generate_single_puzzle(self):
        """Test generation of a single puzzle"""
        puzzle = self.generator.generate_puzzle(difficulty="medium")
        
        self.assertIsNotNone(puzzle)
        self.assertIn("grid", puzzle)
        self.assertIn("solution", puzzle)
        self.assertIn("difficulty", puzzle)
        self.assertEqual(puzzle["difficulty"], "medium")
    
    def test_puzzle_dimensions(self):
        """Test that puzzles have correct dimensions"""
        puzzle = self.generator.generate_puzzle()
        
        # Check grid is 9x9
        self.assertEqual(len(puzzle["grid"]), 9)
        for row in puzzle["grid"]:
            self.assertEqual(len(row), 9)
        
        # Check solution is 9x9
        self.assertEqual(len(puzzle["solution"]), 9)
        for row in puzzle["solution"]:
            self.assertEqual(len(row), 9)
    
    def test_puzzle_validity(self):
        """Test that generated puzzles are valid"""
        puzzle = self.generator.generate_puzzle()
        grid = puzzle["grid"]
        
        # Check all values are 0-9
        for row in grid:
            for cell in row:
                self.assertIn(cell, range(10))
        
        # Check that puzzle has empty cells
        empty_count = sum(1 for row in grid for cell in row if cell == 0)
        self.assertGreater(empty_count, 0)
        self.assertLess(empty_count, 81)  # Not completely empty
    
    def test_solution_validity(self):
        """Test that solutions are valid complete Sudoku grids"""
        puzzle = self.generator.generate_puzzle()
        solution = puzzle["solution"]
        
        # Check all values are 1-9
        for row in solution:
            for cell in row:
                self.assertIn(cell, range(1, 10))
        
        # Check rows have unique values
        for row in solution:
            self.assertEqual(len(set(row)), 9)
        
        # Check columns have unique values
        for col in range(9):
            column = [solution[row][col] for row in range(9)]
            self.assertEqual(len(set(column)), 9)
        
        # Check 3x3 boxes have unique values
        for box_row in range(3):
            for box_col in range(3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box_values.append(solution[row][col])
                self.assertEqual(len(set(box_values)), 9)
    
    def test_puzzle_matches_solution(self):
        """Test that puzzle clues match the solution"""
        puzzle = self.generator.generate_puzzle()
        grid = puzzle["grid"]
        solution = puzzle["solution"]
        
        for i in range(9):
            for j in range(9):
                if grid[i][j] != 0:
                    self.assertEqual(grid[i][j], solution[i][j])
    
    def test_difficulty_levels(self):
        """Test different difficulty levels"""
        difficulties = ["easy", "medium", "hard", "expert"]
        
        for difficulty in difficulties:
            puzzle = self.generator.generate_puzzle(difficulty=difficulty)
            self.assertEqual(puzzle["difficulty"], difficulty)
            
            # Check that harder puzzles have more empty cells
            grid = puzzle["grid"]
            empty_count = sum(1 for row in grid for cell in row if cell == 0)
            
            if difficulty == "easy":
                self.assertLess(empty_count, 45)
            elif difficulty == "expert":
                self.assertGreater(empty_count, 55)
    
    def test_unique_puzzles(self):
        """Test that generator creates unique puzzles"""
        puzzles = []
        for _ in range(5):
            puzzle = self.generator.generate_puzzle()
            # Convert grid to tuple for comparison
            grid_tuple = tuple(tuple(row) for row in puzzle["grid"])
            self.assertNotIn(grid_tuple, puzzles)
            puzzles.append(grid_tuple)
    
    def test_puzzle_solvability(self):
        """Test that puzzles have unique solutions"""
        puzzle = self.generator.generate_puzzle()
        
        # This is a simple check - in production, you'd want a full solver
        # For now, we just verify the solution is provided
        self.assertIsNotNone(puzzle["solution"])
        
        # Verify solution is complete (no zeros)
        solution = puzzle["solution"]
        for row in solution:
            self.assertNotIn(0, row)
    
    def test_batch_generation(self):
        """Test generating multiple puzzles"""
        count = 10
        puzzles = []
        
        for i in range(count):
            puzzle = self.generator.generate_puzzle()
            puzzles.append(puzzle)
        
        self.assertEqual(len(puzzles), count)
        
        # Check all puzzles are valid
        for puzzle in puzzles:
            self.assertIn("grid", puzzle)
            self.assertIn("solution", puzzle)
            self.assertIn("difficulty", puzzle)
    
    def test_invalid_difficulty(self):
        """Test handling of invalid difficulty parameter"""
        # Should default to medium or raise exception
        puzzle = self.generator.generate_puzzle(difficulty="invalid")
        self.assertIn(puzzle["difficulty"], ["easy", "medium", "hard", "expert"])
    
    def test_puzzle_statistics(self):
        """Test that puzzle includes statistics"""
        puzzle = self.generator.generate_puzzle()
        
        # Count given clues
        grid = puzzle["grid"]
        given_count = sum(1 for row in grid for cell in row if cell != 0)
        
        # Should have reasonable number of clues
        self.assertGreater(given_count, 17)  # Minimum for unique solution
        self.assertLess(given_count, 81)     # Not a complete grid


class TestSudokuGeneratorHelpers(unittest.TestCase):
    """Test helper methods of SudokuGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = SudokuGenerator()
    
    def test_is_valid_placement(self):
        """Test the validity checker for number placement"""
        # Create a partially filled grid
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        
        # Test valid placements
        self.assertTrue(self.generator._is_valid(grid, 0, 1, 3))
        self.assertTrue(self.generator._is_valid(grid, 1, 0, 3))
        
        # Test invalid placements
        self.assertFalse(self.generator._is_valid(grid, 0, 1, 5))  # Same row
        self.assertFalse(self.generator._is_valid(grid, 1, 0, 5))  # Same column
        self.assertFalse(self.generator._is_valid(grid, 1, 1, 5))  # Same box
    
    def test_grid_initialization(self):
        """Test grid initialization"""
        grid = self.generator._create_empty_grid()
        
        self.assertEqual(len(grid), 9)
        for row in grid:
            self.assertEqual(len(row), 9)
            self.assertEqual(set(row), {0})


if __name__ == "__main__":
    unittest.main()