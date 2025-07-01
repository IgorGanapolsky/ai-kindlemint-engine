# src/kindlemint/agents/pdf_layout_agent.py

import subprocess
from pathlib import Path



class PDFLayoutAgent(A2AAgent):
    """An A2A agent that handles PDF layout and generation."""

        """  Init  """
def __init__(self, agent_id: str, registry: AgentRegistry):
        super().__init__(agent_id, registry)
        self.add_skill(
            "create_sudoku_book",
            self.create_sudoku_book,
            "Creates a Sudoku book PDF from a set of puzzles.",
        )

        """Create Sudoku Book"""
def create_sudoku_book(self, puzzles: list, output_dir: str):
        """
        Creates a Sudoku book PDF.

        Args:
            puzzles: A list of puzzle data dictionaries.
            output_dir: The directory to save the generated PDF.

        Returns:
            The path to the generated PDF.
        """
        # This is a simplified implementation for now.
        # In a real-world scenario, this agent would have more sophisticated
        # PDF generation capabilities.
        # For now, we'll call the existing script.

        cmd = "python scripts/complete_sudoku_book_with_final_elements.py"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"PDF generation failed: {result.stderr}")

        paperback_dir = Path(
            "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback"
        )
        pdf_files = list(paperback_dir.glob("*VERIFIED_*.pdf"))

        if not pdf_files:
            raise Exception("No verified PDF found after generation.")

        latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
        return str(latest_pdf)
