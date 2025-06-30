# src/kindlemint/agents/puzzle_generator_agent.py

from kindlemint.a2a.agent import A2AAgent
from kindlemint.a2a.registry import AgentRegistry
from kindlemint.engines.sudoku import SudokuGenerator


class PuzzleGeneratorAgent(A2AAgent):
    """An A2A agent that generates puzzles."""

    def __init__(self, agent_id: str, registry: AgentRegistry):
        super().__init__(agent_id, registry)
        self.core_generator = SudokuGenerator()
        self.add_skill(
            "generate_sudoku",
            self.generate_sudoku,
            "Generates a Sudoku puzzle with a specified difficulty.",
        )

    def generate_sudoku(self, difficulty: str = "medium"):
        """
        Generates a Sudoku puzzle.

        Args:
            difficulty: The difficulty of the puzzle (e.g., 'easy', 'medium', 'hard').

        Returns:
            A dictionary containing the puzzle grid, solution, and other metadata.
        """
        return self.core_generator.generate_puzzle(difficulty)
