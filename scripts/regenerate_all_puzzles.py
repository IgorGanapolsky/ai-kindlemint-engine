#!/usr/bin/env python3
"""
Regenerate ALL puzzle images with the fixed visual distinction code
"""

from kindlemint.engines.sudoku import SudokuGenerator
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))


def regenerate_all_puzzles():
    """Regenerate all puzzle images with visual distinction fix."""

    puzzle_dir = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles"
    )
    metadata_dir = puzzle_dir / "metadata"

    if not metadata_dir.exists():
        print(f"❌ Metadata directory not found: {metadata_dir}")
        return False

    # Create sudoku generator
    engine = SudokuGenerator(puzzle_count=1, output_dir=puzzle_dir.parent)

    # Get all puzzle metadata files
    json_files = list(metadata_dir.glob("sudoku_puzzle_*.json"))

    print(f"🔄 Regenerating {len(json_files)} puzzle images with FIXED renderer...")

    success_count = 0

    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                puzzle_data = json.load(f)

            puzzle_id = puzzle_data.get("id", 0)
            initial_grid = puzzle_data.get("initial_grid", [])
            solution_grid = puzzle_data.get("solution_grid", [])

            if not initial_grid or not solution_grid:
                print(f"⚠️  Skipping puzzle {puzzle_id} - missing grid data")
                continue

            # Regenerate puzzle image with FIXED renderer
            puzzle_path = engine.create_grid_image(
                initial_grid, puzzle_id, is_solution=False
            )

            # Regenerate solution image
            solution_path = engine.create_grid_image(
                solution_grid, puzzle_id, is_solution=True
            )

            print(f"✅ Regenerated puzzle {puzzle_id}")
            success_count += 1

        except Exception as e:
            print(f"❌ Failed to regenerate puzzle {puzzle_id}: {e}")

    print(f"\n🎯 Successfully regenerated {success_count}/{len(json_files)} puzzles")
    return success_count == len(json_files)


if __name__ == "__main__":
    print("🔧 REGENERATING ALL PUZZLE IMAGES WITH VISUAL DISTINCTION FIX")
    print("=" * 70)

    success = regenerate_all_puzzles()

    if success:
        print("\n✅ ALL PUZZLE IMAGES REGENERATED WITH FIXED RENDERER")
    else:
        print("\n❌ SOME PUZZLES FAILED TO REGENERATE")

    print("=" * 70)
