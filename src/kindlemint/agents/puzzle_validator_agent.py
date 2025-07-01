"""
Puzzle Validator Agent - Simplified without A2A framework
Validates puzzles directly
"""

from scripts.sudoku_validator import SudokuValidator


class PuzzleValidatorAgent:
    """A simplified agent that validates puzzles."""

    def __init__(self, agent_id=None, registry=None):
        """Initialize the puzzle validator agent"""
        self.agent_id = agent_id or "puzzle_validator"
        self.core_validator = SudokuValidator()

    def validate_sudoku(self, puzzle_data):
        """Validate a Sudoku puzzle"""
        return self.core_validator.validate(puzzle_data)
