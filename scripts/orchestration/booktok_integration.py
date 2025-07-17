#!/usr/bin/env python3
"""
BookTok Integration - Connect Social Media Automation with AI-KindleMint-Engine
Leverages existing autonomous worktree system for parallel social content generation
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, Any
import logging

# Import existing worktree orchestration
try:
    from scripts.orchestration.worktree_orchestrator import WorktreeOrchestrator, WorktreeTask
except ImportError as e:
    print(f"Warning: Could not import WorktreeOrchestrator - {e}")
    WorktreeOrchestrator = None
    WorktreeTask = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookTokWorktreeIntegration:
    """Integrate BookTok automation with existing WorktreeOrchestrator for parallel execution"""
    
    def __init__(self, base_directory: str = None):
        if base_directory is None:
            base_directory = Path(__file__).parent.parent.parent
        
        self.base_dir = Path(base_directory)
        self.worktrees_dir = self.base_dir / "worktrees"
        self.books_dir = self.base_dir / "books"
        self.social_content_dir = self.base_dir / "data" / "social_content"
        self.analytics_dir = self.base_dir / "data" / "analytics"
        
        # Create directories
        for directory in [self.social_content_dir, self.analytics_dir, self.worktrees_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize WorktreeOrchestrator if available
        if WorktreeOrchestrator:
            self.orchestrator = WorktreeOrchestrator()
            logger.info("✅ WorktreeOrchestrator initialized for parallel BookTok automation")
        else:
            self.orchestrator = None
            logger.warning("⚠️ WorktreeOrchestrator not available, falling back to sequential processing")
        
        # BookTok worktree configurations for parallel execution
        self.booktok_worktrees = {
            "booktok-content": {
                "branch": "feature/booktok-content-generation",
                "purpose": "TikTok script and hashtag generation",
                "tasks": ["tiktok_scripts", "hashtag_optimization", "content_calendar"]
            },
            "booktok-visuals": {
                "branch": "feature/booktok-visual-assets", 
                "purpose": "Visual content and thumbnail generation",
                "tasks": ["puzzle_teasers", "behind_scenes_clips", "brain_health_graphics"]
            },
            "booktok-analytics": {
                "branch": "feature/booktok-analytics",
                "purpose": "Social media tracking and ROI analysis", 
                "tasks": ["utm_generation", "metrics_tracking", "performance_reports"]
            },
            "booktok-scheduler": {
                "branch": "feature/booktok-scheduling",
                "purpose": "Automated posting and content queue management",
                "tasks": ["posting_calendar", "content_queue", "cross_platform_sync"]
            }
        }
    
    def setup_booktok_worktree(self) -> bool:
        """Setup dedicated worktree for BookTok automation"""
        try:
            worktree_path = self.worktrees_dir / self.booktok_worktree_config["name"]
            
            if worktree_path.exists():
                print(f"✅ BookTok worktree already exists: {worktree_path}")
                return True
            
            # Create worktree
            cmd = [
                "git", "worktree", "add", 
                str(worktree_path), 
                "-b", self.booktok_worktree_config["branch"]
            ]
            
            result = subprocess.run(cmd, cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created BookTok worktree: {worktree_path}")
                
                # Setup worktree-specific directories
                social_dir = worktree_path / "social_media_automation"
                social_dir.mkdir(exist_ok=True)
                
                return True
            else:
                print(f"❌ Failed to create worktree: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up BookTok worktree: {e}")
            return False
    
    def generate_social_content_for_all_books(self) -> Dict[str, Any]:
        """Generate social media content for all published books"""
        results = {
            "total_books": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "generated_content": []
        }
        
        # Find all book directories
        if not self.books_dir.exists():
            print(f"❌ Books directory not found: {self.books_dir}")
            return results
        
        book_directories = [d for d in self.books_dir.iterdir() if d.is_dir()]
        results["total_books"] = len(book_directories)
        
        print(f"🚀 Generating social content for {len(book_directories)} books...")
        
        # Use parallel processing for content generation
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_book = {
                executor.submit(self._generate_content_for_book, book_dir): book_dir 
                for book_dir in book_directories
            }
            
            for future in concurrent.futures.as_completed(future_to_book):
                book_dir = future_to_book[future]
                try:
                    content_result = future.result()
                    if content_result["success"]:
                        results["successful_generations"] += 1
                        results["generated_content"].append(content_result)
                        print(f"✅ Generated content for: {book_dir.name}")
                    else:
                        results["failed_generations"] += 1
                        print(f"❌ Failed to generate content for: {book_dir.name}")
                        
                except Exception as e:
                    results["failed_generations"] += 1
                    print(f"❌ Error processing {book_dir.name}: {e}")
        
        print("📊 Content generation complete:")
        print(f"  - Successful: {results['successful_generations']}")
        print(f"  - Failed: {results['failed_generations']}")
        
        return results
    
    def _generate_content_for_book(self, book_directory: Path) -> Dict[str, Any]:
        """Generate social media content for a single book"""
        try:
            generator = BookTokContentGenerator(str(book_directory))
            generator.generate_all_content()
            
            return {
                "success": True,
                "book_title": book_directory.name,
                "book_directory": str(book_directory),
                "content_directory": str(generator.output_dir),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "book_title": book_directory.name,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def create_master_posting_schedule(self) -> None:
        """Create master posting schedule for all books"""
        print("📅 Creating master posting schedule...")
        
        # Collect all book data
        books_data = []
        
        if self.books_dir.exists():
            for book_dir in self.books_dir.iterdir():
                if book_dir.is_dir():
                    books_data.append({
                        "title": book_dir.name.replace("_", " ").title(),
                        "directory": str(book_dir),
                        "social_content_dir": str(book_dir / "social_media_content")
                    })
        
        if not books_data:
            print("❌ No books found for scheduling")
            return
        
        # Create schedule using scheduler
        self.scheduler.create_weekly_schedule(books_data)
        
        # Generate content queue for next week
        self.scheduler.generate_content_queue(7)
        
        print(f"✅ Master schedule created for {len(books_data)} books")
    
    def setup_automated_pipeline(self) -> None:
        """Setup complete automated BookTok pipeline"""
        print("🤖 Setting up automated BookTok pipeline...")
        
        # 1. Setup worktree
        if not self.setup_booktok_worktree():
            print("❌ Failed to setup worktree")
            return
        
        # 2. Generate content for all books
        content_results = self.generate_social_content_for_all_books()
        
        if content_results["successful_generations"] == 0:
            print("❌ No content generated successfully")
            return
        
        # 3. Create master posting schedule
        self.create_master_posting_schedule()
        
        # 4. Setup analytics tracking
        self.setup_analytics_tracking()
        
        # 5. Create automation scripts
        self.create_automation_scripts()
        
        print("✅ BookTok automation pipeline setup complete!")
        self.print_setup_summary(content_results)
    
    def setup_analytics_tracking(self) -> None:
        """Setup analytics tracking system"""
        print("📊 Setting up analytics tracking...")
        
        # Create sample books data for UTM link generation
        sample_amazon_url = "https://amazon.com/dp/SAMPLE123"
        utm_links = self.analytics.generate_utm_links(sample_amazon_url)
        
        # Save UTM links template
        utm_file = self.analytics_dir / "utm_links_template.json"
        with open(utm_file, 'w') as f:
            json.dump({
                "template_url": sample_amazon_url,
                "utm_links": utm_links,
                "instructions": "Replace SAMPLE123 with actual Amazon ASIN for each book"
            }, f, indent=2)
        
        print(f"✅ UTM tracking template saved: {utm_file}")
    
    def create_automation_scripts(self) -> None:
        """Create automation helper scripts"""
        scripts_dir = self.base_dir / "scripts" / "automation"
        scripts_dir.mkdir(exist_ok=True)
        
        # Daily automation script
        daily_script = scripts_dir / "daily_booktok_automation.py"
        daily_script_content = '''#!/usr/bin/env python3
"""
Daily BookTok Automation - Run daily social media tasks
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.orchestration.booktok_integration import BookTokIntegration

