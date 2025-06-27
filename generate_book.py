#!/usr/bin/env python3
"""
KindleMint Business-in-a-Box: The One-Click Book Generator

This script orchestrates the entire process of creating and launching a
profitable KDP puzzle book, from market validation to final launch checklist.
It integrates all KindleMint Engine components into a single, powerful,
business-first workflow.

**This is not just a content generator; it's a revenue generator.**

It follows a strict "validate-then-create" pipeline:
1.  **Market Validation:** Checks if a theme is commercially viable before
    any work is done.
2.  **Content Generation:** Calls the unified generator to create high-quality,
    KDP-compliant book assets.
3.  **QA Validation:** Runs content-aware QA to ensure the book is perfect.
4.  **Marketing Package:** Generates marketing assets, KDP optimization
    guides, and a complete launch checklist.

Usage:
    # Interactive mode (recommended for first-time users)
    python generate_book.py

    # Direct command for a specific book
    python generate_book.py "Garden Flowers" 50 medium

    # With flags for more control
    python generate_book.py --theme "Classic Movies" --count 40 --difficulty hard --format hardcover
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --- Setup Project Root and Logging ---
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("KindleMintBusinessGenerator")

# --- Helper Functions ---


def run_subprocess(command: list, cwd: Path) -> subprocess.CompletedProcess:
    """Runs a command as a subprocess and handles errors."""
    logger.info(f"Running command: {' '.join(map(str, command))}")
    try:
        return subprocess.run(
            command, check=True, capture_output=True, text=True, cwd=cwd
        )
    except FileNotFoundError:
        logger.error(
            f"❌ Command not found: {command[0]}. Is the script in the correct path?"
        )
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Command failed with exit code {e.returncode}")
        logger.error(f"   STDOUT: {e.stdout}")
        logger.error(f"   STDERR: {e.stderr}")
        raise


# --- Pipeline Step Functions ---


def run_market_validation(context: dict) -> bool:
    """Runs the market validator and decides whether to proceed."""
    theme = context["theme"]
    validator_script = context["project_root"] / "scripts" / "market_validator.py"

    if not validator_script.exists():
        logger.warning("⚠️ Market validator script not found. Skipping validation.")
        context["market_report"] = None
        return True

    try:
        result = run_subprocess(
            [sys.executable, str(validator_script), theme], context["project_root"]
        )
        report = json.loads(
            result.stdout.split("=" * 60)[-1].strip()
        )  # Crude but effective parsing
        context["market_report"] = report

        recommendation = report.get("recommendation", {})
        decision = recommendation.get("decision", "NO-GO")

        if decision == "NO-GO":
            logger.error(f"❌ Market Validation Failed: {recommendation.get('reason')}")
            return False
        elif decision == "PIVOT":
            logger.warning(
                f"⚠️ Market Validation suggests a PIVOT: {recommendation.get('reason')}"
            )
            proceed = input(
                "   Do you want to continue with this theme anyway? (y/n): "
            ).lower()
            return proceed == "y"

        logger.info(f"✅ Market Validation Passed with recommendation: {decision}")
        return True
    except Exception as e:
        logger.error(f"Failed to run or parse market validation: {e}")
        return False  # Fail safe


def run_unified_generator(context: dict) -> bool:
    """Calls the unified volume generator to create the book assets."""
    generator_script = (
        context["project_root"] / "scripts" / "unified_volume_generator.py"
    )
    if not generator_script.exists():
        logger.error(f"❌ Unified generator script not found at {generator_script}")
        return False

    cmd = [
        sys.executable,
        str(generator_script),
        "--series",
        context["series_name"],
        "--volumes",
        str(context["volume_num"]),
        "--puzzle-type",
        context["puzzle_type"],
        "--difficulty",
        context["difficulty"],
        "--format",
        context["format"],
        "--skip-qa",  # We run our own QA step later
    ]

    run_subprocess(cmd, context["project_root"])
    return True


def run_qa_validation(context: dict) -> bool:
    """Runs the enhanced QA validator on the generated book."""
    qa_script = context["project_root"] / "scripts" / "enhanced_qa_validator_v3.py"
    if not qa_script.exists():
        logger.warning("⚠️ QA validator script not found. Skipping QA.")
        return True

    result = run_subprocess(
        [sys.executable, str(qa_script), str(context["book_dir"]), "--verbose"],
        context["project_root"],
    )
    report = json.loads(result.stdout.split("=" * 60)[-1].strip())

    if report.get("overall_status") == "FAIL":
        logger.error("❌ QA Validation Failed. See report for details.")
        return False

    logger.info("✅ QA Validation Passed.")
    return True


def generate_marketing_assets(context: dict) -> bool:
    """Generates marketing materials for the book."""
    logger.info("Generating marketing assets...")
    marketing_dir = context["book_dir"] / "Marketing_Assets"
    marketing_dir.mkdir(exist_ok=True)

    # Create a marketing guide
    marketing_guide_path = marketing_dir / "Marketing_Guide.md"
    content = f"""
