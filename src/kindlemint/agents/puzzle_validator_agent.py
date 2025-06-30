# src/kindlemint/agents/puzzle_validator_agent.py

from kindlemint.a2a.agent import A2AAgent
from kindlemint.a2a.registry import AgentRegistry
from kindlemint.validators.sudoku_validator import SudokuValidator


class PuzzleValidatorAgent(A2AAgent):
    """An A2A agent that validates puzzles."""

        """  Init  """
def __init__(self, agent_id: str, registry: AgentRegistry):
        super().__init__(agent_id, registry)
        self.core_validator = SudokuValidator()
        self.add_skill(
            "validate_sudoku",
            self.validate_sudoku,
            "Validates a Sudoku puzzle.",
        )

        """Validate Sudoku"""
def validate_sudoku(self, puzzle_data: dict, puzzle_id: str):
        """
        Validates a Sudoku puzzle.

        Args:
            puzzle_data: The puzzle data to validate.
            puzzle_id: The ID of the puzzle being validated.

        Returns:
            A list of validation issues.
        """
        return self.core_validator.validate_puzzle(puzzle_data, puzzle_id)
