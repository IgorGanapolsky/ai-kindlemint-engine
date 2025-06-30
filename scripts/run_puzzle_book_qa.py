#!/usr/bin/env python3
"""
Automated QA Runner for Puzzle Books
Integrates with the build process to ensure quality before publication
"""

from kindlemint.validators.sudoku_book_qa import SudokuBookQAValidator
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_qa_checks():
    """Run QA checks on all active production puzzle books"""
    print("🤖 AUTOMATED QA SYSTEM")
    print("=" * 50)
    print(f"Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Find all puzzle books in active production
    active_production = Path(__file__).parent.parent / "books" / "active_production"

    if not active_production.exists():
        print("❌ No active production directory found")
        return False

    all_passed = True
    books_checked = 0

    # Check all PDF files in active production
    for pdf_path in active_production.rglob("*.pdf"):
        if "COMPLETE" in pdf_path.name:  # Only check complete books
            print(f"\n📖 Checking: {pdf_path.relative_to(active_production)}")

            validator = SudokuBookQAValidator()
            report = validator.validate_book(pdf_path)

            if report["status"] == "FAIL":
                all_passed = False
                error_count = report.get("errors", 0)
                print(f"❌ FAILED: {error_count} critical errors!")

                # Save detailed failure report
                failure_report = {
                    "book": str(pdf_path),
                    "timestamp": datetime.now().isoformat(),
                    "errors": report.get("error_details", []),
                    "warnings": report.get("warning_details", []),
                }

                failure_path = (
                    pdf_path.parent
                    / f"QA_FAILURE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(failure_path, "w") as f:
                    json.dump(failure_report, f, indent=2)

                print(f"📄 Failure report saved to: {failure_path}")

            books_checked += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 QA SUMMARY")
    print("=" * 50)
    print(f"Books checked: {books_checked}")

    if all_passed and books_checked > 0:
        print("✅ All books passed QA!")
        return True
    elif books_checked == 0:
        print("⚠️ No complete books found to check")
        return True
    else:
        print("❌ QA FAILED - Fix errors before publishing!")
        return False


def main():
    """Main entry point"""
    passed = run_qa_checks()

    # Exit with appropriate code for CI/CD integration
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