# 🚀 Marketing Assets & Guide for "{context['theme']}"

## 1. Sample Puzzle PDF
A sample PDF with 3 puzzles has been created. Use this as a lead magnet to build an email list.
- **File:** `sample_puzzles.pdf` (TODO: Implement generation)

## 2. Social Media Post Drafts

**Facebook/Instagram Post:**
> Just launched! 🚀 Dive into our new "{context['theme']} Crossword Puzzle Book"! Perfect for relaxing evenings and keeping your mind sharp. 🧠 Get your copy on Amazon today! #crossword #puzzles #booklaunch #[yourbrand]
> [Link to your Amazon page]

**Pinterest Pin Idea:**
- **Image:** A high-quality photo of your book cover, or an aesthetic shot of a sample puzzle page.
- **Title:** 10-Minute Brain Teaser: Can You Solve This '{context['theme']}' Puzzle?
- **Description:** Get a sneak peek of our new puzzle book! 50 hand-crafted crosswords for hours of fun. Click through to get your copy.

## 3. DALL-E Cover Prompt
Use this prompt to generate more cover ideas:
> "Create a vibrant, high-contrast, professional book cover for a puzzle book titled '{context['series_name']}: Volume {context['volume_num']}'. The theme is '{context['theme']}'. The style should be modern and clean, with easily readable text. Avoid small, busy details."
"""
    marketing_guide_path.write_text(content)
    logger.info(f"✅ Marketing guide created at {marketing_guide_path}")
    return True


def create_launch_package(context: dict) -> bool:
    """Creates the final KDP launch checklist and revenue tracker."""
    logger.info("Creating KDP Launch Package...")
    launch_dir = context["book_dir"] / "KDP_Launch_Package"
    launch_dir.mkdir(exist_ok=True)

    # --- KDP Launch Checklist ---
    checklist_path = launch_dir / "KDP_LAUNCH_CHECKLIST.md"
    title = f"{context['series_name']}: Volume {context['volume_num']}"
    subtitle = f"{context['count']} {context['difficulty'].title()} {context['theme']} Crossword Puzzles for Adults"

    # Generate keywords from theme
    keywords = [
        f"{context['theme'].lower()} crossword puzzles",
        "large print puzzle books for adults",
        "brain games for seniors",
        f"{context['difficulty']} crossword puzzles",
        "activity books for women",
        "puzzle books for travel",
        "mind workout puzzles",
    ]

    checklist_content = f"""
# 🚀 KDP Launch Checklist: "{title}"

## 1. Pre-Launch: Final Checks
- [ ] **Final Review:** Manually flip through the generated PDF. Does it look professional?
- [ ] **Cover Design:** Create your cover using the prompts in the Marketing Assets folder.
- [ ] **Pricing Decision:** Review the market data below and set your launch price.

## 2. KDP Listing Optimization (Copy & Paste)

### **Title:**
`{title}`

### **Subtitle:**
`{subtitle}`

### **Book Description (Copy this HTML into the KDP description box):**
```html
<b>Sharpen your mind and relax your soul with 50 beautifully crafted crossword puzzles themed around the enchanting world of {context['theme']}!</b>

<p>Whether you're a seasoned puzzle enthusiast or looking for a delightful way to unwind, this book offers the perfect blend of challenge and enjoyment. Each puzzle is designed to be engaging but not overwhelming, making it the ideal companion for a quiet afternoon, a long trip, or your daily mental workout.</p>

<p><b>Inside this book, you will find:</b></p>
<ul>
    <li>✅ <b>50 High-Quality Puzzles:</b> Hours of entertainment with unique and interesting clues.</li>
    <li>✅ <b>Large Print Format:</b> Easy on the eyes, with spacious grids that are a pleasure to fill out.</li>
    <li>✅ <b>Themed Content:</b> Immerse yourself in the world of {context['theme']} with every clue you solve.</li>
    <li>✅ <b>Complete Solutions:</b> Full answer grids are provided at the back of the book for every puzzle.</li>
    <li>✅ <b>Perfect for All Skill Levels:</b> With a {context['difficulty']} level, it's great for both beginners and experienced solvers.</li>
</ul>

<p>This puzzle book is more than just a pastime—it's a journey. It makes a wonderful gift for puzzle lovers, seniors, or anyone looking to keep their mind active and engaged.</p>

<b>Ready for your next puzzle adventure? Scroll up and click "Buy Now" to get your copy today!</b>
```

