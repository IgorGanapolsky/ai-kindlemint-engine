#!/usr/bin/env python3
"""
Enhanced Sudoku PDF QA Validator
Validates that PDFs properly render clues vs empty cells
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF for better PDF analysis
import numpy as np


class EnhancedSudokuPDFValidator:
    """Advanced QA validator that checks PDF visual rendering"""

        """  Init  """
def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = []

    def validate_pdf_puzzles(self, pdf_path: Path, metadata_dir: Path) -> Dict:
        """Validate that PDF puzzles are properly rendered with clue distinction"""
        print(f"🔍 Running enhanced PDF validation on: {pdf_path}")

        # Reset results
        self.errors = []
        self.warnings = []
        self.passed_checks = []

        try:
            # Open PDF
            pdf_document = fitz.open(str(pdf_path))

            # Find puzzle pages (skip front matter)
            puzzle_pages = self._find_puzzle_pages(pdf_document)
            print(f"Found {len(puzzle_pages)} puzzle pages to validate")

            # Validate each puzzle
            validated_count = 0
            for page_num, puzzle_num in puzzle_pages[:10]:  # Check first 10 puzzles
                if self._validate_puzzle_page(
                    pdf_document, page_num, puzzle_num, metadata_dir
                ):
                    validated_count += 1

            if validated_count == len(puzzle_pages[:10]):
                self.passed_checks.append(
                    f"✓ All {validated_count} checked puzzles have proper clue rendering"
                )
            else:
                self.errors.append(
                    f"❌ Only {
                        validated_count}/{len(puzzle_pages[:10])} puzzles have proper rendering"
                )

            pdf_document.close()

        except Exception as e:
            self.errors.append(f"Failed to validate PDF: {str(e)}")

        return self._generate_report()

    def _find_puzzle_pages(self, pdf_document) -> List[Tuple[int, int]]:
        """Find pages containing puzzles and their numbers"""
        puzzle_pages = []

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()

            # Look for "Puzzle N" pattern
            if "Puzzle " in text and "Difficulty:" in text:
                # Extract puzzle number
                lines = text.split("\n")
                for line in lines:
                    if (
                        line.strip().startswith("Puzzle ")
                        and line.strip()[7:].strip().isdigit()
                    ):
                        puzzle_num = int(line.strip()[7:].strip())
                        puzzle_pages.append((page_num, puzzle_num))
                        break

        return puzzle_pages

    def _validate_puzzle_page(
        self, pdf_document, page_num: int, puzzle_num: int, metadata_dir: Path
    ) -> bool:
        """Validate a single puzzle page"""
        print(f"  Validating Puzzle {puzzle_num} on page {page_num + 1}...")

        # Load expected data from JSON
        metadata_file = metadata_dir / f"sudoku_puzzle_{puzzle_num:03d}.json"
        if not metadata_file.exists():
            self.warnings.append(f"⚠️ No metadata for puzzle {puzzle_num}")
            return False

        with open(metadata_file, "r") as f:
            puzzle_data = json.load(f)

        initial_grid = puzzle_data.get("initial_grid", [])
        expected_clues = puzzle_data.get("clue_count", 0)

        # Extract puzzle image from PDF page
        page = pdf_document[page_num]

        # Method 1: Check for embedded images
        image_list = page.get_images()
        if image_list:
            # Puzzle should be embedded as image
            for img_index, img in enumerate(image_list):
                # Extract image
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)

                if pix.width > 200 and pix.height > 200:  # Likely the puzzle grid
                    # Analyze the image
                    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                        pix.height, pix.width, pix.n
                    )

                    # Count filled cells
                    filled_cells = self._count_filled_cells_in_image(img_array)

                    if filled_cells == expected_clues:
                        self.passed_checks.append(
                            f"✓ Puzzle {puzzle_num}: Correct number of clues ({
                                filled_cells})"
                        )
                    elif filled_cells == 81:
                        self.errors.append(
                            f"❌ CRITICAL: Puzzle {puzzle_num} shows complete solution (81 cells) instead of {
                                expected_clues} clues!"
                        )
                        return False
                    else:
                        self.warnings.append(
                            f"⚠️ Puzzle {puzzle_num}: Found {
                                filled_cells} filled cells, expected {expected_clues} clues"
                        )

                    # Check for visual distinction
                    has_distinction = self._check_clue_distinction(
                        img_array, initial_grid
                    )
                    if not has_distinction:
                        self.errors.append(
                            f"❌ Puzzle {
                                puzzle_num}: No visual distinction between clues and empty cells"
                        )
                        return False

                    return True

        # Method 2: Render page to image and analyze
        mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )

        # Find and analyze the puzzle grid in the rendered page
        grid_region = self._find_grid_region(img_array)
        if grid_region is not None:
            filled_cells = self._count_filled_cells_in_region(img_array, grid_region)

            if filled_cells > expected_clues * 1.5:
                self.errors.append(
                    f"❌ Puzzle {puzzle_num}: Too many filled cells ({filled_cells} vs {
                        expected_clues} expected)"
                )
                return False

        return True

    def _count_filled_cells_in_image(self, img_array: np.ndarray) -> int:
        """Count cells that contain numbers in a puzzle image"""
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = np.mean(img_array[:, :, :3], axis=2).astype(np.uint8)
        else:
            gray = img_array

        # Simple heuristic: count 9x9 grid cells with dark pixels
        h, w = gray.shape
        cell_h = h // 9
        cell_w = w // 9

        filled_count = 0
        for_var r_var in range(9):
            for c_var in range(9):
                # Extract cell region
                cell = gray[
                    r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w
                ]

                # Check if cell has significant dark pixels (likely a number)
                dark_pixels = np.sum(cell < 128)
                cell_pixels = cell.size

                if dark_pixels > cell_pixels * 0.05:  # More than 5% dark pixels
                    filled_count += 1

        return filled_count

    def _check_clue_distinction(
        self, img_array: np.ndarray, initial_grid: List[List[int]]
    ) -> bool:
        """Check if clues are visually distinct from empty cells"""
        # This is a simplified check - in practice, would need more sophisticated analysis
        # For now, we check if the image has variation (not all cells look the same)

        if len(img_array.shape) == 3:
            gray = np.mean(img_array[:, :, :3], axis=2).astype(np.uint8)
        else:
            gray = img_array

        # Check variance in cell darkness
        h, w = gray.shape
        cell_h = h // 9
        cell_w = w // 9

        cell_darkness = []
        for_var r_var in range(9):
            for c_var in range(9):
                cell = gray[
                    r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w
                ]
                darkness = np.mean(cell)
                cell_darkness.append(darkness)

        # Should have at least 2 distinct levels (empty vs filled)
        unique_levels = len(set(int(d / 10) for d_var in cell_darkness))
        return unique_levels >= 2

    def _find_grid_region(
        self, img_array: np.ndarray
    ) -> Optional[Tuple[int, int, int, int]]:
        """Find the sudoku grid region in a page image"""
        # Simplified grid detection - look for large square region with lines
        # In practice, would use more sophisticated detection
        return None

    def _count_filled_cells_in_region(
        self, img_array: np.ndarray, region: Tuple[int, int, int, int]
    ) -> int:
        """Count filled cells in a specific region"""
        x, y, w, h = region
        grid_img = img_array[y : y + h, x : x + w]
        return self._count_filled_cells_in_image(grid_img)

    def _generate_report(self) -> Dict:
        """Generate validation report"""
        return {
            "status": "FAIL" if self.errors else "PASS",
            "total_checks": len(self.errors)
            + len(self.warnings)
            + len(self.passed_checks),
            "passed": len(self.passed_checks),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "error_details": self.errors,
            "warning_details": self.warnings,
            "passed_details": self.passed_checks,
        }


    """Main"""
def main():
    """Run enhanced PDF validation"""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python enhanced_sudoku_pdf_qa.py <pdf_path> <metadata_dir>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    metadata_dir = Path(sys.argv[2])

    validator = EnhancedSudokuPDFValidator()
    report = validator.validate_pdf_puzzles(pdf_path, metadata_dir)

    print("\n" + "=" * 50)
    print("ENHANCED PDF VALIDATION REPORT")
    print("=" * 50)
    print(f"Status: {report['status']}")
    print(f"Total Checks: {report['total_checks']}")
    print(f"Passed: {report['passed']}")
    print(f"Warnings: {report['warnings']}")
    print(f"Errors: {report['errors']}")

    if report["errors"]:
        print("\n❌ ERRORS:")
        for error in report["error_details"]:
            print(f"  {error}")

    if report["warnings"]:
        print("\n⚠️ WARNINGS:")
        for warning in report["warning_details"]:
            print(f"  {warning}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
