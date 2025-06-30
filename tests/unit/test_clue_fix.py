#!/usr/bin/env python3
"""
Test the fixed clue rendering to verify visual distinction works
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from kindlemint.engines.sudoku import SudokuGenerator


def test_clue_rendering():
    """Test the fixed clue rendering with visual distinction."""
    print("🧪 Testing fixed clue rendering...")

    # Load existing puzzle data
    puzzle_dir = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles"
    )
    metadata_dir = puzzle_dir / "metadata"

    if not metadata_dir.exists():
        print(f"❌ Metadata directory not found: {metadata_dir}")
        return False

    # Test with puzzle 100 (the one the user showed)
    test_puzzle_file = metadata_dir / "sudoku_puzzle_100.json"

    if not test_puzzle_file.exists():
        print(f"❌ Test puzzle file not found: {test_puzzle_file}")
        return False

    # Load puzzle data
    with open(test_puzzle_file, "r") as f:
        puzzle_data = json.load(f)

    # Create sudoku generator for regeneration
    engine = SudokuGenerator(puzzle_count=1, output_dir=puzzle_dir.parent)

    print(f"🔍 Testing Puzzle 100:")
    print(f"  • Difficulty: {puzzle_data.get('difficulty', 'unknown')}")
    print(f"  • Clue count: {puzzle_data.get('clue_count', 'unknown')}")

    # Get the initial grid (clues)
    initial_grid = puzzle_data.get("initial_grid", [])
    solution_grid = puzzle_data.get("solution_grid", [])

    if not initial_grid:
        print("❌ No initial grid found in puzzle data")
        return False

    # Count clues in the data
    actual_clues = sum(1 for row in initial_grid for cell in row if cell != 0)
    print(f"  • Actual clues in data: {actual_clues}")

    # Regenerate puzzle image with FIXED renderer
    print("\n🎨 Regenerating puzzle image with visual distinction fix...")
    try:
        puzzle_path = engine.create_grid_image(initial_grid, 100, is_solution=False)
        print(f"✅ Regenerated puzzle: {puzzle_path}")

        # Also regenerate solution
        solution_path = engine.create_grid_image(solution_grid, 100, is_solution=True)
        print(f"✅ Regenerated solution: {solution_path}")

        return True

    except Exception as e:
        print(f"❌ Failed to regenerate: {e}")
        return False


def validate_fix():
    """Run emergency validation on the fixed images."""
    print("\n🚨 Running emergency validation on fixed images...")

    # Import emergency validator
    sys.path.append(str(Path(__file__).parent))
    from emergency_visual_validator import EmergencyVisualValidator

    # Test the specific puzzle we fixed
    pdf_path = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback/Large_Print_Sudoku_Masters_V1_COMPLETE.pdf"
    )

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False

    validator = EmergencyVisualValidator()

    # Focus on page 100 that user showed
    print("\n🔍 Validating Page 100 specifically...")
    try:
        import fitz

        pdf = fitz.open(str(pdf_path))

        if len(pdf) > 100:
            issues = validator._analyze_puzzle_page(pdf, 100)

            print(f"📊 Page 100 Analysis Results:")
            if issues:
                print(f"❌ Still has {len(issues)} issues:")
                for issue in issues:
                    print(f"  • {issue}")
                return False
            else:
                print("✅ Page 100 now passes validation!")
                return True
        else:
            print("❌ PDF doesn't have enough pages")
            return False

        pdf.close()

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    print("🔧 CLUE RENDERING FIX TEST")
    print("=" * 50)

    # Test 1: Regenerate images
    regen_success = test_clue_rendering()

    if regen_success:
        print("\n" + "=" * 50)
        # Test 2: Validate the fix
        validation_success = validate_fix()

        if validation_success:
            print("\n🎉 SUCCESS: Clue rendering fix appears to work!")
        else:
            print("\n⚠️  Images regenerated but validation still shows issues")
    else:
        print("\n❌ Failed to regenerate images")

    print("\n" + "=" * 50)
