#!/usr/bin/env python3
"""
Daily Summary Generator for KindleMint Engine
Tracks production metrics, revenue, and market trends
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class DailySummaryGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.reports_dir = self.base_dir / "reports" / "daily-summaries"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary(self) -> Dict:
        """Generate comprehensive daily summary"""
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "production": self._get_production_metrics(),
            "quality": self._get_quality_metrics(),
            "market_research": self._get_market_insights(),
            "revenue_estimate": self._calculate_revenue(),
            "automation_status": self._check_automation(),
            "next_actions": self._generate_recommendations(),
        }

        return summary

    def _get_production_metrics(self) -> Dict:
        """Track books and puzzles generated"""
        metrics = {
            "books_generated_today": 0,
            "total_books": 0,
            "puzzles_created": 0,
            "formats": {"paperback": 0, "hardcover": 0, "kindle": 0},
            "series_status": [],
        }

        # Count books in active production
        production_dir = self.base_dir / "books" / "active_production"
        if production_dir.exists():
            for series_dir in production_dir.iterdir():
                if series_dir.is_dir():
                    series_info = {"name": series_dir.name, "volumes": []}

                    for volume_dir in series_dir.iterdir():
                        if volume_dir.is_dir() and volume_dir.name.startswith(
                            "volume_"
                        ):
                            volume_num = int(volume_dir.name.split("_")[1])
                            series_info["volumes"].append(volume_num)
                            metrics["total_books"] += 1

                            # Check formats
                            if (volume_dir / "paperback").exists():
                                metrics["formats"]["paperback"] += 1
                            if (volume_dir / "hardcover").exists():
                                metrics["formats"]["hardcover"] += 1
                            if (volume_dir / "kindle").exists():
                                metrics["formats"]["kindle"] += 1

                    series_info["volumes"].sort()
                    metrics["series_status"].append(series_info)

        # Calculate total puzzles (50 per book)
        metrics["puzzles_created"] = metrics["total_books"] * 50

        return metrics

    def _get_quality_metrics(self) -> Dict:
        """Track QA validation results"""
        metrics = {
            "qa_runs_today": 0,
            "qa_pass_rate": 0,
            "common_issues": [],
            "last_validation": None,
        }

        # Check for recent QA reports
        qa_reports = list(self.base_dir.glob("**/qa_production_report.json"))
        if qa_reports:
            # Sort by modification time
            qa_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Get today's reports
            today = datetime.now().date()
            today_reports = []

            for report_path in qa_reports:
                mod_time = datetime.fromtimestamp(report_path.stat().st_mtime).date()
                if mod_time == today:
                    today_reports.append(report_path)

            metrics["qa_runs_today"] = len(today_reports)

            # Calculate pass rate
            if today_reports:
                passed = 0
                issues = []

                for report_path in today_reports:
                    try:
                        with open(report_path) as f:
                            report = json.load(f)
                            if report.get("qa_score", 0) >= 80:
                                passed += 1
                            if "critical_issues" in report:
                                issues.extend(report["critical_issues"][:2])
                    except:
                        pass

                metrics["qa_pass_rate"] = (passed / len(today_reports)) * 100
                metrics["common_issues"] = list(set(issues))[:5]
                metrics["last_validation"] = datetime.fromtimestamp(
                    today_reports[0].stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")

        return metrics

    def _get_market_insights(self) -> Dict:
        """Get latest market research data"""
        insights = {
            "trending_keywords": [],
            "hot_niches": [],
            "competitor_activity": "Unknown",
            "last_scrape": None,
        }

        # Check for market insights
        market_dir = self.base_dir / "data" / "market-insights"
        if market_dir.exists():
            # Get today's insights
            today_file = (
                market_dir / f"reddit_insights_{datetime.now().strftime('%Y%m%d')}.json"
            )
            if today_file.exists():
                try:
                    with open(today_file) as f:
                        data = json.load(f)

                    if "overall_trends" in data:
                        # Get top keywords
                        top_keywords = data["overall_trends"].get("top_keywords", {})
                        insights["trending_keywords"] = list(top_keywords.keys())[:5]

                        # Get recommendations
                        recs = data["overall_trends"].get("recommendations", [])
                        insights["hot_niches"] = [r["niche"] for r in recs[:3]]

                    insights["last_scrape"] = data.get("timestamp", "Unknown")
                except:
                    pass

        return insights

    def _calculate_revenue(self) -> Dict:
        """Estimate revenue based on books published"""
        revenue = {
            "daily_estimate": 0,
            "monthly_estimate": 0,
            "breakdown": {"paperback": 0, "hardcover": 0, "kindle": 0},
            "assumptions": {
                "avg_sales_per_book_daily": 2,
                "paperback_profit": 5.74,
                "hardcover_profit": 8.50,
                "kindle_profit": 7.00,
            },
        }

        # Get production metrics
        prod = self._get_production_metrics()
        formats = prod["formats"]

        # Calculate daily revenue
        daily_sales = revenue["assumptions"]["avg_sales_per_book_daily"]

        revenue["breakdown"]["paperback"] = (
            formats["paperback"]
            * daily_sales
            * revenue["assumptions"]["paperback_profit"]
        )
        revenue["breakdown"]["hardcover"] = (
            formats["hardcover"]
            * daily_sales
            * revenue["assumptions"]["hardcover_profit"]
        )
        revenue["breakdown"]["kindle"] = (
            formats["kindle"] * daily_sales * revenue["assumptions"]["kindle_profit"]
        )

        revenue["daily_estimate"] = sum(revenue["breakdown"].values())
        revenue["monthly_estimate"] = revenue["daily_estimate"] * 30

        return revenue

    def _check_automation(self) -> Dict:
        """Check status of automated systems"""
        status = {
            "github_actions": "Unknown",
            "market_research": "Unknown",
            "last_commit": None,
            "pending_tasks": [],
        }

        # Check last git commit
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                capture_output=True,
                text=True,
                cwd=self.base_dir,
            )
            if result.returncode == 0:
                status["last_commit"] = result.stdout.strip()
        except:
            pass

        # Check for GitHub Actions runs (simplified)
        status["github_actions"] = (
            "Configured"
            if (self.base_dir / ".github" / "workflows").exists()
            else "Not configured"
        )

        # Check market research
        if (
            self.base_dir
            / "data"
            / "market-insights"
            / f"reddit_insights_{datetime.now().strftime('%Y%m%d')}.json"
        ).exists():
            status["market_research"] = "Completed today"
        else:
            status["market_research"] = "Pending"
            status["pending_tasks"].append("Run market research")

        return status

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Get metrics
        prod = self._get_production_metrics()
        quality = self._get_quality_metrics()
        market = self._get_market_insights()

        # Production recommendations
        if prod["total_books"] < 5:
            recommendations.append(
                "📚 Generate more volumes to build a series (target: 5-10 books)"
            )

        if prod["formats"]["hardcover"] < prod["formats"]["paperback"]:
            recommendations.append(
                "📖 Create hardcover editions for existing paperbacks (higher profit margin)"
            )

        # Quality recommendations
        if quality["qa_pass_rate"] < 80:
            recommendations.append(
                "⚠️ Fix QA issues before publishing - current pass rate: {:.0f}%".format(
                    quality["qa_pass_rate"]
                )
            )

        # Market recommendations
        if market["trending_keywords"]:
            recommendations.append(
                f"🔥 Create content for trending keyword: {market['trending_keywords'][0]}"
            )

        if market["hot_niches"]:
            recommendations.append(f"🎯 Target hot niche: {market['hot_niches'][0]}")

        # Revenue recommendations
        if prod["total_books"] > 0 and not recommendations:
            recommendations.append(
                "✅ All systems operational - focus on marketing and sales"
            )

        return recommendations[:5]  # Top 5 recommendations

    def save_summary(self, summary: Dict):
        """Save summary in multiple formats"""
        date_str = summary["date"]

        # Save JSON
        json_path = self.reports_dir / f"summary_{date_str}.json"
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=2)

        # Save Markdown
        md_path = self.reports_dir / f"summary_{date_str}.md"
        md_content = self._format_markdown(summary)
        with open(md_path, "w") as f:
            f.write(md_content)

        # Update latest symlink
        latest_json = self.reports_dir / "latest.json"
        latest_md = self.reports_dir / "latest.md"

        # Copy files (symlinks don't work well on all systems)
        with open(json_path) as src, open(latest_json, "w") as dst:
            dst.write(src.read())
        with open(md_path) as src, open(latest_md, "w") as dst:
            dst.write(src.read())

        print(f"✅ Summary saved to {self.reports_dir}")

    def _format_markdown(self, summary: Dict) -> str:
        """Format summary as readable markdown"""
        md = f"""# 📊 KindleMint Daily Summary - {summary['date']}

