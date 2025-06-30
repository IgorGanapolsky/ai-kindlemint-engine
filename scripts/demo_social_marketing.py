#!/usr/bin/env python3
"""
Demo Script: Social Media Marketing Podcast Integration

Demonstrates the complete transformation of book content into a
comprehensive content marketing ecosystem.
"""

import os
import sys

from kindlemint.social.core import demo_social_media_marketing

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


    """Main"""
def main():
    """Run the Social Media Marketing demonstration"""

    print("🚀 KindleMint Social Media Marketing Podcast Integration Demo")
    print("=" * 60)
    print()
    print("Transforming book content into a complete content marketing ecosystem...")
    print()

    try:
        # Run the demonstration
        results = demo_social_media_marketing()

        print("\n" + "=" * 60)
        print("✅ TRANSFORMATION COMPLETE!")
        print()
        print("📈 Results Summary:")
        print(f"   • {results['total_atomic_pieces']} atomic content pieces extracted")
        print(f"   • {results['optimized_posts']} platform-optimized posts created")
        print(f"   • {results['estimated_total_reach']:,} estimated total reach")
        print(f"   • 30-day content calendar generated")
        print(f"   • Authority building strategy developed")
        print()
        print("🎯 Your book is now a complete content marketing ecosystem!")
        print("   Ready for multi-platform distribution and audience building.")
        print()
        print("📁 Check 'social_media_marketing_results.json' for complete export.")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
