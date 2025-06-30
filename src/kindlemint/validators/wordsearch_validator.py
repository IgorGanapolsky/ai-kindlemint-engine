#!/usr/bin/env python3
"""
Word Search Puzzle Validator Module

This module provides validation functionality for Word Search puzzles,
checking for valid grid structure, word list validation, grid size consistency,
and word placement verification.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from .base_validator import IssueSeverity, PuzzleValidator, ValidationIssue

# Configure logging
logger = logging.getLogger(__name__)


class WordSearchValidator(PuzzleValidator):
    """
    Validator for Word Search puzzles.

    This class validates Word Search puzzles for correctness, checking:
    - Grid structure (typically NxN)
    - Word list validity
    - Word placement in the grid (all words must be findable)
    - Grid content (only uppercase letters)
    """

    # Define directions for word search (8 directions)
    DIRECTIONS = [
        (0, 1),  # right
        (1, 0),  # down
        (1, 1),  # down-right
        (1, -1),  # down-left
        (0, -1),  # left
        (-1, 0),  # up
        (-1, 1),  # up-right
        (-1, -1),  # up-left
    ]

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the Word Search validator.

        Args:
            strict_mode: If True, warnings are treated as errors
        """
        super().__init__(strict_mode)

    def validate_puzzle(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Validate a single Word Search puzzle.

        Args:
            puzzle_data: The puzzle data to validate
            puzzle_id: Identifier for the puzzle

        Returns:
            List of validation issues found in the puzzle
        """
        issues = []

        # Run all checks
        issues.extend(self.check_structure(puzzle_data, puzzle_id))
        issues.extend(self.check_content(puzzle_data, puzzle_id))
        issues.extend(self.check_solvability(puzzle_data, puzzle_id))

        return issues

    def check_structure(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check the structure of a Word Search puzzle.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of structural issues found in the puzzle
        """
        issues = []

        # Check required fields
        required_fields = ["id", "grid", "words", "grid_size"]
        for field in required_fields:
            if field not in puzzle_data:
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Missing required field: {field}",
                        puzzle_id=puzzle_id,
                        recommendation=f"Add the {field} field to the puzzle data",
                    )
                )

        # Check grid structure
        if "grid" in puzzle_data:
            grid = puzzle_data["grid"]

            # Check grid is a list
            if not isinstance(grid, list):
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description="Grid must be a list of lists",
                        puzzle_id=puzzle_id,
                    )
                )
            else:
                # Check grid dimensions
                grid_height = len(grid)
                if grid_height == 0:
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description="Grid is empty",
                            puzzle_id=puzzle_id,
                        )
                    )
                else:
                    grid_width = (
                        len(grid[0])
                        if len(grid) > 0 and isinstance(grid[0], list)
                        else 0
                    )

                    # Check all rows have the same length
                    for i, row in enumerate(grid):
                        if not isinstance(row, list):
                            issues.append(
                                self.create_issue(
                                    severity=IssueSeverity.ERROR,
                                    description=f"Grid row {i} must be a list",
                                    puzzle_id=puzzle_id,
                                    location=f"grid[{i}]",
                                )
                            )
                        elif len(row) != grid_width:
                            issues.append(
                                self.create_issue(
                                    severity=IssueSeverity.ERROR,
                                    description=f"Grid row {i} has inconsistent length: {
                                        len(row)} (expected {grid_width})",
                                    puzzle_id=puzzle_id,
                                    location=f"grid[{i}]",
                                )
                            )

                    # Check grid is square (optional)
                    if grid_height != grid_width:
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.WARNING,
                                description=f"Grid is not square: {
                                    grid_height}x{grid_width}",
                                puzzle_id=puzzle_id,
                            )
                        )

                    # Check grid size matches grid_size field
                    if "grid_size" in puzzle_data:
                        grid_size = puzzle_data["grid_size"]
                        if not isinstance(grid_size, int):
                            issues.append(
                                self.create_issue(
                                    severity=IssueSeverity.ERROR,
                                    description="grid_size must be an integer",
                                    puzzle_id=puzzle_id,
                                )
                            )
                        elif grid_size != grid_height or grid_size != grid_width:
                            issues.append(
                                self.create_issue(
                                    severity=IssueSeverity.ERROR,
                                    description=f"grid_size ({grid_size}) doesn't match actual grid dimensions ({
                                        grid_height}x{grid_width})",
                                    puzzle_id=puzzle_id,
                                    recommendation="Update grid_size to match actual grid dimensions",
                                )
                            )

        # Check words list
        if "words" in puzzle_data:
            words = puzzle_data["words"]

            # Check words is a list
            if not isinstance(words, list):
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description="Words must be a list",
                        puzzle_id=puzzle_id,
                    )
                )
            elif len(words) == 0:
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description="Words list is empty",
                        puzzle_id=puzzle_id,
                        recommendation="Add words to the puzzle",
                    )
                )
            else:
                # Check each word
                for i, word in enumerate(words):
                    if not isinstance(word, str):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Word at index {i} must be a string",
                                puzzle_id=puzzle_id,
                                location=f"words[{i}]",
                            )
                        )
                    elif not word:
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Empty word at index {i}",
                                puzzle_id=puzzle_id,
                                location=f"words[{i}]",
                                recommendation="Remove empty words or add valid words",
                            )
                        )

        return issues

    def check_content(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check the content of a Word Search puzzle.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of content issues found in the puzzle
        """
        issues = []

        # Skip if grid or words are missing or malformed
        if "grid" not in puzzle_data or "words" not in puzzle_data:
            return issues

        grid = puzzle_data["grid"]
        words = puzzle_data["words"]

        if not isinstance(grid, list) or not isinstance(words, list):
            return issues

        # Check grid cells contain only uppercase letters
        for i, row in enumerate(grid):
            if not isinstance(row, list):
                continue

            for j, cell in enumerate(row):
                if not isinstance(cell, str):
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Grid cell at [{i},{j}] must be a string",
                            puzzle_id=puzzle_id,
                            location=f"grid[{i}][{j}]",
                        )
                    )
                elif not cell.isalpha() or not cell.isupper():
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Grid cell at [{i},{
                                j}] must contain an uppercase letter, found: '{cell}'",
                            puzzle_id=puzzle_id,
                            location=f"grid[{i}][{j}]",
                            recommendation="Use only uppercase letters A-Z in the grid",
                        )
                    )

        # Check words are valid
        for i, word in enumerate(words):
            if not isinstance(word, str):
                continue

            if not word.isalpha():
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Word '{word}' at index {
                            i} contains non-letter characters",
                        puzzle_id=puzzle_id,
                        location=f"words[{i}]",
                        recommendation="Words should contain only letters",
                    )
                )

            # Check for duplicate words
            if words.count(word) > 1:
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.WARNING,
                        description=f"Duplicate word: '{word}'",
                        puzzle_id=puzzle_id,
                        location=f"words[{i}]",
                        recommendation="Remove duplicate words",
                    )
                )

            # Check word length
            if len(word) < 3:
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.WARNING,
                        description=f"Word '{word}' is too short (less than 3 letters)",
                        puzzle_id=puzzle_id,
                        location=f"words[{i}]",
                        recommendation="Use words with at least 3 letters",
                    )
                )

            # Check if word is too long for the grid
            if "grid_size" in puzzle_data and isinstance(puzzle_data["grid_size"], int):
                grid_size = puzzle_data["grid_size"]
                if len(word) > grid_size:
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Word '{word}' is too long for the grid (length: {len(word)}, grid size: {
                                grid_size})",
                            puzzle_id=puzzle_id,
                            location=f"words[{i}]",
                            recommendation="Shorten the word or increase grid size",
                        )
                    )

        return issues

    def check_solvability(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check if all words can be found in the Word Search grid.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of solvability issues found in the puzzle
        """
        issues = []

        # Skip if grid or words are missing or malformed
        if "grid" not in puzzle_data or "words" not in puzzle_data:
            return issues

        grid = puzzle_data["grid"]
        words = puzzle_data["words"]

        if not isinstance(grid, list) or not isinstance(words, list):
            return issues

        # Check each word can be found in the grid
        for i, word in enumerate(words):
            if not isinstance(word, str) or not word:
                continue

            # Convert word to uppercase for comparison
            word_upper = word.upper()

            # Try to find the word in the grid
            found = False
            for direction in self.DIRECTIONS:
                if self._find_word_in_grid(grid, word_upper, direction):
                    found = True
                    break

            if not found:
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Word '{word}' cannot be found in the grid",
                        puzzle_id=puzzle_id,
                        location=f"words[{i}]",
                        recommendation="Ensure the word is correctly placed in the grid",
                    )
                )

        return issues

    def _find_word_in_grid(
        self, grid: List[List[str]], word: str, direction: Tuple[int, int]
    ) -> bool:
        """
        Find a word in the grid in a specific direction.

        Args:
            grid: The Word Search grid
            word: The word to find (uppercase)
            direction: Direction to search (row_delta, col_delta)

        Returns:
            True if the word is found, False otherwise
        """
        if not grid or not word:
            return False

        grid_height = len(grid)
        grid_width = len(grid[0]) if grid_height > 0 else 0

        # Try each starting position
        for row in range(grid_height):
            for col in range(grid_width):
                # Check if word can fit from this position in this direction
                row_delta, col_delta = direction
                if (
                    0 <= row + row_delta * (len(word) - 1) < grid_height
                    and 0 <= col + col_delta * (len(word) - 1) < grid_width
                ):

                    # Check if word matches
                    match = True
                    for i in range(len(word)):
                        r = row + row_delta * i
                        c = col + col_delta * i
                        if grid[r][c] != word[i]:
                            match = False
                            break

                    if match:
                        return True

        return False


def validate_wordsearch_content(
    puzzle_dir: Union[str, Path], strict: bool = False
) -> Dict[str, Any]:
    """
    Validate Word Search puzzles in a directory.

    Args:
        puzzle_dir: Directory containing Word Search puzzle metadata files
        strict: Whether to fail validation on warnings (not just errors)

    Returns:
        Dictionary containing validation results
    """
    validator = WordSearchValidator(strict_mode=strict)
    result = validator.validate_directory(puzzle_dir)

    return result.to_dict()


def validate_wordsearch(puzzle_dir: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Legacy validation function for compatibility with existing tests.

    Args:
        puzzle_dir: Directory containing Word Search puzzle metadata files

    Returns:
        List of validation issues found
    """
    result = validate_wordsearch_content(puzzle_dir)
    return [issue for issue in result.get("issues", [])]
