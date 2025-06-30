#!/usr/bin/env python3
"""
Enhanced Sudoku Content Validator - Validates actual puzzle content
Checks that puzzles have blanks and solutions are complete
"""

import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Dict, List

import fitz  # PyMuPDF
from PIL import Image


class SudokuContentValidator:
    """Validates actual Sudoku content in PDFs and images"""

    def __init__(self):
        self.results = {
            "status": "UNKNOWN",
            "errors": [],
            "warnings": [],
            "puzzle_checks": [],
            "solution_checks": [],
            "summary": {},
        }

    def validate_pdf_content(self, pdf_path: Path) -> Dict:
        """Validate actual Sudoku content in PDF"""
        print(f"🔍 Validating PDF content: {pdf_path}")

        try:
            doc = fitz.open(str(pdf_path))

            # Check puzzle pages (pages 3-102, assuming 100 puzzles)
            puzzle_errors = self._check_puzzle_pages(doc, start_page=2, end_page=101)

            # Check solution pages (pages 104-203, assuming 100 solutions)
            solution_errors = self._check_solution_pages(
                doc, start_page=103, end_page=202
            )

            doc.close()

            # Compile results
            self.results["errors"].extend(puzzle_errors)
            self.results["errors"].extend(solution_errors)

            if not self.results["errors"]:
                self.results["status"] = "PASSED"
                print("✅ CONTENT VALIDATION PASSED")
            else:
                self.results["status"] = "FAILED"
                print(
                    f"❌ CONTENT VALIDATION FAILED - {len(self.results['errors'])} errors"
                )

            self._print_summary()
            return self.results

        except Exception as e:
            error_msg = f"Failed to validate PDF content: {str(e)}"
            self.results["errors"].append(error_msg)
            self.results["status"] = "ERROR"
            print(f"❌ {error_msg}")
            return self.results

    def _check_puzzle_pages(self, doc, start_page: int, end_page: int) -> List[str]:
        """Check that puzzle pages contain blanks (not complete grids)"""
        errors = []

        print(f"🧩 Checking puzzle pages {start_page+1} to {end_page+1}...")

        for page_num in range(start_page, min(end_page + 1, doc.page_count)):
            try:
                page = doc[page_num]

                # Extract images from page
                image_list = page.get_images()

                if not image_list:
                    errors.append(
                        f"Page {page_num+1}: No images found (expected puzzle)"
                    )
                    continue

                # Check the main image (should be a puzzle with blanks)
                for img_index, img in enumerate(image_list):
                    if self._is_sudoku_grid_image(page, img):
                        is_complete = self._check_if_grid_complete(page, img)
                        if is_complete:
                            puzzle_num = page_num - start_page + 1
                            errors.append(
                                f"Puzzle #{puzzle_num} (Page {page_num+1}): Shows complete solution instead of puzzle with blanks"
                            )
                        break

            except Exception as e:
                errors.append(
                    f"Page {page_num+1}: Error checking puzzle content - {str(e)}"
                )

        return errors

    def _check_solution_pages(self, doc, start_page: int, end_page: int) -> List[str]:
        """Check that solution pages contain complete grids"""
        errors = []

        print(f"💡 Checking solution pages {start_page+1} to {end_page+1}...")

        for page_num in range(start_page, min(end_page + 1, doc.page_count)):
            try:
                page = doc[page_num]

                # Extract images from page
                image_list = page.get_images()

                if not image_list:
                    errors.append(
                        f"Page {page_num+1}: No images found (expected solution)"
                    )
                    continue

                # Check the main image (should be a complete solution)
                for img_index, img in enumerate(image_list):
                    if self._is_sudoku_grid_image(page, img):
                        is_complete = self._check_if_grid_complete(page, img)
                        if not is_complete:
                            solution_num = page_num - start_page + 1
                            errors.append(
                                f"Solution #{solution_num} (Page {page_num+1}): Incomplete solution grid"
                            )
                        break

            except Exception as e:
                errors.append(
                    f"Page {page_num+1}: Error checking solution content - {str(e)}"
                )

        return errors

    def _is_sudoku_grid_image(self, page, img) -> bool:
        """Check if image is likely a Sudoku grid"""
        try:
            # Get image dimensions
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)

            # Check if image is roughly square and reasonable size for Sudoku
            width, height = pix.width, pix.height
            aspect_ratio = width / height if height > 0 else 0

            # Sudoku grids should be roughly square and reasonably sized
            is_square = 0.8 <= aspect_ratio <= 1.2
            is_reasonable_size = width >= 300 and height >= 300

            pix = None  # Free memory
            return is_square and is_reasonable_size

        except:
            return False

    def _check_if_grid_complete(self, page, img) -> bool:
        """Check if Sudoku grid is complete using pixel analysis"""
        try:
            # Extract image
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            pil_img = Image.open(BytesIO(img_data))

            # Convert to grayscale for analysis
            gray_img = pil_img.convert("L")

            # Calculate image statistics
            # Complete grids have more text/numbers (darker pixels)
            # Puzzle grids with blanks have more white space

            # Count pixels in different brightness ranges
            pixel_data = list(gray_img.getdata())
            total_pixels = len(pixel_data)

            # Count very bright pixels (likely empty cells)
            bright_pixels = sum(1 for p in pixel_data if p > 240)

            # Count medium pixels (likely numbers/text)
            text_pixels = sum(1 for p in pixel_data if 50 <= p <= 200)

            # Calculate ratios
            bright_ratio = bright_pixels / total_pixels
            text_ratio = text_pixels / total_pixels

            # Heuristic: Complete grids have more text/numbers, less white space
            # Puzzle grids have more white space in empty cells
            # Based on analysis: solutions have ~42KB files, puzzles have ~26KB files
            is_complete = text_ratio > 0.12 and bright_ratio < 0.65

            pix = None  # Free memory
            return is_complete

        except Exception as e:
            print(f"Warning: Could not analyze grid completeness - {str(e)}")
            return False  # Assume incomplete if can't determine

    def _print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("📊 SUDOKU CONTENT VALIDATION REPORT")
        print("=" * 50)
        print(f"✅ STATUS: {self.results['status']}")
        print(f"\n📈 Summary:")
        print(f"  • Errors: {len(self.results['errors'])}")
        print(f"  • Warnings: {len(self.results['warnings'])}")

        if self.results["errors"]:
            print(f"\n❌ ERRORS FOUND:")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"  {i}. {error}")

        print("=" * 50)


def main():
    if len(sys.argv) != 2:
        print("Usage: python sudoku_content_validator.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    print("🔍 Starting enhanced content validation...")

    validator = SudokuContentValidator()
    results = validator.validate_pdf_content(pdf_path)

    # Save results
    report_path = pdf_path.parent / "sudoku_content_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Full report saved to: {report_path}")

    # Exit with error code if validation failed
    if results["status"] == "FAILED":
        sys.exit(1)


if __name__ == "__main__":
    main()