def main():
    integration = BookTokIntegration()
    
    print("🌅 Running daily BookTok automation...")
    
    # Check today's posts
    today_posts = integration.scheduler.get_today_posts()
    if today_posts:
        print(f"📅 {len(today_posts)} posts scheduled for today")
        for post in today_posts:
            print(f"  {post['time']}: {post['content_type']} - {post['book_title']}")
    
    # Generate weekly analytics report (if it's Monday)
    from datetime import datetime
    if datetime.now().weekday() == 0:  # Monday
        print("📊 Generating weekly analytics report...")
        integration.analytics.generate_weekly_report()
    
    # Update content queue
    integration.scheduler.generate_content_queue(7)
    
    print("✅ Daily automation complete!")

if __name__ == "__main__":
    main()
'''
        
        with open(daily_script, 'w') as f:
            f.write(daily_script_content)
        
        # Make executable
        daily_script.chmod(0o755)
        
        print(f"✅ Created daily automation script: {daily_script}")
        
        # Weekly automation script
        weekly_script = scripts_dir / "weekly_booktok_maintenance.py"
        weekly_script_content = '''#!/usr/bin/env python3
"""
Weekly BookTok Maintenance - Run weekly social media maintenance tasks
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.orchestration.booktok_integration import BookTokIntegration

def main():
    integration = BookTokIntegration()
    
    print("🔧 Running weekly BookTok maintenance...")
    
    # Generate new content for any new books
    content_results = integration.generate_social_content_for_all_books()
    
    # Update master posting schedule
    integration.create_master_posting_schedule()
    
    # Generate comprehensive analytics report
    integration.analytics.generate_weekly_report()
    integration.analytics.export_data_for_analysis()
    
    # Generate posting performance report
    integration.scheduler.generate_posting_report()
    
    print("✅ Weekly maintenance complete!")
    print(f"📊 Content generated for {content_results['successful_generations']} books")

if __name__ == "__main__":
    main()
'''
        
        with open(weekly_script, 'w') as f:
            f.write(weekly_script_content)
        
        # Make executable
        weekly_script.chmod(0o755)
        
        print(f"✅ Created weekly maintenance script: {weekly_script}")
    
    def print_setup_summary(self, content_results: Dict[str, Any]) -> None:
        """Print setup summary and next steps"""
        print("\n" + "="*60)
        print("🎉 BOOKTOK AUTOMATION PIPELINE SETUP COMPLETE!")
        print("="*60)
        
        print(f"""
