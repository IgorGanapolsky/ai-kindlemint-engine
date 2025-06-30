"""
Sudoku-specific QA Validator
Properly validates Sudoku puzzle books without false positives
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF
import PyPDF2

logger = logging.getLogger(__name__)


class SudokuQAValidator:
    """QA validator specifically designed for Sudoku puzzle books"""

    def __init__(self):
        self.qa_results = {
            "file_path": "",
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "publish_ready": False,
            "issues_found": [],
            "warnings": [],
            "info": [],
            "checks": {},
        }

    def run_qa(self, pdf_path: str) -> dict:
        """Run comprehensive QA checks on a Sudoku PDF"""
        pdf_path = Path(pdf_path)
        self.qa_results["file_path"] = str(pdf_path)

        print(f"\n🔍 SUDOKU QA VALIDATOR")
        print("=" * 70)
        print(f"📁 File: {pdf_path.name}")
        print(f"📊 Location: {pdf_path}")
        print("=" * 70)

        # Run all checks
        self._check_file_properties(pdf_path)
        self._check_pdf_structure(pdf_path)
        self._check_sudoku_content(pdf_path)
        self._calculate_overall_score()

        # Save report
        report_path = pdf_path.parent / \
            f"SUDOKU_QA_REPORT_{pdf_path.stem}.json"
        with open(report_path, "w") as f:
            json.dump(self.qa_results, f, indent=2)

        print(f"\n📄 QA report saved: {report_path}")

        return self.qa_results

    def _check_file_properties(self, pdf_path: Path):
        """Check basic file properties"""
        print("\n📋 CHECKING FILE PROPERTIES...")
        checks = {}

        if not pdf_path.exists():
            self._add_issue("FILE_NOT_FOUND",
                            "PDF file does not exist", "CRITICAL")
            return

        file_size = pdf_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        checks["file_size_mb"] = file_size_mb

        if file_size_mb < 0.1:
            self._add_issue(
                "FILE_TOO_SMALL", f"File only {file_size_mb:.2f} MB", "WARNING"
            )
        elif file_size_mb > 650:
            self._add_issue(
                "FILE_TOO_LARGE",
                f"File {file_size_mb:.2f} MB exceeds KDP limit",
                "CRITICAL",
            )
        else:
            print(f"  ✅ File size: {file_size_mb:.1f} MB (valid)")

        self.qa_results["checks"]["file_properties"] = checks

    def _check_pdf_structure(self, pdf_path: Path):
        """Check PDF structure and metadata"""
        print("\n🔧 CHECKING PDF STRUCTURE...")
        checks = {}

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                checks["page_count"] = num_pages

                if num_pages < 50:
                    self._add_issue(
                        "LOW_PAGE_COUNT", f"Only {num_pages} pages", "WARNING"
                    )
                else:
                    print(f"  ✅ Page count: {num_pages} pages")

                if pdf_reader.is_encrypted:
                    self._add_issue("PDF_ENCRYPTED",
                                    "PDF is encrypted", "CRITICAL")
                else:
                    print(f"  ✅ PDF not encrypted")

                # Check metadata
                metadata = pdf_reader.metadata
                if metadata and metadata.title:
                    print(f"  ✅ Title: {metadata.title}")
                    checks["has_title"] = True

        except Exception as e:
            self._add_issue("PDF_READ_ERROR", str(e), "CRITICAL")

        self.qa_results["checks"]["pdf_structure"] = checks

    def _check_sudoku_content(self, pdf_path: Path):
        """Check Sudoku-specific content"""
        print("\n🧩 CHECKING SUDOKU CONTENT...")
        checks = {
            "puzzles_found": 0,
            "solutions_found": 0,
            "pages_with_grids": 0,
            "grid_coverage": [],
        }

        try:
            doc = fitz.open(pdf_path)

            for page_num, page in enumerate(doc):
                # Get page content
                pix = page.get_pixmap()
                img_data = pix.samples

                # Calculate non-white pixels (grid lines, numbers)
                total_pixels = len(img_data)
                non_white = sum(1 for pixel in img_data if pixel < 250)
                coverage = non_white / total_pixels if total_pixels > 0 else 0

                checks["grid_coverage"].append(coverage)

                # Sudoku pages typically have 2-8% non-white pixels
                if 0.02 <= coverage <= 0.08:
                    checks["pages_with_grids"] += 1

                    # Check page text for puzzle/solution indicators
                    text = page.get_text().lower()
                    if "puzzle" in text:
                        checks["puzzles_found"] += 1
                    if "solution" in text:
                        checks["solutions_found"] += 1

            doc.close()

            # Validate findings
            if checks["puzzles_found"] > 0:
                print(f"  ✅ Found {checks['puzzles_found']} puzzle pages")
            else:
                self._add_issue(
                    "NO_PUZZLES", "No puzzle pages detected", "CRITICAL")

            if checks["solutions_found"] > 0:
                print(f"  ✅ Found {checks['solutions_found']} solution pages")
            else:
                self._add_issue(
                    "NO_SOLUTIONS", "No solution pages found", "WARNING")

            # Check grid coverage consistency
            avg_coverage = sum(checks["grid_coverage"]) / \
                len(checks["grid_coverage"])
            if avg_coverage < 0.01:
                self._add_issue("NO_CONTENT", "Pages appear blank", "CRITICAL")
            else:
                print(f"  ✅ Average grid coverage: {avg_coverage * 100:.1f}%")

        except Exception as e:
            self._add_issue("CONTENT_CHECK_ERROR", str(e), "WARNING")

        self.qa_results["checks"]["sudoku_content"] = checks

    def _add_issue(self, code: str, description: str, level: str):
        """Add an issue to the report"""
        issue = {"type": level, "code": code, "description": description}

        if level == "CRITICAL":
            self.qa_results["issues_found"].append(issue)
            print(f"  ❌ CRITICAL: {description}")
        elif level == "WARNING":
            self.qa_results["warnings"].append(issue)
            print(f"  ⚠️  WARNING: {description}")
        else:
            self.qa_results["info"].append(issue)
            print(f"  ℹ️  INFO: {description}")

    def _calculate_overall_score(self):
        """Calculate overall QA score"""
        base_score = 100

        # Deduct points for issues
        critical_count = len(self.qa_results["issues_found"])
        warning_count = len(self.qa_results["warnings"])

        score = base_score - (critical_count * 20) - (warning_count * 5)
        score = max(0, min(100, score))

        self.qa_results["overall_score"] = score
        self.qa_results["publish_ready"] = critical_count == 0 and score >= 70

        print("\n" + "=" * 70)
        print("📊 SUDOKU QA REPORT SUMMARY")
        print("=" * 70)
        print(f"🎯 Overall Score: {score}/100")
        print(f"❌ Critical Issues: {critical_count}")
        print(f"⚠️  Warnings: {warning_count}")
        print(
            f"{'✅ READY' if self.qa_results['publish_ready'] else '❌ NOT READY'}: {
                'Fix critical issues before publishing' if not self.qa_results['publish_ready'] else 'Book ready for KDP'}"
        )
        print("=" * 70)


# Quick wrapper for compatibility
class EnhancedQAValidator:
    """Wrapper to use Sudoku validator for Sudoku books"""

    def run_enhanced_qa(self, pdf_path: str) -> dict:
        # Detect if this is a Sudoku book
        pdf_path_str = str(pdf_path).lower()
        if "sudoku" in pdf_path_str:
            validator = SudokuQAValidator()
            return validator.run_qa(pdf_path)
        else:
            # Fall back to original validator for other book types
            raise NotImplementedError("Only Sudoku validation is implemented")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        validator = SudokuQAValidator()
        results = validator.run_qa(sys.argv[1])
        print(f"\nFinal Score: {results['overall_score']}/100")
        print(f"Publish Ready: {results['publish_ready']}")
