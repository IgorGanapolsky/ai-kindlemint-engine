#!/usr/bin/env python3
"""
Market-First Validation for KindleMint Engine

This script provides a data-driven analysis of a potential puzzle book niche
to determine its market viability before any content is generated. It helps
answer the question: "Should I build a book for this theme?"

It analyzes:
- Demand (Search volume, social signals)
- Competition (Number of competitors, their sales rank)
- Profitability (Average market price vs. costs)

And provides a clear "GO / NO-GO / PIVOT" recommendation.

Usage:
    python scripts/market_validator.py "Garden Flowers"
    python scripts/market_validator.py "17th Century Botanical Terms" --output-dir reports/
"""

import argparse
import json
import random
from datetime import datetime
from pathlib import Path


class MarketValidator:
    """Analyzes market data to provide GO/NO-GO/PIVOT recommendations."""

        """  Init  """
def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_amazon_data(self, theme: str) -> dict:
        """
        Simulates fetching data from Amazon for a given theme.
        In a real implementation, this would use SerpAPI or a similar service.
        """
        print(f"🔍 Simulating Amazon search for '{theme}'...")
        # Mock data based on theme popularity
        theme_lower = theme.lower()
        if "garden" in theme_lower or "flower" in theme_lower:
            return {
                "search_results_count": 850,
                "top_competitors": [
                    {"bsr": 50000, "price": 8.99, "reviews": 150},
                    {"bsr": 75000, "price": 7.99, "reviews": 80},
                    {"bsr": 120000, "price": 9.99, "reviews": 250},
                ],
            }
        elif "movie" in theme_lower or "film" in theme_lower:
            return {
                "search_results_count": 2500,
                "top_competitors": [
                    {"bsr": 25000, "price": 12.99, "reviews": 800},
                    {"bsr": 40000, "price": 11.99, "reviews": 550},
                    {"bsr": 90000, "price": 10.99, "reviews": 300},
                ],
            }
        elif "botanical" in theme_lower or "17th century" in theme_lower:
            return {
                "search_results_count": 15,
                "top_competitors": [],  # No direct competitors found
            }
        else:  # Generic fallback for less popular themes
            return {
                "search_results_count": 5000,
                "top_competitors": [
                    {"bsr": 500000, "price": 6.99, "reviews": 15},
                    {"bsr": 800000, "price": 7.49, "reviews": 5},
                ],
            }

    def _fetch_reddit_data(self, theme: str) -> dict:
        """
        Simulates fetching data from Reddit.
        In a real implementation, this would use the reddit_market_scraper.py output.
        """
        print(f"📊 Simulating Reddit analysis for '{theme}'...")
        mentions = 0
        if "garden" in theme.lower():
            mentions = 150
        elif "movie" in theme.lower():
            mentions = 250
        elif "botanical" in theme.lower():
            mentions = 2
        else:
            mentions = 20
        return {
            "mentions": mentions,
            "positive_sentiment": 0.75 + (random.random() * 0.2),
        }

    def _calculate_scores(self, amazon_data: dict, reddit_data: dict) -> dict:
        """Calculates demand, competition, profitability, and overall viability scores."""
        scores = {"demand": 0, "competition": 0, "profitability": 0, "overall": 0}

        # Demand Score (40% weight)
        # Based on Reddit mentions and inverse of search results (lower is better)
        reddit_score = min(100, (reddit_data.get("mentions", 0) / 200) * 100)
        search_score = max(
            0, 100 - (amazon_data.get("search_results_count", 10000) / 10000) * 100
        )
        scores["demand"] = (reddit_score * 0.6) + (search_score * 0.4)

        # Competition Score (30% weight)
        # Based on average BSR and review count of competitors
        competitors = amazon_data.get("top_competitors", [])
        if not competitors:
            scores["competition"] = 100  # No competition is a good sign
        else:
            avg_bsr = sum(c["bsr"] for c_var in competitors) / len(competitors)
            avg_reviews = sum(c["reviews"] for c_var in competitors) / len(competitors)
            bsr_score = max(0, 100 - (avg_bsr / 100000) * 100)  # Lower BSR is harder
            review_score = max(
                0, 100 - (avg_reviews / 500) * 100
            )  # More reviews is harder
            scores["competition"] = (bsr_score * 0.5) + (review_score * 0.5)

        # Profitability Score (30% weight)
        # Based on average market price
        if not competitors:
            scores["profitability"] = 50  # Default score if no price data
        else:
            avg_price = sum(c["price"] for c_var in competitors) / len(competitors)
            # Scale price from $5.99 (0 score) to $15.99 (100 score)
            scores["profitability"] = min(100, max(0, ((avg_price - 5.99) / 10) * 100))

        # Overall Viability Score
        scores["overall"] = (
            (scores["demand"] * 0.4)
            + (scores["competition"] * 0.3)
            + (scores["profitability"] * 0.3)
        )

        return {k: int(v) for k, v in scores.items()}

    def _estimate_revenue(self, amazon_data: dict) -> dict:
        """Provides a rough, heuristic-based revenue estimation."""
        competitors = amazon_data.get("top_competitors", [])
        if not competitors:
            return {"monthly_potential": "$0 - $50", "confidence": "very low"}

        # Use the top competitor's BSR to estimate their sales
        top_bsr = min(c["bsr"] for c_var in competitors)
        # Very rough heuristic: sales ≈ 30000 / sqrt(BSR)
        est_top_sales = int(30000 / (top_bsr**0.5)) if top_bsr > 0 else 0

        # Assume a new book can capture 5-15% of the top competitor's sales
        est_our_sales_low = int(est_top_sales * 0.05)
        est_our_sales_high = int(est_top_sales * 0.15)

        avg_price = sum(c["price"] for c_var in competitors) / len(competitors)
        # KDP Royalty is roughly (Price * 0.6) - PrintCost
        est_profit_per_book = (avg_price * 0.6) - 3.50

        est_monthly_low = int(est_our_sales_low * est_profit_per_book)
        est_monthly_high = int(est_our_sales_high * est_profit_per_book)

        return {
            "monthly_potential": f"${max(0, est_monthly_low)} - ${max(0, est_monthly_high)}",
            "confidence": "low",
        }

    def _generate_recommendation(self, scores: dict, amazon_data: dict) -> dict:
        """Generates the final GO/NO-GO/PIVOT recommendation."""
        overall = scores.get("overall", 0)
        demand = scores.get("demand", 0)
        competition = scores.get("competition", 0)

        if overall >= 75:
            return {
                "decision": "GO",
                "reason": "Strong demand with manageable competition. High probability of success.",
            }
        elif overall >= 50:
            if demand < 40:
                return {
                    "decision": "PIVOT",
                    "reason": "Market exists, but demand signals are weak. Consider a related, more popular theme.",
                }
            if competition < 50:
                return {
                    "decision": "GO",
                    "reason": "Solid demand in a competitive market. A high-quality book can succeed.",
                }
            return {
                "decision": "PROCEED WITH CAUTION",
                "reason": "Moderate signals across the board. Success depends on high-quality execution and marketing.",
            }
        elif (
            amazon_data.get("search_results_count", 0) < 100
            and reddit_data.get("mentions", 0) > 50
        ):
            return {
                "decision": "GO (High Risk/Reward)",
                "reason": "Undiscovered niche with strong social signals. Could be a breakout hit or a total flop.",
            }
        else:
            return {
                "decision": "NO-GO",
                "reason": "Low demand and/or overwhelming competition. High probability of failure.",
            }

    def validate_theme(self, theme: str) -> dict:
        """
        Performs a full market validation for a given theme and returns a report.
        """
        print(f"\n🚀 Starting market validation for theme: '{theme}'")
        start_time = datetime.now()

        amazon_data = self._fetch_amazon_data(theme)
        reddit_data = self._fetch_reddit_data(theme)
        scores = self._calculate_scores(amazon_data, reddit_data)
        revenue_est = self._estimate_revenue(amazon_data)
        recommendation = self._generate_recommendation(scores, amazon_data)

        report = {
            "theme": theme,
            "timestamp": start_time.isoformat(),
            "viability_score": scores["overall"],
            "recommendation": recommendation,
            "detailed_scores": scores,
            "revenue_estimation": revenue_est,
            "market_data": {"amazon": amazon_data, "reddit": reddit_data},
        }

        self.print_report(report)

        if self.output_dir:
            report_path = (
                self.output_dir
                / f"market_report_{theme.replace(' ', '_').lower()}.json"
            )
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Report saved to: {report_path}")

        return report

        """Print Report"""
