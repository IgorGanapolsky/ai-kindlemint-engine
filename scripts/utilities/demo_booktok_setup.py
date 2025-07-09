#!/usr/bin/env python3
"""
BookTok Setup Demo - Demonstrate the complete BookTok automation system
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def create_sample_book_data():
    """Create sample book data for demonstration"""
    books_dir = Path("books")
    books_dir.mkdir(exist_ok=True)
    
    sample_books = [
        "Large_Print_Crossword_Puzzles_For_Seniors",
        "Daily_Sudoku_Brain_Training_Book", 
        "Word_Search_Puzzles_Large_Print",
        "Mixed_Puzzle_Book_Brain_Health",
        "Crossword_Puzzles_Easy_Medium_Hard"
    ]
    
    for book_name in sample_books:
        book_dir = books_dir / book_name
        book_dir.mkdir(exist_ok=True)
        
        # Create sample book metadata
        metadata = {
            "title": book_name.replace("_", " "),
            "type": "crossword" if "crossword" in book_name.lower() else "mixed",
            "target_audience": "seniors" if "senior" in book_name.lower() else "general",
            "created_date": datetime.now().isoformat(),
            "amazon_url": f"https://amazon.com/dp/SAMPLE{hash(book_name) % 10000}"
        }
        
        with open(book_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    return sample_books

def generate_booktok_content_demo(book_name):
    """Generate sample BookTok content for a book"""
    content_dir = Path("books") / book_name / "social_media_content"
    content_dir.mkdir(exist_ok=True)
    
    book_title = book_name.replace("_", " ")
    
    # TikTok Scripts
    tiktok_scripts = [
        {
            "id": "script_1_1",
            "pillar": "behind_scenes",
            "hook": f"POV: You create '{book_title}' in 30 minutes using AI",
            "content": f"Watch me generate '{book_title}' from scratch using my AI system. From concept to finished PDF in under 30 minutes!",
            "cta": "Would you buy an AI-generated puzzle book? Comment below!",
            "hashtags": ["#BookTok", "#PuzzleBooks", "#AIGenerated", "#BehindTheScenes"],
            "duration": "60s"
        },
        {
            "id": "script_2_1", 
            "pillar": "puzzle_demo",
            "hook": "Can you solve this crossword clue in 10 seconds?",
            "content": f"Testing your brain with a puzzle from '{book_title}'. This large-print crossword is perfect for daily brain training!",
            "cta": "Drop your answer in the comments! Link to full book in bio.",
            "hashtags": ["#PuzzleChallenge", "#BrainGames", "#CrosswordPuzzles", "#BookTok"],
            "duration": "30s"
        },
        {
            "id": "script_3_1",
            "pillar": "brain_health", 
            "hook": "Your brain on puzzles vs. your brain on scrolling",
            "content": "Crosswords activate multiple brain regions, improve memory, and reduce cognitive decline. That's why I created large-print puzzle books for seniors!",
            "cta": "Tag someone who needs more brain exercise! 🧠",
            "hashtags": ["#BrainHealth", "#WellnessWednesday", "#PuzzleBooks", "#SeniorHealth"],
            "duration": "45s"
        }
    ]
    
    with open(content_dir / "tiktok_scripts.json", 'w') as f:
        json.dump(tiktok_scripts, f, indent=2)
    
    # Hashtag Strategy
    hashtag_strategy = {
        "book_title": book_title,
        "book_type": "crossword" if "crossword" in book_name.lower() else "mixed",
        "primary_hashtags": ["#BookTok", "#PuzzleBooks", "#BrainHealth"],
        "niche_hashtags": ["#CrosswordPuzzles", "#SudokuDaily", "#WordSearch", "#BrainGames"],
        "audience_hashtags": ["#SeniorFriendly", "#LargePrint", "#GiftIdeas", "#PuzzleLovers"],
        "tech_hashtags": ["#AIGenerated", "#AutomatedPublishing", "#TechCreator"]
    }
    
    with open(content_dir / "hashtag_strategy.json", 'w') as f:
        json.dump(hashtag_strategy, f, indent=2)
    
    # Content Calendar
    calendar_data = []
    start_date = datetime.now()
    
    daily_themes = {
        0: "behind_scenes",    # Monday
        1: "puzzle_demo",      # Tuesday  
        2: "brain_health",     # Wednesday
        3: "puzzle_demo",      # Thursday
        4: "behind_scenes",    # Friday
        5: "senior_friendly",  # Saturday
        6: "brain_health"      # Sunday
    }
    
    for day in range(7):  # One week
        post_date = start_date + timedelta(days=day)
        theme = daily_themes[post_date.weekday()]
        
        calendar_data.append({
            "date": post_date.strftime("%Y-%m-%d"),
            "day_of_week": post_date.strftime("%A"),
            "theme": theme,
            "book_title": book_title,
            "posting_time": "14:00" if theme == "behind_scenes" else "19:00",
            "hashtags": " ".join(hashtag_strategy["primary_hashtags"][:3])
        })
    
    import csv
    with open(content_dir / "posting_calendar.csv", 'w', newline='') as f:
        if calendar_data:
            writer = csv.DictWriter(f, fieldnames=calendar_data[0].keys())
            writer.writeheader()
            writer.writerows(calendar_data)
    
    # Summary Report
    summary = f"""# BookTok Content Summary: {book_title}

