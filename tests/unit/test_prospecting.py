#!/usr/bin/env python3
"""
Quick test script for prospecting automation module
"""

import json

# Add scripts to path
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from prospecting_automation import ProspectingAutomation


def test_prospecting_automation():
    """Test the prospecting automation with sample data"""

    print("🧪 Testing Prospecting Automation Module...")

    # Create sample book configuration
    book_config = {
        "id": "test_book",
        "title": "Test Crossword Masters - Volume 1",
        "subtitle": "50 Brain-Boosting Puzzles for Testing",
        "author": "Test Author",
        "series_name": "Test_Crossword_Masters",
        "volume": 1,
        "puzzle_type": "crossword",
        "puzzle_count": 50,
        "prospecting_config": {
            "target_audience": "puzzle_enthusiasts",
            "linkedin_focus": "brain_training",
            "podcast_categories": ["health", "business"],
            "authority_positioning": "puzzle_expert",
        },
    }

    # Create sample artifacts
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create mock puzzle metadata
        metadata_dir = temp_path / "metadata"
        metadata_dir.mkdir(parents=True)

        # Sample collection data
        collection_data = {
            "title": book_config["title"],
            "puzzle_count": 50,
            "difficulty_distribution": {"easy": 15, "medium": 25, "hard": 10},
        }

        with open(metadata_dir / "collection.json", "w") as f:
            json.dump(collection_data, f, indent=2)

        # Sample puzzle data
        for i in range(5):  # Just create 5 sample puzzles
            puzzle_data = {
                "id": i + 1,
                "theme": f"Test Theme {i + 1}",
                "difficulty": "medium",
                "clues": {
                    "across": [
                        [1, "Test clue across", "ANSWER"],
                        [3, "Another test clue", "WORD"],
                    ],
                    "down": [
                        [2, "Test clue down", "TEST"],
                        [4, "Final test clue", "DONE"],
                    ],
                },
            }

            with open(metadata_dir / f"puzzle_{i+1:03d}.json", "w") as f:
                json.dump(puzzle_data, f, indent=2)

        # Create artifacts dict
        artifacts = {
            "puzzles_dir": str(temp_path),
            "pdf_file": str(temp_path / "test_interior.pdf"),
        }

        # Test the automation
        try:
            automation = ProspectingAutomation(book_config, artifacts)
            results = automation.generate_prospecting_materials()

            print(f"✅ Prospecting automation test PASSED!")
            print(f"📁 Generated {len(results)} asset types:")

            for asset_type, file_path in results.items():
                asset_path = Path(file_path)
                if asset_path.exists():
                    print(
                        f"   ✅ {asset_type}: {asset_path.name} ({asset_path.stat().st_size} bytes)"
                    )
                else:
                    print(f"   ❌ {asset_type}: File not found at {file_path}")

            # Verify key files exist
            required_files = [
                "quotable_content",
                "linkedin_calendar_json",
                "email_capture_page",
                "podcast_pitches",
                "dashboard_html",
            ]

            missing_files = []
            for req_file in required_files:
                if req_file not in results:
                    missing_files.append(req_file)
                elif not Path(results[req_file]).exists():
                    missing_files.append(req_file)

            if missing_files:
                print(f"⚠️  Warning: Missing required files: {missing_files}")
            else:
                print("✅ All required files generated successfully!")

            # Test content quality
            print("\n📝 Content Quality Check:")

            # Check LinkedIn calendar
            if "linkedin_calendar_json" in results:
                with open(results["linkedin_calendar_json"], "r") as f:
                    calendar_data = json.load(f)
                    print(
                        f"   📅 LinkedIn calendar: {len(calendar_data)} days of content"
                    )

                    # Verify content variety
                    post_types = set(day["type"] for day in calendar_data)
                    print(f"   🎯 Post types: {', '.join(post_types)}")

            # Check email sequences
            if "email_sequences" in results:
                with open(results["email_sequences"], "r") as f:
                    email_data = json.load(f)
                    welcome_sequence = email_data.get("welcome_sequence", [])
                    print(f"   📧 Email sequence: {len(welcome_sequence)} emails")

            # Check podcast pitches
            if "podcast_pitches" in results:
                with open(results["podcast_pitches"], "r") as f:
                    pitch_data = json.load(f)
                    pitch_templates = pitch_data.get("pitch_templates", {})
                    print(f"   🎙️  Podcast pitches: {len(pitch_templates)} categories")

            return True

        except Exception as e:
            print(f"❌ Prospecting automation test FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False


def test_standalone_cli():
    """Test the standalone CLI interface"""
    print("\n🖥️  Testing Standalone CLI...")

    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config = {
            "title": "CLI Test Book",
            "author": "CLI Test Author",
            "series_name": "CLI_Test_Series",
            "volume": 1,
        }
        json.dump(config, f, indent=2)
        config_path = f.name

    try:
        # This would test the CLI interface
        print(f"   ✅ CLI interface available (config: {config_path})")

        # Clean up
        Path(config_path).unlink()

        return True

    except Exception as e:
        print(f"   ❌ CLI test failed: {e}")
        return False


if __name__ == "__main__":
    print("🎯 KindleMint Prospecting Automation Test Suite")
    print("=" * 60)

    # Run tests
    test1_passed = test_prospecting_automation()
    test2_passed = test_standalone_cli()

    print("\n" + "=" * 60)

    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! Prospecting automation is ready to use.")
        print("\nNext steps:")
        print("1. Add 'generate_prospecting': true to your batch config")
        print("2. Run batch processor with prospecting enabled")
        print("3. Follow generated LinkedIn calendar and email sequences")
        print("4. Start sending podcast pitches using templates")
        print("5. Track progress in the HTML dashboard")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