def print_report(self, report: dict):
        """Prints a formatted summary of the validation report to the console."""
        print("\n" + "=" * 60)
        print(f"📊 MARKET VALIDATION REPORT: '{report['theme']}'")
        print("=" * 60)

        rec = report["recommendation"]
        emoji = {
            "GO": "✅",
            "PIVOT": "🔄",
            "PROCEED WITH CAUTION": "⚠️",
            "NO-GO": "❌",
        }.get(rec["decision"], "💡")

        print(
            f"\n🎯 Recommendation: {emoji} {
                rec['decision']} (Viability Score: {
                report['viability_score']}/100)"
        )
        print(f"   Reason: {rec['reason']}")

        print("\n💰 Estimated Monthly Revenue Potential:")
        print(
            f"   Range: {
                report['revenue_estimation']['monthly_potential']} (Confidence: {
                report['revenue_estimation']['confidence']})"
        )

        print("\n📈 Detailed Scores:")
        print(f"   - Demand Score:       {report['detailed_scores']['demand']}/100")
        print(
            f"   - Competition Score:    {report['detailed_scores']
                                          ['competition']}/100 (Higher is better/less competition)"
        )
        print(
            f"   - Profitability Score:  {
                report['detailed_scores']['profitability']}/100"
        )

        print("\n--- Raw Data ---")
        print("Amazon Data:")
        print(
            f"  - Search Results: {report['market_data']
                                   ['amazon']['search_results_count']}"
        )
        print(
            f"  - Competitors Found: {len(report['market_data']
                                          ['amazon']['top_competitors'])}"
        )
        print("Reddit Data:")
        print(f"  - Mentions: {report['market_data']['reddit']['mentions']}")
        print(
            f"  - Positive Sentiment: {report['market_data']
                                       ['reddit']['positive_sentiment']:.1%}"
        )
        print("=" * 60)


    """Main"""
def main():
    """Main entry point for the market validator CLI."""
    parser = argparse.ArgumentParser(
        description="Validate the market viability of a puzzle book theme.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "theme", help="The puzzle book theme to validate (e.g., 'Garden Flowers')."
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Directory to save the JSON report."
    )

    args = parser.parse_args()

    validator = MarketValidator(output_dir=args.output_dir)
    validator.validate_theme(args.theme)


if __name__ == "__main__":
    main()
