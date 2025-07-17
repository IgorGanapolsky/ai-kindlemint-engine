#!/usr/bin/env python3
"""
Quick Revenue Setup - Get your book selling TODAY
"""

import json


def setup_gumroad_product():
    """Generate Gumroad product configuration"""
    
    product_config = {
        "title": "Large Print Sudoku Volume 1 - 100 Progressive Puzzles",
        "price": 8.99,
        "description": """Perfect for seniors and puzzle lovers!

✅ 100 puzzles with progressive difficulty
✅ Large print format - easy on the eyes
✅ Complete solutions included
✅ 25 Easy + 50 Medium + 25 Hard puzzles

Start your brain training journey today!""",
        
        "tags": ["sudoku", "puzzles", "large print", "seniors", "brain training"],
        "category": "Books & Education",
        
        "marketing_copy": {
            "headline": "Keep Your Mind Sharp with Large Print Sudoku",
            "subheadline": "100 Progressive Puzzles Perfect for Daily Brain Training",
            "call_to_action": "Get Instant Download - Only $8.99"
        }
    }
    
    # Save configuration
    with open('gumroad_product_config.json', 'w') as f:
        json.dump(product_config, f, indent=2)
    
    print("✅ Gumroad product configuration created!")
    print("📁 Upload file: Large_Print_Sudoku_Complete.pdf")
    print(f"💰 Price: ${product_config['price']}")
    

def create_reddit_post():
    """Generate Reddit marketing post"""
    
    post = """I created a Large Print Sudoku book for my grandma who loves puzzles but struggles with small print. She loved it so much, I decided to share it!

Features:
• 100 puzzles (25 easy, 50 medium, 25 hard)
• Extra large print that's easy on the eyes
• Progressive difficulty to build skills
• Complete solutions included
• Clear instructions on every page

I made it specifically for seniors and anyone who finds regular puzzle books too small to read comfortably. 

If you know someone who might enjoy this, it's available as an instant PDF download for $8.99.

Happy puzzling! 🧩"""
    
    with open('reddit_marketing_post.txt', 'w') as f:
        f.write(post)
    
    print("\n📝 Reddit post created!")
    print("Post to: r/sudoku, r/puzzles, r/eldercare")


def create_landing_page():
    """Generate simple landing page HTML"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Large Print Sudoku - Easy on the Eyes</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .hero { text-align: center; padding: 40px 0; }
        .cta-button { 
            background: #27AE60; 
            color: white; 
            padding: 15px 40px; 
            font-size: 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .features { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 40px 0; }
        .feature { padding: 20px; background: #f5f5f5; border-radius: 10px; }
        .price { font-size: 36px; color: #27AE60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>Large Print Sudoku Volume 1</h1>
        <h2>100 Progressive Puzzles Perfect for Seniors</h2>
        <p class="price">Only $8.99</p>
        <a href="YOUR_GUMROAD_LINK" class="cta-button">Get Instant Download</a>
    </div>
    
    <div class="features">
        <div class="feature">
            <h3>👁️ Easy on the Eyes</h3>
            <p>Extra large print designed for comfortable solving</p>
        </div>
        <div class="feature">
            <h3>📈 Progressive Difficulty</h3>
            <p>25 Easy + 50 Medium + 25 Hard puzzles</p>
        </div>
        <div class="feature">
            <h3>📖 Complete Solutions</h3>
            <p>All answers included at the back</p>
        </div>
        <div class="feature">
            <h3>🧠 Brain Training</h3>
            <p>Perfect for daily mental exercise</p>
        </div>
    </div>
    
    <div style="text-align: center; margin: 40px 0;">
        <h2>Start Your Puzzle Journey Today!</h2>
        <a href="YOUR_GUMROAD_LINK" class="cta-button">Buy Now - Instant Download</a>
    </div>
</body>
</html>"""
    
    with open('sudoku_landing_page.html', 'w') as f:
        f.write(html)
    
    print("\n🌐 Landing page created!")
    print("Host on: GitHub Pages, Netlify, or Vercel")


def main():
    print("🚀 Quick Revenue Setup for Large Print Sudoku")
    print("=" * 50)
    
    # Create all marketing materials
    setup_gumroad_product()
    create_reddit_post()
    create_landing_page()
    
    print("\n📋 Next Steps:")
    print("1. Create Gumroad account (free)")
    print("2. Upload Large_Print_Sudoku_Complete.pdf")
    print("3. Set price to $8.99")
    print("4. Get your product link")
    print("5. Update landing page with your link")
    print("6. Share on Reddit and social media")
    print("\n💰 Start making sales TODAY!")


if __name__ == "__main__":
    main()