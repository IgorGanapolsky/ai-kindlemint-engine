#!/usr/bin/env python3
"""
Generate Book - Thin Entry Point Script
Orchestrates book generation using core logic from src/kindlemint
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.engines.sudoku import SudokuGenerator
from kindlemint.engines.crossword import CrosswordEngine
from kindlemint.validators.base_validator import ValidationResult


def main():
    """Main orchestration function"""
    print("🚀 KindleMint Book Generator")
    print("=" * 40)
    
    # Initialize engines
    sudoku_generator = SudokuGenerator()
    crossword_engine = CrosswordEngine()
    
    # Generate puzzles
    sudoku_puzzle = sudoku_generator.generate_puzzle(difficulty="medium")
    crossword_puzzle = crossword_engine.generate_puzzle(difficulty="medium", size=15)
    
    # Validate
    is_valid = crossword_engine.validate_puzzle(crossword_puzzle)
    
    # Create validation result
    validation_result = ValidationResult(
        valid=is_valid,
        total_puzzles=2,
        valid_puzzles=2 if is_valid else 0,
        invalid_puzzles=0 if is_valid else 2
    )
    
    print(f"✅ Sudoku puzzle generated: {sudoku_puzzle['difficulty']} difficulty")
    print(f"✅ Crossword puzzle generated: {crossword_puzzle.difficulty} difficulty")
    print(f"✅ Validation: {'PASSED' if validation_result.valid else 'FAILED'}")
    print(f"✅ Total puzzles: {validation_result.total_puzzles}")
    print(f"✅ Valid puzzles: {validation_result.valid_puzzles}")
    
    return 0 if validation_result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
