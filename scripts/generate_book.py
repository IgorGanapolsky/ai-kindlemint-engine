# scripts/a2a_orchestrator.py

import sys
from pathlib import Path

from kindlemint.agents.pdf_layout_agent import PDFLayoutAgent
from kindlemint.agents.puzzle_generator_agent import PuzzleGeneratorAgent
from kindlemint.agents.puzzle_validator_agent import PuzzleValidatorAgent
from scripts.large_print_sudoku_generator import LargePrintSudokuGenerator

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent))

"""Orchestrates the book generation process using A2A agents."""

"""  Init  """


def __init__(self):
    self.registry = AgentRegistry(registry_file="a2a_registry.json")
    self.server = A2AServer(self.registry)

    # Instantiate and register agents
    self.puzzle_generator = PuzzleGeneratorAgent(
        "puzzle_generator", self.registry)
    self.puzzle_validator = PuzzleValidatorAgent(
        "puzzle_validator", self.registry)
    self.pdf_layout = PDFLayoutAgent("pdf_layout", self.registry)
    self.image_renderer = LargePrintSudokuGenerator(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles"
    )

    self.server.register_agent(self.puzzle_generator)
    self.server.register_agent(self.puzzle_validator)
    self.server.register_agent(self.pdf_layout)

    """Run Workflow"""


def run_workflow(self):
    """Runs the full book generation workflow."""
    print("🚀 Starting A2A book generation workflow...")

    # 1. Generate puzzles
    print("   -> Requesting 100 'easy' puzzles from puzzle_generator...")
    puzzles = []
    for i in range(100):
        puzzle_data = self.puzzle_generator.generate_sudoku(difficulty="easy")

        # 2. Validate each puzzle
        validation_result = self.puzzle_validator.validate_sudoku(
            puzzle_data, f"puzzle_{i + 1}"
        )
        if validation_result:
            print(
                f"   -> Validation failed for puzzle {i + 1}: {validation_result}")
            # For simplicity, we'll stop on the first error.
            # A more robust implementation would handle this differently.
            return

        puzzles.append(puzzle_data)

    print("   -> Successfully generated and validated 100 puzzles.")

    # 3. Render puzzle images
    print("   -> Rendering puzzle images...")
    for i, puzzle in enumerate(puzzles):
        self.image_renderer.generate_puzzle_image(puzzle, i + 1)
        self.image_renderer.generate_solution_image(puzzle, i + 1)
    print("   -> Successfully rendered 100 puzzle and solution images.")

    # 4. Generate the PDF
    print("   -> Requesting PDF generation from pdf_layout...")
    pdf_path = self.pdf_layout.create_sudoku_book(
        puzzles,
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback",
    )
    print(f"   -> PDF generated at: {pdf_path}")

    print("✅ A2A book generation workflow complete.")


if __name__ == "__main__":
    orchestrator.run_workflow()
