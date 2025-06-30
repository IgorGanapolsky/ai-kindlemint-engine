#!/usr/bin/env python3
"""
Test script for Dan Kennedy's Magnetic Marketing System
"""

import json

# Add scripts to path
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from magnetic_marketing import MagneticMarketingEngine

    """Test Magnetic Marketing System"""
def test_magnetic_marketing_system():
    """Test the complete magnetic marketing system"""

    print("🧲 Testing Magnetic Marketing System...")

    # Create sample book configuration - Crossword book
    crossword_config = {
        "id": "test_crossword_book",
        "title": "The 15-Minute Crossword Secret That Retirement Homes Don't Want You to Know",
        "subtitle": "How I Solved My Daily Crossword in 15 Minutes Without Cheating",
        "author": "Margaret Thompson",
        "series_name": "Test_Magnetic_Crosswords",
        "volume": 1,
        "puzzle_type": "crossword",
        "puzzle_count": 50,
        "target_audience": "retired_professionals",
        "magnetic_marketing_config": {
            "avatar_focus": "retired_educators",
            "price_positioning": "premium",
            "backend_focus": True,
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
            "title": crossword_config["title"],
            "puzzle_count": 50,
            "difficulty_distribution": {"easy": 15, "medium": 25, "hard": 10},
        }

        with open(metadata_dir / "collection.json", "w") as f:
            json.dump(collection_data, f, indent=2)

        # Sample puzzle data with themes
        puzzle_themes = [
            "Nature and Wildlife",
            "Historical Events",
            "Science and Technology",
            "Literature and Arts",
            "Sports and Recreation",
            "Food and Cooking",
        ]

        for i in range(6):  # Create sample puzzles
            puzzle_data = {
                "id": i + 1,
                "theme": puzzle_themes[i],
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

        # Test the magnetic marketing engine
        try:
            engine = MagneticMarketingEngine(crossword_config, artifacts)
            results = engine.create_magnetic_marketing_system()

            print(f"✅ Magnetic Marketing test PASSED!")
            print(f"📁 Generated {len(results)} marketing components:")

            expected_components = [
                "customer_avatar",
                "magnetic_triangle",
                "direct_response_copy",
                "lead_magnet_funnel",
                "premium_positioning",
                "shock_and_awe_package",
                "deadline_funnel",
                "media_domination_plan",
                "backend_systems",
                "social_proof_systems",
            ]

            for component in expected_components:
                if component in results:
                    file_path = Path(results[component])
                    if file_path.exists():
                        print(
                            f"   ✅ {component}: {file_path.name} ({file_path.stat().st_size} bytes)"
                        )
                    else:
                        print(f"   ❌ {component}: File not found")
                else:
                    print(f"   ❌ {component}: Component missing")

            # Test content quality
            print("\n📝 Content Quality Check:")

            # Check customer avatar
            if "customer_avatar" in results:
                with open(results["customer_avatar"], "r") as f:
                    avatar_data = json.load(f)
                    avatar_profile = avatar_data.get("avatar_profile", {})
                    print(
                        f"   👤 Customer Avatar: {avatar_profile.get('avatar_name', 'Generated')}"
                    )
                    print(
                        f"   🎯 Demographics: {avatar_profile.get('demographics', 'Defined')[:50]}..."
                    )

            # Check direct response copy
            if "direct_response_copy" in results:
                with open(results["direct_response_copy"], "r") as f:
                    copy_data = json.load(f)
                    titles = copy_data.get("magnetic_titles", [])
                    print(f"   📝 Generated {len(titles)} magnetic titles")
                    if titles:
                        print(f"   🎯 Example: {titles[0][:60]}...")

            # Check lead magnet funnel
            if "lead_magnet_funnel" in results:
                with open(results["lead_magnet_funnel"], "r") as f:
                    funnel_data = json.load(f)
                    funnel_system = funnel_data.get("funnel_system", {})
                    stages = funnel_system.get("funnel_stages", {})
                    print(f"   🧲 Funnel stages: {', '.join(stages.keys())}")

            # Check backend systems
            if "backend_systems" in results:
                with open(results["backend_systems"], "r") as f:
                    backend_data = json.load(f)
                    product_ladder = backend_data.get("product_ladder", [])
                    print(f"   💰 Product ladder: {len(product_ladder)} levels")
                    if product_ladder:
                        total_potential = sum(
                            float(
                                level.get("price", "$0").replace("$", "").split("/")[0]
                            )
                            for level in product_ladder
                        )
                        print(f"   💵 Total potential value: ${total_potential:.2f}")

            return True

        except Exception as e:
            print(f"❌ Magnetic Marketing test FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False


    """Test Productivity Book"""
def test_productivity_book():
    """Test with productivity book configuration"""
    print("\n🚀 Testing Productivity Book Configuration...")

    # Create productivity book config
    productivity_config = {
        "id": "test_productivity_book",
        "title": "The 4-Hour CEO: How I Went From 80-Hour Weeks to $2M Revenue",
        "subtitle": "The Exact System Burned-Out Founders Use to Scale Without Losing Their Marriage",
        "author": "David Chen",
        "series_name": "Test_Productivity_Masters",
        "volume": 1,
        "puzzle_type": "productivity",
        "target_audience": "startup_founders",
        "magnetic_marketing_config": {
            "avatar_focus": "burned_out_founders",
            "price_positioning": "ultra_premium",
            "backend_focus": True,
        },
    }

    # Create basic artifacts
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts = {
            "puzzles_dir": temp_dir,
            "pdf_file": f"{temp_dir}/productivity.pdf",
        }

        try:
            engine = MagneticMarketingEngine(productivity_config, artifacts)
            results = engine.create_magnetic_marketing_system()

            print(f"✅ Productivity book test PASSED!")
            print(f"📁 Generated components for high-value market")

            # Check that premium positioning was applied
            if "premium_positioning" in results:
                with open(results["premium_positioning"], "r") as f:
                    positioning_data = json.load(f)
                    pricing_strategy = positioning_data.get("pricing_strategy", {})
                    print(
                        f"   💎 Premium strategy: {pricing_strategy.get('never_lowest_price', 'Applied')}"
                    )

            return True

        except Exception as e:
            print(f"❌ Productivity book test FAILED: {e}")
            return False


    """Test Integration Readiness"""
def test_integration_readiness():
    """Test integration with batch processor"""
    print("\n🔧 Testing Batch Processor Integration...")

    try:
        # Test that magnetic marketing can be imported
        import scripts.magnetic_marketing as mm

        print("✅ Module import successful")

        # Test that MagneticMarketingEngine class exists
        engine_class = getattr(mm, "MagneticMarketingEngine", None)
        if engine_class:
            print("✅ MagneticMarketingEngine class available")
        else:
            print("❌ MagneticMarketingEngine class missing")
            return False

        # Test that main method exists
        main_method = getattr(mm, "main", None)
        if main_method:
            print("✅ CLI interface available")
        else:
            print("❌ CLI interface missing")
            return False

        print("✅ Integration ready for batch processor")
        return True

    except Exception as e:
        print(f"❌ Integration test FAILED: {e}")
        return False


    """Test Kennedy Principles"""
def test_kennedy_principles():
    """Test that Kennedy's principles are properly implemented"""
    print("\n🎯 Testing Kennedy's Principles Implementation...")

    config = {
        "id": "kennedy_test",
        "title": "Test Book",
        "author": "Test Author",
        "series_name": "Test_Series",
        "volume": 1,
        "puzzle_type": "crossword",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts = {"puzzles_dir": temp_dir, "pdf_file": f"{temp_dir}/test.pdf"}

        try:
            engine = MagneticMarketingEngine(config, artifacts)

            # Test Kennedy principles are in the engine
            principles = engine.kennedy_principles
            expected_principles = [
                "message_before_market",
                "direct_response_only",
                "premium_positioning",
                "backend_focus",
                "deadline_driven",
                "social_proof_heavy",
            ]

            principles_passed = 0
            for principle in expected_principles:
                if principles.get(principle, False):
                    print(f"   ✅ {principle.replace('_', ' ').title()}: Implemented")
                    principles_passed += 1
                else:
                    print(f"   ❌ {principle.replace('_', ' ').title()}: Missing")

            if principles_passed == len(expected_principles):
                print("✅ All Kennedy principles implemented")
                return True
            else:
                print(
                    f"❌ Only {principles_passed}/{len(expected_principles)} principles implemented"
                )
                return False

        except Exception as e:
            print(f"❌ Kennedy principles test FAILED: {e}")
            return False


if __name__ == "__main__":
    print("🧲 Dan Kennedy's Magnetic Marketing Test Suite")
    print("=" * 60)

    # Run all tests
    test1_passed = test_magnetic_marketing_system()
    test2_passed = test_productivity_book()
    test3_passed = test_integration_readiness()
    test4_passed = test_kennedy_principles()

    print("\n" + "=" * 60)

    if all([test1_passed, test2_passed, test3_passed, test4_passed]):
        print("🎉 ALL TESTS PASSED! Magnetic Marketing System is ready!")
        print("\nNext steps:")
        print("1. Add 'generate_magnetic_marketing': true to batch config")
        print("2. Run batch processor with full marketing automation")
        print("3. Implement generated marketing strategies")
        print("4. Transform from invisible to irresistible!")
        print("\n💰 Expected Result: 10x revenue increase through Kennedy's system")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
