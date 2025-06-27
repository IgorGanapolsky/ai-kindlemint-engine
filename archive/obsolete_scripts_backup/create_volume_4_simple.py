#!/usr/bin/env python3
"""
Create Volume 4 of Large Print Crossword Masters
Based on successful Volume 3 generation pattern
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import json
from datetime import datetime

# Import the Volume 3 generator and modify for Volume 4
from create_volume_3_unique_solutions import Volume3CrosswordGenerator


class Volume4Generator(Volume3CrosswordGenerator):
    def __init__(self):
        # Override the output directory for Volume 4
        self.output_dir = Path(
            "books/active_production/Large_Print_Crossword_Masters/volume_4"
        )
        self.paperback_dir = self.output_dir / "paperback"
        self.hardcover_dir = self.output_dir / "hardcover"

        # Ensure directories exist
        for dir_path in [self.paperback_dir, self.hardcover_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            (dir_path / "metadata").mkdir(exist_ok=True)

        # Initialize parent class word database
        super().__init__()

        # Update metadata for Volume 4
        self.volume_number = 4
        self.title = "Large Print Crossword Masters - Volume 4"
        self.subtitle = "50 Challenging Puzzles for Word Enthusiasts"


def generate_volume_4():
    """Generate Volume 4 using the proven Volume 3 approach"""

    print("🚀 Starting Volume 4 generation...")
    print("📊 This will create 50 unique crossword puzzles")

    generator = Volume4Generator()

    # Generate metadata
    metadata = {
        "volume": 4,
        "title": generator.title,
        "subtitle": generator.subtitle,
        "author": "Crossword Masters Publishing",
        "generated_at": datetime.now().isoformat(),
        "puzzle_count": 50,
        "formats": ["paperback", "hardcover"],
    }

    # Save metadata
    for format_dir in [generator.paperback_dir, generator.hardcover_dir]:
        with open(format_dir / "metadata" / "volume_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    # Generate the puzzles and PDFs
    print("\n📝 Generating 50 unique crossword puzzles...")
    try:
        # Use the parent class method to generate everything
        generator.generate_all_formats()

        print("\n✅ Volume 4 generation complete!")
        print(f"📁 Output location: {generator.output_dir}")
        print("\n📋 Next steps:")
        print("1. Run QA validation on the generated PDFs")
        print("2. Create covers for each format")
        print("3. Generate hardcover wrap using hardcover_config.json")
        print("4. Upload to KDP")

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        raise


if __name__ == "__main__":
    generate_volume_4()
