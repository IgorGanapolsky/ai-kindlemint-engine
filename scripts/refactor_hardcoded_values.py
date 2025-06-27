#!/usr/bin/env python3
"""
Refactoring Script: Replace Hardcoded Values with Configuration
This script systematically updates Python files to use the centralized config loader
instead of hardcoded paths and magic numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Define the files that need refactoring based on our audit
FILES_WITH_ABSOLUTE_PATHS = [
    "scripts/create_volume_3_final_unique.py",  # Already partially fixed
    "scripts/crossword_content_validator.py",
    "scripts/create_volume_3_unique_puzzles.py",
]

FILES_WITH_HARDCODED_DIMENSIONS = [
    "scripts/create_volume_3_production_ready.py",
    "scripts/generate_crossword_volume_2_professional.py",
    "scripts/fix_volume_2_dimensions.py",
    "scripts/create_volume_2_cover.py",
    "scripts/create_volume_3_cover.py",
    "scripts/hardcover/create_hardcover_package_8.5x11.py",
]

# Replacement patterns
REPLACEMENTS = {
    # Absolute paths
    r'Path\("/Users/[^"]+/ai-kindlemint-engine/(.+?)"\)': r'Path(config.get_path("file_paths.base_output_dir")).parent / "\1"',
    r'"/Users/[^"]+/ai-kindlemint-engine/(.+?)"': r'str(Path(config.get_path("file_paths.base_output_dir")).parent / "\1")',
    # Common base paths
    r'"books/active_production"': 'config.get("file_paths.base_output_dir")',
    r'Path\("books/active_production"\)': 'Path(config.get_path("file_paths.base_output_dir"))',
    # Page dimensions
    r"8\.5(?!\d)": 'config.get("kdp_specifications.paperback.page_width_in", 8.5)',
    r"11(?![\d.])": 'config.get("kdp_specifications.paperback.page_height_in", 11)',
    # Margins (in context of inches)
    r"0\.75\s*\*\s*72": 'config.get("kdp_specifications.paperback.top_margin_in", 0.75) * 72',
    r"0\.5\s*\*\s*72": 'config.get("kdp_specifications.paperback.outer_margin_in", 0.5) * 72',
    r"0\.375\s*\*\s*72": 'config.get("kdp_specifications.paperback.gutter_in", 0.375) * 72',
    # Grid sizes
    r"GRID_SIZE\s*=\s*15": 'GRID_SIZE = config.get("puzzle_generation.crossword.grid_size", 15)',
    r"CELL_SIZE\s*=\s*18": 'CELL_SIZE = config.get("puzzle_generation.crossword.cell_size_pixels", 18)',
    # Font sizes (in setFont calls)
    r'setFont\("Helvetica-Bold",\s*18\)': 'setFont(config.get("typography.fonts.title", "Helvetica-Bold"), config.get("typography.font_sizes.title", 18))',
    r'setFont\("Helvetica",\s*14\)': 'setFont(config.get("typography.fonts.subtitle", "Helvetica"), config.get("typography.font_sizes.subtitle", 14))',
    r'setFont\("Helvetica",\s*12\)': 'setFont(config.get("typography.fonts.body", "Helvetica"), config.get("typography.font_sizes.body", 12))',
    # DPI values
    r"300(?:\s*#.*?DPI|.*?dpi)": 'config.get("kdp_specifications.dpi", 300)',
    r"dpi\s*=\s*150": 'dpi=config.get("processing.pdf_to_image_dpi", 150)',
    # Puzzle counts
    r"50\s*#?\s*puzzles": 'config.get("puzzle_generation.default_puzzle_count", 50)',
    r"PUZZLE_COUNT\s*=\s*50": 'PUZZLE_COUNT = config.get("puzzle_generation.default_puzzle_count", 50)',
}

# Import statement to add at the beginning of files
CONFIG_IMPORT = """# Import configuration loader
from scripts.config_loader import config
"""


def add_config_import(content):
    """Add config import after the module docstring and other imports"""
    lines = content.split("\n")

    # Find where to insert the import
    insert_index = 0
    in_docstring = False
    docstring_count = 0

    for i, line in enumerate(lines):
        # Handle module docstrings
        if '"""' in line or "'''" in line:
            docstring_count += 1
            if docstring_count >= 2:  # End of module docstring
                in_docstring = False
                continue
            else:
                in_docstring = True
                continue

        # Skip if we're inside a docstring
        if in_docstring:
            continue

        # Look for import statements
        if line.startswith("import ") or line.startswith("from "):
            insert_index = i + 1
        elif insert_index > 0 and line.strip() and not line.startswith("#"):
            # We've passed all imports, insert here
            break

    # Check if config import already exists
    config_import_exists = any(
        "from scripts.config_loader import config" in line
        or "from config_loader import config" in line
        for line in lines
    )

    if not config_import_exists:
        lines.insert(insert_index, CONFIG_IMPORT)

    return "\n".join(lines)


def refactor_file(filepath, dry_run=False):
    """Refactor a single file to use configuration"""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {filepath}")

    try:
        with open(filepath, "r") as f:
            content = f.read()

        original_content = content

        # Add config import if needed
        content = add_config_import(content)

        # Apply replacements
        changes_made = 0
        for pattern, replacement in REPLACEMENTS.items():
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                print(f"  - Replaced {count} instances of pattern: {pattern[:50]}...")
                changes_made += count
                content = new_content

        if changes_made > 0:
            if not dry_run:
                # Create backup
                backup_path = (
                    filepath + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                )
                shutil.copy2(filepath, backup_path)
                print(f"  - Created backup: {backup_path}")

                # Write updated content
                with open(filepath, "w") as f:
                    f.write(content)
                print(f"  - Updated file with {changes_made} changes")
            else:
                print(f"  - Would make {changes_made} changes")
        else:
            print("  - No changes needed")

        return changes_made > 0

    except Exception as e:
        print(f"  - ERROR: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Refactor hardcoded values to use configuration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument("--file", help="Refactor a specific file")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Refactor all known files with hardcoded values",
    )

    args = parser.parse_args()

    if args.file:
        files_to_process = [args.file]
    elif args.all:
        files_to_process = FILES_WITH_ABSOLUTE_PATHS + FILES_WITH_HARDCODED_DIMENSIONS
    else:
        # Default to just the files with absolute paths
        files_to_process = FILES_WITH_ABSOLUTE_PATHS

    print("Configuration Refactoring Tool")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Files to process: {len(files_to_process)}")

    # Process files
    files_changed = 0
    for filepath in files_to_process:
        full_path = Path(filepath)
        if not full_path.is_absolute():
            full_path = Path(__file__).parent.parent / filepath

        if full_path.exists():
            if refactor_file(str(full_path), dry_run=args.dry_run):
                files_changed += 1
        else:
            print(f"\nWARNING: File not found: {full_path}")

    print(f"\n{'Would modify' if args.dry_run else 'Modified'} {files_changed} files")

    if args.dry_run and files_changed > 0:
        print("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
