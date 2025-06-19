#!/usr/bin/env python3
"""
Manual KDP Upload Guide Generator
Creates step-by-step instructions with all prepared assets
"""
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

def generate_manual_upload_guide():
    """Generate comprehensive manual upload guide for Volume 1."""
    logger = get_logger('manual_kdp_guide')
    
    # Volume 1 folder path
    vol_1_folder = Path("output/generated_books/large_print_crossword_masters_vol_1_final")
    
    if not vol_1_folder.exists():
        logger.error(f"❌ Volume 1 folder not found: {vol_1_folder}")
        return False
    
    # File paths
    pdf_manuscript = vol_1_folder / "large_print_crossword_masters_vol_1_final_KDP_READY.pdf"
    cover_image = vol_1_folder / "cover_vol_1.png"
    kdp_guide = vol_1_folder / "KDP_PUBLISHING_GUIDE.txt"
    
    print("=" * 80)
    print("📚 MANUAL KDP UPLOAD GUIDE - VOLUME 1")
    print("=" * 80)
    print()
    print("🎯 BOOK DETAILS:")
    print("   Title: Large Print Crossword Masters: Volume 1")
    print("   Subtitle: Easy Large Print Crosswords for Seniors")
    print("   Author: Senior Puzzle Studio")
    print("   Price: $7.99")
    print("   Format: Paperback")
    print("   Pages: 100+ (estimated)")
    print()
    
    print("📁 REQUIRED FILES:")
    print(f"   ✅ PDF Manuscript: {pdf_manuscript.name}")
    print(f"      Location: {pdf_manuscript}")
    print(f"   ✅ Cover Image: {cover_image.name}")
    print(f"      Location: {cover_image}")
    print()
    
    print("🚀 STEP-BY-STEP UPLOAD PROCESS:")
    print("=" * 80)
    print()
    
    print("STEP 1: LOGIN TO KDP")
    print("-" * 20)
    print("1. Go to: https://kdp.amazon.com")
    print("2. Click 'Sign In'")
    print("3. Enter your Amazon account credentials")
    print("4. Complete 2FA if required")
    print()
    
    print("STEP 2: CREATE NEW BOOK")
    print("-" * 25)
    print("1. Click 'Create New Title' button")
    print("2. Select 'Paperback' (not Kindle eBook)")
    print("3. You'll be taken to the book setup page")
    print()
    
    print("STEP 3: BOOK DETAILS TAB")
    print("-" * 24)
    print("1. Title: Large Print Crossword Masters: Volume 1")
    print("2. Subtitle: Easy Large Print Crosswords for Seniors")
    print("3. Author: Senior Puzzle Studio")
    print("4. Description: (copy from below)")
    print()
    
    # Read description from KDP guide
    try:
        with open(kdp_guide, 'r') as f:
            guide_content = f.read()
        
        # Extract description
        desc_start = guide_content.find("→ Description:") + len("→ Description:")
        desc_end = guide_content.find("\n4. KEYWORDS")
        description = guide_content[desc_start:desc_end].strip()
        
        print("   DESCRIPTION TO COPY:")
        print("   " + "="*50)
        print(f"   {description}")
        print("   " + "="*50)
        print()
        
    except Exception as e:
        logger.warning(f"Could not extract description: {e}")
    
    print("5. Keywords (enter each in separate field):")
    keywords = [
        "large print crossword",
        "easy crossword puzzles", 
        "senior crossword puzzles",
        "crossword for seniors",
        "puzzle book for seniors",
        "large print puzzle book",
        "easy brain games"
    ]
    
    for i, keyword in enumerate(keywords, 1):
        print(f"   Keyword {i}: {keyword}")
    print()
    
    print("6. Categories:")
    print("   Primary: Games & Puzzles > Crosswords")
    print("   Secondary: Health & Fitness > Aging")
    print()
    print("7. Click 'Save and Continue'")
    print()
    
    print("STEP 4: CONTENT TAB")
    print("-" * 17)
    print("1. Upload Manuscript:")
    print(f"   - Click 'Upload your manuscript'")
    print(f"   - Select file: {pdf_manuscript}")
    print(f"   - Wait for upload to complete (may take 2-5 minutes)")
    print()
    print("2. Upload Cover:")
    print(f"   - Click 'Upload a cover you already have'")
    print(f"   - Select file: {cover_image}")
    print(f"   - Wait for cover processing")
    print()
    print("3. Review Preview:")
    print("   - Check that crossword grids are clearly visible")
    print("   - Verify text is large and readable")
    print("   - Ensure cover looks professional")
    print()
    print("4. Click 'Save and Continue'")
    print()
    
    print("STEP 5: PRICING TAB")
    print("-" * 18)
    print("1. Territories: Select 'All territories'")
    print("2. Primary marketplace: Amazon.com")
    print("3. Print price: $7.99")
    print("4. Royalty: Will be calculated automatically (~60%)")
    print("5. Expanded distribution: Optional (recommended YES)")
    print("6. Click 'Save and Continue'")
    print()
    
    print("STEP 6: REVIEW & PUBLISH")
    print("-" * 24)
    print("1. Review all information carefully:")
    print("   - Book details are correct")
    print("   - Manuscript uploaded successfully")
    print("   - Cover looks professional")
    print("   - Pricing is set to $7.99")
    print()
    print("2. Click 'Publish Your Book'")
    print()
    print("3. Confirmation:")
    print("   - You'll see 'Your book has been submitted'")
    print("   - Note down the ASIN if provided")
    print("   - Book will be 'In Review' status")
    print()
    
    print("STEP 7: REVIEW PROCESS")
    print("-" * 22)
    print("⏰ Timeline: 24-72 hours typically")
    print("📧 Email: You'll receive notification when approved")
    print("🔍 Status: Check KDP dashboard for updates")
    print("🛠️ Changes: Can be made while in review if needed")
    print()
    
    print("🎉 SUCCESS INDICATORS:")
    print("=" * 80)
    print("✅ Book status changes to 'Live'")
    print("✅ ASIN appears in your dashboard")
    print("✅ Book is visible on Amazon.com")
    print("✅ Amazon assigns a publication date")
    print("✅ You can view your book's Amazon page")
    print()
    
    print("💰 REVENUE TRACKING:")
    print("=" * 80)
    print("📊 KDP Reports: Available 24-48 hours after sales")
    print("💵 Royalty Rate: ~60% of list price = ~$4.80 per book")
    print("📈 Sales Rank: Track in Books > Games & Puzzles")
    print("⭐ Reviews: Monitor customer feedback")
    print()
    
    print("🚨 TROUBLESHOOTING:")
    print("=" * 80)
    print("❌ Upload fails: Check file size (PDF should be < 50MB)")
    print("❌ Cover rejected: Ensure high resolution (300 DPI minimum)")
    print("❌ Content issues: Review for formatting problems")
    print("❌ Review delays: Contact KDP support if > 72 hours")
    print()
    
    print("📋 NEXT STEPS AFTER PUBLICATION:")
    print("=" * 80)
    print("1. 🔗 Get your Amazon book URL")
    print("2. 📱 Share on social media")
    print("3. 🎯 Target senior Facebook groups")
    print("4. 📧 Email your network")
    print("5. 🚀 Prepare Volume 2 for series momentum")
    print()
    
    print("=" * 80)
    print("🎯 YOUR BOOK IS READY FOR SUCCESS!")
    print("📚 50 High-Quality Crossword Puzzles")
    print("🎨 Professional Cover Design")
    print("💰 Premium Pricing Strategy")
    print("🔥 Series Potential for Growth")
    print("=" * 80)
    
    return True

def main():
    """Main function."""
    print("Generating manual KDP upload guide...")
    success = generate_manual_upload_guide()
    
    if success:
        print("\n✅ Manual upload guide generated successfully!")
        print("📋 Follow the steps above to publish Volume 1 to KDP")
        return True
    else:
        print("\n❌ Failed to generate upload guide")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)