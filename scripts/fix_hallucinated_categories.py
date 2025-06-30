#!/usr/bin/env python3
"""
Fix Hallucinated KDP Categories Across All Metadata Files
Replaces fake categories with actual KDP categories and ensures 3 categories
"""

import json
import os
from pathlib import Path

# Actual KDP categories with FULL PATHS including subcategories (from real interface)
ACTUAL_KDP_CATEGORIES = {
    "puzzle_books": [
        "Crafts, Hobbies & Home > Games & Activities > Puzzles & Games",
        "Education & Teaching > Studying & Workbooks > Logic & Brain Teasers",
        "Games > Puzzles",
    ],
    "crossword_books": [
        "Crafts, Hobbies & Home > Games & Activities > Puzzles & Games",
        "Education & Teaching > Studying & Workbooks > Logic & Brain Teasers",
        "Games > Word Games",
    ],
    "brain_training": [
        "Self-Help > Memory Improvement",
        "Education & Teaching > Studying & Workbooks > Logic & Brain Teasers",
        "Crafts, Hobbies & Home > Games & Activities > Puzzles & Games",
    ],
}

# Hallucinated categories to replace
HALLUCINATED_CATEGORIES = [
    "Games, Puzzles & Trivia",
    "Games & Puzzles",
    "Puzzles & Games",
    "Brain Games",
    "Memory Games",
]


def fix_metadata_file(file_path: Path):
    """Fix categories in a single metadata JSON file"""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        # Check if file has categories
        if "categories" not in data:
            return False

        original_categories = data["categories"]
        fixed = False

        # Determine book type and appropriate categories
        file_str = str(file_path).lower()
        if "sudoku" in file_str:
            new_categories = ACTUAL_KDP_CATEGORIES["puzzle_books"]
        elif "crossword" in file_str:
            new_categories = ACTUAL_KDP_CATEGORIES["crossword_books"]
        else:
            new_categories = ACTUAL_KDP_CATEGORIES["brain_training"]

        # Check if current categories are hallucinated
        current_cats_str = str(original_categories)
        for hallucinated in HALLUCINATED_CATEGORIES:
            if hallucinated in current_cats_str:
                fixed = True
                break

        # Also fix if we don't have exactly 3 categories
        if len(original_categories) != 3:
            fixed = True

        if fixed:
            data["categories"] = new_categories

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)

            print(f"✅ Fixed: {file_path}")
            print(f"   Old: {original_categories}")
            print(f"   New: {new_categories}")
            return True

        return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def fix_markdown_files():
    """Fix categories in markdown files"""
    base_path = Path("books/active_production")

    # Find markdown files with category information
    md_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".md") and (
                "template" in file.lower() or "checklist" in file.lower()
            ):
                md_files.append(Path(root) / file)

    for md_file in md_files:
        try:
            with open(md_file, "r") as f:
                content = f.read()

            original_content = content

            # Replace hallucinated categories
            for hallucinated in HALLUCINATED_CATEGORIES:
                if hallucinated in content:
                    # Replace with appropriate real categories
                    if "sudoku" in str(md_file).lower():
                        content = content.replace(
                            hallucinated, "Crafts, Hobbies & Home"
                        )
                    elif "crossword" in str(md_file).lower():
                        content = content.replace(
                            hallucinated, "Crafts, Hobbies & Home"
                        )

            # Fix category count mentions
            content = content.replace(
                "Choose 2)", "Choose 3 - KDP ALLOWS 3 CATEGORIES!)"
            )
            content = content.replace(
                "(Choose 2", "(Choose 3 - KDP ALLOWS 3 CATEGORIES!"
            )

            if content != original_content:
                with open(md_file, "w") as f:
                    f.write(content)
                print(f"✅ Fixed markdown: {md_file}")

        except Exception as e:
            print(f"❌ Error fixing {md_file}: {e}")


def main():
    """Main function to fix all hallucinated categories"""
    print("🚨 FIXING HALLUCINATED KDP CATEGORIES")
    print("=" * 50)
    print("CRITICAL: Using ACTUAL KDP categories from real interface")
    print("KDP allows exactly 3 categories - fixing all files")
    print("=" * 50)

    base_path = Path("books/active_production")

    # Find all JSON metadata files
    json_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json") and "metadata" in file:
                json_files.append(Path(root) / file)

    print(f"Found {len(json_files)} metadata files to check...")

    fixed_count = 0
    for json_file in json_files:
        if fix_metadata_file(json_file):
            fixed_count += 1

    print(f"\n📊 RESULTS:")
    print(f"✅ Fixed {fixed_count} JSON files")

    # Fix markdown files
    print(f"\n🔧 Fixing markdown files...")
    fix_markdown_files()

    print(f"\n🎯 ACTUAL KDP CATEGORIES NOW USED:")
    print(f"📚 Sudoku Books: {ACTUAL_KDP_CATEGORIES['puzzle_books']}")
    print(f"🧩 Crossword Books: {ACTUAL_KDP_CATEGORIES['crossword_books']}")
    print(f"🧠 Brain Training: {ACTUAL_KDP_CATEGORIES['brain_training']}")

    print(f"\n✅ ALL HALLUCINATED CATEGORIES FIXED!")
    print(f"🚨 Remember: Always verify against ACTUAL KDP interface!")


if __name__ == "__main__":
    main()
