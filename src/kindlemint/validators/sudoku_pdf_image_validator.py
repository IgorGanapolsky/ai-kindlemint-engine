#!/usr/bin/env python3
"""
Enhanced Sudoku PDF Image Validator
Validates that puzzle images are actually rendered in the PDF
"""

import json
import sys
from pathlib import Path
from typing import Dict

import fitz  # PyMuPDF


class SudokuPDFImageValidator:
    """Validates Sudoku PDFs have proper image rendering"""

        """  Init  """
def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = []

    def validate_pdf_images(self, pdf_path: Path) -> Dict:
        """Validate that PDF contains actual puzzle images.

        Args:
            pdf_path: Path to the PDF file to validate

        Returns:
            Dictionary containing validation report with:
                - status: 'PASS' or 'FAIL'
                - total_checks: Total number of checks performed
                - passed: Number of passed checks
                - warnings: Number of warnings
                - errors: Number of errors
                - error_details: List of error messages
                - warning_details: List of warning messages
                - passed_details: List of passed check messages (first 10)
        """
        print(f"🔍 Validating PDF images: {pdf_path}")

        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(str(pdf_path))

            # Count pages and images
            total_pages = len(doc)
            puzzle_pages_with_images = 0
            solution_pages_with_images = 0
            pages_with_text_fallback = 0

            # Expected structure: ~100 puzzle pages + ~100 solution pages + extras
            expected_puzzle_pages = 100
            expected_solution_pages = 100

            # Check each page
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()
                images = page.get_images()

                # Check if this is a puzzle page
                if (
                    "Puzzle #" in text and page_num < 110
                ):  # First ~100 pages are puzzles
                    if images:
                        puzzle_pages_with_images += 1
                        self.passed_checks.append(
                            f"✓ Page {page_num + 1}: Puzzle has image"
                        )
                    else:
                        # Check for text fallback
                        if ". . ." in text or "[ Sudoku Grid ]" in text:
                            pages_with_text_fallback += 1
                            self.errors.append(
                                f"❌ Page {page_num + 1}: Puzzle using text fallback!"
                            )
                        else:
                            self.warnings.append(
                                f"⚠️ Page {page_num + 1}: No puzzle image found"
                            )

                # Check if this is a solution page
                elif "Solution to Puzzle" in text and page_num > 100:
                    if images:
                        solution_pages_with_images += 1
                        self.passed_checks.append(
                            f"✓ Page {page_num + 1}: Solution has image"
                        )
                    else:
                        # Check for text fallback
                        if "1 2 3" in text or "[ Solution Grid ]" in text:
                            pages_with_text_fallback += 1
                            self.errors.append(
                                f"❌ Page {page_num + 1}: Solution using text fallback!"
                            )
                        else:
                            self.warnings.append(
                                f"⚠️ Page {page_num + 1}: No solution image found"
                            )

            # Validate counts
            if (
                puzzle_pages_with_images < expected_puzzle_pages * 0.9
            ):  # Allow 10% margin
                self.errors.append(
                    f"❌ CRITICAL: Only {
                        puzzle_pages_with_images}/{expected_puzzle_pages} puzzle pages have images!"
                )
            else:
                self.passed_checks.append(
                    f"✓ {puzzle_pages_with_images} puzzle pages have images"
                )

            if solution_pages_with_images < expected_solution_pages * 0.9:
                self.errors.append(
                    f"❌ CRITICAL: Only {
                        solution_pages_with_images}/{expected_solution_pages} solution pages have images!"
                )
            else:
                self.passed_checks.append(
                    f"✓ {solution_pages_with_images} solution pages have images"
                )

            if pages_with_text_fallback > 0:
                self.errors.append(
                    f"❌ CRITICAL: {
                        pages_with_text_fallback} pages using text fallback instead of images!"
                )

            # Check image quality
            self._check_image_quality(doc)

            doc.close()

        except Exception as e:
            self.errors.append(f"Failed to analyze PDF: {str(e)}")

        return self._generate_report()

        """ Check Image Quality"""
