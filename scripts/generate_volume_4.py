#!/usr/bin/env python3

    def get_varied_instructions(self, difficulty, puzzle_number):
        """Generate varied instructions for each puzzle to avoid repetition"""
        instructions = {
            "easy": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>HOW TO SOLVE:</b> Your goal is to complete the grid by placing numbers 1-9 in each empty cell. Remember: no number can repeat in the same row, column, or 3×3 box.",
                "<b>PUZZLE RULES:</b> Fill every empty square with a number from 1 to 9. Each row, column, and 3×3 section must contain all nine numbers exactly once.",
                "<b>SOLVING GOAL:</b> Complete the 9×9 grid by adding numbers 1-9 to empty cells. Every row, column, and 3×3 box must have all nine numbers with no repeats.",
                "<b>GAME RULES:</b> Place numbers 1 through 9 in each empty square. Each horizontal row, vertical column, and 3×3 box must contain all nine numbers.",
            ],
            "medium": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>CHALLENGE RULES:</b> Complete the grid by placing numbers 1-9 in empty cells. The constraint: no number can repeat within any row, column, or 3×3 box.",
                "<b>SOLVING INSTRUCTIONS:</b> Your task is to fill every empty cell with a number from 1 to 9, ensuring each row, column, and 3×3 section contains all nine numbers exactly once.",
                "<b>PUZZLE OBJECTIVE:</b> Fill the 9×9 grid completely. Each row, column, and 3×3 box must contain the numbers 1-9 with no duplicates.",
                "<b>GAME OBJECTIVE:</b> Complete the grid by adding numbers 1 through 9 to empty squares. Every row, column, and outlined 3×3 box must have all nine numbers.",
            ],
            "hard": [
                "<b>INSTRUCTIONS:</b> Fill in the empty squares so that each row, each column, and each 3×3 box contains all numbers from 1 to 9. Each number can appear only once in each row, column, and 3×3 box.",
                "<b>EXPERT CHALLENGE:</b> Complete this grid by placing numbers 1-9 in each empty cell. The rule: no number can appear twice in the same row, column, or 3×3 box.",
                "<b>ADVANCED RULES:</b> Fill every empty square with a number from 1 to 9. Each horizontal row, vertical column, and 3×3 section must contain all nine numbers without repetition.",
                "<b>MASTER PUZZLE:</b> Your goal is to complete the 9×9 grid. Each row, column, and 3×3 box must contain the numbers 1-9 with no number appearing more than once.",
                "<b>CHALLENGE GOAL:</b> Fill the entire grid with numbers 1 through 9. Every row, column, and 3×3 box must have all nine numbers exactly once.",
            ],
        }
        
        instruction_list = instructions.get(difficulty, instructions["medium"])
        instruction_index = (puzzle_number - 1) % len(instruction_list)
        return instruction_list[instruction_index]

    def get_varied_tips(self, difficulty, puzzle_number):
        """Generate varied tips for each puzzle to avoid repetition"""
        tips = {
            "easy": [
                "<b>💡 TIP:</b> Start with rows, columns, or boxes that have the most numbers already filled in!",
                "<b>💡 HINT:</b> Look for cells where only one number can possibly fit by checking what's already in that row, column, and box.",
                "<b>💡 STRATEGY:</b> Focus on the number that appears most frequently in the grid - find where it can go in empty areas.",
                "<b>💡 APPROACH:</b> Work on one 3×3 box at a time. Complete boxes give you more clues for adjacent areas.",
                "<b>💡 METHOD:</b> If a row has 8 numbers filled, the empty cell must contain the missing number - look for these 'gift' cells first.",
                "<b>💡 TECHNIQUE:</b> Scan each number 1-9 systematically. For each number, see where it can legally go in each 3×3 box.",
                "<b>💡 SHORTCUT:</b> Start with areas that are nearly complete - they often reveal obvious moves that unlock other areas.",
            ],
            "medium": [
                "<b>💡 TIP:</b> Look for cells where only one number can fit by checking the row, column, and box constraints.",
                "<b>💡 STRATEGY:</b> Use pencil marks to write small numbers in cell corners showing all possibilities, then eliminate them systematically.",
                "<b>💡 TECHNIQUE:</b> Look for 'naked pairs' - when two cells in the same unit can only contain the same two numbers.",
                "<b>💡 METHOD:</b> When a number can only go in one row or column within a 3×3 box, eliminate it from the rest of that row/column.",
                "<b>💡 APPROACH:</b> If you find a cell where only one number fits, fill it immediately and scan for new opportunities this creates.",
                "<b>💡 HINT:</b> Focus on cells that are constrained by multiple factors - intersections of nearly-complete rows, columns, and boxes.",
                "<b>💡 STRATEGY:</b> Make a few moves, then re-scan the entire grid for new possibilities that your moves have created.",
            ],
            "hard": [
                "<b>💡 TIP:</b> Use pencil marks to note possible numbers in each cell, then eliminate them systematically.",
                "<b>💡 EXPERT TIP:</b> Advanced puzzles often require 'chain logic' - following a series of if-then statements through multiple cells.",
                "<b>💡 X-WING:</b> Look for numbers that appear in only two cells across two rows (or columns) - this creates elimination opportunities.",
                "<b>💡 ADVANCED:</b> Use 'coloring' technique - mark cells with the same candidate in different colors to spot contradictions.",
                "<b>💡 FORCING:</b> If a cell has only two possibilities, try assuming one is correct and follow the logical chain to find contradictions.",
                "<b>💡 PATTERN:</b> Look for 'Swordfish' patterns - when a number appears in only three cells across three rows, forming elimination chains.",
                "<b>💡 PERSISTENCE:</b> Hard puzzles may require multiple advanced techniques in sequence. Don't give up after one method fails.",
            ],
        }
        
        tip_list = tips.get(difficulty, tips["medium"])
        tip_index = (puzzle_number - 1) % len(tip_list)
        return tip_list[tip_index]

"""
Generate Volume 4 of Large Print Crossword Masters
50 unique crossword puzzles with progressive difficulty
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

from book_layout_bot import BookLayoutBot as BookLayoutEngine
from comprehensive_qa_validator import ComprehensiveQAValidator
from crossword_engine_v2 import CrosswordEngineV2 as CrosswordEngine
from slack_notifier import SlackNotifier

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# Configuration
VOLUME_NUMBER = 4
PUZZLE_COUNT = 50
OUTPUT_BASE = Path("books/active_production/Large_Print_Crossword_Masters/volume_4")
TITLE = "Large Print Crossword Masters"
SUBTITLE = "Volume 4: 50 Challenging Puzzles for Word Enthusiasts"
AUTHOR = "Crossword Masters Publishing"


    """Generate Volume 4"""
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
            "puzzles": [p["id"] for p_var in puzzles],
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
            if all(r.get("passed", False) for_var r_var in qa_results.values())
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
