"""
PredictiveTrendAnalyzer: Core engine for identifying and validating profitable niches.

This module analyzes data from multiple sources (Reddit, TikTok, Google Trends, Amazon)
to identify emerging trends and predict their profitability for book publishing.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import aiohttp
import pandas as pd

from ..utils.data_manager import DataManager
from ..utils.config import Config

logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    """Data structure for trend information."""
    topic: str
    source: str
    score: float
    volume: int
    sentiment: float
    competition_level: str
    predicted_profitability: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class TrendAnalysis:
    """Complete trend analysis result."""
    trends: List[TrendData]
    summary: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


class PredictiveTrendAnalyzer:
    """
    Core engine for identifying and validating profitable niches.
    
    Analyzes data from multiple sources to predict trending topics
    and their potential profitability for book publishing.
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.data_manager = DataManager()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Data sources configuration
        self.reddit_subreddits = [
            'books', 'kindle', 'bookrecommendations', 'suggestmeabook',
            'whattoreadwhen', 'bookclub', 'reading', 'literature'
        ]
        
        self.tiktok_hashtags = [
            '#booktok', '#reading', '#books', '#bookrecommendations',
            '#bookreview', '#readinglist', '#booklover', '#bookish'
        ]
        
        # Scoring weights for different factors
        self.scoring_weights = {
            'volume': 0.3,
            'sentiment': 0.2,
            'competition': 0.25,
            'trend_velocity': 0.25
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def analyze_trends(self) -> TrendAnalysis:
        """
        Perform comprehensive trend analysis across all data sources.
        
        Returns:
            TrendAnalysis: Complete analysis with trends, summary, and recommendations
        """
        logger.info("Starting comprehensive trend analysis")
        
        # Collect data from all sources
        reddit_data = await self._collect_reddit_data()
        tiktok_data = await self._collect_tiktok_data()
        google_trends_data = await self._collect_google_trends_data()
        amazon_data = await self._collect_amazon_data()
        
        # Combine and analyze data
        combined_trends = self._combine_data_sources(
            reddit_data, tiktok_data, google_trends_data, amazon_data
        )
        
        # Score and rank trends
        scored_trends = self._score_trends(combined_trends)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scored_trends)
        
        # Create summary
        summary = self._create_summary(scored_trends)
        
        analysis = TrendAnalysis(
            trends=scored_trends,
            summary=summary,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
        
        # Save analysis results
        await self._save_analysis(analysis)
        
        logger.info(f"Trend analysis complete. Found {len(scored_trends)} trends")
        return analysis
    
    async def _collect_reddit_data(self) -> List[Dict[str, Any]]:
        """Collect trending topics from Reddit."""
        logger.info("Collecting Reddit data")
        
        # For now, return mock data - in production, implement Reddit API calls
        mock_reddit_data = [
            {
                'topic': 'AI and Machine Learning Books',
                'source': 'reddit',
                'volume': 150,
                'sentiment': 0.8,
                'subreddit': 'books',
                'timestamp': datetime.now()
            },
            {
                'topic': 'Self-Help for Entrepreneurs',
                'source': 'reddit',
                'volume': 89,
                'sentiment': 0.7,
                'subreddit': 'bookrecommendations',
                'timestamp': datetime.now()
            },
            {
                'topic': 'Fantasy Romance Novels',
                'source': 'reddit',
                'volume': 234,
                'sentiment': 0.9,
                'subreddit': 'books',
                'timestamp': datetime.now()
            }
        ]
        
        return mock_reddit_data
    
    async def _collect_tiktok_data(self) -> List[Dict[str, Any]]:
        """Collect trending topics from TikTok."""
        logger.info("Collecting TikTok data")
        
        # Mock TikTok data - implement TikTok API in production
        mock_tiktok_data = [
            {
                'topic': 'BookTok Recommendations',
                'source': 'tiktok',
                'volume': 1200,
                'sentiment': 0.85,
                'hashtag': '#booktok',
                'timestamp': datetime.now()
            },
            {
                'topic': 'Reading Challenges',
                'source': 'tiktok',
                'volume': 890,
                'sentiment': 0.75,
                'hashtag': '#reading',
                'timestamp': datetime.now()
            }
        ]
        
        return mock_tiktok_data
    
    async def _collect_google_trends_data(self) -> List[Dict[str, Any]]:
        """Collect trending topics from Google Trends."""
        logger.info("Collecting Google Trends data")
        
        # Mock Google Trends data - implement pytrends in production
        mock_google_data = [
            {
                'topic': 'AI Books 2025',
                'source': 'google_trends',
                'volume': 95,
                'sentiment': 0.8,
                'trend_velocity': 0.7,
                'timestamp': datetime.now()
            },
            {
                'topic': 'Entrepreneurship Books',
                'source': 'google_trends',
                'volume': 78,
                'sentiment': 0.6,
                'trend_velocity': 0.5,
                'timestamp': datetime.now()
            }
        ]
        
        return mock_google_data
    
    async def _collect_amazon_data(self) -> List[Dict[str, Any]]:
        """Collect data from Amazon Best Sellers."""
        logger.info("Collecting Amazon data")
        
        # Mock Amazon data - implement Amazon API in production
        mock_amazon_data = [
            {
                'topic': 'Business Strategy Books',
                'source': 'amazon',
                'volume': 200,
                'competition_level': 'medium',
                'avg_rating': 4.2,
                'timestamp': datetime.now()
            },
            {
                'topic': 'Personal Development',
                'source': 'amazon',
                'volume': 180,
                'competition_level': 'high',
                'avg_rating': 4.1,
                'timestamp': datetime.now()
            }
        ]
        
        return mock_amazon_data
    
    def _combine_data_sources(
        self,
        reddit_data: List[Dict[str, Any]],
        tiktok_data: List[Dict[str, Any]],
        google_trends_data: List[Dict[str, Any]],
        amazon_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine data from all sources and normalize."""
        combined = []
        
        # Process Reddit data
        for item in reddit_data:
            combined.append({
                'topic': item['topic'],
                'source': 'reddit',
                'volume': item['volume'],
                'sentiment': item['sentiment'],
                'competition_level': self._assess_competition(item['topic']),
                'trend_velocity': 0.6,  # Default value
                'metadata': {
                    'subreddit': item.get('subreddit', ''),
                    'timestamp': item['timestamp']
                }
            })
        
        # Process TikTok data
        for item in tiktok_data:
            combined.append({
                'topic': item['topic'],
                'source': 'tiktok',
                'volume': item['volume'],
                'sentiment': item['sentiment'],
                'competition_level': self._assess_competition(item['topic']),
                'trend_velocity': 0.8,  # Higher for social media
                'metadata': {
                    'hashtag': item.get('hashtag', ''),
                    'timestamp': item['timestamp']
                }
            })
        
        # Process Google Trends data
        for item in google_trends_data:
            combined.append({
                'topic': item['topic'],
                'source': 'google_trends',
                'volume': item['volume'],
                'sentiment': item['sentiment'],
                'competition_level': self._assess_competition(item['topic']),
                'trend_velocity': item.get('trend_velocity', 0.5),
                'metadata': {
                    'timestamp': item['timestamp']
                }
            })
        
        # Process Amazon data
        for item in amazon_data:
            combined.append({
                'topic': item['topic'],
                'source': 'amazon',
                'volume': item['volume'],
                'sentiment': 0.7,  # Default sentiment for Amazon
                'competition_level': item['competition_level'],
                'trend_velocity': 0.4,  # Lower for marketplace data
                'metadata': {
                    'avg_rating': item.get('avg_rating', 0),
                    'timestamp': item['timestamp']
                }
            })
        
        return combined
    
    def _assess_competition(self, topic: str) -> str:
        """Assess competition level for a given topic."""
        # Simple keyword-based competition assessment
        high_competition_keywords = ['business', 'self-help', 'fiction', 'romance']
        medium_competition_keywords = ['technology', 'science', 'history', 'biography']
        
        topic_lower = topic.lower()
        
        if any(keyword in topic_lower for keyword in high_competition_keywords):
            return 'high'
        elif any(keyword in topic_lower for keyword in medium_competition_keywords):
            return 'medium'
        else:
            return 'low'
    
    def _score_trends(self, trends: List[Dict[str, Any]]) -> List[TrendData]:
        """Score and rank trends based on multiple factors."""
        scored_trends = []
        
        for trend in trends:
            # Calculate profitability score
            volume_score = min(trend['volume'] / 1000, 1.0)  # Normalize to 0-1
            sentiment_score = trend['sentiment']
            
            # Competition score (inverse relationship)
            competition_scores = {'low': 1.0, 'medium': 0.7, 'high': 0.4}
            competition_score = competition_scores.get(trend['competition_level'], 0.5)
            
            trend_velocity_score = trend['trend_velocity']
            
            # Calculate weighted profitability score
            profitability = (
                volume_score * self.scoring_weights['volume'] +
                sentiment_score * self.scoring_weights['sentiment'] +
                competition_score * self.scoring_weights['competition'] +
                trend_velocity_score * self.scoring_weights['trend_velocity']
            )
            
            trend_data = TrendData(
                topic=trend['topic'],
                source=trend['source'],
                score=profitability,
                volume=trend['volume'],
                sentiment=trend['sentiment'],
                competition_level=trend['competition_level'],
                predicted_profitability=profitability,
                timestamp=trend['metadata']['timestamp'],
                metadata=trend['metadata']
            )
            
            scored_trends.append(trend_data)
        
        # Sort by profitability score (descending)
        scored_trends.sort(key=lambda x: x.predicted_profitability, reverse=True)
        
        return scored_trends
    
    def _generate_recommendations(self, trends: List[TrendData]) -> List[str]:
        """Generate actionable recommendations based on trend analysis."""
        recommendations = []
        
        if not trends:
            recommendations.append("No significant trends detected. Consider expanding data sources.")
            return recommendations
        
        # Top trend recommendation
        top_trend = trends[0]
        recommendations.append(
            f"Focus on '{top_trend.topic}' - highest profitability score ({top_trend.predicted_profitability:.2f}) "
            f"with {top_trend.competition_level} competition"
        )
        
        # Low competition opportunities
        low_competition_trends = [t for t in trends if t.competition_level == 'low']
        if low_competition_trends:
            recommendations.append(
                f"Target {len(low_competition_trends)} low-competition niches for quick market entry"
            )
        
        # High volume opportunities
        high_volume_trends = [t for t in trends if t.volume > 500]
        if high_volume_trends:
            recommendations.append(
                f"Capitalize on {len(high_volume_trends)} high-volume trends for maximum reach"
            )
        
        # Sentiment-based recommendations
        positive_trends = [t for t in trends if t.sentiment > 0.8]
        if positive_trends:
            recommendations.append(
                f"Leverage {len(positive_trends)} highly positive trends for viral potential"
            )
        
        return recommendations
    
    def _create_summary(self, trends: List[TrendData]) -> Dict[str, Any]:
        """Create summary statistics for the trend analysis."""
        if not trends:
            return {
                'total_trends': 0,
                'avg_profitability': 0,
                'top_sources': [],
                'competition_distribution': {}
            }
        
        # Calculate summary statistics
        avg_profitability = sum(t.predicted_profitability for t in trends) / len(trends)
        
        # Top sources
        source_counts = {}
        for trend in trends:
            source_counts[trend.source] = source_counts.get(trend.source, 0) + 1
        
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Competition distribution
        competition_distribution = {}
        for trend in trends:
            competition_distribution[trend.competition_level] = \
                competition_distribution.get(trend.competition_level, 0) + 1
        
        return {
            'total_trends': len(trends),
            'avg_profitability': avg_profitability,
            'top_sources': top_sources,
            'competition_distribution': competition_distribution,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def _save_analysis(self, analysis: TrendAnalysis) -> None:
        """Save analysis results to storage."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trend_analysis_{timestamp}.json"
        
        # Convert to JSON-serializable format
        analysis_dict = {
            'trends': [asdict(trend) for trend in analysis.trends],
            'summary': analysis.summary,
            'recommendations': analysis.recommendations,
            'generated_at': analysis.generated_at.isoformat()
        }
        
        # Save to data storage
        await self.data_manager.save_data(
            'trend_analysis',
            filename,
            analysis_dict
        )
        
        logger.info(f"Trend analysis saved to {filename}")
    
    async def get_latest_analysis(self) -> Optional[TrendAnalysis]:
        """Retrieve the most recent trend analysis."""
        try:
            # Get the most recent analysis file
            analysis_files = await self.data_manager.list_data('trend_analysis')
            if not analysis_files:
                return None
            
            # Sort by timestamp and get the latest
            latest_file = sorted(analysis_files, reverse=True)[0]
            analysis_data = await self.data_manager.load_data('trend_analysis', latest_file)
            
            # Convert back to TrendAnalysis object
            trends = [TrendData(**trend) for trend in analysis_data['trends']]
            
            return TrendAnalysis(
                trends=trends,
                summary=analysis_data['summary'],
                recommendations=analysis_data['recommendations'],
                generated_at=datetime.fromisoformat(analysis_data['generated_at'])
            )
        
        except Exception as e:
            logger.error(f"Error retrieving latest analysis: {e}")
            return None


async def main():
    """Main function for testing the trend analyzer."""
    config = Config()
    
    async with PredictiveTrendAnalyzer(config) as analyzer:
        analysis = await analyzer.analyze_trends()
        
        print(f"\n=== Trend Analysis Results ===")
        print(f"Total trends found: {len(analysis.trends)}")
        print(f"Average profitability: {analysis.summary['avg_profitability']:.2f}")
        
        print(f"\n=== Top 5 Trends ===")
        for i, trend in enumerate(analysis.trends[:5], 1):
            print(f"{i}. {trend.topic}")
            print(f"   Profitability: {trend.predicted_profitability:.2f}")
            print(f"   Competition: {trend.competition_level}")
            print(f"   Source: {trend.source}")
            print()
        
        print(f"\n=== Recommendations ===")
        for rec in analysis.recommendations:
            print(f"• {rec}")


if __name__ == "__main__":
    asyncio.run(main()) 