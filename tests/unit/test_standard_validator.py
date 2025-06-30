#!/usr/bin/env python3
"""Test the standard Sudoku validator after fixes"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.validators.sudoku_validator import validate_sudoku_content

    """Main"""
def main():
    """Run the standard validator"""
    puzzle_dir = (
        Path(__file__).parent.parent
        / "books"
        / "active_production"
        / "Large_Print_Sudoku_Masters"
        / "volume_1"
        / "puzzles"
    )

    print("🔍 Running standard Sudoku validator...")
    print("=" * 50)

    result = validate_sudoku_content(puzzle_dir, strict=False)

    print(f"\nValidation complete!")
    print(f"Total puzzles: {result['total_puzzles']}")
    print(f"Valid puzzles: {result['valid_puzzles']}")
    print(f"Invalid puzzles: {result['invalid_puzzles']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Validation passed: {'✅ YES' if result['validation_passed'] else '❌ NO'}")

    # Calculate score
    score = 100 - (result["errors"] * 20) - (result["warnings"] * 5)
    score = max(0, score)
    print(f"Score: {score}/100")

    if result["errors"] > 0:
        print("\n❌ ERRORS FOUND:")
        for issue in result.get("issues", []):
            if issue.get("severity") == "error":
                print(
                    f"  - Puzzle #{issue.get('puzzle_id', '?')}: {issue['description']}"
                )


if __name__ == "__main__":
    main()
