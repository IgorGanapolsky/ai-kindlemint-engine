#!/usr/bin/env python3
"""
Claude Cost Analytics Engine
Provides comprehensive cost tracking with multiple time periods and clear metrics
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote


class CostAnalytics:
    """Advanced cost analytics for Claude API usage"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.commit_costs_file = self.repo_path / "commit_costs.json"
        self.cost_analytics_file = self.repo_path / "cost_analytics.json"

    def load_commit_costs(self) -> Dict:
        """Load existing commit costs data"""
        if self.commit_costs_file.exists():
            try:
                with open(self.commit_costs_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"total_cost": 0.0, "commits": []}

    def calculate_time_periods(self) -> Dict[str, Dict]:
        """Calculate costs for different time periods"""
        cost_data = self.load_commit_costs()
        commits = cost_data.get("commits", [])

        if not commits:
            return self._empty_analytics()

        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Time period boundaries
        week_ago = now - timedelta(days=7)
        month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        # Initialize period totals
        periods = {
            "today": {"cost": 0.0, "commits": 0, "tokens": 0},
            "yesterday": {"cost": 0.0, "commits": 0, "tokens": 0},
            "week": {"cost": 0.0, "commits": 0, "tokens": 0},
            "month": {"cost": 0.0, "commits": 0, "tokens": 0},
            "last_month": {"cost": 0.0, "commits": 0, "tokens": 0},
            "year": {"cost": 0.0, "commits": 0, "tokens": 0},
            "all_time": {"cost": 0.0, "commits": 0, "tokens": 0},
        }

        # Calculate costs per period
        for commit in commits:
            try:
                timestamp = datetime.fromisoformat(commit["timestamp"])
                cost = commit.get("cost", 0.0)
                tokens = commit.get("tokens", 0)

                # All time
                periods["all_time"]["cost"] += cost
                periods["all_time"]["commits"] += 1
                periods["all_time"]["tokens"] += tokens

                # Year to date
                if timestamp >= year_start:
                    periods["year"]["cost"] += cost
                    periods["year"]["commits"] += 1
                    periods["year"]["tokens"] += tokens

                # Current month
                if timestamp >= month_start:
                    periods["month"]["cost"] += cost
                    periods["month"]["commits"] += 1
                    periods["month"]["tokens"] += tokens

                # Last month
                elif timestamp >= last_month_start and timestamp < month_start:
                    periods["last_month"]["cost"] += cost
                    periods["last_month"]["commits"] += 1
                    periods["last_month"]["tokens"] += tokens

                # Last 7 days
                if timestamp >= week_ago:
                    periods["week"]["cost"] += cost
                    periods["week"]["commits"] += 1
                    periods["week"]["tokens"] += tokens

                # Today
                if timestamp >= today:
                    periods["today"]["cost"] += cost
                    periods["today"]["commits"] += 1
                    periods["today"]["tokens"] += tokens

                # Yesterday
                yesterday = today - timedelta(days=1)
                if timestamp >= yesterday and timestamp < today:
                    periods["yesterday"]["cost"] += cost
                    periods["yesterday"]["commits"] += 1
                    periods["yesterday"]["tokens"] += tokens

            except Exception:
                continue

        # Calculate derived metrics
        analytics = {
            "periods": periods,
            "daily_average": self._calculate_daily_average(periods, now),
            "monthly_projection": self._calculate_monthly_projection(periods, now),
            "trends": self._calculate_trends(periods),
            "last_commit": commits[-1] if commits else None,
            "updated": now.isoformat(),
        }

        # Save analytics
        with open(self.cost_analytics_file, "w") as f:
            json.dump(analytics, f, indent=2)

        return analytics

    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure"""
        return {
            "periods": {
                "today": {"cost": 0.0, "commits": 0, "tokens": 0},
                "yesterday": {"cost": 0.0, "commits": 0, "tokens": 0},
                "week": {"cost": 0.0, "commits": 0, "tokens": 0},
                "month": {"cost": 0.0, "commits": 0, "tokens": 0},
                "last_month": {"cost": 0.0, "commits": 0, "tokens": 0},
                "year": {"cost": 0.0, "commits": 0, "tokens": 0},
                "all_time": {"cost": 0.0, "commits": 0, "tokens": 0},
            },
            "daily_average": 0.0,
            "monthly_projection": 0.0,
            "trends": {"month_over_month": 0.0, "week_over_week": 0.0},
            "last_commit": None,
            "updated": datetime.now().isoformat(),
        }

    def _calculate_daily_average(self, periods: Dict, now: datetime) -> float:
        """Calculate daily average for current month"""
        if periods["month"]["commits"] == 0:
            return 0.0

        days_in_month = now.day
        return periods["month"]["cost"] / days_in_month

    def _calculate_monthly_projection(self, periods: Dict, now: datetime) -> float:
        """Project total monthly cost based on current daily average"""
        daily_avg = self._calculate_daily_average(periods, now)

        # Days in current month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)

        last_day = (next_month - timedelta(days=1)).day

        return daily_avg * last_day

    def _calculate_trends(self, periods: Dict) -> Dict[str, float]:
        """Calculate percentage trends"""
        trends = {}

        # Month over month
        if periods["last_month"]["cost"] > 0:
            mom_change = (
                (periods["month"]["cost"] - periods["last_month"]["cost"])
                / periods["last_month"]["cost"]
            ) * 100
            trends["month_over_month"] = round(mom_change, 1)
        else:
            trends["month_over_month"] = 0.0

        # Week over week (compare last 7 days to previous 7 days)
        # This is approximate since we don't have exact week-before data
        if periods["month"]["commits"] > 14:  # Need enough data
            weekly_avg = periods["week"]["cost"]
            monthly_avg_weekly = periods["month"]["cost"] / 4  # Rough estimate
            if monthly_avg_weekly > 0:
                wow_change = (
                    (weekly_avg - monthly_avg_weekly) / monthly_avg_weekly
                ) * 100
                trends["week_over_week"] = round(wow_change, 1)
            else:
                trends["week_over_week"] = 0.0
        else:
            trends["week_over_week"] = 0.0

        return trends

    def generate_badges(self, analytics: Optional[Dict] = None) -> Dict[str, str]:
        """Generate all cost badges with proper labeling"""
        if analytics is None:
            analytics = self.calculate_time_periods()

        badges = {}

        # Primary badges (for-the-badge style)
        badges["monthly"] = self._generate_badge(
            "This Month",
            analytics["periods"]["month"]["cost"],
            self._get_budget_color(
                analytics["periods"]["month"]["cost"], 50.0
            ),  # $50 budget
            style="for-the-badge",
        )

        # Add trend indicator to monthly
        trend = analytics["trends"]["month_over_month"]
        trend_symbol = "▲" if trend > 0 else "▼" if trend < 0 else "→"
        trend_color = "red" if trend > 10 else "green" if trend < -10 else "yellow"

        badges["trend"] = self._generate_badge(
            "Trend",
            f"{trend_symbol} {abs(trend):.0f}%",
            trend_color,
            style="for-the-badge",
            is_currency=False,
        )

        badges["projection"] = self._generate_badge(
            "Projected",
            analytics["monthly_projection"],
            self._get_budget_color(analytics["monthly_projection"], 50.0),
            style="for-the-badge",
        )

        # Secondary badges (flat-square style)
        badges["daily_avg"] = self._generate_badge(
            "Daily Avg",
            analytics["daily_average"],
            "informational",
            style="flat-square",
        )

        badges["weekly"] = self._generate_badge(
            "Last 7 Days",
            analytics["periods"]["week"]["cost"],
            "informational",
            style="flat-square",
        )

        badges["ytd"] = self._generate_badge(
            "Year to Date",
            analytics["periods"]["year"]["cost"],
            "informational",
            style="flat-square",
        )

        # Latest commit badge
        if analytics["last_commit"]:
            badges["last_commit"] = self._generate_badge(
                "Last Commit", analytics["last_commit"]["cost"], "blue", style="flat"
            )

        # Budget status badge
        budget_percent = (
            analytics["periods"]["month"]["cost"] / 50.0
        ) * 100  # $50 budget
        budget_color = self._get_budget_color(
            analytics["periods"]["month"]["cost"], 50.0
        )

        badges["budget"] = self._generate_badge(
            "Budget",
            f"{budget_percent:.0f}%",
            budget_color,
            style="for-the-badge",
            is_currency=False,
        )

        return badges

    def _generate_badge(
        self,
        label: str,
        value: float | str,
        color: str,
        style: str = "flat",
        is_currency: bool = True,
    ) -> str:
        """Generate a single badge URL"""
        if is_currency and isinstance(value, (int, float)):
            if value < 0.01:
                message = "$0.00"
            elif value < 1.0:
                message = f"${value:.2f}"
            elif value < 1000:
                message = f"${value:.0f}"
            else:
                message = f"${value/1000:.1f}k"
        else:
            message = str(value)

        # URL encode the label and message
        encoded_label = quote(label.replace(" ", "_"))
        encoded_message = quote(message)

        base_url = (
            f"https://img.shields.io/badge/{encoded_label}-{encoded_message}-{color}"
        )

        if style != "flat":
            base_url += f"?style={style}"

        return base_url

    def _get_budget_color(self, cost: float, budget: float) -> str:
        """Get color based on budget percentage"""
        if cost <= 0:
            return "green"

        percent = (cost / budget) * 100

        if percent < 50:
            return "green"
        elif percent < 70:
            return "yellow"
        elif percent < 90:
            return "orange"
        else:
            return "red"

    def generate_cost_report(self) -> str:
        """Generate detailed cost report in markdown"""
        analytics = self.calculate_time_periods()

        report = []
        report.append("# 📊 Claude API Cost Report")
        report.append(
            f"\n*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        )

        # Executive Summary
        report.append("## Executive Summary\n")
        report.append(
            f"- **Monthly Cost**: ${analytics['periods']['month']['cost']:.2f}"
        )
        report.append(
            f"- **Daily Average**: ${analytics['daily_average']:.2f}")
        report.append(
            f"- **Projected Monthly**: ${analytics['monthly_projection']:.2f}"
        )
        report.append(
            f"- **Budget Status**: {(analytics['periods']['month']['cost'] / 50.0 * 100):.0f}% of $50"
        )

        # Trends
        trend_mom = analytics["trends"]["month_over_month"]
        trend_symbol = "📈" if trend_mom > 0 else "📉" if trend_mom < 0 else "➡️"
        report.append(
            f"- **Month-over-Month**: {trend_symbol} {trend_mom:+.1f}%\n")

        # Detailed Breakdown
        report.append("## Time Period Breakdown\n")
        report.append("| Period | Cost | Commits | Tokens | Avg/Commit |")
        report.append("|--------|------|---------|--------|------------|")

        for period_name, period_data in analytics["periods"].items():
            if period_data["commits"] > 0:
                avg_per_commit = period_data["cost"] / period_data["commits"]
                report.append(
                    f"| {period_name.replace('_', ' ').title()} | "
                    f"${period_data['cost']:.2f} | "
                    f"{period_data['commits']} | "
                    f"{period_data['tokens']:,} | "
                    f"${avg_per_commit:.2f} |"
                )

        return "\n".join(report)
