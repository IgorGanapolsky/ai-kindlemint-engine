#!/usr/bin/env python3
"""
Fix Difficulty Progression for Large Print Sudoku Masters Volume 1
Updates all puzzle metadata to implement Easy → Medium → Hard progression
"""

import json
import sys
from pathlib import Path


def update_difficulty_progression(puzzles_dir: Path):
    """Update all puzzle metadata files with proper difficulty progression"""

    # Define progression: 1-33 Easy, 34-66 Medium, 67-100 Hard
    progression_map = {}

    # Easy: Puzzles 1-33 (33 puzzles)
    for i in range(1, 34):
        progression_map[i] = "easy"

    # Medium: Puzzles 34-66 (33 puzzles)
    for i in range(34, 67):
        progression_map[i] = "medium"

    # Hard: Puzzles 67-100 (34 puzzles)
    for i in range(67, 101):
        progression_map[i] = "hard"

    metadata_dir = puzzles_dir / "metadata"
    if not metadata_dir.exists():
        print(f"❌ Metadata directory not found: {metadata_dir}")
        return False

    updated_count = 0

    for puzzle_id in range(1, 101):
        puzzle_file = metadata_dir / f"sudoku_puzzle_{puzzle_id:03d}.json"

        if not puzzle_file.exists():
            print(f"⚠️  Puzzle file not found: {puzzle_file}")
            continue

        try:
            # Load puzzle metadata
            with open(puzzle_file, "r") as f:
                puzzle_data = json.load(f)

            # Get old and new difficulty
            old_difficulty = puzzle_data.get("difficulty", "unknown")
            new_difficulty = progression_map[puzzle_id]

            # Update difficulty
            puzzle_data["difficulty"] = new_difficulty

            # Save updated metadata
            with open(puzzle_file, "w") as f:
                json.dump(puzzle_data, f, indent=2)

            updated_count += 1

            if old_difficulty != new_difficulty:
                print(
                    f"✅ Updated Puzzle {puzzle_id: 3d}: {
                        old_difficulty} → {new_difficulty}"
                )

        except Exception as e:
            print(f"❌ Error updating {puzzle_file}: {e}")

    print(f"\n🎯 Difficulty Progression Update Complete!")
    print(f"📊 Updated {updated_count}/100 puzzle metadata files")
    print(f"📈 Progression: Easy (1-33), Medium (34-66), Hard (67-100)")

    return True


def main():
    """Main function"""
    if len(sys.argv) > 1:
        puzzles_dir = Path(sys.argv[1])
    else:
        # Default to current Volume 1 location
        puzzles_dir = Path(
            "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles"
        )

    if not puzzles_dir.exists():
        print(f"❌ Puzzles directory not found: {puzzles_dir}")
        print(
            "Usage: python fix_difficulty_progression.py [puzzles_directory]")
        return 1

    print(f"🔄 Updating difficulty progression in: {puzzles_dir}")

    success = update_difficulty_progression(puzzles_dir)

    if success:
        print("\n🎉 Success! Difficulty progression has been implemented.")
        print("📋 Next step: Regenerate the PDF to reflect the changes.")
        return 0
    else:
        print("\n❌ Failed to update difficulty progression.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