*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📚 Production Metrics

| Metric | Value |
|--------|-------|
| Total Books | {summary['production']['total_books']} |
| Books Today | {summary['production']['books_generated_today']} |
| Total Puzzles | {summary['production']['puzzles_created']:,} |
| Paperback Editions | {summary['production']['formats']['paperback']} |
| Hardcover Editions | {summary['production']['formats']['hardcover']} |
| Kindle Editions | {summary['production']['formats']['kindle']} |

### Series Status
"""

        for series in summary["production"]["series_status"]:
            volumes = ", ".join(str(v) for v in series["volumes"])
            md += f"- **{series['name']}**: Volumes {volumes}\n"

        md += f"""

## ✅ Quality Metrics

| Metric | Value |
|--------|-------|
| QA Runs Today | {summary['quality']['qa_runs_today']} |
| QA Pass Rate | {summary['quality']['qa_pass_rate']:.0f}% |
| Last Validation | {summary['quality']['last_validation'] or 'N/A'} |
"""

        if summary["quality"]["common_issues"]:
            md += "\n### Common Issues\n"
            for issue in summary["quality"]["common_issues"]:
                md += f"- {issue}\n"

        md += f"""

## 🔥 Market Research

| Metric | Value |
|--------|-------|
| Last Scrape | {summary['market_research']['last_scrape'] or 'N/A'} |
| Trending Keywords | {len(summary['market_research']['trending_keywords'])} found |

