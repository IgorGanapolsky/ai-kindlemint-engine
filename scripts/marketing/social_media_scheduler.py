#!/usr/bin/env python3
"""
Social Media Scheduler - Automated BookTok Posting Pipeline
Integrates with existing AI infrastructure for consistent social media presence
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from typing import Dict, List, Any
import sys
import schedule
import time
from dataclasses import dataclass

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

@dataclass
class PostContent:
    """Social media post content structure"""
    platform: str
    content_type: str
    script: str
    hashtags: List[str]
    visual_prompt: str
    posting_time: str
    target_audience: List[str]
    book_title: str
    amazon_link: str

class SocialMediaScheduler:
    """Automated social media posting scheduler for BookTok strategy"""
    
    def __init__(self, content_directory: str = "data/social_content"):
        self.content_dir = Path(content_directory)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        
        # Scheduling files
        self.schedule_file = self.content_dir / "posting_schedule.json"
        self.posted_content_file = self.content_dir / "posted_content_log.json"
        self.queue_file = self.content_dir / "content_queue.json"
        
        # Daily content themes (aligned with BookTok strategy)
        self.daily_themes = {
            "monday": {
                "theme": "behind_scenes",
                "content_type": "AI Magic Monday",
                "description": "Behind-the-scenes AI book creation",
                "optimal_time": "14:00",  # 2 PM EST
                "hashtags": ["#AICreator", "#BehindTheScenes", "#BookTok", "#TechTok"]
            },
            "tuesday": {
                "theme": "puzzle_demo", 
                "content_type": "Puzzle Challenge Tuesday",
                "description": "Interactive puzzle solving demos",
                "optimal_time": "19:00",  # 7 PM EST
                "hashtags": ["#PuzzleChallenge", "#BrainGames", "#CrosswordPuzzles", "#BookTok"]
            },
            "wednesday": {
                "theme": "brain_health",
                "content_type": "Wellness Wednesday", 
                "description": "Brain health education and benefits",
                "optimal_time": "10:00",  # 10 AM EST
                "hashtags": ["#BrainHealth", "#WellnessWednesday", "#PuzzleBooks", "#SeniorHealth"]
            },
            "thursday": {
                "theme": "puzzle_demo",
                "content_type": "Throwback Thursday",
                "description": "Customer testimonials and reviews",
                "optimal_time": "16:00",  # 4 PM EST
                "hashtags": ["#CustomerLove", "#PuzzleReviews", "#BookTok", "#TestimonialThursday"]
            },
            "friday": {
                "theme": "behind_scenes",
                "content_type": "Feature Friday",
                "description": "Weekend puzzle book recommendations",
                "optimal_time": "17:00",  # 5 PM EST
                "hashtags": ["#WeekendReads", "#PuzzleBooks", "#BookTok", "#FeatureFriday"]
            },
            "saturday": {
                "theme": "senior_friendly",
                "content_type": "Senior Saturday",
                "description": "Senior-friendly content and gift ideas",
                "optimal_time": "15:00",  # 3 PM EST
                "hashtags": ["#SeniorFriendly", "#LargePrint", "#GiftIdeas", "#PuzzleBooks"]
            },
            "sunday": {
                "theme": "brain_health",
                "content_type": "Self-Care Sunday",
                "description": "Community engagement and Q&A",
                "optimal_time": "11:00",  # 11 AM EST
                "hashtags": ["#SelfCareSunday", "#BrainHealth", "#CommunityQ&A", "#PuzzleLovers"]
            }
        }
        
        # Platform-specific settings
        self.platform_settings = {
            "tiktok": {
                "max_hashtags": 30,
                "optimal_length": 60,  # seconds
                "best_times": ["14:00", "19:00", "21:00"],
                "content_formats": ["video", "carousel"]
            },
            "pinterest": {
                "max_hashtags": 20,
                "optimal_dimensions": "1000x1500",  # pixels
                "best_times": ["20:00", "21:00", "22:00"],
                "content_formats": ["pin", "story_pin"]
            },
            "instagram": {
                "max_hashtags": 30,
                "optimal_length": 30,  # seconds for reels
                "best_times": ["11:00", "14:00", "17:00"],
                "content_formats": ["reel", "story", "post"]
            }
        }
    
    def create_weekly_schedule(self, books_data: List[Dict[str, Any]]) -> None:
        """Create weekly posting schedule from book content"""
        schedule_data = []
        start_date = datetime.now()
        
        for week in range(4):  # 4 weeks ahead
            for day_offset in range(7):  # 7 days per week
                post_date = start_date + timedelta(weeks=week, days=day_offset)
                day_name = post_date.strftime("%A").lower()
                
                if day_name in self.daily_themes:
                    theme_config = self.daily_themes[day_name]
                    
                    # Select book for this post (rotate through available books)
                    book_index = (week * 7 + day_offset) % len(books_data)
                    selected_book = books_data[book_index]
                    
                    # Create post content
                    post_content = self._create_post_content(
                        theme_config, selected_book, post_date
                    )
                    
                    schedule_entry = {
                        "id": f"post_{post_date.strftime('%Y%m%d')}_{day_name}",
                        "date": post_date.strftime("%Y-%m-%d"),
                        "day": day_name,
                        "time": theme_config["optimal_time"],
                        "theme": theme_config["theme"],
                        "content_type": theme_config["content_type"],
                        "book_title": selected_book["title"],
                        "book_directory": selected_book["directory"],
                        "platforms": ["tiktok", "pinterest", "instagram"],
                        "content": post_content,
                        "status": "scheduled",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    schedule_data.append(schedule_entry)
        
        # Save schedule
        with open(self.schedule_file, 'w') as f:
            json.dump(schedule_data, f, indent=2)
        
        print(f"✅ Created 4-week posting schedule with {len(schedule_data)} posts")
        print(f"📅 Schedule saved to: {self.schedule_file}")
    
    def _create_post_content(self, theme_config: Dict, book_data: Dict, post_date: datetime) -> Dict[str, Any]:
        """Create platform-specific post content"""
        book_title = book_data["title"]
        
        # Content templates based on theme
        content_templates = {
            "behind_scenes": {
                "tiktok_script": f"POV: Creating '{book_title}' in 30 minutes with AI ✨ Watch the magic happen! From blank page to published puzzle book. What should I create next? 🤖📚",
                "pinterest_description": f"Behind the scenes: How I create puzzle books like '{book_title}' using AI automation. Perfect for puzzle lovers and brain health! 🧩",
                "instagram_caption": f"The AI magic behind '{book_title}' 🤖✨ 30 minutes from idea to finished puzzle book! What's your favorite puzzle type? 🧩"
            },
            "puzzle_demo": {
                "tiktok_script": f"Can you solve this crossword from '{book_title}' in 10 seconds? ⏰ Large print, senior-friendly puzzles that keep your brain sharp! 🧠",
                "pinterest_description": f"Brain-boosting crossword puzzle from '{book_title}' - Large print design perfect for seniors and puzzle enthusiasts! 🧩",
                "instagram_caption": f"Quick puzzle challenge from '{book_title}' 🧩⏰ Tag someone who loves crosswords! Link in bio for the full book 📚"
            },
            "brain_health": {
                "tiktok_script": f"Your brain on puzzles vs scrolling 🧠 Books like '{book_title}' improve memory, focus, and cognitive health. Choose puzzles over endless scrolling! 📱➡️📚",
                "pinterest_description": f"Brain health benefits of puzzle books like '{book_title}' - Improve memory, reduce cognitive decline, boost mental wellness! 🧠",
                "instagram_caption": f"Why I choose puzzles over scrolling 🧠✨ '{book_title}' and books like it keep your mind sharp and healthy! What's your brain exercise? 🧩"
            },
            "senior_friendly": {
                "tiktok_script": f"The perfect gift for puzzle-loving grandparents 👵👴 '{book_title}' features large print, quality paper, and engaging themes! 🎁",
                "pinterest_description": f"Perfect gift for seniors: '{book_title}' with large print puzzles designed for comfort and enjoyment! 🎁👵",
                "instagram_caption": f"Gift idea alert! 🎁 '{book_title}' is perfect for grandparents who love puzzles. Large print = happy eyes! 👀✨"
            }
        }
        
        theme = theme_config["theme"]
        templates = content_templates.get(theme, content_templates["puzzle_demo"])
        
        return {
            "tiktok": {
                "script": templates["tiktok_script"],
                "hashtags": theme_config["hashtags"] + ["#PuzzleBooks", "#LargePrint"],
                "duration": "60s",
                "visual_cues": self._get_visual_cues(theme, book_title)
            },
            "pinterest": {
                "description": templates["pinterest_description"],
                "hashtags": theme_config["hashtags"] + ["#PuzzleBooks", "#BrainHealth", "#Seniors"],
                "pin_title": f"{book_title} - {theme_config['content_type']}",
                "board": "Puzzle Books & Brain Health"
            },
            "instagram": {
                "caption": templates["instagram_caption"],
                "hashtags": theme_config["hashtags"] + ["#PuzzleBooks", "#BrainGames"],
                "story_text": f"New puzzle book: {book_title} 🧩",
                "format": "reel"
            }
        }
    
    def _get_visual_cues(self, theme: str, book_title: str) -> List[str]:
        """Get visual cues for video content creation"""
        visual_cues_map = {
            "behind_scenes": [
                "Screen recording of AI generation process",
                "Time-lapse effect showing book creation",
                "Split screen: prompt input → generated content",
                "Final book reveal with page flip"
            ],
            "puzzle_demo": [
                f"Close-up of puzzle page from {book_title}",
                "Hand solving crossword with pencil",
                "Timer countdown overlay",
                "Answer reveal with checkmark animation"
            ],
            "brain_health": [
                "Brain animation or infographic",
                "Before/after comparison graphics",
                "Book showcase with health benefits text",
                "Happy senior solving puzzles"
            ],
            "senior_friendly": [
                f"Book flip-through showing {book_title}",
                "Large print close-up demonstration",
                "Gift wrapping or presentation scene",
                "Testimonial or review highlight"
            ]
        }
        
        return visual_cues_map.get(theme, ["Book showcase", "Puzzle demonstration"])
    
    def generate_content_queue(self, days_ahead: int = 7) -> None:
        """Generate content queue for upcoming posts"""
        if not self.schedule_file.exists():
            print("❌ No schedule file found. Create schedule first.")
            return
        
        with open(self.schedule_file, 'r') as f:
            schedule_data = json.load(f)
        
        # Filter upcoming posts
        today = datetime.now()
        upcoming_posts = []
        
        for post in schedule_data:
            post_date = datetime.strptime(post["date"], "%Y-%m-%d")
            if today <= post_date <= today + timedelta(days=days_ahead):
                if post["status"] == "scheduled":
                    upcoming_posts.append(post)
        
        # Sort by date
        upcoming_posts.sort(key=lambda x: x["date"])
        
        # Save to queue
        with open(self.queue_file, 'w') as f:
            json.dump(upcoming_posts, f, indent=2)
        
        print(f"✅ Generated content queue with {len(upcoming_posts)} posts for next {days_ahead} days")
        print(f"📋 Queue saved to: {self.queue_file}")
    
    def mark_as_posted(self, post_id: str, platform: str, post_url: str = "") -> None:
        """Mark content as posted and log performance tracking info"""
        # Load posted content log
        posted_log = []
        if self.posted_content_file.exists():
            with open(self.posted_content_file, 'r') as f:
                posted_log = json.load(f)
        
        # Add new posted content
        posted_entry = {
            "post_id": post_id,
            "platform": platform,
            "posted_at": datetime.now().isoformat(),
            "post_url": post_url,
            "status": "posted",
            "performance_tracking": {
                "views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "clicks": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        posted_log.append(posted_entry)
        
        # Save updated log
        with open(self.posted_content_file, 'w') as f:
            json.dump(posted_log, f, indent=2)
        
        print(f"✅ Marked {post_id} as posted on {platform}")
    
    def get_today_posts(self) -> List[Dict[str, Any]]:
        """Get posts scheduled for today"""
        if not self.schedule_file.exists():
            return []
        
        with open(self.schedule_file, 'r') as f:
            schedule_data = json.load(f)
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_posts = [post for post in schedule_data if post["date"] == today and post["status"] == "scheduled"]
        
        return today_posts
    
    def setup_automated_posting(self) -> None:
        """Setup automated posting schedule (requires manual platform integration)"""
        print("🤖 Setting up automated posting schedule...")
        
        # Schedule daily content check
        schedule.every().day.at("09:00").do(self._daily_content_check)
        
        # Schedule posting times for each theme
        for day, theme_config in self.daily_themes.items():
            posting_time = theme_config["optimal_time"]
            schedule.every().day.at(posting_time).do(self._check_and_post, day)
        
        print("✅ Automated posting schedule configured")
        print("⚠️  Note: Platform API integration required for full automation")
    
    def _daily_content_check(self) -> None:
        """Daily check for content preparation"""
        today_posts = self.get_today_posts()
        
        if today_posts:
            print(f"📅 {len(today_posts)} posts scheduled for today")
            for post in today_posts:
                print(f"  - {post['time']}: {post['content_type']} ({post['book_title']})")
        else:
            print("📅 No posts scheduled for today")
    
    def _check_and_post(self, day: str) -> None:
        """Check and post content for specific day"""
        today_posts = self.get_today_posts()
        current_time = datetime.now().strftime("%H:%M")
        
        for post in today_posts:
            if post["day"] == day and post["time"] <= current_time:
                print(f"🚀 Ready to post: {post['content_type']}")
                # Here you would integrate with platform APIs
                # For now, just log the action
                self._simulate_posting(post)
    
    def _simulate_posting(self, post: Dict[str, Any]) -> None:
        """Simulate posting (replace with actual platform API calls)"""
        print(f"📱 Simulating post to platforms: {', '.join(post['platforms'])}")
        print(f"📝 Content: {post['content']['tiktok']['script'][:50]}...")
        print(f"🏷️  Hashtags: {' '.join(post['content']['tiktok']['hashtags'][:5])}")
        
        # Mark as posted (simulation)
        for platform in post["platforms"]:
            self.mark_as_posted(post["id"], platform, f"https://{platform}.com/simulated_post")
    
    def generate_posting_report(self) -> None:
        """Generate posting performance report"""
        if not self.posted_content_file.exists():
            print("❌ No posted content data found")
            return
        
        with open(self.posted_content_file, 'r') as f:
            posted_content = json.load(f)
        
        # Calculate statistics
        total_posts = len(posted_content)
        platforms = {}
        
        for post in posted_content:
            platform = post["platform"]
            if platform not in platforms:
                platforms[platform] = 0
            platforms[platform] += 1
        
        # Generate report
        report = f"""# Social Media Posting Report
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Posting Summary
- **Total Posts:** {total_posts}
- **Platforms:** {', '.join(platforms.keys())}

