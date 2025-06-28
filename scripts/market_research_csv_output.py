#!/usr/bin/env python3
"""
Market Research with CSV Output - Proper Schema Implementation
"""

import csv
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from security import safe_requests

# Import Sentry if available
try:
    # Try to import from the scripts directory
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from sentry_config import add_breadcrumb, capture_kdp_error, init_sentry

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

    def init_sentry(*args, **kwargs):
        return False

    def add_breadcrumb(*args, **kwargs):
        pass

    def capture_kdp_error(*args, **kwargs):
        pass


@dataclass
class MarketDataPoint:
    """Schema for market research data"""

    date: str
    keyword: str
    amazon_rank: int
    avg_price: float
    est_sales: int
    competition_level: str = "medium"
    reviews_avg: float = 0.0


class MarketResearchEngine:
    """Enhanced market research with proper CSV output"""

    def __init__(self):
        self.output_dir = Path("research") / datetime.now().strftime("%Y-%m-%d")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Sentry if available
        if SENTRY_AVAILABLE:
            init_sentry("market-research-csv")

        # Default keywords if none provided
        self.default_keywords = [
            "crossword puzzle books large print",
            "sudoku books for adults",
            "word search puzzle books",
            "brain games for seniors",
            "logic puzzles adults",
            "cryptogram puzzle books",
            "kakuro puzzle books",
            "maze books for adults",
            "brain teasers for adults",
            "activity books for seniors",
        ]

    def fetch_serpapi_data(self, keyword: str) -> List[Dict]:
        """Fetch Amazon product data via SerpAPI"""
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            print(f"⚠️ SERPAPI_API_KEY not set, using mock data for: {keyword}")
            return self._generate_mock_data(keyword)

        try:
            params = {
                "engine": "amazon",
                "amazon_domain": "amazon.com",
                "k": keyword,
                "api_key": api_key,
                "num": 20,  # Get top 20 results
            }

            add_breadcrumb(f"Fetching SerpAPI data for: {keyword}", category="api")
            response = safe_requests.get(
                "https://serpapi.com/search", params=params, timeout=30
            )

            # Rate limiting
            time.sleep(1)  # Be nice to the API

            if response.status_code == 429:
                print("⚠️ Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self.fetch_serpapi_data(keyword)  # Retry

            response.raise_for_status()
            data = response.json()

            return data.get("organic_results", [])

        except Exception as e:
            capture_kdp_error(e, {"keyword": keyword, "api": "serpapi"})
            print(f"❌ Error fetching data for '{keyword}': {e}")
            return self._generate_mock_data(keyword)

    def _generate_mock_data(self, keyword: str) -> List[Dict]:
        """Generate realistic mock data for testing"""
        import random

        mock_products = []
        for i in range(10):
            mock_products.append(
                {
                    "position": i + 1,
                    "title": f"Mock {keyword} Book #{i+1}",
                    "price": f"${random.uniform(6.99, 24.99):.2f}",
                    "rating": random.uniform(3.5, 5.0),
                    "reviews": random.randint(10, 5000),
                }
            )
        return mock_products

    def calculate_estimated_sales(self, rank: int, reviews: int) -> int:
        """Estimate monthly sales based on rank and reviews"""
        # Simplified estimation formula
        # Real formula would use more sophisticated calculations
        if rank <= 10:
            base_sales = 1000
        elif rank <= 50:
            base_sales = 500
        elif rank <= 100:
            base_sales = 200
        else:
            base_sales = 50

        # Adjust based on review velocity (rough estimate)
        review_factor = min(reviews / 100, 2.0)  # Cap at 2x

        return int(base_sales * review_factor)

    def process_keyword(self, keyword: str) -> List[MarketDataPoint]:
        """Process a single keyword and return market data points"""
        products = self.fetch_serpapi_data(keyword)
        data_points = []

        for idx, product in enumerate(products[:10]):  # Top 10 only
            try:
                # Extract price
                price_str = product.get("price", "$0")
                price = float(price_str.replace("$", "").replace(",", "").split("-")[0])

                # Extract reviews
                reviews = int(product.get("reviews", 0))
                rating = float(product.get("rating", 0))

                # Calculate rank and sales
                rank = idx + 1  # Position in search results
                est_sales = self.calculate_estimated_sales(rank, reviews)

                # Determine competition level
                if reviews > 1000:
                    competition = "high"
                elif reviews > 100:
                    competition = "medium"
                else:
                    competition = "low"

                data_point = MarketDataPoint(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    keyword=keyword,
                    amazon_rank=rank,
                    avg_price=price,
                    est_sales=est_sales,
                    competition_level=competition,
                    reviews_avg=rating,
                )

                data_points.append(data_point)

            except Exception as e:
                print(f"⚠️ Error processing product: {e}")
                continue

        return data_points

    def save_to_csv(
        self, data_points: List[MarketDataPoint], filename: str = "market_analysis.csv"
    ):
        """Save data points to CSV with proper schema"""
        csv_path = self.output_dir / filename

        # Define CSV schema
        fieldnames = [
            "date",
            "keyword",
            "amazon_rank",
            "avg_price",
            "est_sales",
            "competition_level",
            "reviews_avg",
        ]

        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for point in data_points:
                writer.writerow(asdict(point))

        print(f"✅ Saved {len(data_points)} data points to: {csv_path}")
        return csv_path

    def run_research(self, keywords: Optional[List[str]] = None) -> Path:
        """Run complete market research cycle"""
        if not keywords:
            keywords = self.default_keywords

        print(f"🔍 Starting market research for {len(keywords)} keywords...")
        add_breadcrumb(
            "Market research started",
            category="research",
            data={"keyword_count": len(keywords)},
        )

        all_data_points = []

        for idx, keyword in enumerate(keywords):
            print(f"📊 [{idx+1}/{len(keywords)}] Researching: {keyword}")
            data_points = self.process_keyword(keyword)
            all_data_points.extend(data_points)

            # Progress tracking
            if (idx + 1) % 5 == 0:
                print(f"⏳ Progress: {idx+1}/{len(keywords)} keywords processed")

        # Save to CSV
        csv_path = self.save_to_csv(all_data_points)

        # Generate summary
        self.generate_summary(all_data_points)

        print(f"✅ Market research complete! Total data points: {len(all_data_points)}")
        return csv_path

    def generate_summary(self, data_points: List[MarketDataPoint]):
        """Generate JSON summary of findings"""
        if not data_points:
            return

        # Group by keyword
        keyword_groups = {}
        for point in data_points:
            if point.keyword not in keyword_groups:
                keyword_groups[point.keyword] = []
            keyword_groups[point.keyword].append(point)

        # Calculate opportunities
        opportunities = []
        for keyword, points in keyword_groups.items():
            avg_price = sum(p.avg_price for p in points) / len(points)
            total_sales = sum(p.est_sales for p in points)
            avg_competition = sum(
                (
                    1
                    if p.competition_level == "low"
                    else 2 if p.competition_level == "medium" else 3
                )
                for p in points
            ) / len(points)

            opportunity_score = (total_sales * avg_price) / (avg_competition + 1)

            opportunities.append(
                {
                    "keyword": keyword,
                    "avg_price": round(avg_price, 2),
                    "total_est_sales": total_sales,
                    "competition_score": round(avg_competition, 2),
                    "opportunity_score": round(opportunity_score, 2),
                    "data_points": len(points),
                }
            )

        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_keywords": len(keyword_groups),
            "total_data_points": len(data_points),
            "top_opportunities": opportunities[:5],
            "market_insights": {
                "avg_book_price": round(
                    sum(p.avg_price for p in data_points) / len(data_points), 2
                ),
                "high_competition_keywords": sum(
                    1 for p in data_points if p.competition_level == "high"
                ),
                "low_competition_keywords": sum(
                    1 for p in data_points if p.competition_level == "low"
                ),
            },
        }

        # Save summary
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"📄 Summary saved to: {summary_path}")


def main():
    """Main entry point"""
    # Check for custom keywords from environment
    custom_keywords = os.getenv("RESEARCH_KEYWORDS", "").split(",")
    keywords = [k.strip() for k in custom_keywords if k.strip()] or None

    # Run research
    engine = MarketResearchEngine()
    csv_path = engine.run_research(keywords)

    # Exit successfully
    return 0


if __name__ == "__main__":
    exit(main())
