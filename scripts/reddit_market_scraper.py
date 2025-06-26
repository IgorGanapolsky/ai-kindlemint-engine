#!/usr/bin/env python3
"""
Reddit Market Research Scraper for KindleMint Engine
Scrapes trending puzzle and book niches from Reddit
"""

import json
import requests
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, List

class RedditMarketScraper:
    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'KindleMint/1.0 (Market Research Bot)'
        }
        self.output_dir = Path("data/market-insights")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_subreddit_data(self, subreddit: str, limit: int = 25) -> List[Dict]:
        """Fetch hot posts from a subreddit"""
        url = f"{self.base_url}/r/{subreddit}/hot.json?limit={limit}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for post in data['data']['children']:
                    post_data = post['data']
                    posts.append({
                        'title': post_data['title'],
                        'score': post_data['score'],
                        'num_comments': post_data['num_comments'],
                        'created_utc': post_data['created_utc'],
                        'subreddit': post_data['subreddit'],
                        'url': f"{self.base_url}{post_data['permalink']}"
                    })
                
                return posts
            else:
                print(f"Failed to fetch r/{subreddit}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            return []
            
    def analyze_trends(self, posts: List[Dict]) -> Dict:
        """Analyze posts for trending topics and keywords"""
        trends = {
            'keywords': {},
            'top_posts': [],
            'engagement_stats': {
                'avg_score': 0,
                'avg_comments': 0,
                'total_posts': len(posts)
            }
        }
        
        # Common puzzle/book related keywords
        keywords = [
            'crossword', 'sudoku', 'word search', 'puzzle', 'brain teaser',
            'riddle', 'logic', 'kdp', 'self publish', 'kindle', 'amazon',
            'coloring', 'activity book', 'workbook', 'journal', 'planner',
            'notebook', 'large print', 'seniors', 'adults', 'kids', 'children',
            'easy', 'hard', 'challenging', 'beginner', 'advanced', 'daily',
            'collection', 'volume', 'series', 'gift', 'birthday', 'christmas'
        ]
        
        total_score = 0
        total_comments = 0
        
        for post in posts:
            title_lower = post['title'].lower()
            
            # Count keyword occurrences
            for keyword in keywords:
                if keyword in title_lower:
                    if keyword not in trends['keywords']:
                        trends['keywords'][keyword] = 0
                    trends['keywords'][keyword] += 1
                    
            # Track engagement
            total_score += post['score']
            total_comments += post['num_comments']
            
            # Keep top posts
            if post['score'] > 100:
                trends['top_posts'].append({
                    'title': post['title'],
                    'score': post['score'],
                    'url': post['url']
                })
                
        # Calculate averages
        if posts:
            trends['engagement_stats']['avg_score'] = total_score / len(posts)
            trends['engagement_stats']['avg_comments'] = total_comments / len(posts)
            
        # Sort keywords by frequency
        trends['keywords'] = dict(sorted(trends['keywords'].items(), 
                                       key=lambda x: x[1], reverse=True))
        
        # Sort top posts by score
        trends['top_posts'] = sorted(trends['top_posts'], 
                                   key=lambda x: x['score'], reverse=True)[:10]
        
        return trends
        
    def scrape_puzzle_communities(self) -> Dict:
        """Scrape multiple puzzle and publishing related subreddits"""
        subreddits = [
            'crossword', 'puzzles', 'sudoku', 'riddles', 'wordgames',
            'selfpublishing', 'KDP', 'amazonKDP', 'kindlepublishing',
            'activitybooks', 'printables', 'journaling', 'planners',
            'educationalgames', 'homeschool', 'seniorcitizens'
        ]
        
        all_data = {
            'timestamp': datetime.now().isoformat(),
            'subreddits': {},
            'overall_trends': {
                'top_keywords': {},
                'hot_niches': [],
                'recommendations': []
            }
        }
        
        print("🔍 Scraping Reddit for market insights...")
        
        for subreddit in subreddits:
            print(f"  Checking r/{subreddit}...")
            posts = self.get_subreddit_data(subreddit)
            
            if posts:
                trends = self.analyze_trends(posts)
                all_data['subreddits'][subreddit] = trends
                
                # Aggregate keywords
                for keyword, count in trends['keywords'].items():
                    if keyword not in all_data['overall_trends']['top_keywords']:
                        all_data['overall_trends']['top_keywords'][keyword] = 0
                    all_data['overall_trends']['top_keywords'][keyword] += count
                    
            # Be respectful to Reddit's API
            time.sleep(2)
            
        # Sort overall keywords
        all_data['overall_trends']['top_keywords'] = dict(
            sorted(all_data['overall_trends']['top_keywords'].items(),
                   key=lambda x: x[1], reverse=True)[:20]
        )
        
        # Generate recommendations
        self._generate_recommendations(all_data)
        
        return all_data
        
    def _generate_recommendations(self, data: Dict):
        """Generate niche recommendations based on trends"""
        top_keywords = data['overall_trends']['top_keywords']
        
        recommendations = []
        
        # Check for hot combinations
        if 'large print' in top_keywords and 'crossword' in top_keywords:
            recommendations.append({
                'niche': 'Large Print Crosswords',
                'reason': 'High demand in senior communities',
                'keywords': ['large print', 'crossword', 'seniors', 'easy']
            })
            
        if 'sudoku' in top_keywords and ('hard' in top_keywords or 'challenging' in top_keywords):
            recommendations.append({
                'niche': 'Expert Sudoku Collections',
                'reason': 'Enthusiasts seeking difficult puzzles',
                'keywords': ['sudoku', 'expert', 'challenging', 'advanced']
            })
            
        if 'kids' in top_keywords or 'children' in top_keywords:
            recommendations.append({
                'niche': 'Kids Activity Books',
                'reason': 'Parents and educators always need new content',
                'keywords': ['kids', 'activity', 'educational', 'fun']
            })
            
        if 'planner' in top_keywords or 'journal' in top_keywords:
            recommendations.append({
                'niche': 'Specialized Planners/Journals',
                'reason': 'Growing productivity and wellness market',
                'keywords': ['planner', 'journal', 'productivity', 'wellness']
            })
            
        data['overall_trends']['recommendations'] = recommendations
        
    def save_insights(self, data: Dict):
        """Save insights to JSON and markdown"""
        # Save JSON
        json_path = self.output_dir / f"reddit_insights_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Create markdown report
        self._create_markdown_report(data)
        
        print(f"✅ Insights saved to {self.output_dir}")
        
    def _create_markdown_report(self, data: Dict):
        """Create a readable markdown report"""
        md_path = self.output_dir / "market-insights.md"
        
        content = f"""# KindleMint Market Insights

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 🔥 Trending Keywords

| Keyword | Mentions | Heat Level |
|---------|----------|------------|
"""
        
        for keyword, count in list(data['overall_trends']['top_keywords'].items())[:10]:
            heat = "🔥" * min(5, count // 5)
            content += f"| {keyword} | {count} | {heat} |\n"
            
        content += "\n## 📊 Niche Recommendations\n\n"
        
        for rec in data['overall_trends']['recommendations']:
            content += f"### {rec['niche']}\n"
            content += f"**Why:** {rec['reason']}\n"
            content += f"**Keywords:** {', '.join(rec['keywords'])}\n\n"
            
        content += "\n## 🏆 Top Engaging Posts\n\n"
        
        # Aggregate top posts across all subreddits
        all_top_posts = []
        for subreddit, trends in data['subreddits'].items():
            for post in trends.get('top_posts', []):
                post['subreddit'] = subreddit
                all_top_posts.append(post)
                
        all_top_posts.sort(key=lambda x: x['score'], reverse=True)
        
        for post in all_top_posts[:10]:
            content += f"- **[{post['title']}]({post['url']})** (r/{post['subreddit']}, {post['score']} upvotes)\n"
            
        content += f"\n## 📈 Engagement Averages\n\n"
        
        total_avg_score = 0
        total_avg_comments = 0
        subreddit_count = 0
        
        for subreddit, trends in data['subreddits'].items():
            stats = trends.get('engagement_stats', {})
            if stats.get('total_posts', 0) > 0:
                total_avg_score += stats.get('avg_score', 0)
                total_avg_comments += stats.get('avg_comments', 0)
                subreddit_count += 1
                
        if subreddit_count > 0:
            content += f"- Average post score: {total_avg_score/subreddit_count:.1f}\n"
            content += f"- Average comments: {total_avg_comments/subreddit_count:.1f}\n"
            
        content += f"\n---\n*Generated by KindleMint Market Research Bot*"
        
        with open(md_path, 'w') as f:
            f.write(content)
            
    def run_daily_scrape(self):
        """Main method to run the daily scrape"""
        data = self.scrape_puzzle_communities()
        self.save_insights(data)
        return data


if __name__ == "__main__":
    scraper = RedditMarketScraper()
    insights = scraper.run_daily_scrape()
    
    print("\n📊 Top 5 Trending Keywords:")
    for keyword, count in list(insights['overall_trends']['top_keywords'].items())[:5]:
        print(f"  - {keyword}: {count} mentions")