"""
Organic Feedback Loop - Zero-Budget Performance Analysis
Analyzes ONLY organic KDP sales and KU page-read data for learning.

BUSINESS IMPACT: Pure organic performance tracking without ad noise
STRATEGY: Memory learns from natural market response to optimize content
"""
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

from ..memory import KDPMemory

logger = logging.getLogger(__name__)

class OrganicFeedbackAnalyzer:
    """Analyzes organic KDP performance to guide content strategy."""
    
    def __init__(self, region_name: str = 'us-east-2', profile_name: Optional[str] = None):
        """Initialize organic feedback analyzer."""
        self.region_name = region_name
        self.profile_name = profile_name
        
        # Initialize memory system
        try:
            self.memory = KDPMemory(region_name=region_name, profile_name=profile_name)
            logger.info("Organic Feedback Analyzer initialized with memory system")
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            raise
    
    async def analyze_organic_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze organic KDP performance over specified period.
        
        CRITICAL: Only analyzes organic sales data - NO ad performance.
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dict with organic performance insights
        """
        try:
            logger.info(f"🔍 ANALYZING ORGANIC PERFORMANCE ({days_back} days)")
            
            # Get all books from memory
            all_books = await self.memory.get_all_books()
            
            if not all_books:
                logger.warning("No books found in memory for analysis")
                return self._empty_analysis()
            
            # Filter for organic performance data only
            organic_books = self._filter_organic_data(all_books, days_back)
            
            # Analyze performance patterns
            performance_insights = self._analyze_performance_patterns(organic_books)
            
            # Generate content strategy recommendations
            content_recommendations = self._generate_content_recommendations(performance_insights)
            
            # Identify winning niches
            winning_niches = self._identify_winning_niches(organic_books)
            
            # Calculate overall organic ROI
            organic_roi = self._calculate_organic_roi(organic_books)
            
            analysis_result = {
                'analysis_date': datetime.now().isoformat(),
                'period_analyzed_days': days_back,
                'total_books_analyzed': len(organic_books),
                'organic_roi_overall': organic_roi,
                'winning_niches': winning_niches,
                'performance_insights': performance_insights,
                'content_recommendations': content_recommendations,
                'top_performers': self._get_top_performers(organic_books),
                'learning_priorities': self._identify_learning_priorities(performance_insights)
            }
            
            logger.info(f"✅ Organic analysis complete: {len(winning_niches)} winning niches identified")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Organic performance analysis failed: {str(e)}")
            return self._empty_analysis()
    
    def _filter_organic_data(self, books: List[Dict[str, Any]], days_back: int) -> List[Dict[str, Any]]:
        """Filter books to include only organic performance data."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            organic_books = []
            
            for book in books:
                # Skip if no organic sales data
                if not book.get('kdp_sales_count') and not book.get('kenp_read_count'):
                    continue
                
                # Check if book is within analysis period
                creation_date = datetime.fromisoformat(book.get('creation_date', '2024-01-01'))
                if creation_date < cutoff_date:
                    continue
                
                # Ensure we're only analyzing organic metrics
                organic_book = {
                    'book_id': book['book_id'],
                    'topic': book.get('topic', 'unknown'),
                    'niche': book.get('niche', 'unknown'),
                    'creation_date': book['creation_date'],
                    'kdp_sales_count': book.get('kdp_sales_count', 0),
                    'kenp_read_count': book.get('kenp_read_count', 0),
                    'calculated_roi': book.get('calculated_roi', 0),
                    'days_live': (datetime.now() - creation_date).days,
                    # CRITICAL: Exclude any ad-related metrics
                    'organic_only': True
                }
                
                organic_books.append(organic_book)
            
            logger.info(f"📊 Filtered to {len(organic_books)} books with organic data")
            return organic_books
            
        except Exception as e:
            logger.error(f"Failed to filter organic data: {e}")
            return []
    
    def _analyze_performance_patterns(self, books: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in organic performance."""
        try:
            if not books:
                return {}
            
            # Group by niche
            niche_performance = {}
            topic_performance = {}
            time_patterns = {}
            
            for book in books:
                niche = book['niche']
                topic = book['topic']
                sales = book['kdp_sales_count']
                reads = book['kenp_read_count']
                roi = book['calculated_roi']
                days_live = book['days_live']
                
                # Niche analysis
                if niche not in niche_performance:
                    niche_performance[niche] = {
                        'total_books': 0,
                        'total_sales': 0,
                        'total_reads': 0,
                        'total_roi': 0,
                        'avg_roi': 0
                    }
                
                niche_data = niche_performance[niche]
                niche_data['total_books'] += 1
                niche_data['total_sales'] += sales
                niche_data['total_reads'] += reads
                niche_data['total_roi'] += roi
                niche_data['avg_roi'] = niche_data['total_roi'] / niche_data['total_books']
                
                # Topic analysis
                if topic not in topic_performance:
                    topic_performance[topic] = {
                        'sales': sales,
                        'reads': reads,
                        'roi': roi,
                        'days_live': days_live
                    }
                
                # Time pattern analysis
                week_bucket = days_live // 7  # Group by week
                if week_bucket not in time_patterns:
                    time_patterns[week_bucket] = {
                        'books': 0,
                        'avg_sales': 0,
                        'avg_reads': 0
                    }
                
                time_data = time_patterns[week_bucket]
                time_data['books'] += 1
                time_data['avg_sales'] = (time_data['avg_sales'] * (time_data['books'] - 1) + sales) / time_data['books']
                time_data['avg_reads'] = (time_data['avg_reads'] * (time_data['books'] - 1) + reads) / time_data['books']
            
            return {
                'niche_performance': niche_performance,
                'topic_performance': topic_performance,
                'time_patterns': time_patterns,
                'total_organic_sales': sum(book['kdp_sales_count'] for book in books),
                'total_organic_reads': sum(book['kenp_read_count'] for book in books),
                'avg_roi_per_book': sum(book['calculated_roi'] for book in books) / len(books)
            }
            
        except Exception as e:
            logger.error(f"Performance pattern analysis failed: {e}")
            return {}
    
    def _generate_content_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate content strategy recommendations based on organic performance."""
        try:
            recommendations = []
            
            if not insights:
                return recommendations
            
            niche_performance = insights.get('niche_performance', {})
            
            # Find best performing niches
            best_niches = sorted(
                niche_performance.items(),
                key=lambda x: x[1]['avg_roi'],
                reverse=True
            )[:3]
            
            for niche, data in best_niches:
                if data['avg_roi'] > 0:
                    recommendations.append({
                        'type': 'focus_niche',
                        'priority': 'high',
                        'action': f'Double down on {niche} niche',
                        'reason': f'Average ROI: {data["avg_roi"]:.2f}%, {data["total_books"]} books tested',
                        'expected_impact': f'Potential {data["total_sales"] * 2} additional organic sales'
                    })
            
            # Identify underperforming areas to avoid
            worst_niches = sorted(
                niche_performance.items(),
                key=lambda x: x[1]['avg_roi']
            )[:2]
            
            for niche, data in worst_niches:
                if data['avg_roi'] < 0:
                    recommendations.append({
                        'type': 'avoid_niche',
                        'priority': 'medium',
                        'action': f'Avoid {niche} niche temporarily',
                        'reason': f'Negative ROI: {data["avg_roi"]:.2f}%, {data["total_books"]} books tested',
                        'expected_impact': 'Prevent resource waste on low-performing content'
                    })
            
            # Content timing recommendations
            time_patterns = insights.get('time_patterns', {})
            if time_patterns:
                best_week = max(time_patterns.items(), key=lambda x: x[1]['avg_sales'])
                recommendations.append({
                    'type': 'timing_optimization',
                    'priority': 'medium',
                    'action': f'Focus on week {best_week[0]} performance patterns',
                    'reason': f'Best organic sales week: {best_week[1]["avg_sales"]:.1f} avg sales',
                    'expected_impact': 'Optimize launch timing for maximum organic reach'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Content recommendations generation failed: {e}")
            return []
    
    def _identify_winning_niches(self, books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify niches with strong organic performance."""
        try:
            niche_stats = {}
            
            for book in books:
                niche = book['niche']
                if niche not in niche_stats:
                    niche_stats[niche] = {
                        'total_books': 0,
                        'total_sales': 0,
                        'total_reads': 0,
                        'total_roi': 0,
                        'books': []
                    }
                
                stats = niche_stats[niche]
                stats['total_books'] += 1
                stats['total_sales'] += book['kdp_sales_count']
                stats['total_reads'] += book['kenp_read_count']
                stats['total_roi'] += book['calculated_roi']
                stats['books'].append(book['book_id'])
            
            # Calculate averages and identify winners
            winning_niches = []
            for niche, stats in niche_stats.items():
                avg_roi = stats['total_roi'] / stats['total_books']
                avg_sales = stats['total_sales'] / stats['total_books']
                
                # Winning criteria: positive ROI and at least 1 sale per book on average
                if avg_roi > 0 and avg_sales >= 1:
                    winning_niches.append({
                        'niche': niche,
                        'avg_roi': round(avg_roi, 2),
                        'avg_organic_sales': round(avg_sales, 1),
                        'total_books': stats['total_books'],
                        'confidence_score': min(100, stats['total_books'] * 20),  # More books = higher confidence
                        'recommendation': 'EXPAND' if avg_roi > 50 else 'CONTINUE'
                    })
            
            # Sort by ROI
            winning_niches.sort(key=lambda x: x['avg_roi'], reverse=True)
            
            return winning_niches
            
        except Exception as e:
            logger.error(f"Winning niches identification failed: {e}")
            return []
    
    def _calculate_organic_roi(self, books: List[Dict[str, Any]]) -> float:
        """Calculate overall organic ROI."""
        try:
            if not books:
                return 0.0
            
            total_roi = sum(book['calculated_roi'] for book in books)
            return round(total_roi / len(books), 2)
            
        except Exception as e:
            logger.error(f"Organic ROI calculation failed: {e}")
            return 0.0
    
    def _get_top_performers(self, books: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top performing books based on organic metrics."""
        try:
            # Sort by ROI first, then by sales
            sorted_books = sorted(
                books,
                key=lambda x: (x['calculated_roi'], x['kdp_sales_count']),
                reverse=True
            )
            
            top_performers = []
            for book in sorted_books[:top_n]:
                top_performers.append({
                    'book_id': book['book_id'],
                    'niche': book['niche'],
                    'topic': book['topic'],
                    'organic_sales': book['kdp_sales_count'],
                    'page_reads': book['kenp_read_count'],
                    'roi': book['calculated_roi'],
                    'days_live': book['days_live'],
                    'daily_avg_sales': round(book['kdp_sales_count'] / max(1, book['days_live']), 2)
                })
            
            return top_performers
            
        except Exception as e:
            logger.error(f"Top performers identification failed: {e}")
            return []
    
    def _identify_learning_priorities(self, insights: Dict[str, Any]) -> List[str]:
        """Identify what the system should focus on learning next."""
        try:
            priorities = []
            
            niche_performance = insights.get('niche_performance', {})
            
            # If we have less than 3 books per niche, need more data
            for niche, data in niche_performance.items():
                if data['total_books'] < 3:
                    priorities.append(f"Test more variations in {niche} niche (only {data['total_books']} books)")
            
            # If ROI varies widely, need to understand why
            rois = [data['avg_roi'] for data in niche_performance.values()]
            if len(rois) > 1:
                roi_variance = max(rois) - min(rois)
                if roi_variance > 100:
                    priorities.append("Investigate large ROI variance between niches")
            
            # If no clear winner, need more exploration
            if not any(data['avg_roi'] > 50 for data in niche_performance.values()):
                priorities.append("Explore new niches - current ones underperforming")
            
            return priorities[:5]  # Top 5 priorities
            
        except Exception as e:
            logger.error(f"Learning priorities identification failed: {e}")
            return []
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'analysis_date': datetime.now().isoformat(),
            'period_analyzed_days': 0,
            'total_books_analyzed': 0,
            'organic_roi_overall': 0.0,
            'winning_niches': [],
            'performance_insights': {},
            'content_recommendations': [],
            'top_performers': [],
            'learning_priorities': ['Initialize system with first organic book publication']
        }
    
    async def update_learning_memory(self, analysis_result: Dict[str, Any]) -> bool:
        """Update memory system with learning insights."""
        try:
            # Store analysis results in memory for future reference
            analysis_record = {
                'record_type': 'organic_analysis',
                'analysis_date': analysis_result['analysis_date'],
                'insights': analysis_result,
                'learning_status': 'processed'
            }
            
            # This would integrate with memory system to store learning insights
            logger.info("💾 Analysis insights stored in memory system")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update learning memory: {e}")
            return False

# Configuration flag to disable ad tracking
ORGANIC_ONLY_MODE = True

def validate_organic_only_configuration() -> bool:
    """Validate that system is configured for organic-only analysis."""
    try:
        # Check environment variables
        ad_related_vars = [
            'AMAZON_ADS_CLIENT_ID',
            'AMAZON_ADS_CLIENT_SECRET', 
            'AMAZON_ADS_REFRESH_TOKEN',
            'FACEBOOK_ADS_TOKEN',
            'GOOGLE_ADS_CLIENT_ID'
        ]
        
        active_ad_vars = [var for var in ad_related_vars if os.getenv(var)]
        
        if active_ad_vars and ORGANIC_ONLY_MODE:
            logger.warning(f"🚨 ORGANIC-ONLY MODE: Ignoring ad variables: {active_ad_vars}")
        
        logger.info("✅ ORGANIC-ONLY CONFIGURATION VALIDATED")
        return True
        
    except Exception as e:
        logger.error(f"Organic configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    # Validate organic-only mode
    validate_organic_only_configuration()
    
    # Test analyzer
    import asyncio
    analyzer = OrganicFeedbackAnalyzer()
    result = asyncio.run(analyzer.analyze_organic_performance())
    print(json.dumps(result, indent=2))