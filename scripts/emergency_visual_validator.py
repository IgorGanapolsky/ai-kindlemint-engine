#!/usr/bin/env python3
"""
EMERGENCY Visual Validator - Actually detect the real visual issues
Replaces the broken unified validator that reports false positives
"""

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # PyMuPDF
import numpy as np
from PIL import Image


class EmergencyVisualValidator:
    """EMERGENCY validator that actually detects visual rendering issues"""

    def __init__(self):
        self.critical_issues = []
        self.analysis_results = {}

    def validate_sudoku_pdf(self, pdf_path: Path) -> Dict:
        """Validate actual visual rendering of Sudoku puzzles."""
        print(f"\n🚨 EMERGENCY VISUAL VALIDATION: {pdf_path.name}")
        print("=" * 60)

        try:
            pdf = fitz.open(str(pdf_path))

            # Check multiple puzzle pages
            puzzle_pages = [10, 20, 50, 100]
            total_issues = 0

            for page_num in puzzle_pages:
                if page_num < len(pdf):
                    print(f"\n🔍 Analyzing page {page_num}...")
                    issues = self._analyze_puzzle_page(pdf, page_num)

                    self.analysis_results[f"page_{page_num}"] = {
                        "page": page_num,
                        "critical_issues": issues,
                        "issue_count": len(issues),
                    }

                    if issues:
                        total_issues += len(issues)
                        print(
                            f"❌ Found {len(issues)} critical issues on page {page_num}"
                        )
                        for issue in issues:
                            print(f"  • {issue}")
                            self.critical_issues.append(
                                f"Page {page_num}: {issue}")
                    else:
                        print(f"✅ Page {page_num} looks correct")

            pdf.close()

            # Generate final report
            status = "CRITICAL_FAILURE" if total_issues > 0 else "PASSED"

            report = {
                "timestamp": datetime.now().isoformat(),
                "pdf_path": str(pdf_path),
                "status": status,
                "total_critical_issues": total_issues,
                "pages_analyzed": len(puzzle_pages),
                "critical_issues": self.critical_issues,
                "detailed_analysis": self.analysis_results,
                "summary": {
                    "has_visual_distinction": total_issues == 0,
                    "clues_properly_styled": total_issues == 0,
                    "puzzle_solvable": total_issues == 0,
                },
            }

            # Save emergency report
            emergency_report_path = pdf_path.parent / "EMERGENCY_VISUAL_REPORT.json"
            with open(emergency_report_path, "w") as f:
                json.dump(report, f, indent=2)

            # Print summary
            print(f"\n{'=' * 60}")
            print(f"🚨 EMERGENCY REPORT: {status}")
            print(f"{'=' * 60}")

            if total_issues > 0:
                print(f"\n❌ CRITICAL VISUAL ISSUES DETECTED: {total_issues}")
                print("\n🔥 TOP ISSUES:")
                for issue in self.critical_issues[:5]:
                    print(f"  • {issue}")
            else:
                print("\n✅ Visual rendering appears correct")

            print(f"\n📄 Emergency report: {emergency_report_path}")

            return report

        except Exception as e:
            error_report = {
                "timestamp": datetime.now().isoformat(),
                "status": "ERROR",
                "error": str(e),
                "critical_issues": [f"Failed to analyze PDF: {e}"],
            }
            print(f"❌ ERROR: {e}")
            return error_report

    def _analyze_puzzle_page(self, pdf: fitz.Document, page_num: int) -> List[str]:
        """Analyze a single puzzle page for visual issues."""
        issues = []

        try:
            page = pdf[page_num]

            # Render page to high-res image
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3)
                                  )  # 3x scale for detail
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))
            img_gray = np.array(img.convert("L"))

            # Extract puzzle grid area (center 60% of page)
            h, w = img_gray.shape
            grid_area = img_gray[
                int(h * 0.2): int(h * 0.8), int(w * 0.2): int(w * 0.8)
            ]

            # CRITICAL CHECK 1: Count filled cells
            filled_cells, empty_cells = self._count_grid_cells(grid_area)

            if filled_cells > 45:  # More than half the grid filled
                issues.append(
                    f"Too many numbers visible({
                        filled_cells}/81 cells) - appears to show solution"
                )

            if empty_cells < 30:  # Too few empty cells
                issues.append(
                    f"Too few empty cells ({empty_cells}/81) - puzzle not solvable"
                )

            # CRITICAL CHECK 2: Check for visual distinction
            if filled_cells > 0:
                has_distinction = self._check_visual_distinction(grid_area)
                if not has_distinction:
                    issues.append(
                        "No visual distinction between clues and empty cells - all numbers look identical"
                    )

            # CRITICAL CHECK 3: Check for proper clue styling
            bold_cells, regular_cells = self._analyze_number_styling(grid_area)

            if bold_cells == 0 and regular_cells > 0:
                issues.append(
                    "No bold clues found - all numbers appear in same style")

            # CRITICAL CHECK 4: Validate grid completeness
            if filled_cells == 81:
                issues.append(
                    "Complete grid detected - showing full solution instead of puzzle"
                )

            # CRITICAL CHECK 5: Check for completely empty grid
            if filled_cells == 0:
                issues.append("No numbers found - puzzle appears blank")

        except Exception as e:
            issues.append(f"Analysis failed: {str(e)}")

        return issues

    def _count_grid_cells(self, grid_area: np.ndarray) -> Tuple[int, int]:
        """Count filled vs empty cells in the grid."""
        h, w = grid_area.shape
        cell_h, cell_w = h // 9, w // 9

        filled_count = 0
        empty_count = 0

        for row in range(9):
            for col in range(9):
                # Extract cell region
                y1 = row * cell_h
                y2 = (row + 1) * cell_h
                x1 = col * cell_w
                x2 = (col + 1) * cell_w

                cell = grid_area[y1:y2, x1:x2]

                # Check if cell contains a number (dark pixels)
                if cell.size > 0:
                    np.min(cell)
                    dark_pixels = np.sum(cell < 150)  # Dark threshold
                    dark_ratio = dark_pixels / cell.size

                    if dark_ratio > 0.1:  # Significant dark content = number
                        filled_count += 1
                    else:
                        empty_count += 1

        return filled_count, empty_count

    def _check_visual_distinction(self, grid_area: np.ndarray) -> bool:
        """Check if there's visual distinction between different cell types."""
        h, w = grid_area.shape
        cell_h, cell_w = h // 9, w // 9

        cell_intensities = []

        # Sample cell intensities
        for row in range(9):
            for col in range(9):
                y1 = row * cell_h + cell_h // 4
                y2 = row * cell_h + 3 * cell_h // 4
                x1 = col * cell_w + cell_w // 4
                x2 = col * cell_w + 3 * cell_w // 4

                if y2 < h and x2 < w:
                    cell_center = grid_area[y1:y2, x1:x2]
                    if cell_center.size > 0:
                        avg_intensity = np.mean(cell_center)
                        cell_intensities.append(avg_intensity)

        if len(cell_intensities) < 10:
            return False

        # Check for variety in intensities (indicates distinction)
        intensity_std = np.std(cell_intensities)

        # If all cells look very similar, there's no distinction
        return intensity_std > 30  # Threshold for meaningful variation

    def _analyze_number_styling(self, grid_area: np.ndarray) -> Tuple[int, int]:
        """Analyze if numbers have different styling (bold vs regular)."""
        h, w = grid_area.shape
        cell_h, cell_w = h // 9, w // 9

        bold_count = 0
        regular_count = 0

        for row in range(9):
            for col in range(9):
                y1 = row * cell_h
                y2 = (row + 1) * cell_h
                x1 = col * cell_w
                x2 = (col + 1) * cell_w

                cell = grid_area[y1:y2, x1:x2]

                if cell.size > 0:
                    # Check for number presence
                    dark_pixels = np.sum(cell < 150)
                    if dark_pixels > cell.size * 0.05:  # Has a number

                        # Analyze thickness (bold detection)
                        very_dark_pixels = np.sum(
                            cell < 100)  # Very dark = bold
                        thickness_ratio = (
                            very_dark_pixels / dark_pixels if dark_pixels > 0 else 0
                        )

                        if thickness_ratio > 0.7:  # Thick/bold number
                            bold_count += 1
                        else:  # Regular number
                            regular_count += 1

        return bold_count, regular_count


def emergency_validate(pdf_path: str) -> bool:
    """Emergency validation entry point."""
    validator = EmergencyVisualValidator()
    report = validator.validate_sudoku_pdf(Path(pdf_path))

    # Return False if any critical issues found
    return report.get("total_critical_issues", 1) == 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python emergency_visual_validator.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    success = emergency_validate(pdf_path)

    print(f"\n🎯 EMERGENCY VALIDATION: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
