#!/usr/bin/env python3
"""
Sudoku Puzzle Validator Module

This module provides validation functionality for Sudoku puzzles,
checking for valid grid structure, unique solutions, proper clue counts,
and grid validity according to Sudoku rules.
"""

import json
import logging
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .base_validator import IssueSeverity, PuzzleValidator, ValidationIssue, ValidationResult

# Configure logging
logger = logging.getLogger(__name__)

class SudokuValidator(PuzzleValidator):
    """
    Validator for Sudoku puzzles.
    
    This class validates Sudoku puzzles for correctness, checking:
    - Grid structure (9x9)
    - Valid clue placement
    - Unique solution
    - Appropriate difficulty (clue count)
    - Solution correctness
    """
    
    # Define expected clue counts for different difficulty levels
    DIFFICULTY_CLUE_RANGES = {
        "easy": {"min": 32, "max": 48, "target": 40},
        "medium": {"min": 25, "max": 36, "target": 30},
        "hard": {"min": 20, "max": 28, "target": 24},
        "expert": {"min": 17, "max": 26, "target": 20}
    }
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the Sudoku validator.
        
        Args:
            strict_mode: If True, warnings are treated as errors
        """
        super().__init__(strict_mode)
    
    def validate_puzzle(self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]) -> List[ValidationIssue]:
        """
        Validate a single Sudoku puzzle.
        
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
    
    def check_structure(self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]) -> List[ValidationIssue]:
        """
        Check the structure of a Sudoku puzzle.
        
        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle
            
        Returns:
            List of structural issues found in the puzzle
        """
        issues = []
        
        # Check required fields
        required_fields = ["grid", "solution", "difficulty"]
        for field in required_fields:
            if field not in puzzle_data:
                issues.append(self.create_issue(
                    severity=IssueSeverity.ERROR,
                    description=f"Missing required field: {field}",
                    puzzle_id=puzzle_id,
                    recommendation=f"Add the {field} field to the puzzle data"
                ))
        
        # Check grid structure
        if "grid" in puzzle_data:
            grid = puzzle_data["grid"]
            
            # Check grid is a list
            if not isinstance(grid, list):
                issues.append(self.create_issue(
                    severity=IssueSeverity.ERROR,
                    description="Grid must be a list of lists",
                    puzzle_id=puzzle_id
                ))
            else:
                # Check grid dimensions
                if len(grid) != 9:
                    issues.append(self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Grid must have 9 rows, found {len(grid)}",
                        puzzle_id=puzzle_id
                    ))
                
                # Check each row
                for i, row in enumerate(grid):
                    if not isinstance(row, list):
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Row {i} must be a list",
                            puzzle_id=puzzle_id,
                            location=f"grid[{i}]"
                        ))
                    elif len(row) != 9:
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Row {i} must have 9 cells, found {len(row)}",
                            puzzle_id=puzzle_id,
                            location=f"grid[{i}]"
                        ))
                    
                    # Check each cell
                    for j, cell in enumerate(row):
                        if not isinstance(cell, int):
                            issues.append(self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Cell at [{i},{j}] must be an integer",
                                puzzle_id=puzzle_id,
                                location=f"grid[{i}][{j}]"
                            ))
                        elif cell < 0 or cell > 9:
                            issues.append(self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Cell at [{i},{j}] must be between 0-9, found {cell}",
                                puzzle_id=puzzle_id,
                                location=f"grid[{i}][{j}]",
                                recommendation="Use 0 for empty cells, 1-9 for clues"
                            ))
        
        # Check solution structure
        if "solution" in puzzle_data:
            solution = puzzle_data["solution"]
            
            # Check solution is a list
            if not isinstance(solution, list):
                issues.append(self.create_issue(
                    severity=IssueSeverity.ERROR,
                    description="Solution must be a list of lists",
                    puzzle_id=puzzle_id
                ))
            else:
                # Check solution dimensions
                if len(solution) != 9:
                    issues.append(self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Solution must have 9 rows, found {len(solution)}",
                        puzzle_id=puzzle_id
                    ))
                
                # Check each row
                for i, row in enumerate(solution):
                    if not isinstance(row, list):
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Solution row {i} must be a list",
                            puzzle_id=puzzle_id,
                            location=f"solution[{i}]"
                        ))
                    elif len(row) != 9:
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Solution row {i} must have 9 cells, found {len(row)}",
                            puzzle_id=puzzle_id,
                            location=f"solution[{i}]"
                        ))
                    
                    # Check each cell
                    for j, cell in enumerate(row):
                        if not isinstance(cell, int):
                            issues.append(self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Solution cell at [{i},{j}] must be an integer",
                                puzzle_id=puzzle_id,
                                location=f"solution[{i}][{j}]"
                            ))
                        elif cell < 1 or cell > 9:
                            issues.append(self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Solution cell at [{i},{j}] must be between 1-9, found {cell}",
                                puzzle_id=puzzle_id,
                                location=f"solution[{i}][{j}]"
                            ))
        
        # Check difficulty
        if "difficulty" in puzzle_data:
            difficulty = puzzle_data["difficulty"]
            if not isinstance(difficulty, str):
                issues.append(self.create_issue(
                    severity=IssueSeverity.ERROR,
                    description="Difficulty must be a string",
                    puzzle_id=puzzle_id
                ))
            elif difficulty.lower() not in self.DIFFICULTY_CLUE_RANGES:
                issues.append(self.create_issue(
                    severity=IssueSeverity.WARNING,
                    description=f"Unknown difficulty: {difficulty}",
                    puzzle_id=puzzle_id,
                    recommendation=f"Use one of: {', '.join(self.DIFFICULTY_CLUE_RANGES.keys())}"
                ))
        
        return issues
    
    def check_content(self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]) -> List[ValidationIssue]:
        """
        Check the content of a Sudoku puzzle.
        
        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle
            
        Returns:
            List of content issues found in the puzzle
        """
        issues = []
        
        # Skip if grid or solution are missing or malformed
        if "grid" not in puzzle_data or "solution" not in puzzle_data:
            return issues
        
        grid = puzzle_data["grid"]
        solution = puzzle_data["solution"]
        
        if not isinstance(grid, list) or not isinstance(solution, list):
            return issues
        
        # Check grid validity (no rule violations in initial clues)
        if len(grid) == 9 and all(len(row) == 9 for row in grid):
            # Check rows for duplicates
            for i, row in enumerate(grid):
                seen = set()
                for j, cell in enumerate(row):
                    if cell != 0 and cell in seen:
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Duplicate value {cell} in row {i}",
                            puzzle_id=puzzle_id,
                            location=f"grid[{i}][{j}]",
                            recommendation="Remove duplicate or correct the value"
                        ))
                    if cell != 0:
                        seen.add(cell)
            
            # Check columns for duplicates
            for j in range(9):
                seen = set()
                for i in range(9):
                    cell = grid[i][j]
                    if cell != 0 and cell in seen:
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"Duplicate value {cell} in column {j}",
                            puzzle_id=puzzle_id,
                            location=f"grid[{i}][{j}]",
                            recommendation="Remove duplicate or correct the value"
                        ))
                    if cell != 0:
                        seen.add(cell)
            
            # Check 3x3 boxes for duplicates
            for box_i in range(3):
                for box_j in range(3):
                    seen = set()
                    for i in range(3):
                        for j in range(3):
                            cell = grid[box_i * 3 + i][box_j * 3 + j]
                            if cell != 0 and cell in seen:
                                issues.append(self.create_issue(
                                    severity=IssueSeverity.ERROR,
                                    description=f"Duplicate value {cell} in 3x3 box at [{box_i},{box_j}]",
                                    puzzle_id=puzzle_id,
                                    location=f"grid[{box_i * 3 + i}][{box_j * 3 + j}]",
                                    recommendation="Remove duplicate or correct the value"
                                ))
                            if cell != 0:
                                seen.add(cell)
        
        # Check solution validity
        if len(solution) == 9 and all(len(row) == 9 for row in solution):
            # Check rows for completeness
            for i, row in enumerate(solution):
                if set(row) != set(range(1, 10)):
                    issues.append(self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Row {i} in solution is not complete or has duplicates",
                        puzzle_id=puzzle_id,
                        location=f"solution[{i}]",
                        recommendation="Solution rows must contain all digits 1-9 exactly once"
                    ))
            
            # Check columns for completeness
            for j in range(9):
                column = [solution[i][j] for i in range(9)]
                if set(column) != set(range(1, 10)):
                    issues.append(self.create_issue(
                        severity=IssueSeverity.ERROR,
                        description=f"Column {j} in solution is not complete or has duplicates",
                        puzzle_id=puzzle_id,
                        location=f"solution[:][{j}]",
                        recommendation="Solution columns must contain all digits 1-9 exactly once"
                    ))
            
            # Check 3x3 boxes for completeness
            for box_i in range(3):
                for box_j in range(3):
                    box = [solution[box_i * 3 + i][box_j * 3 + j] for i in range(3) for j in range(3)]
                    if set(box) != set(range(1, 10)):
                        issues.append(self.create_issue(
                            severity=IssueSeverity.ERROR,
                            description=f"3x3 box at [{box_i},{box_j}] in solution is not complete or has duplicates",
                            puzzle_id=puzzle_id,
                            recommendation="Solution boxes must contain all digits 1-9 exactly once"
                        ))
        
        # Check if grid matches solution (all clues must match solution)
        if len(grid) == 9 and len(solution) == 9:
            for i in range(9):
                for j in range(9):
                    if i < len(grid) and j < len(grid[i]) and i < len(solution) and j < len(solution[i]):
                        if grid[i][j] != 0 and grid[i][j] != solution[i][j]:
                            issues.append(self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Grid clue at [{i},{j}] doesn't match solution: {grid[i][j]} vs {solution[i][j]}",
                                puzzle_id=puzzle_id,
                                location=f"grid[{i}][{j}]",
                                recommendation="Ensure all clues match the solution"
                            ))
        
        # Check clue count for difficulty
        if "difficulty" in puzzle_data and isinstance(puzzle_data["difficulty"], str):
            difficulty = puzzle_data["difficulty"].lower()
            if difficulty in self.DIFFICULTY_CLUE_RANGES:
                clue_count = sum(1 for row in grid for cell in row if cell != 0)
                expected_range = self.DIFFICULTY_CLUE_RANGES[difficulty]
                
                if clue_count < expected_range["min"]:
                    issues.append(self.create_issue(
                        severity=IssueSeverity.WARNING,
                        description=f"Too few clues for {difficulty} difficulty: {clue_count} (min: {expected_range['min']})",
                        puzzle_id=puzzle_id,
                        recommendation=f"Add more clues or change difficulty level"
                    ))
                elif clue_count > expected_range["max"]:
                    issues.append(self.create_issue(
                        severity=IssueSeverity.WARNING,
                        description=f"Too many clues for {difficulty} difficulty: {clue_count} (max: {expected_range['max']})",
                        puzzle_id=puzzle_id,
                        recommendation=f"Remove some clues or change difficulty level"
                    ))
        
        return issues
    
    def check_solvability(self, puzzle_data: Dict[str, Any], puzzle_id: Union[int, str]) -> List[ValidationIssue]:
        """
        Check if a Sudoku puzzle is solvable and has a unique solution.
        
        Args:
            puzzle_data: The puzzle data to check
            puzzle_id: Identifier for the puzzle
            
        Returns:
            List of solvability issues found in the puzzle
        """
        issues = []
        
        # Skip if grid is missing or malformed
        if "grid" not in puzzle_data or not isinstance(puzzle_data["grid"], list):
            return issues
        
        grid = puzzle_data["grid"]
        if len(grid) != 9 or not all(len(row) == 9 for row in grid):
            return issues
        
        # Create a copy of the grid for solving
        grid_copy = copy.deepcopy(grid)
        
        # Check if puzzle is solvable
        solution_count = self._count_solutions(grid_copy)
        
        if solution_count == 0:
            issues.append(self.create_issue(
                severity=IssueSeverity.ERROR,
                description="Puzzle has no solution",
                puzzle_id=puzzle_id,
                recommendation="Fix the puzzle to ensure it has a valid solution"
            ))
        elif solution_count > 1:
            issues.append(self.create_issue(
                severity=IssueSeverity.ERROR,
                description="Puzzle has multiple solutions",
                puzzle_id=puzzle_id,
                recommendation="Add more clues to ensure a unique solution"
            ))
        
        # If solution is provided, check if it matches our solution
        if solution_count == 1 and "solution" in puzzle_data and isinstance(puzzle_data["solution"], list):
            provided_solution = puzzle_data["solution"]
            
            # Solve the puzzle
            solved_grid = copy.deepcopy(grid)
            self._solve_grid(solved_grid)
            
            # Compare solutions
            if len(provided_solution) == 9 and all(len(row) == 9 for row in provided_solution):
                for i in range(9):
                    for j in range(9):
                        if solved_grid[i][j] != provided_solution[i][j]:
                            issues.append(self.create_issue(
                                severity=IssueSeverity.ERROR,
                                description=f"Provided solution doesn't match computed solution at [{i},{j}]",
                                puzzle_id=puzzle_id,
                                location=f"solution[{i}][{j}]",
                                recommendation="Correct the solution or the puzzle"
                            ))
        
        return issues
    
    def _is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Check if placing num at grid[row][col] is valid.
        
        Args:
            grid: The Sudoku grid
            row: Row index
            col: Column index
            num: Number to check
            
        Returns:
            True if the placement is valid, False otherwise
        """
        # Check row
        for x in range(9):
            if grid[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if grid[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def _solve_grid(self, grid: List[List[int]]) -> bool:
        """
        Solve a Sudoku grid using backtracking.
        
        Args:
            grid: The Sudoku grid to solve
            
        Returns:
            True if the grid was solved, False otherwise
        """
        # Find an empty cell
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    # Try each number
                    for num in range(1, 10):
                        if self._is_valid(grid, i, j, num):
                            grid[i][j] = num
                            
                            # Recursively solve the rest
                            if self._solve_grid(grid):
                                return True
                            
                            # If we get here, this num didn't work
                            grid[i][j] = 0
                    
                    # If no number works, backtrack
                    return False
        
        # If we get here, the grid is filled (solved)
        return True
    
    def _count_solutions(self, grid: List[List[int]], limit: int = 2) -> int:
        """
        Count the number of solutions for a Sudoku puzzle.
        
        Args:
            grid: The Sudoku grid
            limit: Maximum number of solutions to find before stopping
            
        Returns:
            Number of solutions found (up to limit)
        """
        solutions = [0]
        
        def solve_and_count(grid: List[List[int]]) -> None:
            # Find an empty cell
            found_empty = False
            for i in range(9):
                for j in range(9):
                    if grid[i][j] == 0:
                        found_empty = True
                        # Try each number
                        for num in range(1, 10):
                            if self._is_valid(grid, i, j, num):
                                grid[i][j] = num
                                solve_and_count(grid)
                                grid[i][j] = 0
                                
                                # Stop if we've reached the limit
                                if solutions[0] >= limit:
                                    return
                        return
            
            # If no empty cells, we found a solution
            if not found_empty:
                solutions[0] += 1
        
        # Start the recursive counting
        solve_and_count(grid)
        return solutions[0]


def validate_sudoku_content(
    puzzle_dir: Union[str, Path], 
    strict: bool = False
) -> Dict[str, Any]:
    """
    Validate Sudoku puzzles in a directory.
    
    Args:
        puzzle_dir: Directory containing Sudoku puzzle metadata files
        strict: Whether to fail validation on warnings (not just errors)
        
    Returns:
        Dictionary containing validation results
    """
    validator = SudokuValidator(strict_mode=strict)
    result = validator.validate_directory(puzzle_dir)
    
    return result.to_dict()


def validate_sudoku(puzzle_dir: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Legacy validation function for compatibility with existing tests.
    
    Args:
        puzzle_dir: Directory containing Sudoku puzzle metadata files
        
    Returns:
        List of validation issues found
    """
    result = validate_sudoku_content(puzzle_dir)
    return [issue for issue in result.get("issues", [])]
