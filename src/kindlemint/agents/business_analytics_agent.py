"""
Business Analytics Agent

This agent provides comprehensive business intelligence and analytics for the
KindleMint publishing system including:
- Revenue tracking and projections
- Market trend analysis
- ROI calculations
- Performance benchmarking
- Strategic recommendations
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import pandas as pd
import numpy as np

from .agent_types import AgentCapability
from .base_agent import BaseAgent
from .task_system import Task, TaskResult, TaskStatus


class BusinessAnalyticsAgent(BaseAgent):
    """Agent responsible for business intelligence and analytics"""

    def __init__(self, 
                 data_storage_path: str = "books/analytics_data",
                 performance_data_path: str = "books/performance_data"):
        super().__init__(
            agent_type="business_analytics",
            capabilities=[
                AgentCapability.BUSINESS_INTELLIGENCE,
                AgentCapability.BUSINESS_REPORTING,
                AgentCapability.MARKET_ANALYTICS,
                AgentCapability.PERFORMANCE_MONITORING
            ],
            max_concurrent_tasks=3,
            heartbeat_interval=300  # 5 minutes
        )
        
        self.data_storage_path = Path(data_storage_path)
        self.performance_data_path = Path(performance_data_path)
        self.analytics_cache: Dict[str, Any] = {}
        self.benchmarks: Dict[str, Any] = {}
        
        # Create storage directory
        self.data_storage_path.mkdir(parents=True, exist_ok=True)
        
    async def _initialize(self) -> None:
        """Initialize the business analytics agent"""
        self.logger.info("Initializing Business Analytics Agent")
        
        # Load existing analytics data
        await self._load_analytics_cache()
        await self._load_benchmarks()
        
        # Start periodic analytics updates
        asyncio.create_task(self._periodic_analytics_update())
        
        self.logger.info("Business Analytics Agent initialized")

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        await self._save_analytics_cache()
        
    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute analytics task"""
        try:
            task_type = task.task_data.get("type")
            
            if task_type == "generate_business_report":
                return await self._generate_business_report(task)
            elif task_type == "calculate_roi":
                return await self._calculate_roi(task)
            elif task_type == "analyze_market_trends":
                return await self._analyze_market_trends(task)
            elif task_type == "benchmark_performance":
                return await self._benchmark_performance(task)
            elif task_type == "revenue_forecast":
                return await self._revenue_forecast(task)
            elif task_type == "strategic_recommendations":
                return await self._generate_strategic_recommendations(task)
            else:
                return TaskResult(
                    success=False,
                    error=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return TaskResult(success=False, error=str(e))

    async def _generate_business_report(self, task: Task) -> TaskResult:
        """Generate comprehensive business intelligence report"""
        report_type = task.task_data.get("report_type", "comprehensive")
        time_period = task.task_data.get("time_period", "30d")
        
        try:
            # Gather all performance data
            performance_data = await self._gather_performance_data(time_period)
            
            # Generate comprehensive report
            report = {
                "report_id": f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "report_type": report_type,
                "time_period": time_period,
                "summary": await self._generate_executive_summary(performance_data),
                "financial_metrics": await self._calculate_financial_metrics(performance_data),
                "performance_metrics": await self._analyze_performance_metrics(performance_data),
                "market_analysis": await self._analyze_market_position(performance_data),
                "recommendations": await self._generate_business_recommendations(performance_data)
            }
            
            # Save report
            report_file = self.data_storage_path / f"{report['report_id']}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            # Generate executive dashboard
            dashboard = await self._create_executive_dashboard(report)
            dashboard_file = self.data_storage_path / f"{report['report_id']}_dashboard.json"
            with open(dashboard_file, 'w') as f:
                json.dump(dashboard, f, indent=2)
                
            return TaskResult(
                success=True,
                data={
                    "report": report,
                    "report_file": str(report_file),
                    "dashboard_file": str(dashboard_file)
                }
            )
            
        except Exception as e:
            return TaskResult(success=False, error=str(e))

    async def _gather_performance_data(self, time_period: str) -> Dict[str, Any]:
        """Gather all performance data for analysis"""
        cutoff_date = datetime.now() - self._parse_time_period(time_period)
        
        performance_data = {
            "books": {},
            "aggregated_metrics": {},
            "time_range": {
                "start": cutoff_date.isoformat(),
                "end": datetime.now().isoformat(),
                "days": (datetime.now() - cutoff_date).days
            }
        }
        
        # Load performance data from KDP Performance Agent
        if self.performance_data_path.exists():
            # Load active books
            active_books_file = self.performance_data_path / "active_books.json"
            if active_books_file.exists():
                with open(active_books_file, 'r') as f:
                    active_books = json.load(f)
                    
                # Load metrics for each book
                for book_id, book_info in active_books.items():
                    book_metrics_file = self.performance_data_path / f"{book_id}_metrics.json"
                    if book_metrics_file.exists():
                        with open(book_metrics_file, 'r') as f:
                            all_metrics = json.load(f)
                            
                        # Filter by time period
                        recent_metrics = [
                            m for m in all_metrics
                            if datetime.fromisoformat(m["timestamp"]) >= cutoff_date
                        ]
                        
                        performance_data["books"][book_id] = {
                            "info": book_info,
                            "metrics": recent_metrics,
                            "metric_count": len(recent_metrics)
                        }
        
        return performance_data

    async def _generate_executive_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of key metrics"""
        total_books = len(data["books"])
        active_books = sum(1 for book in data["books"].values() if book["metrics"])
        
        # Calculate key metrics
        total_metrics_collected = sum(book["metric_count"] for book in data["books"].values())
        
        # Revenue estimates (placeholder - would need actual sales data)
        estimated_revenue = await self._estimate_revenue(data)
        
        summary = {
            "portfolio_overview": {
                "total_books": total_books,
                "active_books": active_books,
                "monitoring_coverage": (active_books / total_books * 100) if total_books > 0 else 0,
                "data_points_collected": total_metrics_collected
            },
            "financial_snapshot": estimated_revenue,
            "performance_highlights": await self._identify_top_performers(data),
            "alerts": await self._generate_business_alerts(data),
            "key_insights": await self._extract_key_insights(data)
        }
        
        return summary

    async def _estimate_revenue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate revenue based on available data"""
        # This is a placeholder implementation
        # In a real system, you'd integrate with KDP reports API
        
        total_books = len(data["books"])
        
        # Conservative estimates based on industry averages
        avg_monthly_revenue_per_book = 25  # Conservative estimate
        estimated_monthly = total_books * avg_monthly_revenue_per_book
        
        return {
            "estimated_monthly_revenue": estimated_monthly,
            "estimated_annual_revenue": estimated_monthly * 12,
            "revenue_per_book_avg": avg_monthly_revenue_per_book,
            "calculation_method": "industry_average_estimate",
            "note": "Estimates based on industry averages. Actual revenue may vary significantly."
        }

    async def _identify_top_performers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify top performing books"""
        book_scores = {}
        
        for book_id, book_data in data["books"].items():
            if not book_data["metrics"]:
                continue
                
            latest_metrics = book_data["metrics"][-1]
            
            # Create performance score based on available metrics
            score = 0
            
            # Rating score
            if "reviews" in latest_metrics and latest_metrics["reviews"].get("average_rating"):
                score += latest_metrics["reviews"]["average_rating"] * 10
                
            # Review count score
            if "reviews" in latest_metrics and latest_metrics["reviews"].get("total_reviews"):
                score += min(latest_metrics["reviews"]["total_reviews"], 100)
                
            # Availability score
            if "availability" in latest_metrics:
                if "in stock" in latest_metrics["availability"].lower():
                    score += 20
                    
            book_scores[book_id] = score
        
        # Sort by score
        sorted_books = sorted(book_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "top_performers": sorted_books[:5],
            "performance_scores": book_scores,
            "ranking_criteria": ["rating", "review_count", "availability"]
        }

    async def _generate_business_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business alerts and warnings"""
        alerts = []
        
        # Check for books with no recent data
        stale_books = []
        for book_id, book_data in data["books"].items():
            if not book_data["metrics"]:
                stale_books.append(book_id)
                
        if stale_books:
            alerts.append({
                "type": "warning",
                "category": "data_quality",
                "message": f"{len(stale_books)} books have no performance data",
                "affected_books": stale_books,
                "recommendation": "Check monitoring configuration for these books"
            })
            
        # Check for books with low ratings
        low_rated_books = []
        for book_id, book_data in data["books"].items():
            if book_data["metrics"]:
                latest = book_data["metrics"][-1]
                if "reviews" in latest and latest["reviews"].get("average_rating", 5) < 3.5:
                    low_rated_books.append({
                        "book_id": book_id,
                        "rating": latest["reviews"]["average_rating"]
                    })
                    
        if low_rated_books:
            alerts.append({
                "type": "attention",
                "category": "quality",
                "message": f"{len(low_rated_books)} books have ratings below 3.5 stars",
                "affected_books": low_rated_books,
                "recommendation": "Review content quality and consider improvements"
            })
            
        return alerts

    async def _extract_key_insights(self, data: Dict[str, Any]) -> List[str]:
        """Extract key business insights from the data"""
        insights = []
        
        total_books = len(data["books"])
        books_with_reviews = sum(
            1 for book in data["books"].values()
            if book["metrics"] and book["metrics"][-1].get("reviews", {}).get("total_reviews", 0) > 0
        )
        
        if books_with_reviews > 0:
            review_rate = (books_with_reviews / total_books) * 100
            insights.append(f"{review_rate:.1f}% of books have customer reviews")
            
        # Add more insights based on available data
        insights.append(f"Monitoring {total_books} books across your portfolio")
        
        return insights

    async def _calculate_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial performance metrics"""
        return {
            "revenue_metrics": await self._estimate_revenue(data),
            "cost_analysis": await self._analyze_costs(data),
            "roi_analysis": await self._calculate_portfolio_roi(data),
            "projections": await self._calculate_financial_projections(data)
        }

    async def _analyze_costs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze costs and expenses"""
        # Placeholder for cost analysis
        # In a real system, you'd track actual costs for content creation, covers, etc.
        
        total_books = len(data["books"])
        
        # Estimated costs per book
        estimated_cost_per_book = {
            "content_generation": 5,  # AI costs
            "cover_design": 0,  # Assuming you create covers yourself
            "editing_qa": 2,  # AI-assisted QA
            "marketing": 3,  # Promotional costs
            "total": 10
        }
        
        return {
            "cost_per_book": estimated_cost_per_book,
            "total_portfolio_cost": total_books * estimated_cost_per_book["total"],
            "monthly_operational_costs": {
                "ai_services": 50,
                "tools_software": 30,
                "total": 80
            }
        }

    async def _calculate_portfolio_roi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ROI for the entire portfolio"""
        revenue_data = await self._estimate_revenue(data)
        cost_data = await self._analyze_costs(data)
        
        estimated_monthly_revenue = revenue_data["estimated_monthly_revenue"]
        total_costs = cost_data["total_portfolio_cost"] + cost_data["monthly_operational_costs"]["total"]
        
        roi = ((estimated_monthly_revenue - total_costs) / total_costs * 100) if total_costs > 0 else 0
        
        return {
            "monthly_roi": roi,
            "break_even_timeline": self._calculate_break_even(revenue_data, cost_data),
            "profitability_threshold": await self._calculate_profitability_threshold(data)
        }

    def _calculate_break_even(self, revenue_data: Dict, cost_data: Dict) -> Dict[str, Any]:
        """Calculate break-even analysis"""
        monthly_revenue = revenue_data["estimated_monthly_revenue"]
        total_investment = cost_data["total_portfolio_cost"]
        monthly_costs = cost_data["monthly_operational_costs"]["total"]
        
        if monthly_revenue <= monthly_costs:
            return {"status": "not_profitable", "months_to_break_even": None}
            
        months_to_break_even = total_investment / (monthly_revenue - monthly_costs)
        
        return {
            "status": "profitable",
            "months_to_break_even": round(months_to_break_even, 1),
            "break_even_date": (datetime.now() + timedelta(days=months_to_break_even * 30)).strftime("%Y-%m-%d")
        }

    async def _calculate_profitability_threshold(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate how many books needed for target profitability"""
        target_monthly_profit = 1000  # Target $1000/month profit
        cost_data = await self._analyze_costs(data)
        
        monthly_operational = cost_data["monthly_operational_costs"]["total"]
        revenue_per_book = 25  # Conservative estimate
        cost_per_book_monthly = 2  # Amortized cost
        
        net_per_book = revenue_per_book - cost_per_book_monthly
        books_needed = (target_monthly_profit + monthly_operational) / net_per_book
        
        return {
            "target_monthly_profit": target_monthly_profit,
            "books_needed_for_target": round(books_needed),
            "current_books": len(data["books"]),
            "additional_books_needed": max(0, round(books_needed) - len(data["books"]))
        }

    async def _calculate_financial_projections(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial projections"""
        current_books = len(data["books"])
        
        # Projection scenarios
        scenarios = {
            "conservative": {"growth_rate": 0.05, "books_per_month": 2},
            "moderate": {"growth_rate": 0.10, "books_per_month": 4},
            "aggressive": {"growth_rate": 0.15, "books_per_month": 6}
        }
        
        projections = {}
        
        for scenario_name, params in scenarios.items():
            monthly_projections = []
            books_count = current_books
            
            for month in range(1, 13):  # 12 months
                books_count += params["books_per_month"]
                monthly_revenue = books_count * 25 * (1 + params["growth_rate"]) ** month
                
                monthly_projections.append({
                    "month": month,
                    "books": books_count,
                    "revenue": round(monthly_revenue, 2)
                })
                
            projections[scenario_name] = {
                "parameters": params,
                "projections": monthly_projections,
                "year_end": {
                    "books": monthly_projections[-1]["books"],
                    "monthly_revenue": monthly_projections[-1]["revenue"],
                    "annual_revenue": sum(p["revenue"] for p in monthly_projections)
                }
            }
            
        return projections

    async def _analyze_performance_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics across the portfolio"""
        metrics_summary = {
            "rating_analysis": await self._analyze_ratings(data),
            "review_analysis": await self._analyze_reviews(data),
            "availability_analysis": await self._analyze_availability(data),
            "trend_analysis": await self._analyze_trends(data)
        }
        
        return metrics_summary

    async def _analyze_ratings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze rating distribution and trends"""
        ratings = []
        
        for book_data in data["books"].values():
            if book_data["metrics"]:
                latest = book_data["metrics"][-1]
                if "reviews" in latest and latest["reviews"].get("average_rating"):
                    ratings.append(latest["reviews"]["average_rating"])
        
        if not ratings:
            return {"status": "no_rating_data"}
            
        return {
            "average_rating": round(statistics.mean(ratings), 2),
            "median_rating": statistics.median(ratings),
            "rating_distribution": self._calculate_distribution(ratings, [1, 2, 3, 4, 5]),
            "books_with_ratings": len(ratings),
            "total_books": len(data["books"]),
            "rating_coverage": len(ratings) / len(data["books"]) * 100
        }

    def _calculate_distribution(self, values: List[float], bins: List[int]) -> Dict[str, int]:
        """Calculate distribution of values across bins"""
        distribution = {str(bin_val): 0 for bin_val in bins}
        
        for value in values:
            for i, bin_val in enumerate(bins):
                if value <= bin_val or i == len(bins) - 1:
                    distribution[str(bin_val)] += 1
                    break
                    
        return distribution

    async def _analyze_market_position(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market position and competitive landscape"""
        return {
            "portfolio_positioning": await self._assess_portfolio_positioning(data),
            "competitive_analysis": await self._perform_competitive_analysis(data),
            "market_opportunities": await self._identify_market_opportunities(data)
        }

    async def _assess_portfolio_positioning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall portfolio positioning"""
        total_books = len(data["books"])
        
        # Analyze series distribution
        series_count = {}
        for book_data in data["books"].values():
            series = book_data["info"].get("series", "Unknown")
            series_count[series] = series_count.get(series, 0) + 1
            
        return {
            "portfolio_size": total_books,
            "series_distribution": series_count,
            "diversification_score": len(series_count) / total_books if total_books > 0 else 0,
            "largest_series": max(series_count.items(), key=lambda x: x[1]) if series_count else None
        }

    async def _generate_business_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategic business recommendations"""
        recommendations = []
        
        total_books = len(data["books"])
        books_with_data = sum(1 for book in data["books"].values() if book["metrics"])
        
        # Data coverage recommendation
        if books_with_data < total_books:
            recommendations.append({
                "priority": "high",
                "category": "data_quality",
                "title": "Improve Performance Monitoring Coverage",
                "description": f"Only {books_with_data} out of {total_books} books have performance data",
                "action_items": [
                    "Verify ASIN data for all books",
                    "Check monitoring agent configuration",
                    "Implement automated ASIN discovery"
                ]
            })
            
        # Growth recommendations
        financial_metrics = await self._calculate_financial_metrics(data)
        if total_books < 50:  # Arbitrary threshold
            recommendations.append({
                "priority": "medium",
                "category": "growth",
                "title": "Scale Book Production",
                "description": "Increase portfolio size to improve revenue potential",
                "action_items": [
                    f"Target {financial_metrics['roi_analysis']['profitability_threshold']['books_needed_for_target']} books for profitability",
                    "Identify high-performing niches for expansion",
                    "Automate content generation pipeline"
                ]
            })
            
        return recommendations

    async def _calculate_roi(self, task: Task) -> TaskResult:
        """Calculate ROI for specific books or periods"""
        try:
            calculation_type = task.task_data.get("calculation_type", "portfolio")
            time_period = task.task_data.get("time_period", "30d")
            
            performance_data = await self._gather_performance_data(time_period)
            roi_data = await self._calculate_portfolio_roi(performance_data)
            
            return TaskResult(
                success=True,
                data={"roi_analysis": roi_data, "time_period": time_period}
            )
            
        except Exception as e:
            return TaskResult(success=False, error=str(e))

    async def _create_executive_dashboard(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive dashboard with key metrics"""
        dashboard = {
            "dashboard_id": f"exec_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "widgets": [
                {
                    "type": "metric_card",
                    "title": "Total Books",
                    "value": report["summary"]["portfolio_overview"]["total_books"],
                    "trend": "stable"
                },
                {
                    "type": "metric_card", 
                    "title": "Estimated Monthly Revenue",
                    "value": f"${report['financial_metrics']['revenue_metrics']['estimated_monthly_revenue']}",
                    "trend": "up"
                },
                {
                    "type": "chart",
                    "title": "Revenue Projection",
                    "data": report["financial_metrics"]["projections"]["moderate"]["projections"]
                },
                {
                    "type": "alert_list",
                    "title": "Business Alerts",
                    "alerts": report["summary"]["alerts"]
                }
            ]
        }
        
        return dashboard

    def _parse_time_period(self, time_period: str) -> timedelta:
        """Parse time period string to timedelta"""
        if time_period.endswith('d'):
            return timedelta(days=int(time_period[:-1]))
        elif time_period.endswith('w'):
            return timedelta(weeks=int(time_period[:-1]))
        elif time_period.endswith('m'):
            return timedelta(days=int(time_period[:-1]) * 30)
        else:
            return timedelta(days=30)  # Default

    async def _load_analytics_cache(self) -> None:
        """Load cached analytics data"""
        cache_file = self.data_storage_path / "analytics_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.analytics_cache = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load analytics cache: {e}")

    async def _save_analytics_cache(self) -> None:
        """Save analytics cache"""
        cache_file = self.data_storage_path / "analytics_cache.json"
        self.analytics_cache["last_updated"] = datetime.now().isoformat()
        
        with open(cache_file, 'w') as f:
            json.dump(self.analytics_cache, f, indent=2)

    async def _load_benchmarks(self) -> None:
        """Load industry benchmarks"""
        # Load or initialize benchmarks
        self.benchmarks = {
            "industry_averages": {
                "monthly_revenue_per_book": 25,
                "average_rating": 4.2,
                "review_rate": 0.05,  # 5% of readers leave reviews
                "return_on_ad_spend": 3.0
            },
            "performance_thresholds": {
                "good_rating": 4.0,
                "good_review_count": 10,
                "profitable_revenue": 15  # per book per month
            }
        }

    async def _periodic_analytics_update(self) -> None:
        """Periodic analytics updates"""
        while self.status.value != "shutdown":
            try:
                self.logger.info("Running periodic analytics update")
                
                # Update cached analytics
                performance_data = await self._gather_performance_data("7d")
                self.analytics_cache["last_performance_summary"] = await self._generate_executive_summary(performance_data)
                
                await self._save_analytics_cache()
                
                # Wait 1 hour for next update
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in periodic analytics update: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error