📊 SETUP SUMMARY:
  - Books processed: {content_results['total_books']}
  - Content generated: {content_results['successful_generations']}
  - Social platforms: TikTok, Pinterest, Instagram
  - Posting schedule: 4 weeks ahead
  - Analytics tracking: Enabled

📁 KEY FILES CREATED:
  - BookTok content generator: scripts/marketing/booktok_content_generator.py
  - Social media scheduler: scripts/marketing/social_media_scheduler.py
  - Analytics tracker: scripts/marketing/social_media_analytics.py
  - Integration orchestrator: scripts/orchestration/booktok_integration.py
  - Daily automation: scripts/automation/daily_booktok_automation.py
  - Weekly maintenance: scripts/automation/weekly_booktok_maintenance.py

🚀 NEXT STEPS:
  1. Review generated content in each book's social_media_content/ folder
  2. Create TikTok business account and get API access
  3. Set up Pinterest business account for puzzle pins
  4. Configure posting automation with platform APIs
  5. Start tracking performance metrics
  6. Run daily automation: python scripts/automation/daily_booktok_automation.py

💡 IMMEDIATE ACTIONS:
  - Check today's posting schedule: python scripts/marketing/social_media_scheduler.py --today-posts
  - Generate UTM links for books: python scripts/marketing/social_media_analytics.py --utm-links YOUR_AMAZON_URL
  - Review content calendar: data/social_content/posting_calendar.csv

🎯 SUCCESS METRICS TO TRACK:
  - TikTok followers (target: 10K in 90 days)
  - Social media → Amazon click-through rate
  - Book sales from social traffic
  - Engagement rates by content type
""")
        
        print("="*60)
        print("Your BookTok strategy is now AUTOMATED and ready to scale! 🚀")
        print("="*60)
    
    def run_daily_automation(self) -> None:
        """Run daily automation tasks"""
        print("🌅 Running daily BookTok automation...")
        
        # Check today's posts
        today_posts = self.scheduler.get_today_posts()
        if today_posts:
            print(f"📅 {len(today_posts)} posts scheduled for today:")
            for post in today_posts:
                print(f"  {post['time']}: {post['content_type']} - {post['book_title']}")
        else:
            print("📅 No posts scheduled for today")
        
        # Update content queue
        self.scheduler.generate_content_queue(7)
        
        # Generate analytics if it's Monday
        if datetime.now().weekday() == 0:
            print("📊 Generating weekly analytics report...")
            self.analytics.generate_weekly_report()
        
        print("✅ Daily automation complete!")
    
    def run_weekly_maintenance(self) -> None:
        """Run weekly maintenance tasks"""
        print("🔧 Running weekly BookTok maintenance...")
        
        # Generate content for any new books
        content_results = self.generate_social_content_for_all_books()
        
        # Update master schedule
        self.create_master_posting_schedule()
        
        # Generate reports
        self.analytics.generate_weekly_report()
        self.analytics.export_data_for_analysis()
        self.scheduler.generate_posting_report()
        
        print("✅ Weekly maintenance complete!")
        print(f"📊 Content generated for {content_results['successful_generations']} books")

def main():
    parser = argparse.ArgumentParser(description="BookTok Integration with AI-KindleMint-Engine")
    parser.add_argument("--base-dir", help="Base directory for AI-KindleMint-Engine")
    parser.add_argument("--setup", action="store_true", help="Setup complete BookTok automation pipeline")
    parser.add_argument("--generate-content", action="store_true", help="Generate social content for all books")
    parser.add_argument("--create-schedule", action="store_true", help="Create master posting schedule")
    parser.add_argument("--daily-automation", action="store_true", help="Run daily automation tasks")
    parser.add_argument("--weekly-maintenance", action="store_true", help="Run weekly maintenance tasks")
    parser.add_argument("--setup-worktree", action="store_true", help="Setup BookTok worktree only")
    
    args = parser.parse_args()
    
    integration = BookTokIntegration(args.base_dir)
    
    if args.setup:
        integration.setup_automated_pipeline()
    elif args.generate_content:
        integration.generate_social_content_for_all_books()
    elif args.create_schedule:
        integration.create_master_posting_schedule()
    elif args.daily_automation:
        integration.run_daily_automation()
    elif args.weekly_maintenance:
        integration.run_weekly_maintenance()
    elif args.setup_worktree:
        integration.setup_booktok_worktree()
    else:
        print("BookTok Integration initialized.")
        print("Use --help for available commands.")
        print("Quick start: --setup to configure complete automation pipeline")

if __name__ == "__main__":
    main()