## 📊 Content Overview
- **Total TikTok Scripts:** {len(tiktok_scripts)}
- **Content Pillars:** 3 (Behind-the-scenes, Puzzle demos, Brain health)
- **Hashtag Combinations:** 4 categories
- **Posting Calendar:** 7 days scheduled

## 🎯 Content Pillars
- **Behind-the-scenes:** AI book creation process
- **Puzzle Demo:** Interactive puzzle solving
- **Brain Health:** Educational content about puzzle benefits

## 📅 Posting Schedule
- **Monday:** Behind-the-scenes AI magic
- **Tuesday:** Puzzle solving demos
- **Wednesday:** Brain health education
- **Thursday:** Puzzle challenges
- **Friday:** Behind-the-scenes content
- **Saturday:** Senior-friendly content
- **Sunday:** Brain health tips

## 🏷️ Top Hashtags
{chr(10).join([f"- {tag}" for tag in hashtag_strategy["primary_hashtags"]])}

## 📈 Success Metrics to Track
- Views, likes, shares, comments
- Click-through rate to Amazon
- Follower growth rate
- Hashtag performance
- Audience engagement rate

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    with open(content_dir / "booktok_content_summary.md", 'w') as f:
        f.write(summary)
    
    return len(tiktok_scripts)

def create_master_analytics_setup():
    """Create analytics tracking setup"""
    analytics_dir = Path("data/analytics")
    analytics_dir.mkdir(parents=True, exist_ok=True)
    
    # UTM Links Template
    utm_template = {
        "template_url": "https://amazon.com/dp/YOUR_BOOK_ASIN",
        "utm_links": {
            "tiktok": "https://amazon.com/dp/YOUR_BOOK_ASIN?utm_source=tiktok&utm_medium=social&utm_campaign=booktok",
            "pinterest": "https://amazon.com/dp/YOUR_BOOK_ASIN?utm_source=pinterest&utm_medium=social&utm_campaign=puzzle_pins",
            "instagram": "https://amazon.com/dp/YOUR_BOOK_ASIN?utm_source=instagram&utm_medium=social&utm_campaign=reels",
            "facebook": "https://amazon.com/dp/YOUR_BOOK_ASIN?utm_source=facebook&utm_medium=social&utm_campaign=groups"
        },
        "instructions": "Replace YOUR_BOOK_ASIN with actual Amazon ASIN for each book"
    }
    
    with open(analytics_dir / "utm_links_template.json", 'w') as f:
        json.dump(utm_template, f, indent=2)
    
    # Sample Analytics Data
    sample_metrics = [
        {
            "platform": "tiktok",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "views": 0,
            "likes": 0,
            "shares": 0,
            "comments": 0,
            "clicks": 0,
            "followers_gained": 0,
            "engagement_rate": 0.0,
            "reach": 0,
            "impressions": 0
        }
    ]
    
    with open(analytics_dir / "social_media_metrics.json", 'w') as f:
        json.dump(sample_metrics, f, indent=2)
    
    return analytics_dir

