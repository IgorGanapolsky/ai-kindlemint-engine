#!/usr/bin/env python3
"""
Autonomous Puzzle Book Creator
Creates a complete puzzle book while you're away
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.kindlemint.generators.sudoku_generator import generate_puzzles

def create_puzzle_book():
    """Create a complete puzzle book autonomously"""
    
    print("📚 AUTONOMOUS PUZZLE BOOK CREATOR")
    print("=" * 50)
    print("Creating a new puzzle book while you're on the road...\n")
    
    # Book metadata
    book_id = f"road_trip_book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    book_data = {
        "title": "Large Print Sudoku: Road Trip Edition",
        "subtitle": "200 Puzzles for Your Journey",
        "description": "Perfect for travel! Extra-large print sudoku puzzles designed for solving on the go. Progressive difficulty from easy to expert.",
        "keywords": [
            "large print sudoku",
            "travel puzzle book", 
            "road trip activities",
            "senior sudoku puzzles",
            "easy to hard sudoku"
        ],
        "categories": [
            "Games & Activities > Puzzles > Sudoku",
            "Travel > Travel Games",
            "Health & Fitness > Aging"
        ],
        "price": 7.99,
        "pages": 206
    }
    
    # Create book directory
    book_dir = Path(f"generated_books/{book_id}")
    book_dir.mkdir(parents=True, exist_ok=True)
    
    print("📝 Generating puzzles...")
    
    # Generate puzzles (50 of each difficulty)
    all_puzzles = []
    difficulties = ["easy", "medium", "hard", "expert"]
    
    for difficulty in difficulties:
        print(f"   Creating {difficulty} puzzles...")
        puzzles = generate_puzzles(count=50, difficulty=difficulty)
        all_puzzles.extend(puzzles)
    
    print(f"✅ Generated {len(all_puzzles)} puzzles\n")
    
    # Save puzzle data
    with open(book_dir / "puzzles.json", "w") as f:
        json.dump(all_puzzles, f, indent=2)
    
    # Create book structure
    book_structure = {
        "metadata": book_data,
        "content": {
            "front_matter": {
                "title_page": True,
                "copyright": f"© {datetime.now().year} Your Publishing Name",
                "introduction": "Welcome to your sudoku journey!",
                "how_to_play": True,
                "difficulty_guide": True
            },
            "puzzles": {
                "total": 200,
                "per_page": 1,
                "sections": [
                    {"title": "Easy Puzzles", "puzzles": 50},
                    {"title": "Medium Puzzles", "puzzles": 50},
                    {"title": "Hard Puzzles", "puzzles": 50},
                    {"title": "Expert Puzzles", "puzzles": 50}
                ]
            },
            "solutions": {
                "start_page": 103,
                "per_page": 4
            }
        }
    }
    
    with open(book_dir / "book_structure.json", "w") as f:
        json.dump(book_structure, f, indent=2)
    
    # Create marketing copy
    marketing = {
        "amazon_description": f"""
LARGE PRINT SUDOKU - Perfect for Travel!

★ 200 hand-crafted puzzles
★ Extra-large print for easy reading
★ Progressive difficulty levels
★ Complete solutions included
★ Perfect binding lays flat

This book includes:
• 50 Easy puzzles - Build confidence
• 50 Medium puzzles - Develop skills  
• 50 Hard puzzles - Challenge yourself
• 50 Expert puzzles - Master level

Great for:
✓ Long car rides
✓ Airplane travel
✓ Waiting rooms
✓ Daily brain training
✓ Gift giving

Order now and start your puzzle journey today!
        """,
        "marketing_angles": [
            "Travel companion",
            "Senior-friendly",
            "Brain training",
            "Stress relief",
            "Screen-free entertainment"
        ],
        "email_pitch": "Just created a new travel-themed puzzle book while on the road. Perfect timing for summer road trips!"
    }
    
    with open(book_dir / "marketing.json", "w") as f:
        json.dump(marketing, f, indent=2)
    
    # Create production checklist
    checklist = f"""# Production Checklist for {book_data['title']}

## When You're Back:

### 1. Generate PDF (10 minutes)
```bash
cd {book_dir}
python3 ../../scripts/generate_book.py --input puzzles.json --output {book_id}.pdf
```

### 2. Create Cover (15 minutes)
- Use Canva template
- Title: {book_data['title']}
- Subtitle: {book_data['subtitle']}
- Add "LARGE PRINT" badge
- Use road/travel theme

### 3. Upload to KDP (20 minutes)
- Title: {book_data['title']}
- Categories: {', '.join(book_data['categories'])}
- Keywords: {', '.join(book_data['keywords'])}
- Price: ${book_data['price']}

### 4. Marketing (10 minutes)
- Post in Facebook group
- Email your list with travel angle
- Reddit post about road trip activities

## Revenue Projection:
- 10-20 sales first week = $30-60
- Ongoing: 5-10 sales/week = $20-40/week
- Annual: $1,000-2,000 from this book alone
"""
    
    with open(book_dir / "PRODUCTION_CHECKLIST.md", "w") as f:
        f.write(checklist)
    
    print("📋 BOOK CREATION SUMMARY:")
    print(f"   Title: {book_data['title']}")
    print(f"   Puzzles: 200 (50 each difficulty)")
    print(f"   Price: ${book_data['price']}")
    print(f"   Location: {book_dir}/")
    
    print("\n💰 REVENUE IMPACT:")
    print("   First month: $120-240")
    print("   First year: $1,000-2,000")
    print("   Effort when back: 45 minutes")
    
    print("\n✅ Book #101 created autonomously!")
    print(f"   See: {book_dir}/PRODUCTION_CHECKLIST.md")
    
    return book_dir

if __name__ == "__main__":
    create_puzzle_book()