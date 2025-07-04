#!/usr/bin/env python3
"""
Comprehensive Sudoku Validator for Quality Assurance
Ensures all Sudoku puzzles are 100% correct before publication
"""

import copy
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import secrets


class SudokuValidator:
    """Comprehensive validator for Sudoku puzzle quality assurance."""

    def __init__(self):
        self.grid_size = 9
        self.box_size = 3

    def validate_puzzle(
        self, puzzle: List[List[int]], solution: List[List[int]]
    ) -> Dict[str, any]:
        """
        Perform comprehensive validation on a Sudoku puzzle.

        Returns a dictionary with validation results and any issues found.
        """
        results = {"valid": True, "errors": [], "warnings": [], "stats": {}}

        # 1. Validate grid structure
        self._validate_grid_structure(puzzle, "puzzle", results)
        self._validate_grid_structure(solution, "solution", results)

        # 2. Validate puzzle values
        self._validate_values(puzzle, "puzzle", allow_zeros=True, results=results)
        self._validate_values(solution, "solution", allow_zeros=False, results=results)

        # 3. Validate solution correctness
        if not self._is_valid_solution(solution):
            results["valid"] = False
            results["errors"].append("Solution is not a valid Sudoku solution")

        # 4. Validate puzzle matches solution
        if not self._puzzle_matches_solution(puzzle, solution):
            results["valid"] = False
            results["errors"].append("Puzzle clues do not match the solution")

        # 5. Check unique solution
        solution_count = self._count_solutions(puzzle, limit=2)
        if solution_count == 0:
            results["valid"] = False
            results["errors"].append("Puzzle has no solution")
        elif solution_count > 1:
            results["valid"] = False
            results["errors"].append("Puzzle has multiple solutions")

        # 6. Check minimum clues
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        results["stats"]["clue_count"] = clue_count

        if clue_count < 17:
            results["valid"] = False
            results["errors"].append(
                f"Puzzle has only {clue_count} clues (minimum is 17)"
            )

        # 7. Check for symmetry (optional quality check)
        symmetry_type = self._check_symmetry(puzzle)
        results["stats"]["symmetry"] = symmetry_type
        if symmetry_type == "none":
            results["warnings"].append(
                "Puzzle lacks symmetry (not required but often preferred)"
            )

        # 8. Estimate difficulty
        difficulty = self._estimate_difficulty(puzzle)
        results["stats"]["estimated_difficulty"] = difficulty

        # 9. Check puzzle minimality
        if clue_count > 0:
            is_minimal = self._check_minimality_sample(puzzle)
            results["stats"]["appears_minimal"] = is_minimal
            if not is_minimal:
                results["warnings"].append("Puzzle may contain redundant clues")

        return results

    def _validate_grid_structure(self, grid: List[List[int]], name: str, results: Dict):
        """Validate the basic structure of a grid."""
        if not isinstance(grid, list):
            results["valid"] = False
            results["errors"].append(f"{name} is not a list")
            return

        if len(grid) != self.grid_size:
            results["valid"] = False
            results["errors"].append(
                f"{name} has {len(grid)} rows (expected {self.grid_size})"
            )
            return

        for i, row in enumerate(grid):
            if not isinstance(row, list):
                results["valid"] = False
                results["errors"].append(f"{name} row {i} is not a list")
                continue

            if len(row) != self.grid_size:
                results["valid"] = False
                results["errors"].append(
                    f"{name} row {i} has {len(row)} columns (expected {self.grid_size})"
                )

    def _validate_values(
        self, grid: List[List[int]], name: str, allow_zeros: bool, results: Dict
    ):
        """Validate all values in the grid are within acceptable range."""
        valid_range = range(0 if allow_zeros else 1, 10)

        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if not isinstance(cell, int):
                    results["valid"] = False
                    results["errors"].append(
                        f"{name}[{i}][{j}] is not an integer: {type(cell)}"
                    )
                elif cell not in valid_range:
                    results["valid"] = False
                    results["errors"].append(
                        f"{name}[{i}][{j}] has invalid value: {cell}"
                    )

    def _is_valid_solution(self, grid: List[List[int]]) -> bool:
        """Check if a complete grid is a valid Sudoku solution."""
        # Check rows
        for row in grid:
            if len(set(row)) != 9 or set(row) != set(range(1, 10)):
                return False

        # Check columns
        for col in range(9):
            column = [grid[row][col] for row in range(9)]
            if len(set(column)) != 9 or set(column) != set(range(1, 10)):
                return False

        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box_values.append(grid[row][col])
                if len(set(box_values)) != 9 or set(box_values) != set(range(1, 10)):
                    return False

        return True

    def _puzzle_matches_solution(
        self, puzzle: List[List[int]], solution: List[List[int]]
    ) -> bool:
        """Check that all puzzle clues match the solution."""
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0 and puzzle[i][j] != solution[i][j]:
                    return False
        return True

    def _is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at grid[row][col] is valid."""
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

    def _count_solutions(self, grid: List[List[int]], limit: int = 2) -> int:
        """Count the number of solutions for a puzzle."""
        solutions = [0]
        grid_copy = copy.deepcopy(grid)

        def solve(row: int, col: int):
            if solutions[0] >= limit:
                return

            # Find next empty cell
            while row < 9:
                if col >= 9:
                    row += 1
                    col = 0
                    continue
                if row >= 9:
                    solutions[0] += 1
                    return
                if grid_copy[row][col] == 0:
                    break
                col += 1

            if row >= 9:
                solutions[0] += 1
                return

            # Try each number
            for num in range(1, 10):
                if self._is_valid(grid_copy, row, col, num):
                    grid_copy[row][col] = num
                    solve(row, col + 1)
                    grid_copy[row][col] = 0

                    if solutions[0] >= limit:
                        return

        solve(0, 0)
        return solutions[0]

    def _check_symmetry(self, puzzle: List[List[int]]) -> str:
        """Check what type of symmetry the puzzle has."""
        # Get positions of all clues
        clues = set()
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    clues.add((i, j))

        # Check 180-degree rotational symmetry (most common)
        rotational_180 = True
        for i, j in clues:
            if (8 - i, 8 - j) not in clues:
                rotational_180 = False
                break

        if rotational_180:
            return "rotational_180"

        # Check horizontal reflection
        horizontal = True
        for i, j in clues:
            if (8 - i, j) not in clues:
                horizontal = False
                break

        if horizontal:
            return "horizontal"

        # Check vertical reflection
        vertical = True
        for i, j in clues:
            if (i, 8 - j) not in clues:
                vertical = False
                break

        if vertical:
            return "vertical"

        # Check diagonal reflection
        diagonal = True
        for i, j in clues:
            if (j, i) not in clues:
                diagonal = False
                break

        if diagonal:
            return "diagonal"

        return "none"

    def _estimate_difficulty(self, puzzle: List[List[int]]) -> str:
        """Estimate puzzle difficulty based on clue count and pattern."""
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)

        if clue_count >= 35:
            return "easy"
        elif clue_count >= 27:
            return "medium"
        elif clue_count >= 22:
            return "hard"
        else:
            return "expert"

    def _check_minimality_sample(
        self, puzzle: List[List[int]], sample_size: int = 5
    ) -> bool:
        """
        Check if puzzle appears to be minimal by testing a sample of clues.
        Returns True if puzzle appears minimal, False if redundant clues found.
        """
        # Get all clue positions
        clue_positions = [
            (r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0
        ]

        if len(clue_positions) == 0:
            return True

        test_positions = secrets.SystemRandom().sample(clue_positions, min(sample_size, len(clue_positions))
        )

        puzzle_copy = copy.deepcopy(puzzle)

        for row, col in test_positions:
            # Remove clue temporarily
            temp = puzzle_copy[row][col]
            puzzle_copy[row][col] = 0

            # Check solution count
            solution_count = self._count_solutions(puzzle_copy, limit=2)

            # Restore clue
            puzzle_copy[row][col] = temp

            # If puzzle still has unique solution without this clue, it's redundant
            if solution_count == 1:
                return False

        return True

    def validate_batch(self, puzzle_dir: Path) -> Dict[str, any]:
        """Validate all puzzles in a directory."""
        metadata_dir = puzzle_dir / "metadata"

        if not metadata_dir.exists():
            return {
                "error": f"Metadata directory not found: {metadata_dir}",
                "valid": False,
            }

        # Load collection metadata
        collection_path = metadata_dir / "sudoku_collection.json"
        if not collection_path.exists():
            return {
                "error": f"Collection metadata not found: {collection_path}",
                "valid": False,
            }

        with open(collection_path) as f:
            collection = json.load(f)

        results = {
            "total_puzzles": collection["puzzle_count"],
            "valid_puzzles": 0,
            "invalid_puzzles": 0,
            "puzzle_results": [],
            "summary": {"all_valid": True, "total_errors": 0, "total_warnings": 0},
        }

        # Validate each puzzle
        for puzzle_id in collection["puzzles"]:
            puzzle_meta_path = metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"

            if not puzzle_meta_path.exists():
                results["puzzle_results"].append(
                    {
                        "id": puzzle_id,
                        "valid": False,
                        "error": "Metadata file not found",
                    }
                )
                results["invalid_puzzles"] += 1
                results["summary"]["all_valid"] = False
                continue

            with open(puzzle_meta_path) as f:
                puzzle_data = json.load(f)

            # Validate the puzzle
            validation = self.validate_puzzle(
                puzzle_data["initial_grid"], puzzle_data["solution_grid"]
            )

            validation["id"] = puzzle_id
            validation["difficulty"] = puzzle_data.get("difficulty", "unknown")

            results["puzzle_results"].append(validation)

            if validation["valid"]:
                results["valid_puzzles"] += 1
            else:
                results["invalid_puzzles"] += 1
                results["summary"]["all_valid"] = False

            results["summary"]["total_errors"] += len(validation["errors"])
            results["summary"]["total_warnings"] += len(validation["warnings"])

        return results


def main():
    """Main entry point for Sudoku validator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sudoku Validator - Quality Assurance Tool"
    )
    parser.add_argument("puzzle_dir", help="Directory containing puzzles to validate")
    parser.add_argument("--verbose", action="store_true", help="Show detailed results")

    args = parser.parse_args()

    validator = SudokuValidator()
    results = validator.validate_batch(Path(args.puzzle_dir))

    if "error" in results:
        print(f"❌ ERROR: {results['error']}")
        return 1

    # Print summary
    print(f"\n🔍 SUDOKU VALIDATION REPORT")
    print(f"{'='*50}")
    print(f"📁 Directory: {args.puzzle_dir}")
    print(f"📊 Total puzzles: {results['total_puzzles']}")
    print(f"✅ Valid puzzles: {results['valid_puzzles']}")
    print(f"❌ Invalid puzzles: {results['invalid_puzzles']}")
    print(f"⚠️  Total warnings: {results['summary']['total_warnings']}")

    if results["summary"]["all_valid"]:
        print(f"\n✅ ALL PUZZLES PASSED VALIDATION!")
    else:
        print(f"\n❌ VALIDATION FAILED!")
        print(f"   Total errors: {results['summary']['total_errors']}")

    if args.verbose:
        print(f"\n📋 DETAILED RESULTS:")
        print(f"{'='*50}")

        for puzzle_result in results["puzzle_results"]:
            print(
                f"\nPuzzle #{puzzle_result['id']} ({puzzle_result.get('difficulty', 'unknown')})"
            )

            if puzzle_result["valid"]:
                print(f"  ✅ Valid")
                if "stats" in puzzle_result:
                    stats = puzzle_result["stats"]
                    print(f"  📊 Clues: {stats.get('clue_count', 'N/A')}")
                    print(f"  🔄 Symmetry: {stats.get('symmetry', 'N/A')}")
                    print(
                        f"  📈 Difficulty: {stats.get('estimated_difficulty', 'N/A')}"
                    )
            else:
                print(f"  ❌ Invalid")

            if puzzle_result.get("errors"):
                print(f"  ❌ Errors:")
                for error in puzzle_result["errors"]:
                    print(f"    - {error}")

            if puzzle_result.get("warnings"):
                print(f"  ⚠️  Warnings:")
                for warning in puzzle_result["warnings"]:
                    print(f"    - {warning}")

    return 0 if results["summary"]["all_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
