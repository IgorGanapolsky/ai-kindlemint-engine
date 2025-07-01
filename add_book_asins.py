#!/usr/bin/env python3
"""
Script to add ASINs to your published books for performance monitoring

Since you mentioned publishing 6 books (2 series x 3 books each) 3 weeks ago,
you'll need to add the ASINs from Amazon KDP to enable performance monitoring.
"""

import json
import sys
from pathlib import Path


def add_asins():
    """Interactive script to add ASINs to books"""

    print("📚 KindleMint ASIN Configuration Tool")
    print("=====================================\n")

    # Load active books
    active_books_file = Path("books/performance_data/active_books.json")

    if not active_books_file.exists():
        print(
            "❌ No active books file found. Please run the orchestration system first."
        )
        return

    with open(active_books_file, "r") as f:
        books = json.load(f)

    print(f"Found {len(books)} books in your portfolio:\n")

    # Group by series
    series_books = {}
    for book_id, book_info in books.items():
        series = book_info.get("series", "Unknown")
        if series not in series_books:
            series_books[series] = []
        series_books[series].append((book_id, book_info))

    # Display books by series
    for series, book_list in series_books.items():
        print(f"\n📖 Series: {series.replace('_', ' ')}")
        print("-" * 40)
        for book_id, book_info in sorted(
            book_list, key=lambda x: x[1].get("volume", "")
        ):
            has_asin = "✅" if book_info.get("asin") else "❌"
            volume = book_info.get("volume", "").replace("volume_", "Volume ")
            print(f"{has_asin} {volume}: {book_info.get('title', 'Unknown')}")
            if book_info.get("asin"):
                print(f"   ASIN: {book_info['asin']}")

    print("\n" + "=" * 50)
    print("\n🔧 Add ASINs for your published books")
    print("(Press Enter to skip books that aren't published yet)\n")

    updated_count = 0

    # Update ASINs
    for series in ["Large_Print_Crossword_Masters", "Large_Print_Sudoku_Masters"]:
        if series not in series_books:
            continue

        print(f"\n📚 {series.replace('_', ' ')}:")

        for book_id, book_info in sorted(
            series_books[series], key=lambda x: x[1].get("volume", "")
        ):
            volume = book_info.get("volume", "").replace("volume_", "Volume ")
            current_asin = book_info.get("asin", "")

            if current_asin:
                print(f"\n{volume} already has ASIN: {current_asin}")
                update = input("Update? (y/N): ").strip().lower()
                if update != "y":
                    continue

            asin = input(
                f"\nEnter ASIN for {volume} (or press Enter to skip): "
            ).strip()

            if asin:
                # Validate ASIN format
                if len(asin) == 10 and asin.startswith("B"):
                    books[book_id]["asin"] = asin
                    updated_count += 1
                    print(f"✅ Added ASIN: {asin}")
                else:
                    print(
                        f"⚠️  Invalid ASIN format. ASINs should be 10 characters starting with 'B'"
                    )

    # Save updates
    if updated_count > 0:
        with open(active_books_file, "w") as f:
            json.dump(books, f, indent=2)

        print(f"\n✅ Updated {updated_count} books with ASINs")
        print("\n🚀 Your books are now ready for performance monitoring!")
        print("Run './launch_orchestration.sh' to start monitoring")
    else:
        print("\n❌ No ASINs were added")
        print("\n💡 Tip: You can find your ASINs in your KDP Bookshelf")
        print("Each book's ASIN is shown on its Amazon product page URL")
        print("Example: amazon.com/dp/B0XXXXXXXXX <- The ASIN is B0XXXXXXXXX")


if __name__ == "__main__":
    add_asins()