def _check_image_quality(self, doc):
        """Check that images are high resolution.

        Args:
            doc: PyMuPDF document object to analyze

        Note:
            - Checks image dimensions (minimum 300x300)
            - Checks file size (minimum 10KB)
            - Adds warnings for low quality images
        """
        min_expected_size = 10000  # 10KB minimum for a decent puzzle image

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img_index, img in enumerate(page.get_images()):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)

                        # Check image dimensions
                        if pix.width < 300 or pix.height < 300:
                            self.warnings.append(
                                f"⚠️ Page {
                                    page_num +
                                    1}: Low resolution image ({
                                    pix.width}x{
                                    pix.height})"
                            )

                        # Check approximate file size
                        img_data = doc.extract_image(xref)
                        if img_data and len(img_data["image"]) < min_expected_size:
                            self.warnings.append(
                                f"⚠️ Page {
                                    page_num + 1}: Small image size ({len(img_data['image'])} bytes)"
                            )

                        pix = None  # Release pixmap
                    except Exception as e:
                        self.warnings.append(
                            f"⚠️ Could not check image on page {page_num + 1}: {str(e)}"
                        )
        except Exception as e:
            self.warnings.append(f"⚠️ Could not check image quality: {str(e)}")

    def _generate_report(self) -> Dict:
        """Generate validation report.

        Returns:
            Dictionary containing:
                - status: 'PASS' if no errors, 'FAIL' otherwise
                - total_checks: Total number of checks performed
                - passed: Number of passed checks
                - warnings: Number of warnings
                - errors: Number of errors
                - error_details: List of error messages
                - warning_details: List of warning messages
                - passed_details: First 10 passed check messages
        """
        total_checks = len(self.errors) + len(self.warnings) + len(self.passed_checks)

        report = {
            "status": "PASS" if len(self.errors) == 0 else "FAIL",
            "total_checks": total_checks,
            "passed": len(self.passed_checks),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "error_details": self.errors,
            "warning_details": self.warnings,
            "passed_details": self.passed_checks[:10],  # First 10 only
        }

        # Print summary
        print("\n" + "=" * 50)
        print("📊 PDF IMAGE VALIDATION REPORT")
        print("=" * 50)

        if report["status"] == "FAIL":
            print(f"❌ STATUS: FAILED - {len(self.errors)} critical errors found!")
        else:
            print("✅ STATUS: PASSED")

        print(f"\n📈 Summary:")
        print(f"  • Passed checks: {len(self.passed_checks)}")
        print(f"  • Warnings: {len(self.warnings)}")
        print(f"  • Errors: {len(self.errors)}")

        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors[:5]:  # Show first 5
                print(f"  • {error}")
            if len(self.errors) > 5:
                print(f"  • ... and {len(self.errors) - 5} more errors")

        print("\n" + "=" * 50)

        return report


def validate_sudoku_pdf(pdf_path: str) -> bool:
    """Main entry point for PDF image validation.

    Args:
        pdf_path: Path to the PDF file to validate

    Returns:
        True if validation passed (no errors), False otherwise

    Side Effects:
        - Creates pdf_image_validation_report.json in the same directory
        - Installs PyMuPDF if not already installed
        - Prints validation summary to console
    """
    try:
        # Install PyMuPDF if needed
        pass
    except ImportError:
        print("Installing PyMuPDF...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])

    validator = SudokuPDFImageValidator()
    report = validator.validate_pdf_images(Path(pdf_path))

    # Save report
    report_path = Path(pdf_path).parent / "pdf_image_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved to: {report_path}")

    return report["status"] == "PASS"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sudoku_pdf_image_validator.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    passed = validate_sudoku_pdf(pdf_path)

    sys.exit(0 if passed else 1)
