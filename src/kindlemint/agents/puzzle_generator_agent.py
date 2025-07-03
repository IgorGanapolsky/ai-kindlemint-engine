"""
Puzzle Generator Agent - Generates puzzles
Generates puzzles directly
"""

from scripts.sudoku_generator_engine import SudokuGenerator


class PuzzleGeneratorAgent:
    """A simplified agent that generates puzzles."""

    def __init__(self, agent_id=None, registry=None):
        """Initialize the puzzle generator agent"""
        self.agent_id = agent_id or "puzzle_generator"
        self.core_generator = SudokuGenerator()

    def generate_sudoku(self, difficulty="medium"):
        """Generate a Sudoku puzzle with specified difficulty"""
        return self.core_generator.generate_puzzle(difficulty)
