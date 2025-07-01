"""
Puzzle Generator Agent - Simplified without A2A framework
Generates puzzles directly
"""

from scripts.sudoku_generator_engine import SudokuGenerator


class PuzzleGeneratorAgent:
    """A simplified agent that generates puzzles."""

    def __init__(self, agent_id=None, registry=None):
        """
        Initialize a PuzzleGeneratorAgent with an optional agent ID and a Sudoku puzzle generator.

        Parameters:
            agent_id (str, optional): Custom identifier for the agent. Defaults to "puzzle_generator" if not provided.
        """
        self.agent_id = agent_id or "puzzle_generator"
        self.core_generator = SudokuGenerator()

    def generate_sudoku(self, difficulty="medium"):
        """
        Generate a Sudoku puzzle of the specified difficulty level.

        Parameters:
            difficulty (str): The desired difficulty level for the puzzle (e.g., "easy", "medium", "hard").

        Returns:
            dict: A dictionary representing the generated Sudoku puzzle.
        """
        return self.core_generator.generate_puzzle(difficulty)
