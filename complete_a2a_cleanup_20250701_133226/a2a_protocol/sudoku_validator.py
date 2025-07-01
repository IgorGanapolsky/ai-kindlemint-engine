#!/usr/bin/env python3
"""
Simple Sudoku Validator for A2A demo
"""

from typing import List, Tuple


class SudokuValidator:
    """Basic Sudoku validation logic"""

    def validate_solution(self, grid: List[List[int]]) -> Tuple[bool, List[str]]:
        """
        Validates whether a given 9x9 grid is a correct and complete Sudoku solution.
        
        Checks that the grid has the correct dimensions, and that each row, column, and 3x3 box contains all numbers from 1 to 9 exactly once. Returns a tuple indicating validity and a list of error messages describing any issues found.
        
        Parameters:
            grid (List[List[int]]): A 9x9 Sudoku grid to validate.
        
        Returns:
            Tuple[bool, List[str]]: A tuple where the first element is True if the solution is valid, False otherwise; the second element is a list of error messages.
        """
        errors = []

        # Check dimensions
        if len(grid) != 9:
            errors.append("Grid must have 9 rows")
            return False, errors

        for i, row in enumerate(grid):
            if len(row) != 9:
                errors.append(f"Row {i} must have 9 columns")
                return False, errors

        # Check rows
        for i in range(9):
            row = grid[i]
            if not self._is_valid_group(row):
                errors.append(
                    f"Row {i + 1} contains duplicates or invalid numbers")

        # Check columns
        for j in range(9):
            col = [grid[i][j] for i in range(9)]
            if not self._is_valid_group(col):
                errors.append(
                    f"Column {j + 1} contains duplicates or invalid numbers")

        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(grid[box_row * 3 + i][box_col * 3 + j])
                if not self._is_valid_group(box):
                    errors.append(
                        f"Box({box_row + 1}, {box_col +
                                              1}) contains duplicates or invalid numbers"
                    )

        return len(errors) == 0, errors

    def validate_puzzle_solution_match(
        self, puzzle: List[List[int]], solution: List[List[int]]
    ) -> Tuple[bool, List[str]]:
        """
        Checks whether all clues in the given Sudoku puzzle match the corresponding values in the provided solution.
        
        Parameters:
            puzzle (List[List[int]]): The original Sudoku puzzle grid, where non-zero values are clues.
            solution (List[List[int]]): The proposed solution grid to be checked against the puzzle clues.
        
        Returns:
            Tuple[bool, List[str]]: A tuple containing a boolean indicating if all clues match the solution, and a list of error messages for any mismatches.
        """
        errors = []

        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:  # It's a clue
                    if puzzle[i][j] != solution[i][j]:
                        errors.append(
                            f"Clue at position({i + 1}, {j +
                                                         1}) doesn't match solution: "
                            f"puzzle has {puzzle[i][j]}, solution has {solution[i][j]}"
                        )

        return len(errors) == 0, errors

    def _is_valid_group(self, group: List[int]) -> bool:
        """Check if a group (row, column, or box) contains valid unique numbers"""
        # Should contain exactly numbers 1-9
        return sorted(group) == list(range(1, 10))
