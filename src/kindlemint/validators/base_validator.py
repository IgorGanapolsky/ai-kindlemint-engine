#!/usr/bin/env python3
"""
Base Validator Module

This module provides the base classes and data structures for puzzle validation.
It defines the common interface and utilities that all specific validators
(crossword, sudoku, wordsearch) will implement.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class IssueSeverity(str, Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """
    Represents an issue found during puzzle validation.

    Attributes:
        severity: The severity level of the issue (error, warning, info)
        description: Detailed description of the issue
        puzzle_id: Identifier of the puzzle with the issue
        location: Location within the puzzle where the issue was found
        recommendation: Suggested fix for the issue
    """

    severity: IssueSeverity
    description: str
    puzzle_id: Union[int, str]
    location: Optional[str] = None
    recommendation: Optional[str] = None

    def is_error(self) -> bool:
        """Check if this issue is an error."""
        return self.severity == IssueSeverity.ERROR

    def is_warning(self) -> bool:
        """Check if this issue is a warning."""
        return self.severity == IssueSeverity.WARNING

    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary for serialization."""
        return {
            "severity": self.severity.value,
            "description": self.description,
            "puzzle_id": self.puzzle_id,
            "location": self.location,
            "recommendation": self.recommendation,
        }


@dataclass
class ValidationResult:
    """
    Represents the result of a validation operation.

    Attributes:
        valid: Whether the validation passed (True) or failed (False)
        issues: List of validation issues found
        total_puzzles: Total number of puzzles validated
        valid_puzzles: Number of puzzles that passed validation
        invalid_puzzles: Number of puzzles that failed validation
        metadata: Additional metadata about the validation
    """

    valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    total_puzzles: int = 0
    valid_puzzles: int = 0
    invalid_puzzles: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(issue.is_error() for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warning-level issues."""
        return any(issue.is_warning() for issue in self.issues)

    @property
    def error_count(self) -> int:
        """Get the number of error-level issues."""
        return sum(1 for issue in self.issues if issue.is_error())

    @property
    def warning_count(self) -> int:
        """Get the number of warning-level issues."""
        return sum(1 for issue in self.issues if issue.is_warning())

    def add_issue(self, issue: ValidationIssue) -> None:
        """
        Add an issue to the validation result.

        Args:
            issue: The validation issue to add
        """
        self.issues.append(issue)
        if issue.is_error():
            self.valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation result to a dictionary for serialization."""
        return {
            "validation_passed": self.valid,
            "total_puzzles": self.total_puzzles,
            "valid_puzzles": self.valid_puzzles,
            "invalid_puzzles": self.invalid_puzzles,
            "errors": self.error_count,
            "warnings": self.warning_count,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the validation result to a JSON string.

        Args:
            indent: Number of spaces for indentation in the JSON output

        Returns:
            JSON string representation of the validation result
        """
        return json.dumps(self.to_dict(), indent=indent)


class PuzzleValidator(ABC):
    """
    Abstract base class for puzzle validators.

    This class defines the common interface that all puzzle validators must implement.
    Specific validators (CrosswordValidator, SudokuValidator, etc.) will inherit from
    this class and provide puzzle-specific validation logic.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, warnings are treated as errors
        """
        self.strict_mode = strict_mode
        self.result = ValidationResult()

    @abstractmethod
    def validate_puzzle(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Validate a single puzzle.

        Args:
            puzzle_data: The puzzle data to validate
            puzzle_id: Identifier for the puzzle

        Returns:
            List of validation issues found in the puzzle
        """
        pass

    @abstractmethod
    def check_structure(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check the structure of a puzzle.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of structural issues found in the puzzle
        """
        pass

    @abstractmethod
    def check_content(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check the content of a puzzle.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of content issues found in the puzzle
        """
        pass

    @abstractmethod
    def check_solvability(
        self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]
    ) -> List[ValidationIssue]:
        """
        Check if a puzzle is solvable.

        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle

        Returns:
            List of solvability issues found in the puzzle
        """
        pass

    def validate_directory(self, directory_path: Union[str, Path]) -> ValidationResult:
        """
        Validate all puzzles in a directory.

        Args:
            directory_path: Path to the directory containing puzzle files

        Returns:
            ValidationResult containing the validation results
        """
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory path: {directory}")

        # Reset the validation result
        self.result = ValidationResult()

        # Find all JSON files in the directory
        puzzle_files = list(directory.glob("*.json"))
        self.result.total_puzzles = len(puzzle_files)

        # Validate each puzzle
        for puzzle_file in puzzle_files:
            try:
                with open(puzzle_file, "r") as f:
                    puzzle_data = json.load(f)

                puzzle_id = puzzle_data.get("id", puzzle_file.stem)
                issues = self.validate_puzzle(puzzle_data, puzzle_id)

                # Add all issues to the result
                for issue in issues:
                    self.result.add_issue(issue)

                # Update puzzle counts
                has_errors = any(issue.is_error() for issue in issues)
                has_warnings = any(issue.is_warning() for issue in issues)

                if has_errors or (self.strict_mode and has_warnings):
                    self.result.invalid_puzzles += 1
                else:
                    self.result.valid_puzzles += 1

            except Exception as e:
                logger.error(f"Error validating puzzle {puzzle_file}: {e}")
                error_issue = ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    description=f"Failed to validate puzzle: {str(e)}",
                    puzzle_id=puzzle_file.stem,
                    recommendation="Check file format and content",
                )
                self.result.add_issue(error_issue)
                self.result.invalid_puzzles += 1

        return self.result

    def create_issue(
        self,
        severity: IssueSeverity,
        description: str,
        puzzle_id: Union[int, str],
        location: Optional[str] = None,
        recommendation: Optional[str] = None,
    ) -> ValidationIssue:
        """
        Create a validation issue.

        Args:
            severity: The severity level of the issue
            description: Detailed description of the issue
            puzzle_id: Identifier of the puzzle with the issue
            location: Location within the puzzle where the issue was found
            recommendation: Suggested fix for the issue

        Returns:
            A ValidationIssue instance
        """
        return ValidationIssue(
            severity=severity,
            description=description,
            puzzle_id=puzzle_id,
            location=location,
            recommendation=recommendation,
        )
