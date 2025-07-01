"""
Puzzle Validator Agent - Simplified without A2A framework
Validates puzzles directly
"""

from scripts.sudoku_validator import SudokuValidator


class PuzzleValidatorAgent:
    """A simplified agent that validates puzzles."""

    def __init__(self, agent_id=None, registry=None):
        """
        Initialize a PuzzleValidatorAgent with an optional agent ID.
        
        If no agent ID is provided, defaults to "puzzle_validator". Also creates an internal SudokuValidator instance for puzzle validation.
        """
        self.agent_id = agent_id or "puzzle_validator"
        self.core_validator = SudokuValidator()

    def validate_sudoku(self, puzzle_data):
        """
        Validates a Sudoku puzzle using the core SudokuValidator.
        
        Parameters:
            puzzle_data (dict): The Sudoku puzzle data to be validated.
        
        Returns:
            dict: The result of the validation, typically including validity status and any errors found.
        """
        return self.core_validator.validate(puzzle_data)
