#!/usr/bin/env python3
"""
Fix corrupted JSON metadata files identified by critical_metadata_qa.py.

This script:
1. Backs up corrupted files
2. Fixes JSON syntax errors
3. Handles string content by wrapping in a dictionary
4. Exits with code 0 if all fixed, 1 otherwise
"""

import json
import re
import shutil
import sys
from pathlib import Path


def fix_json_file(file_path: Path, backup_dir: Path) -> bool:
    """
    Fix a corrupted JSON file.

    Args:
        file_path: Path to the corrupted JSON file
        backup_dir: Directory to store backups

    Returns:
        bool: True if fixed successfully, False otherwise
    """
    print(f"Attempting to fix: {file_path}")

    # Create backup path (treat provided path as already-relative to repo root)
    # Using .relative_to(Path.cwd()) can raise ValueError if CWD is not the repo
    # root.  Instead, just reuse the given path string.
    relative_path = file_path
    backup_path = backup_dir / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Create backup
        shutil.copy2(file_path, backup_path)
        print(f"  Backed up to: {backup_path}")
    except Exception as e:
        print(f"  ERROR: Could not create backup: {e}")
        return False

    try:
        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Try to parse as JSON
        try:
            # If it parses correctly, just reformat it
            data = json.loads(content)
            fixed_content = json.dumps(data, indent=2)
            file_path.write_text(fixed_content, encoding="utf-8")
            print(f"  SUCCESS: Reformatted valid JSON")
            return True
        except json.JSONDecodeError as e:
            if "Extra data" in str(e):
                # Handle "Extra data" error by finding the end of the first valid JSON object
                try:
                    # Extract position of extra data from error message
                    match = re.search(r"char (\d+)", str(e))
                    if match:
                        pos = int(match.group(1))
                        valid_part = content[:pos]
                        data = json.loads(valid_part)
                        fixed_content = json.dumps(data, indent=2)
                        file_path.write_text(fixed_content, encoding="utf-8")
                        print(f"  SUCCESS: Fixed 'Extra data' error")
                        return True
                    else:
                        print(f"  ERROR: Could not determine position of extra data")
                        return False
                except Exception as inner_e:
                    print(f"  ERROR: Failed to fix 'Extra data' error: {inner_e}")
                    return False
            else:
                # Handle other JSON decode errors (likely string content)
                try:
                    # Wrap content in a dictionary
                    wrapped_data = {"value": content}
                    fixed_content = json.dumps(wrapped_data, indent=2)
                    file_path.write_text(fixed_content, encoding="utf-8")
                    print(f"  SUCCESS: Wrapped string content in a dictionary")
                    return True
                except Exception as inner_e:
                    print(f"  ERROR: Failed to wrap content: {inner_e}")
                    return False
    except Exception as e:
        print(f"  ERROR: Failed to read or write file: {e}")
        return False


def main():
    """Fix all corrupted JSON files."""
    # List of corrupted files from QA output
    corrupted_files = [
        "books/active_production/Large_Print_Crossword_Masters/volume_1/hardcover/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_1/paperback/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_2/hardcover/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_2/paperback/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_2/paperback/metadata_professional.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_3/hardcover/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_3/paperback/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_3/paperback/metadata_volume3.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_4/hardcover/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_4/hardcover/metadata_volume4.json",
        "books/active_production/Large_Print_Crossword_Masters/volume_4/paperback/metadata_volume4.json",
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/hardcover/amazon_kdp_metadata.json",
        "books/active_production/Large_Print_Sudoku_Masters/volume_2/hardcover/amazon_kdp_metadata.json",
        "books/active_production/Test_Series/volume_1/paperback/amazon_kdp_metadata.json",
    ]

    # Create backup directory
    backup_dir = Path("books/active_production/_backup")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Track success
    all_fixed = True

    # Fix each file
    for file_path_str in corrupted_files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}")
            all_fixed = False
            continue

        if not fix_json_file(file_path, backup_dir):
            all_fixed = False

        print("-" * 50)

    # Report results
    if all_fixed:
        print("\n✅ All files fixed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some files could not be fixed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
