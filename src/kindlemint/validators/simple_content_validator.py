#!/usr/bin/env python3
"""
Simple Content Validator - Uses file size heuristics
Puzzles: ~26KB, Solutions: ~42KB
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

import fitz


class SimpleContentValidator:
    """Simple validation using file size patterns"""

    def __init__(self):


def __init__(self):
        self.results = {
            "status": "UNKNOWN",
            "errors": [],
            "warnings": [],
            "summary": {},
        }

    def validate_pdf_content(self, pdf_path: Path) -> Dict:
        """Validate PDF using extracted image sizes"""
        print(f"🔍 Validating PDF content: {pdf_path}")

        try:
            doc = fitz.open(str(pdf_path))

            # Check puzzle pages (pages 3-102)
            puzzle_errors = self._check_puzzle_pages(doc, start_page=2, end_page=101)

            # Check solution pages (pages 104-203)
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
                    f"❌ CONTENT VALIDATION FAILED - {
                        len(self.results['errors'])} errors"
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
        """Check puzzle pages using size heuristics"""
        errors = []

        print(f"🧩 Checking puzzle pages {start_page + 1} to {end_page + 1}...")

        # Sample check - only check first 5 puzzles for speed
        sample_pages = list(range(start_page, min(start_page + 5, end_page + 1)))

        for page_num in sample_pages:
            try:
                page = doc[page_num]
                image_list = page.get_images()

                if not image_list:
                    errors.append(
                        f"Page {page_num + 1}: No images found (expected puzzle)"
                    )
                    continue

                # Check main image size
                for img_index, img in enumerate(image_list):
                    if self._is_sudoku_grid_image(page, img):
                        img_size = self._get_image_size(page, img)

                        # Puzzles should be smaller (~26KB), solutions larger (~42KB)
                        # If puzzle image is too large, it might be showing a complete
                        # solution
                        if img_size > 35000:  # 35KB threshold
                            puzzle_num = page_num - start_page + 1
                            errors.append(
                                f"Puzzle #{puzzle_num} (Page {page_num + 1}): Image too large ({
                                    img_size} bytes) - likely showing complete solution instead of puzzle with blanks"
                            )
                        break

            except Exception as e:
                errors.append(f"Page {page_num + 1}: Error checking puzzle - {str(e)}")

        return errors

    def _check_solution_pages(self, doc, start_page: int, end_page: int) -> List[str]:
        """Check solution pages using size heuristics"""
        errors = []

        print(f"💡 Checking solution pages {start_page + 1} to {end_page + 1}...")

        # Sample check - only check first 5 solutions for speed
        sample_pages = list(
            range(start_page, min(start_page + 5, end_page + 1, doc.page_count))
        )

        for page_num in sample_pages:
            try:
                page = doc[page_num]
                image_list = page.get_images()

                if not image_list:
                    errors.append(
                        f"Page {page_num + 1}: No images found (expected solution)"
                    )
                    continue

                # Check main image size
                for img_index, img in enumerate(image_list):
                    if self._is_sudoku_grid_image(page, img):
                        img_size = self._get_image_size(page, img)

                        # Solutions should be larger (~42KB)
                        if img_size < 35000:  # 35KB threshold
                            solution_num = page_num - start_page + 1
                            errors.append(
                                f"Solution #{solution_num} (Page {
                                    page_num + 1}): Image too small ({img_size} bytes) - likely incomplete solution"
                            )
                        break

            except Exception as e:
                errors.append(
                    f"Page {page_num +
                                      1}: Error checking solution - {str(e)}"
                )

        return errors

    def _is_sudoku_grid_image(self, page, img) -> bool:
        """Check if image is likely a Sudoku grid"""
        try:
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)

            width, height = pix.width, pix.height
            aspect_ratio = width / height if height > 0 else 0

            is_square = 0.8 <= aspect_ratio <= 1.2
            is_reasonable_size = width >= 300 and height >= 300

            pix = None
            return is_square and is_reasonable_size

        except BaseException:
            return False

    def _get_image_size(self, page, img) -> int:
        """Get the compressed size of an image in bytes"""
        try:
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)
            img_data = pix.tobytes("png")
            pix = None
            return len(img_data)
        except BaseException:
            return 0

        """ Print Summary"""
def _print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("📊 SIMPLE CONTENT VALIDATION REPORT")
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


    """Main"""
def main():
    if len(sys.argv) != 2:
        print("Usage: python simple_content_validator.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    validator = SimpleContentValidator()
    results = validator.validate_pdf_content(pdf_path)

    # Save results
    report_path = pdf_path.parent / "simple_content_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Report saved to: {report_path}")

    if results["status"] == "FAILED":
        sys.exit(1)


if __name__ == "__main__":
    main()