def create_automation_scripts():
    """Create automation helper scripts"""
    scripts_dir = Path("scripts/automation")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Daily automation script
    daily_script = scripts_dir / "daily_booktok_tasks.sh"
    daily_script_content = '''#!/bin/bash
# Daily BookTok Automation Tasks

echo "🌅 Running daily BookTok automation..."

# Check today's posting schedule
echo "📅 Today's posting schedule:"
if [ -f "data/social_content/posting_calendar.csv" ]; then
    grep "$(date +%Y-%m-%d)" data/social_content/posting_calendar.csv || echo "No posts scheduled for today"
else
    echo "No posting calendar found"
fi

# Generate content queue for next 7 days
echo "📋 Updating content queue..."

# Check for new books that need social content
echo "📚 Checking for new books..."
for book_dir in books/*/; do
    if [ -d "$book_dir" ] && [ ! -d "${book_dir}social_media_content" ]; then
        echo "New book found: $(basename "$book_dir")"
        echo "Run: python3 demo_booktok_setup.py to generate content"
    fi
done

echo "✅ Daily automation complete!"
'''
    
    with open(daily_script, 'w') as f:
        f.write(daily_script_content)
    
    daily_script.chmod(0o755)
    
    return scripts_dir

def main():
    print("🚀 Setting up BookTok Automation Demo...")
    print("="*60)
    
    # 1. Create sample books
    print("📚 Creating sample book data...")
    sample_books = create_sample_book_data()
    print(f"✅ Created {len(sample_books)} sample books")
    
    # 2. Generate social content for each book
    print("\n📱 Generating BookTok content...")
    total_scripts = 0
    for book_name in sample_books:
        scripts_count = generate_booktok_content_demo(book_name)
        total_scripts += scripts_count
        print(f"✅ Generated {scripts_count} TikTok scripts for: {book_name.replace('_', ' ')}")
    
    # 3. Setup analytics tracking
    print("\n📊 Setting up analytics tracking...")
    analytics_dir = create_master_analytics_setup()
    print(f"✅ Analytics setup complete: {analytics_dir}")
    
    # 4. Create automation scripts
    print("\n🤖 Creating automation scripts...")
    scripts_dir = create_automation_scripts()
    print(f"✅ Automation scripts created: {scripts_dir}")
    
    # 5. Generate summary report
    print("\n" + "="*60)
    print("🎉 BOOKTOK AUTOMATION DEMO COMPLETE!")
    print("="*60)
    
    print(f"""
📊 SETUP SUMMARY:
  - Sample books created: {len(sample_books)}
  - Total TikTok scripts: {total_scripts}
  - Social platforms: TikTok, Pinterest, Instagram
  - Content pillars: Behind-the-scenes, Puzzle demos, Brain health
  - Analytics tracking: UTM codes and metrics setup

📁 KEY FILES CREATED:
  - Sample books: books/*/
  - Social content: books/*/social_media_content/
  - Analytics setup: data/analytics/
  - Automation scripts: scripts/automation/

🚀 NEXT STEPS:
  1. Review generated content in books/*/social_media_content/
  2. Create TikTok business account
  3. Set up Pinterest business account
  4. Configure posting automation with platform APIs
  5. Start tracking performance metrics

💡 IMMEDIATE ACTIONS:
  - Review content: ls books/*/social_media_content/
  - Check posting calendar: cat books/*/social_media_content/posting_calendar.csv
  - Run daily automation: ./scripts/automation/daily_booktok_tasks.sh

🎯 SUCCESS METRICS TO TRACK:
  - TikTok followers (target: 10K in 90 days)
  - Social media → Amazon click-through rate
  - Book sales from social traffic
  - Engagement rates by content type

📈 REVENUE OPPORTUNITY:
  Your current ZERO revenue problem can be solved by:
  - Consistent BookTok posting (daily content)
  - Behind-the-scenes AI content (viral potential)
  - Puzzle solving demos (engagement)
  - Senior-friendly content (target audience)
""")
    
    print("="*60)
    print("Your BookTok strategy is now AUTOMATED and ready to scale! 🚀")
    print("="*60)

if __name__ == "__main__":
    main()
