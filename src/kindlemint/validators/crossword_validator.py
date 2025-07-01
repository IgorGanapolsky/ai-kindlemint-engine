#!/usr/bin/env python3
"""
Crossword Puzzle Validator Module

This module provides validation functionality for crossword puzzles,
checking for empty answers, invalid characters, duplicate clues,
grid structure issues, and solution completeness.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Union

from .base_validator import IssueSeverity, PuzzleValidator, ValidationIssue

# Configure logging
logger = logging.getLogger(__name__)


class CrosswordValidator(PuzzleValidator):
    """
    Validator for crossword puzzles.

    This class validates crossword puzzles for correctness, checking:
    - Empty or invalid answers
    - Duplicate clues
    - Grid structure
    - Solution completeness
    - Answer validity (only letters)
    - Clue numbering consistency
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the crossword validator.

        Args:
            strict_mode: If True, warnings are treated as errors
        """
        super().__init__(strict_mode)

    def validate_puzzle(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Validate a single crossword puzzle.

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
        Check the structure of a crossword puzzle.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of structural issues found in the puzzle
        """
        issues = []

        # Check required fields
        required_fields = ["id", "clues"]
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

        # Check clues structure
        if "clues" in puzzle_data:
            clues = puzzle_data["clues"]

            # Check clues contain across and down sections
            if not isinstance(clues, dict):
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description="Clues must be a dictionary with 'across' and 'down' keys",
                        puzzle_id=puzzle_id,
                    )
                )
            else:
                # Check across and down clues
                for direction in ["across", "down"]:
                    if direction not in clues:
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Missing {direction} clues",
                                puzzle_id=puzzle_id,
                                recommendation=f"Add {direction} clues to the puzzle",
                            )
                        )
                    elif not isinstance(clues[direction], list):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"{
                                    direction.capitalize()} clues must be a list",
                                puzzle_id=puzzle_id,
                            )
                        )
                    else:
                        # Check each clue format
                        for i, clue in enumerate(clues[direction]):
                            if not isinstance(clue, list):
                                issues.append(
                                    self.create_issue(
                                        severity=IssueSeverity.ERROR,
                                        description=f"Invalid clue format at {
                                            direction} index {i}",
                                        puzzle_id=puzzle_id,
                                        location=f"{direction}[{i}]",
                                        recommendation="Clue should be a list: [number, text, answer]",
                                    )
                                )
                            elif len(clue) < 2:
                                issues.append(
                                    self.create_issue(
                                        severity=IssueSeverity.ERROR,
                                        description=f"Incomplete clue at {
                                            direction} index {i}",
                                        puzzle_id=puzzle_id,
                                        location=f"{direction}[{i}]",
                                        recommendation="Clue should have at least [number, text]",
                                    )
                                )

        # Check clue positions if present
        if "clue_positions" in puzzle_data:
            clue_positions = puzzle_data["clue_positions"]
            if not isinstance(clue_positions, dict):
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description="Clue positions must be a dictionary",
                        puzzle_id=puzzle_id,
                    )
                )

        return issues

    def check_content(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check the content of a crossword puzzle.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of content issues found in the puzzle
        """
        issues = []

        # Skip if clues are missing or malformed
        if "clues" not in puzzle_data or not isinstance(puzzle_data["clues"], dict):
            return issues

        clues = puzzle_data["clues"]

        # Check for empty or invalid answers
        for direction in ["across", "down"]:
            if direction not in clues or not isinstance(clues[direction], list):
                continue

            # Track clue texts to check for duplicates
            clue_texts = set()
            clue_numbers = set()

            for i, clue in enumerate(clues[direction]):
                if not isinstance(clue, list) or len(clue) < 2:
                    continue

                # Check clue number
                clue_number = clue[0]
                if not isinstance(clue_number, int):
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Clue number must be an integer",
                            puzzle_id=puzzle_id,
                            location=f"{direction}[{i}]",
                        )
                    )
                else:
                    # Check for duplicate clue numbers within the same direction
                    if clue_number in clue_numbers:
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Duplicate clue number {
                                    clue_number} in {direction} clues",
                                puzzle_id=puzzle_id,
                                location=f"{direction}[{i}]",
                            )
                        )
                    clue_numbers.add(clue_number)

                # Check clue text
                clue_text = clue[1]
                if not clue_text or not isinstance(clue_text, str):
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Empty or invalid clue text",
                            puzzle_id=puzzle_id,
                            location=f"{direction}[{i}]",
                        )
                    )
                else:
                    # Check for duplicate clue texts
                    if clue_text in clue_texts:
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.WARNING,
                                description=f"Duplicate clue text: '{clue_text}'",
                                puzzle_id=puzzle_id,
                                location=f"{direction}[{i}]",
                            )
                        )
                    clue_texts.add(clue_text)

                # Check answer if present
                if len(clue) >= 3:
                    answer = clue[2]
                    if answer is None or answer == "":
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Empty answer for clue: '{clue_text}'",
                                puzzle_id=puzzle_id,
                                location=f"{direction}[{i}]",
                                recommendation="Provide a valid answer for the clue",
                            )
                        )
                    elif not isinstance(answer, str):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Answer must be a string",
                                puzzle_id=puzzle_id,
                                location=f"{direction}[{i}]",
                            )
                        )
                    elif not answer.isalpha():
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Answer contains non-letters: '{answer}'",
                                puzzle_id=puzzle_id,
                                location=f"{direction}[{i}]",
                                recommendation="Answers should contain only letters A-Z",
                            )
                        )

        # Check clue numbering consistency with positions
        if "clue_positions" in puzzle_data and isinstance(
            puzzle_data["clue_positions"], dict
        ):
            clue_positions = puzzle_data["clue_positions"]
            position_numbers = set(
                int(pos_num)
                for pos_num in clue_positions.values()
                if isinstance(pos_num, (int, str)) and str(pos_num).isdigit()
            )

            # Collect all clue numbers from across and down
            all_clue_numbers = set()
            for direction in ["across", "down"]:
                if direction in clues and isinstance(clues[direction], list):
                    for clue in clues[direction]:
                        if (
                            isinstance(clue, list)
                            and len(clue) >= 1
                            and isinstance(clue[0], int)
                        ):
                            all_clue_numbers.add(clue[0])

            # Check for numbers in positions but not in clues
            for pos_num in position_numbers:
                if pos_num not in all_clue_numbers:
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Clue number {
                                pos_num} in positions but not in clues",
                            puzzle_id=puzzle_id,
                            recommendation="Add corresponding clue or remove position",
                        )
                    )

            # Check for numbers in clues but not in positions
            for clue_num in all_clue_numbers:
                if clue_num not in position_numbers:
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.WARNING,
                            description=f"Clue number {
                                clue_num} in clues but not in positions",
                            puzzle_id=puzzle_id,
                            recommendation="Add corresponding position or remove clue",
                        )
                    )

        return issues

    def check_solvability(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check if a crossword puzzle is solvable.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of solvability issues found in the puzzle
        """
        issues = []

        # Check if grid is present
        if "grid" in puzzle_data:
            grid = puzzle_data["grid"]

            # Check grid is a list of lists
            if not isinstance(grid, list) or not all(
                isinstance(row, list) for row in grid
            ):
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
                    grid_width = len(grid[0])

                    # Check all rows have the same length
                    if not all(len(row) == grid_width for row in grid):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description="Grid rows have inconsistent lengths",
                                puzzle_id=puzzle_id,
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

                    # Check grid cells contain valid values
                    for i, row in enumerate(grid):
                        for j, cell in enumerate(row):
                            if not isinstance(cell, str):
                                issues.append(
                                    self.create_issue(
                                        severity=IssueSeverity.ERROR,
                                        description=f"Grid cell at[{
                                            i}, {j}] is not a string",
                                        puzzle_id=puzzle_id,
                                        location=f"grid[{i}][{j}]",
                                    )
                                )
                            elif cell not in ["", "#"] and not cell.isalpha():
                                issues.append(
                                    self.create_issue(
                                        severity=IssueSeverity.ERROR,
                                        description=f"Invalid grid cell value at[{
                                            i}, {j}]: '{cell}'",
                                        puzzle_id=puzzle_id,
                                        location=f"grid[{i}][{j}]",
                                        recommendation="Cell should be empty, '#', or a letter",
                                    )
                                )

        # Check if solution grid is present
        if "solution" in puzzle_data:
            solution = puzzle_data["solution"]

            # Check solution is a list of lists
            if not isinstance(solution, list) or not all(
                isinstance(row, list) for row in solution
            ):
                issues.append(
                    self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description="Solution must be a list of lists",
                        puzzle_id=puzzle_id,
                    )
                )
            else:
                # Check solution dimensions
                solution_height = len(solution)
                if solution_height == 0:
                    issues.append(
                        self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description="Solution is empty",
                            puzzle_id=puzzle_id,
                        )
                    )
                else:
                    solution_width = len(solution[0])

                    # Check all rows have the same length
                    if not all(len(row) == solution_width for row in solution):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description="Solution rows have inconsistent lengths",
                                puzzle_id=puzzle_id,
                            )
                        )

                    # Check solution cells contain valid values
                    for i, row in enumerate(solution):
                        for j, cell in enumerate(row):
                            if not isinstance(cell, str):
                                issues.append(
                                    self.create_issue(
                                        severity=IssueSeverity.ERROR,
                                        description=f"Solution cell at[{
                                            i}, {j}] is not a string",
                                        puzzle_id=puzzle_id,
                                        location=f"solution[{i}][{j}]",
                                    )
                                )
                            elif cell != "#" and not cell.isalpha():
                                issues.append(
                                    self.create_issue(
                                        severity=IssueSeverity.ERROR,
                                        description=f"Invalid solution cell value at[{
                                            i}, {j}]: '{cell}'",
                                        puzzle_id=puzzle_id,
                                        location=f"solution[{i}][{j}]",
                                        recommendation="Cell should be '#' or a letter",
                                    )
                                )

                # Check solution completeness
                if "grid" in puzzle_data and isinstance(puzzle_data["grid"], list):
                    grid = puzzle_data["grid"]

                    # Check grid and solution have same dimensions
                    if len(grid) != len(solution):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description="Grid and solution have different heights",
                                puzzle_id=puzzle_id,
                            )
                        )
                    elif len(grid) > 0 and len(grid[0]) != len(solution[0]):
                        issues.append(
                            self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description="Grid and solution have different widths",
                                puzzle_id=puzzle_id,
                            )
                        )
                    else:
                        # Check solution is complete (all non-block cells filled)
                        for i in range(len(grid)):
                            for j in range(len(grid[0])):
                                if i < len(solution) and j < len(solution[0]):
                                    if grid[i][j] != "#" and solution[i][j] == "":
                                        issues.append(
                                            self.create_issue(
                                                severity=IssueSeverity.ERROR,
                                                description=f"Empty solution cell at[{
                                                    i}, {j}]",
                                                puzzle_id=puzzle_id,
                                                location=f"solution[{i}][{j}]",
                                                recommendation="Fill in all solution cells",
                                            )
                                        )

        return issues


def validate_crossword_content(
    puzzle_dir: Union[str, Path], strict: bool = False
) -> Dict[str, Any]:
    """
    Validate crossword puzzles in a directory.

    Args:
        puzzle_dir: Directory containing crossword puzzle metadata files
        strict: Whether to fail validation on warnings (not just errors)

    Returns:
        Dictionary containing validation results
    """
    validator = CrosswordValidator(strict_mode=strict)
    result = validator.validate_directory(puzzle_dir)

    return result.to_dict()


def validate_crossword(puzzle_dir: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Legacy validation function for compatibility with existing tests.

    Args:
        puzzle_dir: Directory containing crossword puzzle metadata files

    Returns:
        List of validation issues found
    """
    result = validate_crossword_content(puzzle_dir)
    return [issue for issue in result.get("issues", [])]
