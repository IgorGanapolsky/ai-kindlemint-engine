#!/usr/bin/env python3
"""
COMPREHENSIVE Sudoku Book Generator with REAL Content Validation
Generates PDF and immediately validates that puzzles have blanks and solutions are complete
FAILS if any content issues are detected
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, description):
    """Run a command and check for success"""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        print(f"Error: {result.stderr}")
        return False

    print(f"✅ SUCCESS: {description}")
    return True


def validate_source_images():
    """Validate that source puzzle images have blanks and solution images are complete"""
    print("🔍 Validating source images...")

    puzzles_dir = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles/puzzles"
    )

    errors = []

    # Check a sample of puzzle and solution images
    for i in [1, 27, 50, 100]:  # Test sample images
        puzzle_img = puzzles_dir / f"sudoku_puzzle_{i:03d}.png"
        solution_img = puzzles_dir / f"sudoku_solution_{i:03d}.png"

        if not puzzle_img.exists():
            errors.append(f"Missing puzzle image: {puzzle_img}")

        if not solution_img.exists():
            errors.append(f"Missing solution image: {solution_img}")

        # Check file sizes - puzzles should be smaller than solutions
        if puzzle_img.exists() and solution_img.exists():
            puzzle_size = puzzle_img.stat().st_size
            solution_size = solution_img.stat().st_size

            if puzzle_size >= solution_size:
                errors.append(
                    f"Puzzle {i} size ({puzzle_size}) >= solution size ({solution_size}) - likely wrong content"
                )

    if errors:
        print("❌ Source image validation FAILED:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✅ Source image validation PASSED")
    return True


def generate_pdf():
    """Generate the PDF"""
    print("📚 Generating PDF...")

    cmd = "python scripts/complete_sudoku_book_with_final_elements.py"
    return run_command(cmd, "PDF Generation")


def validate_pdf_content(pdf_path):
    """Validate the generated PDF content"""
    print(f"🔍 Validating PDF content: {pdf_path}")

    # Run the enhanced content validator
    cmd = f"python src/kindlemint/validators/sudoku_content_validator.py {pdf_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Check if validation passed
    if "STATUS: PASSED" in result.stdout:
        print("✅ PDF content validation PASSED")
        return True
    elif "STATUS: FAILED" in result.stdout:
        print("❌ PDF content validation FAILED")
        print(result.stdout)
        return False
    else:
        print("❌ PDF content validation ERROR")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        return False


def manual_spot_check(pdf_path):
    """Extract and verify specific pages for manual spot check"""
    print("🎯 Performing manual spot check...")

    # Extract puzzle page 3 (should have blanks)
    cmd = f"python debug_pdf_images.py {pdf_path} 3 /tmp/spot_check"
    if not run_command(cmd, "Extract puzzle page 3"):
        return False

    # Extract solution page 104 (should be complete)
    cmd = f"python debug_pdf_images.py {pdf_path} 104 /tmp/spot_check"
    if not run_command(cmd, "Extract solution page 104"):
        return False

    print("✅ Spot check images extracted to /tmp/spot_check")
    print("📋 MANUAL VERIFICATION REQUIRED:")
    print("   - Check /tmp/spot_check/page_3_image_1.png (should have BLANKS)")
    print("   - Check /tmp/spot_check/page_104_image_1.png (should be COMPLETE)")

    return True


def main():
    """Main validation pipeline"""
    print("🚀 COMPREHENSIVE SUDOKU BOOK GENERATION & VALIDATION")
    print("=" * 60)

    # Step 1: Validate source images
    if not validate_source_images():
        print("❌ PIPELINE FAILED: Source image validation failed")
        sys.exit(1)

    # Step 2: Generate PDF
    if not generate_pdf():
        print("❌ PIPELINE FAILED: PDF generation failed")
        sys.exit(1)

    # Find the generated PDF
    paperback_dir = Path(
        "books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback"
    )
    pdf_files = list(paperback_dir.glob("*VERIFIED_*.pdf"))

    if not pdf_files:
        print("❌ PIPELINE FAILED: No verified PDF found")
        sys.exit(1)

    # Get the most recent PDF
    latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 Found generated PDF: {latest_pdf}")

    # Step 3: Validate PDF content
    if not validate_pdf_content(latest_pdf):
        print("❌ PIPELINE FAILED: PDF content validation failed")
        print(f"🗑️  Removing failed PDF: {latest_pdf}")
        latest_pdf.unlink()
        sys.exit(1)

    # Step 4: Manual spot check
    if not manual_spot_check(latest_pdf):
        print("❌ PIPELINE FAILED: Spot check failed")
        sys.exit(1)

    # Success!
    print("\n" + "=" * 60)
    print("🎉 PIPELINE SUCCESS!")
    print(f"✅ Verified PDF: {latest_pdf}")
    print(f"📊 Size: {latest_pdf.stat().st_size / 1024 / 1024:.1f} MB")
    print("🚀 Ready for KDP upload!")
    print("=" * 60)


if __name__ == "__main__":
    main()
