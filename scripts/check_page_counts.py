#!/usr/bin/env python3
"""Check page counts of all PDF files in the Large Print Crossword Masters series."""

import os
from pathlib import Path

from pypdf import PdfReader


def check_pdf_page_count(pdf_path):
    """Get page count from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    base_dir = Path(
        "/Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine/books/active_production/Large_Print_Crossword_Masters"
    )

    results = {}

    for volume in range(1, 5):
        volume_dir = base_dir / f"volume_{volume}"
        results[f"Volume {volume}"] = {}

        # Check paperback
        paperback_dir = volume_dir / "paperback"
        if paperback_dir.exists():
            for pdf_file in paperback_dir.glob("*.pdf"):
                if "FINAL" in pdf_file.name or "interior" in pdf_file.name:
                    pages = check_pdf_page_count(pdf_file)
                    results[f"Volume {volume}"]["paperback"] = {
                        "file": pdf_file.name,
                        "pages": pages,
                    }
                    break

        # Check hardcover
        hardcover_dir = volume_dir / "hardcover"
        if hardcover_dir.exists():
            for pdf_file in hardcover_dir.glob("*.pdf"):
                if (
                    "FINAL" in pdf_file.name or "interior" in pdf_file.name
                ) and "cover" not in pdf_file.name.lower():
                    pages = check_pdf_page_count(pdf_file)
                    results[f"Volume {volume}"]["hardcover"] = {
                        "file": pdf_file.name,
                        "pages": pages,
                    }
                    break

    # Print results
    print("Page Count Analysis for Large Print Crossword Masters\n")
    print("=" * 60)

    for volume, formats in results.items():
        print(f"\n{volume}:")
        for format_type, info in formats.items():
            if isinstance(info, dict):
                print(
                    f"  {format_type.title()}: {info['pages']} pages ({info['file']})"
                )

    print("\n" + "=" * 60)
    print("\nSummary:")
    for i in range(1, 5):
        vol_key = f"Volume {i}"
        if vol_key in results:
            pp_pages = results[vol_key].get("paperback", {}).get("pages", "N/A")
            hc_pages = results[vol_key].get("hardcover", {}).get("pages", "N/A")
            print(f"Volume {i}: Paperback={pp_pages}, Hardcover={hc_pages}")


if __name__ == "__main__":
    main()