### Top Trending Keywords
"""

        for keyword in summary["market_research"]["trending_keywords"]:
            md += f"- {keyword}\n"

        if summary["market_research"]["hot_niches"]:
            md += "\n### Hot Niches\n"
            for niche in summary["market_research"]["hot_niches"]:
                md += f"- {niche}\n"

        md += f"""

## 💰 Revenue Estimates

| Type | Daily | Monthly |
|------|-------|---------|
| Paperback | ${summary['revenue_estimate']['breakdown']['paperback']:.2f} | ${summary['revenue_estimate']['breakdown']['paperback'] * 30:.2f} |
| Hardcover | ${summary['revenue_estimate']['breakdown']['hardcover']:.2f} | ${summary['revenue_estimate']['breakdown']['hardcover'] * 30:.2f} |
| Kindle | ${summary['revenue_estimate']['breakdown']['kindle']:.2f} | ${summary['revenue_estimate']['breakdown']['kindle'] * 30:.2f} |
| **Total** | **${summary['revenue_estimate']['daily_estimate']:.2f}** | **${summary['revenue_estimate']['monthly_estimate']:,.2f}** |

*Based on {summary['revenue_estimate']['assumptions']['avg_sales_per_book_daily']} daily sales per book*

## 🤖 Automation Status

| System | Status |
|--------|--------|
| GitHub Actions | {summary['automation_status']['github_actions']} |
| Market Research | {summary['automation_status']['market_research']} |
| Last Commit | {summary['automation_status']['last_commit'] or 'Unknown'} |
"""

        if summary["automation_status"]["pending_tasks"]:
            md += "\n### Pending Tasks\n"
            for task in summary["automation_status"]["pending_tasks"]:
                md += f"- {task}\n"

        md += "\n## 🎯 Recommended Actions\n\n"

        for i, rec in enumerate(summary["next_actions"], 1):
            md += f"{i}. {rec}\n"

        md += """

---

*This summary is automatically generated by KindleMint Engine*
*For detailed analytics, check the JSON version of this report*
"""

        return md

    def run(self):
        """Generate and save daily summary"""
        print("📊 Generating daily summary...")

        summary = self.generate_summary()
        self.save_summary(summary)

        # Print key metrics
        print(f"\n📚 Total Books: {summary['production']['total_books']}")
        print(
            f"💰 Monthly Revenue Estimate: ${summary['revenue_estimate']['monthly_estimate']:,.2f}"
        )
        print(f"✅ QA Pass Rate: {summary['quality']['qa_pass_rate']:.0f}%")

        print("\n🎯 Top Recommendations:")
        for rec in summary["next_actions"][:3]:
            print(f"  - {rec}")

        return summary


if __name__ == "__main__":
    generator = DailySummaryGenerator()
    generator.run()
