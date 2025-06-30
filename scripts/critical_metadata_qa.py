#!/usr/bin/env python3
"""
CRITICAL METADATA QA VALIDATOR
Catches critical errors that MUST NOT reach production:
- Wrong trim sizes for puzzle books
- Missing KDP book type classifications
- Hallucinated KDP categories
- Missing required fields

This QA MUST PASS before any commit!
"""

import glob
import json
import os
from pathlib import Path
from typing import Dict


class CriticalMetadataQA:
    """Critical QA validator for metadata files"""

    def __init__(self):
        self.base_dir = "/Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine"
        self.critical_errors = []
        self.warnings = []
        self.validated_files = 0

        # Verified KDP categories from actual interface screenshots
        self.valid_kdp_categories = {
            "Crafts, Hobbies & Home > Games & Activities > Puzzles & Games",
            "Education & Teaching > Studying & Workbooks > Logic & Brain Teasers",
            "Games > Puzzles",
            "Games > Word Games", 
            "Self-Help > Memory Improvement",
            "Health, Fitness & Dieting > Aging",
            "Crafts, Hobbies & Home > Games & Activities",  # Valid parent category
        }

        # Known hallucinated categories to catch
        self.hallucinated_categories = {
            "Games, Puzzles & Trivia > Sudoku",
            "Activity Books",
            "Crafts, Hobbies & Home > Activity Books",
            "Brain Games",
            "Memory Games",
        }

    def validate_trim_size(self, data: Dict, file_path: str) -> None:
        """Validate trim sizes for puzzle books"""
        # Handle both nested and flat format structures
        format_info = data.get("format", {})
        if isinstance(format_info, str):
            # Flat structure - format is a string
            book_type = format_info.lower()
            trim_size = data.get("trim_size")
            dimensions = data.get("dimensions")
        else:
            # Nested structure
            trim_size = format_info.get("trim_size")
            dimensions = data.get("dimensions")
            book_type = format_info.get("type", "").lower()

        # Also check binding field for book type
        if not book_type and data.get("binding"):
            binding = data.get("binding", "").lower()
            if "paperback" in binding or "perfect" in binding:
                book_type = "paperback"
            elif "hardcover" in binding or "case" in binding:
                book_type = "hardcover"

        size_value = trim_size or dimensions

        if book_type == "paperback":
            if size_value == "6x9 inches" or size_value == "6 x 9 inches":
                self.critical_errors.append(
                    {
                        "file": file_path,
                        "error": "CRITICAL: Paperback puzzle book using 6x9 trim size - TOO SMALL for puzzles!",
                        "fix": "Change to '8.5x11 inches' for paperback puzzle books",
                        "current": size_value,
                    }
                )
            elif size_value and "8.5" not in size_value and "11" not in size_value:
                self.warnings.append(
                    {
                        "file": file_path,
                        "warning": f"Unusual paperback size: {size_value}. Standard is 8.5x11 inches for puzzle books",
                    }
                )

    def validate_kdp_categories(self, data: Dict, file_path: str) -> None:
        """Validate KDP categories against actual interface"""
        categories = data.get("categories", [])

        if not categories:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Missing KDP categories",
                    "fix": "Add 3 KDP categories with full subcategory paths",
                }
            )
            return

        if len(categories) != 3:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": f"CRITICAL: Wrong number of KDP categories ({len(categories)}). KDP requires exactly 3",
                    "fix": "Provide exactly 3 KDP categories",
                    "current": categories,
                }
            )

        # Check for hallucinated categories
        for category in categories:
            if any(
                hallucinated in category
                for hallucinated in self.hallucinated_categories
            ):
                self.critical_errors.append(
                    {
                        "file": file_path,
                        "error": f"CRITICAL: HALLUCINATED KDP category: '{category}'",
                        "fix": "Use only ACTUAL KDP categories from interface screenshots",
                        "current": category,
                    }
                )

            # Check for missing subcategories
            if ">" not in category:
                self.critical_errors.append(
                    {
                        "file": file_path,
                        "error": f"CRITICAL: Missing subcategory in '{category}'",
                        "fix": "Use full category path: 'Category > Subcategory'",
                        "current": category,
                    }
                )

    def validate_cover_prompts(self, data: Dict, file_path: str) -> None:
        """Validate DALL-E cover creation prompts"""
        cover_design = data.get("cover_design")

        # Handle both nested and flat format structures
        format_info = data.get("format", {})
        if isinstance(format_info, str):
            format_type = format_info.lower()
        else:
            format_type = format_info.get("type", "").lower()

        # Also check binding field for book type
        if not format_type and data.get("binding"):
            binding = data.get("binding", "").lower()
            if "paperback" in binding or "perfect" in binding:
                format_type = "paperback"
            elif "hardcover" in binding or "case" in binding:
                format_type = "hardcover"

        if not cover_design:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Missing cover_design field with DALL-E prompts",
                    "fix": "Add cover_design with dalle_prompt for book cover creation",
                }
            )
            return

        # Check front cover
        dalle_prompt = cover_design.get("dalle_prompt")
        if not dalle_prompt:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Missing DALL-E cover creation prompt",
                    "fix": "Add detailed dalle_prompt for professional book cover",
                }
            )
        elif len(dalle_prompt) < 50:
            self.warnings.append(
                {
                    "file": file_path,
                    "warning": "DALL-E prompt too short - should be detailed for quality covers",
                }
            )

        # Check back cover for physical books
        if format_type in ["paperback", "hardcover"]:
            back_cover_prompt = cover_design.get("back_cover_dalle_prompt")
            if not back_cover_prompt:
                self.critical_errors.append(
                    {
                        "file": file_path,
                        "error": f"CRITICAL: Missing back cover prompt for {format_type} book!",
                        "fix": f"Add 'back_cover_dalle_prompt' - {format_type} books need both front AND back covers",
                        "current_format": format_type,
                    }
                )
            elif len(back_cover_prompt) < 50:
                self.warnings.append(
                    {
                        "file": file_path,
                        "warning": f"Back cover DALL-E prompt too short for {format_type} - needs detailed description",
                    }
                )

    def validate_kdp_book_types(self, data: Dict, file_path: str) -> None:
        """Validate KDP book type classifications"""
        kdp_types = data.get("kdp_book_types")

        if not kdp_types:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Missing kdp_book_types field",
                    "fix": "Add kdp_book_types with low_content_book and large_print_book flags",
                }
            )
            return

        # Check required fields
        if "low_content_book" not in kdp_types:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Missing low_content_book classification",
                    "fix": "Add 'low_content_book': true for puzzle books",
                }
            )
        elif kdp_types.get("low_content_book") != True:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Puzzle books should have low_content_book: true",
                    "fix": "Set 'low_content_book': true",
                    "current": kdp_types.get("low_content_book"),
                }
            )

        if "large_print_book" not in kdp_types:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": "CRITICAL: Missing large_print_book classification",
                    "fix": "Add 'large_print_book': true/false based on book title",
                }
            )
        else:
            # Validate large_print_book flag matches title
            title = data.get("title", "")
            has_large_print = "Large Print" in title
            declared_large_print = kdp_types.get("large_print_book")

            if has_large_print and not declared_large_print:
                self.critical_errors.append(
                    {
                        "file": file_path,
                        "error": "CRITICAL: 'Large Print' in title but large_print_book: false",
                        "fix": "Set 'large_print_book': true for Large Print series",
                    }
                )
            elif not has_large_print and declared_large_print:
                self.critical_errors.append(
                    {
                        "file": file_path,
                        "error": "CRITICAL: large_print_book: true but no 'Large Print' in title",
                        "fix": "Set 'large_print_book': false or add 'Large Print' to title",
                    }
                )

    def validate_file(self, file_path: str) -> None:
        """Validate a single metadata file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # If loaded data is not a dict, wrap it into a dict
            if not isinstance(data, dict):
                data = {"raw": data}

            self.validated_files += 1

            # Run all critical validations
            self.validate_trim_size(data, file_path)
            self.validate_kdp_categories(data, file_path)
            self.validate_kdp_book_types(data, file_path)
            self.validate_cover_prompts(data, file_path)

        except json.JSONDecodeError as e:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": f"CRITICAL: Invalid JSON - {e}",
                    "fix": "Fix JSON syntax errors",
                }
            )
        except Exception as e:
            self.critical_errors.append(
                {
                    "file": file_path,
                    "error": f"CRITICAL: File read error - {e}",
                    "fix": "Check file permissions and encoding",
                }
            )

    def run_validation(self) -> bool:
        """Run validation on all metadata files"""
        print("🚨 RUNNING CRITICAL METADATA QA")
        print("=" * 50)

        # Find all metadata files
        patterns = [
            "**/books/active_production/**/*metadata*.json",
            "**/books/active_production/**/amazon_kdp_metadata.json",
            "**/books/active_production/**/kindle_metadata.json",
            "**/books/active_production/**/paperback_metadata.json",
        ]

        all_files = set()
        for pattern in patterns:
            files = glob.glob(os.path.join(str(self.base_dir), pattern), recursive=True)
            all_files.update(files)

        # Filter out files under any _backup directory
        filtered_files = [f for f in all_files if "_backup" not in Path(f).parts]

        print(f"📁 Found {len(filtered_files)} metadata files to validate")
        print()

        # Validate each file
        for file_path in sorted(filtered_files):
            rel_path = os.path.relpath(file_path, str(self.base_dir))
            print(f"Checking: {rel_path}")
            self.validate_file(file_path)

        # Generate report
        print()
        print("=" * 50)
        print("📊 CRITICAL QA RESULTS")
        print("=" * 50)

        if self.critical_errors:
            print(f"❌ CRITICAL ERRORS FOUND: {len(self.critical_errors)}")
            print()
            for i, error in enumerate(self.critical_errors, 1):
                print(f"{i}. 🚨 {error['error']}")
                print(f"   📁 File: {error['file']}")
                print(f"   🔧 Fix: {error['fix']}")
                if "current" in error:
                    print(f"   📄 Current: {error['current']}")
                print()

            print("🛑 QA FAILED - Fix critical errors before commit!")
            return False

        if self.warnings:
            print(f"⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning['warning']} ({warning['file']})")
            print()

        print(f"✅ QA PASSED - {self.validated_files} files validated")
        print("🚀 Ready for commit!")
        return True


def main():
    """Run critical metadata QA validation"""
    qa = CriticalMetadataQA()
    success = qa.run_validation()

    if not success:
        exit(1)

    return 0


if __name__ == "__main__":
    main()
