"""
Market Research Agent

This agent conducts comprehensive market research and competitive analysis including:
- Competitor book analysis
- Niche trend identification
- Keyword research and optimization
- Pricing strategy analysis
- Market opportunity assessment
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import aiohttp

from .agent_types import AgentCapability
from .base_agent import BaseAgent
from .task_system import Task, TaskResult, TaskStatus


class MarketResearchAgent(BaseAgent):
    """Agent responsible for market research and competitive analysis"""

    def __init__(
        self,
        data_storage_path: str = "books/market_research",
        research_interval: int = 86400,
    ):  # 24 hours default
        super().__init__(
            agent_type="market_research",
            capabilities=[
                AgentCapability.MARKET_RESEARCH,
                AgentCapability.MARKET_ANALYTICS,
                AgentCapability.BUSINESS_INTELLIGENCE,
                AgentCapability.SEO_OPTIMIZATION,
            ],
            max_concurrent_tasks=3,
            heartbeat_interval=600,  # 10 minutes
        )

        self.data_storage_path = Path(data_storage_path)
        self.research_interval = research_interval
        self.market_data: Dict[str, Any] = {}
        self.competitor_data: Dict[str, Any] = {}
        self.trend_data: Dict[str, Any] = {}

        # Create storage directory
        self.data_storage_path.mkdir(parents=True, exist_ok=True)

    async def _initialize(self) -> None:
        """Initialize the market research agent"""
        self.logger.info("Initializing Market Research Agent")

        # Load existing research data
        await self._load_research_data()

        # Start periodic research updates
        asyncio.create_task(self._periodic_research_update())

        self.logger.info("Market Research Agent initialized")

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        await self._save_research_data()

    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute market research task"""
        try:
            task_type = task.parameters.get("type")

            if task_type == "analyze_competitors":
                return await self._analyze_competitors(task)
            elif task_type == "research_niche":
                return await self._research_niche(task)
            elif task_type == "keyword_research":
                return await self._keyword_research(task)
            elif task_type == "pricing_analysis":
                return await self._pricing_analysis(task)
            elif task_type == "market_opportunities":
                return await self._identify_market_opportunities(task)
            elif task_type == "trend_analysis":
                return await self._trend_analysis(task)
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Unknown task type: {task_type}",
                )

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return TaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED, error=str(e)
            )

    async def _analyze_competitors(self, task: Task) -> TaskResult:
        """Analyze competitors in a specific niche"""
        niche = task.parameters.get("niche")
        keywords = task.parameters.get("keywords", [])
        task.parameters.get("depth", "standard")  # standard, deep

        if not niche:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="Niche is required for competitor analysis",
            )

        try:
            # Search for competitor books
            competitor_books = await self._search_competitor_books(niche, keywords)

            # Analyze each competitor
            detailed_analysis = []
            for book in competitor_books[:20]:  # Limit to top 20
                analysis = await self._analyze_single_competitor(book)
                detailed_analysis.append(analysis)

                # Rate limiting
                await asyncio.sleep(2)

            # Generate competitive landscape report
            competitive_landscape = await self._generate_competitive_landscape(
                detailed_analysis
            )

            # Store results
            results = {
                "niche": niche,
                "keywords": keywords,
                "analysis_date": datetime.now().isoformat(),
                "competitor_count": len(detailed_analysis),
                "competitive_landscape": competitive_landscape,
                "detailed_analysis": detailed_analysis,
                "recommendations": await self._generate_competitive_recommendations(
                    competitive_landscape
                ),
            }

            # Save to file
            filename = f"competitor_analysis_{niche.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = self.data_storage_path / filename
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output={"analysis": results, "file_path": str(filepath)},
            )

        except Exception as e:
            return TaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED, error=str(e)
            )

    async def _search_competitor_books(
        self, niche: str, keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Search for competitor books on Amazon"""
        search_terms = [niche] + keywords
        competitor_books = []


        for search_term in search_terms[:5]:  # Limit searches
            try:
                # Amazon search URL
                (
                    f"https://www.amazon.com/s?k={quote_plus(search_term)}&i=stripbooks"
                )

                # Placeholder - should use official Amazon API
                self.logger.warning(
                    f"Amazon search disabled for '{search_term}' - implement official API integration"
                )
                await asyncio.sleep(1)  # Simulated delay

            except Exception as e:
                self.logger.error(f"Error searching for '{search_term}': {e}")

        # Remove duplicates and limit results
        seen_asins = set()
        unique_books = []
        for book in competitor_books:
            if book.get("asin") and book["asin"] not in seen_asins:
                seen_asins.add(book["asin"])
                unique_books.append(book)

        return unique_books[:50]  # Limit to top 50

    def _extract_books_from_search(self, data: Any) -> List[Dict[str, Any]]:
        """Extract book information from API response"""
        # Placeholder for API-based extraction
        self.logger.warning(
            "Book extraction disabled - implement official API integration"
        )
        return []

    async def _analyze_single_competitor(self, book: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single competitor book in detail"""
        asin = book.get("asin")
        if not asin:
            return book

        try:
            # Get detailed book information
            detailed_info = await self._get_detailed_book_info(asin)

            # Merge with basic info
            analysis = {**book, **detailed_info}

            # Add competitive analysis
            analysis["competitive_analysis"] = {
                "strengths": await self._identify_book_strengths(analysis),
                "weaknesses": await self._identify_book_weaknesses(analysis),
                "opportunities": await self._identify_improvement_opportunities(
                    analysis
                ),
                "threat_level": await self._assess_threat_level(analysis),
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing competitor {asin}: {e}")
            return {**book, "analysis_error": str(e)}

    async def _get_detailed_book_info(self, asin: str) -> Dict[str, Any]:
        """Get detailed information about a book"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }


        try:
            async with aiohttp.ClientSession(headers=headers):
                # Placeholder - should use official Amazon API
                self.logger.warning(
                    f"Product detail fetch disabled for {asin} - implement official API integration"
                )
                return {
                    "error": "Web scraping disabled - use Amazon Product Advertising API instead",
                    "description": None,
                    "page_count": None,
                    "publication_date": None,
                    "publisher": None,
                    "bsr_info": {},
                    "categories": [],
                    "keywords_found": [],
                }

        except Exception as e:
            return {"error": str(e)}

    def _extract_description(self, data: Dict) -> Optional[str]:
        """Extract book description from API response"""
        # Placeholder for API-based extraction
        return data.get("description")

    def _extract_page_count(self, data: Dict) -> Optional[int]:
        """Extract page count from API response"""
        # Placeholder for API-based extraction
        return data.get("page_count")

    def _extract_publication_date(self, data: Dict) -> Optional[str]:
        """Extract publication date from API response"""
        # Placeholder for API-based extraction
        return data.get("publication_date")

    def _extract_publisher(self, data: Dict) -> Optional[str]:
        """Extract publisher information from API response"""
        # Placeholder for API-based extraction
        return data.get("publisher")

    def _extract_bsr_info(self, data: Dict) -> Dict[str, Any]:
        """Extract Best Sellers Rank information from API response"""
        # Placeholder for API-based extraction
        return data.get("bsr_info", {"overall_rank": None, "category_ranks": []})

    async def _identify_book_strengths(self, book_data: Dict[str, Any]) -> List[str]:
        """Identify competitive strengths of a book"""
        strengths = []

        # High rating
        if book_data.get("rating", 0) >= 4.5:
            strengths.append(f"Excellent rating ({book_data['rating']} stars)")

        # Many reviews
        if book_data.get("review_count", 0) >= 100:
            strengths.append(
                f"Strong review count ({book_data['review_count']} reviews)"
            )

        # Good BSR
        bsr_info = book_data.get("bsr_info", {})
        if bsr_info.get("overall_rank"):
            try:
                rank = int(bsr_info["overall_rank"])
                if rank <= 100000:
                    strengths.append(f"Strong BSR (#{rank:,})")
            except:
                pass

        # Established publisher
        publisher = book_data.get("publisher", "")
        if publisher and "amazon" not in publisher.lower():
            strengths.append(f"Established publisher ({publisher})")

        return strengths

    async def _identify_book_weaknesses(self, book_data: Dict[str, Any]) -> List[str]:
        """Identify competitive weaknesses of a book"""
        weaknesses = []

        # Low rating
        if book_data.get("rating", 5) < 3.5:
            weaknesses.append(
                f"Below average rating ({book_data['rating']} stars)")

        # Few reviews
        if book_data.get("review_count", 0) < 10:
            weaknesses.append(
                f"Limited reviews ({book_data['review_count']} reviews)")

        # High price for niche
        price_str = book_data.get("price", "")
        if price_str:
            try:
                price = float(re.sub(r"[^\d.]", "", price_str))
                if price > 20:  # Arbitrary threshold
                    weaknesses.append(f"High price point (${price})")
            except:
                pass

        # Old publication
        pub_date = book_data.get("publication_date", "")
        if pub_date:
            try:
                # Simple year extraction
                year_match = re.search(r"(\d{4})", pub_date)
                if year_match:
                    year = int(year_match.group(1))
                    if year < 2020:
                        weaknesses.append(f"Older publication ({year})")
            except:
                pass

        return weaknesses

    async def _research_niche(self, task: Task) -> TaskResult:
        """Research a specific niche for opportunities"""
        niche = task.parameters.get("niche")
        task.parameters.get("depth", "standard")

        if not niche:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="Niche is required for research",
            )

        try:
            # Comprehensive niche research
            research_results = {
                "niche": niche,
                "research_date": datetime.now().isoformat(),
                "market_size": await self._estimate_market_size(niche),
                "competition_analysis": await self._analyze_niche_competition(niche),
                "keyword_opportunities": await self._find_keyword_opportunities(niche),
                "pricing_landscape": await self._analyze_niche_pricing(niche),
                "content_gaps": await self._identify_content_gaps(niche),
                "recommendations": await self._generate_niche_recommendations(niche),
            }

            # Save results
            filename = f"niche_research_{niche.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = self.data_storage_path / filename
            with open(filepath, "w") as f:
                json.dump(research_results, f, indent=2)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output={"research": research_results,
                        "file_path": str(filepath)},
            )

        except Exception as e:
            return TaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED, error=str(e)
            )

    async def _estimate_market_size(self, niche: str) -> Dict[str, Any]:
        """Estimate market size for a niche"""
        try:
            # Search for books in the niche
            competitor_books = await self._search_competitor_books(niche, [])

            # Calculate market metrics
            total_books = len(competitor_books)
            books_with_reviews = sum(
                1 for book in competitor_books if book.get("review_count", 0) > 0
            )
            avg_reviews = sum(
                book.get("review_count", 0) for book in competitor_books
            ) / max(total_books, 1)
            avg_rating = sum(
                book.get("rating", 0) for book in competitor_books if book.get("rating")
            ) / max(books_with_reviews, 1)

            return {
                "total_books_found": total_books,
                "books_with_reviews": books_with_reviews,
                "average_reviews": round(avg_reviews, 1),
                "average_rating": round(avg_rating, 2),
                "market_saturation": self._calculate_market_saturation(
                    total_books, avg_reviews
                ),
                "estimated_monthly_searches": self._estimate_search_volume(niche),
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_market_saturation(self, total_books: int, avg_reviews: float) -> str:
        """Calculate market saturation level"""
        if total_books < 50:
            return "low"
        elif total_books < 200:
            return "moderate"
        elif total_books < 500:
            return "high"
        else:
            return "very_high"

    def _estimate_search_volume(self, niche: str) -> int:
        """Estimate monthly search volume (placeholder)"""
        # This would typically use Google Keyword Planner API or similar
        # For now, return a conservative estimate based on niche complexity
        word_count = len(niche.split())
        if word_count <= 2:
            return 10000  # Broad terms
        elif word_count <= 4:
            return 5000  # Specific terms
        else:
            return 1000  # Very specific terms

    async def _periodic_research_update(self) -> None:
        """Periodic market research updates"""
        while self.status.value != "shutdown":
            try:
                self.logger.info("Running periodic market research update")

                # Update trend data
                await self._update_trend_data()

                # Save research data
                await self._save_research_data()

                # Wait for next update
                await asyncio.sleep(self.research_interval)

            except Exception as e:
                self.logger.error(f"Error in periodic research update: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def _update_trend_data(self) -> None:
        """Update trend data and market insights"""
        # Placeholder for trend analysis
        # This would typically integrate with Google Trends API or similar
        self.trend_data = {
            "last_updated": datetime.now().isoformat(),
            "trending_topics": [],
            "seasonal_patterns": {},
            "emerging_niches": [],
        }

    async def _load_research_data(self) -> None:
        """Load existing research data"""
        try:
            # Load market data
            market_file = self.data_storage_path / "market_data.json"
            if market_file.exists():
                with open(market_file, "r") as f:
                    self.market_data = json.load(f)

            # Load competitor data
            competitor_file = self.data_storage_path / "competitor_data.json"
            if competitor_file.exists():
                with open(competitor_file, "r") as f:
                    self.competitor_data = json.load(f)

            self.logger.info("Loaded existing research data")

        except Exception as e:
            self.logger.error(f"Error loading research data: {e}")

    async def _save_research_data(self) -> None:
        """Save research data to files"""
        try:
            # Save market data
            market_file = self.data_storage_path / "market_data.json"
            with open(market_file, "w") as f:
                json.dump(self.market_data, f, indent=2)

            # Save competitor data
            competitor_file = self.data_storage_path / "competitor_data.json"
            with open(competitor_file, "w") as f:
                json.dump(self.competitor_data, f, indent=2)

            # Save trend data
            trend_file = self.data_storage_path / "trend_data.json"
            with open(trend_file, "w") as f:
                json.dump(self.trend_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving research data: {e}")

    async def _generate_competitive_landscape(
        self, detailed_analysis: List[Dict]
    ) -> Dict[str, Any]:
        """Generate competitive landscape overview"""
        if not detailed_analysis:
            return {"error": "No competitor data available"}

        # Calculate competitive metrics
        ratings = [
            book.get("rating", 0) for book in detailed_analysis if book.get("rating")
        ]
        review_counts = [
            book.get("review_count", 0)
            for book in detailed_analysis
            if book.get("review_count")
        ]

        return {
            "total_competitors": len(detailed_analysis),
            "average_rating": sum(ratings) / len(ratings) if ratings else 0,
            "average_reviews": (
                sum(review_counts) / len(review_counts) if review_counts else 0
            ),
            "top_performers": sorted(
                detailed_analysis,
                key=lambda x: x.get("rating", 0) * x.get("review_count", 0),
                reverse=True,
            )[:5],
            "market_gaps": await self._identify_market_gaps(detailed_analysis),
            "competitive_intensity": self._assess_competitive_intensity(
                detailed_analysis
            ),
        }

    async def _identify_market_gaps(self, competitor_analysis: List[Dict]) -> List[str]:
        """Identify gaps in the competitive landscape"""
        gaps = []

        # Analyze common weaknesses
        low_rated_books = sum(
            1 for book in competitor_analysis if book.get("rating", 5) < 4.0
        )
        if low_rated_books > len(competitor_analysis) * 0.3:
            gaps.append("Quality gap - many competitors have low ratings")

        # Analyze pricing gaps
        prices = []
        for book in competitor_analysis:
            price_str = book.get("price", "")
            if price_str:
                try:
                    price = float(re.sub(r"[^\d.]", "", price_str))
                    prices.append(price)
                except:
                    continue

        if prices:
            avg_price = sum(prices) / len(prices)
            if avg_price > 15:
                gaps.append(
                    "Price gap - opportunity for more affordable options")
            elif avg_price < 5:
                gaps.append(
                    "Premium gap - opportunity for higher-quality offerings")

        return gaps

    def _assess_competitive_intensity(self, competitor_analysis: List[Dict]) -> str:
        """Assess the intensity of competition"""
        if len(competitor_analysis) < 20:
            return "low"
        elif len(competitor_analysis) < 50:
            return "moderate"
        elif len(competitor_analysis) < 100:
            return "high"
        else:
            return "very_high"