## 📱 Platform Breakdown
"""
        
        for platform, count in platforms.items():
            report += f"- **{platform.title()}:** {count} posts\n"
        
        report += """
## 📈 Recent Activity
"""
        
        # Show last 5 posts
        recent_posts = sorted(posted_content, key=lambda x: x["posted_at"], reverse=True)[:5]
        for post in recent_posts:
            posted_date = datetime.fromisoformat(post["posted_at"]).strftime("%Y-%m-%d %H:%M")
            report += f"- {posted_date}: {post['platform']} - {post['post_id']}\n"
        
        # Save report
        report_file = self.content_dir / "posting_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ Generated posting report: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Social Media Scheduler for BookTok Strategy")
    parser.add_argument("--content-dir", default="data/social_content", help="Content directory")
    parser.add_argument("--create-schedule", help="Create schedule from books JSON file")
    parser.add_argument("--generate-queue", type=int, default=7, help="Generate content queue (days ahead)")
    parser.add_argument("--today-posts", action="store_true", help="Show today's posts")
    parser.add_argument("--run-scheduler", action="store_true", help="Run automated scheduler")
    parser.add_argument("--posting-report", action="store_true", help="Generate posting report")
    
    args = parser.parse_args()
    
    scheduler = SocialMediaScheduler(args.content_dir)
    
    if args.create_schedule:
        if os.path.exists(args.create_schedule):
            with open(args.create_schedule, 'r') as f:
                books_data = json.load(f)
            scheduler.create_weekly_schedule(books_data)
        else:
            print(f"❌ Books file not found: {args.create_schedule}")
    
    if args.generate_queue:
        scheduler.generate_content_queue(args.generate_queue)
    
    if args.today_posts:
        today_posts = scheduler.get_today_posts()
        if today_posts:
            print(f"📅 Today's posts ({len(today_posts)}):")
            for post in today_posts:
                print(f"  {post['time']}: {post['content_type']} - {post['book_title']}")
        else:
            print("📅 No posts scheduled for today")
    
    if args.posting_report:
        scheduler.generate_posting_report()
    
    if args.run_scheduler:
        print("🤖 Starting automated scheduler...")
        scheduler.setup_automated_posting()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n⏹️  Scheduler stopped")
    
    if not any([args.create_schedule, args.generate_queue, args.today_posts, args.run_scheduler, args.posting_report]):
        print("Social Media Scheduler initialized.")
        print(f"Content directory: {scheduler.content_dir}")
        print("Use --help for available commands.")

if __name__ == "__main__":
    main()