### **Keywords (Enter these 7 keywords in the KDP backend):**
1. `{keywords[0]}`
2. `{keywords[1]}`
3. `{keywords[2]}`
4. `{keywords[3]}`
5. `{keywords[4]}`
6. `{keywords[5]}`
7. `{keywords[6]}`

### **Categories:**
1. `Games & Puzzles > Crosswords`
2. `Health, Fitness & Dieting > Exercise & Fitness > Brain & Memory Games`

## 3. Pricing Strategy
- **Market Data Suggests:** Price range of **{context.get('market_report', {}).get('revenue_estimation', {}).get('price_range', '$7.99 - $12.99')}**
- **Launch Price (First 14 Days):** Consider launching at **$6.99** to attract initial sales and reviews.
- **Target Price:** After 5+ reviews, increase to **$9.99** or your target price.

## 4. Post-Launch Marketing
- [ ] **Amazon Ads:** Start a $5/day automatic campaign.
- [ ] **Social Media:** Use the generated marketing assets to post on Pinterest, Facebook, or Instagram.
- [ ] **Request Reviews:** Add a page to the back of your book asking for reviews (see marketing guide).
"""
    checklist_path.write_text(checklist_content)

    # --- Revenue Tracker Template ---
    tracker_path = launch_dir / "revenue_tracker_template.csv"
    tracker_content = "Date,Book Title,Format,Marketplace,Units Sold,Royalty per Unit,Total Royalty,Ad Spend,Net Profit\n"
    tracker_path.write_text(tracker_content)

    logger.info(f"✅ KDP Launch Package created at {launch_dir}")
    return True


# --- Main Orchestrator ---


def main():
    """Main entry point for the business-in-a-box generator."""
    parser = argparse.ArgumentParser(
        description="KindleMint Business-in-a-Box: Generate and launch profitable puzzle books.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "theme",
        nargs="?",
        help='Book theme (e.g., "Garden Flowers"). Will be prompted if not provided.',
    )
    parser.add_argument(
        "count", nargs="?", type=int, help="Number of puzzles (e.g., 50)."
    )
    parser.add_argument(
        "difficulty",
        nargs="?",
        choices=["easy", "medium", "hard", "mixed"],
        help="Puzzle difficulty.",
    )
    parser.add_argument(
        "--format",
        default="paperback",
        choices=["paperback", "hardcover", "both"],
        help="Book format(s).",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip market validation for faster generation.",
    )

    args = parser.parse_args()

    # Interactive mode if essential args are missing
    theme = args.theme or input("📚 Enter book theme: ").strip()
    count = args.count or int(
        input("🔢 Number of puzzles (e.g., 50): ").strip() or "50"
    )
    difficulty = (
        args.difficulty
        or input("⚡ Difficulty (easy/medium/hard/mixed): ").strip()
        or "medium"
    )

    if not all([theme, count, difficulty]):
        logger.error("❌ Theme, count, and difficulty are required.")
        sys.exit(1)

    series_name = f"{theme.title()} Puzzle Books"
    book_dir = (
        project_root
        / "output"
        / f"{theme.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}"
    )

    context = {
        "theme": theme,
        "count": count,
        "difficulty": difficulty,
        "format": args.format,
        "book_dir": book_dir,
        "project_root": project_root,
        "series_name": series_name,
        "volume_num": 1,  # Default to volume 1 for single runs
        "puzzle_type": "crossword",
    }

    logger.info(f"\n🚀 Starting Business-in-a-Box Generation for '{theme}'...")
    book_dir.mkdir(parents=True, exist_ok=True)

    pipeline = [
        ("Market Validation", run_market_validation if not args.quick else None),
        ("Unified Content Generation", run_unified_generator),
        ("Content-Aware QA", run_qa_validation),
        ("Marketing Asset Generation", generate_marketing_assets),
        ("KDP Launch Package Creation", create_launch_package),
    ]

    for i, (step_name, step_func) in enumerate(pipeline, 1):
        if step_func is None:
            continue
        logger.info(f"\n--- [Step {i}/{len(pipeline)}] {step_name} ---")
        if not step_func(context):
            logger.error(f"❌ Pipeline failed at step: {step_name}. Aborting.")
            sys.exit(1)
        logger.info(f"✅ Step '{step_name}' completed successfully.")

    logger.info("\n" + "=" * 60)
    logger.info("🎉 SUCCESS! Your complete book business package is ready!")
    logger.info(f"   Find all your files in: {context['book_dir']}")
    logger.info(
        "   Next step: Follow the KDP_LAUNCH_CHECKLIST.md to publish and market your book."
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
