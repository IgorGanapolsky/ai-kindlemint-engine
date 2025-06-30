#!/usr/bin/env python3
"""
KindleMint Quick Start Script
Generate your first book in 60 seconds!
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_banner():
    """Print welcome banner"""
    print(
        """
    🚀 KindleMint Engine - Quick Start
    ================================
    Generate professional puzzle books in minutes!
    """
    )


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        pass

        return True
    except ImportError:
        print("⚠️  Missing dependencies. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        return True


def generate_book(book_type: str, volume: int, output_dir: str = None):
    """Generate a book based on type and volume"""

    if output_dir is None:
        output_dir = f"output/quick_start/{book_type}_volume_{volume}"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n📚 Generating {book_type.title()} Book - Volume {volume}")
    print(f"📁 Output directory: {output_path}")

    if book_type == "crossword":
        generate_crossword_book(volume, output_path)
    elif book_type == "sudoku":
        generate_sudoku_book(volume, output_path)
    elif book_type == "wordsearch":
        generate_wordsearch_book(volume, output_path)
    else:
        print(f"❌ Unknown book type: {book_type}")
        return False

    return True


def generate_crossword_book(volume: int, output_path: Path):
    """Generate a crossword puzzle book"""
    from book_layout_bot import BookLayoutBot
    from crossword_engine_v3_fixed import CrosswordEngineV3

    print("🎯 Initializing Crossword Engine...")
    engine = CrosswordEngineV3(
        output_dir=str(output_path), puzzle_count=50, difficulty="mixed"
    )

    print("📝 Generating 50 crossword puzzles...")
    start_time = time.time()

    # Generate puzzles
    puzzles = engine.generate_all_puzzles()

    # Create PDF
    print("📄 Creating PDF interior...")
    layout_bot = BookLayoutBot()

    book_metadata = {
        "title": f"Large Print Crossword Masters - Volume {volume}",
        "subtitle": "50 Challenging Puzzles for Word Enthusiasts",
        "author": "Crossword Masters Publishing",
        "volume": volume,
        "puzzle_count": 50,
        "difficulty": "Progressive",
    }

    pdf_path = output_path / "interior.pdf"
    layout_bot.create_crossword_pdf(puzzles, book_metadata, str(pdf_path))

    elapsed = time.time() - start_time
    print(f"\n✅ Book generated in {elapsed:.1f} seconds!")
    print(f"📄 PDF location: {pdf_path}")

    # Generate metadata
    create_kdp_metadata(book_metadata, output_path)

    # Show next steps
    show_next_steps(output_path)


def generate_sudoku_book(volume: int, output_path: Path):
    """Generate a sudoku puzzle book"""
    print("🔢 Generating Sudoku puzzles...")

    # Use the sudoku generator
    cmd = [
        sys.executable,
        "scripts/sudoku_generator.py",
        "--output",
        str(output_path),
        "--count",
        "50",
        "--difficulty",
        "mixed",
    ]

    subprocess.run(cmd)

    print("\n✅ Sudoku book generated!")
    show_next_steps(output_path)


def generate_wordsearch_book(volume: int, output_path: Path):
    """Generate a word search puzzle book"""
    print("🔤 Generating Word Search puzzles...")

    # Use the word search generator
    cmd = [
        sys.executable,
        "scripts/word_search_generator.py",
        "--output",
        str(output_path),
        "--count",
        "50",
        "--grid-size",
        "15",
    ]

    subprocess.run(cmd)

    print("\n✅ Word Search book generated!")
    show_next_steps(output_path)


def create_kdp_metadata(book_metadata: dict, output_path: Path):
    """Create KDP metadata files"""
    import json

    kdp_data = {
        "title": book_metadata["title"],
        "subtitle": book_metadata["subtitle"],
        "author": book_metadata["author"],
        "description": f"""Challenge your mind with Volume {book_metadata['volume']} of our bestselling puzzle series!

