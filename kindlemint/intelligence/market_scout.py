"""
KDP Market Intelligence System - Niche Scout Agent
Identifies profitable micro-niches with high demand and low competition.

BUSINESS IMPACT: Transforms blind publishing into intelligent market hunting
STRATEGY: BSR < 100,000 + Reviews < 100 = Profit Opportunity
"""
import json
import logging
import os
import asyncio
import aiohttp
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import quote_plus
import time

logger = logging.getLogger(__name__)

@dataclass
class NicheOpportunity:
    """Data structure for a profitable niche opportunity."""
    micro_niche: str
    broad_category: str
    demand_score: int  # 1-100 based on BSR analysis
    competition_score: int  # 1-100 based on review analysis
    profit_potential: float  # Estimated daily revenue
    keywords: List[str]
    top_competitors: List[Dict[str, Any]]
    series_opportunities: List[str]
    brand_potential: str
    confidence_score: float  # Overall opportunity confidence

@dataclass
class BookAnalysis:
    """Analysis of a specific book in the market."""
    asin: str
    title: str
    bsr: int
    review_count: int
    rating: float
    price: float
    estimated_monthly_sales: int
    niche_keywords: List[str]

class KDPMarketScout:
    """Intelligent market scouting system for profitable micro-niches."""
    
    def __init__(self):
        """Initialize market scout with intelligence capabilities."""
        self.session = None
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Market intelligence thresholds
        self.target_bsr_threshold = 100000  # Books with BSR < 100k have good demand
        self.low_competition_reviews = 100  # Books with < 100 reviews = low competition
        self.min_price = 2.99  # Minimum profitable price point
        
        # Micro-niche categories to explore
        self.profitable_categories = [
            "Activity Books",
            "Coloring Books", 
            "Puzzle Books",
            "Journals & Planners",
            "Educational Workbooks",
            "Recipe Books",
            "Self-Help Guides",
            "Children's Books"
        ]
    
    async def discover_profitable_micro_niches(self, max_niches: int = 5) -> List[NicheOpportunity]:
        """
        Discover profitable micro-niches using market intelligence.
        
        Args:
            max_niches: Maximum number of opportunities to return
            
        Returns:
            List of ranked niche opportunities
        """
        try:
            logger.info("🔍 MARKET INTELLIGENCE ACTIVATED - Hunting profitable micro-niches")
            
            opportunities = []
            
            # Initialize HTTP session
            async with aiohttp.ClientSession() as session:
                self.session = session
                
                # Scan each broad category for micro-niche opportunities
                for category in self.profitable_categories:
                    try:
                        category_opportunities = await self._analyze_category_for_niches(category)
                        opportunities.extend(category_opportunities)
                        
                        # Respectful delay between category scans
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.warning(f"Category analysis failed for {category}: {e}")
                        continue
                
                # Rank opportunities by profit potential
                ranked_opportunities = self._rank_opportunities(opportunities)
                
                # Return top opportunities
                top_opportunities = ranked_opportunities[:max_niches]
                
                logger.info(f"✅ Market intelligence complete: {len(top_opportunities)} profitable niches identified")
                
                return top_opportunities
                
        except Exception as e:
            logger.error(f"❌ Market discovery failed: {str(e)}")
            return []
    
    async def _analyze_category_for_niches(self, category: str) -> List[NicheOpportunity]:
        """Analyze a broad category to find profitable micro-niches."""
        try:
            logger.info(f"🎯 Analyzing category: {category}")
            
            # Generate micro-niche variations using AI
            micro_niches = await self._generate_micro_niche_variations(category)
            
            opportunities = []
            
            for micro_niche in micro_niches:
                try:
                    # Analyze market data for this micro-niche
                    market_data = await self._analyze_micro_niche_market(micro_niche, category)
                    
                    if market_data and self._is_profitable_opportunity(market_data):
                        opportunity = self._create_niche_opportunity(micro_niche, category, market_data)
                        opportunities.append(opportunity)
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Micro-niche analysis failed for {micro_niche}: {e}")
                    continue
            
            return opportunities
            
        except Exception as e:
            logger.warning(f"Category analysis failed: {e}")
            return []
    
    async def _generate_micro_niche_variations(self, broad_category: str) -> List[str]:
        """Generate specific micro-niche variations using AI."""
        try:
            from openai import OpenAI
            
            if not self.openai_api_key:
                return self._fallback_micro_niches(broad_category)
            
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Generate 8 highly specific micro-niches for the broad category: {broad_category}
            
            Requirements for each micro-niche:
            1. HYPER-SPECIFIC target audience (age, interest, demographic)
            2. Specific content type or theme
            3. Searchable on Amazon KDP
            4. Not oversaturated (avoid "general" terms)
            
            Examples of good micro-niches:
            - "Sudoku puzzle books for adults with visual impairments"
            - "Dinosaur coloring books for boys aged 4-8"
            - "Anxiety management journals for college students"
            - "Keto recipe books for busy working moms"
            
            Generate for {broad_category}:
            
            Format as JSON array of strings:
            ["micro-niche 1", "micro-niche 2", ...]
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            
            micro_niches = json.loads(content)
            
            logger.info(f"Generated {len(micro_niches)} micro-niches for {broad_category}")
            return micro_niches
            
        except Exception as e:
            logger.warning(f"AI micro-niche generation failed: {e}")
            return self._fallback_micro_niches(broad_category)
    
    def _fallback_micro_niches(self, broad_category: str) -> List[str]:
        """Fallback micro-niches if AI generation fails."""
        fallback_map = {
            "Activity Books": [
                "Brain teaser activity books for seniors",
                "STEM activity books for homeschooled kids",
                "Mindfulness activity books for anxious adults"
            ],
            "Coloring Books": [
                "Mandala coloring books for stress relief",
                "Animal coloring books for toddlers",
                "Inspirational quote coloring books for women"
            ],
            "Puzzle Books": [
                "Large print crossword puzzles for seniors",
                "Logic puzzles for gifted children",
                "Word search books for English learners"
            ],
            "Journals & Planners": [
                "Gratitude journals for new mothers",
                "Fitness tracking planners for beginners",
                "Travel journals for solo female travelers"
            ]
        }
        
        return fallback_map.get(broad_category, [f"Specific {broad_category.lower()} for niche audience"])
    
    async def _analyze_micro_niche_market(self, micro_niche: str, category: str) -> Optional[Dict[str, Any]]:
        """Analyze market data for a specific micro-niche."""
        try:
            # Simulate Amazon search analysis
            # In real implementation, this would use Amazon Product Advertising API
            # or web scraping (with proper rate limiting and compliance)
            
            # Generate realistic market data based on niche characteristics
            market_data = await self._simulate_market_analysis(micro_niche, category)
            
            return market_data
            
        except Exception as e:
            logger.warning(f"Market analysis failed for {micro_niche}: {e}")
            return None
    
    async def _simulate_market_analysis(self, micro_niche: str, category: str) -> Dict[str, Any]:
        """Simulate market analysis for development purposes."""
        try:
            # Generate realistic market metrics
            import random
            
            # Determine niche characteristics
            specificity_score = len(micro_niche.split()) / 10  # More words = more specific
            
            # High specificity usually means lower competition but also lower demand
            base_competition = max(20, 100 - (specificity_score * 30))
            base_demand = max(30, 80 - (specificity_score * 20))
            
            # Add some randomness
            competition_score = random.randint(int(base_competition - 20), int(base_competition + 20))
            demand_score = random.randint(int(base_demand - 15), int(base_demand + 15))
            
            # Generate top competitors
            competitors = []
            for i in range(3):
                bsr = random.randint(50000, 200000) if demand_score > 50 else random.randint(100000, 500000)
                reviews = random.randint(5, competition_score)
                price = round(random.uniform(2.99, 9.99), 2)
                
                competitors.append({
                    'asin': f'B{random.randint(100000000, 999999999)}',
                    'title': f'{micro_niche.title()} Book {i+1}',
                    'bsr': bsr,
                    'review_count': reviews,
                    'rating': round(random.uniform(3.8, 4.7), 1),
                    'price': price,
                    'estimated_monthly_sales': max(1, int(500000 / bsr))
                })
            
            # Extract keywords
            keywords = self._extract_keywords_from_niche(micro_niche)
            
            return {
                'micro_niche': micro_niche,
                'category': category,
                'demand_score': demand_score,
                'competition_score': competition_score,
                'top_competitors': competitors,
                'keywords': keywords,
                'avg_price': sum(c['price'] for c in competitors) / len(competitors),
                'avg_reviews': sum(c['review_count'] for c in competitors) / len(competitors),
                'avg_bsr': sum(c['bsr'] for c in competitors) / len(competitors)
            }
            
        except Exception as e:
            logger.error(f"Market simulation failed: {e}")
            return {}
    
    def _extract_keywords_from_niche(self, micro_niche: str) -> List[str]:
        """Extract relevant keywords from micro-niche description."""
        # Remove common words and extract key terms
        common_words = {'for', 'with', 'and', 'the', 'of', 'in', 'to', 'a', 'an', 'books', 'book'}
        words = micro_niche.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        return keywords[:7]  # Limit to 7 keywords for KDP
    
    def _is_profitable_opportunity(self, market_data: Dict[str, Any]) -> bool:
        """Determine if a market opportunity is profitable."""
        try:
            avg_bsr = market_data.get('avg_bsr', 500000)
            avg_reviews = market_data.get('avg_reviews', 200)
            avg_price = market_data.get('avg_price', 2.99)
            demand_score = market_data.get('demand_score', 0)
            competition_score = market_data.get('competition_score', 100)
            
            # Profitable criteria:
            # 1. Good demand (BSR < 100k average)
            # 2. Low competition (< 100 reviews average)
            # 3. Decent price point (> $2.99)
            # 4. Good demand/competition ratio
            
            good_demand = avg_bsr < self.target_bsr_threshold
            low_competition = avg_reviews < self.low_competition_reviews
            good_price = avg_price >= self.min_price
            good_ratio = demand_score > competition_score
            
            return good_demand and low_competition and good_price and good_ratio
            
        except Exception as e:
            logger.warning(f"Profitability analysis failed: {e}")
            return False
    
    def _create_niche_opportunity(self, micro_niche: str, category: str, market_data: Dict[str, Any]) -> NicheOpportunity:
        """Create a structured niche opportunity from market data."""
        try:
            # Calculate profit potential (daily revenue estimate)
            avg_price = market_data.get('avg_price', 2.99)
            demand_score = market_data.get('demand_score', 50)
            competition_score = market_data.get('competition_score', 50)
            
            # Simple profit estimation: (demand - competition) * price factor
            daily_sales_estimate = max(1, (demand_score - competition_score) / 10)
            profit_per_sale = avg_price * 0.35  # KDP royalty rate
            daily_profit_estimate = daily_sales_estimate * profit_per_sale
            
            # Generate series opportunities
            series_opportunities = self._generate_series_ideas(micro_niche)
            
            # Generate brand potential
            brand_potential = self._analyze_brand_potential(micro_niche)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(market_data)
            
            return NicheOpportunity(
                micro_niche=micro_niche,
                broad_category=category,
                demand_score=market_data.get('demand_score', 50),
                competition_score=market_data.get('competition_score', 50),
                profit_potential=round(daily_profit_estimate, 2),
                keywords=market_data.get('keywords', []),
                top_competitors=market_data.get('top_competitors', []),
                series_opportunities=series_opportunities,
                brand_potential=brand_potential,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Opportunity creation failed: {e}")
            # Return basic opportunity
            return NicheOpportunity(
                micro_niche=micro_niche,
                broad_category=category,
                demand_score=50,
                competition_score=50,
                profit_potential=5.0,
                keywords=self._extract_keywords_from_niche(micro_niche),
                top_competitors=[],
                series_opportunities=[f"{micro_niche} Volume 1", f"{micro_niche} Volume 2"],
                brand_potential=f"Brand focused on {micro_niche}",
                confidence_score=70.0
            )
    
    def _generate_series_ideas(self, micro_niche: str) -> List[str]:
        """Generate series ideas for the micro-niche."""
        base_terms = [
            "Volume 1", "Volume 2", "Volume 3",
            "Beginner Edition", "Advanced Edition",
            "Part 1", "Part 2",
            "Easy Level", "Medium Level", "Hard Level"
        ]
        
        series_ideas = [f"{micro_niche} - {term}" for term in base_terms[:5]]
        return series_ideas
    
    def _analyze_brand_potential(self, micro_niche: str) -> str:
        """Analyze brand building potential for the niche."""
        # Extract key themes for brand building
        if "coloring" in micro_niche.lower():
            return f"Brand: '{micro_niche.split()[0].title()} Art Studio' - Build loyal following through quality designs"
        elif "puzzle" in micro_niche.lower():
            return f"Brand: '{micro_niche.split()[0].title()} Brain Games' - Focus on cognitive benefits"
        elif "journal" in micro_niche.lower():
            return f"Brand: '{micro_niche.split()[0].title()} Wellness' - Build community around personal growth"
        else:
            return f"Brand opportunity around {micro_niche.split()[0]} theme with recurring customers"
    
    def _calculate_confidence_score(self, market_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the opportunity."""
        try:
            demand_score = market_data.get('demand_score', 50)
            competition_score = market_data.get('competition_score', 50)
            avg_bsr = market_data.get('avg_bsr', 200000)
            avg_reviews = market_data.get('avg_reviews', 100)
            
            # Higher confidence for:
            # - High demand, low competition
            # - Good BSR performance
            # - Low review counts (less competition)
            
            demand_factor = demand_score / 100
            competition_factor = (100 - competition_score) / 100
            bsr_factor = min(1.0, self.target_bsr_threshold / avg_bsr)
            review_factor = min(1.0, self.low_competition_reviews / avg_reviews)
            
            confidence = (demand_factor + competition_factor + bsr_factor + review_factor) / 4 * 100
            
            return round(min(95.0, max(30.0, confidence)), 1)
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 70.0
    
    def _rank_opportunities(self, opportunities: List[NicheOpportunity]) -> List[NicheOpportunity]:
        """Rank opportunities by profit potential and confidence."""
        try:
            # Sort by profit potential * confidence score
            ranked = sorted(
                opportunities,
                key=lambda opp: opp.profit_potential * (opp.confidence_score / 100),
                reverse=True
            )
            
            return ranked
            
        except Exception as e:
            logger.error(f"Opportunity ranking failed: {e}")
            return opportunities
    
    async def get_best_opportunity_for_immediate_action(self) -> Optional[NicheOpportunity]:
        """Get the single best opportunity for immediate book creation."""
        try:
            opportunities = await self.discover_profitable_micro_niches(max_niches=1)
            
            if opportunities:
                best_opportunity = opportunities[0]
                logger.info(f"🎯 BEST OPPORTUNITY IDENTIFIED: {best_opportunity.micro_niche}")
                logger.info(f"   Profit Potential: ${best_opportunity.profit_potential}/day")
                logger.info(f"   Confidence: {best_opportunity.confidence_score}%")
                return best_opportunity
            
            return None
            
        except Exception as e:
            logger.error(f"Best opportunity identification failed: {e}")
            return None

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for market intelligence scouting.
    """
    try:
        logger.info("🔍 MARKET INTELLIGENCE SYSTEM ACTIVATED")
        
        # Initialize market scout
        scout = KDPMarketScout()
        
        # Discover profitable opportunities
        max_niches = event.get('max_niches', 3)
        opportunities = asyncio.run(scout.discover_profitable_micro_niches(max_niches))
        
        # Format results
        results = []
        for opp in opportunities:
            results.append({
                'micro_niche': opp.micro_niche,
                'category': opp.broad_category,
                'profit_potential_daily': opp.profit_potential,
                'confidence_score': opp.confidence_score,
                'keywords': opp.keywords,
                'series_opportunities': opp.series_opportunities,
                'brand_potential': opp.brand_potential,
                'demand_score': opp.demand_score,
                'competition_score': opp.competition_score
            })
        
        logger.info(f"✅ Market intelligence complete: {len(results)} opportunities found")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'opportunities': results,
                'total_opportunities': len(results),
                'best_opportunity': results[0] if results else None
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Market intelligence failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Market intelligence failed: {str(e)}'
            })
        }

if __name__ == "__main__":
    # Test market intelligence
    import asyncio
    
    scout = KDPMarketScout()
    opportunities = asyncio.run(scout.discover_profitable_micro_niches(max_niches=3))
    
    for opp in opportunities:
        print(f"\n🎯 OPPORTUNITY: {opp.micro_niche}")
        print(f"   Profit Potential: ${opp.profit_potential}/day")
        print(f"   Confidence: {opp.confidence_score}%")
        print(f"   Keywords: {', '.join(opp.keywords)}")
        print(f"   Series Ideas: {opp.series_opportunities[0]}, {opp.series_opportunities[1]}")
        print(f"   Brand: {opp.brand_potential}")