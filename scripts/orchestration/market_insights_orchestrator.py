#!/usr/bin/env python3
"""
Market Insights Orchestrator - Daily automated market intelligence system
Combines multiple data sources for comprehensive KDP market analysis
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pytrends.request import TrendReq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketInsightsOrchestrator:
    """Orchestrates daily market insights collection from multiple sources"""
    
    def __init__(self):
        self.data_dir = Path('data/market-insights')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path('reports/market-insights')
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data sources
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        # Market categories to track
        self.market_categories = {
            'puzzle_books': ['sudoku books', 'crossword puzzles', 'word search books', 'puzzle books adults'],
            'coloring_books': ['adult coloring books', 'coloring books', 'mandala coloring'],
            'journals': ['journal notebook', 'diary journal', 'gratitude journal'],
            'planners': ['daily planner', 'weekly planner', 'productivity planner'],
            'activity_books': ['activity books adults', 'brain games', 'puzzle activity books']
        }
        
    async def collect_all_insights(self) -> Dict:
        """Collect insights from all available sources"""
        logger.info("🚀 Starting daily market insights collection...")
        
        insights = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sources': {}
        }
        
        # 1. Reddit insights (already collected by reddit_market_scraper.py)
        reddit_insights = self.load_reddit_insights()
        if reddit_insights:
            insights['sources']['reddit'] = reddit_insights
        
        # 2. Google Trends insights
        trends_insights = await self.collect_google_trends()
        if trends_insights:
            insights['sources']['google_trends'] = trends_insights
        
        # 3. Amazon marketplace signals (simulated)
        amazon_signals = await self.analyze_amazon_marketplace()
        if amazon_signals:
            insights['sources']['amazon'] = amazon_signals
        
        # 4. Seasonal trends
        seasonal_insights = self.analyze_seasonal_trends()
        insights['sources']['seasonal'] = seasonal_insights
        
        # 5. Synthesize all insights
        insights['synthesis'] = self.synthesize_insights(insights['sources'])
        
        # 6. Generate recommendations
        insights['recommendations'] = self.generate_recommendations(insights['synthesis'])
        
        return insights
    
    def load_reddit_insights(self) -> Optional[Dict]:
        """Load today's Reddit insights if available"""
        today = datetime.now().strftime('%Y%m%d')
        reddit_file = self.data_dir / f"reddit_insights_{today}.json"
        
        if reddit_file.exists():
            with open(reddit_file, 'r') as f:
                return json.load(f)
        
        logger.warning("No Reddit insights found for today")
        return None
    
    async def collect_google_trends(self) -> Dict:
        """Collect Google Trends data for market categories"""
        logger.info("📈 Collecting Google Trends data...")
        
        trends_data = {}
        
        for category, keywords in self.market_categories.items():
            try:
                # Get interest over time
                self.pytrends.build_payload(keywords, timeframe='today 3-m')
                interest_df = self.pytrends.interest_over_time()
                
                if not interest_df.empty:
                    # Calculate trend direction
                    recent_avg = interest_df.iloc[-7:].mean()
                    older_avg = interest_df.iloc[-30:-7].mean()
                    
                    trends_data[category] = {
                        'keywords': keywords,
                        'current_interest': float(recent_avg.mean()),
                        'trend_direction': 'up' if recent_avg.mean() > older_avg.mean() else 'down',
                        'trend_strength': abs(float((recent_avg.mean() - older_avg.mean()) / older_avg.mean() * 100))
                    }
                
                # Get related queries
                related = self.pytrends.related_queries()
                rising_queries = []
                
                for kw in keywords:
                    if kw in related and related[kw]['rising'] is not None:
                        rising_queries.extend(related[kw]['rising']['query'].tolist()[:3])
                
                if rising_queries:
                    trends_data[category]['rising_queries'] = list(set(rising_queries))[:5]
                
            except Exception as e:
                logger.error(f"Error collecting trends for {category}: {e}")
        
        return trends_data
    
    async def analyze_amazon_marketplace(self) -> Dict:
        """Analyze Amazon marketplace for opportunities (simulated)"""
        logger.info("🛒 Analyzing Amazon marketplace signals...")
        
        # In production, this would use Amazon API or web scraping
        # For now, we'll simulate based on known patterns
        
        marketplace_data = {
            'hot_categories': [],
            'saturated_niches': [],
            'emerging_opportunities': []
        }
        
        # Simulate seasonal patterns
        current_month = datetime.now().month
        
        # Q1 patterns (Jan-Mar)
        if current_month in [1, 2, 3]:
            marketplace_data['hot_categories'] = [
                {'category': 'Planners & Organizers', 'competition': 'high', 'demand': 'very high'},
                {'category': 'Diet & Fitness Journals', 'competition': 'medium', 'demand': 'high'}
            ]
        # Q2 patterns (Apr-Jun)
        elif current_month in [4, 5, 6]:
            marketplace_data['hot_categories'] = [
                {'category': 'Summer Activity Books', 'competition': 'low', 'demand': 'rising'},
                {'category': 'Travel Journals', 'competition': 'medium', 'demand': 'high'}
            ]
        # Q3 patterns (Jul-Sep)
        elif current_month in [7, 8, 9]:
            marketplace_data['hot_categories'] = [
                {'category': 'Back-to-School Planners', 'competition': 'high', 'demand': 'very high'},
                {'category': 'Academic Journals', 'competition': 'medium', 'demand': 'high'}
            ]
        # Q4 patterns (Oct-Dec)
        else:
            marketplace_data['hot_categories'] = [
                {'category': 'Holiday Activity Books', 'competition': 'medium', 'demand': 'very high'},
                {'category': 'Gift Journals', 'competition': 'high', 'demand': 'high'}
            ]
        
        # Add emerging opportunities based on trends
        marketplace_data['emerging_opportunities'] = [
            {
                'niche': 'AI-themed Puzzle Books',
                'rationale': 'Growing interest in AI/tech themes',
                'competition': 'very low',
                'estimated_demand': 'growing'
            },
            {
                'niche': 'Mindfulness Coloring Books',
                'rationale': 'Mental health awareness trend',
                'competition': 'medium',
                'estimated_demand': 'stable high'
            }
        ]
        
        return marketplace_data
    
    def analyze_seasonal_trends(self) -> Dict:
        """Analyze seasonal patterns for publishing timing"""
        current_date = datetime.now()
        
        # Major selling seasons
        holidays = {
            'New Year': datetime(current_date.year + (1 if current_date.month == 12 else 0), 1, 1),
            'Valentine\'s Day': datetime(current_date.year, 2, 14),
            'Mother\'s Day': datetime(current_date.year, 5, 12),  # Second Sunday of May (approx)
            'Back to School': datetime(current_date.year, 8, 15),
            'Halloween': datetime(current_date.year, 10, 31),
            'Black Friday': datetime(current_date.year, 11, 29),  # Approximate
            'Christmas': datetime(current_date.year, 12, 25)
        }
        
        seasonal_data = {
            'upcoming_seasons': [],
            'current_opportunities': []
        }
        
        for holiday, date in holidays.items():
            if date < current_date:
                date = date.replace(year=date.year + 1)
            
            days_until = (date - current_date).days
            
            if 0 <= days_until <= 60:  # Within 60 days
                seasonal_data['upcoming_seasons'].append({
                    'season': holiday,
                    'days_until': days_until,
                    'preparation_status': 'urgent' if days_until < 30 else 'plan now',
                    'recommended_categories': self.get_seasonal_categories(holiday)
                })
        
        return seasonal_data
    
    def get_seasonal_categories(self, holiday: str) -> List[str]:
        """Get recommended categories for each season"""
        seasonal_map = {
            'New Year': ['Planners', 'Goal Setting Journals', 'Habit Trackers'],
            'Valentine\'s Day': ['Love Journals', 'Couple\'s Activity Books', 'Romance Planners'],
            'Mother\'s Day': ['Gratitude Journals', 'Family Memory Books', 'Adult Coloring Books'],
            'Back to School': ['Student Planners', 'Study Guides', 'Academic Journals'],
            'Halloween': ['Spooky Activity Books', 'Halloween Coloring Books', 'Horror Puzzles'],
            'Black Friday': ['Gift Sets', 'Puzzle Collections', 'Premium Journals'],
            'Christmas': ['Holiday Activity Books', 'Gift Journals', 'Advent Calendars']
        }
        return seasonal_map.get(holiday, [])
    
    def synthesize_insights(self, sources: Dict) -> Dict:
        """Synthesize insights from all sources into actionable intelligence"""
        synthesis = {
            'top_opportunities': [],
            'market_temperature': {},
            'action_items': []
        }
        
        # Combine Reddit and Google Trends data
        if 'reddit' in sources and sources['reddit']:
            top_reddit_keywords = list(sources['reddit'].get('top_keywords', {}).keys())[:5]
            
            for keyword in top_reddit_keywords:
                synthesis['top_opportunities'].append({
                    'keyword': keyword,
                    'source': 'reddit',
                    'strength': 'high' if sources['reddit']['top_keywords'][keyword]['engagement'] > 500 else 'medium'
                })
        
        if 'google_trends' in sources:
            for category, data in sources['google_trends'].items():
                if data['trend_direction'] == 'up' and data['trend_strength'] > 10:
                    synthesis['top_opportunities'].append({
                        'category': category,
                        'source': 'google_trends',
                        'strength': 'rising',
                        'growth': f"{data['trend_strength']:.1f}%"
                    })
        
        # Market temperature
        total_signals = len(synthesis['top_opportunities'])
        synthesis['market_temperature'] = {
            'overall': 'hot' if total_signals > 5 else 'warm' if total_signals > 2 else 'cool',
            'recommendation': 'Increase production' if total_signals > 5 else 'Maintain pace'
        }
        
        return synthesis
    
    def generate_recommendations(self, synthesis: Dict) -> List[Dict]:
        """Generate specific action recommendations"""
        recommendations = []
        
        # Priority 1: Immediate opportunities
        for opp in synthesis['top_opportunities'][:3]:
            if 'keyword' in opp:
                recommendations.append({
                    'priority': 1,
                    'action': f"Create {opp['keyword']}-themed puzzle book",
                    'timeframe': 'This week',
                    'rationale': f"High engagement on Reddit ({opp['strength']} interest)"
                })
            elif 'category' in opp:
                recommendations.append({
                    'priority': 1,
                    'action': f"Expand {opp['category']} product line",
                    'timeframe': 'Next 2 weeks',
                    'rationale': f"Google Trends shows {opp['growth']} growth"
                })
        
        # Priority 2: Seasonal preparation
        current_date = datetime.now()
        if current_date.month in [10, 11]:  # Pre-holiday season
            recommendations.append({
                'priority': 2,
                'action': 'Prepare holiday-themed collections',
                'timeframe': 'Next 30 days',
                'rationale': 'Q4 is highest revenue period'
            })
        
        return recommendations
    
    def save_insights(self, insights: Dict):
        """Save insights and generate reports"""
        # Save raw JSON
        filename = f"market_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(insights, f, indent=2)
        
        # Generate executive summary
        self.generate_executive_summary(insights)
        
        # Update dashboard data
        self.update_dashboard_data(insights)
        
        logger.info(f"✅ Market insights saved to {filepath}")
        
        return filepath
    
    def generate_executive_summary(self, insights: Dict):
        """Generate executive summary report"""
        report_path = self.reports_dir / f"executive_summary_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# 📊 KindleMint Daily Market Intelligence Report\n\n")
            f.write(f"*Generated: {insights['timestamp']}*\n\n")
            
            # Key Metrics
            f.write("## 🎯 Key Metrics\n\n")
            if 'reddit' in insights['sources'] and insights['sources']['reddit']:
                reddit = insights['sources']['reddit']['summary']
                f.write(f"- **Reddit Posts Analyzed**: {reddit['total_posts_analyzed']}\n")
                f.write(f"- **Average Engagement**: {reddit['avg_engagement']:.1f}\n")
            
            # Top Opportunities
            f.write("\n## 💡 Top 3 Opportunities\n\n")
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                f.write(f"{i}. **{rec['action']}**\n")
                f.write(f"   - Timeframe: {rec['timeframe']}\n")
                f.write(f"   - Rationale: {rec['rationale']}\n\n")
            
            # Market Temperature
            synthesis = insights.get('synthesis', {})
            if 'market_temperature' in synthesis:
                temp = synthesis['market_temperature']
                f.write(f"\n## 🌡️ Market Temperature: {temp['overall'].upper()}\n")
                f.write(f"*{temp['recommendation']}*\n\n")
            
            # Trending Topics
            if 'reddit' in insights['sources'] and insights['sources']['reddit']:
                f.write("## 🔥 Trending Topics\n\n")
                for topic in insights['sources']['reddit']['trending_topics'][:5]:
                    f.write(f"- {topic['title'][:80]}...\n")
            
            f.write("\n---\n*KindleMint Market Intelligence System*")
        
        logger.info(f"📝 Executive summary saved to {report_path}")
    
    def update_dashboard_data(self, insights: Dict):
        """Update data for dashboards and monitoring"""
        dashboard_file = self.data_dir / 'dashboard_data.json'
        
        # Load existing data or create new
        if dashboard_file.exists():
            with open(dashboard_file, 'r') as f:
                dashboard_data = json.load(f)
        else:
            dashboard_data = {
                'history': [],
                'current_state': {}
            }
        
        # Add today's summary
        summary = {
            'date': insights['date'],
            'opportunities_count': len(insights['synthesis']['top_opportunities']),
            'market_temperature': insights['synthesis']['market_temperature']['overall'],
            'recommendations_count': len(insights['recommendations'])
        }
        
        dashboard_data['history'].append(summary)
        dashboard_data['current_state'] = summary
        
        # Keep last 30 days
        dashboard_data['history'] = dashboard_data['history'][-30:]
        
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)


async def main():
    """Main orchestration entry point"""
    orchestrator = MarketInsightsOrchestrator()
    
    try:
        # Collect all insights
        insights = await orchestrator.collect_all_insights()
        
        # Save and generate reports
        orchestrator.save_insights(insights)
        
        # Print summary for CI/CD
        print("\n✅ Market Insights Collection Complete!")
        print(f"📊 Opportunities found: {len(insights['synthesis']['top_opportunities'])}")
        print(f"🌡️ Market temperature: {insights['synthesis']['market_temperature']['overall']}")
        print(f"💡 Recommendations: {len(insights['recommendations'])}")
        print(f"📁 Reports saved to: {orchestrator.reports_dir}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Market insights orchestration failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)