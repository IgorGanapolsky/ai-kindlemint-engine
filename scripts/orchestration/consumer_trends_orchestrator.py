#!/usr/bin/env python3
"""
Consumer Trends Orchestrator

Integrates Consumer Trends Integration with existing content generation workflows,
automatically triggering book generation based on trend insights.
"""

import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from kindlemint.intelligence.predictive_trend_analyzer import PredictiveTrendAnalyzer
from kindlemint.marketing.personalization_engine import PersonalizationEngine
from kindlemint.utils.data_manager import DataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsumerTrendsOrchestrator:
    """Orchestrates Consumer Trends Integration with content generation."""
    
    def __init__(self):
        self.config_path = Path("config/consumer_trends_production.json")
        self.workflow_config_path = Path("config/workflow_config.json")
        self.trend_analyzer = None
        self.personalization_engine = None
        self.data_manager = None
        
        # Load configurations
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Load all necessary configurations."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.trends_config = json.load(f)
        else:
            logger.error(f"Consumer trends config not found: {self.config_path}")
            sys.exit(1)
        
        if self.workflow_config_path.exists():
            with open(self.workflow_config_path, 'r') as f:
                self.workflow_config = json.load(f)
        else:
            logger.warning(f"Workflow config not found: {self.workflow_config_path}")
            self.workflow_config = {}
    
    async def initialize_services(self) -> None:
        """Initialize Consumer Trends services."""
        logger.info("🚀 Initializing Consumer Trends Orchestrator...")
        
        # Initialize data manager
        self.data_manager = DataManager(
            storage_type=self.trends_config["storage"]["type"],
            bucket_name=self.trends_config["storage"]["bucket"],
            region=self.trends_config["storage"]["region"]
        )
        
        # Initialize trend analyzer
        self.trend_analyzer = PredictiveTrendAnalyzer(
            data_manager=self.data_manager,
            config=self.trends_config["trend_analysis"]
        )
        
        # Initialize personalization engine
        self.personalization_engine = PersonalizationEngine(
            data_manager=self.data_manager,
            config=self.trends_config["personalization"]
        )
        
        logger.info("✅ Consumer Trends Orchestrator initialized")
    
    async def analyze_trends_for_content_generation(self) -> List[Dict]:
        """Analyze trends specifically for content generation opportunities."""
        logger.info("📊 Analyzing trends for content generation...")
        
        try:
            # Get all trends
            all_trends = await self.trend_analyzer.analyze_all_trends()
            
            # Filter trends suitable for book generation
            book_trends = []
            for trend in all_trends:
                if self.is_trend_suitable_for_books(trend):
                    book_trends.append(trend)
            
            # Sort by priority and market potential
            book_trends.sort(key=lambda x: x.get("priority", 0) * x.get("market_potential", 0), reverse=True)
            
            logger.info(f"✅ Found {len(book_trends)} trends suitable for book generation")
            return book_trends
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {e}")
            return []
    
    def is_trend_suitable_for_books(self, trend: Dict) -> bool:
        """Determine if a trend is suitable for book generation."""
        # Check if trend has sufficient data
        if trend.get("data_points", 0) < 10:
            return False
        
        # Check if trend is in relevant categories
        relevant_categories = [
            "puzzles", "crosswords", "sudoku", "wordsearch", "activity books",
            "children's books", "educational", "kindle", "amazon", "books"
        ]
        
        trend_name = trend.get("name", "").lower()
        trend_category = trend.get("category", "").lower()
        
        for category in relevant_categories:
            if category in trend_name or category in trend_category:
                return True
        
        return False
    
    async def generate_content_briefs(self, trends: List[Dict]) -> List[Dict]:
        """Generate content briefs based on trends."""
        logger.info("📝 Generating content briefs...")
        
        content_briefs = []
        for trend in trends[:5]:  # Top 5 trends
            brief = await self.create_content_brief(trend)
            if brief:
                content_briefs.append(brief)
        
        logger.info(f"✅ Generated {len(content_briefs)} content briefs")
        return content_briefs
    
    async def create_content_brief(self, trend: Dict) -> Optional[Dict]:
        """Create a detailed content brief for a trend."""
        try:
            # Get personalization data
            user_segments = await self.personalization_engine.generate_user_segments()
            
            # Create content brief
            brief = {
                "trend_id": trend.get("id"),
                "trend_name": trend.get("name"),
                "book_title": self.generate_book_title(trend),
                "book_type": self.determine_book_type(trend),
                "target_audience": self.determine_target_audience(trend, user_segments),
                "content_outline": await self.generate_content_outline(trend),
                "marketing_angles": self.generate_marketing_angles(trend),
                "priority": trend.get("priority", 0),
                "estimated_demand": trend.get("market_potential", 0),
                "competition_level": trend.get("competition", "medium"),
                "generated_at": datetime.now().isoformat()
            }
            
            return brief
            
        except Exception as e:
            logger.error(f"❌ Failed to create content brief for {trend.get('name')}: {e}")
            return None
    
    def generate_book_title(self, trend: Dict) -> str:
        """Generate a compelling book title based on the trend."""
        trend_name = trend.get("name", "")
        trend.get("category", "")
        
        # Template-based title generation
        templates = [
            f"The Ultimate {trend_name} Guide",
            f"{trend_name} Mastery: Complete Collection",
            f"Fun with {trend_name}: Activity Book",
            f"{trend_name} for Everyone: Beginner to Expert",
            f"The {trend_name} Challenge: 100+ Activities"
        ]
        
        # Select template based on trend characteristics
        if "puzzle" in trend_name.lower() or "game" in trend_name.lower():
            return templates[2]  # Activity book template
        elif "guide" in trend_name.lower() or "how" in trend_name.lower():
            return templates[0]  # Guide template
        else:
            return templates[1]  # Mastery template
    
    def determine_book_type(self, trend: Dict) -> str:
        """Determine the best book type for a trend."""
        trend_name = trend.get("name", "").lower()
        
        if any(word in trend_name for word in ["puzzle", "crossword", "sudoku", "wordsearch"]):
            return "puzzle_book"
        elif any(word in trend_name for word in ["activity", "craft", "coloring"]):
            return "activity_book"
        elif any(word in trend_name for word in ["guide", "how", "tutorial"]):
            return "educational_book"
        else:
            return "general_book"
    
    def determine_target_audience(self, trend: Dict, user_segments: List[Dict]) -> Dict:
        """Determine target audience for the book."""
        # Analyze trend characteristics to determine audience
        trend_name = trend.get("name", "").lower()
        
        if any(word in trend_name for word in ["kids", "children", "toddler"]):
            return {"age_group": "children", "skill_level": "beginner"}
        elif any(word in trend_name for word in ["senior", "elderly", "large print"]):
            return {"age_group": "seniors", "skill_level": "beginner"}
        elif any(word in trend_name for word in ["expert", "advanced", "master"]):
            return {"age_group": "adults", "skill_level": "advanced"}
        else:
            return {"age_group": "adults", "skill_level": "intermediate"}
    
    async def generate_content_outline(self, trend: Dict) -> List[Dict]:
        """Generate a content outline for the book."""
        book_type = self.determine_book_type(trend)
        
        if book_type == "puzzle_book":
            return [
                {"section": "Introduction", "pages": 2, "content": "Welcome and instructions"},
                {"section": "Easy Puzzles", "pages": 20, "content": "Beginner-level puzzles"},
                {"section": "Medium Puzzles", "pages": 30, "content": "Intermediate-level puzzles"},
                {"section": "Hard Puzzles", "pages": 20, "content": "Advanced-level puzzles"},
                {"section": "Solutions", "pages": 15, "content": "Answer key"}
            ]
        elif book_type == "activity_book":
            return [
                {"section": "Getting Started", "pages": 5, "content": "Materials and setup"},
                {"section": "Basic Activities", "pages": 25, "content": "Simple activities"},
                {"section": "Advanced Activities", "pages": 30, "content": "Complex activities"},
                {"section": "Bonus Projects", "pages": 15, "content": "Special projects"}
            ]
        else:
            return [
                {"section": "Introduction", "pages": 5, "content": "Overview and goals"},
                {"section": "Main Content", "pages": 50, "content": "Core educational content"},
                {"section": "Practice Exercises", "pages": 20, "content": "Reinforcement activities"},
                {"section": "Conclusion", "pages": 5, "content": "Summary and next steps"}
            ]
    
    def generate_marketing_angles(self, trend: Dict) -> List[str]:
        """Generate marketing angles for the book."""
        trend_name = trend.get("name", "")
        category = trend.get("category", "")
        
        angles = [
            f"Perfect for {category} enthusiasts",
            f"Based on trending {trend_name} demand",
            f"Comprehensive {trend_name} collection",
            f"Great gift for {category} lovers",
            f"Educational and entertaining {trend_name} content"
        ]
        
        return angles
    
    async def trigger_content_generation(self, content_briefs: List[Dict]) -> List[Dict]:
        """Trigger content generation for high-priority briefs."""
        logger.info("🚀 Triggering content generation...")
        
        generated_content = []
        for brief in content_briefs:
            if brief.get("priority", 0) > 0.7:  # High priority threshold
                try:
                    content = await self.generate_content(brief)
                    if content:
                        generated_content.append(content)
                except Exception as e:
                    logger.error(f"❌ Content generation failed for {brief.get('book_title')}: {e}")
        
        logger.info(f"✅ Generated content for {len(generated_content)} books")
        return generated_content
    
    async def generate_content(self, brief: Dict) -> Optional[Dict]:
        """Generate actual content for a book brief."""
        # This would integrate with existing content generation workflows
        # For now, we'll create a placeholder that can be expanded
        
        content = {
            "brief_id": brief.get("trend_id"),
            "book_title": brief.get("book_title"),
            "book_type": brief.get("book_type"),
            "status": "queued",
            "generation_started": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        # Save to workflow queue
        await self.data_manager.save_data(
            f"workflow_queue/{content['brief_id']}.json",
            content
        )
        
        return content
    
    async def run_orchestration_cycle(self) -> None:
        """Run a complete orchestration cycle."""
        logger.info("🔄 Starting Consumer Trends orchestration cycle...")
        
        try:
            # Step 1: Analyze trends for content generation
            trends = await self.analyze_trends_for_content_generation()
            
            if not trends:
                logger.info("📊 No suitable trends found for content generation")
                return
            
            # Step 2: Generate content briefs
            content_briefs = await self.generate_content_briefs(trends)
            
            # Step 3: Save briefs for review
            timestamp = datetime.now().isoformat()
            await self.data_manager.save_data(
                f"content_briefs/{timestamp}.json",
                {
                    "timestamp": timestamp,
                    "briefs": content_briefs,
                    "trends_analyzed": len(trends)
                }
            )
            
            # Step 4: Trigger content generation for high-priority briefs
            generated_content = await self.trigger_content_generation(content_briefs)
            
            # Step 5: Save orchestration results
            results = {
                "timestamp": timestamp,
                "trends_analyzed": len(trends),
                "briefs_generated": len(content_briefs),
                "content_triggered": len(generated_content),
                "cycle_duration": time.time()
            }
            
            await self.data_manager.save_data(
                f"orchestration_results/{timestamp}.json",
                results
            )
            
            logger.info(f"✅ Orchestration cycle complete: {len(generated_content)} books queued for generation")
            
        except Exception as e:
            logger.error(f"❌ Orchestration cycle failed: {e}")
    
    async def run(self) -> None:
        """Main orchestration run loop."""
        logger.info("🚀 Starting Consumer Trends Orchestrator...")
        
        try:
            # Initialize services
            await self.initialize_services()
            
            # Run initial orchestration cycle
            await self.run_orchestration_cycle()
            
            logger.info("✅ Consumer Trends Orchestrator completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Orchestrator failed: {e}")
            raise

async def main():
    """Main orchestration entry point."""
    orchestrator = ConsumerTrendsOrchestrator()
    await orchestrator.run()

if __name__ == "__main__":
    import time
    asyncio.run(main()) 