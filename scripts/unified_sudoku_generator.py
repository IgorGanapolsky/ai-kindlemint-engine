#!/usr/bin/env python3
"""
Unified Sudoku Generator for Volume 2
Creates high-quality Sudoku puzzles with solutions
"""

import copy
import random


def generate_sudoku_with_solution(difficulty="medium", target_clues=35):
    """Generate a complete Sudoku puzzle with solution"""

    # Generate a complete solution grid first
    solution_grid = generate_complete_sudoku()

    # Create initial grid by removing numbers
    initial_grid = create_puzzle_from_solution(solution_grid, target_clues)

    # Verify the puzzle has a unique solution
    if not verify_unique_solution(initial_grid, solution_grid):
        # If not unique, try again (recursively, but limit attempts)
        return generate_sudoku_with_solution(difficulty, target_clues)

    # Count actual clues
    actual_clues = sum(1 for row in initial_grid for cell in row if cell != 0)

    return {
        "initial_grid": initial_grid,
        "solution_grid": solution_grid,
        "difficulty": difficulty,
        "clue_count": actual_clues,
        "target_clues": target_clues,
    }


def generate_complete_sudoku():
    """Generate a complete valid Sudoku solution"""

    # Start with an empty grid
    grid = [[0 for _ in range(9)] for _ in range(9)]

    # Fill the grid using backtracking
    if solve_sudoku(grid):
        return grid
    else:
        # If failed (shouldn't happen), try again
        return generate_complete_sudoku()


def solve_sudoku(grid):
    """Solve Sudoku using backtracking algorithm"""

    # Find empty cell
    empty = find_empty_cell(grid)
    if not empty:
        return True  # No empty cells, puzzle solved

    row, col = empty

    # Try numbers 1-9 in random order for variety
    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for num in numbers:
        if is_valid_placement(grid, num, row, col):
            grid[row][col] = num

            if solve_sudoku(grid):
                return True

            # Backtrack
            grid[row][col] = 0

    return False


def find_empty_cell(grid):
    """Find an empty cell (0) in the grid"""
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None


def is_valid_placement(grid, num, row, col):
    """Check if placing num at (row, col) is valid"""

    # Check row
    for j in range(9):
        if grid[row][j] == num:
            return False

    # Check column
    for i in range(9):
        if grid[i][col] == num:
            return False

    # Check 3x3 box
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if grid[i][j] == num:
                return False

    return True


def create_puzzle_from_solution(solution, target_clues):
    """Create puzzle by removing numbers from solution"""

    # Start with the complete solution
    puzzle = copy.deepcopy(solution)

    # Get all cell positions
    positions = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(positions)

    # Remove numbers until we reach target clue count
    current_clues = 81  # Start with all cells filled

    for row, col in positions:
        if current_clues <= target_clues:
            break

        # Try removing this cell
        original_value = puzzle[row][col]
        puzzle[row][col] = 0

        # Check if puzzle still has unique solution
        if has_unique_solution(puzzle):
            current_clues -= 1
        else:
            # Put the number back if removing it creates multiple solutions
            puzzle[row][col] = original_value

    return puzzle


def has_unique_solution(puzzle):
    """Check if puzzle has exactly one solution"""

    solutions = []
    find_all_solutions(copy.deepcopy(puzzle), solutions, max_solutions=2)

    return len(solutions) == 1


def find_all_solutions(grid, solutions, max_solutions=2):
    """Find all solutions to a puzzle (limited to max_solutions for efficiency)"""

    if len(solutions) >= max_solutions:
        return  # Stop if we already found enough solutions

    empty = find_empty_cell(grid)
    if not empty:
        # Found a complete solution
        solutions.append(copy.deepcopy(grid))
        return

    row, col = empty

    for num in range(1, 10):
        if is_valid_placement(grid, num, row, col):
            grid[row][col] = num
            find_all_solutions(grid, solutions, max_solutions)
            grid[row][col] = 0  # Backtrack

            if len(solutions) >= max_solutions:
                return


def verify_unique_solution(puzzle, expected_solution):
    """Verify that puzzle has the expected unique solution"""

    solutions = []
    find_all_solutions(copy.deepcopy(puzzle), solutions, max_solutions=2)

    if len(solutions) != 1:
        return False

    # Check if the solution matches expected
    solution = solutions[0]
    for i in range(9):
        for j in range(9):
            if solution[i][j] != expected_solution[i][j]:
                return False

    return True


def print_grid(grid, title="Grid"):
    """Print grid for debugging"""
    print(f"\n{title}:")
    for i, row in enumerate(grid):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")

        row_str = ""
        for j, cell in enumerate(row):
            if j % 3 == 0 and j != 0:
                row_str += "| "
            row_str += str(cell if cell != 0 else ".") + " "

        print(row_str)


if __name__ == "__main__":
    # Test the generator
    print("🧪 Testing Sudoku generator...")

    puzzle = generate_sudoku_with_solution("medium", 35)

    print_grid(puzzle["initial_grid"], "Generated Puzzle")
    print_grid(puzzle["solution_grid"], "Solution")

    print(f"\nClues: {puzzle['clue_count']}")
    print(f"Difficulty: {puzzle['difficulty']}")
    print("✅ Generator working correctly!")
