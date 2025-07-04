#!/usr/bin/env python3
"""
Reddit Market Scraper - Collects market insights from Reddit communities
Part of the daily market insights orchestration system
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from security import safe_requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedditMarketScraper:
    """Scrapes Reddit for KDP and self-publishing market insights"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'KindleMint-Market-Research/1.0'
        }
        self.subreddits = [
            'selfpublishing',
            'KDP',
            'eroticauthors',
            'writingopportunities',
            'amazonKDP',
            'publishing',
            'selfpublish',
            'BookMarketing'
        ]
        self.base_url = 'https://www.reddit.com'
        
    def fetch_subreddit_posts(self, subreddit: str, sort: str = 'hot', limit: int = 25) -> List[Dict]:
        """Fetch posts from a subreddit using Reddit's JSON API"""
        url = f"{self.base_url}/r/{subreddit}/{sort}.json"
        params = {'limit': limit}
        
        try:
            response = safe_requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                posts.append({
                    'title': post_data.get('title', ''),
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'created_utc': post_data.get('created_utc', 0),
                    'subreddit': post_data.get('subreddit', ''),
                    'url': f"{self.base_url}{post_data.get('permalink', '')}",
                    'selftext': post_data.get('selftext', '')[:500]  # First 500 chars
                })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching r/{subreddit}: {e}")
            return []
    
    def analyze_posts(self, posts: List[Dict]) -> Dict:
        """Analyze posts for market insights"""
        keywords = {}
        total_engagement = 0
        trending_topics = []
        
        # Keywords to track
        tracking_keywords = [
            'kdp', 'kindle', 'publishing', 'sales', 'niche', 'keywords',
            'cover', 'marketing', 'amazon', 'book', 'ebook', 'paperback',
            'puzzle', 'coloring', 'journal', 'notebook', 'planner',
            'romance', 'fantasy', 'mystery', 'self-help', 'children',
            'advertising', 'ads', 'promotion', 'review', 'launch'
        ]
        
        for post in posts:
            # Count engagement
            engagement = post['score'] + (post['num_comments'] * 2)
            total_engagement += engagement
            
            # Extract keywords from title and text
            text = f"{post['title']} {post['selftext']}".lower()
            
            for keyword in tracking_keywords:
                if keyword in text:
                    if keyword not in keywords:
                        keywords[keyword] = {'count': 0, 'engagement': 0}
                    keywords[keyword]['count'] += 1
                    keywords[keyword]['engagement'] += engagement
            
            # Track high-engagement posts
            if engagement > 50:
                trending_topics.append({
                    'title': post['title'],
                    'engagement': engagement,
                    'url': post['url'],
                    'subreddit': post['subreddit']
                })
        
        # Sort trending topics by engagement
        trending_topics.sort(key=lambda x: x['engagement'], reverse=True)
        
        return {
            'keywords': keywords,
            'trending_topics': trending_topics[:10],  # Top 10
            'total_posts': len(posts),
            'avg_engagement': total_engagement / len(posts) if posts else 0
        }
    
    def collect_market_insights(self) -> Dict:
        """Collect insights from all configured subreddits"""
        all_posts = []
        subreddit_insights = {}
        
        logger.info(f"Collecting insights from {len(self.subreddits)} subreddits...")
        
        for subreddit in self.subreddits:
            logger.info(f"Fetching r/{subreddit}...")
            posts = self.fetch_subreddit_posts(subreddit)
            
            if posts:
                all_posts.extend(posts)
                subreddit_insights[subreddit] = self.analyze_posts(posts)
        
        # Aggregate insights
        aggregated = self.analyze_posts(all_posts)
        
        # Sort keywords by engagement
        sorted_keywords = sorted(
            aggregated['keywords'].items(),
            key=lambda x: x[1]['engagement'],
            reverse=True
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_posts_analyzed': len(all_posts),
                'subreddits_scraped': len([s for s in subreddit_insights if subreddit_insights[s]['total_posts'] > 0]),
                'avg_engagement': aggregated['avg_engagement']
            },
            'top_keywords': dict(sorted_keywords[:20]),  # Top 20 keywords
            'trending_topics': aggregated['trending_topics'],
            'subreddit_insights': subreddit_insights,
            'market_signals': self.extract_market_signals(aggregated, subreddit_insights)
        }
    
    def extract_market_signals(self, aggregated: Dict, subreddit_insights: Dict) -> List[Dict]:
        """Extract actionable market signals from the data"""
        signals = []
        
        # High-demand niches (keywords with high engagement)
        for keyword, data in list(aggregated['keywords'].items())[:10]:
            if data['engagement'] > 100:
                signals.append({
                    'type': 'high_demand_niche',
                    'keyword': keyword,
                    'strength': 'strong' if data['engagement'] > 500 else 'moderate',
                    'engagement': data['engagement'],
                    'recommendation': f"Consider creating content around '{keyword}' - high community interest"
                })
        
        # Emerging trends (recent posts with rapid engagement)
        for topic in aggregated['trending_topics'][:5]:
            signals.append({
                'type': 'trending_topic',
                'title': topic['title'],
                'engagement': topic['engagement'],
                'source': topic['subreddit'],
                'recommendation': 'Monitor this topic for content opportunities'
            })
        
        return signals
    
    def save_insights(self, insights: Dict):
        """Save insights to data directory"""
        # Create directories
        data_dir = Path('data/market-insights')
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON data
        filename = f"reddit_insights_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(insights, f, indent=2)
        
        logger.info(f"Saved insights to {filepath}")
        
        # Update the markdown report
        self.update_markdown_report(insights)
        
        return filepath
    
    def update_markdown_report(self, insights: Dict):
        """Update the human-readable markdown report"""
        report_path = Path('data/market-insights/market-insights.md')
        
        with open(report_path, 'w') as f:
            f.write("# KindleMint Market Insights\n\n")
            f.write(f"*Last Updated: {insights['timestamp']}*\n\n")
            
            # Summary
            f.write("## 📊 Summary\n\n")
            f.write(f"- **Posts Analyzed**: {insights['summary']['total_posts_analyzed']}\n")
            f.write(f"- **Subreddits**: {insights['summary']['subreddits_scraped']}\n")
            f.write(f"- **Avg Engagement**: {insights['summary']['avg_engagement']:.1f}\n\n")
            
            # Top Keywords
            f.write("## 🔥 Trending Keywords\n\n")
            f.write("| Keyword | Mentions | Total Engagement |\n")
            f.write("|---------|----------|------------------|\n")
            
            for keyword, data in list(insights['top_keywords'].items())[:10]:
                f.write(f"| {keyword} | {data['count']} | {data['engagement']} |\n")
            
            # Market Signals
            f.write("\n## 🎯 Market Signals\n\n")
            for signal in insights['market_signals'][:5]:
                if signal['type'] == 'high_demand_niche':
                    f.write(f"- **{signal['keyword']}** - {signal['recommendation']}\n")
                elif signal['type'] == 'trending_topic':
                    f.write(f"- **Trending**: {signal['title'][:80]}... (r/{signal['source']})\n")
            
            # Top Posts
            f.write("\n## 🏆 Top Engaging Posts\n\n")
            for topic in insights['trending_topics'][:5]:
                f.write(f"1. **[{topic['title'][:80]}...]({topic['url']})**\n")
                f.write(f"   - Engagement: {topic['engagement']} | Subreddit: r/{topic['subreddit']}\n\n")
            
            f.write("\n---\n*Generated by KindleMint Market Research Bot*\n")
        
        logger.info("Updated market insights report")


def main():
    """Main entry point"""
    logger.info("Starting Reddit market scraper...")
    
    scraper = RedditMarketScraper()
    insights = scraper.collect_market_insights()
    filepath = scraper.save_insights(insights)
    
    # Print summary for CI/CD logs
    print(f"\n✅ Market insights collected successfully!")
    print(f"📊 Analyzed {insights['summary']['total_posts_analyzed']} posts")
    print(f"🔥 Top keyword: {list(insights['top_keywords'].keys())[0] if insights['top_keywords'] else 'N/A'}")
    print(f"💾 Saved to: {filepath}")


if __name__ == "__main__":
    main()
