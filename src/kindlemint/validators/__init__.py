#!/usr/bin/env python3
"""
KindleMint Validators Package

This package provides validation tools for puzzle content quality assurance.
Unlike the previous QA validators that only checked PDF structure,
these validators inspect the actual puzzle content for correctness,
uniqueness, and solvability.
"""

from typing import Any, Dict

# Version information
__version__ = "1.0.0"

from .base_validator import PuzzleValidator, ValidationIssue, ValidationResult

# Import validators to make them available from the package
from .crossword_validator import CrosswordValidator, validate_crossword_content
from .sudoku_validator import SudokuValidator, validate_sudoku_content
from .wordsearch_validator import WordSearchValidator, validate_wordsearch_content

# Export main classes and functions
__all__ = [
    "PuzzleValidator",
    "CrosswordValidator",
    "SudokuValidator",
    "WordSearchValidator",
    "validate_crossword_content",
    "validate_sudoku_content",
    "validate_wordsearch_content",
    "ValidationIssue",
    "ValidationResult",
    "validate_puzzle_batch",
]


def validate_puzzle_batch(
    puzzle_dir: str, puzzle_type: str, strict: bool = False
) -> Dict[str, Any]:
    """
    Validate a batch of puzzles of the specified type.

    Args:
        puzzle_dir: Directory containing puzzle metadata files
        puzzle_type: Type of puzzles to validate ('crossword', 'sudoku', 'wordsearch')
        strict: Whether to fail validation on warnings (not just errors)

    Returns:
        Dictionary containing validation results and statistics
    """
    validator_map = {
        "crossword": validate_crossword_content,
        "sudoku": validate_sudoku_content,
        "wordsearch": validate_wordsearch_content,
    }

    if puzzle_type not in validator_map:
        raise ValueError(f"Unsupported puzzle type: {puzzle_type}")

    validator_func = validator_map[puzzle_type]
    results = validator_func(puzzle_dir, strict=strict)

    # Compile statistics
    stats = {
        "puzzle_type": puzzle_type,
        "total_puzzles": results.get("total_puzzles", 0),
        "valid_puzzles": results.get("valid_puzzles", 0),
        "invalid_puzzles": results.get("invalid_puzzles", 0),
        "warnings": results.get("warnings", 0),
        "errors": results.get("errors", 0),
        "validation_passed": results.get("validation_passed", False),
    }

    return {
        "statistics": stats,
        "issues": results.get("issues", []),
        "results": results,
    }
