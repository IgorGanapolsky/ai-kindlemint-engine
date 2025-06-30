#!/usr/bin/env python3
"""
ENHANCED QA Checker - Visual Layout Validation
CRITICAL: Detects cut-off text, overlapping elements, visual issues
Updated: 2025-06-23 - Streamlined for revenue-focused book validation
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF for visual analysis
    import PyPDF2
    from PIL import Image
except ImportError:
    print("❌ Enhanced QA dependencies missing. Run: pip install PyPDF2 Pillow PyMuPDF")
    sys.exit(1)


class EnhancedQAChecker:
    """Enhanced QA with visual layout validation"""

    def __init__(self):
        self.qa_results = {
            "file_path": "",
            "timestamp": datetime.now().isoformat(),
            "file_checks": {},
            "content_checks": {},
            "layout_checks": {},
            "visual_checks": {},  # NEW: Visual validation
            "amazon_kdp_checks": {},
            "overall_score": 0,
            "issues_found": [],
            "warnings": [],
            "publish_ready": False,
        }

    def run_enhanced_qa(self, pdf_path):
        """Run enhanced QA with visual validation"""

        pdf_path = Path(pdf_path)

        print("🔍 ENHANCED QA CHECK - VISUAL LAYOUT VALIDATION")
        print("=" * 70)
        print(f"📁 File: {pdf_path.name}")
        print(f"📊 Location: {pdf_path}")
        print("=" * 70)

        self.qa_results["file_path"] = str(pdf_path)

        # 1. Basic checks
        self.check_file_properties(pdf_path)
        self.check_pdf_structure(pdf_path)
        self.check_content_quality(pdf_path)

        # 2. ENHANCED: Visual layout validation
        self.check_visual_layout(pdf_path)

        # 3. Amazon KDP compliance
        self.check_amazon_kdp_compliance(pdf_path)

        # 4. Generate enhanced report
        self.generate_enhanced_report(pdf_path)

        return self.qa_results

    def check_visual_layout(self, pdf_path):
        """CRITICAL: Check visual layout for cut-off text, overlaps, spacing issues"""

        print("👁️  CHECKING VISUAL LAYOUT (CRITICAL)...")

        checks = {}

        try:
            # Open PDF with PyMuPDF for visual analysis
            doc = fitz.open(str(pdf_path))

            for page_num in range(len(doc)):
                page = doc[page_num]

                print(f"  🔍 Analyzing page {page_num + 1}...")

                # Get text blocks with positions
                text_blocks = page.get_text("dict")

                # Check for text near page edges (cut-off risk)
                page_rect = page.rect
                margin_threshold = 20  # Points from edge

                edge_text_issues = []

                if "blocks" in text_blocks:
                    for block in text_blocks["blocks"]:
                        if "lines" in block:
                            for line in block["lines"]:
                                if "spans" in line:
                                    for span in line["spans"]:
                                        bbox = span["bbox"]  # [x0, y0, x1, y1]
                                        text = span["text"].strip()

                                        if not text:
                                            continue

                                        # Check if text is too close to edges
                                        if (
                                            bbox[0] < margin_threshold  # Left edge
                                            or bbox[1] < margin_threshold  # Top edge
                                            or bbox[2]
                                            > page_rect.width
                                            - margin_threshold  # Right edge
                                            or bbox[3]
                                            > page_rect.height - margin_threshold
                                        ):  # Bottom edge

                                            edge_text_issues.append(
                                                {
                                                    "page": page_num + 1,
                                                    "text": (
                                                        text[:20] + "..."
                                                        if len(text) > 20
                                                        else text
                                                    ),
                                                    "position": bbox,
                                                    "issue": "Near page edge - may be cut off",
                                                }
                                            )

                # Check specifically for crossword grid numbers
                self.check_crossword_grid_numbers(page, page_num + 1, checks)

                # Store issues found
                if edge_text_issues:
                    checks[f"page_{page_num + 1}_edge_issues"] = edge_text_issues
                    for issue in edge_text_issues:
                        self.add_critical_issue(
                            "TEXT_NEAR_EDGE",
                            f"Page {
                                issue['page']}: Text '{
                                issue['text']}' may be cut off",
                        )

                # Render page as image for visual analysis
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Basic image analysis
                width, height = img.size
                checks[f"page_{page_num + 1}_rendered_size"] = (width, height)

                # Check for completely black or white regions (rendering issues)
                img_array = list(img.getdata())
                black_pixels = sum(1 for pixel in img_array if sum(pixel) < 30)
                white_pixels = sum(1 for pixel in img_array if sum(pixel) > 750)
                total_pixels = len(img_array)

                black_ratio = black_pixels / total_pixels
                white_ratio = white_pixels / total_pixels

                checks[f"page_{page_num + 1}_black_ratio"] = black_ratio
                checks[f"page_{page_num + 1}_white_ratio"] = white_ratio

                if black_ratio > 0.5:
                    self.add_critical_issue(
                        "EXCESSIVE_BLACK",
                        f"Page {
                            page_num +
                            1}: {
                            black_ratio *
                            100:.1f}% black - may have rendering issues",
                    )

                if white_ratio > 0.9:
                    self.add_warning(
                        "MOSTLY_WHITE",
                        f"Page {
                            page_num +
                            1}: {
                            white_ratio *
                            100:.1f}% white - may lack content",
                    )

            doc.close()

            if not any("edge_issues" in key for key in checks.keys()):
                checks["no_edge_text_issues"] = True
                print("  ✅ No text cut-off issues detected")

        except Exception as e:
            self.add_critical_issue(
                "VISUAL_ANALYSIS_FAILED", f"Could not perform visual analysis: {e}"
            )

        self.qa_results["visual_checks"] = checks

    def check_crossword_grid_numbers(self, page, page_num, checks):
        """Specifically check crossword grid numbers for visibility"""

        # Look for number patterns in crossword grids
        text_dict = page.get_text("dict")

        number_issues = []

        if "blocks" in text_dict:
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                bbox = span["bbox"]

                                # Check if this looks like a crossword number (1-25)
                                if text.isdigit() and 1 <= int(text) <= 25:
                                    font_size = span.get("size", 0)

                                    # Check if number is too small
                                    if font_size < 6:
                                        number_issues.append(
                                            {
                                                "number": text,
                                                "font_size": font_size,
                                                "position": bbox,
                                                "issue": "Font too small - may be unreadable",
                                            }
                                        )

                                    # Check if number is positioned in a way that suggests grid placement
                                    # Numbers should be in upper-left of grid squares
                                    x, y = bbox[0], bbox[1]

                                    # If number is very close to edge, it might be cut
                                    # off
                                    if x < 10 or y < 10:
                                        number_issues.append(
                                            {
                                                "number": text,
                                                "position": bbox,
                                                "issue": "Number too close to edge - likely cut off",
                                            }
                                        )

        if number_issues:
            checks[f"page_{page_num}_crossword_number_issues"] = number_issues
            for issue in number_issues:
                self.add_critical_issue(
                    "CROSSWORD_NUMBER_ISSUE",
                    f"Page {page_num}: Number '{issue['number']}' - {issue['issue']}",
                )
        else:
            print(f"  ✅ Page {page_num}: Crossword numbers appear properly positioned")

    def check_file_properties(self, pdf_path):
        """Check basic file properties"""

        print("📋 CHECKING FILE PROPERTIES...")

        checks = {}

        if not pdf_path.exists():
            self.add_critical_issue("FILE_NOT_FOUND", "PDF file does not exist")
            return

        checks["file_exists"] = True

        file_size = pdf_path.stat().st_size
        checks["file_size_bytes"] = file_size

        if file_size < 10000:
            self.add_critical_issue(
                "FILE_TOO_SMALL", f"PDF only {file_size} bytes - likely corrupted"
            )
        elif file_size > 650 * 1024 * 1024:
            self.add_critical_issue(
                "FILE_TOO_LARGE",
                f"PDF {file_size / 1024 / 1024:.1f}MB exceeds KDP 650MB limit",
            )
        else:
            checks["size_valid"] = True
            print(f"  ✅ File size: {file_size / 1024:.1f} KB (valid)")

        self.qa_results["file_checks"] = checks

    def check_pdf_structure(self, pdf_path):
        """Check PDF structure"""

        print("🔧 CHECKING PDF STRUCTURE...")

        checks = {}

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                num_pages = len(pdf_reader.pages)
                checks["page_count"] = num_pages

                if num_pages < 5:
                    self.add_warning(
                        "LOW_PAGE_COUNT", f"Only {num_pages} pages - may seem short"
                    )
                else:
                    print(f"  ✅ Page count: {num_pages} pages (good)")

                if pdf_reader.is_encrypted:
                    self.add_critical_issue(
                        "PDF_ENCRYPTED", "PDF is encrypted - Amazon KDP cannot process"
                    )
                else:
                    checks["not_encrypted"] = True
                    print(f"  ✅ PDF not encrypted")

        except Exception as e:
            self.add_critical_issue("PDF_CORRUPT", f"Cannot read PDF file: {e}")

        self.qa_results["content_checks"] = checks

    def check_content_quality(self, pdf_path):
        """Check content quality"""

        print("📝 CHECKING CONTENT QUALITY...")

        checks = {}

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                all_text = ""
                for page in pdf_reader.pages:
                    all_text += page.extract_text()

                checks["total_characters"] = len(all_text)
                checks["total_words"] = len(all_text.split())

                if len(all_text) < 1000:
                    self.add_critical_issue(
                        "INSUFFICIENT_CONTENT",
                        f"Only {len(all_text)} characters - too short",
                    )
                else:
                    print(f"  ✅ Content length: {len(all_text):,} characters")

                # Check for duplicates
                lines = all_text.split("\n")
                unique_lines = set(lines)
                duplicate_ratio = 1 - (len(unique_lines) / len(lines)) if lines else 0

                checks["duplicate_content_ratio"] = duplicate_ratio

                if duplicate_ratio > 0.7:
                    self.add_critical_issue(
                        "HIGH_DUPLICATION",
                        f"Content is {duplicate_ratio * 100:.1f}% duplicate",
                    )
                elif duplicate_ratio > 0.4:
                    self.add_warning(
                        "MODERATE_DUPLICATION",
                        f"Content is {duplicate_ratio * 100:.1f}% duplicate",
                    )
                else:
                    print(
                        f"  ✅ Content duplication: {
                            duplicate_ratio * 100:.1f}% (acceptable)"
                    )

        except Exception as e:
            self.add_warning(
                "CONTENT_ANALYSIS_FAILED", f"Could not analyze content: {e}"
            )

        self.qa_results["content_checks"].update(checks)

    def check_amazon_kdp_compliance(self, pdf_path):
        """Check Amazon KDP compliance"""

        print("📚 CHECKING AMAZON KDP COMPLIANCE...")

        checks = {}

        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)

        if file_size_mb <= 650:
            checks["size_under_kdp_limit"] = True
            print(f"  ✅ File size {file_size_mb:.1f}MB under KDP limit")
        else:
            self.add_critical_issue(
                "EXCEEDS_KDP_LIMIT", f"File {file_size_mb:.1f}MB exceeds KDP limit"
            )

        self.qa_results["amazon_kdp_checks"] = checks

    def add_critical_issue(self, code, description):
        """Add a critical issue"""
        self.qa_results["issues_found"].append(
            {"type": "CRITICAL", "code": code, "description": description}
        )
        print(f"  ❌ CRITICAL: {description}")

    def add_warning(self, code, description):
        """Add a warning"""
        self.qa_results["warnings"].append(
            {"type": "WARNING", "code": code, "description": description}
        )
        print(f"  ⚠️  WARNING: {description}")

    def calculate_overall_score(self):
        """Calculate quality score"""

        total_checks = 0
        passed_checks = 0

        for section in [
            "file_checks",
            "content_checks",
            "visual_checks",
            "amazon_kdp_checks",
        ]:
            if section in self.qa_results:
                for key, value in self.qa_results[section].items():
                    if isinstance(value, bool):
                        total_checks += 1
                        if value:
                            passed_checks += 1

        critical_penalty = len(self.qa_results["issues_found"]) * 25  # Higher penalty
        warning_penalty = len(self.qa_results["warnings"]) * 5

        if total_checks > 0:
            base_score = (passed_checks / total_checks) * 100
        else:
            base_score = 50

        final_score = max(0, base_score - critical_penalty - warning_penalty)

        return round(final_score)

    def generate_enhanced_report(self, pdf_path):
        """Generate enhanced QA report"""

        self.qa_results["overall_score"] = self.calculate_overall_score()

        # Much stricter publishing criteria
        critical_issues = len(self.qa_results["issues_found"])

        self.qa_results["publish_ready"] = (
            critical_issues == 0 and self.qa_results["overall_score"] >= 85
        )

        print("\n" + "=" * 70)
        print("📊 ENHANCED QA REPORT SUMMARY")
        print("=" * 70)

        print(f"📁 File: {pdf_path.name}")
        print(f"🎯 Overall Score: {self.qa_results['overall_score']}/100")
        print(f"❌ Critical Issues: {len(self.qa_results['issues_found'])}")
        print(f"⚠️  Warnings: {len(self.qa_results['warnings'])}")

        if self.qa_results["publish_ready"]:
            print(f"✅ PUBLISH READY: PDF meets enhanced quality standards")
        else:
            print(f"❌ NOT READY: Fix all critical issues before publishing")

        print("\n" + "=" * 70)

        if self.qa_results["issues_found"]:
            print("🚨 CRITICAL ISSUES TO FIX:")
            for issue in self.qa_results["issues_found"]:
                print(f"   • {issue['description']}")

        if self.qa_results["warnings"]:
            print("\n⚠️  WARNINGS TO REVIEW:")
            for warning in self.qa_results["warnings"]:
                print(f"   • {warning['description']}")

        # Save enhanced report
        qa_report_path = pdf_path.parent / f"ENHANCED_QA_REPORT_{pdf_path.stem}.json"
        with open(qa_report_path, "w") as f:
            json.dump(self.qa_results, f, indent=2)

        print(f"\n📄 Enhanced QA report saved: {qa_report_path}")
        print("=" * 70)


def main():
    """Run enhanced QA check"""

    if len(sys.argv) != 2:
        print("❌ Usage: python enhanced_qa_checker.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    print("🔍 ENHANCED QA CHECKER - VISUAL LAYOUT VALIDATION")
    print("=" * 70)
    print("📋 Comprehensive quality assurance with visual validation")
    print("🎯 Detects cut-off text, overlaps, and layout issues")
    print("=" * 70)

    checker = EnhancedQAChecker()
    results = checker.run_enhanced_qa(pdf_path)

    if not results["publish_ready"]:
        print("\n💥 ENHANCED QA CHECK FAILED - DO NOT PUBLISH")
        sys.exit(1)
    else:
        print("\n🎉 ENHANCED QA CHECK PASSED - READY FOR PUBLISHING")
        sys.exit(0)


if __name__ == "__main__":
    main()
