#!/usr/bin/env python3
"""
UNIFIED Sudoku QA Validator - Single Source of Truth
Replaces all the contradicting validators with one comprehensive check
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF for visual validation
import numpy as np
import PyPDF2
from PIL import Image


class UnifiedSudokuQAValidator:
    """THE ONLY validator you should use for Sudoku books"""

    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING",
            "critical_errors": [],
            "errors": [],
            "warnings": [],
            "passed": [],
            "visual_validation": {},
            "content_validation": {},
            "summary": {},
        }

    def validate_book(self, pdf_path: Path) -> Dict:
        """Run ALL validations and produce ONE report."""
        print(f"\n🔍 UNIFIED QA VALIDATION: {pdf_path.name}")
        print("=" * 60)

        if not pdf_path.exists():
            self.report["critical_errors"].append(f"PDF file not found: {pdf_path}")
            self.report["status"] = "FAILED"
            return self.report

        # 1. Visual Validation - Most Important!
        print("\n📸 Visual Validation (what customers actually see)...")
        self._validate_visual_rendering(pdf_path)

        # 2. Content Validation
        print("\n📄 Content Validation...")
        self._validate_content_structure(pdf_path)

        # 3. Puzzle Data Validation
        print("\n🧩 Puzzle Data Validation...")
        puzzle_dir = pdf_path.parent.parent / "puzzles"
        if puzzle_dir.exists():
            self._validate_puzzle_data(puzzle_dir)

        # 4. Generate Final Status
        self._determine_final_status()

        # 5. Save the ONE TRUE REPORT
        self._save_report(pdf_path)

        return self.report

    def _validate_visual_rendering(self, pdf_path: Path):
        """ACTUALLY check what the PDF looks like visually."""
        try:
            pdf = fitz.open(str(pdf_path))

            # Sample puzzle pages
            puzzle_pages_checked = 0
            visual_issues = []

            for page_num in [10, 20, 50, 100]:  # Sample pages
                if page_num < len(pdf):
                    page = pdf[page_num]

                    # Render page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale
                    img_data = pix.tobytes("png")

                    # Analyze the image
                    from io import BytesIO

                    img = Image.open(BytesIO(img_data))
                    img_array = np.array(img.convert("L"))  # Grayscale

                    # Check for visual distinction
                    result = self._analyze_puzzle_visual(img_array, page_num)
                    if result["has_issues"]:
                        visual_issues.extend(result["issues"])

                    puzzle_pages_checked += 1

                    # Store visual check result
                    self.report["visual_validation"][f"page_{page_num}"] = result

            # Report findings
            if visual_issues:
                for issue in visual_issues:
                    self.report["critical_errors"].append(f"❌ VISUAL: {issue}")
            else:
                self.report["passed"].append(
                    f"✅ Visual rendering looks correct ({puzzle_pages_checked} pages checked)"
                )

            pdf.close()

        except Exception as e:
            self.report["critical_errors"].append(
                f"❌ Visual validation failed: {str(e)}"
            )

    def _analyze_puzzle_visual(self, img_array: np.ndarray, page_num: int) -> Dict:
        """Analyze puzzle image for proper clue rendering."""
        h, w = img_array.shape
        issues = []

        # Extract puzzle area (center of page)
        puzzle_area = img_array[
            int(h * 0.2) : int(h * 0.8), int(w * 0.2) : int(w * 0.8)
        ]

        # Count dark regions (numbers)
        dark_threshold = 100
        dark_pixels = np.sum(puzzle_area < dark_threshold)
        total_pixels = puzzle_area.size
        dark_ratio = dark_pixels / total_pixels

        # Check for visual patterns
        if dark_ratio > 0.15:  # Too many numbers
            issues.append(
                f"Page {page_num}: Appears to show complete solution (too many numbers visible)"
            )

        # Check for contrast in cells
        # A proper puzzle should have high contrast between filled and empty cells
        cell_samples = self._sample_cells(puzzle_area)
        contrast_ratios = []

        for cell in cell_samples:
            if cell.size > 0:
                min_val = np.min(cell)
                max_val = np.max(cell)
                contrast = max_val - min_val
                contrast_ratios.append(contrast)

        avg_contrast = np.mean(contrast_ratios) if contrast_ratios else 0

        if avg_contrast < 100:  # Low contrast = all cells look similar
            issues.append(
                f"Page {page_num}: No visual distinction between clues and empty cells"
            )

        return {
            "page": page_num,
            "has_issues": len(issues) > 0,
            "issues": issues,
            "dark_ratio": float(dark_ratio),
            "avg_contrast": float(avg_contrast),
        }

    def _sample_cells(self, puzzle_area: np.ndarray) -> List[np.ndarray]:
        """Sample individual cells from puzzle grid."""
        cells = []
        h, w = puzzle_area.shape

        # Estimate cell size (9x9 grid)
        cell_h = h // 9
        cell_w = w // 9

        # Sample some cells
        for i in range(0, 9, 3):  # Every 3rd row
            for j in range(0, 9, 3):  # Every 3rd col
                y1 = i * cell_h
                y2 = (i + 1) * cell_h
                x1 = j * cell_w
                x2 = (j + 1) * cell_w

                if y2 <= h and x2 <= w:
                    cell = puzzle_area[y1:y2, x1:x2]
                    cells.append(cell)

        return cells

    def _validate_content_structure(self, pdf_path: Path):
        """Check PDF structure and content."""
        try:
            with open(pdf_path, "rb") as f:
                pdf = PyPDF2.PdfReader(f)
                num_pages = len(pdf.pages)

                # Basic structure checks
                if num_pages < 200:
                    self.report["warnings"].append(
                        f"⚠️ Only {num_pages} pages (expected 200+)"
                    )
                else:
                    self.report["passed"].append(f"✅ Page count OK: {num_pages}")

                # Check for solutions section
                solution_found = False
                for i in range(max(0, num_pages - 110), num_pages):
                    if i < num_pages:
                        text = pdf.pages[i].extract_text()
                        if "solution" in text.lower():
                            solution_found = True
                            break

                if not solution_found:
                    self.report["errors"].append("❌ No solutions section found")
                else:
                    self.report["passed"].append("✅ Solutions section exists")

        except Exception as e:
            self.report["errors"].append(f"❌ Content validation error: {str(e)}")

    def _validate_puzzle_data(self, puzzle_dir: Path):
        """Validate puzzle JSON/PNG consistency."""
        metadata_dir = puzzle_dir / "metadata"
        puzzles_dir = puzzle_dir / "puzzles"

        if not metadata_dir.exists():
            self.report["warnings"].append("⚠️ No puzzle metadata found")
            return

        json_files = list(metadata_dir.glob("sudoku_puzzle_*.json"))

        # Check a sample
        mismatches = 0
        for json_file in json_files[:10]:
            with open(json_file, "r") as f:
                data = json.load(f)

            puzzle_id = data.get("id", 0)
            clue_count = data.get("clue_count", 0)

            # Verify puzzle has appropriate blanks
            grid = data.get("initial_grid", [])
            actual_clues = sum(1 for row in grid for cell in row if cell != 0)

            if actual_clues != clue_count:
                mismatches += 1
                self.report["errors"].append(
                    f"❌ Puzzle {puzzle_id}: Metadata mismatch ({actual_clues} vs {clue_count} clues)"
                )

        if mismatches == 0:
            self.report["passed"].append("✅ Puzzle data consistency OK")

    def _determine_final_status(self):
        """Determine overall PASS/FAIL status."""
        if self.report["critical_errors"]:
            self.report["status"] = "FAILED - CRITICAL"
            self.report["summary"]["reason"] = "Critical visual rendering issues"
        elif self.report["errors"]:
            self.report["status"] = "FAILED"
            self.report["summary"]["reason"] = "Content/structure errors"
        elif self.report["warnings"]:
            self.report["status"] = "PASSED WITH WARNINGS"
            self.report["summary"]["reason"] = "Minor issues found"
        else:
            self.report["status"] = "PASSED"
            self.report["summary"]["reason"] = "All checks passed"

        # Summary stats
        self.report["summary"]["total_checks"] = (
            len(self.report["critical_errors"])
            + len(self.report["errors"])
            + len(self.report["warnings"])
            + len(self.report["passed"])
        )
        self.report["summary"]["visual_checks"] = len(self.report["visual_validation"])

    def _save_report(self, pdf_path: Path):
        """Save the ONE unified report."""
        report_path = pdf_path.parent / "UNIFIED_QA_REPORT.json"

        # Archive old conflicting reports
        old_reports = [
            "qa_report.json",
            "pdf_image_validation_report.json",
            "simple_content_validation_report.json",
            "sudoku_content_validation_report.json",
        ]

        archive_dir = pdf_path.parent / "archived_reports"
        archive_dir.mkdir(exist_ok=True)

        for old_report in old_reports:
            old_path = pdf_path.parent / old_report
            if old_path.exists():
                old_path.rename(archive_dir / old_report)

        # Save new unified report
        with open(report_path, "w") as f:
            json.dump(self.report, f, indent=2)

        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 UNIFIED QA REPORT: {self.report['status']}")
        print(f"{'='*60}")

        if self.report["critical_errors"]:
            print("\n❌ CRITICAL ERRORS:")
            for err in self.report["critical_errors"][:5]:
                print(f"  • {err}")

        if self.report["errors"]:
            print("\n❌ ERRORS:")
            for err in self.report["errors"][:5]:
                print(f"  • {err}")

        print(f"\n📄 Full report: {report_path}")
        print(f"🗄️  Old reports archived to: {archive_dir}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python unified_sudoku_qa_validator.py <pdf_path>")
        sys.exit(1)

    validator = UnifiedSudokuQAValidator()
    report = validator.validate_book(Path(sys.argv[1]))

    sys.exit(0 if report["status"] in ["PASSED", "PASSED WITH WARNINGS"] else 1)
