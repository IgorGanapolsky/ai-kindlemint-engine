#!/usr/bin/env python3
"""
BookTok Content Generator - Automated Social Media Content Creation
Leverages existing AI infrastructure to create viral TikTok content from puzzle books
"""

import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from typing import Dict, List, Any
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

try:
    from kindlemint.utils.api import get_api_client
    from kindlemint.agents.content_agent import ContentAgent
except ImportError:
    print("Warning: KindleMint modules not found. Running in standalone mode.")
    get_api_client = None
    ContentAgent = None

class BookTokContentGenerator:
    """Generate viral TikTok content from puzzle books"""
    
    def __init__(self, book_directory: str):
        self.book_dir = Path(book_directory)
        self.output_dir = self.book_dir / "social_media_content"
        self.output_dir.mkdir(exist_ok=True)
        
        # Content pillars for BookTok
        self.content_pillars = {
            "behind_scenes": "Behind-the-Scenes AI Magic",
            "puzzle_demo": "Puzzle Solving Demos", 
            "brain_health": "Brain Health Education",
            "senior_friendly": "Senior-Friendly Content"
        }
        
        # Trending hashtags (updated from market research)
        self.hashtags = {
            "broad": ["#BookTok", "#PuzzleBooks", "#BrainHealth", "#SelfPublishing"],
            "niche": ["#CrosswordPuzzles", "#SudokuDaily", "#WordSearch", "#BrainGames"],
            "audience": ["#SeniorFriendly", "#LargePrint", "#GiftIdeas", "#PuzzleLovers"],
            "tech": ["#AIGenerated", "#AutomatedPublishing", "#TechCreator", "#AIBooks"]
        }
    
    def generate_tiktok_scripts(self) -> List[Dict[str, Any]]:
        """Generate 10 TikTok video scripts per book"""
        scripts = []
        
        book_title = self.book_dir.name.replace("_", " ").title()
        
        # Script templates for each content pillar
        script_templates = [
            {
                "pillar": "behind_scenes",
                "hook": "POV: You create a puzzle book in 30 minutes using AI",
                "content": f"Watch me generate '{book_title}' from scratch using my AI system. From concept to finished PDF in under 30 minutes!",
                "cta": "Would you buy an AI-generated puzzle book? Comment below!",
                "duration": "60s",
                "visual_cues": ["Screen recording of AI generation", "Time-lapse effect", "Final book reveal"]
            },
            {
                "pillar": "puzzle_demo",
                "hook": "Can you solve this crossword clue in 10 seconds?",
                "content": f"Testing your brain with a puzzle from '{book_title}'. This large-print crossword is perfect for daily brain training!",
                "cta": "Drop your answer in the comments! Link to full book in bio.",
                "duration": "30s",
                "visual_cues": ["Close-up of puzzle", "Timer countdown", "Answer reveal"]
            },
            {
                "pillar": "brain_health",
                "hook": "Your brain on puzzles vs. your brain on scrolling",
                "content": "Crosswords activate multiple brain regions, improve memory, and reduce cognitive decline. That's why I created large-print puzzle books for seniors!",
                "cta": "Tag someone who needs more brain exercise! 🧠",
                "duration": "45s",
                "visual_cues": ["Brain animation", "Before/after comparison", "Book showcase"]
            },
            {
                "pillar": "senior_friendly",
                "hook": "The perfect gift for grandparents who love puzzles",
                "content": f"Large print, high-quality paper, and engaging themes. '{book_title}' is designed specifically for senior puzzle lovers!",
                "cta": "What's your grandparent's favorite puzzle type?",
                "duration": "40s",
                "visual_cues": ["Book flip-through", "Large print close-up", "Happy senior solving"]
            }
        ]
        
        # Generate variations of each template
        for i, template in enumerate(script_templates):
            for variation in range(3):  # 3 variations per template
                script = {
                    "id": f"script_{i+1}_{variation+1}",
                    "pillar": template["pillar"],
                    "hook": template["hook"],
                    "content": template["content"],
                    "cta": template["cta"],
                    "duration": template["duration"],
                    "visual_cues": template["visual_cues"],
                    "hashtags": self._generate_hashtag_combination(),
                    "best_posting_time": self._get_optimal_posting_time(template["pillar"]),
                    "target_audience": self._get_target_audience(template["pillar"])
                }
                scripts.append(script)
        
        return scripts[:10]  # Return top 10 scripts
    
    def _generate_hashtag_combination(self) -> List[str]:
        """Generate optimized hashtag combination (max 30 hashtags)"""
        hashtags = []
        hashtags.extend(self.hashtags["broad"][:2])  # 2 broad
        hashtags.extend(self.hashtags["niche"][:3])  # 3 niche
        hashtags.extend(self.hashtags["audience"][:2])  # 2 audience
        hashtags.extend(self.hashtags["tech"][:1])  # 1 tech
        
        # Add book-specific hashtags
        book_type = self._detect_book_type()
        if book_type == "crossword":
            hashtags.extend(["#Crosswords", "#WordPuzzles", "#CrosswordDaily"])
        elif book_type == "sudoku":
            hashtags.extend(["#Sudoku", "#NumberPuzzles", "#SudokuChallenge"])
        elif book_type == "wordsearch":
            hashtags.extend(["#WordSearch", "#WordFind", "#WordHunt"])
        
        return hashtags[:30]  # TikTok limit
    
    def _detect_book_type(self) -> str:
        """Detect puzzle type from book directory name"""
        book_name = self.book_dir.name.lower()
        if "crossword" in book_name:
            return "crossword"
        elif "sudoku" in book_name:
            return "sudoku"
        elif "word" in book_name and "search" in book_name:
            return "wordsearch"
        return "mixed"
    
    def _get_optimal_posting_time(self, pillar: str) -> str:
        """Get optimal posting time based on content pillar"""
        time_map = {
            "behind_scenes": "2:00 PM EST",  # Peak engagement
            "puzzle_demo": "7:00 PM EST",    # Evening entertainment
            "brain_health": "10:00 AM EST",  # Morning motivation
            "senior_friendly": "3:00 PM EST" # Afternoon browsing
        }
        return time_map.get(pillar, "6:00 PM EST")
    
    def _get_target_audience(self, pillar: str) -> List[str]:
        """Get target audience for content pillar"""
        audience_map = {
            "behind_scenes": ["Tech enthusiasts", "Content creators", "Entrepreneurs"],
            "puzzle_demo": ["Puzzle lovers", "Brain game players", "Challenge seekers"],
            "brain_health": ["Health conscious", "Seniors", "Caregivers"],
            "senior_friendly": ["Seniors", "Adult children", "Gift buyers"]
        }
        return audience_map.get(pillar, ["General audience"])
    
    def create_content_calendar(self, scripts: List[Dict]) -> None:
        """Create 30-day posting calendar"""
        calendar_file = self.output_dir / "posting_calendar.csv"
        
        # Define posting schedule (daily themes)
        daily_themes = {
            0: "behind_scenes",    # Monday
            1: "puzzle_demo",      # Tuesday  
            2: "brain_health",     # Wednesday
            3: "puzzle_demo",      # Thursday
            4: "behind_scenes",    # Friday
            5: "senior_friendly",  # Saturday
            6: "brain_health"      # Sunday
        }
        
        calendar_data = []
        start_date = datetime.now()
        
        for day in range(30):
            post_date = start_date + timedelta(days=day)
            theme = daily_themes[post_date.weekday()]
            
            # Find script matching theme
            matching_scripts = [s for s in scripts if s["pillar"] == theme]
            if matching_scripts:
                script = matching_scripts[day % len(matching_scripts)]
                
                calendar_data.append({
                    "date": post_date.strftime("%Y-%m-%d"),
                    "day_of_week": post_date.strftime("%A"),
                    "theme": theme,
                    "script_id": script["id"],
                    "hook": script["hook"],
                    "posting_time": script["best_posting_time"],
                    "hashtags": " ".join(script["hashtags"][:10]),  # First 10 hashtags
                    "target_audience": ", ".join(script["target_audience"])
                })
        
        # Write calendar to CSV
        with open(calendar_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=calendar_data[0].keys())
            writer.writeheader()
            writer.writerows(calendar_data)
        
        print(f"✅ Created 30-day posting calendar: {calendar_file}")
    
    def generate_hashtag_strategy(self) -> None:
        """Generate hashtag strategy JSON"""
        strategy_file = self.output_dir / "hashtag_strategy.json"
        
        strategy = {
            "book_title": self.book_dir.name.replace("_", " ").title(),
            "book_type": self._detect_book_type(),
            "primary_hashtags": self.hashtags["broad"],
            "niche_hashtags": self.hashtags["niche"],
            "audience_hashtags": self.hashtags["audience"],
            "tech_hashtags": self.hashtags["tech"],
            "optimal_combinations": [
                self._generate_hashtag_combination() for _ in range(5)
            ],
            "hashtag_performance_tracking": {
                "high_performing": [],
                "low_performing": [],
                "trending": [],
                "seasonal": []
            },
            "competitor_hashtags": [
                "#PuzzleTime", "#BrainTraining", "#MindGames", 
                "#PuzzleAddict", "#CrosswordFan", "#SudokuMaster"
            ]
        }
        
        with open(strategy_file, 'w') as f:
            json.dump(strategy, f, indent=2)
        
        print(f"✅ Generated hashtag strategy: {strategy_file}")
    
    def create_visual_content_prompts(self) -> None:
        """Generate prompts for visual content creation"""
        prompts_file = self.output_dir / "visual_content_prompts.json"
        
        book_title = self.book_dir.name.replace("_", " ").title()
        
        prompts = {
            "puzzle_demo_images": [
                f"Close-up shot of {book_title} puzzle page with pencil",
                f"Hand solving crossword clue in {book_title}",
                f"Before and after puzzle completion from {book_title}",
                "Timer countdown overlay on puzzle solving",
                "Magnifying glass over large print puzzle text"
            ],
            "behind_scenes_content": [
                "Screen recording of AI generating crossword grid",
                "Time-lapse of book layout creation process", 
                "Split screen: AI prompt → generated puzzle",
                "Dashboard showing book generation progress",
                "Final PDF export and preview"
            ],
            "pinterest_pins": [
                f"'{book_title}' book cover with '50+ Puzzles' overlay",
                "Large print crossword sample with 'Easy to Read' text",
                "Brain health benefits infographic with book promotion",
                "Gift idea graphic: 'Perfect for Puzzle Lovers'",
                "Before/after brain scan with puzzle solving benefits"
            ],
            "instagram_stories": [
                "Poll: 'Crosswords or Sudoku?' with book covers",
                "Quiz: 'Can you solve this clue?' with answer reveal",
                "Behind-the-scenes: 'How I make puzzle books'",
                "User testimonial with book recommendation",
                "Countdown: 'New puzzle book launching soon'"
            ]
        }
        
        with open(prompts_file, 'w') as f:
            json.dump(prompts, f, indent=2)
        
        print(f"✅ Created visual content prompts: {prompts_file}")
    
    def generate_all_content(self) -> None:
        """Generate all BookTok content for the book"""
        print(f"🚀 Generating BookTok content for: {self.book_dir.name}")
        
        # Generate TikTok scripts
        scripts = self.generate_tiktok_scripts()
        scripts_file = self.output_dir / "tiktok_scripts.json"
        with open(scripts_file, 'w') as f:
            json.dump(scripts, f, indent=2)
        print(f"✅ Generated {len(scripts)} TikTok scripts: {scripts_file}")
        
        # Create content calendar
        self.create_content_calendar(scripts)
        
        # Generate hashtag strategy
        self.generate_hashtag_strategy()
        
        # Create visual content prompts
        self.create_visual_content_prompts()
        
        # Generate summary report
        self.create_summary_report(scripts)
        
        print("\n🎉 BookTok content generation complete!")
        print(f"📁 All files saved to: {self.output_dir}")
    
    def create_summary_report(self, scripts: List[Dict]) -> None:
        """Create summary report of generated content"""
        report_file = self.output_dir / "booktok_content_summary.md"
        
        book_title = self.book_dir.name.replace("_", " ").title()
        
        report = f"""# BookTok Content Summary: {book_title}

## 📊 Content Overview
- **Total TikTok Scripts:** {len(scripts)}
- **Content Pillars:** {len(self.content_pillars)}
- **Hashtag Combinations:** 5 optimized sets
- **Posting Calendar:** 30 days scheduled
- **Visual Content Prompts:** 20+ ideas

## 🎯 Content Pillars
{chr(10).join([f"- **{pillar.title()}:** {desc}" for pillar, desc in self.content_pillars.items()])}

## 📅 Posting Schedule
- **Monday:** Behind-the-scenes AI magic
- **Tuesday:** Puzzle solving demos
- **Wednesday:** Brain health education
- **Thursday:** Puzzle challenges
- **Friday:** Behind-the-scenes content
- **Saturday:** Senior-friendly content
- **Sunday:** Brain health tips

## 🏷️ Top Hashtags
{chr(10).join([f"- {tag}" for tag in self.hashtags["broad"] + self.hashtags["niche"][:3]])}

## 📈 Success Metrics to Track
- Views, likes, shares, comments
- Click-through rate to Amazon
- Follower growth rate
- Hashtag performance
- Audience engagement rate

## 🚀 Next Steps
1. Review and customize scripts
2. Create visual content using prompts
3. Set up posting schedule
4. Monitor performance and optimize
5. Scale successful content types

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ Created summary report: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate BookTok content for puzzle books")
    parser.add_argument("book_directory", help="Path to book directory")
    parser.add_argument("--output-only", action="store_true", help="Only show output paths")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.book_directory):
        print(f"❌ Error: Book directory not found: {args.book_directory}")
        return 1
    
    generator = BookTokContentGenerator(args.book_directory)
    
    if args.output_only:
        print(f"Output directory: {generator.output_dir}")
        return 0
    
    try:
        generator.generate_all_content()
        return 0
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
