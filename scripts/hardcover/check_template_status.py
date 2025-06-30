#!/usr/bin/env python3
"""
Check which KDP hardcover templates are needed for current books
"""

from pathlib import Path

import PyPDF2


def get_pdf_page_count(pdf_path):
    """Get exact page count from PDF"""
    try:
        with open(pdf_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            return len(pdf.pages)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None


def check_templates():
    """Check template status for all books"""
    books_dir = Path("books/active_production")
    template_dir = Path("templates/hardcover/kdp_case_laminate")

    print("🔍 KDP Hardcover Template Status Check\n")
    print("=" * 70)

    # Track needed templates
    needed_templates = set()

    # Check each series
    for series_dir in books_dir.iterdir():
        if not series_dir.is_dir():
            continue

        print(f"\n📚 Series: {series_dir.name}")

        # Check each volume
        for volume_dir in series_dir.iterdir():
            if not volume_dir.is_dir() or not volume_dir.name.startswith("volume"):
                continue

            # Find interior PDF
            paperback_dir = volume_dir / "paperback"
            if not paperback_dir.exists():
                continue

            # Look for interior PDF
            interior_pdf = None
            for pdf_file in paperback_dir.glob("*interior*.pdf"):
                interior_pdf = pdf_file
                break

            if interior_pdf:
                page_count = get_pdf_page_count(interior_pdf)
                if page_count:
                    template_name = f"6x9_{page_count}pages_template.png"
                    template_path = template_dir / template_name

                    status = "✅ EXISTS" if template_path.exists() else "❌ NEEDED"

                    print(
                        f"  📖 {volume_dir.name}: {
                            page_count} pages - Template: {status}"
                    )

                    if not template_path.exists():
                        needed_templates.add((page_count, template_name))
                else:
                    print(f"  ⚠️  {volume_dir.name}: Could not read page count")
            else:
                print(f"  ⚠️  {volume_dir.name}: No interior PDF found")

    # Summary
    print("\n" + "=" * 70)
    print("\n📋 SUMMARY:")

    if needed_templates:
        print("\n❌ Templates to download from KDP Cover Calculator:")
        for page_count, template_name in sorted(needed_templates):
            spine_width = (page_count * 0.0025) + 0.06
            print(f"   - {template_name} (spine width: {spine_width:.3f} inches)")

        print("\n📌 Download instructions:")
        print("   1. Go to https://kdp.amazon.com/en_US/cover-calculator")
        print("   2. Select: Hardcover, Black & white, White paper, 6×9 in")
        print("   3. Enter page count and download template")
        print(f"   4. Save to: templates/hardcover/kdp_case_laminate/")
    else:
        print("\n✅ All templates are available!")

    # Check existing templates
    print("\n📂 Existing templates:")
    for template in sorted(template_dir.glob("*.png")):
        print(f"   ✓ {template.name}")


if __name__ == "__main__":
    check_templates()
