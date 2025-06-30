#!/usr/bin/env python3
"""
Generate Volume 4 of Large Print Crossword Masters
50 unique crossword puzzles with progressive difficulty
"""

from slack_notifier import SlackNotifier
from crossword_engine_v2 import CrosswordEngineV2 as CrosswordEngine
from comprehensive_qa_validator import ComprehensiveQAValidator
from book_layout_bot import BookLayoutBot as BookLayoutEngine
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Configuration
VOLUME_NUMBER = 4
PUZZLE_COUNT = 50
OUTPUT_BASE = Path("books/active_production/Large_Print_Crossword_Masters/volume_4")
TITLE = "Large Print Crossword Masters"
SUBTITLE = "Volume 4: 50 Challenging Puzzles for Word Enthusiasts"
AUTHOR = "Crossword Masters Publishing"


def generate_volume_4():
    """Generate Volume 4 with all required components"""

    print(f"🚀 Starting generation of {TITLE} - Volume {VOLUME_NUMBER}")
    print(f"📊 Target: {PUZZLE_COUNT} puzzles")

    start_time = time.time()
    notifier = SlackNotifier()

    # Initialize engines
    crossword_engine = CrosswordEngine()
    layout_engine = BookLayoutEngine()
    qa_validator = ComprehensiveQAValidator()

    # Create output directories
    paperback_dir = OUTPUT_BASE / "paperback"
    hardcover_dir = OUTPUT_BASE / "hardcover"
    kindle_dir = OUTPUT_BASE / "kindle"

    for dir_path in [paperback_dir, hardcover_dir, kindle_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "metadata").mkdir(exist_ok=True)

    # Generate puzzles with progressive difficulty
    puzzles = []
    difficulty_distribution = {
        "easy": 10,  # Puzzles 1-10
        "medium": 30,  # Puzzles 11-40
        "hard": 10,  # Puzzles 41-50
    }

    puzzle_id = 1
    for difficulty, count in difficulty_distribution.items():
        print(f"\n📝 Generating {count} {difficulty} puzzles...")

        for i in range(count):
            print(
                f"  Creating puzzle {puzzle_id}/{PUZZLE_COUNT}...", end="", flush=True
            )

            try:
                # Generate crossword
                puzzle_data = crossword_engine.generate_puzzle(
                    difficulty=difficulty,
                    theme="General Knowledge",  # Varied themes
                    puzzle_id=f"puzzle_{puzzle_id:03d}",
                )

                # Add volume metadata
                puzzle_data["volume"] = VOLUME_NUMBER
                puzzle_data["position"] = puzzle_id

                puzzles.append(puzzle_data)
                print(" ✅")

            except Exception as e:
                print(f" ❌ Error: {e}")
                # Continue with generation

            puzzle_id += 1

            # Small delay to avoid API rate limits
            if puzzle_id % 5 == 0:
                time.sleep(2)

    print(f"\n✅ Generated {len(puzzles)} puzzles")

    # Save puzzle metadata
    print("\n💾 Saving puzzle metadata...")
    for format_dir in [paperback_dir, hardcover_dir, kindle_dir]:
        metadata_dir = format_dir / "metadata"

        # Save individual puzzle files
        for puzzle in puzzles:
            puzzle_file = metadata_dir / f"{puzzle['id']}.json"
            with open(puzzle_file, "w") as f:
                json.dump(puzzle, f, indent=2)

        # Save collection metadata
        collection_data = {
            "title": TITLE,
            "subtitle": SUBTITLE,
            "volume": VOLUME_NUMBER,
            "author": AUTHOR,
            "puzzle_count": len(puzzles),
            "difficulty_distribution": difficulty_distribution,
            "generated_at": datetime.now().isoformat(),
            "puzzles": [p["id"] for p in puzzles],
        }

        with open(metadata_dir / "collection.json", "w") as f:
            json.dump(collection_data, f, indent=2)

    # Generate book layouts
    print("\n📖 Generating book layouts...")

    # Paperback (6x9, 107 pages typical)
    print("  📘 Creating paperback layout...")
    paperback_pdf = layout_engine.create_book(
        puzzles=puzzles,
        output_path=paperback_dir / "interior.pdf",
        format_type="paperback",
        title=f"{TITLE} - Volume {VOLUME_NUMBER}",
        subtitle=SUBTITLE,
        trim_size=(6, 9),
        target_pages=107,
    )

    # Hardcover (6x9, 156 pages)
    print("  📕 Creating hardcover layout...")
    hardcover_pdf = layout_engine.create_book(
        puzzles=puzzles,
        output_path=hardcover_dir / "interior.pdf",
        format_type="hardcover",
        title=f"{TITLE} - Volume {VOLUME_NUMBER}",
        subtitle=SUBTITLE,
        trim_size=(6, 9),
        target_pages=156,
    )

    # Kindle (specific formatting)
    print("  📱 Creating Kindle layout...")
    kindle_pdf = layout_engine.create_book(
        puzzles=puzzles,
        output_path=kindle_dir / "interior.pdf",
        format_type="kindle",
        title=f"{TITLE} - Volume {VOLUME_NUMBER}",
        subtitle=SUBTITLE,
    )

    # Run QA validation
    print("\n🔍 Running quality assurance checks...")
    qa_results = {}

    for format_type, pdf_path in [
        ("paperback", paperback_dir / "interior.pdf"),
        ("hardcover", hardcover_dir / "interior.pdf"),
        ("kindle", kindle_dir / "interior.pdf"),
    ]:
        if pdf_path.exists():
            result = qa_validator.validate_book(pdf_path)
            qa_results[format_type] = result

            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"  {format_type}: {status} (Score: {result['score']}/100)")

    # Create KDP metadata files
    print("\n📋 Creating KDP metadata...")

    kdp_metadata = {
        "title": f"{TITLE} - Volume {VOLUME_NUMBER}",
        "subtitle": SUBTITLE,
        "author": AUTHOR,
        "description": f"Challenge your mind with Volume {VOLUME_NUMBER} of our bestselling Large Print Crossword Masters series! This collection features {PUZZLE_COUNT} carefully crafted crossword puzzles designed specifically for puzzle enthusiasts who appreciate larger, easier-to-read print.\n\nPerfect for:\n• Adults who prefer large print formats\n• Daily mental exercise and brain training\n• Relaxation and stress relief\n• Gift-giving to puzzle lovers\n\nFeatures:\n• {PUZZLE_COUNT} unique crossword puzzles\n• Progressive difficulty from easy to challenging\n• Large print grids and clues for comfortable solving\n• Complete answer key included\n• Professional quality puzzles with symmetric grids\n\nJoin thousands of satisfied puzzlers who have made Large Print Crossword Masters their go-to series for quality crossword entertainment!",
        "keywords": [
            "large print crossword puzzles",
            "crossword puzzle books for adults",
            "large print puzzle books",
            f"crossword volume {VOLUME_NUMBER}",
            "brain games large print",
            "crossword puzzle book",
            "mental exercise puzzles",
        ],
        "categories": [
            "Books > Humor & Entertainment > Puzzles & Games > Crosswords",
            "Books > Humor & Entertainment > Puzzles & Games > Logic & Brain Teasers",
            "Books > Health, Fitness & Dieting > Aging > Exercise & Fitness",
        ],
        "language": "English",
        "publication_date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Save KDP metadata for each format
    for format_dir in [paperback_dir, hardcover_dir, kindle_dir]:
        with open(format_dir / "amazon_kdp_metadata.json", "w") as f:
            json.dump(kdp_metadata, f, indent=2)

    # Create publishing checklists
    for format_type, format_dir in [
        ("paperback", paperback_dir),
        ("hardcover", hardcover_dir),
        ("kindle", kindle_dir),
    ]:
        checklist_content = f"""# KDP Publishing Checklist - {TITLE} Volume {VOLUME_NUMBER} ({format_type.title()})

## Pre-Publishing QA
- [ ] All {PUZZLE_COUNT} puzzles verified complete
- [ ] Solutions validated and correct
- [ ] No duplicate puzzles from previous volumes
- [ ] Page count correct for format
- [ ] Margins meet KDP requirements
- [ ] Cover spine width calculated (if applicable)

## KDP Upload Steps
1. [ ] Log into KDP account
2. [ ] Click "Create New Title"
3. [ ] Select appropriate format ({format_type})
4. [ ] Enter metadata from `amazon_kdp_metadata.json`
5. [ ] Upload interior PDF
6. [ ] Upload cover file
7. [ ] Preview entire book
8. [ ] Set pricing (see strategy below)
9. [ ] Submit for publishing

## Pricing Strategy
- Paperback: $12.99 (printing cost ~$3.50)
- Hardcover: $19.99 (printing cost ~$6.50)
- Kindle: $6.99 (70% royalty tier)

## Post-Publishing
- [ ] Order author proof copy
- [ ] Verify live listing
- [ ] Update series page
- [ ] Announce on social media
- [ ] Update website

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        with open(format_dir / "kdp_publishing_checklist.md", "w") as f:
            f.write(checklist_content)

    # Calculate generation time
    generation_time = time.time() - start_time
    minutes = int(generation_time // 60)
    seconds = int(generation_time % 60)

    # Send completion notification
    summary = {
        "volume": VOLUME_NUMBER,
        "title": f"{TITLE} - Volume {VOLUME_NUMBER}",
        "puzzles_generated": len(puzzles),
        "formats_created": ["paperback", "hardcover", "kindle"],
        "qa_scores": {k: v.get("score", 0) for k, v in qa_results.items()},
        "generation_time": f"{minutes}m {seconds}s",
        "status": (
            "READY FOR PUBLISHING"
            if all(r.get("passed", False) for r in qa_results.values())
            else "NEEDS REVIEW"
        ),
    }

    print(f"\n{'=' * 60}")
    print(f"✅ VOLUME {VOLUME_NUMBER} GENERATION COMPLETE!")
    print(f"{'=' * 60}")
    print(f"📚 Title: {summary['title']}")
    print(f"🧩 Puzzles: {summary['puzzles_generated']}")
    print(f"⏱️  Time: {summary['generation_time']}")
    print(f"📊 QA Scores: {summary['qa_scores']}")
    print(f"📋 Status: {summary['status']}")
    print(f"\n📁 Output location: {OUTPUT_BASE}")

    # Send Slack notification
    notifier.send_message(
        f"✅ Volume {VOLUME_NUMBER} Complete! {
            summary['puzzles_generated']} puzzles generated in {
            summary['generation_time']}. Status: {
            summary['status']}",
        color="#2ecc71",
    )

    return summary


if __name__ == "__main__":
    generate_volume_4()
