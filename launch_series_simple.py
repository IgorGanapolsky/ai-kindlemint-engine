#!/usr/bin/env python3
"""
Simple Series Launcher - GET PUBLISHING TODAY!
Focus on generating and saving books locally first, then add KDP later
"""
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

def generate_simple_book(series_name, volume_number):
    """Generate a simple book structure for immediate testing"""
    
    book_data = {
        "title": f"{series_name} - Volume {volume_number}",
        "subtitle": "Easy and Fun Puzzles for Everyone",
        "author": "Senior Puzzle Studio",
        "series": series_name,
        "volume_number": volume_number,
        "description": f"This is Volume {volume_number} of the {series_name} series. "
                      "Featuring large print crossword puzzles perfect for seniors and puzzle enthusiasts. "
                      "Each puzzle is carefully crafted with clear, easy-to-read fonts and engaging themes.",
        "keywords": [
            "large print crosswords",
            "crossword puzzles", 
            "seniors puzzles",
            "easy crosswords",
            "puzzle books",
            "brain games",
            "word puzzles"
        ],
        "price": 7.99,
        "generated_at": datetime.now().isoformat(),
        "status": "generated_locally"
    }
    
    return book_data

def save_book_locally(book_data, output_dir):
    """Save book data locally for testing"""
    
    # Create directory structure
    series_dir = output_dir / book_data["series"].replace(" ", "_")
    volume_dir = series_dir / f"volume_{book_data['volume_number']}"
    volume_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metadata
    metadata_file = volume_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(book_data, f, indent=2)
    
    # Create placeholder files
    (volume_dir / "manuscript.txt").write_text(f"""
{book_data['title']}
{book_data['subtitle']}

By {book_data['author']}

This is a placeholder manuscript for {book_data['title']}.
In a real implementation, this would contain the full crossword puzzle content.

Volume {book_data['volume_number']} of the {book_data['series']} series.

Generated on: {book_data['generated_at']}
""")
    
    (volume_dir / "cover_placeholder.txt").write_text(f"""
Cover design for: {book_data['title']}
Series: {book_data['series']}
Volume: {book_data['volume_number']}

This is a placeholder. In production, this would be a PNG/JPG cover image.
""")
    
    return volume_dir

def launch_series_simple(series_name="Large Print Crossword Masters", dry_run=True):
    """Simple series launch that actually works"""
    
    print("🚀" * 20)
    print("📚 SIMPLE SERIES LAUNCHER - GET PUBLISHING TODAY!")
    print("🚀" * 20)
    print(f"📖 Series: {series_name}")
    print(f"🧪 Dry run: {dry_run}")
    print("🚀" * 20)
    
    # Setup output directory
    output_dir = Path("output/Senior_Puzzle_Studio")
    
    try:
        # Generate Volume 1
        print("📝 Generating Volume 1...")
        book_data = generate_simple_book(series_name, 1)
        print(f"✅ Generated: {book_data['title']}")
        
        # Save locally
        print("💾 Saving locally...")
        volume_dir = save_book_locally(book_data, output_dir)
        print(f"✅ Saved to: {volume_dir}")
        
        # List what we created
        print("\n📁 Created files:")
        for file in volume_dir.iterdir():
            print(f"   📄 {file.name}")
        
        # Report success
        print("\n🎉 SUCCESS!")
        print(f"📖 Book generated: {book_data['title']}")
        print(f"📁 Location: {volume_dir}")
        print(f"💰 Price: ${book_data['price']}")
        
        if dry_run:
            print("\n🧪 DRY RUN MODE:")
            print("   - Book generated and saved locally")
            print("   - No KDP publishing attempted")
            print("   - Ready for manual review and testing")
        else:
            print("\n🚀 PRODUCTION MODE:")
            print("   - Book generated successfully")
            print("   - KDP publishing would happen here")
            print("   - Add KDP credentials to enable publishing")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Simple Series Launcher')
    parser.add_argument('--series', default='Large Print Crossword Masters', 
                       help='Series name')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Generate locally without KDP publishing')
    
    args = parser.parse_args()
    
    success = launch_series_simple(args.series, args.dry_run)
    
    if success:
        print("\n✅ SERIES LAUNCH SUCCESSFUL!")
        print("🎯 Next steps:")
        print("   1. Review generated content")
        print("   2. Add KDP credentials") 
        print("   3. Test KDP authentication")
        print("   4. Publish first book!")
    else:
        print("\n❌ SERIES LAUNCH FAILED!")
        print("🔧 Fix issues and try again")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())