#!/usr/bin/env python3
"""
Comprehensive QA Validator - Strict validation for crossword puzzle books
Combines PDF validation with metadata validation for complete quality assurance
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import PyPDF2

# Import our enhanced validators
from puzzle_validators import (
    validate_crossword,
    validate_crossword_metadata,
    validate_crossword_solutions_in_pdf,
)


class ComprehensiveQAValidator:
    """Complete validation for crossword puzzle books"""

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.metadata_dir = self.book_dir / "metadata"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "book_directory": str(self.book_dir),
            "status": "PENDING",
            "score": 0,
            "critical_issues": [],
            "warnings": [],
            "passed_checks": [],
            "pdf_validation": {},
            "metadata_validation": {},
            "content_validation": {},
        }

    def validate(self) -> Dict:
        """Run all validation checks"""
        print(f"\n🔍 COMPREHENSIVE QA VALIDATION")
        print(f"📁 Book: {self.book_dir}")
        print("=" * 60)

        # 1. Check directory structure
        self._validate_directory_structure()

        # 2. Validate metadata
        if self.metadata_dir.exists():
            self._validate_metadata()

        # 3. Find and validate PDFs
        pdf_files = list(self.book_dir.glob("*.pdf"))
        if pdf_files:
            for pdf_file in pdf_files:
                if (
                    "interior" in pdf_file.name.lower()
                    or "manuscript" in pdf_file.name.lower()
                ):
                    self._validate_pdf(pdf_file)
        else:
            self.report["critical_issues"].append("No PDF files found")

        # 4. Calculate final score and status
        self._calculate_score()

        # 5. Save report
        self._save_report()

        return self.report

    def _validate_directory_structure(self):
        """Check required files and directories"""
        required_items = [
            ("metadata", "directory"),
            ("metadata/collection.json", "file"),
            ("*.pdf", "pdf_file"),
        ]

        for item, item_type in required_items:
            if item_type == "directory":
                if not (self.book_dir / item).is_dir():
                    self.report["critical_issues"].append(
                        f"Missing required directory: {item}"
                    )
                else:
                    self.report["passed_checks"].append(f"✅ Found {item} directory")
            elif item_type == "file":
                if not (self.book_dir / item).exists():
                    self.report["critical_issues"].append(
                        f"Missing required file: {item}"
                    )
                else:
                    self.report["passed_checks"].append(f"✅ Found {item}")
            elif item_type == "pdf_file":
                if not list(self.book_dir.glob(item)):
                    self.report["critical_issues"].append(f"No {item} files found")

    def _validate_metadata(self):
        """Validate all metadata files"""
        print("\n📋 Validating metadata...")

        # Load collection
        collection_file = self.metadata_dir / "collection.json"
        if not collection_file.exists():
            self.report["critical_issues"].append("collection.json not found")
            return

        with open(collection_file) as f:
            collection = json.load(f)

        puzzle_ids = collection.get("puzzles", [])
        if not puzzle_ids:
            self.report["critical_issues"].append("No puzzles listed in collection")
            return

        self.report["metadata_validation"]["total_puzzles"] = len(puzzle_ids)

        # Validate each puzzle metadata
        valid_puzzles = 0
        puzzles_with_solutions = 0

        for puzzle_id in puzzle_ids:
            puzzle_file = self.metadata_dir / f"puzzle_{puzzle_id:02d}.json"
            if not puzzle_file.exists():
                self.report["critical_issues"].append(
                    f"Missing metadata for puzzle {puzzle_id}"
                )
                continue

            with open(puzzle_file) as f:
                puzzle_data = json.load(f)

            # Check for required fields
            required_fields = ["id", "theme", "difficulty", "clues", "word_count"]
            missing_fields = [f for f in required_fields if f not in puzzle_data]
            if missing_fields:
                self.report["critical_issues"].append(
                    f"Puzzle {puzzle_id} missing fields: {', '.join(missing_fields)}"
                )
                continue

            # Check for solution data
            if "solution_grid" in puzzle_data or "solution_path" in puzzle_data:
                puzzles_with_solutions += 1

            # Validate clues have answers
            clues = puzzle_data.get("clues", {})
            empty_answers = []

            for direction in ["across", "down"]:
                for clue in clues.get(direction, []):
                    if len(clue) < 3 or not clue[2] or not clue[2].strip():
                        empty_answers.append(f"{direction} {clue[0] if clue else '?'}")

            if empty_answers:
                self.report["critical_issues"].append(
                    f"Puzzle {puzzle_id} has empty answers: {', '.join(empty_answers[:5])}"
                )
            else:
                valid_puzzles += 1

        # Run enhanced metadata validation
        metadata_issues = validate_crossword_metadata(self.metadata_dir)
        for issue in metadata_issues:
            if "placeholder" in issue.get("description", "").lower():
                self.report["critical_issues"].append(issue["description"])
            else:
                self.report["warnings"].append(issue["description"])

        self.report["metadata_validation"]["valid_puzzles"] = valid_puzzles
        self.report["metadata_validation"][
            "puzzles_with_solutions"
        ] = puzzles_with_solutions

        if valid_puzzles == len(puzzle_ids):
            self.report["passed_checks"].append(
                f"✅ All {valid_puzzles} puzzles have valid metadata"
            )
        else:
            self.report["critical_issues"].append(
                f"Only {valid_puzzles}/{len(puzzle_ids)} puzzles have valid metadata"
            )

    def _validate_pdf(self, pdf_path: Path):
        """Validate PDF content and solutions"""
        print(f"\n📄 Validating PDF: {pdf_path.name}")

        try:
            # Basic PDF validation
            with open(pdf_path, "rb") as file:
                pdf = PyPDF2.PdfReader(file)
                page_count = len(pdf.pages)

                self.report["pdf_validation"]["page_count"] = page_count

                # Check page count
                if page_count == 156:
                    self.report["passed_checks"].append("✅ Correct page count (156)")
                else:
                    self.report["critical_issues"].append(
                        f"Wrong page count: {page_count} (expected 156)"
                    )

                # Check for empty pages
                empty_pages = []
                for i in range(min(10, page_count)):
                    text = pdf.pages[i].extract_text().strip()
                    if len(text) < 50:
                        empty_pages.append(i + 1)

                if empty_pages:
                    self.report["warnings"].append(f"Nearly empty pages: {empty_pages}")

                # Check for test content
                sample_text = ""
                for i in range(min(5, page_count)):
                    sample_text += pdf.pages[i].extract_text()

                if (
                    "test" in sample_text.lower()
                    or "lorem ipsum" in sample_text.lower()
                ):
                    self.report["critical_issues"].append(
                        "Test or placeholder content found"
                    )

            # Validate solutions using our enhanced validator
            success, stats = validate_crossword_solutions_in_pdf(pdf_path)
            self.report["pdf_validation"]["solution_validation"] = stats

            if not success:
                self.report["critical_issues"].append(
                    f"Solution validation failed: {stats.get('empty_solutions', 0)} empty solutions found"
                )
                if "empty_solution_ids" in stats:
                    self.report["critical_issues"].append(
                        f"Empty solutions for puzzles: {stats['empty_solution_ids']}"
                    )
            else:
                self.report["passed_checks"].append(
                    f"✅ All {stats.get('total_solutions', 0)} solutions properly filled"
                )

            # File size check
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            self.report["pdf_validation"]["file_size_mb"] = file_size_mb

            if file_size_mb > 400:
                self.report["critical_issues"].append(
                    f"File too large: {file_size_mb:.2f} MB"
                )
            elif file_size_mb < 0.1:
                self.report["critical_issues"].append(
                    f"File too small: {file_size_mb:.2f} MB"
                )
            else:
                self.report["passed_checks"].append(
                    f"✅ File size OK: {file_size_mb:.2f} MB"
                )

        except Exception as e:
            self.report["critical_issues"].append(f"Failed to validate PDF: {str(e)}")

    def _calculate_score(self):
        """Calculate final QA score"""
        # Base score of 100
        score = 100

        # Deduct points for issues
        score -= len(self.report["critical_issues"]) * 10
        score -= len(self.report["warnings"]) * 2

        # Ensure score doesn't go below 0
        score = max(0, score)

        self.report["score"] = score

        # Determine status
        if self.report["critical_issues"]:
            self.report["status"] = "FAIL"
        elif score >= 80:
            self.report["status"] = "PASS"
        else:
            self.report["status"] = "WARN"

    def _save_report(self):
        """Save validation report"""
        report_path = self.book_dir / "comprehensive_qa_report.json"
        with open(report_path, "w") as f:
            json.dump(self.report, f, indent=2)

        print(f"\n📊 Report saved to: {report_path}")

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE QA REPORT")
        print("=" * 60)
        print(f"🎯 Score: {self.report['score']}/100")
        print(f"📋 Status: {self.report['status']}")

        if self.report["status"] == "PASS":
            print("✅ READY FOR PUBLISHING")
        else:
            print("❌ NOT READY - FIX ISSUES FIRST")

        if self.report["critical_issues"]:
            print(f"\n❌ CRITICAL ISSUES ({len(self.report['critical_issues'])}):")
            for issue in self.report["critical_issues"][:10]:
                print(f"   • {issue}")
            if len(self.report["critical_issues"]) > 10:
                print(f"   ... and {len(self.report['critical_issues']) - 10} more")

        if self.report["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.report['warnings'])}):")
            for warning in self.report["warnings"][:5]:
                print(f"   • {warning}")

        if self.report["passed_checks"]:
            print(f"\n✅ PASSED CHECKS ({len(self.report['passed_checks'])}):")
            for check in self.report["passed_checks"][:5]:
                print(f"   • {check}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive QA Validator for KDP Books"
    )
    parser.add_argument("book_dir", help="Path to book directory")
    parser.add_argument(
        "--strict", action="store_true", help="Use strict validation (fail on warnings)"
    )

    args = parser.parse_args()

    validator = ComprehensiveQAValidator(args.book_dir)
    report = validator.validate()
    validator.print_summary()

    # Exit with appropriate code
    if report["status"] == "FAIL":
        sys.exit(1)
    elif report["status"] == "WARN" and args.strict:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