This collection features {book_metadata['puzzle_count']} carefully crafted puzzles designed for puzzle enthusiasts who appreciate quality and variety.

Perfect for:
• Daily mental exercise
• Relaxation and stress relief
• Gift-giving to puzzle lovers
• Hours of entertainment

Features:
• {book_metadata['puzzle_count']} unique puzzles
• {book_metadata['difficulty']} difficulty levels
• Complete answer key
• Professional quality construction
• Large print format

Join thousands of satisfied puzzlers who have made this their go-to series!""",
        "keywords": [
            "puzzle book",
            "brain games",
            "mental exercise",
            "large print",
            "gift book",
            "activity book",
            f"volume {book_metadata['volume']}",
        ],
        "categories": [
            "Books > Humor & Entertainment > Puzzles & Games",
            "Books > Health, Fitness & Dieting > Aging > Exercise & Fitness",
        ],
        "language": "English",
        "pages": 156,
        "price_usd": 12.99,
    }

    # Save metadata
    with open(output_path / "kdp_metadata.json", "w") as f:
        json.dump(kdp_data, f, indent=2)

    # Create checklist
    checklist = f"""# KDP Publishing Checklist

## Book Details
- Title: {book_metadata['title']}
- Subtitle: {book_metadata['subtitle']}
- Author: {book_metadata['author']}
- Pages: 156
- Price: $12.99

## Pre-Upload Checklist
- [ ] Review interior PDF
- [ ] Check all puzzles have solutions
- [ ] Verify page count (156)
- [ ] Create cover image (1600x2560)
- [ ] Write book description

## KDP Upload Steps
1. [ ] Log into KDP (kdp.amazon.com)
2. [ ] Click "Create New Title"
3. [ ] Enter book details from kdp_metadata.json
4. [ ] Upload interior PDF
5. [ ] Upload cover image
6. [ ] Preview book
7. [ ] Set pricing ($12.99)
8. [ ] Publish!

## Post-Publishing
- [ ] Order proof copy
- [ ] Share on social media
- [ ] Create series page
- [ ] Plan next volume
"""

    with open(output_path / "kdp_checklist.md", "w") as f:
        f.write(checklist)


def show_next_steps(output_path: Path):
    """Show next steps to the user"""
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Your book is ready!")
    print("=" * 50)

    print(f"\n📁 Files created in: {output_path}")

    # List files
    files = list(output_path.glob("*"))
    for f in files[:5]:  # Show first 5 files
        print(f"   - {f.name}")
    if len(files) > 5:
        print(f"   ... and {len(files)-5} more files")

    print("\n🚀 Next Steps:")
    print("1. Review the generated PDF")
    print("2. Create a cover using Canva or DALL-E")
    print("3. Upload to KDP following kdp_checklist.md")
    print("4. Set competitive pricing ($9.99-$14.99)")
    print("5. Publish and start earning!")

    print("\n💡 Pro Tips:")
    print("• Create a series of 5+ volumes for better sales")
    print("• Use seasonal themes for holiday sales")
    print("• Target specific audiences (seniors, kids, experts)")

    print("\n📊 Want market insights?")
    print("Run: python scripts/reddit_market_scraper.py")

    print("\n🙋 Need help?")
    print("• README.md - Full documentation")
    print("• GitHub Issues - Report problems")
    print("• Discord - Join the community")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="KindleMint Quick Start - Generate your first book!"
    )
    parser.add_argument(
        "--type",
        choices=["crossword", "sudoku", "wordsearch"],
        default="crossword",
        help="Type of puzzle book to generate",
    )
    parser.add_argument(
        "--volume", type=int, default=1, help="Volume number for the book"
    )
    parser.add_argument("--output", help="Output directory (optional)")

    args = parser.parse_args()

    print_banner()

    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return 1

    # Generate the book
    success = generate_book(args.type, args.volume, args.output)

    if not success:
        print("\n❌ Book generation failed!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
